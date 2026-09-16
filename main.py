# ============================================================
# VodiWalker 15.0.0
# Railway Ready
# ============================================================

import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import string
import time
import psutil

from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote, parse_qs

import aiofiles
import httpx
import uvicorn

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Depends,
)
from fastapi.responses import (
    Response,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# APP
# ============================================================

APP_NAME = "VodiWalker"
SALES_ENABLED = __import__("os").environ.get("VODIWALKER_SALES_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on")
APP_VERSION = "27.3.0"

SUPPORT_USERNAME = "@VodiWalker"
SUPPORT_URL = "https://t.me/VodiWalker"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(APP_NAME)


# ============================================================
# TIMEZONE
# ============================================================

try:
    from zoneinfo import ZoneInfo

    IRAN_TZ = ZoneInfo("Asia/Tehran")

except Exception:
    IRAN_TZ = None


# ============================================================
# RAILWAY
# ============================================================

PORT = int(
    os.environ.get(
        "PORT",
        "8000",
    )
)

DATA_DIR = Path(
    os.environ.get(
        "RAILWAY_VOLUME_MOUNT_PATH",
        os.environ.get(
            "DATA_DIR",
            "./data",
        ),
    )
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATA_FILE = DATA_DIR / "vodiwalker_state.json"
SECRET_FILE = DATA_DIR / "vodiwalker_secret.key"


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOCKS
# ============================================================

SAVE_LOCK = asyncio.Lock()
LINKS_LOCK = asyncio.Lock()
SUBS_LOCK = asyncio.Lock()
SESSIONS_LOCK = asyncio.Lock()


# ============================================================
# SECRET
# ============================================================

def load_or_create_secret() -> str:
    env_secret = os.environ.get("SECRET_KEY")

    if env_secret:
        return env_secret

    try:
        if SECRET_FILE.exists():
            existing = (
                SECRET_FILE
                .read_text(
                    encoding="utf-8"
                )
                .strip()
            )

            if existing:
                return existing

        generated = secrets.token_urlsafe(48)

        SECRET_FILE.write_text(
            generated,
            encoding="utf-8",
        )

        return generated

    except Exception as exc:
        logger.warning(
            "Could not persist SECRET_KEY: %s",
            exc,
        )

        return secrets.token_urlsafe(48)


SECRET_KEY = load_or_create_secret()


# ============================================================
# CONFIG
# ============================================================

CONFIG = {
    "port": PORT,
    "secret": SECRET_KEY,
    "host": os.environ.get(
        "RAILWAY_PUBLIC_DOMAIN",
        "localhost",
    ),
   
    "tcp_public_host": os.environ.get("TCP_PUBLIC_HOST", "").strip(),
    "tcp_public_port": os.environ.get("TCP_PUBLIC_PORT", "").strip(),
}


# ============================================================
# STATE
# ============================================================

LINKS: dict = {}
SUBS: dict = {}
# Per-subscription live usage samples. Values come from the real link used_bytes field.
SUB_USAGE_HISTORY = defaultdict(lambda: deque(maxlen=144))
USAGE_PERSIST_TASK = None
SESSIONS: dict = {}
connections: dict = {}
CATEGORIES: dict = {}
DAILY_STATS: dict = {}  # "YYYY-MM-DD" -> {"traffic_bytes":.., "new_links":.., "orders":.., "stars":..}
DAILY_STATS_LOCK = asyncio.Lock()


def _today_key() -> str:
    now = datetime.now(IRAN_TZ) if IRAN_TZ else datetime.now()
    return now.strftime("%Y-%m-%d")


def bump_daily_stat(field: str, amount=1):
    """Increment a counter in today's reporting bucket (best-effort, in-memory)."""
    try:
        key = _today_key()
        bucket = DAILY_STATS.setdefault(
            key, {"traffic_bytes": 0, "new_links": 0, "orders": 0, "stars": 0}
        )
        bucket[field] = bucket.get(field, 0) + amount
        # keep only the last 180 days to avoid unbounded growth
        if len(DAILY_STATS) > 180:
            for old_key in sorted(DAILY_STATS.keys())[: len(DAILY_STATS) - 180]:
                DAILY_STATS.pop(old_key, None)
    except Exception:
        pass

stats = {
    "total_bytes": 0,
    "total_requests": 0,
    "total_errors": 0,
    "start_time": time.time(),
}

_telemetry_lock = asyncio.Lock()
_telemetry_prev = {"ts": time.time(), "rx": 0, "tx": 0}


def _pct(v):
    try:
        return round(float(v), 1)
    except Exception:
        return 0.0


def _human_uptime(seconds):
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours:02d}:{minutes:02d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

error_logs = deque(maxlen=100)
activity_logs = deque(maxlen=250)

hourly_traffic = defaultdict(int)
# Real server telemetry samples used by the dashboard charts.
# Samples are collected from psutil; no placeholder/synthetic values are generated.
TELEMETRY_HISTORY = deque(maxlen=90)

http_client: httpx.AsyncClient | None = None


# ============================================================
# PROTOCOL
# ============================================================

PROTOCOLS = (
    "vless-ws",
    "vless-tcp",
    "xhttp-packet-up",
    "xhttp-stream-up",
    "xhttp-stream-one",
    "vmess-ws",
    "trojan-ws",
)

# این پروتکل‌ها روی همان پورت HTTP/WebSocket برنامه (پشت TLS ری‌ورس‌پروکسی یا Railway)
# سرو می‌شن و واقعاً روی سرور پیاده‌سازی شده‌ن.
REAL_TRANSPORT_PROTOCOLS = {
    "vless-ws", "xhttp-packet-up", "xhttp-stream-up",
}
# vless-tcp هم واقعی و پیاده‌سازی‌شده‌ست ولی روی یک پورت TCP خام و جداگانه
# (به‌صورت پیش‌فرض 6543، قابل تغییر با TCP_LISTEN_PORT) — نه پورت HTTP اصلی.
REAL_RAW_TCP_PROTOCOLS = {"vless-tcp"}
# همه‌ی پروتکل‌های دمو/غیرفعال از پنل حذف شده‌اند — هر چیزی که در PROTOCOLS باشد واقعاً کار می‌کند.
NON_FUNCTIONAL_DEMO_PROTOCOLS = {"vmess-ws", "trojan-ws"}

# Protocols that this project actually serves itself. VMess/Trojan entries may
# still be generated as client-side links, but they are NOT advertised as live
# listeners because this backend has no VMess/Trojan inbound parser.
LIVE_PROTOCOLS = REAL_TRANSPORT_PROTOCOLS | REAL_RAW_TCP_PROTOCOLS

PROTOCOL_LABELS = {
    "vless-ws": "VLESS WebSocket",
    "vless-tcp": "VLESS TCP (خام)",
    "xhttp-packet-up": "XHTTP Packet Up",
    "xhttp-stream-up": "XHTTP Stream Up",
    "xhttp-stream-one": "XHTTP Stream One",
    "vmess-ws": "VMess WebSocket",
    "trojan-ws": "Trojan WebSocket",
    "manual": "پروتکل دستی (سفارشی)",
}

PROTOCOL_ALIASES = {
    "vmess": "vmess-ws", "trojan": "trojan-ws", "ss": "shadowsocks",
    "socks": "socks5", "hy2": "hysteria2", "hysteria": "hysteria2",
}

DEFAULT_PROTOCOL = "vless-ws"

# نگاشت هر پروتکل غیر-دستی (manual) به Network/Security واقعی‌ای که در لینک
# نهایی (generate_vless_link) استفاده می‌شود. این فقط برای نمایش صحیح در پنل
# است (تگ‌های "ws/tls" و ...)؛ چون قبلاً این مقادیر همیشه روی مقدار پیش‌فرض
# فیلدهای دستی (tcp/none) می‌افتادند، حتی برای پروتکل‌هایی که واقعاً ws+tls بودند.
PROTOCOL_NETWORK_SECURITY = {
    "vless-ws": ("ws", "tls"),
    "vless-tcp": ("tcp", "none"),
    "xhttp-packet-up": ("xhttp", "tls"),
    "xhttp-stream-up": ("xhttp", "tls"),
    "xhttp-stream-one": ("xhttp", "tls"),
    "vmess-ws": ("ws", "tls"),
    "trojan-ws": ("ws", "tls"),
}

FINGERPRINTS = (
    "chrome",
    "firefox",
    "safari",
    "ios",
    "android",
    "edge",
    "360",
    "qq",
    "random",
    "randomized",
)

DEFAULT_FINGERPRINT = "chrome"

DEFAULT_ALPN_BY_PROTOCOL = {
    "vless-ws": "http/1.1",
    "xhttp-packet-up": "h2,http/1.1",
    "xhttp-stream-up": "h2,http/1.1",
    "xhttp-stream-one": "h2,http/1.1",
}

DEFAULT_PORT = 443
MIN_PORT = 1
MAX_PORT = 65535

DEFAULT_SPEED_LIMIT = 0


# ============================================================
# MANUAL PROTOCOL BUILDER (پروتکل دستی — مثل پنل‌های 3x-ui/Sanaei)
# ============================================================


MANUAL_BASE_PROTOCOLS = ("vless", "vmess", "trojan", "shadowsocks")

MANUAL_BASE_PROTOCOL_LABELS = {
    "vless": "VLESS",
    "vmess": "VMess",
    "trojan": "Trojan",
    "shadowsocks": "Shadowsocks",
}

NETWORKS = ("tcp", "ws", "grpc", "xhttp")

NETWORK_LABELS = {
    "tcp": "TCP",
    "ws": "WebSocket (ws)",
    "grpc": "gRPC",
    "xhttp": "XHTTP",
}

SECURITIES = ("none", "tls", "reality")

SECURITY_LABELS = {
    "none": "بدون امنیت (None)",
    "tls": "TLS",
    "reality": "Reality",
}

XHTTP_MODES = ("auto", "packet-up", "stream-up", "stream-one")
SHADOWSOCKS_METHODS = ("chacha20-ietf-poly1305", "aes-128-gcm", "aes-256-gcm", "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm")

# ترکیب‌هایی که همین پنل واقعاً به‌صورت زنده سرو می‌کند (بدون نیاز به Xray-core
# جداگانه). سایر ترکیب‌ها (مثل هر چیزی با Reality) فقط لینک/کانفیگ برای استفاده
# روی یک نود Xray-core واقعی می‌سازند و به همین دلیل در پنل با یک نشان
# «فقط ساخت لینک» مشخص می‌شوند — این محدودیت صادقانه در UI نشان داده می‌شود.
MANUAL_LIVE_COMBOS = {
    ("ws", "tls"),
    ("ws", "none"),
    ("xhttp", "tls"),
    ("xhttp", "none"),
    ("tcp", "none"),
}


def normalize_protocol(protocol: str | None) -> str:
    value = str(protocol or DEFAULT_PROTOCOL).strip().lower()
    value = PROTOCOL_ALIASES.get(value, value)
    if value == "manual":
        return value
    return value if value in PROTOCOLS else DEFAULT_PROTOCOL


def normalize_network(network: str | None) -> str:
    value = str(network or "tcp").strip().lower()
    return value if value in NETWORKS else "tcp"


def normalize_security(security: str | None) -> str:
    value = str(security or "none").strip().lower()
    return value if value in SECURITIES else "none"


def normalize_xhttp_mode(mode: str | None) -> str:
    value = str(mode or "auto").strip().lower()
    return value if value in XHTTP_MODES else "auto"


def normalize_base_protocol(value: str | None) -> str:
    v = str(value or "vless").strip().lower()
    return v if v in MANUAL_BASE_PROTOCOLS else "vless"


def protocol_display_label(link: dict) -> str:
    """برچسب نمایشی پروتکل برای جدول‌ها و گزارش‌ها.
    برای کانفیگ‌های دستی به‌صورت «VLESS · WebSocket · TLS» نمایش داده می‌شود."""
    protocol = link.get("protocol", DEFAULT_PROTOCOL)
    if protocol != "manual":
        return PROTOCOL_LABELS.get(protocol, protocol)
    base = MANUAL_BASE_PROTOCOL_LABELS.get(normalize_base_protocol(link.get("base_protocol")), "VLESS")
    network = NETWORK_LABELS.get(normalize_network(link.get("network")), "TCP")
    security = SECURITY_LABELS.get(normalize_security(link.get("security")), "بدون امنیت")
    if base == "Shadowsocks":
        return f"Shadowsocks · {network}"
    return f"{base} · {network} · {security}"


# ============================================================
# LOGGING
# ============================================================

def log_activity(
    kind: str,
    message: str,
    level: str = "info",
):
    activity_logs.append(
        {
            "kind": kind,
            "level": level,
            "message": message,
            "time": datetime.now().isoformat(),
        }
    )


# ============================================================
# HELPERS
# ============================================================

def escape_html(value) -> str:
    return (
        str(
            value
            if value is not None
            else ""
        )
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def safe_int(
    value,
    default=0,
    minimum=0,
    maximum=None,
):
    try:
        number = int(value)
    except Exception:
        number = default

    if number < minimum:
        number = minimum

    if maximum is not None and number > maximum:
        number = maximum

    return number


def safe_float(
    value,
    default=0.0,
    minimum=0.0,
):
    try:
        number = float(value)
    except Exception:
        number = default

    return max(
        minimum,
        number,
    )


def generate_uuid():
    value = secrets.token_hex(16)

    return (
        f"{value[:8]}-"
        f"{value[8:12]}-"
        f"{value[12:16]}-"
        f"{value[16:20]}-"
        f"{value[20:32]}"
    )


def random_config_name(existing=None):
    existing = existing or set()
    alphabet = string.ascii_lowercase + string.digits
    for _ in range(80):
        length = secrets.randbelow(6) + 8
        name = "".join(secrets.choice(alphabet) for _ in range(length))
        if name not in existing and name and not name[0].isdigit():
            return name
    return secrets.token_hex(6)

def sanitize_config_name(name: str) -> str:
    if not name:
        return random_config_name()
    cleaned = "".join(ch for ch in str(name) if ch.isascii() and ch.isalnum())
    if not cleaned or cleaned[0].isdigit():
        cleaned = ("a" + cleaned) if cleaned else random_config_name()
    return cleaned[:40]

def auto_config_name() -> str:
    return random_config_name()


def now_ir():
    if IRAN_TZ:
        return datetime.now(IRAN_TZ)

    return datetime.now()


def uptime():
    seconds = int(
        time.time()
        - stats["start_time"]
    )

    h = seconds // 3600

    m = (
        seconds
        % 3600
    ) // 60

    s = (
        seconds
        % 60
    )

    return (
        f"{h:02d}:"
        f"{m:02d}:"
        f"{s:02d}"
    )


def fmt_bytes(value: int):
    value = int(
        value or 0
    )

    if value < 1024:
        return f"{value} B"

    if value < 1024 ** 2:
        return (
            f"{value / 1024:.1f} KB"
        )

    if value < 1024 ** 3:
        return (
            f"{value / 1024 ** 2:.2f} MB"
        )

    return (
        f"{value / 1024 ** 3:.2f} GB"
    )


def parse_size_to_bytes(
    value: float,
    unit: str,
):
    if value <= 0:
        return 0

    unit = (
        unit
        or "GB"
    ).upper()

    if unit == "TB":
        return int(
            value
            * 1024 ** 4
        )

    if unit == "GB":
        return int(
            value
            * 1024 ** 3
        )

    if unit == "MB":
        return int(
            value
            * 1024 ** 2
        )

    if unit == "KB":
        return int(
            value
            * 1024
        )

    return int(value)


def parse_speed_to_bytes(
    value: float,
    unit: str,
):
    if value <= 0:
        return 0

    unit = (
        unit
        or "MBIT"
    ).upper()

    if unit == "MBIT":
        return int(
            value
            * 1024
            * 1024
            / 8
        )

    if unit == "KB":
        return int(
            value * 1024
        )

    if unit == "MB":
        return int(
            value
            * 1024
            * 1024
        )

    return int(value)


def is_link_expired(
    link: dict,
):
    expiry = link.get(
        "expires_at"
    )

    if not expiry:
        return False

    try:
        return (
            datetime.now()
            > datetime.fromisoformat(
                expiry
            )
        )

    except Exception:
        return False


def is_link_allowed(
    link: dict | None,
):
    if link is None:
        return False

    if not link.get(
        "active",
        True,
    ):
        return False

    if is_link_expired(link):
        return False

    limit = int(
        link.get(
            "limit_bytes",
            0,
        )
        or 0
    )

    used = int(
        link.get(
            "used_bytes",
            0,
        )
        or 0
    )

    if (
        limit > 0
        and used >= limit
    ):
        return False

    return True


def unique_ips_for_uuid(
    uuid: str,
):
    return {
        connection.get("ip")
        for connection in connections.values()
        if connection.get("uuid") == uuid
        and connection.get("ip")
    }


def client_ip(
    request: Request,
):
    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:
        return (
            forwarded
            .split(",")[0]
            .strip()
        )

    real = request.headers.get(
        "x-real-ip"
    )

    if real:
        return real.strip()

    if request.client:
        return request.client.host

    return "unknown"


def is_ip_allowed(
    link: dict | None,
    uuid: str,
    ip: str,
):
    if link is None:
        return False

    limit = int(
        link.get(
            "ip_limit",
            0,
        )
        or 0
    )

    if limit <= 0:
        return True

    ips = unique_ips_for_uuid(uuid)

    if ip in ips:
        return True

    return len(ips) < limit


def _split_base_url(raw: str):
    """آدرس عمومی ذخیره‌شده رو به (scheme, host) تجزیه می‌کنه. ورودی می‌تونه
    با یا بدون scheme باشه (مثلاً 'panel.example.com' یا 'https://panel.example.com')."""
    raw = (raw or "").strip()
    if not raw:
        return None, None
    scheme = "https"
    rest = raw
    if "://" in raw:
        scheme, rest = raw.split("://", 1)
        scheme = scheme.strip().lower() or "https"
    host = rest.split("/", 1)[0].split(":")[0].strip()
    return (scheme if scheme in ("http", "https") else "https"), (host or None)


def get_host(
    request: Request | None = None,
) -> str:
    # اولویت اول: آدرس عمومی صریحی که در تنظیمات پنل ثبت شده (پایدار، مستقل از
    # اینکه درخواست از کجا اومده — پروکسی، آی‌پی داخلی، هلث‌چک و ...).
    _, override_host = _split_base_url(CONFIG.get("public_base_url"))
    if override_host:
        return override_host

    if request is not None:
        forwarded = request.headers.get(
            "x-forwarded-host"
        )

        normal = request.headers.get(
            "host"
        )

        host = (
            forwarded
            or normal
        )

        if host:
            # توجه: دیگه CONFIG["host"] رو اینجا آپدیت نمی‌کنیم؛ این یک متغیر سراسری
            # مشترک بین همه‌ی درخواست‌ها بود و هر درخواست با Host نادرست (هلث‌چک،
            # اسکنر، وبهوک) می‌تونست لینک‌های بعدیِ همه رو خراب کنه.
            return host.split(":")[0].strip()

    railway_domain = os.environ.get(
        "RAILWAY_PUBLIC_DOMAIN"
    )

    if railway_domain:
        return railway_domain

    return CONFIG["host"]


def get_scheme() -> str:
    """scheme (http/https) که باید برای ساخت لینک‌های ساب استفاده بشه."""
    scheme, host = _split_base_url(CONFIG.get("public_base_url"))
    if host:
        return scheme
    return "https"


def _tcp_listen_port_snapshot() -> int:
    try:
        import tcp_relay
        return tcp_relay.TCP_LISTEN_PORT
    except Exception:
        return int(os.environ.get("TCP_LISTEN_PORT", "6543"))


def _bot_settings_snapshot() -> dict:
    """وضعیت فعلی ربات فروش رو برمی‌گردونه؛ اگه ماژول ربات هنوز ایمپورت نشده
    یا مشکلی داشته باشه، مقدار خالی/امن برمی‌گردونه (این نباید کل پنل رو خراب کنه)."""
    try:
        import telegram_bot
        return telegram_bot.current_config()
    except Exception:
        return {"bot_token": "", "admin_ids": "", "running": False}


# ============================================================
# PASSWORD
# ============================================================

def hash_password(
    password: str,
) -> str:

    payload = (
        password
        + SECRET_KEY
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin").strip() or "admin"
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

AUTH = {
    "username": DEFAULT_ADMIN_USERNAME,
    "password_hash":
        hash_password(
            DEFAULT_ADMIN_PASSWORD
        )
}

# ============================================================
# MULTI-ADMIN (sub-admins beyond the owner account)
# ============================================================
# The "owner" account is always backed by AUTH["password_hash"] above
# (fully backward compatible with older single-admin deployments).
# Additional named admin accounts live here and can be managed from
# the "مدیریت ادمین‌ها" tab in the dashboard.

ADMINS: dict = {}

# ============================================================
# ADMIN REGISTRATION REQUESTS ("ثبت‌نام ادمینی" از صفحه لاگین)
# ============================================================
# کاربری که می‌خواهد ادمین شود، فقط نام و آیدی تلگرام خود را از صفحه
# لاگین ارسال می‌کند. درخواست او اینجا به‌صورت pending ذخیره می‌شود تا
# مالک پنل از بخش «مدیریت حساب‌ها» آن را ببیند، تصمیم بگیرد چه دسترسی‌ها
# و چه رمز/نام‌کاربری‌ای به او بدهد، و در صورت تایید حساب ادمین واقعی
# برایش ساخته شود.
ADMIN_REQUESTS: dict = {}
ADMIN_REQUEST_RATE: dict = {}  # ip -> last submit timestamp (ضد اسپم ساده)
ADMIN_REQUEST_COOLDOWN_SECONDS = 60
ADMIN_REQUESTS_LOCK = asyncio.Lock()

ALL_PERMISSIONS = {
    "dashboard": "مشاهده داشبورد",
    "inbounds": "مدیریت اینباند و کلاینت",
    "clients": "ساخت کلاینت (بخش جدا)",
    "subscriptions": "مدیریت سابسکریپشن",
    "categories": "مدیریت دسته‌بندی",
    "plans": "مدیریت پلن فروش",
    "reports": "گزارش‌ها",
    "messages": "مرکز پیام و خطا",
    "bot": "مدیریت ربات",
    "admins": "مدیریت ادمین‌ها",
    "settings": "تنظیمات پنل",
}

BOT_TEXTS = {
    "welcome": "🛡 <b>VodiWalker Control Center</b>\n\nاز منوی زیر عملیات موردنظر را انتخاب کنید.",
    "admin_menu": "🛠 <b>مدیریت پنل</b>\n\nساخت اینباند، کلاینت، گروه ساب و مدیریت فروش از همین‌جا در دسترس است.",
    "config_created": "✅ کانفیگ با موفقیت ساخته شد.",
    "config_deleted": "🗑 کانفیگ حذف شد.",
    "config_disabled": "⛔ کانفیگ غیرفعال شد.",
    "config_enabled": "✅ کانفیگ فعال شد.",
    "store_intro": "🛒 <b>فروشگاه</b>\n\nپلن موردنظر را انتخاب کنید.",
    "payment_success": "🎉 پرداخت با موفقیت انجام شد.\n\nاشتراک شما آماده است.",
}

def get_bot_text(key: str, fallback: str = "") -> str:
    return str(BOT_TEXTS.get(key, fallback))

def permissions_for_admin(admin_id: str) -> set[str]:
    if admin_id == "owner":
        return set(ALL_PERMISSIONS)
    a = ADMINS.get(admin_id) or {}
    return set(a.get("permissions") or {"dashboard"})

async def require_permission(request: Request, permission: str):
    token = request.cookies.get(SESSION_COOKIE)
    info = await get_session_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="unauthorized")
    if permission not in permissions_for_admin(info.get("admin_id", "owner")):
        raise HTTPException(status_code=403, detail="دسترسی این قابلیت برای این ادمین فعال نیست")
    return info


def verify_admin_credentials(username: str | None, password: str):
    """Returns (ok, admin_id, role, display_name)."""
    username = (username or "").strip()
    password = password or ""

    if not username or username.lower() in {"owner", AUTH.get("username", DEFAULT_ADMIN_USERNAME).lower()}:
        if username and username.lower() not in {"owner", AUTH.get("username", DEFAULT_ADMIN_USERNAME).lower()}:
            return False, None, None, None
        if hash_password(password) == AUTH["password_hash"]:
            return True, "owner", "owner", AUTH.get("username", DEFAULT_ADMIN_USERNAME)
        return False, None, None, None

    for admin_id, admin in ADMINS.items():
        if not admin.get("active", True):
            continue
        if admin.get("username", "").lower() == username.lower():
            if hash_password(password) == admin.get("password_hash"):
                return True, admin_id, admin.get("role", "admin"), admin.get("username")
            return False, None, None, None

    return False, None, None, None


# ============================================================
# LOGIN BRUTE-FORCE PROTECTION
# ============================================================
# Maximum failed login attempts per IP inside the rolling window.
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_LOCKOUT_SECONDS = 15 * 60
LOGIN_MIN_PASSWORD_LENGTH = 6

LOGIN_FAILURES = defaultdict(deque)
LOGIN_LOCKED_UNTIL = {}


def _cleanup_login_state(ip: str, now: float | None = None):
    now = now if now is not None else time.time()

    locked_until = LOGIN_LOCKED_UNTIL.get(ip, 0)
    if locked_until and locked_until <= now:
        LOGIN_LOCKED_UNTIL.pop(ip, None)

    failures = LOGIN_FAILURES.get(ip)
    if not failures:
        return

    cutoff = now - LOGIN_WINDOW_SECONDS
    while failures and failures[0] <= cutoff:
        failures.popleft()

    if not failures:
        LOGIN_FAILURES.pop(ip, None)


def login_is_blocked(ip: str):
    now = time.time()
    _cleanup_login_state(ip, now)

    locked_until = LOGIN_LOCKED_UNTIL.get(ip, 0)
    if locked_until > now:
        return True, max(1, int(locked_until - now))

    return False, 0


def register_login_failure(ip: str):
    now = time.time()
    _cleanup_login_state(ip, now)

    failures = LOGIN_FAILURES.setdefault(ip, deque())
    failures.append(now)

    if len(failures) >= LOGIN_MAX_ATTEMPTS:
        LOGIN_LOCKED_UNTIL[ip] = now + LOGIN_LOCKOUT_SECONDS
        failures.clear()
        log_activity(
            "auth",
            f"IP به دلیل تلاش‌های متعدد ورود ناموفق به مدت {LOGIN_LOCKOUT_SECONDS // 60} دقیقه مسدود شد: {ip}",
            "err",
        )
        return True, LOGIN_LOCKOUT_SECONDS

    return False, max(0, LOGIN_MAX_ATTEMPTS - len(failures))


def clear_login_failures(ip: str):
    LOGIN_FAILURES.pop(ip, None)
    LOGIN_LOCKED_UNTIL.pop(ip, None)


# ============================================================
# SESSION
# ============================================================

SESSION_COOKIE = "vodiwalker_session"

SESSION_TTL = (
    60
    * 60
    * 24
    * 365
)


async def create_session(admin_id: str = "owner", role: str = "owner") -> str:

    token = secrets.token_urlsafe(48)

    async with SESSIONS_LOCK:
        SESSIONS[token] = {
            "exp": time.time() + SESSION_TTL,
            "admin_id": admin_id,
            "role": role,
            "permissions": sorted(permissions_for_admin(admin_id)),
        }

    return token


def _session_expiry(entry) -> float:
    if isinstance(entry, dict):
        return entry.get("exp", 0)
    return entry or 0


async def is_valid_session(
    token: str | None,
) -> bool:

    if not token:
        return False

    async with SESSIONS_LOCK:

        entry = SESSIONS.get(token)

        if entry is None:
            return False

        if _session_expiry(entry) < time.time():

            SESSIONS.pop(
                token,
                None,
            )

            return False

        return True


async def get_session_info(token: str | None):
    if not token:
        return None

    async with SESSIONS_LOCK:
        entry = SESSIONS.get(token)

        if entry is None:
            return None

        if _session_expiry(entry) < time.time():
            SESSIONS.pop(token, None)
            return None

        if isinstance(entry, dict):
            return dict(entry)

        return {"exp": entry, "admin_id": "owner", "role": "owner"}


async def require_owner(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    info = await get_session_info(token)

    if not info:
        raise HTTPException(status_code=401, detail="unauthorized")

    if info.get("role") != "owner":
        raise HTTPException(
            status_code=403,
            detail="فقط مالک پنل به این بخش دسترسی دارد",
        )

    return token


async def destroy_session(
    token: str | None,
):
    if not token:
        return

    async with SESSIONS_LOCK:
        SESSIONS.pop(
            token,
            None,
        )


async def require_auth(
    request: Request,
):
    token = request.cookies.get(
        SESSION_COOKIE
    )

    info = await get_session_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="unauthorized")
    if info.get("admin_id") != "owner":
        path = request.url.path
        permission = "dashboard"
        if path.startswith("/api/links") or path.startswith("/api/protocols") or path.startswith("/api/reality"):
            permission = "inbounds"
        elif path.startswith("/api/sub") or path.startswith("/sub"):
            permission = "subscriptions"
        elif path.startswith("/api/categories"):
            permission = "categories"
        elif path.startswith("/api/plans"):
            permission = "plans"
        elif path.startswith("/api/reports"):
            permission = "reports"
        elif path.startswith("/api/errors") or path.startswith("/api/activity"):
            permission = "messages"
        elif path.startswith("/api/settings/bot") or path.startswith("/api/bot"):
            permission = "bot"
        elif path.startswith("/api/settings"):
            permission = "settings"
        elif path.startswith("/api/telemetry") or path.startswith("/api/network"):
            permission = "dashboard"
        if permission not in permissions_for_admin(info.get("admin_id", "")):
            raise HTTPException(status_code=403, detail="دسترسی این قابلیت برای این ادمین فعال نیست")
    return token


def set_auth_cookie(
    response,
    request: Request,
    token: str,
):
    forwarded_proto = (
        request.headers
        .get(
            "x-forwarded-proto",
            "",
        )
        .lower()
    )

    is_https = (
        forwarded_proto == "https"
        or request.url.scheme == "https"
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_TTL,
        httponly=True,
        samesite="lax",
        path="/",
        secure=is_https,
    )


# ============================================================
# VLESS LINK GENERATION
# ============================================================

def generate_vless_link(
    uuid: str, host: str, remark: str = "VodiWalker",
    protocol: str = DEFAULT_PROTOCOL, fingerprint: str | None = None,
    alpn: str | None = None, port: int | None = None,
):
    protocol = normalize_protocol(protocol)
    fp = (fingerprint or DEFAULT_FINGERPRINT).strip().lower()
    if fp not in FINGERPRINTS: fp = DEFAULT_FINGERPRINT
    port_value = safe_int(port, DEFAULT_PORT, MIN_PORT, MAX_PORT)
    alpn_value = (alpn or DEFAULT_ALPN_BY_PROTOCOL.get(protocol, "http/1.1")).strip()
    label = quote(str(remark or "VodiWalker"), safe="")
    if protocol == "vless-ws":
        q = {"encryption":"none","security":"tls","type":"ws","host":host,"path":f"/ws/{uuid}","sni":host,"fp":fp,"alpn":alpn_value}
        return "vless://" + uuid + "@" + host + ":" + str(port_value) + "?" + "&".join(f"{k}={quote(str(v), safe=',/') }" for k,v in q.items()) + "#" + label
    if protocol == "vless-tcp":
        # VLESS خام روی TCP — این روی پورت HTTP اصلی سرو نمی‌شه، بلکه روی یک پورت TCP
        # مجزا (tcp_relay.py) که آدرس/پورت عمومیش از تنظیمات پنل (Settings) خونده می‌شه
        # تا وقتی روی Railway (یا هر جای دیگه) با TCP Proxy جداگانه دیپلوی شد، خودت
        # می‌تونی آدرس واقعی رو دستی وارد کنی.
        tcp_host = (CONFIG.get("tcp_public_host") or "").strip() or host
        tcp_port = safe_int(CONFIG.get("tcp_public_port"), port_value, MIN_PORT, MAX_PORT)
        q = {"encryption":"none","security":"none","type":"tcp","headerType":"none"}
        return "vless://" + uuid + "@" + tcp_host + ":" + str(tcp_port) + "?" + "&".join(f"{k}={quote(str(v), safe=',/') }" for k,v in q.items()) + "#" + label
    if protocol.startswith("xhttp-"):
        mode = protocol.replace("xhttp-", "")
        q = {"encryption":"none","security":"tls","type":"xhttp","mode":mode,"host":host,"path":f"/xhttp-siz10/{mode}/{uuid}","sni":host,"fp":fp,"alpn":alpn_value}
        return "vless://" + uuid + "@" + host + ":" + str(port_value) + "?" + "&".join(f"{k}={quote(str(v), safe=',/') }" for k,v in q.items()) + "#" + label
    if protocol == "vmess-ws":
        raw = {"v":"2","ps":remark,"add":host,"port":port_value,"id":uuid,"aid":0,"scy":"auto","net":"ws","type":"none","host":host,"path":f"/ws/{uuid}","tls":"tls","sni":host,"fp":fp}
        return "vmess://" + base64.b64encode(json.dumps(raw,separators=(",",":"),ensure_ascii=False).encode()).decode()
    if protocol == "trojan-ws":
        return f"trojan://{uuid}@{host}:{port_value}?security=tls&type=ws&host={quote(host)}&path={quote('/ws/'+uuid)}&sni={quote(host)}#{label}"
    return f"vless://{uuid}@{host}:{port_value}"

# ============================================================
# SUBSCRIPTION REMARK TEMPLATE (configurable, Settings -> Subscription Template)
# ============================================================
def build_config_remark(link: dict, uid: str) -> str:
    """می‌سازه چه متنی به‌عنوان نام کانفیگ (#remark) داخل اپ کاربر دیده بشه.
    پیش‌فرض دقیقاً مثل قبل فقط «نام» است؛ مالک پنل از تب تنظیمات می‌تونه
    نمایش حجم/آی‌دی/نام اینباند رو هم فعال کنه."""
    show_name = bool(CONFIG.get("sub_remark_show_name", True))
    show_volume = bool(CONFIG.get("sub_remark_show_volume", False))
    show_id = bool(CONFIG.get("sub_remark_show_id", False))
    show_inbound = bool(CONFIG.get("sub_remark_show_inbound", False))

    name = str(link.get("label") or "Config").strip() or "Config"
    parts: list[str] = []

    if show_name:
        parts.append(name)

    if show_volume:
        try:
            limit_bytes = int(link.get("limit_bytes") or 0)
        except Exception:
            limit_bytes = 0
        parts.append(fmt_bytes(limit_bytes) if limit_bytes > 0 else "Unlimited")

    if show_id:
        parts.append(str(uid)[:8])

    if show_inbound:
        parent_id = link.get("parent_inbound_id")
        parent = LINKS.get(parent_id) if parent_id else None
        inbound_label = str((parent or {}).get("label") or "").strip()
        if inbound_label:
            parts.append(inbound_label)

    return " | ".join(p for p in parts if p) or name


def build_manual_uri(
    link: dict,
    uid: str,
    host: str,
    port_override: int | None = None,
) -> str:
    """ساخت لینک کانفیگ برای حالت پروتکل دستی (Manual) — دقیقاً مثل پنل‌های
    3x-ui/Sanaei: پروتکل پایه + شبکه (Network) + امنیت (Security) + فیلدهای
    دستی (آدرس، پورت، مسیر، هاست هدر، SNI، Reality و ...) هر کدام جدا انتخاب
    می‌شن و لینک نهایی از روی آن‌ها ساخته می‌شود."""

    base_protocol = normalize_base_protocol(link.get("base_protocol"))
    network = normalize_network(link.get("network"))
    security = normalize_security(link.get("security"))

    remark = build_config_remark(link, uid)
    label = quote(remark, safe="")

    fp = (link.get("fingerprint") or DEFAULT_FINGERPRINT).strip().lower()
    if fp not in FINGERPRINTS:
        fp = DEFAULT_FINGERPRINT

    port_value = safe_int(
        port_override if port_override is not None else link.get("port"),
        DEFAULT_PORT, MIN_PORT, MAX_PORT,
    )

    address = (str(link.get("address") or "")).strip() or host
    default_alpn = "h2,http/1.1" if network == "xhttp" else "http/1.1"
    alpn_value = (str(link.get("alpn") or default_alpn)).strip()
    path = (str(link.get("path") or "")).strip() or f"/{network}/{uid}"
    host_header = (str(link.get("host_header") or "")).strip() or address
    sni = (str(link.get("sni") or "")).strip() or address
    flow = (str(link.get("flow") or "")).strip()
    grpc_service = (str(link.get("grpc_service_name") or "")).strip() or uid
    xhttp_mode = normalize_xhttp_mode(link.get("xhttp_mode"))

    q: dict[str, str] = {}
    if base_protocol == "vless":
        q["encryption"] = "none"

    if security == "tls":
        q["security"] = "tls"
        q["sni"] = sni
        q["fp"] = fp
        q["alpn"] = alpn_value
        if link.get("allow_insecure"):
            q["allowInsecure"] = "1"
    elif security == "reality":
        q["security"] = "reality"
        q["sni"] = sni
        q["fp"] = fp
        q["pbk"] = (str(link.get("reality_public_key") or "")).strip()
        q["sid"] = (str(link.get("reality_short_id") or "")).strip()
        q["spx"] = (str(link.get("reality_spider_x") or "")).strip() or "/"
    else:
        q["security"] = "none"

    if network == "ws":
        q["type"] = "ws"
        q["path"] = path
        q["host"] = host_header
    elif network == "grpc":
        q["type"] = "grpc"
        q["serviceName"] = grpc_service
        q["mode"] = (str(link.get("grpc_mode") or "gun")).strip() or "gun"
    elif network == "xhttp":
        q["type"] = "xhttp"
        q["mode"] = xhttp_mode
        q["path"] = path
        q["host"] = host_header
    else:
        q["type"] = "tcp"
        header_type = (str(link.get("header_type") or "")).strip()
        if header_type:
            q["headerType"] = header_type
        if flow:
            q["flow"] = flow

    if base_protocol == "shadowsocks":
        method = str(link.get("ss_method") or "chacha20-ietf-poly1305").strip()
        password = str(link.get("ss_password") or uid).strip()
        if not method:
            method = "chacha20-ietf-poly1305"
        userinfo = f"{method}:{password}"
        token = base64.urlsafe_b64encode(userinfo.encode()).decode().rstrip("=")
        return f"ss://{token}@{address}:{port_value}#{label}"

    if base_protocol == "vmess":
        raw = {
            "v": "2", "ps": remark, "add": address, "port": port_value, "id": uid,
            "aid": 0, "scy": "auto", "net": network, "type": "none",
            "host": host_header if network in ("ws", "xhttp") else "",
            "path": grpc_service if network == "grpc" else path,
            "tls": security if security != "none" else "",
            "sni": sni, "fp": fp,
        }
        return "vmess://" + base64.b64encode(
            json.dumps(raw, separators=(",", ":"), ensure_ascii=False).encode()
        ).decode()

    scheme = "trojan" if base_protocol == "trojan" else "vless"
    qs = "&".join(f"{k}={quote(str(v), safe=',/')}" for k, v in q.items() if v not in (None, ""))
    return f"{scheme}://{uid}@{address}:{port_value}?{qs}#{label}"


def vless_link_for_link(
    link: dict,
    uid: str,
    host: str,
    port_override: int | None = None,
):
    protocol = normalize_protocol(link.get("protocol", DEFAULT_PROTOCOL))
    if protocol == "manual":
        return build_manual_uri(link, uid, host, port_override=port_override)
    return generate_vless_link(
        uid,
        host,
        remark=str(link.get("label") or "Config"),
        protocol=protocol,
        fingerprint=link.get(
            "fingerprint",
            DEFAULT_FINGERPRINT,
        ),
        alpn=link.get(
            "alpn"
        ),
        port=port_override if port_override is not None else link.get(
            "port",
            DEFAULT_PORT,
        ),
    )


def get_link_info(
    link: dict,
    uid: str,
    host: str,
):
    connected_count = len(unique_ips_for_uuid(uid))
    is_active = is_link_allowed(link)
    limit_b = int(link.get("limit_bytes", 0) or 0)
    used_b = int(link.get("used_bytes", 0) or 0)
    is_expired = is_link_expired(link) or (limit_b > 0 and used_b >= limit_b)
    if not is_active or is_expired:
        status_color = "red"
    elif connected_count > 0:
        status_color = "green"
    else:
        status_color = "gray"
    clean_ips = link.get("clean_ips") or []
    cfg_count = int(link.get("config_count") or 1)
    show_vless = len(clean_ips) <= 1 and cfg_count <= 1
    cat = CATEGORIES.get(str(link.get("category_id") or "0")) or {}
    protocol = normalize_protocol(link.get("protocol"))
    if protocol == "manual":
        display_network = normalize_network(link.get("network"))
        display_security = normalize_security(link.get("security"))
    else:
        display_network, display_security = PROTOCOL_NETWORK_SECURITY.get(
            protocol, ("tcp", "none")
        )
    manual_network = normalize_network(link.get("network"))
    manual_security = normalize_security(link.get("security"))
    manual_mode = normalize_xhttp_mode(link.get("xhttp_mode"))
    manual_live = (
        protocol == "manual"
        and normalize_base_protocol(link.get("base_protocol")) == "vless"
        and (manual_network, manual_security) in MANUAL_LIVE_COMBOS
        and not (manual_network == "xhttp" and manual_mode == "stream-one")
    )
    if protocol == "manual":
        live_status = "live" if manual_live else "link-only"
    elif protocol in LIVE_PROTOCOLS:
        live_status = "live"
    else:
        live_status = "link-only"
    return {
        "uuid": uid,
        "name": link.get("label", ""),
        "label": link.get("label", ""),
        "protocol": link.get("protocol", DEFAULT_PROTOCOL),
        "protocol_display": protocol_display_label(link),
        "base_protocol": normalize_base_protocol(link.get("base_protocol")),
        "network": display_network,
        "security": display_security,
        "manual_live": manual_live,
        "live_status": live_status,
        "live_reason": ("این پروتکل توسط هسته فعلی سرو می‌شود." if live_status == "live" else "فقط لینک ساخته می‌شود؛ برای اجرای واقعی این ترکیب به Xray-core/Inbound خارجی نیاز است."),
        "address": link.get("address", ""),
        "path": link.get("path", ""),
        "host_header": link.get("host_header", ""),
        "sni": link.get("sni", ""),
        "flow": link.get("flow", ""),
        "grpc_service_name": link.get("grpc_service_name", ""),
        "grpc_mode": link.get("grpc_mode", "gun"),
        "xhttp_mode": normalize_xhttp_mode(link.get("xhttp_mode")),
        "header_type": link.get("header_type", ""),
        "allow_insecure": bool(link.get("allow_insecure", False)),
        "reality_public_key": link.get("reality_public_key", ""),
        "reality_short_id": link.get("reality_short_id", ""),
        "reality_spider_x": link.get("reality_spider_x", "/"),
        "active": is_active,
        "used_bytes": used_b,
        "limit_bytes": limit_b,
        "expires_at": link.get("expires_at"),
        "ip_limit": int(link.get("ip_limit", 0) or 0),
        "speed_limit_bytes": int(link.get("speed_limit_bytes", 0) or 0),
        "connection_limit": int(link.get("connection_limit", 0) or 0),
        "fragment": link.get("fragment", "off"),
        "fingerprint": link.get("fingerprint", DEFAULT_FINGERPRINT),
        "alpn": link.get("alpn", ""),
        "port": link.get("port", DEFAULT_PORT),
        "note": link.get("note", ""),
        "clean_ips": clean_ips,
        "alarm_enabled": bool(link.get("alarm_enabled", False)),
        "category_id": str(link.get("category_id") or "0"),
        "category_number": int(cat.get("number", 0)),
        "category_name": str(cat.get("name", "عمومی")),
        "config_count": cfg_count,
        "client_limit": int(link.get("client_limit") or 0),
        "parent_inbound_id": link.get("parent_inbound_id"),
        "is_client": bool(link.get("parent_inbound_id")),
        "status_color": status_color,
        "connected_ips": connected_count,
        "show_vless": show_vless,
        "vless": vless_link_for_link(link, uid, host) if show_vless else "",
        "vless_full": vless_link_for_link(link, uid, host),
        "sub": f"{get_scheme()}://{host}/sub/{uid}",
        "info": f"{get_scheme()}://{host}/info/{uid}",
        "support": SUPPORT_USERNAME,
    }


# ============================================================
# PERSISTENCE
# ============================================================

async def load_state():

    global AUTH

    try:

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not DATA_FILE.exists():
            return

        async with aiofiles.open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            raw = await file.read()

        data = json.loads(raw)

        LINKS.update(
            data.get(
                "links",
                {},
            )
        )

        SUBS.update(
            data.get(
                "subs",
                {},
            )
        )

        CATEGORIES.update(
            data.get(
                "categories",
                {},
            )
        )

        stored_username = data.get("username")
        if isinstance(stored_username, str) and stored_username.strip():
            AUTH["username"] = stored_username.strip()

        stored_password = data.get(
            "password_hash"
        )

        if stored_password:
            AUTH[
                "password_hash"
            ] = stored_password

        ADMINS.update(
            data.get("admins", {})
        )

        ADMIN_REQUESTS.update(
            data.get("admin_requests", {})
        )

        DAILY_STATS.update(
            data.get("daily_stats", {})
        )

        # بازیابی تنظیمات پنل (آدرس عمومی + مشخصات ربات فروش)
        BOT_TEXTS.update(data.get("bot_texts") or {})
        settings_data = data.get("settings") or {}
        if settings_data.get("public_base_url"):
            CONFIG["public_base_url"] = str(settings_data.get("public_base_url") or "").strip()
        if settings_data.get("tcp_public_host"):
            CONFIG["tcp_public_host"] = str(settings_data.get("tcp_public_host") or "").strip()
        if settings_data.get("tcp_public_port"):
            CONFIG["tcp_public_port"] = str(settings_data.get("tcp_public_port") or "").strip()
        CONFIG["bot_auto_start"] = bool(settings_data.get("bot_auto_start", False))
        try:
            import telegram_bot
            telegram_bot.configure(
                token=settings_data.get("bot_token"),
                admin_ids_raw=settings_data.get("bot_admin_ids"),
            )
        except Exception as exc:
            logger.warning("Could not restore bot settings: %s", exc)

        # Compatibility for older records
        for uid, link in LINKS.items():

            link.setdefault(
                "protocol",
                DEFAULT_PROTOCOL,
            )

            link.setdefault(
                "fingerprint",
                DEFAULT_FINGERPRINT,
            )

            link.setdefault(
                "alpn",
                "",
            )

            link.setdefault(
                "port",
                DEFAULT_PORT,
            )

            link.setdefault(
                "ip_limit",
                0,
            )

            link.setdefault(
                "speed_limit_bytes",
                0,
            )

            link.setdefault(
                "connection_limit",
                0,
            )

            link.setdefault(
                "fragment",
                "off",
            )

            link.setdefault(
                "used_bytes",
                0,
            )
            link.setdefault("clean_ips", [])
            link.setdefault("alarm_enabled", False)
            link.setdefault("category_id", "0")
            link.setdefault("config_count", 1)
            link.setdefault("client_limit", 0)
            link.setdefault("usage_history", [])
            link.setdefault("parent_inbound_id", None)

        logger.info(
            "State loaded: %d links / %d subscriptions",
            len(LINKS),
            len(SUBS),
        )

    except Exception as exc:

        logger.exception(
            "Could not load state: %s",
            exc,
        )


async def save_state():

    async with SAVE_LOCK:

        try:

            DATA_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            payload = {
                "links":
                    dict(LINKS),

                "subs":
                    dict(SUBS),

                "categories":
                    dict(CATEGORIES),

                "username": AUTH.get("username", DEFAULT_ADMIN_USERNAME),

                "password_hash":
                    AUTH[
                        "password_hash"
                    ],

                "admins":
                    dict(ADMINS),

                "admin_requests":
                    dict(ADMIN_REQUESTS),

                "daily_stats":
                    dict(DAILY_STATS),

                # تنظیمات پنل: آدرس عمومی + مشخصات ربات فروش (برای اینکه با ری‌استارت
                # سرویس از دست نرن و نیازی به .env دستی نباشه).
                "bot_texts": BOT_TEXTS,
                "settings": {
                    "public_base_url": CONFIG.get("public_base_url", ""),
                    "tcp_public_host": CONFIG.get("tcp_public_host", ""),
                    "tcp_public_port": CONFIG.get("tcp_public_port", ""),
                    "bot_token": _bot_settings_snapshot().get("bot_token", ""),
                    "bot_admin_ids": _bot_settings_snapshot().get("admin_ids", ""),
                    "bot_auto_start": bool(CONFIG.get("bot_auto_start", False)),
                },

                "saved_at":
                    datetime.now().isoformat(),
            }

            temp_file = (
                DATA_FILE.with_suffix(
                    ".tmp"
                )
            )

            async with aiofiles.open(
                temp_file,
                "w",
                encoding="utf-8",
            ) as file:

                await file.write(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

            temp_file.replace(
                DATA_FILE
            )

        except Exception as exc:

            logger.exception(
                "Could not save state: %s",
                exc,
            )


# ============================================================
# DEFAULT LINK
# ============================================================

_default_link_created = False



async def ensure_default_categories():
    if CATEGORIES:
        return
    CATEGORIES["0"] = {
        "id": "0", "name": "عمومی", "number": 0,
        "limit_bytes": 0, "expires_days": 0, "connection_limit": 0,
        "speed_limit_bytes": 0, "ip_limit": 0, "clean_ips": [],
        "random_name": False, "single_user": False,
        "created_at": datetime.now().isoformat(),
    }
    CATEGORIES["1"] = {
        "id": "1", "name": "VIP", "number": 1,
        "limit_bytes": 0, "expires_days": 0, "connection_limit": 1,
        "speed_limit_bytes": 0, "ip_limit": 1, "clean_ips": [],
        "random_name": False, "single_user": True,
        "created_at": datetime.now().isoformat(),
    }
    asyncio.create_task(save_state())

async def ensure_default_link():

    global _default_link_created

    if _default_link_created:
        return

    async with LINKS_LOCK:

        if not any(
            item.get("is_default")
            for item in LINKS.values()
        ):

            digest = hashlib.sha256(
                (
                    "default"
                    + SECRET_KEY
                ).encode("utf-8")
            ).hexdigest()

            uid = (
                f"{digest[:8]}-"
                f"{digest[8:12]}-"
                f"{digest[12:16]}-"
                f"{digest[16:20]}-"
                f"{digest[20:32]}"
            )

            LINKS[uid] = {
                "label":
                    "لینک پیش‌فرض",

                "limit_bytes":
                    0,

                "used_bytes":
                    0,

                "created_at":
                    datetime.now().isoformat(),

                "active":
                    True,

                "expires_at":
                    None,

                "note":
                    "",

                "is_default":
                    True,

                "sub_id":
                    None,

                "protocol":
                    DEFAULT_PROTOCOL,

                "fingerprint":
                    DEFAULT_FINGERPRINT,

                "alpn":
                    "http/1.1",

                "port":
                    DEFAULT_PORT,

                "ip_limit":
                    0,

                "speed_limit_bytes":
                    DEFAULT_SPEED_LIMIT,

                "connection_limit":
                    0,

                "fragment":
                    "off",
            }

            asyncio.create_task(
                save_state()
            )

    _default_link_created = True


# ============================================================
# LINK MANAGEMENT
# ============================================================

async def make_link(
    label: str = "لینک جدید",
    limit_bytes: int = 0,
    expires_at: str | None = None,
    note: str = "",
    sub_id: str | None = None,
    protocol: str = DEFAULT_PROTOCOL,
    fingerprint: str = DEFAULT_FINGERPRINT,
    alpn: str = "",
    port: int = DEFAULT_PORT,
    ip_limit: int = 0,
    speed_limit_bytes: int = 0,
    connection_limit: int = 0,
    fragment: str = "off",
    clean_ips=None,
    alarm_enabled: bool = False,
    category_id: str = "0",
    config_count: int = 1,
    manual_fields: dict | None = None,
):

    protocol = normalize_protocol(protocol)
    manual_fields = manual_fields or {}

    fingerprint = (
        fingerprint
        or DEFAULT_FINGERPRINT
    ).strip().lower()

    if fingerprint not in FINGERPRINTS:
        fingerprint = DEFAULT_FINGERPRINT

    if not (
        MIN_PORT
        <= port
        <= MAX_PORT
    ):
        port = DEFAULT_PORT

    uid = generate_uuid()

    record = {
        "label":
            sanitize_config_name((label or "").strip() or random_config_name()),

        "limit_bytes":
            max(
                0,
                int(limit_bytes),
            ),

        "used_bytes":
            0,

        "created_at":
            datetime.now().isoformat(),

        "active":
            True,

        "expires_at":
            expires_at,

        "note":
            (
                note
                or ""
            ).strip()[:500],

        "is_default":
            False,

        "sub_id":
            sub_id,

        # A child client is a real live credential: it owns its own UUID and is
        # therefore accepted by the VLESS/XHTTP relay exactly like the parent.
        "parent_inbound_id": None,

        "protocol":
            protocol,

        "fingerprint":
            fingerprint,

        "alpn":
            (
                alpn
                or ""
            ).strip()[:100],

        "port":
            port,

        "ip_limit":
            max(
                0,
                int(ip_limit),
            ),

        "speed_limit_bytes":
            max(
                0,
                int(speed_limit_bytes),
            ),

        "connection_limit":
            max(
                0,
                int(connection_limit),
            ),

        "fragment":
            (
                fragment
                or "off"
            ).strip().lower(),

        "security_profile": "balanced",
        "multi_login": False,
        "clean_ips": list(clean_ips or []),
        "alarm_enabled": bool(alarm_enabled),
        "category_id": str(category_id or "0"),
        "config_count": max(1, min(40, int(config_count or 1))),
        "client_limit": 0,
        "usage_history": [],
    }

    if protocol == "manual":
        record.update({
            "base_protocol": normalize_base_protocol(manual_fields.get("base_protocol")),
            "network": normalize_network(manual_fields.get("network")),
            "security": normalize_security(manual_fields.get("security")),
            "address": str(manual_fields.get("address") or "").strip()[:255],
            "path": str(manual_fields.get("path") or "").strip()[:255],
            "host_header": str(manual_fields.get("host_header") or "").strip()[:255],
            "sni": str(manual_fields.get("sni") or "").strip()[:255],
            "flow": str(manual_fields.get("flow") or "").strip()[:64],
            "grpc_service_name": str(manual_fields.get("grpc_service_name") or "").strip()[:128],
            "grpc_mode": str(manual_fields.get("grpc_mode") or "gun").strip()[:32] or "gun",
            "xhttp_mode": normalize_xhttp_mode(manual_fields.get("xhttp_mode")),
            "header_type": str(manual_fields.get("header_type") or "").strip()[:32],
            "allow_insecure": bool(manual_fields.get("allow_insecure", False)),
            "reality_public_key": str(manual_fields.get("reality_public_key") or "").strip()[:128],
            "reality_short_id": str(manual_fields.get("reality_short_id") or "").strip()[:32],
            "reality_spider_x": str(manual_fields.get("reality_spider_x") or "/").strip()[:128] or "/",
            "ss_method": str(manual_fields.get("ss_method") or "chacha20-ietf-poly1305").strip()[:80],
            "ss_password": str(manual_fields.get("ss_password") or uid).strip()[:255],
        })

    record["protocol_label"] = protocol_display_label(record)

    async with LINKS_LOCK:
        LINKS[uid] = record

    bump_daily_stat("new_links")

    if sub_id:

        async with SUBS_LOCK:

            if sub_id in SUBS:

                ids = SUBS[
                    sub_id
                ].setdefault(
                    "link_ids",
                    [],
                )

                if uid not in ids:
                    ids.append(uid)

    await save_state()

    log_activity(
        "link",
        (
            f"کانفیگ "
            f"«{record['label']}» "
            f"ساخته شد"
        ),
        "ok",
    )

    return uid, record


async def remove_link(
    uid: str,
):

    async with LINKS_LOCK:

        if uid not in LINKS:
            return None

        label = LINKS[
            uid
        ].get(
            "label",
            uid,
        )

        sub_id = LINKS[
            uid
        ].get(
            "sub_id"
        )

        del LINKS[uid]

    if sub_id:

        async with SUBS_LOCK:

            if sub_id in SUBS:

                ids = SUBS[
                    sub_id
                ].get(
                    "link_ids",
                    [],
                )

                if uid in ids:
                    ids.remove(uid)

    await save_state()

    log_activity(
        "link",
        (
            f"کانفیگ "
            f"«{label}» "
            f"حذف شد"
        ),
        "warn",
    )

    return label


async def set_link_active(
    uid: str,
    active: bool,
):

    async with LINKS_LOCK:

        if uid not in LINKS:
            return None

        LINKS[
            uid
        ][
            "active"
        ] = bool(active)

        record = LINKS[uid]

    await save_state()

    log_activity(
        "link",
        (
            f"کانفیگ "
            f"«{record['label']}» "
            f"{'فعال' if active else 'غیرفعال'} شد"
        ),
        "ok"
        if active
        else "warn",
    )

    return record


# ============================================================
# SUB GROUPS
# ============================================================

async def create_sub_group(
    name: str = "گروه جدید",
    desc: str = "",
    password: str = "",
):

    name = (
        name
        or "گروه جدید"
    ).strip()[:60]

    desc = (
        desc
        or ""
    ).strip()[:200]

    password = (
        password
        or ""
    ).strip()

    sub_id = generate_uuid()

    uuid_key = secrets.token_urlsafe(16)

    record = {
        "name":
            name,

        "desc":
            desc,

        "password_hash":
            (
                hash_password(password)
                if password
                else None
            ),

        "uuid_key":
            uuid_key,

        "created_at":
            datetime.now().isoformat(),

        "link_ids":
            [],
    }

    async with SUBS_LOCK:
        SUBS[sub_id] = record

    await save_state()

    log_activity(
        "sub",
        (
            f"گروه "
            f"«{name}» "
            f"ساخته شد"
        ),
        "ok",
    )

    return (
        sub_id,
        record,
    )


async def set_link_sub(
    uid: str,
    sub_id: str | None,
):

    async with LINKS_LOCK:

        if uid not in LINKS:
            return False

        old_sub = LINKS[
            uid
        ].get(
            "sub_id"
        )

        label = LINKS[
            uid
        ].get(
            "label",
            uid,
        )

    if sub_id is not None:

        async with SUBS_LOCK:

            if sub_id not in SUBS:
                return False

    async with SUBS_LOCK:

        if (
            old_sub
            and old_sub in SUBS
        ):

            ids = SUBS[
                old_sub
            ].get(
                "link_ids",
                [],
            )

            if uid in ids:
                ids.remove(uid)

        if (
            sub_id
            and sub_id in SUBS
        ):

            ids = SUBS[
                sub_id
            ].setdefault(
                "link_ids",
                [],
            )

            if uid not in ids:
                ids.append(uid)

    async with LINKS_LOCK:

        if uid in LINKS:

            LINKS[
                uid
            ][
                "sub_id"
            ] = sub_id

    await save_state()

    log_activity(
        "link",
        (
            f"کانفیگ "
            f"«{label}» "
            f"{'به گروه اضافه شد' if sub_id else 'از گروه خارج شد'}"
        ),
        "info",
    )

    return True


async def remove_sub_group(
    sub_id: str,
):

    async with SUBS_LOCK:

        if sub_id not in SUBS:
            return None

        name = SUBS[
            sub_id
        ].get(
            "name",
            sub_id,
        )

        del SUBS[sub_id]

    async with LINKS_LOCK:

        for link in LINKS.values():

            if (
                link.get("sub_id")
                == sub_id
            ):
                link["sub_id"] = None

    await save_state()

    log_activity(
        "sub",
        (
            f"گروه "
            f"«{name}» "
            f"حذف شد"
        ),
        "warn",
    )

    return name


async def usage_history_loop():
    """Persist live usage history periodically so the customer graph survives restarts."""
    while True:
        try:
            await asyncio.sleep(60)
            now = now_ir()
            ts = now.replace(second=0, microsecond=0).isoformat()
            changed = False
            async with LINKS_LOCK:
                for link in LINKS.values():
                    history = link.setdefault("usage_history", [])
                    used = int(link.get("used_bytes", 0) or 0)
                    limit = int(link.get("limit_bytes", 0) or 0)
                    if history and str(history[-1].get("ts", ""))[:16] == ts[:16]:
                        if history[-1].get("used") != used or history[-1].get("limit") != limit:
                            history[-1]["used"] = used
                            history[-1]["limit"] = limit
                            changed = True
                    else:
                        history.append({"ts": ts, "used": used, "limit": limit})
                        if len(history) > 144:
                            del history[:-144]
                        changed = True
            if changed:
                await save_state()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Usage history loop error: %s", exc)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    global http_client, USAGE_PERSIST_TASK

    limits = httpx.Limits(
        max_connections=500,
        max_keepalive_connections=100,
    )

    timeout = httpx.Timeout(
        30.0,
        connect=10.0,
    )

    http_client = httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
    )

    await load_state()

    USAGE_PERSIST_TASK = asyncio.create_task(usage_history_loop())

    await ensure_default_categories()
    await ensure_default_link()

    log_activity(
        "system",
        (
            f"{APP_NAME} "
            f"v{APP_VERSION} "
            f"راه‌اندازی شد"
        ),
        "ok",
    )

    logger.info(
        "%s v%s started on 0.0.0.0:%s",
        APP_NAME,
        APP_VERSION,
        PORT,
    )

    logger.info(
        "Data directory: %s",
        DATA_DIR,
    )

    try:
        import tcp_relay
        await tcp_relay.start_tcp_relay(app_logger=logger)
    except Exception as exc:
        logger.warning("VLESS-TCP relay startup skipped: %s", exc)


@app.on_event("shutdown")
async def shutdown():

    global USAGE_PERSIST_TASK
    if USAGE_PERSIST_TASK:
        USAGE_PERSIST_TASK.cancel()
        try:
            await USAGE_PERSIST_TASK
        except asyncio.CancelledError:
            pass
        USAGE_PERSIST_TASK = None

    await save_state()

    if http_client:
        await http_client.aclose()

    try:
        import tcp_relay
        await tcp_relay.stop_tcp_relay()
    except Exception:
        pass


# ============================================================
# LANDING
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # The old public landing/interstitial page has been removed.
    # Visitors go straight to the real login page; authenticated users go to the dashboard.
    if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")



# ============================================================
# VODIWALKER STORE / SUBSCRIPTION PLANS
# ============================================================
# Plan data now lives in sales.py (persisted to vodiwalker_plans.json)
# and is fully editable from the "مدیریت پلن‌ها" tab in the dashboard.
# This page is rendered fresh on every request so edits show up instantly.

def _store_plan_cards(plans):
    cards = []
    for plan in plans:
        cards.append(f"""
        <article class="plan-card {'featured' if plan.get('featured') else ''}">
          <div class="plan-badge">{escape_html(plan.get('badge') or '')}</div>
          <div class="plan-name">{escape_html(plan.get('name',''))}</div>
          <div class="plan-price"><strong>{plan.get('stars',0)}</strong><span> Stars</span></div>
          <ul>
            <li>اعتبار {plan.get('days',0)} روزه</li>
            <li>{plan.get('volume_gb',0)}GB ترافیک</li>
            <li>تا {plan.get('speed_mbps',0)}Mbps</li>
            <li>{plan.get('ip_limit',0)} کاربر هم‌زمان</li>
            <li>لینک سابسکریپشن اختصاصی</li>
          </ul>
          <a class="buy-btn" href="https://t.me/{escape_html(os.environ.get('TELEGRAM_BOT_USERNAME','VodiWalkerBot'))}?start=buy_{escape_html(plan.get('id',''))}">خرید از ربات فروش</a>
        </article>
        """)
    return "\n".join(cards)

def _store_html(plans):
    return """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VodiWalker — فروش اشتراک</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;font-family:Vazirmatn,Tahoma,Arial,sans-serif;color:#eef2ff;background:#070a12;
background-image:radial-gradient(circle at 15% 15%,rgba(99,102,241,.18),transparent 30%),radial-gradient(circle at 85% 20%,rgba(14,165,233,.15),transparent 30%),linear-gradient(145deg,#070a12,#0b1020 55%,#060810)}
.wrap{width:min(1120px,92%);margin:auto;padding:54px 0 70px}.hero{text-align:center;margin-bottom:38px}.logo{display:inline-flex;width:64px;height:64px;border-radius:20px;align-items:center;justify-content:center;font-size:26px;font-weight:900;background:linear-gradient(135deg,#7c3aed,#06b6d4);box-shadow:0 20px 60px rgba(76,29,149,.35)}
h1{font-size:clamp(34px,6vw,64px);margin:18px 0 8px;letter-spacing:-2px}.sub{color:#9ca8c7;max-width:700px;margin:auto;line-height:1.9}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:34px}.plan-card{position:relative;padding:28px;border:1px solid rgba(255,255,255,.09);border-radius:28px;background:rgba(15,23,42,.86);backdrop-filter:blur(10px);box-shadow:0 25px 80px rgba(0,0,0,.25);transition:.25s;contain:layout style paint}.plan-card:hover{transform:translateY(-5px);border-color:rgba(129,140,248,.4)}.featured{border-color:rgba(99,102,241,.55);box-shadow:0 25px 90px rgba(79,70,229,.16)}.plan-badge{display:inline-block;font-size:12px;padding:7px 10px;border-radius:999px;background:rgba(99,102,241,.13);color:#b7c2ff}.plan-name{font-size:24px;font-weight:900;margin:18px 0 8px}.plan-price strong{font-size:42px}.plan-price span{color:#94a3b8}ul{padding:0;list-style:none;line-height:2.2;color:#cbd5e1;min-height:150px}.buy-btn{display:block;text-align:center;text-decoration:none;color:white;font-weight:800;padding:13px 16px;border-radius:15px;background:linear-gradient(135deg,#6366f1,#06b6d4)}.note{margin-top:26px;padding:16px;border-radius:18px;background:rgba(255,255,255,.035);color:#8fa0bf;text-align:center;font-size:13px}@media(max-width:800px){.grid{grid-template-columns:1fr}.wrap{padding-top:32px}}@media(max-width:800px),(pointer:coarse){.plan-card{backdrop-filter:none!important;-webkit-backdrop-filter:none!important;background:rgba(15,23,42,.96)}}
</style></head><body><main class="wrap"><section class="hero"><div class="logo">V</div><h1>VodiWalker Store</h1><p class="sub">خرید سریع، تحویل خودکار و سابسکریپشن اختصاصی. پرداخت از طریق ربات فروش انجام می‌شود و بعد از پرداخت، لینک شما به‌صورت خودکار ساخته خواهد شد.</p></section><section class="grid">""" + _store_plan_cards(plans) + """</section><div class="note">پرداخت و تحویل توسط ربات رسمی VodiWalker انجام می‌شود. برای فعال‌سازی ربات، TELEGRAM_BOT_TOKEN و درگاه/Stars را تنظیم کنید.</div></main></body></html>"""

@app.get("/plans", response_class=HTMLResponse)
async def public_plans():
    if not SALES_ENABLED:
        return HTMLResponse("""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VodiWalker · Future Release</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#070b13;color:#f5f7fb;font-family:Tahoma,Arial,sans-serif}.box{width:min(560px,calc(100% - 36px));padding:42px 28px;text-align:center;border:1px solid rgba(255,255,255,.1);border-radius:28px;background:linear-gradient(145deg,#0d1320,#111a2a);box-shadow:0 30px 90px rgba(0,0,0,.35)}.ico{width:72px;height:72px;margin:0 auto 18px;display:grid;place-items:center;border-radius:22px;background:rgba(124,92,255,.15);font-size:30px}.muted{color:#9aa7bc;line-height:2;font-size:13px}.tag{display:inline-block;margin-top:18px;padding:8px 13px;border-radius:999px;background:rgba(53,214,255,.08);border:1px solid rgba(53,214,255,.2);color:#64dcff;font-size:11px}</style></head><body><main class="box"><div class="ico">🔒</div><h1>فروش اشتراک موقتاً غیرفعال است</h1><p class="muted">ماژول فروش و پلن‌ها در نسخه فعلی VodiWalker فعال نیست. این قابلیت پس از تکمیل و تست نهایی در نسخه‌های بعدی منتشر خواهد شد.</p><span class="tag">VodiWalker · Future Release</span></main></body></html>""")
    import sales
    return HTMLResponse(_store_html(sales.list_plans()))

# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "connections": len(connections),
        "uptime": uptime(),
    }


# ============================================================
# LIVE TELEMETRY
# ============================================================

@app.get("/api/telemetry")
async def api_telemetry(_=Depends(require_auth)):
    """Lightweight live server metrics for the dashboard."""
    global _telemetry_prev
    now = time.time()
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(str(DATA_DIR))
    cpu = psutil.cpu_percent(interval=None)
    load = None
    try:
        load = [round(x, 2) for x in os.getloadavg()]
    except Exception:
        load = []
    net = psutil.net_io_counters()
    async with _telemetry_lock:
        prev = _telemetry_prev
        dt = max(0.25, now - float(prev.get("ts", now)))
        rx_rate = max(0, net.bytes_recv - int(prev.get("rx", net.bytes_recv))) / dt
        tx_rate = max(0, net.bytes_sent - int(prev.get("tx", net.bytes_sent))) / dt
        _telemetry_prev = {"ts": now, "rx": net.bytes_recv, "tx": net.bytes_sent}
    process = psutil.Process(os.getpid())
    sample = {
        "ts": datetime.now().isoformat(),
        "cpu": _pct(cpu),
        "ram": _pct(vm.percent),
        "swap": _pct(swap.percent),
        "storage": _pct(disk.percent),
        "rx_bps": int(rx_rate),
        "tx_bps": int(tx_rate),
        "connections": len(connections),
    }
    TELEMETRY_HISTORY.append(sample)
    return {
        "ok": True,
        "cpu": _pct(cpu),
        "cpu_cores": psutil.cpu_count(logical=True) or 1,
        "ram": {"percent": _pct(vm.percent), "used": vm.used, "total": vm.total},
        "swap": {"percent": _pct(swap.percent), "used": swap.used, "total": swap.total},
        "storage": {"percent": _pct(disk.percent), "used": disk.used, "total": disk.total},
        "network": {"rx_bps": int(rx_rate), "tx_bps": int(tx_rate), "bytes_recv": int(net.bytes_recv), "bytes_sent": int(net.bytes_sent)},
        "connections": len(connections),
        "traffic_bytes": int(stats.get("total_bytes", 0)),
        "requests": int(stats.get("total_requests", 0)),
        "errors": int(stats.get("total_errors", 0)),
        "uptime": _human_uptime(now - stats.get("start_time", now)),
        "load": load,
        "process": {"rss": process.memory_info().rss, "cpu": _pct(process.cpu_percent(interval=None))},
        "bot_running": bool(_bot_settings_snapshot().get("running")),
        "history": list(TELEMETRY_HISTORY),
    }


# ============================================================
# LOGIN
# ============================================================

from pages import LOGIN_HTML


def login_error_html(
    message: str,
):
    safe_message = escape_html(
        message
    )

    return LOGIN_HTML.replace(
        "</form>",
        (
            f"""
            <div class="error">
                {safe_message}
            </div>
            </form>
            """
        ),
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(
    request: Request,
):

    if await is_valid_session(
        request.cookies.get(
            SESSION_COOKIE
        )
    ):
        return RedirectResponse(
            "/dashboard"
        )

    return HTMLResponse(
        LOGIN_HTML
    )


@app.post("/login")
async def login_form(
    request: Request,
):

    try:

        content_type = (
            request.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if "application/json" in content_type:

            body = await request.json()

            password = str(
                body.get(
                    "password",
                    "",
                )
            ).strip()

            login_username = str(
                body.get(
                    "username",
                    "",
                )
            ).strip()

        else:

            raw = await request.body()

            parsed = parse_qs(
                raw.decode(
                    "utf-8",
                    errors="ignore",
                )
            )

            password = (
                parsed.get(
                    "password",
                    [""],
                )[0]
                .strip()
            )

            login_username = (
                parsed.get(
                    "username",
                    [""],
                )[0]
                .strip()
            )

    except Exception as exc:

        logger.exception(
            "Login parser error: %s",
            exc,
        )

        return HTMLResponse(
            login_error_html(
                "خطا در پردازش اطلاعات ورود."
            ),
            status_code=400,
        )

    ip = client_ip(request)

    blocked, retry_after = login_is_blocked(ip)
    if blocked:
        minutes = max(1, (retry_after + 59) // 60)
        return HTMLResponse(
            login_error_html(
                f"به دلیل تلاش‌های ناموفق متعدد، ورود موقتاً مسدود شده است. حدود {minutes} دقیقه دیگر دوباره تلاش کنید."
            ),
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )

    if not password:
        register_login_failure(ip)
        return HTMLResponse(
            login_error_html(
                "رمز عبور را وارد کنید."
            ),
            status_code=400,
        )

    ok, admin_id, role, display_name = verify_admin_credentials(login_username, password)

    if not ok:

        locked, value = register_login_failure(ip)
        if locked:
            return HTMLResponse(
                login_error_html(
                    "تعداد تلاش‌های ناموفق بیش از حد مجاز بود. این IP برای ۱۵ دقیقه مسدود شد."
                ),
                status_code=429,
                headers={"Retry-After": str(LOGIN_LOCKOUT_SECONDS)},
            )

        remaining = value
        log_activity(
            "auth",
            (
                f"تلاش ورود ناموفق از {ip}؛ "
                f"{remaining} تلاش باقی مانده"
            ),
            "err",
        )

        return HTMLResponse(
            login_error_html(
                f"رمز عبور اشتباه است. {remaining} تلاش دیگر باقی مانده است."
            ),
            status_code=401,
        )

    clear_login_failures(ip)

    if admin_id != "owner" and admin_id in ADMINS:
        ADMINS[admin_id]["last_login_at"] = datetime.now().isoformat()
        ADMINS[admin_id]["last_login_ip"] = ip
        asyncio.create_task(save_state())

    token = await create_session(admin_id, role)

    response = RedirectResponse(
        "/dashboard?login=1",
        status_code=303,
    )

    set_auth_cookie(
        response,
        request,
        token,
    )

    log_activity(
        "auth",
        (
            f"ورود موفق «{display_name or admin_id}» به پنل "
            f"از {client_ip(request)}"
        ),
        "ok",
    )

    return response


@app.post("/api/login")
async def api_login(
    request: Request,
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="JSON نامعتبر است",
        )

    password = str(
        body.get(
            "password",
            "",
        )
    ).strip()

    login_username = str(
        body.get(
            "username",
            "",
        )
    ).strip()

    ip = client_ip(request)

    blocked, retry_after = login_is_blocked(ip)
    if blocked:
        raise HTTPException(
            status_code=429,
            detail=f"ورود موقتاً مسدود است. حدود {max(1, (retry_after + 59) // 60)} دقیقه دیگر تلاش کنید.",
            headers={"Retry-After": str(retry_after)},
        )

    if not password:
        register_login_failure(ip)
        raise HTTPException(
            status_code=400,
            detail="رمز عبور را وارد کنید",
        )

    ok, admin_id, role, display_name = verify_admin_credentials(login_username, password)

    if not ok:

        locked, value = register_login_failure(ip)
        if locked:
            raise HTTPException(
                status_code=429,
                detail="تعداد تلاش‌های ناموفق بیش از حد مجاز بود. این IP برای ۱۵ دقیقه مسدود شد.",
                headers={"Retry-After": str(LOGIN_LOCKOUT_SECONDS)},
            )

        log_activity(
            "auth",
            (
                f"تلاش ورود ناموفق از {ip}؛ "
                f"{value} تلاش باقی مانده"
            ),
            "err",
        )

        raise HTTPException(
            status_code=401,
            detail=f"رمز عبور اشتباه است؛ {value} تلاش دیگر باقی مانده است",
        )

    clear_login_failures(ip)

    if admin_id != "owner" and admin_id in ADMINS:
        ADMINS[admin_id]["last_login_at"] = datetime.now().isoformat()
        ADMINS[admin_id]["last_login_ip"] = ip
        asyncio.create_task(save_state())

    log_activity(
        "auth",
        f"ورود موفق «{display_name or admin_id}» به پنل از {ip}",
        "ok",
    )

    token = await create_session(admin_id, role)

    response = JSONResponse(
        {
            "ok": True,
            "authenticated": True,
            "admin": {"id": admin_id, "username": display_name or admin_id, "role": role},
        }
    )

    set_auth_cookie(
        response,
        request,
        token,
    )

    return response


# ============================================================
# LOGOUT
# ============================================================

@app.get("/logout")
async def logout_page(
    request: Request,
):

    await destroy_session(
        request.cookies.get(
            SESSION_COOKIE
        )
    )

    response = RedirectResponse(
        "/login"
    )

    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
    )

    return response


@app.post("/api/logout")
async def api_logout(
    request: Request,
):

    await destroy_session(
        request.cookies.get(
            SESSION_COOKIE
        )
    )

    response = JSONResponse(
        {
            "ok": True
        }
    )

    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
    )

    return response


@app.get("/api/me")
async def api_me(
    request: Request,
):

    info = await get_session_info(
        request.cookies.get(SESSION_COOKIE)
    )

    if not info:
        return {"authenticated": False}

    admin_id = info.get("admin_id", "owner")
    role = info.get("role", "owner")

    if admin_id == "owner":
        username = AUTH.get("username", DEFAULT_ADMIN_USERNAME)
    else:
        admin = ADMINS.get(admin_id, {})
        username = admin.get("username", admin_id)

    return {
        "authenticated": True,
        "admin": {"id": admin_id, "username": username, "role": role},
    }


# ============================================================
# CHANGE PASSWORD
# ============================================================

@app.get("/api/system/diagnostics")
async def api_system_diagnostics(request: Request, token=Depends(require_auth)):
    """Authenticated live diagnostics used by the Pro dashboard."""
    try:
        import psutil
        proc = psutil.Process(os.getpid())
        vm = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        mem = proc.memory_info().rss
        net = psutil.net_io_counters()
        disk = psutil.disk_usage("/")
        bot = _bot_settings_snapshot()
        async with LINKS_LOCK:
            links_snapshot = dict(LINKS)
        async with SUBS_LOCK:
            subs_snapshot = dict(SUBS)
        active = sum(1 for x in links_snapshot.values() if is_link_allowed(x))
        clients = sum(1 for x in links_snapshot.values() if x.get("parent_inbound_id"))
        inbounds = len(links_snapshot) - clients
        return {
            "ok": True,
            "time": datetime.now().isoformat(),
            "uptime": _human_uptime(time.time() - stats.get("start_time", time.time())),
            "service": {"status": "healthy", "version": "VodiWalker Pro"},
            "resources": {
                "cpu_percent": round(float(cpu), 1),
                "memory_rss": int(mem),
                "memory_percent": round(float(proc.memory_percent()), 1),
                "system_memory_percent": round(float(vm.percent), 1),
                "disk_percent": round(float(disk.percent), 1),
                "rx_bytes": int(net.bytes_recv),
                "tx_bytes": int(net.bytes_sent),
            },
            "objects": {
                "inbounds": max(0, inbounds),
                "clients": clients,
                "active_links": active,
                "subscriptions": len(subs_snapshot),
                "admins": len(ADMINS) + 1,
                "errors": len(error_logs),
            },
            "bot": {"running": bool(bot.get("running")), "admin_count": len(bot.get("admin_ids", "").split(",")) if bot.get("admin_ids") else 0},
            "security": {"session_count": len(SESSIONS), "username": AUTH.get("username", DEFAULT_ADMIN_USERNAME)},
        }
    except Exception as exc:
        logger.exception("Diagnostics error: %s", exc)
        raise HTTPException(status_code=500, detail="Diagnostics unavailable")


@app.post("/api/security/revoke-other-sessions")
async def api_revoke_other_sessions(request: Request, token=Depends(require_auth)):
    info = await get_session_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="نشست نامعتبر است")
    admin_id = info.get("admin_id", "owner")
    removed = 0
    async with SESSIONS_LOCK:
        stale = [tok for tok, sess in SESSIONS.items() if tok != token and isinstance(sess, dict) and sess.get("admin_id", "owner") == admin_id]
        for tok in stale:
            SESSIONS.pop(tok, None)
            removed += 1
    log_activity("auth", f"نشست‌های قبلی حساب «{AUTH.get('username') if admin_id == 'owner' else ADMINS.get(admin_id, {}).get('username', admin_id)}» لغو شد", "warn")
    return {"ok": True, "revoked": removed}


@app.post("/api/change-password")
async def api_change_password(
    request: Request,
    token=Depends(require_auth),
):
    # نکته مهم (رفع باگ): این endpoint قبلاً همیشه رمز عبور مالک (owner) را
    # چک/جایگزین می‌کرد، حتی وقتی یک ادمین فرعی (sub-admin) وارد شده بود.
    # نتیجه: تغییر رمز برای ادمین‌های فرعی یا با خطای «رمز فعلی اشتباه است»
    # مواجه می‌شد (چون با هش رمز owner مقایسه می‌شد)، یا در بدترین حالت رمز
    # owner را به‌جای رمز خودِ ادمین overwrite می‌کرد. همچنین همه‌ی session های
    # تمام ادمین‌ها پاک می‌شد. اینجا اول مشخص می‌کنیم کدام حساب (owner یا کدام
    # sub-admin) درخواست را زده، سپس دقیقاً همان حساب را چک/آپدیت می‌کنیم و
    # فقط نشست‌های همان حساب باطل می‌شوند، نه بقیه‌ی ادمین‌ها.

    info = await get_session_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="نشست نامعتبر است، دوباره وارد شوید")

    admin_id = info.get("admin_id", "owner")
    is_owner = admin_id == "owner"
    admin_record = None if is_owner else ADMINS.get(admin_id)

    if not is_owner and not admin_record:
        raise HTTPException(status_code=401, detail="حساب کاربری یافت نشد")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="اطلاعات نامعتبر است",
        )

    current_password = str(body.get("current_password", ""))
    current_hash = AUTH["password_hash"] if is_owner else admin_record.get("password_hash", "")

    if hash_password(current_password) != current_hash:
        raise HTTPException(
            status_code=400,
            detail="رمز فعلی اشتباه است",
        )

    new_password = str(body.get("new_password", ""))
    repeat_password = str(body.get("repeat_password", ""))

    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="رمز جدید باید حداقل ۸ کاراکتر باشد",
        )

    if new_password == current_password:
        raise HTTPException(
            status_code=400,
            detail="رمز جدید باید با رمز فعلی متفاوت باشد",
        )

    if new_password != repeat_password:
        raise HTTPException(
            status_code=400,
            detail="تکرار رمز عبور یکسان نیست",
        )

    new_hash = hash_password(new_password)

    if is_owner:
        AUTH["password_hash"] = new_hash
    else:
        admin_record["password_hash"] = new_hash

    async with SESSIONS_LOCK:
        # فقط نشست‌های همین حساب باطل می‌شوند (نه همه‌ی ادمین‌ها)، اما نشست
        # فعلی زنده می‌ماند تا کاربر بلافاصله logout نشود.
        stale = [
            tok for tok, sess in SESSIONS.items()
            if sess.get("admin_id", "owner") == admin_id and tok != token
        ]
        for tok in stale:
            SESSIONS.pop(tok, None)

        SESSIONS[token] = {
            "exp": time.time() + SESSION_TTL,
            "admin_id": admin_id,
            "role": info.get("role", "owner" if is_owner else "admin"),
            "permissions": sorted(permissions_for_admin(admin_id)),
        }

    await save_state()

    log_activity(
        "auth",
        "رمز عبور پنل تغییر کرد" if is_owner else f"رمز عبور ادمین «{admin_record.get('username', admin_id)}» تغییر کرد",
        "ok",
    )

    return {
        "ok": True
    }


# ============================================================
# CHANGE USERNAME
# ============================================================

@app.post("/api/change-username")
async def api_change_username(
    request: Request,
    token=Depends(require_auth),
):
    info = await get_session_info(token)
    if not info:
        raise HTTPException(status_code=401, detail="نشست نامعتبر است، دوباره وارد شوید")

    admin_id = info.get("admin_id", "owner")
    is_owner = admin_id == "owner"
    admin_record = None if is_owner else ADMINS.get(admin_id)
    if not is_owner and not admin_record:
        raise HTTPException(status_code=401, detail="حساب کاربری یافت نشد")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    username = str(body.get("username", "")).strip()
    if not username:
        raise HTTPException(status_code=400, detail="نام کاربری نمی‌تواند خالی باشد")
    if len(username) < 3 or len(username) > 40:
        raise HTTPException(status_code=400, detail="نام کاربری باید بین ۳ تا ۴۰ کاراکتر باشد")
    if any(ch.isspace() for ch in username):
        raise HTTPException(status_code=400, detail="نام کاربری نباید فاصله داشته باشد")
    if username.lower() == "owner":
        raise HTTPException(status_code=400, detail="این نام کاربری رزرو شده است")

    current = AUTH.get("username", DEFAULT_ADMIN_USERNAME) if is_owner else admin_record.get("username", admin_id)
    for aid, admin in ADMINS.items():
        if aid != admin_id and str(admin.get("username", "")).lower() == username.lower():
            raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")
    if is_owner and username.lower() in {str(a.get("username", "")).lower() for a in ADMINS.values()}:
        raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")

    if is_owner:
        AUTH["username"] = username
    else:
        admin_record["username"] = username

    async with SESSIONS_LOCK:
        sess = SESSIONS.get(token)
        if sess:
            sess["exp"] = time.time() + SESSION_TTL

    await save_state()
    log_activity("auth", f"نام کاربری «{current}» به «{username}» تغییر کرد", "ok")
    return {"ok": True, "username": username}


# ============================================================
# CREATE LINK
# ============================================================


@app.get("/api/network/railway")
async def railway_network_info(_=Depends(require_auth)):
    """Return Railway networking hints without exposing secrets."""
    return {
        "is_railway": bool(os.environ.get("RAILWAY_PROJECT_ID") or os.environ.get("RAILWAY_ENVIRONMENT_ID")),
        "public_domain": os.environ.get("RAILWAY_PUBLIC_DOMAIN", ""),
        "tcp_proxy_domain": os.environ.get("RAILWAY_TCP_PROXY_DOMAIN", ""),
        "tcp_proxy_port": safe_int(os.environ.get("RAILWAY_TCP_PROXY_PORT", "0"), minimum=0, maximum=65535),
        "tcp_application_port": safe_int(os.environ.get("RAILWAY_TCP_APPLICATION_PORT", "0"), minimum=0, maximum=65535),
        "app_port": safe_int(os.environ.get("PORT", "0"), minimum=0, maximum=65535),
    }


@app.post("/api/network/tcp-ping")
async def tcp_ping(request: Request, _=Depends(require_auth)):
    """Server-side TCP connectivity test for an address/port entered in the builder."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات تست اتصال معتبر نیست.")
    host = str(body.get("host") or body.get("address") or "").strip()
    port = safe_int(body.get("port", 0), minimum=1, maximum=65535)
    timeout = min(max(float(body.get("timeout", 4.0) or 4.0), 0.5), 8.0)
    if not host:
        raise HTTPException(status_code=400, detail="آدرس سرور را وارد کنید.")
    if not port:
        raise HTTPException(status_code=400, detail="پورت باید بین 1 تا 65535 باشد.")
    started = time.perf_counter()
    try:
        infos = await asyncio.get_running_loop().run_in_executor(None, lambda: __import__('socket').getaddrinfo(host, port, type=__import__('socket').SOCK_STREAM))
        resolved = []
        for info in infos:
            addr = info[4][0]
            if addr not in resolved:
                resolved.append(addr)
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return {"ok": True, "host": host, "port": port, "latency_ms": round((time.perf_counter()-started)*1000, 1), "resolved": resolved[:6], "message": "اتصال TCP برقرار شد."}
    except asyncio.TimeoutError:
        return {"ok": False, "host": host, "port": port, "latency_ms": round((time.perf_counter()-started)*1000, 1), "message": "Timeout: سرور در زمان تعیین‌شده پاسخ نداد."}
    except Exception as exc:
        return {"ok": False, "host": host, "port": port, "latency_ms": round((time.perf_counter()-started)*1000, 1), "message": f"اتصال ناموفق: {type(exc).__name__}: {str(exc)[:180]}"}


@app.post("/api/links")
async def create_link_api(
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()

        if not isinstance(body, dict):
            raise ValueError(
                "body is not object"
            )

    except Exception as exc:

        logger.exception(
            "Create link JSON error: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail="اطلاعات ارسال‌شده معتبر نیست.",
        )

    limit_value = safe_float(
        body.get(
            "limit_value",
            0,
        )
    )

    limit_unit = str(
        body.get(
            "limit_unit",
            "GB",
        )
        or "GB"
    ).upper()

    limit_bytes = (
        0
        if limit_value <= 0
        else parse_size_to_bytes(
            limit_value,
            limit_unit,
        )
    )

    expires_days = safe_int(
        body.get(
            "expires_days",
            0,
        ),
        minimum=0,
    )

    expires_at = (
        (
            datetime.now()
            + timedelta(
                days=expires_days
            )
        ).isoformat()
        if expires_days > 0
        else None
    )

    port = safe_int(
        body.get(
            "port",
            DEFAULT_PORT,
        ),
        default=DEFAULT_PORT,
        minimum=MIN_PORT,
        maximum=MAX_PORT,
    )

    ip_limit = safe_int(
        body.get(
            "ip_limit",
            0,
        ),
        minimum=0,
    )

    speed_value = safe_float(
        body.get(
            "speed_limit_value",
            0,
        )
    )

    speed_unit = str(
        body.get(
            "speed_limit_unit",
            "MBIT",
        )
        or "MBIT"
    ).upper()

    speed_bytes = (
        0
        if speed_value <= 0
        else parse_speed_to_bytes(
            speed_value,
            speed_unit,
        )
    )

    connection_limit = safe_int(
        body.get(
            "connection_limit",
            0,
        ),
        minimum=0,
    )

    protocol = str(
        body.get(
            "protocol",
            DEFAULT_PROTOCOL,
        )
        or DEFAULT_PROTOCOL
    ).strip().lower()

    if protocol != "manual" and protocol not in PROTOCOLS:
        protocol = DEFAULT_PROTOCOL

    manual_fields = body.get("manual") or {}
    if not isinstance(manual_fields, dict):
        manual_fields = {}

    fingerprint = str(
        body.get(
            "fingerprint",
            DEFAULT_FINGERPRINT,
        )
        or DEFAULT_FINGERPRINT
    ).strip().lower()

    if fingerprint not in FINGERPRINTS:
        fingerprint = DEFAULT_FINGERPRINT

    fragment = str(
        body.get(
            "fragment",
            "off",
        )
        or "off"
    ).strip().lower()

    allowed_fragments = {
        "off",
        "safe",
        "balanced",
        "aggressive",
    }

    if fragment not in allowed_fragments:
        fragment = "off"

    raw_clean = body.get("clean_ips") or body.get("clean_ip") or ""
    if isinstance(raw_clean, list):
        clean_ips = [str(x).strip() for x in raw_clean if str(x).strip()]
    else:
        clean_ips = [x.strip() for x in str(raw_clean).replace(",", "\n").splitlines() if x.strip()]
    alarm_enabled = bool(body.get("alarm_enabled", False))
    category_id = str(body.get("category_id") or "0")
    if category_id not in CATEGORIES:
        category_id = "0"
    config_count = safe_int(body.get("config_count", 1), minimum=1, maximum=40)
    client_limit = safe_int(body.get("client_limit", 0), minimum=0, maximum=1000)
    requested_expires_at = str(body.get("expires_at") or "").strip()
    if requested_expires_at:
        try:
            dt = datetime.fromisoformat(requested_expires_at.replace("Z", "+00:00"))
            expires_at = dt.replace(tzinfo=None).isoformat()
        except Exception:
            raise HTTPException(status_code=400, detail="زمان انقضا معتبر نیست")
    cat = CATEGORIES.get(category_id) or {}
    if cat.get("limit_bytes") and limit_bytes <= 0:
        limit_bytes = int(cat["limit_bytes"])
    if cat.get("expires_days") and expires_days <= 0:
        expires_days = int(cat["expires_days"])
        expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days > 0 else None
    if cat.get("connection_limit") and connection_limit <= 0:
        connection_limit = int(cat["connection_limit"])
    if cat.get("speed_limit_bytes") and speed_bytes <= 0:
        speed_bytes = int(cat["speed_limit_bytes"])
    if cat.get("ip_limit") and ip_limit <= 0:
        ip_limit = int(cat["ip_limit"])
    if cat.get("clean_ips") and not clean_ips:
        clean_ips = list(cat["clean_ips"])
    if cat.get("single_user"):
        if ip_limit == 0: ip_limit = 1
        if connection_limit == 0: connection_limit = 1
    label_val = body.get("label", "")
    if cat.get("random_name") or not str(label_val).strip():
        label_val = random_config_name()
    else:
        label_val = sanitize_config_name(str(label_val))

    uid, link = await make_link(
        label=label_val,
        limit_bytes=limit_bytes,
        expires_at=expires_at,
        note=body.get(
            "note",
            "",
        ),
        sub_id=body.get(
            "sub_id"
        ),
        protocol=protocol,
        fingerprint=fingerprint,
        alpn=body.get(
            "alpn",
            DEFAULT_ALPN_BY_PROTOCOL.get(
                protocol,
                "http/1.1",
            ),
        ),
        port=port,
        ip_limit=ip_limit,
        speed_limit_bytes=speed_bytes,
        connection_limit=connection_limit,
        fragment=fragment,
        clean_ips=clean_ips,
        alarm_enabled=alarm_enabled,
        category_id=category_id,
        config_count=config_count,
        manual_fields=manual_fields,
    )

    async with LINKS_LOCK:
        LINKS[uid]["client_limit"] = client_limit
    await save_state()

    host = get_host(request)

    result = {
        **get_link_info(
            link,
            uid,
            host,
        ),
        "ok": True,
    }

    return result


# ============================================================
# AUTO CREATE
# ============================================================

@app.post("/api/links/auto")
async def create_auto_link(
    request: Request,
    _=Depends(require_auth),
):
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict): body = {}
    host = get_host(request)
    protocol = normalize_protocol(body.get("protocol", DEFAULT_PROTOCOL))
    profile = str(body.get("profile", "balanced")).strip().lower()
    profiles = {
        "normal": {"ip":0,"conn":0,"speed":0,"fp":"chrome","fragment":"off"},
        "balanced": {"ip":2,"conn":4,"speed":0,"fp":"chrome","fragment":"safe"},
        "gaming": {"ip":1,"conn":2,"speed":0,"fp":"chrome","fragment":"safe"},
        "maximum": {"ip":0,"conn":0,"speed":0,"fp":"randomized","fragment":"safe"},
    }
    cfg = profiles.get(profile, profiles["balanced"])
    uid, link = await make_link(
        label=auto_config_name(), limit_bytes=0, expires_at=None,
        ip_limit=cfg["ip"], speed_limit_bytes=cfg["speed"], connection_limit=cfg["conn"],
        note=f"Auto generated by VodiWalker | profile={profile}",
        protocol=protocol, fingerprint=cfg["fp"],
        alpn=DEFAULT_ALPN_BY_PROTOCOL.get(protocol, ""), port=443, fragment=cfg["fragment"],
    )
    link["security_profile"] = profile
    result = {**get_link_info(link, uid, host), "ok": True, "profile": profile}
    log_activity("link", f"کانفیگ خودکار «{link['label']}» با {PROTOCOL_LABELS.get(protocol, protocol)} ساخته شد", "ok")
    return result


# ============================================================
# INBOUND CLIENT MANAGER
# ============================================================

async def add_client_to_inbound(uid: str, label: str = None, limit_bytes: int = None, expires_days: int = 0,
                                  ip_limit: int = None, speed_limit_bytes: int = None, connection_limit: int = None,
                                  note: str = None):
    """Core logic to create a real client (child link) under an inbound. Shared by the
    HTTP API and the Telegram bot so both stay in sync."""
    async with LINKS_LOCK:
        parent = LINKS.get(uid)
        if not parent:
            raise ValueError("اینباند پیدا نشد")
        source = dict(parent)
        existing_clients = sum(1 for x in LINKS.values() if x.get("parent_inbound_id") == uid)
        client_limit = int(source.get("client_limit") or 0)
        if client_limit and existing_clients >= client_limit:
            raise ValueError(f"ظرفیت اینباند تکمیل است ({client_limit} کاربر)")
    final_label = str(label or f"Client · {existing_clients+1}").strip()[:120]
    final_limit_bytes = safe_int(limit_bytes if limit_bytes is not None else source.get("limit_bytes", 0), minimum=0)
    expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days else source.get("expires_at")
    child_uid, child = await make_link(
        label=final_label,
        limit_bytes=final_limit_bytes,
        expires_at=expires_at,
        note=str(note or source.get("note") or "")[:500],
        sub_id=source.get("sub_id"),
        protocol=source.get("protocol", DEFAULT_PROTOCOL),
        fingerprint=source.get("fingerprint", DEFAULT_FINGERPRINT),
        alpn=source.get("alpn", ""),
        port=int(source.get("port", DEFAULT_PORT) or DEFAULT_PORT),
        ip_limit=safe_int(ip_limit if ip_limit is not None else source.get("ip_limit", 0), minimum=0),
        speed_limit_bytes=safe_int(speed_limit_bytes if speed_limit_bytes is not None else source.get("speed_limit_bytes", 0), minimum=0),
        connection_limit=safe_int(connection_limit if connection_limit is not None else source.get("connection_limit", 0), minimum=0),
        fragment=source.get("fragment", "off"),
        clean_ips=source.get("clean_ips", []),
        alarm_enabled=bool(source.get("alarm_enabled", False)),
        category_id=str(source.get("category_id") or "0"),
        config_count=1,
        manual_fields={k: source.get(k) for k in ("base_protocol","network","security","address","path","host_header","sni","flow","grpc_service_name","grpc_mode","xhttp_mode","header_type","allow_insecure","reality_public_key","reality_short_id","reality_spider_x","ss_method","ss_password")},
    )
    async with LINKS_LOCK:
        LINKS[child_uid]["parent_inbound_id"] = uid
        LINKS[child_uid]["is_default"] = False
        LINKS[child_uid]["protocol_label"] = protocol_display_label(LINKS[child_uid])
    await save_state()
    log_activity("client", f"کلاینت جدید برای «{source.get('label','اینباند')}» ساخته شد", "ok")
    return child_uid, LINKS[child_uid]


async def remove_inbound_client(uid: str, client_id: str):
    async with LINKS_LOCK:
        child = LINKS.get(client_id)
        if not child or child.get("parent_inbound_id") != uid:
            raise ValueError("کلاینت پیدا نشد")
        LINKS.pop(client_id, None)
    await save_state()
    log_activity("client", f"کلاینت {client_id[:8]}… حذف شد", "warn")


@app.get("/api/links/{uid}/clients")
async def list_inbound_clients(uid: str, request: Request, _=Depends(require_auth)):
    async with LINKS_LOCK:
        parent = LINKS.get(uid)
        if not parent:
            raise HTTPException(status_code=404, detail="اینباند پیدا نشد")
        children = [(cid, dict(link)) for cid, link in LINKS.items() if link.get("parent_inbound_id") == uid]
    host = get_host(request)
    return {"ok": True, "inbound": get_link_info(parent, uid, host), "clients": [get_link_info(x, cid, host) for cid, x in children]}

@app.post("/api/links/{uid}/clients")
async def create_inbound_client(uid: str, request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    try:
        child_uid, _child = await add_client_to_inbound(
            uid,
            label=body.get("label"),
            limit_bytes=body.get("limit_bytes"),
            expires_days=safe_int(body.get("expires_days", 0), minimum=0),
            ip_limit=body.get("ip_limit"),
            speed_limit_bytes=body.get("speed_limit_bytes"),
            connection_limit=body.get("connection_limit"),
            note=body.get("note"),
        )
    except ValueError as exc:
        code = 409 if "ظرفیت" in str(exc) else 404
        raise HTTPException(status_code=code, detail=str(exc))
    host = get_host(request)
    return {"ok": True, "client": get_link_info(LINKS[child_uid], child_uid, host)}

@app.delete("/api/links/{uid}/clients/{client_id}")
async def delete_inbound_client(uid: str, client_id: str, _=Depends(require_auth)):
    try:
        await remove_inbound_client(uid, client_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"ok": True, "deleted": client_id}

# ============================================================
# LIST LINKS
# ============================================================

@app.get("/api/protocols")
async def api_protocols(request: Request, _=Depends(require_auth)):
    return {
        "protocols": [
            {
                "id": p,
                "label": PROTOCOL_LABELS.get(p, p),
                "functional": p in LIVE_PROTOCOLS,
                "live_status": "live" if p in LIVE_PROTOCOLS else "link-only",
            }
            for p in PROTOCOLS
        ],
        "default": DEFAULT_PROTOCOL,
        "manual": {
            "base_protocols": [
                {"id": p, "label": MANUAL_BASE_PROTOCOL_LABELS.get(p, p)}
                for p in MANUAL_BASE_PROTOCOLS
            ],
            "networks": [
                {"id": n, "label": NETWORK_LABELS.get(n, n)}
                for n in NETWORKS
            ],
            "securities": [
                {"id": s, "label": SECURITY_LABELS.get(s, s)}
                for s in SECURITIES
            ],
            "xhttp_modes": list(XHTTP_MODES),
            "shadowsocks_methods": list(SHADOWSOCKS_METHODS),
            "fingerprints": list(FINGERPRINTS),
            "live_combos": [["vless", n, s] for n, s in MANUAL_LIVE_COMBOS],
        },
    }


@app.get("/api/reality-keypair")
async def api_reality_keypair(_=Depends(require_auth)):
    """تولید یک جفت‌کلید X25519 و Short ID تصادفی برای Reality — دقیقاً با همان
    فرمتی که Xray-core و کلاینت‌ها (v2rayN، NekoBox، Streisand، ...) انتظار دارند
    (base64url بدون padding، ۳۲ بایت خام)."""
    try:
        from cryptography.hazmat.primitives.asymmetric import x25519
        from cryptography.hazmat.primitives import serialization

        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()

        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        b64 = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")

        return {
            "ok": True,
            "private_key": b64(priv_bytes),
            "public_key": b64(pub_bytes),
            "short_id": secrets.token_hex(4),
        }
    except Exception as exc:
        logger.exception("Reality keypair generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="تولید کلید Reality ممکن نشد. کتابخانه‌ی cryptography نصب است؟")


@app.get("/api/links")
async def list_links(
    request: Request,
    _=Depends(require_auth),
):

    host = get_host(request)

    async with LINKS_LOCK:
        snapshot = dict(LINKS)

    result = []

    for uid, link in snapshot.items():

        info = get_link_info(
            link,
            uid,
            host,
        )

        info["client_count"] = sum(1 for x in snapshot.values() if x.get("parent_inbound_id") == uid)
        result.append(
            {
                **info,

                "created_at":
                    link.get(
                        "created_at"
                    ),

                "expired":
                    is_link_expired(
                        link
                    ),

                "sub_url":
                    f"{get_scheme()}://{host}/sub/{uid}",

                "info_url":
                    f"{get_scheme()}://{host}/info/{uid}",

                "connected_ips":
                    len(
                        unique_ips_for_uuid(
                            uid
                        )
                    ),
            }
        )

    result.sort(
        key=lambda item:
            item.get(
                "created_at",
                "",
            ),
        reverse=True,
    )

    return {
        "links": result
    }


# ============================================================
# LINK INFO API
# ============================================================

@app.get("/api/links/{uid}/info")
async def link_info_api(
    uid: str,
    request: Request,
    _=Depends(require_auth),
):

    async with LINKS_LOCK:

        link = LINKS.get(uid)

        if not link:
            raise HTTPException(
                status_code=404,
                detail="link not found",
            )

        snapshot = dict(link)

    host = get_host(request)

    return {
        "ok": True,
        **get_link_info(
            snapshot,
            uid,
            host,
        ),
    }


# ============================================================
# UPDATE LINK
# ============================================================

@app.patch("/api/links/{uid}")
async def update_link(
    uid: str,
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="اطلاعات نامعتبر است",
        )

    if not isinstance(body, dict):
        raise HTTPException(
            status_code=400,
            detail="اطلاعات نامعتبر است",
        )

    async with LINKS_LOCK:

        if uid not in LINKS:
            raise HTTPException(
                status_code=404,
                detail="link not found",
            )

        link = LINKS[uid]

        old_sub = link.get(
            "sub_id"
        )

        label = link.get(
            "label",
            uid,
        )

        if "active" in body:
            link["active"] = bool(
                body["active"]
            )

        if "label" in body:

            value = str(
                body["label"]
            ).strip()

            if value:
                link["label"] = value[:60]

        if "note" in body:

            link["note"] = str(
                body.get(
                    "note",
                    "",
                )
            )[:500]

        if "reset_usage" in body:

            if body.get(
                "reset_usage"
            ):
                link[
                    "used_bytes"
                ] = 0

        if "limit_value" in body:

            value = safe_float(
                body.get(
                    "limit_value",
                    0,
                )
            )

            unit = str(
                body.get(
                    "limit_unit",
                    "GB",
                )
                or "GB"
            )

            link[
                "limit_bytes"
            ] = (
                0
                if value <= 0
                else parse_size_to_bytes(
                    value,
                    unit,
                )
            )

        if "expires_at" in body and str(body.get("expires_at") or "").strip():
            try:
                dt = datetime.fromisoformat(str(body.get("expires_at")).replace("Z", "+00:00"))
                link["expires_at"] = dt.replace(tzinfo=None).isoformat()
            except Exception:
                raise HTTPException(status_code=400, detail="زمان انقضا معتبر نیست")
        elif "expires_at" in body and not str(body.get("expires_at") or "").strip() and "expires_days" not in body:
            link["expires_at"] = None

        if "expires_days" in body:

            days = safe_int(
                body.get(
                    "expires_days",
                    0,
                ),
                minimum=0,
            )

            link[
                "expires_at"
            ] = (
                (
                    datetime.now()
                    + timedelta(
                        days=days
                    )
                ).isoformat()
                if days > 0
                else None
            )

        if "fingerprint" in body:

            fingerprint = str(
                body.get(
                    "fingerprint",
                    DEFAULT_FINGERPRINT,
                )
            ).strip().lower()

            link[
                "fingerprint"
            ] = (
                fingerprint
                if fingerprint in FINGERPRINTS
                else DEFAULT_FINGERPRINT
            )

        if "alpn" in body:

            link["alpn"] = str(
                body.get(
                    "alpn",
                    "",
                )
            )[:100]

        if "port" in body:

            p = safe_int(
                body.get(
                    "port",
                    DEFAULT_PORT,
                ),
                default=DEFAULT_PORT,
                minimum=MIN_PORT,
                maximum=MAX_PORT,
            )

            link["port"] = p

        if "ip_limit" in body:

            link["ip_limit"] = safe_int(
                body.get(
                    "ip_limit",
                    0,
                ),
                minimum=0,
            )

        if "connection_limit" in body:

            link[
                "connection_limit"
            ] = safe_int(
                body.get(
                    "connection_limit",
                    0,
                ),
                minimum=0,
            )

        if "client_limit" in body:
            link["client_limit"] = safe_int(body.get("client_limit", 0), minimum=0, maximum=1000)

        if "config_count" in body:
            link["config_count"] = safe_int(body.get("config_count", 1), minimum=1, maximum=40)

        if "speed_limit_value" in body:

            speed_value = safe_float(
                body.get(
                    "speed_limit_value",
                    0,
                )
            )

            speed_unit = str(
                body.get(
                    "speed_limit_unit",
                    "MBIT",
                )
                or "MBIT"
            )

            link[
                "speed_limit_bytes"
            ] = (
                0
                if speed_value <= 0
                else parse_speed_to_bytes(
                    speed_value,
                    speed_unit,
                )
            )

        if "protocol" in body:

            protocol = str(
                body.get(
                    "protocol",
                    DEFAULT_PROTOCOL,
                )
            ).strip().lower()

            link["protocol"] = (
                protocol
                if protocol == "manual" or protocol in PROTOCOLS
                else DEFAULT_PROTOCOL
            )
            if link["protocol"] != "manual":
                link["protocol_label"] = protocol_display_label(link)

        if link.get("protocol") == "manual" and isinstance(body.get("manual"), dict):
            manual_fields = body["manual"]
            link["base_protocol"] = normalize_base_protocol(manual_fields.get("base_protocol", link.get("base_protocol")))
            link["network"] = normalize_network(manual_fields.get("network", link.get("network")))
            link["security"] = normalize_security(manual_fields.get("security", link.get("security")))
            if "address" in manual_fields:
                link["address"] = str(manual_fields.get("address") or "").strip()[:255]
            if "path" in manual_fields:
                link["path"] = str(manual_fields.get("path") or "").strip()[:255]
            if "host_header" in manual_fields:
                link["host_header"] = str(manual_fields.get("host_header") or "").strip()[:255]
            if "sni" in manual_fields:
                link["sni"] = str(manual_fields.get("sni") or "").strip()[:255]
            if "flow" in manual_fields:
                link["flow"] = str(manual_fields.get("flow") or "").strip()[:64]
            if "grpc_service_name" in manual_fields:
                link["grpc_service_name"] = str(manual_fields.get("grpc_service_name") or "").strip()[:128]
            if "grpc_mode" in manual_fields:
                link["grpc_mode"] = str(manual_fields.get("grpc_mode") or "gun").strip()[:32] or "gun"
            if "xhttp_mode" in manual_fields:
                link["xhttp_mode"] = normalize_xhttp_mode(manual_fields.get("xhttp_mode"))
            if "header_type" in manual_fields:
                link["header_type"] = str(manual_fields.get("header_type") or "").strip()[:32]
            if "allow_insecure" in manual_fields:
                link["allow_insecure"] = bool(manual_fields.get("allow_insecure"))
            if "reality_public_key" in manual_fields:
                link["reality_public_key"] = str(manual_fields.get("reality_public_key") or "").strip()[:128]
            if "reality_short_id" in manual_fields:
                link["reality_short_id"] = str(manual_fields.get("reality_short_id") or "").strip()[:32]
            if "reality_spider_x" in manual_fields:
                link["reality_spider_x"] = str(manual_fields.get("reality_spider_x") or "/").strip()[:128] or "/"
            if "ss_method" in manual_fields:
                link["ss_method"] = str(manual_fields.get("ss_method") or "chacha20-ietf-poly1305").strip()[:80]
            if "ss_password" in manual_fields:
                link["ss_password"] = str(manual_fields.get("ss_password") or "").strip()[:255]
            link["protocol_label"] = protocol_display_label(link)

        if "fragment" in body:

            fragment = str(
                body.get(
                    "fragment",
                    "off",
                )
                or "off"
            ).strip().lower()

            if fragment not in {
                "off",
                "safe",
                "balanced",
                "aggressive",
            }:
                fragment = "off"

            link["fragment"] = fragment

        if "sub_id" in body:

            link[
                "sub_id"
            ] = (
                body.get(
                    "sub_id"
                )
                or None
            )

        new_sub = body.get(
            "sub_id",
            "UNCHANGED",
        )

    if new_sub != "UNCHANGED":

        async with SUBS_LOCK:

            if (
                old_sub
                and old_sub in SUBS
            ):

                ids = SUBS[
                    old_sub
                ].get(
                    "link_ids",
                    [],
                )

                if uid in ids:
                    ids.remove(uid)

            if (
                new_sub
                and new_sub in SUBS
            ):

                ids = SUBS[
                    new_sub
                ].setdefault(
                    "link_ids",
                    [],
                )

                if uid not in ids:
                    ids.append(uid)

    await save_state()

    log_activity(
        "link",
        (
            f"کانفیگ "
            f"«{label}» "
            f"ویرایش شد"
        ),
        "info",
    )

    return {
        "ok": True
    }


# ============================================================
# RESET USAGE
# ============================================================

@app.post(
    "/api/links/{uid}/reset-usage"
)
async def reset_link_usage(
    uid: str,
    _=Depends(require_auth),
):

    async with LINKS_LOCK:

        link = LINKS.get(uid)

        if not link:
            raise HTTPException(
                status_code=404,
                detail="link not found",
            )

        link["used_bytes"] = 0

        label = link.get(
            "label",
            uid,
        )

    await save_state()

    log_activity(
        "link",
        (
            f"مصرف کانفیگ "
            f"«{label}» ریست شد"
        ),
        "info",
    )

    return {
        "ok": True,
        "uuid": uid,
        "used_bytes": 0,
    }


# ============================================================
# REGENERATE / SWAP LINK (تعویض لینک — UUID جدید، همان تنظیمات)
# ============================================================
# لینک قدیمی بلافاصله از کار می‌افتد (چون UUID عوض شده) و یک UUID جدید با
# همان تنظیمات (حجم، انقضا، دسته، پروتکل، محدودیت‌ها و ...) جایگزینش می‌شود.
# برای کلاینت‌های فرزند یک اینباند هم پشتیبانی می‌شود.

@app.post("/api/links/{uid}/regenerate")
async def regenerate_link(
    uid: str,
    request: Request,
    _=Depends(require_auth),
):
    async with LINKS_LOCK:
        old_link = LINKS.get(uid)
        if not old_link:
            raise HTTPException(status_code=404, detail="link not found")

        new_uid = generate_uuid()
        while new_uid in LINKS:
            new_uid = generate_uuid()

        new_link = dict(old_link)
        # مصرف قبلی حفظ می‌شود (این فقط تعویض کلید/لینک است، نه ریست حجم)
        LINKS[new_uid] = new_link
        del LINKS[uid]

        parent_id = old_link.get("parent_inbound_id")
        sub_id = old_link.get("sub_id")
        label = old_link.get("label", uid)

        # اگر این اینباند بود، فرزندانش را به UUID جدید مادر وصل کن
        updated_children = 0
        for child in LINKS.values():
            if child.get("parent_inbound_id") == uid:
                child["parent_inbound_id"] = new_uid
                updated_children += 1

    if sub_id:
        async with SUBS_LOCK:
            sub = SUBS.get(sub_id)
            if sub:
                ids = sub.get("link_ids", [])
                if uid in ids:
                    ids[ids.index(uid)] = new_uid

    await save_state()

    log_activity(
        "link",
        f"لینک «{label}» تعویض شد (UUID جدید صادر شد)",
        "warn",
    )

    host = get_host(request)
    async with LINKS_LOCK:
        refreshed = LINKS.get(new_uid)

    return {
        **(get_link_info(refreshed, new_uid, host) if refreshed else {}),
        "ok": True,
        "old_uuid": uid,
        "uuid": new_uid,
        "updated_children": updated_children,
    }


# ============================================================
# LINK ACTION
# ============================================================

@app.post(
    "/api/links/{uid}/action"
)
async def link_action(
    uid: str,
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="JSON نامعتبر است",
        )

    action = str(
        body.get(
            "action",
            "",
        )
    ).strip().lower()

    if action == "reset":

        await reset_link_usage(
            uid,
            _
        )

        return {
            "ok": True,
            "action": "reset",
        }

    if action == "enable":

        result = await set_link_active(
            uid,
            True,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="link not found",
            )

        return {
            "ok": True,
            "action": "enable",
        }

    if action == "disable":

        result = await set_link_active(
            uid,
            False,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="link not found",
            )

        return {
            "ok": True,
            "action": "disable",
        }

    raise HTTPException(
        status_code=400,
        detail="unknown action",
    )


# ============================================================
# DELETE LINK
# ============================================================

@app.delete("/api/links/{uid}")
async def delete_link(
    uid: str,
    _=Depends(require_auth),
):

    label = await remove_link(uid)

    if label is None:
        raise HTTPException(
            status_code=404,
            detail="link not found",
        )

    return {
        "ok": True,
        "deleted": uid,
    }




def subscription_metadata_headers(used_bytes: int, limit_bytes: int, expires_at, host: str, info_url: str, title: str):
    """Standard subscription headers understood by v2rayNG/v2rayN/Hiddify and similar clients."""
    used_bytes = max(0, int(used_bytes or 0))
    limit_bytes = max(0, int(limit_bytes or 0))

    expire_unix = 0
    if expires_at:
        try:
            dt = datetime.fromisoformat(str(expires_at))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=IRAN_TZ) if IRAN_TZ else dt
            expire_unix = max(0, int(dt.timestamp()))
        except Exception:
            expire_unix = 0

    userinfo = f"upload=0; download={used_bytes}; total={limit_bytes}; expire={expire_unix}"

    return {
        "profile-title": quote(title, safe=""),
        "profile-web-page-url": info_url,
        "support-url": SUPPORT_URL,
        "profile-update-interval": "12",
        "subscription-userinfo": userinfo,
        "content-disposition": 'inline; filename="subscription.txt"',
    }

# ============================================================
# ONE SUBSCRIPTION LINK FOR BOTH APPS AND BROWSERS
# ============================================================
# VPN clients (v2rayNG, v2rayN, Hiddify, Clash, sing-box, ...) send a
# non-browser User-Agent and never ask for text/html, so they keep getting
# the raw base64 config feed below exactly as before. A normal visit from a
# desktop/mobile browser is redirected to the rich HTML portal instead — the
# customer only ever needs to hand out a single /sub/{uuid} link, whether
# it's pasted into an app or opened by hand to check usage.
_SUB_CLIENT_UA_HINTS = (
    "v2ray", "v2rayng", "v2rayn", "hiddify", "clash", "sing-box", "sing_box",
    "shadowrocket", "streisand", "nekobox", "nekoray", "karing", "matsuri",
    "kitsunebi", "quantumult", "surge", "loon", "stash", "husi", "foxray",
    "v2box", "happ", "flclash", "mihomo", "openclash", "passwall",
    "npvtunnel", "netch", "qv2ray", "leaf", "outline", "throne", "exclave",
    "okhttp", "curl", "wget", "python", "go-http", "libcurl",
)
_SUB_BROWSER_UA_HINTS = ("mozilla", "chrome", "safari", "firefox", "edg/", "opr/", "webkit", "gecko")

def _subscription_wants_browser_view(request: Request) -> bool:
    ua = (request.headers.get("user-agent") or "").lower()
    accept = (request.headers.get("accept") or "").lower()
    if not ua or any(h in ua for h in _SUB_CLIENT_UA_HINTS):
        return False
    return "text/html" in accept and any(h in ua for h in _SUB_BROWSER_UA_HINTS)

# ============================================================
# SINGLE SUB
# ============================================================

@app.get("/sub/{uuid}")
async def subscription_single(
    uuid: str,
    request: Request,
):

    async with LINKS_LOCK:
        link = LINKS.get(uuid)

    if not is_link_allowed(link):
        raise HTTPException(
            status_code=404,
            detail="not found or inactive",
        )

    if _subscription_wants_browser_view(request):
        return RedirectResponse(url=f"/subscription/{uuid}", status_code=307)

    host = get_host(request)
    clean_ips = link.get("clean_ips") or []
    used = int(link.get("used_bytes", 0) or 0)
    limit = int(link.get("limit_bytes", 0) or 0)
    remaining = max(0, limit - used) if limit > 0 else 0
    volume_text = f"{fmt_bytes(used)}/{fmt_bytes(limit)} (باقی {fmt_bytes(remaining)})" if limit > 0 else f"{fmt_bytes(used)}/∞"
    expires_at = link.get("expires_at")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(str(expires_at))
            now_dt = datetime.now(exp_dt.tzinfo) if getattr(exp_dt, "tzinfo", None) else datetime.now()
            secs = int((exp_dt - now_dt).total_seconds())
            if secs <= 0:
                time_text = "منقضی"
            else:
                days, rem = divmod(secs, 86400)
                hours, rem = divmod(rem, 3600)
                mins = rem // 60
                time_text = f"{days}د {hours}س" if days else (f"{hours}س {mins}د" if hours else f"{mins}د")
        except Exception:
            time_text = str(expires_at)[:16]
    else:
        time_text = "∞"
    label = str(link.get("label") or "Config")
    stats_remark = f"{label} | {volume_text} | {time_text}"
    stats_line = vless_link_for_link({**link, "label": stats_remark}, uuid, "0.0.0.0")
    lines = [stats_line]
    used_names = set()
    cfg_count = max(1, min(40, int(link.get("config_count") or 1)))
    if clean_ips:
        hosts = list(clean_ips)
        while len(hosts) < cfg_count:
            hosts.extend(clean_ips)
        hosts = hosts[:cfg_count]
        for cip in hosts:
            name = random_config_name(used_names)
            used_names.add(name)
            lines.append(vless_link_for_link({**link, "label": name}, uuid, cip))
    else:
        for i in range(cfg_count):
            name = random_config_name(used_names)
            used_names.add(name)
            lines.append(vless_link_for_link({**link, "label": name}, uuid, host))
    content = base64.b64encode("\n".join(lines).encode()).decode()
    profile_title = f"0.0.0.0 | {stats_remark}"
    headers = subscription_metadata_headers(
        used,
        limit,
        link.get("expires_at"),
        host,
        f"{get_scheme()}://{host}/info/{uuid}",
        profile_title,
    )

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )

# ============================================================
# LIVE SUBSCRIPTION TELEMETRY
# ============================================================

@app.get("/api/subscription/{uuid}")
async def subscription_telemetry(uuid: str):
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
        if not link or not is_link_allowed(link):
            raise HTTPException(status_code=404, detail="subscription not found or inactive")
        used = int(link.get("used_bytes", 0) or 0)
        limit = int(link.get("limit_bytes", 0) or 0)
        history = list(link.get("usage_history") or [])[-144:]
        if not history:
            history = [{"ts": now_ir().replace(second=0, microsecond=0).isoformat(), "used": used, "limit": limit}]
        active_ips = sorted({str(x.get("ip") or "").strip() for x in connections.values() if x.get("uuid") == uuid and str(x.get("ip") or "").strip()})
        active_sessions = sum(1 for x in connections.values() if x.get("uuid") == uuid)
        return {
            "ok": True, "uuid": uuid, "active": bool(link.get("active", True)),
            "traffic_used": used, "traffic_limit": limit,
            "traffic_remaining": max(0, limit - used) if limit else None,
            "traffic_percent": min(100, round((used / limit) * 100, 1)) if limit else 0,
            "active_connections": len(active_ips), "active_sessions": active_sessions,
            "active_ips": active_ips,
            "connection_limit": int(link.get("connection_limit", 0) or 0),
            "ip_limit": int(link.get("ip_limit", 0) or 0),
            "updated_at": now_ir().isoformat(), "usage_history": history,
        }

# ============================================================
# SMART SUBSCRIPTION PORTAL
# ============================================================

@app.get("/subscription/{uuid}", response_class=HTMLResponse)
async def subscription_portal(uuid: str, request: Request):
    '''Premium customer subscription portal. All figures come from live backend state.'''
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
        if link:
            link = dict(link)
    if not is_link_allowed(link):
        raise HTTPException(status_code=404, detail="subscription not found or inactive")

    host = get_host(request)
    raw_url = f"{get_scheme()}://{host}/sub/{uuid}"
    info_url = f"{get_scheme()}://{host}/info/{uuid}"
    label = str(link.get("label") or "VodiWalker Subscription")
    protocol = protocol_display_label(link)
    used = int(link.get("used_bytes", 0) or 0)
    limit = int(link.get("limit_bytes", 0) or 0)
    pct = min(100, round((used / limit) * 100, 1)) if limit else 0
    remaining = max(0, limit - used) if limit else None
    expires = str(link.get("expires_at") or "نامحدود")
    conn_limit = int(link.get("connection_limit", 0) or 0)
    ip_limit = int(link.get("ip_limit", 0) or 0)
    active = bool(link.get("active", True))
    active_ips = {str(x.get("ip") or "").strip() for x in connections.values()
                  if x.get("uuid") == uuid and str(x.get("ip") or "").strip()}
    active_people = len(active_ips)
    active_sessions = sum(1 for x in connections.values() if x.get("uuid") == uuid)
    qr = quote(raw_url, safe="")
    initial = (label.strip()[:1] or "V").upper()

    html = r'''<!doctype html><html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#070a12"><title>__LABEL__ · VodiWalker</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
:root{--bg:#070a12;--bg2:#0a0e19;--card:#0c111b;--card2:#101725;--line:rgba(255,255,255,.08);--text:#f8fafc;--muted:#8792a6;--soft:#59657a;--a:#8b5cf6;--a2:#6366f1;--c:#22d3ee;--g:#22c55e;--g2:#16a34a;--w:#f59e0b;--r:#ef4444;--shadow:0 24px 80px rgba(0,0,0,.35);--grid:rgba(255,255,255,.055);--url:#080c14;--radius:26px}
body[data-theme="light"]{--bg:#f4f7fb;--bg2:#eef2f8;--card:#ffffff;--card2:#f7f9fc;--line:rgba(15,23,42,.10);--text:#0f172a;--muted:#526176;--soft:#748197;--shadow:0 20px 60px rgba(15,23,42,.10);--grid:rgba(15,23,42,.08);--url:#eef2f7}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;min-height:100vh;background:
    radial-gradient(circle at 12% 0%,rgba(139,92,246,.20),transparent 32%),
    radial-gradient(circle at 100% 18%,rgba(34,211,238,.12),transparent 30%),
    radial-gradient(circle at 30% 100%,rgba(34,197,94,.08),transparent 28%),
    var(--bg);
  color:var(--text);font-family:Vazirmatn,Tahoma,sans-serif;overflow-x:hidden;transition:background .25s,color .25s}
a{text-decoration:none;color:inherit}
button{font-family:inherit;cursor:pointer}
.wrap{width:min(760px,calc(100% - 28px));margin:auto;padding:22px 0 118px}

/* TOP BAR */
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;gap:10px}
.brand{display:flex;gap:11px;align-items:center;min-width:0}
.logo{width:44px;height:44px;flex:none;border-radius:15px;display:grid;place-items:center;background:linear-gradient(135deg,#1c1533,#101b2d);border:1px solid rgba(139,92,246,.4);font-weight:900;font-size:19px;box-shadow:0 0 22px rgba(139,92,246,.22)}
.brand b{display:block;font-size:14px}
.brand small{display:block;color:var(--soft);font-size:9px;margin-top:2px;letter-spacing:.06em}
.top-actions{display:flex;align-items:center;gap:8px}
.theme-btn,.lang-btn{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:12px;padding:9px 11px;display:flex;align-items:center;gap:6px;font-size:9px;font-weight:800;transition:.2s}
.theme-btn:hover,.lang-btn:hover{transform:translateY(-1px);border-color:rgba(139,92,246,.35)}
.theme-btn i{font-size:15px;color:var(--a)}
.live{display:flex;align-items:center;gap:7px;color:var(--g);font-size:9px;font-weight:800;padding:9px 12px;border:1px solid rgba(34,197,94,.2);background:rgba(34,197,94,.08);border-radius:999px;white-space:nowrap}
.live.off{color:var(--r);border-color:rgba(239,68,68,.22);background:rgba(239,68,68,.08)}
.dot{width:7px;height:7px;border-radius:50%;background:currentColor;box-shadow:0 0 12px currentColor;animation:pulse 1.8s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}

/* IDENTITY CARD */
.identity{position:relative;overflow:hidden;border:1px solid var(--line);background:linear-gradient(150deg,rgba(20,16,34,.98),rgba(10,12,20,.98));border-radius:var(--radius);padding:24px;box-shadow:var(--shadow);margin-bottom:14px;display:grid;grid-template-columns:76px 1fr auto;gap:16px;align-items:center}
body[data-theme="light"] .identity{background:linear-gradient(150deg,#ffffff,#f7f9fc)}
.identity:after{content:"";position:absolute;width:320px;height:320px;left:-140px;top:-200px;background:radial-gradient(circle,rgba(139,92,246,.24),transparent 68%);pointer-events:none}
.avatar{position:relative;width:76px;height:76px;border-radius:50%;display:grid;place-items:center;font:900 30px Arial,sans-serif;color:#fff;background:radial-gradient(circle at 38% 32%,#3a2a63,#12101c);border:2px solid rgba(139,92,246,.55);box-shadow:0 0 26px rgba(139,92,246,.35)}
.identity h1{margin:0 0 6px;font-size:clamp(18px,4vw,23px);letter-spacing:-.02em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.identity .chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{padding:6px 10px;border:1px solid var(--line);background:rgba(255,255,255,.03);border-radius:9px;color:var(--muted);font-size:9px}
.chip b{color:var(--text)}
.chip.status-on{color:var(--g);border-color:rgba(34,197,94,.25);background:rgba(34,197,94,.08)}
.chip.status-off{color:var(--r);border-color:rgba(239,68,68,.25);background:rgba(239,68,68,.08)}
.jump-btn{justify-self:end;align-self:center;border:1px solid rgba(139,92,246,.4);background:linear-gradient(135deg,var(--a),var(--a2));color:#fff;border-radius:14px;padding:12px 16px;font-weight:800;font-size:11px;display:flex;align-items:center;gap:6px;white-space:nowrap}

/* GRID */
.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:14px}
.card{border:1px solid var(--line);background:rgba(12,17,27,.96);border-radius:24px;box-shadow:var(--shadow);overflow:hidden}
body[data-theme="light"] .card{background:var(--card)}
.head{padding:17px 19px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:center}
.head b{font-size:13px}
.head small{display:block;color:var(--soft);font-size:8px;margin-top:3px}
.body{padding:19px}

.usage{display:grid;grid-template-columns:190px 1fr;gap:18px;align-items:center}
.gauge{width:172px;height:172px;margin:auto;border-radius:50%;background:conic-gradient(var(--a) calc(var(--pct)*1%),rgba(255,255,255,.07) 0);position:relative;display:grid;place-items:center;box-shadow:0 0 55px rgba(139,92,246,.12)}
.gauge:before{content:"";position:absolute;inset:13px;border-radius:50%;background:var(--card);border:1px solid var(--line)}
body[data-theme="light"] .gauge:before{background:var(--card)}
.gauge-center{position:relative;text-align:center}
.gauge-center b{font-size:32px;letter-spacing:-.06em}
.gauge-center small{display:block;color:var(--soft);font-size:9px;margin-top:2px}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.metric{padding:13px;border:1px solid var(--line);border-radius:15px;background:var(--card2)}
.metric small{display:block;color:var(--soft);font-size:8px}
.metric b{display:block;margin-top:6px;font-size:15px;direction:ltr;text-align:right}
.metric .ok{color:var(--g)}
.metric .cyan{color:var(--c)}
.meter{margin-top:12px;height:9px;border-radius:99px;background:rgba(255,255,255,.07);overflow:hidden}
.meter i{display:block;height:100%;width:calc(var(--pct)*1%);border-radius:inherit;background:linear-gradient(90deg,var(--a),var(--c));transition:width .5s ease}
.actions{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.btn{flex:1;min-width:120px;border:1px solid var(--line);border-radius:12px;padding:12px 13px;background:var(--card2);color:var(--text);font-family:inherit;font-weight:800;font-size:10.5px;text-align:center;display:flex;align-items:center;justify-content:center;gap:6px;transition:.15s}
.btn:hover{border-color:rgba(139,92,246,.4)}
.btn.primary{background:linear-gradient(135deg,var(--a),var(--a2));border-color:transparent;color:#fff}
.url{direction:ltr;text-align:left;word-break:break-all;padding:13px;border:1px dashed var(--line);border-radius:12px;background:var(--url);color:#9ca9bd;font:9.5px/1.6 monospace}

.livebox{display:flex;align-items:center;justify-content:space-between;padding:14px;border:1px solid rgba(34,197,94,.18);background:rgba(34,197,94,.055);border-radius:15px;margin-bottom:10px}
.livebox b{font-size:24px;color:var(--g)}
.livebox small{display:block;color:var(--soft);font-size:8px}
.session{color:var(--muted);font-size:9px}
.status{display:inline-flex;padding:6px 9px;border-radius:9px;background:rgba(34,197,94,.10);color:var(--g);font-size:8px;font-weight:800}
.status.off{background:rgba(239,68,68,.1);color:var(--r)}

.expire-card{display:grid;grid-template-columns:56px 1fr auto;gap:14px;align-items:center;padding:19px}
.expire-icon{width:56px;height:56px;border-radius:16px;display:grid;place-items:center;font-size:24px;background:radial-gradient(circle at 35% 35%,rgba(245,158,11,.28),rgba(20,16,10,.2));border:1px solid rgba(245,158,11,.3);color:var(--w)}
.expire-info span{display:block;color:var(--soft);font-size:9px}
.expire-info strong{display:block;margin-top:5px;font-size:16px;direction:ltr;text-align:right}
.shield-mini{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;font-size:20px;color:var(--g);background:radial-gradient(circle,rgba(34,197,94,.18),transparent 70%);border:1px solid rgba(34,197,94,.3)}

.chart{height:180px;position:relative}
.chart svg{width:100%;height:100%;overflow:visible}
.chart .line{fill:none;stroke:var(--c);stroke-width:3;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 4px 8px rgba(34,211,238,.18))}
.chart .area{fill:url(#area)}
.chart .gridline{stroke:var(--grid);stroke-width:1}
.chart .point{fill:var(--card);stroke:var(--c);stroke-width:2}
.chart text{fill:var(--soft);font-size:8px}
.chart .last{fill:var(--c);stroke:var(--card);stroke-width:3}

.qr-wrap{display:none;place-items:center;margin-bottom:13px}
.qr-wrap.show{display:grid}
.qr-wrap img{width:170px;height:170px;padding:8px;background:#fff;border-radius:16px}

/* APP QUICK CONNECT */
.apps{display:grid;gap:10px;margin-top:4px}
.app-row{display:grid;grid-template-columns:52px 1fr auto;gap:12px;align-items:center;padding:13px 14px;border-radius:18px;background:var(--card2);border:1px solid var(--line)}
.app-icon{width:52px;height:52px;border-radius:15px;display:grid;place-items:center;font-size:23px;background:radial-gradient(circle at 35% 35%,rgba(139,92,246,.3),rgba(20,16,34,.2));border:1px solid rgba(139,92,246,.3)}
.app-name{font-weight:800;font-size:13px}
.app-tag{display:inline-block;margin-top:3px;padding:2px 7px;border-radius:7px;background:rgba(34,197,94,.12);color:var(--g);font-size:8px;font-weight:800}
.app-tag.ios{background:rgba(245,158,11,.14);color:var(--w)}
.app-go{border:1px solid rgba(139,92,246,.35);background:rgba(139,92,246,.1);color:var(--a);border-radius:11px;padding:9px 13px;font-size:10px;font-weight:800;white-space:nowrap}

.note{padding:12px;border-radius:13px;background:rgba(255,255,255,.025);color:var(--muted);font-size:9px;line-height:2;margin-top:10px}
.footer{text-align:center;color:var(--soft);font-size:8px;margin-top:18px}

/* BOTTOM NAV (mobile) */
.bottom-nav{display:none}
@media(max-width:760px){
  .bottom-nav{
    display:grid;position:fixed;z-index:30;left:50%;bottom:12px;transform:translateX(-50%);
    width:min(420px,calc(100% - 24px));grid-template-columns:repeat(3,1fr);align-items:center;
    padding:7px;border-radius:26px;background:rgba(12,17,27,.94);border:1px solid var(--line);
    box-shadow:0 15px 35px rgba(0,0,0,.45);backdrop-filter:blur(18px)
  }
  body[data-theme="light"] .bottom-nav{background:rgba(255,255,255,.94)}
  .bottom-nav button{height:52px;border:0;background:transparent;color:var(--text);font-size:19px;border-radius:19px;display:grid;place-items:center;gap:2px}
  .bottom-nav button small{font-size:8px;font-weight:800;color:var(--soft)}
  .bottom-nav button.active{background:linear-gradient(135deg,rgba(139,92,246,.22),rgba(34,211,238,.14));color:var(--a)}
  .bottom-nav button.active small{color:var(--a)}
}
.toast{position:fixed;top:16px;left:50%;z-index:100;transform:translate(-50%,-120px);padding:12px 18px;border-radius:14px;background:rgba(34,197,94,.14);color:var(--g);border:1px solid rgba(34,197,94,.35);transition:.3s;font-size:11px;font-weight:800;backdrop-filter:blur(10px)}
.toast.show{transform:translate(-50%,0)}

@media(max-width:800px){.grid,.usage{grid-template-columns:1fr}.gauge{width:170px;height:170px}.metrics{grid-template-columns:1fr 1fr}.identity{padding:20px}}
@media(max-width:500px){.metrics{grid-template-columns:1fr}.wrap{width:min(100% - 18px,1120px);padding-top:14px}.identity{border-radius:21px;grid-template-columns:60px 1fr;row-gap:12px}.identity h1{font-size:17px}.jump-btn{grid-column:1/-1}.card{border-radius:20px}.expire-card{grid-template-columns:44px 1fr}.shield-mini{display:none}}
</style></head><body><main class="wrap">

<header class="top">
  <div class="brand"><div class="logo">V</div><div><b>VodiWalker</b><small>SUBSCRIPTION CENTER</small></div></div>
  <div class="top-actions">
    <button class="theme-btn" id="themeBtn" type="button" onclick="toggleTheme()" aria-label="تغییر حالت نمایش"><i class="ti ti-sun-moon"></i><span id="themeLabel">روشن</span></button>
    <div class="live" id="liveBadge"><i class="dot"></i><span id="liveState">سرویس آنلاین</span></div>
  </div>
</header>

<section class="identity">
  <div class="avatar">__INITIAL__</div>
  <div>
    <h1>__LABEL__</h1>
    <div class="chips">
      <span class="chip">پروتکل <b>__PROTOCOL__</b></span>
      <span class="chip" id="statusChip">وضعیت <b id="heroStatus">__STATUS__</b></span>
      <span class="chip">انقضا <b id="expires">__EXPIRES__</b></span>
    </div>
  </div>
  <a class="jump-btn" href="#configs"><i class="ti ti-apps"></i> کانفیگ‌ها</a>
</section>

<section class="grid">
  <div class="card">
    <div class="head"><div><b>مصرف اشتراک</b><small>نمایش مصرف واقعی ثبت‌شده روی سرویس</small></div><span id="updated" style="color:var(--soft);font-size:8px">—</span></div>
    <div class="body">
      <div class="usage">
        <div class="gauge" id="gauge" style="--pct:__PCT__"><div class="gauge-center"><b id="pct">__PCT__%</b><small>مصرف شده</small></div></div>
        <div>
          <div class="metrics">
            <div class="metric"><small>مصرف شده</small><b class="cyan" id="used">__USED__</b></div>
            <div class="metric"><small>باقی‌مانده</small><b class="ok" id="remaining">__REMAINING__</b></div>
            <div class="metric"><small>سقف اشتراک</small><b id="limit">__LIMIT__</b></div>
            <div class="metric"><small>درصد مصرف</small><b id="summaryPct">__PCT__%</b></div>
          </div>
          <div class="meter"><i id="meter"></i></div>
          <div class="note">عدد مصرف از شمارنده واقعی سرویس خوانده می‌شود؛ با هر بار افزایش ترافیک، مقدار و نمودار به‌روزرسانی می‌شوند.</div>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="head"><div><b>اتصال‌های فعال</b><small>کاربران آنلاین همین لحظه</small></div><span class="status" id="statusBadge">فعال</span></div>
    <div class="body">
      <div class="livebox">
        <div><b id="liveConnections">__ACTIVE_CONN__</b><small>دستگاه / IP یکتا</small></div>
        <div style="text-align:left"><span class="session" id="sessions">__ACTIVE_SESSIONS__ session</span><br><span class="session" id="connectionLimit">__CONN_LIMIT__</span></div>
      </div>
      <div class="metric"><small>محدودیت IP</small><b id="ipLimit">__IP_LIMIT__</b></div>
      <div class="note">برای جلوگیری از نمایش عدد غیرواقعی، یک IP فقط یک کاربر فعال محسوب می‌شود؛ Sessionهای فنی جداگانه نمایش داده می‌شود.</div>
      <div class="actions">
        <button class="btn primary" onclick="copyLink()"><i class="ti ti-copy"></i> کپی لینک اشتراک</button>
        <a class="btn" href="__INFO_URL__"><i class="ti ti-info-circle"></i> اطلاعات سرویس</a>
      </div>
    </div>
  </div>
</section>

<section class="card" style="margin-top:14px">
  <div class="head"><div><b>روند مصرف</b><small>تغییرات ثبت‌شده مصرف اشتراک</small></div><span id="chartState" style="color:var(--soft);font-size:8px">در حال همگام‌سازی</span></div>
  <div class="body"><div class="chart" id="chart"><svg viewBox="0 0 900 190" preserveAspectRatio="none"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity=".24"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient></defs><g id="gridLines"></g><path id="areaPath" class="area"></path><path id="linePath" class="line"></path><g id="chartPoints"></g><text x="895" y="184" text-anchor="end">زمان</text></svg></div></div>
</section>

<section class="card" style="margin-top:14px">
  <div class="expire-card">
    <div class="expire-icon"><i class="ti ti-calendar-due"></i></div>
    <div class="expire-info"><span>انقضای اشتراک</span><strong id="expireStrong">__EXPIRES__</strong></div>
    <div class="shield-mini"><i class="ti ti-shield-check"></i></div>
  </div>
</section>

<section class="card" style="margin-top:14px" id="linkCard">
  <div class="head"><div><b>لینک اصلی اشتراک</b><small>برای وارد کردن در کلاینت سازگار</small></div>
    <button class="btn" style="flex:none;padding:8px 12px" onclick="toggleQr()"><i class="ti ti-qrcode"></i> QR</button>
  </div>
  <div class="body">
    <div class="qr-wrap" id="qrWrap"><img src="https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=__QR__" alt="QR"></div>
    <div class="url" id="subUrl">__RAW__</div>
    <div class="actions">
      <button class="btn primary" onclick="copyLink()"><i class="ti ti-copy"></i> کپی لینک</button>
      <a class="btn" href="__RAW_URL__" target="_blank" rel="noopener"><i class="ti ti-external-link"></i> باز کردن لینک</a>
    </div>
  </div>
</section>

<section class="card" style="margin-top:14px" id="configs">
  <div class="head"><div><b>اتصال سریع</b><small>باز کردن مستقیم در برنامه کلاینت</small></div></div>
  <div class="body">
    <div class="apps">
      <div class="app-row">
        <div class="app-icon"><i class="ti ti-brand-android"></i></div>
        <div><div class="app-name">v2rayNG</div><span class="app-tag">اندروید</span></div>
        <button class="app-go" onclick="quickConnect('v2rayng://install-config?url='+encodeURIComponent(SUB_URL))">اتصال</button>
      </div>
      <div class="app-row">
        <div class="app-icon"><i class="ti ti-shield-bolt"></i></div>
        <div><div class="app-name">Hiddify</div><span class="app-tag">اندروید / iOS / ویندوز</span></div>
        <button class="app-go" onclick="quickConnect('hiddify://import/'+encodeURIComponent(SUB_URL))">اتصال</button>
      </div>
      <div class="app-row">
        <div class="app-icon"><i class="ti ti-brand-apple"></i></div>
        <div><div class="app-name">Streisand</div><span class="app-tag ios">iOS</span></div>
        <button class="app-go" onclick="quickConnect('streisand://import/'+encodeURIComponent(SUB_URL))">اتصال</button>
      </div>
      <div class="app-row">
        <div class="app-icon"><i class="ti ti-device-laptop"></i></div>
        <div><div class="app-name">NekoBox</div><span class="app-tag">دسکتاپ</span></div>
        <button class="app-go" onclick="copyLink()">کپی لینک</button>
      </div>
    </div>
    <div class="note">در صورتی که برنامه به‌صورت خودکار باز نشد، برنامه را نصب کرده و لینک کپی‌شده را به‌صورت دستی وارد کنید.</div>
  </div>
</section>

<div class="footer">VodiWalker · وضعیت و مصرف به‌صورت زنده از سرویس خوانده می‌شود</div>
</main>

<nav class="bottom-nav">
  <button class="active" onclick="copyLink()"><i class="ti ti-link"></i><small>کپی لینک</small></button>
  <button onclick="document.getElementById('configs').scrollIntoView({behavior:'smooth'})"><i class="ti ti-apps"></i><small>کانفیگ‌ها</small></button>
  <button onclick="toggleTheme()"><i class="ti ti-sun-moon"></i><small>تم</small></button>
</nav>

<div class="toast" id="toast">کپی شد ✓</div>

<script>
const SUB_URL=__RAW_JS__;
function fmt(n){n=Number(n)||0;if(!n)return'0 B';const u=['B','KB','MB','GB','TB'];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++}return(n>=100?Math.round(n):n>=10?n.toFixed(1):n.toFixed(2))+' '+u[i]}

function showToast(text){
  const toast=document.getElementById('toast');
  toast.textContent=text;
  toast.classList.add('show');
  clearTimeout(window.toastTimer);
  window.toastTimer=setTimeout(()=>toast.classList.remove('show'),2200);
}

async function copyLink(){
  try{
    await navigator.clipboard.writeText(SUB_URL);
    showToast('لینک اشتراک کپی شد ✓');
  }catch(e){
    try{
      const ta=document.createElement('textarea');
      ta.value=SUB_URL;ta.style.position='fixed';ta.style.opacity='0';
      document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();
      showToast('لینک اشتراک کپی شد ✓');
    }catch(e2){ prompt('لینک اشتراک:',SUB_URL); }
  }
}

function quickConnect(deepLink){
  copyLink();
  window.location.href=deepLink;
}

function toggleQr(){
  document.getElementById('qrWrap').classList.toggle('show');
}

function applyTheme(){
  const t=localStorage.getItem('vw_sub_theme')||'dark';
  document.body.dataset.theme=t;
  const light=t==='light';
  document.getElementById('themeLabel').textContent=light?'تیره':'روشن';
  document.querySelector('#themeBtn i').className=light?'ti ti-moon':'ti ti-sun-moon';
}
function toggleTheme(){
  const next=(document.body.dataset.theme||'dark')==='dark'?'light':'dark';
  localStorage.setItem('vw_sub_theme',next);
  applyTheme();
}
applyTheme();

function drawChart(history,limit){
  const line=document.getElementById('linePath'),area=document.getElementById('areaPath'),grid=document.getElementById('gridLines'),points=document.getElementById('chartPoints');
  const clean=Array.isArray(history)?history.filter(x=>Number.isFinite(Number(x.used))).slice(-144):[];
  if(clean.length<2){
    line.setAttribute('d','M 0 158 L 900 158');area.setAttribute('d','M 0 158 L 900 158 L 900 170 L 0 170 Z');grid.innerHTML='';points.innerHTML='';document.getElementById('chartState').textContent='در حال جمع‌آوری داده واقعی';return;
  }
  const vals=clean.map(x=>Number(x.used)||0),max=Math.max(Number(limit)||0,...vals,1),min=0;
  const top=14,bottom=162,height=bottom-top;
  grid.innerHTML=[0,.25,.5,.75,1].map(r=>{const y=bottom-height*r;return `<line class="gridline" x1="0" y1="${y}" x2="900" y2="${y}"></line><text x="0" y="${y-4}">${fmt(vals.length?max*r:0)}</text>`}).join('');
  const pts=vals.map((v,i)=>{const x=i*(900/Math.max(1,vals.length-1));const y=bottom-((v-min)/(max-min))*height;return[x,y]});
  const d=pts.map((p,i)=>(i?'L':'M')+' '+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
  line.setAttribute('d',d);area.setAttribute('d',d+' L '+pts[pts.length-1][0].toFixed(1)+' '+bottom+' L 0 '+bottom+' Z');
  points.innerHTML=pts.map((p,i)=>{const h=clean[i]?.ts?new Date(clean[i].ts).toLocaleString('fa-IR',{hour:'2-digit',minute:'2-digit'}):'';return `<circle class="point ${i===pts.length-1?'last':''}" cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="${i===pts.length-1?5:2.2}"><title>${h} · ${fmt(vals[i])}</title></circle>`}).join('');
  document.getElementById('chartState').textContent=`${clean.length} نقطه واقعی · آخرین مقدار ${fmt(vals[vals.length-1])}`;
}

async function refresh(){
  try{
    const r=await fetch('/api/subscription/__UUID__',{cache:'no-store'});
    if(!r.ok)return;
    const d=await r.json();
    const lim=Number(d.traffic_limit||0),used=Number(d.traffic_used||0),p=lim?Math.min(100,Math.round(used/lim*1000)/10):0;
    document.getElementById('gauge').style.setProperty('--pct',p);
    document.getElementById('pct').textContent=p+'%';
    document.getElementById('summaryPct').textContent=p+'%';
    document.getElementById('used').textContent=fmt(used);
    document.getElementById('limit').textContent=lim?fmt(lim):'نامحدود';
    document.getElementById('remaining').textContent=lim?fmt(Math.max(0,lim-used)):'نامحدود';
    document.getElementById('meter').style.width=p+'%';
    const active=Number(d.active_connections||0);
    document.getElementById('liveConnections').textContent=active;
    document.getElementById('sessions').textContent=Number(d.active_sessions||0)+' session';
    document.getElementById('connectionLimit').textContent=Number(d.connection_limit||0)?'حداکثر '+d.connection_limit+' اتصال':'بدون محدودیت اتصال';
    document.getElementById('ipLimit').textContent=Number(d.ip_limit||0)?'حداکثر '+d.ip_limit+' IP':'بدون محدودیت';
    const statusText=d.active?'فعال':'غیرفعال';
    document.getElementById('heroStatus').textContent=statusText;
    document.getElementById('liveState').textContent=d.active?'سرویس آنلاین':'سرویس غیرفعال';
    document.getElementById('liveBadge').classList.toggle('off',!d.active);
    document.getElementById('statusBadge').textContent=statusText;
    document.getElementById('statusBadge').classList.toggle('off',!d.active);
    document.getElementById('statusChip').classList.toggle('status-on',!!d.active);
    document.getElementById('statusChip').classList.toggle('status-off',!d.active);
    const now=new Date().toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
    document.getElementById('updated').textContent=now;
    drawChart(d.usage_history,lim);
  }catch(e){
    document.getElementById('chartState').textContent='همگام‌سازی ناموفق';
  }
}
refresh();setInterval(()=>{if(!document.hidden)refresh()},10000);
</script></body></html>'''
    replacements={
      '__LABEL__':escape_html(label),'__PROTOCOL__':escape_html(protocol),'__EXPIRES__':escape_html(expires[:19]),
      '__STATUS__':'فعال' if active else 'غیرفعال','__PCT__':str(pct),'__USED__':escape_html(fmt_bytes(used)),
      '__REMAINING__':escape_html(fmt_bytes(remaining) if remaining is not None else 'نامحدود'),
      '__LIMIT__':escape_html(fmt_bytes(limit) if limit else 'نامحدود'),'__ACTIVE_CONN__':str(active_people),
      '__ACTIVE_SESSIONS__':str(active_sessions),'__CONN_LIMIT__':('حداکثر '+str(conn_limit)+' اتصال') if conn_limit else 'بدون محدودیت اتصال',
      '__IP_LIMIT__':('حداکثر '+str(ip_limit)+' IP') if ip_limit else 'بدون محدودیت','__RAW__':escape_html(raw_url),
      '__RAW_URL__':escape_html(raw_url),'__INFO_URL__':escape_html(info_url),'__QR__':qr,'__UUID__':escape_html(uuid),
      '__RAW_JS__':repr(raw_url),'__INITIAL__':escape_html(initial),
    }
    for k,v in replacements.items(): html=html.replace(k,v)
    return HTMLResponse(html)

@app.get("/sub-all")
async def subscription_all(
    request: Request,
    _=Depends(require_auth),
):

    host = get_host(request)

    async with LINKS_LOCK:

        lines = [
            vless_link_for_link(
                link,
                uid,
                host,
            )

            for uid, link
            in LINKS.items()

            if is_link_allowed(link)
        ]

    content = (
        base64
        .b64encode(
            "\n".join(
                lines
            ).encode()
        )
        .decode()
    )

    return Response(
        content=content,
        media_type="text/plain",
    )


# ============================================================
# INFO PAGE
# ============================================================

@app.get(
    "/info/{uid}",
    response_class=HTMLResponse,
)
async def info_page(uid: str, request: Request):
    """Premium client portal. Keeps the stable /info/{uid} route but replaces the legacy card layout."""
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            return HTMLResponse("<html lang=\"fa\" dir=\"rtl\"><body style=\"margin:0;background:#070a10;color:#fff;font-family:sans-serif;padding:40px\"><h2>سرویس پیدا نشد</h2></body></html>", status_code=404)
        snapshot = dict(link)

    host = get_host(request)
    vless_url = vless_link_for_link(snapshot, uid, host)
    sub_url = f"{get_scheme()}://{host}/sub/{uid}"
    label = str(snapshot.get("label") or "VodiWalker")
    protocol = protocol_display_label(snapshot)
    used = int(snapshot.get("used_bytes", 0) or 0)
    limit = int(snapshot.get("limit_bytes", 0) or 0)
    pct = max(0, min(100, round((used / limit) * 100, 1))) if limit else 0
    remaining = fmt_bytes(max(0, limit-used)) if limit else "نامحدود"
    expires_at = snapshot.get("expires_at")
    expiry_display = str(expires_at) if expires_at else "نامحدود"
    expiry_remaining = "نامحدود"
    if expires_at:
        try:
            expiry_dt = datetime.fromisoformat(str(expires_at))
            now_dt = datetime.now(expiry_dt.tzinfo) if expiry_dt.tzinfo else datetime.now()
            seconds = int((expiry_dt - now_dt).total_seconds())
            if seconds <= 0:
                expiry_remaining = "منقضی شده"
            else:
                days, rem = divmod(seconds, 86400)
                hours, rem = divmod(rem, 3600)
                minutes, _ = divmod(rem, 60)
                expiry_remaining = f"{days} روز" if days else (f"{hours} ساعت" if hours else f"{minutes} دقیقه")
        except Exception:
            expiry_remaining = "نامشخص"
    active = is_link_allowed(snapshot)
    ip_limit = "نامحدود" if not snapshot.get("ip_limit", 0) else str(snapshot.get("ip_limit"))
    conn_limit = "نامحدود" if not snapshot.get("connection_limit", 0) else str(snapshot.get("connection_limit"))
    speed_limit = "نامحدود" if not snapshot.get("speed_limit_bytes", 0) else fmt_bytes(snapshot.get("speed_limit_bytes", 0)) + "/s"
    ips = len(unique_ips_for_uuid(uid))

    esc = lambda x: escape_html(str(x))
    label_e = esc(label); protocol_e = esc(protocol); uid_e = esc(uid)
    sub_e = esc(sub_url); vless_e = esc(vless_url); expiry_e = esc(expiry_display)
    rem_e = esc(remaining); speed_e = esc(speed_limit); ip_e = esc(ip_limit); conn_e = esc(conn_limit)
    used_e = esc(fmt_bytes(used)); limit_e = esc(fmt_bytes(limit) if limit else "نامحدود")
    status_e = "فعال" if active else "غیرفعال"
    raw_js = json.dumps(raw_url if 'raw_url' in locals() else sub_url)
    vless_js = json.dumps(vless_url)
    sub_js = json.dumps(sub_url)

    html = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#070a12"><meta name="color-scheme" content="dark"><title>__LABEL__ · VodiWalker</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
<style>
:root{--bg:#060812;--panel:#0d1220;--panel2:#111827;--line:rgba(255,255,255,.08);--muted:#8b97ad;--text:#f5f7fb;--accent:#7c5cff;--cyan:#3dd8ff;--good:#2dd4a0;--warn:#f5b942;--danger:#ff6175}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:Vazirmatn,Inter,sans-serif;background:var(--bg);color:var(--text)}body{overflow-x:hidden;background:radial-gradient(900px 420px at 85% -10%,rgba(124,92,255,.18),transparent 60%),radial-gradient(700px 380px at 5% 25%,rgba(61,216,255,.08),transparent 62%),linear-gradient(180deg,#070a12,#05070d)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.28;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(#000,transparent 90%)}
.wrap{width:min(1180px,calc(100% - 28px));margin:auto;padding:22px 0 70px;position:relative;z-index:1}.top{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:14px}.brand{display:flex;align-items:center;gap:11px}.mark{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(145deg,#1b1730,#111c2c);border:1px solid rgba(124,92,255,.35);box-shadow:0 10px 35px rgba(0,0,0,.3);font-size:18px}.brand b{display:block;font-size:15px}.brand small{display:block;color:#66738a;font-size:9px;letter-spacing:.14em;margin-top:3px}.top-actions{display:flex;gap:8px;flex-wrap:wrap}.btn{border:1px solid var(--line);background:rgba(255,255,255,.035);color:#dce3ef;border-radius:11px;padding:10px 13px;font:800 11px inherit;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;gap:7px}.btn.primary{border-color:rgba(124,92,255,.45);background:linear-gradient(135deg,#7c5cff,#5d72ff);color:#fff;box-shadow:0 12px 32px rgba(92,91,255,.2)}.btn.good{color:#7bf0c6;border-color:rgba(45,212,160,.25);background:rgba(45,212,160,.07)}
.hero{display:grid;grid-template-columns:1fr 250px;gap:18px;padding:28px;border:1px solid var(--line);border-radius:26px;background:linear-gradient(135deg,rgba(17,24,39,.92),rgba(8,12,21,.88));box-shadow:0 30px 100px rgba(0,0,0,.25);overflow:hidden;position:relative}.hero:after{content:"";position:absolute;width:360px;height:360px;left:-140px;top:-220px;border-radius:50%;background:radial-gradient(circle,rgba(124,92,255,.22),transparent 68%)}.hero-main{position:relative;z-index:1}.eyebrow{font-size:9px;letter-spacing:.18em;color:#8290a8;font-weight:900;text-transform:uppercase}.hero h1{font-size:clamp(28px,5vw,50px);line-height:1.08;letter-spacing:-.045em;margin:10px 0 8px}.hero p{margin:0;color:var(--muted);font-size:12px;line-height:2;max-width:700px}.chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:15px}.chip{border:1px solid var(--line);background:rgba(255,255,255,.035);padding:7px 9px;border-radius:10px;color:#b9c4d5;font-size:9.5px}.chip b{color:#fff}.hero-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}.qr-card{position:relative;z-index:1;border:1px solid var(--line);border-radius:20px;background:rgba(0,0,0,.18);padding:14px;text-align:center}.qr-card img{width:174px;height:174px;background:#fff;border-radius:14px;padding:8px}.qr-card small{display:block;color:#69768c;font-size:9px;margin-top:8px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}.kpi{border:1px solid var(--line);border-radius:17px;background:rgba(13,18,32,.82);padding:16px}.kpi .cap{font-size:9px;color:#6e7b90}.kpi .num{font-size:19px;font-weight:900;margin-top:6px}.kpi.good .num{color:#5ee7ba}.kpi.warn .num{color:#ffd067}.kpi.blue .num{color:#72cfff}.kpi.purple .num{color:#b8a7ff}
.grid{display:grid;grid-template-columns:1.35fr .65fr;gap:12px}.panel{border:1px solid var(--line);border-radius:20px;background:rgba(13,18,32,.84);overflow:hidden}.head{padding:16px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:10px}.head b{font-size:12px}.head small{display:block;color:#6e7b90;font-size:9px;margin-top:3px}.body{padding:18px}.usage-top{display:flex;align-items:center;gap:18px}.ring{width:130px;height:130px;border-radius:50%;background:conic-gradient(var(--accent) __PCT__%,#1b2332 0);position:relative;display:grid;place-items:center;flex-shrink:0}.ring:before{content:"";position:absolute;inset:9px;border-radius:50%;background:#0d1220}.ring>div{position:relative;text-align:center}.ring strong{font-size:22px}.ring small{display:block;color:#6d7890;font-size:8px;margin-top:2px}.usage-val{font-size:26px;font-weight:950;letter-spacing:-.04em}.usage-val span{font-size:11px;color:#69768c;font-weight:600}.bar{height:10px;border-radius:99px;background:#1a2230;overflow:hidden;margin:13px 0 9px}.bar i{display:block;height:100%;width:__PCT__%;background:linear-gradient(90deg,var(--accent),var(--cyan));border-radius:inherit}.remaining{display:flex;justify-content:space-between;gap:10px;color:#768297;font-size:9.5px;flex-wrap:wrap}.trend{margin-top:15px;border:1px solid var(--line);background:rgba(0,0,0,.12);border-radius:14px;padding:10px}.trend svg{width:100%;height:80px}.facts{display:grid;grid-template-columns:1fr 1fr;gap:9px}.fact{padding:13px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.018)}.fact small{display:block;color:#6d7890;font-size:8.5px}.fact b{display:block;margin-top:6px;font-size:11px;word-break:break-word}.linkbox{margin-top:12px;padding:13px;border:1px solid var(--line);border-radius:14px;background:#080c15;direction:ltr;text-align:left;color:#b8c7ff;font:10px/1.8 ui-monospace,SFMono-Regular,Consolas,monospace;word-break:break-all}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}.wide{grid-column:1/-1}.tech{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.tech .fact{min-height:76px}.apps{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.app{padding:13px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.018);text-decoration:none}.app b{font-size:11px}.app small{display:block;color:#6d7890;font-size:8.5px;margin-top:4px}.footer{text-align:center;color:#566174;font-size:9px;padding:22px 0}.toast{position:fixed;bottom:22px;left:50%;transform:translate(-50%,18px);opacity:0;pointer-events:none;background:#111827;border:1px solid var(--line);border-radius:12px;padding:10px 14px;font-size:10px;transition:.2s;z-index:20}.toast.show{opacity:1;transform:translate(-50%,0)}
@media(max-width:900px){.hero{grid-template-columns:1fr}.qr-card{max-width:240px}.grid{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}.tech{grid-template-columns:repeat(2,1fr)}}@media(max-width:540px){.wrap{width:calc(100% - 18px);padding-top:12px}.hero{padding:20px;border-radius:21px}.kpis{grid-template-columns:1fr 1fr}.usage-top{align-items:flex-start}.ring{width:100px;height:100px}.usage-val{font-size:21px}.facts{grid-template-columns:1fr}.tech,.apps{grid-template-columns:1fr}.actions{grid-template-columns:1fr}.top{align-items:flex-start}.top-actions{justify-content:flex-end}.hero h1{font-size:32px}}
</style></head><body>
<main class="wrap">
<div class="top"><div class="brand"><div class="mark">✦</div><div><b>VodiWalker</b><small>SECURE CLIENT PORTAL</small></div></div><div class="top-actions"><button class="btn" onclick="toggleTheme()">◐ پوسته</button><button class="btn" onclick="openQr()">▦ QR</button><span class="btn good">● __STATUS__</span></div></div>
<section class="hero"><div class="hero-main"><div class="eyebrow">Private Access Workspace</div><h1>__LABEL__</h1><p>مرکز حرفه‌ای مدیریت دسترسی شما؛ وضعیت مصرف، اعتبار سرویس، لینک اشتراک و مشخصات اتصال در یک فضای سریع و تمیز.</p><div class="chips"><span class="chip">پروتکل <b>__PROTOCOL__</b></span><span class="chip">شناسه <b>__UID_SHORT__</b></span><span class="chip">انقضا <b>__EXPIRY__</b></span></div><div class="hero-actions"><button class="btn primary" onclick="copy(SUB)">کپی Subscription</button><button class="btn" onclick="copy(VLESS)">کپی کانفیگ</button><a class="btn" href="__SUB_URL__">دریافت Subscription</a></div></div><div class="qr-card"><img id="qrImg" alt="QR"><small>اسکن برای اتصال سریع</small></div></section>
<section class="kpis"><div class="kpi good"><div class="cap">مصرف‌شده</div><div class="num">__USED__</div></div><div class="kpi warn"><div class="cap">باقی‌مانده</div><div class="num">__REMAINING__</div></div><div class="kpi blue"><div class="cap">IP فعال</div><div class="num">__IPS__</div></div><div class="kpi purple"><div class="cap">زمان باقی‌مانده</div><div class="num">__EXPIRY_REMAINING__</div></div></section>
<section class="grid"><div class="panel"><div class="head"><div><b>مصرف و سلامت سرویس</b><small>Real-time service overview</small></div><span style="color:#68e6b7;font-size:9px">● LIVE</span></div><div class="body"><div class="usage-top"><div class="ring"><div><strong>__PCT__%</strong><small>مصرف</small></div></div><div style="flex:1;min-width:0"><div class="usage-val">__USED__ <span>/ __LIMIT__</span></div><div class="bar"><i></i></div><div class="remaining"><span>باقی‌مانده: <b style="color:#dce3ef">__REMAINING__</b></span><span>انقضا: <b style="color:#dce3ef">__EXPIRY__</b></span></div></div></div><div class="trend"><small style="color:#6d7890;font-size:8.5px">روند مصرف</small><svg viewBox="0 0 700 90" preserveAspectRatio="none"><polyline points="0,78 80,68 150,72 230,48 310,55 390,34 470,43 550,24 700,18" fill="none" stroke="#6f83ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><polyline points="0,78 80,68 150,72 230,48 310,55 390,34 470,43 550,24 700,18 700,90 0,90" fill="url(#g)" opacity=".22"/><defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#6f83ff"/><stop offset="1" stop-color="#6f83ff" stop-opacity="0"/></linearGradient></defs></svg></div></div></div>
<aside class="panel"><div class="head"><div><b>مشخصات دسترسی</b><small>Limits & connection</small></div></div><div class="body"><div class="facts"><div class="fact"><small>IP Limit</small><b>__IP__</b></div><div class="fact"><small>Connection</small><b>__CONN__</b></div><div class="fact"><small>Speed</small><b>__SPEED__</b></div><div class="fact"><small>Expiry</small><b>__EXPIRY__</b></div></div><div class="linkbox" id="subLink">__SUB_URL__</div><div class="actions"><button class="btn primary" onclick="copy(SUB)">کپی لینک</button><button class="btn" onclick="openQr()">نمایش QR</button></div></div></aside></section>
<section class="panel" style="margin-top:12px"><div class="head"><div><b>اطلاعات فنی</b><small>Connection profile</small></div></div><div class="body"><div class="tech"><div class="fact"><small>Protocol</small><b dir="ltr">__PROTOCOL__</b></div><div class="fact"><small>Fingerprint</small><b dir="ltr">__FINGERPRINT__</b></div><div class="fact"><small>UUID</small><b dir="ltr">__UUID__</b></div><div class="fact"><small>Public subscription</small><b>READY</b></div></div></div></section>
<section class="panel" style="margin-top:12px"><div class="head"><div><b>کلاینت‌های پیشنهادی</b><small>Import the subscription link into a compatible client</small></div></div><div class="body"><div class="apps"><a class="app" href="https://github.com/2dust/v2rayNG/releases/latest" target="_blank" rel="noopener"><b>v2rayNG</b><small>Android</small></a><a class="app" href="https://github.com/2dust/v2rayN/releases/latest" target="_blank" rel="noopener"><b>v2rayN</b><small>Windows / macOS / Linux</small></a><a class="app" href="https://github.com/hiddify/hiddify-app/releases/latest" target="_blank" rel="noopener"><b>Hiddify</b><small>Android / Desktop</small></a></div></div></section>
<div class="footer">VodiWalker Secure Client Portal · اطلاعات اتصال فقط برای صاحب این لینک</div>
</main><div id="toast" class="toast"></div>
<div id="qrModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.86);backdrop-filter:blur(6px);z-index:10;align-items:center;justify-content:center;padding:20px"><div style="width:min(360px,100%);background:#0c1220;border:1px solid var(--line);border-radius:22px;padding:22px;text-align:center"><button class="btn" onclick="closeQr()" style="float:left">بستن</button><h3 style="margin:4px 0 16px">QR اتصال</h3><div style="background:#fff;padding:12px;border-radius:16px;display:inline-block"><div id="qrBox"></div></div><p id="qrText" style="font:9px/1.7 ui-monospace;color:#aebcff;word-break:break-all;direction:ltr;margin-top:14px"></p></div></div>
<script>
const SUB=__SUB_JS__, VLESS=__VLESS_JS__;
function toast(t){const e=document.getElementById('toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1600)}
async function copy(v){try{await navigator.clipboard.writeText(v);toast('کپی شد ✓')}catch(e){const x=document.createElement('textarea');x.value=v;document.body.appendChild(x);x.select();document.execCommand('copy');x.remove();toast('کپی شد ✓')}}
function toggleTheme(){document.body.classList.toggle('light');localStorage.setItem('vw_portal_theme',document.body.classList.contains('light')?'light':'dark')}
(function(){if(localStorage.getItem('vw_portal_theme')==='light'){document.body.classList.add('light');document.documentElement.style.setProperty('--bg','#eef1f7');document.documentElement.style.setProperty('--panel','#fff');document.documentElement.style.setProperty('--panel2','#f5f7fb');document.documentElement.style.setProperty('--text','#151827');document.documentElement.style.setProperty('--muted','#667085')}})();
function qrFor(v){try{const q=qrcode(0,'M');q.addData(v);q.make();document.getElementById('qrImg').src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(q.createSvgTag(4,4));document.getElementById('qrBox').innerHTML=q.createSvgTag(5,4);document.getElementById('qrText').textContent=v}catch(e){}}
function openQr(){document.getElementById('qrModal').style.display='flex'}function closeQr(){document.getElementById('qrModal').style.display='none'}qrFor(VLESS);
</script></body></html>"""
    repl = {
        "__LABEL__": label_e, "__PROTOCOL__": protocol_e, "__UID_SHORT__": esc(uid[:18]+'…'),
        "__EXPIRY__": expiry_e, "__STATUS__": status_e, "__USED__": used_e, "__REMAINING__": rem_e,
        "__IPS__": str(ips), "__EXPIRY_REMAINING__": esc(expiry_remaining), "__LIMIT__": limit_e,
        "__IP__": ip_e, "__CONN__": conn_e, "__SPEED__": speed_e, "__FINGERPRINT__": esc(snapshot.get("fingerprint", "chrome")),
        "__UUID__": uid_e, "__SUB_URL__": sub_e, "__VLESS_URL__": vless_e, "__PCT__": str(pct),
        "__SUB_JS__": sub_js, "__VLESS_JS__": vless_js,
    }
    for k,v in repl.items(): html = html.replace(k,v)
    return HTMLResponse(html)

# ============================================================
# SUB GROUP API
# ============================================================

@app.post("/api/subs")
async def create_sub_api(
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="JSON نامعتبر است",
        )

    sub_id, sub = await create_sub_group(
        name=body.get(
            "name",
            "گروه جدید",
        ),
        desc=body.get(
            "desc",
            "",
        ),
        password=body.get(
            "password",
            "",
        ),
    )

    host = get_host(request)

    return {
        "sub_id":
            sub_id,

        **sub,

        "password_hash":
            None,

        "public_url":
            (
                f"{get_scheme()}://{host}"
                f"/p/{sub['uuid_key']}"
            ),

        "sub_url":
            (
                f"{get_scheme()}://{host}"
                f"/sub-group/{sub['uuid_key']}"
            ),
    }


@app.get("/api/subs")
async def list_subs_api(
    request: Request,
    _=Depends(require_auth),
):

    host = get_host(request)

    async with SUBS_LOCK:
        snapshot_subs = dict(SUBS)

    async with LINKS_LOCK:
        snapshot_links = dict(LINKS)

    result = []

    for sid, sub in snapshot_subs.items():

        link_ids = sub.get(
            "link_ids",
            [],
        )

        active_count = sum(
            1
            for lid in link_ids
            if is_link_allowed(
                snapshot_links.get(
                    lid
                )
            )
        )

        total_used = sum(
            snapshot_links[
                lid
            ].get(
                "used_bytes",
                0,
            )

            for lid in link_ids

            if lid in snapshot_links
        )

        result.append(
            {
                "sub_id":
                    sid,

                **sub,

                "password_hash":
                    None,

                "has_password":
                    sub.get(
                        "password_hash"
                    ) is not None,

                "links_count":
                    len(link_ids),

                "active_count":
                    active_count,

                "total_used_bytes":
                    total_used,

                "total_used_fmt":
                    fmt_bytes(
                        total_used
                    ),

                "public_url":
                    (
                        f"{get_scheme()}://{host}"
                        f"/p/{sub['uuid_key']}"
                    ),

                "sub_url":
                    (
                        f"{get_scheme()}://{host}"
                        f"/sub-group/{sub['uuid_key']}"
                    ),
            }
        )

    result.sort(
        key=lambda item:
            item.get(
                "created_at",
                "",
            ),
        reverse=True,
    )

    return {
        "subs": result
    }


@app.patch("/api/subs/{sub_id}")
async def update_sub_api(
    sub_id: str,
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="JSON نامعتبر است",
        )

    async with SUBS_LOCK:

        if sub_id not in SUBS:
            raise HTTPException(
                status_code=404,
                detail="sub not found",
            )

        sub = SUBS[sub_id]

        if "name" in body:
            sub["name"] = str(
                body["name"]
            )[:60]

        if "desc" in body:
            sub["desc"] = str(
                body["desc"]
            )[:200]

        if "password" in body:

            password = str(
                body.get(
                    "password",
                    "",
                )
            ).strip()

            sub["password_hash"] = (
                hash_password(password)
                if password
                else None
            )

        if "link_ids" in body:

            sub["link_ids"] = list(
                body["link_ids"]
            )

    await save_state()

    return {
        "ok": True
    }


@app.delete("/api/subs/{sub_id}")
async def delete_sub_api(
    sub_id: str,
    _=Depends(require_auth),
):

    name = await remove_sub_group(
        sub_id
    )

    if name is None:
        raise HTTPException(
            status_code=404,
            detail="sub not found",
        )

    return {
        "ok": True,
        "deleted": sub_id,
    }


@app.post("/api/subs/{sub_id}/links")
async def assign_link_to_sub(
    sub_id: str,
    request: Request,
    _=Depends(require_auth),
):

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="JSON نامعتبر است",
        )

    link_id = str(
        body.get(
            "link_id",
            "",
        )
    )

    action = str(
        body.get(
            "action",
            "add",
        )
    )

    if action == "add":

        success = await set_link_sub(
            link_id,
            sub_id,
        )

    else:

        success = await set_link_sub(
            link_id,
            None,
        )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="link or sub not found",
        )

    return {
        "ok": True
    }


# ============================================================
# GROUP SUB
# ============================================================

@app.get("/sub-group/{uuid_key}")
async def sub_group_subscription(
    uuid_key: str,
    request: Request,
):

    async with SUBS_LOCK:

        sub = next(
            (
                item
                for item
                in SUBS.values()
                if item.get(
                    "uuid_key"
                ) == uuid_key
            ),
            None,
        )

    if not sub:
        raise HTTPException(
            status_code=404,
            detail="not found",
        )

    if sub.get(
        "password_hash"
    ):

        password = (
            request.query_params.get(
                "pw",
                "",
            )
        )

        if (
            hash_password(password)
            != sub["password_hash"]
        ):

            raise HTTPException(
                status_code=403,
                detail="wrong password",
            )

    host = get_host(request)

    async with LINKS_LOCK:

        lines = []

        for link_id in sub.get(
            "link_ids",
            [],
        ):

            link = LINKS.get(
                link_id
            )

            if (
                link
                and is_link_allowed(
                    link
                )
            ):

                lines.append(
                    vless_link_for_link(
                        link,
                        link_id,
                        host,
                    )
                )

    content = (
        base64
        .b64encode(
            "\n".join(
                lines
            ).encode()
        )
        .decode()
    )

    total_used = 0
    total_limit = 0
    expiries = []
    valid_ids = list(sub.get("link_ids", []))

    async with LINKS_LOCK:
        for link_id in valid_ids:
            link = LINKS.get(link_id)
            if not link or not is_link_allowed(link):
                continue
            total_used += int(link.get("used_bytes", 0) or 0)
            total_limit += int(link.get("limit_bytes", 0) or 0)
            if link.get("expires_at"):
                expiries.append(str(link.get("expires_at")))

    # For a group subscription, expose aggregate usage/expiry in standard headers.
    group_limit = total_limit if total_limit > 0 else 0
    group_expiry = None
    if expiries:
        try:
            group_expiry = min(
                expiries,
                key=lambda x: datetime.fromisoformat(x)
            )
        except Exception:
            group_expiry = expiries[0]

    group_volume_text = (
        f"{fmt_bytes(total_used)}/{fmt_bytes(group_limit)}"
        if group_limit > 0
        else f"{fmt_bytes(total_used)}/∞"
    )
    group_expiry_text = group_expiry or "∞"
    group_title = (
        f"0.0.0.0 | {group_volume_text} | {group_expiry_text} | "
        f"{sub['name']} | کانال تلگرام: VodiWalker"
    )
    headers = subscription_metadata_headers(
        total_used,
        group_limit,
        group_expiry,
        host,
        f"{get_scheme()}://{host}/public-sub/{uuid_key}",
        group_title,
    )

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )


# ============================================================
# PUBLIC GROUP
# ============================================================

PUBLIC_SUB_HTML = r"""
<!doctype html><html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#080b12"><title>VodiWalker · Subscription</title>
<style>
:root{--bg:#070a10;--panel:#0d121b;--panel2:#111823;--line:rgba(255,255,255,.08);--text:#f5f7fb;--muted:#8e9aae;--soft:#647086;--accent:#7c5cff;--cyan:#39d6ff;--green:#36d399;--red:#ff7088}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 10% 0%,rgba(124,92,255,.18),transparent 28%),radial-gradient(circle at 92% 8%,rgba(57,214,255,.09),transparent 25%),#070a10;color:var(--text);font-family:Inter,Tahoma,Arial,sans-serif}.wrap{width:min(1120px,calc(100% - 28px));margin:auto;padding:25px 0 70px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}.brand{display:flex;align-items:center;gap:10px;font-weight:900}.mark{width:40px;height:40px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#17132a,#111b2a);border:1px solid rgba(124,92,255,.35);box-shadow:inset 0 0 25px rgba(124,92,255,.09)}.brand small{display:block;color:var(--soft);font-size:9px;margin-top:3px}.badge{padding:8px 12px;border-radius:999px;border:1px solid rgba(54,211,153,.22);background:rgba(54,211,153,.07);color:#7ceabf;font-size:10px;font-weight:800}.hero{border:1px solid var(--line);border-radius:28px;padding:27px;background:linear-gradient(135deg,rgba(17,24,35,.94),rgba(9,13,20,.9));box-shadow:0 30px 100px rgba(0,0,0,.24);margin-bottom:14px}.eyebrow{font-size:9px;color:#8995aa;letter-spacing:.15em;text-transform:uppercase;font-weight:900}.hero h1{font-size:clamp(28px,5vw,46px);margin:8px 0}.hero p{color:var(--muted);font-size:12px;line-height:2;margin:0;max-width:760px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:20px}.stat{padding:14px;border:1px solid var(--line);background:rgba(255,255,255,.018);border-radius:16px}.stat label{display:block;color:var(--soft);font-size:9px;margin-bottom:7px}.stat b{font-size:18px}.layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(300px,.6fr);gap:14px}.panel{border:1px solid var(--line);background:rgba(13,18,27,.84);border-radius:23px;overflow:hidden;box-shadow:0 20px 65px rgba(0,0,0,.17)}.head{padding:16px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.head b{font-size:12px}.head small{display:block;color:var(--soft);font-size:9px;margin-top:4px}.body{padding:17px}.url{padding:13px;border-radius:14px;background:#090d15;border:1px solid var(--line);direction:ltr;text-align:left;word-break:break-all;color:#b9c7ff;font:10px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}.btn{border:0;cursor:pointer;text-decoration:none;color:#fff;background:linear-gradient(135deg,#7c5cff,#4d7cff);padding:11px 13px;border-radius:12px;font-size:10px;font-weight:850;text-align:center}.btn.alt{background:#121925;border:1px solid var(--line);color:#dce2eb}.full{grid-column:1/-1}.link{padding:14px;border:1px solid var(--line);border-radius:16px;background:rgba(255,255,255,.015);margin-bottom:9px}.link:last-child{margin-bottom:0}.linktop{display:flex;justify-content:space-between;gap:12px;align-items:center}.linkname{font-weight:850;font-size:12px}.proto{color:#a998ff;font-size:9px;margin-top:4px}.online{padding:5px 8px;border-radius:999px;font-size:8px;background:rgba(54,211,153,.08);color:#79e9bc;border:1px solid rgba(54,211,153,.18)}.offline{background:rgba(255,112,136,.08);color:#ff9aae;border-color:rgba(255,112,136,.18)}.linkmeta{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:12px}.mini{padding:9px;border-radius:11px;background:#0b1018;border:1px solid rgba(255,255,255,.05)}.mini small{display:block;color:var(--soft);font-size:8px}.mini b{display:block;margin-top:4px;font-size:10px}.qr{text-align:center}.qr img{width:190px;height:190px;background:#fff;padding:9px;border-radius:17px}.notice{margin-top:12px;padding:12px;border-radius:13px;background:rgba(57,214,255,.045);border:1px solid rgba(57,214,255,.11);color:#9eb3c9;font-size:9px;line-height:1.9}.footer{text-align:center;color:#566174;font-size:9px;padding-top:22px}.locked{max-width:500px;margin:14vh auto}.field{display:flex;gap:8px}.field input{flex:1;background:#0a0f17;border:1px solid var(--line);color:#fff;padding:12px;border-radius:12px;direction:ltr}.toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;background:#121925;border:1px solid var(--line);padding:10px 14px;border-radius:12px;font-size:10px;transition:.2s}.toast.show{opacity:1;transform:translate(-50%,0)}@media(max-width:800px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr 1fr}}@media(max-width:520px){.wrap{width:calc(100% - 18px);padding-top:12px}.hero{padding:20px}.stats{grid-template-columns:1fr 1fr}.linkmeta{grid-template-columns:1fr 1fr}.actions{grid-template-columns:1fr}}
</style></head><body><main class="wrap"><div class="top"><div class="brand"><div class="mark">✦</div><div>VodiWalker<small>GROUP SUBSCRIPTION</small></div></div><div class="badge">● آماده استفاده</div></div><div id="app"></div><div class="footer">VodiWalker · Secure subscription delivery</div></main><div class="toast" id="toast">کپی شد</div>
<script>
const key=location.pathname.split('/').pop();const qs=location.search||'';function esc(s){return String(s??'').replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[m]))}function toast(t){const e=document.getElementById('toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1600)}async function copy(v){try{await navigator.clipboard.writeText(v);toast('لینک کپی شد ✓')}catch(e){prompt('کپی کنید:',v)}}function fmt(n){if(!n)return'0 B';const u=['B','KB','MB','GB','TB'];let i=0,x=Number(n)||0;while(x>=1024&&i<u.length-1){x/=1024;i++}return(x>=100?Math.round(x):x>=10?x.toFixed(1):x.toFixed(2))+' '+u[i]}function render(d){if(d.locked){document.getElementById('app').innerHTML='<section class="panel locked"><div class="body"><div class="eyebrow">Protected subscription</div><h2>'+esc(d.name||'اشتراک')+'</h2><p style="color:var(--muted);font-size:11px;line-height:2">این اشتراک با رمز محافظت می‌شود. رمز را وارد کنید تا اطلاعات و لینک‌ها نمایش داده شوند.</p><form class="field" onsubmit="event.preventDefault();location.search='?pw='+encodeURIComponent(document.getElementById(\'pw\').value)"><input id="pw" type="password" placeholder="Subscription password"><button class="btn">ورود</button></form></div></section>';return}const links=d.links||[];const qr='https://api.qrserver.com/v1/create-qr-code/?size=220x220&data='+encodeURIComponent(d.sub_url||'');document.getElementById('app').innerHTML='<section class="hero"><div class="eyebrow">Subscription center</div><h1>'+esc(d.name||'Subscription')+'</h1><p>'+esc(d.desc||'مدیریت متمرکز کانفیگ‌ها و لینک اشتراک در یک صفحه حرفه‌ای.')+'</p><div class="stats"><div class="stat"><label>کانفیگ فعال</label><b>'+links.filter(x=>x.active).length+'</b></div><div class="stat"><label>اتصال فعال</label><b>'+Number(d.active_connections||0)+'</b></div><div class="stat"><label>مصرف کل</label><b>'+esc(d.total_used_fmt||'0 B')+'</b></div></div></section><section class="layout"><div class="panel"><div class="head"><div><b>کانفیگ‌های این اشتراک</b><small>وضعیت هر مسیر و مصرف آن</small></div><span style="color:var(--soft);font-size:9px">'+links.length+' مورد</span></div><div class="body">'+(links.length?links.map(l=>'<article class="link"><div class="linktop"><div><div class="linkname">'+esc(l.label||'Config')+'</div><div class="proto">'+esc(l.protocol||'VLESS')+'</div></div><span class="online '+(l.active?'':'offline')+'">'+(l.active?'فعال':'غیرفعال')+'</span></div><div class="linkmeta"><div class="mini"><small>مصرف</small><b>'+esc(l.used_fmt||'0 B')+' / '+esc(l.limit_fmt||'∞')+'</b></div><div class="mini"><small>اتصال</small><b>'+Number(l.connections||0)+' / '+(Number(l.connection_limit||0)||'∞')+'</b></div><div class="mini"><small>انقضا</small><b>'+esc((l.expires_at||'نامحدود').toString().slice(0,16))+'</b></div></div><div class="actions"><button class="btn" onclick="copy('+esc(JSON.stringify(l.sub_url||''))+')">کپی ساب</button><a class="btn alt" href="'+esc(l.info_url||'#')+'">جزئیات</a></div></article>').join(''):'<div style="padding:35px;text-align:center;color:var(--soft);font-size:11px">کانفیگ فعالی برای این اشتراک وجود ندارد.</div>')+'</div></div><aside class="panel"><div class="head"><div><b>لینک اصلی اشتراک</b><small>مناسب برای کلاینت‌های سازگار</small></div></div><div class="body"><div class="qr"><img src="'+qr+'" alt="QR"></div><div class="url">'+esc(d.sub_url||'')+'</div><div class="actions"><button class="btn" onclick="copy('+esc(JSON.stringify(d.sub_url||''))+')">کپی لینک</button><a class="btn alt" href="'+esc(d.sub_url||'#')+'">دریافت</a></div><div class="notice">برای استفاده، لینک بالا را در بخش Subscription کلاینت خود وارد کنید. لینک خام و API بدون تغییر باقی می‌مانند تا سازگاری حفظ شود.</div></div></aside></section>'}async function load(){try{const r=await fetch('/api/public/sub/'+encodeURIComponent(key)+qs,{cache:'no-store'});const d=await r.json();if(!r.ok)throw Error(d.detail||'خطا');render(d)}catch(e){document.getElementById('app').innerHTML='<section class="panel"><div class="body"><h2>اشتراک پیدا نشد</h2><p style="color:var(--muted)">لینک اشتراک منقضی شده، حذف شده یا در دسترس نیست.</p></div></section>'}}load();
</script></body></html>
"""



@app.get(
    "/p/{uuid_key}",
    response_class=HTMLResponse,
)
async def public_sub_page(
    uuid_key: str,
):

    async with SUBS_LOCK:

        exists = any(
            item.get(
                "uuid_key"
            ) == uuid_key
            for item in SUBS.values()
        )

    if not exists:

        return HTMLResponse(
            """
            <h2
            style="
            font-family:sans-serif;
            padding:40px;
            "
            >
            گروه پیدا نشد
            </h2>
            """,
            status_code=404,
        )

    return HTMLResponse(
        PUBLIC_SUB_HTML
    )


@app.get("/api/public/sub/{uuid_key}")
async def public_sub_data(
    uuid_key: str,
    request: Request,
):

    async with SUBS_LOCK:

        entry = next(
            (
                (
                    sid,
                    item,
                )

                for sid, item
                in SUBS.items()

                if item.get(
                    "uuid_key"
                ) == uuid_key
            ),
            None,
        )

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="not found",
        )

    _, sub = entry

    has_password = (
        sub.get(
            "password_hash"
        ) is not None
    )

    if has_password:

        password = (
            request
            .query_params
            .get(
                "pw",
                "",
            )
        )

        if (
            hash_password(password)
            != sub[
                "password_hash"
            ]
        ):

            return JSONResponse(
                {
                    "locked": True,
                    "name":
                        sub["name"],
                }
            )

    host = get_host(request)

    async with LINKS_LOCK:
        snapshot = dict(LINKS)

    links_out = []

    active_ip_set = set()
    active_session_count = 0

    for link_id in sub.get(
        "link_ids",
        [],
    ):

        link = snapshot.get(
            link_id
        )

        if not link:
            continue

        allowed = is_link_allowed(
            link
        )

        link_ips = {
            str(item.get("ip") or "").strip()
            for item in connections.values()
            if item.get("uuid") == link_id and str(item.get("ip") or "").strip()
        }
        connection_count = len(link_ips)
        active_session_count += sum(1 for item in connections.values() if item.get("uuid") == link_id)
        active_ip_set.update(link_ips)

        links_out.append(
            {
                "uuid":
                    link_id,

                "label":
                    link.get(
                        "label"
                    ),

                "active":
                    allowed,

                "protocol":
                    link.get(
                        "protocol",
                        DEFAULT_PROTOCOL,
                    ),

                "used_bytes":
                    link.get(
                        "used_bytes",
                        0,
                    ),

                "used_fmt":
                    fmt_bytes(
                        link.get(
                            "used_bytes",
                            0,
                        )
                    ),

                "limit_bytes":
                    link.get(
                        "limit_bytes",
                        0,
                    ),

                "limit_fmt":
                    (
                        "∞"
                        if not link.get(
                            "limit_bytes",
                            0,
                        )
                        else fmt_bytes(
                            link[
                                "limit_bytes"
                            ]
                        )
                    ),

                "expires_at":
                    link.get(
                        "expires_at"
                    ),

                "vless_link":
                    vless_link_for_link(
                        link,
                        link_id,
                        host,
                    ),

                "sub_url":
                    (
                        f"{get_scheme()}://{host}"
                        f"/sub/{link_id}"
                    ),

                "info_url":
                    (
                        f"{get_scheme()}://{host}"
                        f"/info/{link_id}"
                    ),

                "connections":
                    connection_count,

                "ip_limit":
                    link.get(
                        "ip_limit",
                        0,
                    ),

                "speed_limit_bytes":
                    link.get(
                        "speed_limit_bytes",
                        0,
                    ),

                "connection_limit":
                    link.get(
                        "connection_limit",
                        0,
                    ),
            }
        )

    total_used = sum(
        item["used_bytes"]
        for item in links_out
    )

    return {
        "locked": False,

        "name":
            sub["name"],

        "desc":
            sub.get(
                "desc",
                "",
            ),

        "sub_url":
            (
                f"{get_scheme()}://{host}"
                f"/sub-group/{uuid_key}"
            ),

        "active_connections":
            len(active_ip_set),

        "active_sessions":
            active_session_count,

        "active_ips":
            sorted(active_ip_set),

        "total_used_fmt":
            fmt_bytes(
                total_used
            ),

        "support":
            SUPPORT_USERNAME,

        "links":
            links_out,
    }




@app.post("/api/mix-sub")
async def mix_subscription(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON نامعتبر")
    ids = body.get("link_ids") or []
    if not isinstance(ids, list) or len(ids) < 2:
        raise HTTPException(status_code=400, detail="حداقل ۲ کانفیگ انتخاب کنید")
    if len(ids) > 40:
        raise HTTPException(status_code=400, detail="حداکثر ۴۰ کانفیگ")
    host = get_host(request)
    lines = []
    used_names = set()
    total_used = 0
    total_limit = 0
    labels = []
    async with LINKS_LOCK:
        for lid in ids:
            link = LINKS.get(lid)
            if not link or not is_link_allowed(link):
                continue
            labels.append(str(link.get("label") or lid[:8]))
            total_used += int(link.get("used_bytes", 0) or 0)
            total_limit += int(link.get("limit_bytes", 0) or 0)
            name = random_config_name(used_names)
            used_names.add(name)
            lines.append(vless_link_for_link({**link, "label": name}, lid, host))
    if not lines:
        raise HTTPException(status_code=400, detail="هیچ کانفیگ معتبری انتخاب نشده")
    # stats first line
    vol = f"{fmt_bytes(total_used)}/{fmt_bytes(total_limit)}" if total_limit > 0 else f"{fmt_bytes(total_used)}/∞"
    mix_label = "Mix-" + random_config_name()[:6]
    stats = f"{mix_label} | {vol} | {len(lines)} configs"
    first = generate_vless_link(ids[0], "127.0.0.1", remark=stats, protocol="vless-ws")
    content = base64.b64encode(("\n".join([first] + lines)).encode()).decode()
    # store as a sub group for reuse
    sub_id, sub = await create_sub_group(name=mix_label, desc="مخلوط‌سازی کانفیگ‌ها")
    async with SUBS_LOCK:
        if sub_id in SUBS:
            SUBS[sub_id]["link_ids"] = list(ids)
    await save_state()
    return {
        "ok": True,
        "sub_url": f"{get_scheme()}://{host}/sub-group/{sub['uuid_key']}",
        "name": mix_label,
        "count": len(lines),
        "content_preview": stats,
    }


@app.get("/api/categories")
async def list_categories(_=Depends(require_auth)):
    items = [{**cat, "id": cid} for cid, cat in CATEGORIES.items()]
    items.sort(key=lambda x: int(x.get("number", 0)))
    return {"categories": items}

@app.post("/api/categories")
async def create_category(request: Request, _=Depends(require_auth)):
    if len(CATEGORIES) >= 10:
        raise HTTPException(status_code=400, detail="حداکثر ۱۰ دسته‌بندی")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON نامعتبر")
    name = str(body.get("name") or "دسته جدید").strip()[:40]
    used = {int(x.get("number", 0)) for x in CATEGORIES.values()}
    num = 0
    while num in used:
        num += 1
    cid = str(num)
    limit_value = safe_float(body.get("limit_value", 0))
    limit_unit = str(body.get("limit_unit") or "GB").upper()
    limit_bytes = 0 if limit_value <= 0 else parse_size_to_bytes(limit_value, limit_unit)
    speed_value = safe_float(body.get("speed_limit_value", 0))
    speed_bytes = 0 if speed_value <= 0 else parse_speed_to_bytes(speed_value, "MBIT")
    raw_clean = body.get("clean_ips") or ""
    if isinstance(raw_clean, list):
        clean_ips = [str(x).strip() for x in raw_clean if str(x).strip()]
    else:
        clean_ips = [x.strip() for x in str(raw_clean).replace(",", "\n").splitlines() if x.strip()]
    record = {
        "id": cid, "name": name, "number": num,
        "limit_bytes": limit_bytes,
        "expires_days": safe_int(body.get("expires_days", 0), minimum=0),
        "connection_limit": safe_int(body.get("connection_limit", 0), minimum=0),
        "speed_limit_bytes": speed_bytes,
        "ip_limit": safe_int(body.get("ip_limit", 0), minimum=0),
        "clean_ips": clean_ips,
        "random_name": bool(body.get("random_name", False)),
        "single_user": bool(body.get("single_user", False)),
        "created_at": datetime.now().isoformat(),
    }
    CATEGORIES[cid] = record
    await save_state()
    return {"ok": True, **record}


@app.patch("/api/categories/{cid}")
async def update_category(cid: str, request: Request, _=Depends(require_auth)):
    if cid not in CATEGORIES:
        raise HTTPException(status_code=404, detail="یافت نشد")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON نامعتبر")
    cat = CATEGORIES[cid]
    if "name" in body:
        cat["name"] = str(body.get("name") or cat["name"]).strip()[:40]
    if "limit_value" in body:
        lv = safe_float(body.get("limit_value", 0))
        unit = str(body.get("limit_unit") or "GB").upper()
        cat["limit_bytes"] = 0 if lv <= 0 else parse_size_to_bytes(lv, unit)
    if "expires_days" in body:
        cat["expires_days"] = safe_int(body.get("expires_days", 0), minimum=0)
    if "connection_limit" in body:
        cat["connection_limit"] = safe_int(body.get("connection_limit", 0), minimum=0)
    if "speed_limit_value" in body:
        sv = safe_float(body.get("speed_limit_value", 0))
        cat["speed_limit_bytes"] = 0 if sv <= 0 else parse_speed_to_bytes(sv, "MBIT")
    if "ip_limit" in body:
        cat["ip_limit"] = safe_int(body.get("ip_limit", 0), minimum=0)
    if "clean_ips" in body:
        raw = body.get("clean_ips") or ""
        if isinstance(raw, list):
            cat["clean_ips"] = [str(x).strip() for x in raw if str(x).strip()]
        else:
            cat["clean_ips"] = [x.strip() for x in str(raw).replace(",", "\n").splitlines() if x.strip()]
    if "random_name" in body:
        cat["random_name"] = bool(body.get("random_name"))
    if "single_user" in body:
        cat["single_user"] = bool(body.get("single_user"))
    await save_state()
    return {"ok": True, **cat}

@app.delete("/api/categories/{cid}")
async def delete_category(cid: str, _=Depends(require_auth)):
    if cid in ("0", "1"):
        raise HTTPException(status_code=400, detail="پیش‌فرض قابل حذف نیست")
    if cid not in CATEGORIES:
        raise HTTPException(status_code=404, detail="یافت نشد")
    del CATEGORIES[cid]
    for link in LINKS.values():
        if str(link.get("category_id")) == cid:
            link["category_id"] = "0"
    await save_state()
    return {"ok": True}

# ============================================================
# STATS
# ============================================================

@app.get("/stats")
async def get_stats(
    _=Depends(require_auth),
):

    async with LINKS_LOCK:
        snapshot = dict(LINKS)

    return {
        "service":
            APP_NAME,

        "version":
            APP_VERSION,

        "active_connections":
            len(connections),

        "total_traffic_mb":
            round(
                stats[
                    "total_bytes"
                ]
                / (
                    1024 ** 2
                ),
                2,
            ),

        "total_traffic_bytes":
            stats[
                "total_bytes"
            ],

        "total_requests":
            stats[
                "total_requests"
            ],

        "total_errors":
            stats[
                "total_errors"
            ],

        "uptime":
            uptime(),

        "timestamp":
            datetime.now().isoformat(),

        "hourly":
            dict(
                hourly_traffic
            ),

        "recent_errors":
            list(
                error_logs
            )[-10:],

        "links_count":
            len(snapshot),

        "active_links":
            sum(
                1
                for link
                in snapshot.values()
                if is_link_allowed(
                    link
                )
            ),

        "expired_links":
            sum(
                1
                for link
                in snapshot.values()
                if is_link_expired(
                    link
                )
            ),

        "subs_count":
            len(SUBS),
    }


@app.get("/api/errors")
async def get_errors(
    _=Depends(require_auth),
):
    rows = list(error_logs)[-100:]
    warnings = sum(1 for x in rows if x.get("level") == "warn")
    client_errors = sum(1 for x in rows if x.get("source") == "client")
    return {
        "ok": True,
        "errors": rows,
        "total_errors": len(rows),
        "warnings": warnings,
        "client_errors": client_errors,
        "healthy": not any(x.get("level", "err") == "err" for x in rows[-20:]),
    }


@app.post("/api/errors/client")
async def report_client_error(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    message = str(body.get("message") or "Unknown browser error").strip()[:1200]
    path = str(body.get("path") or request.url.path).strip()[:500]
    stack = str(body.get("stack") or "").strip()[:4000]
    details = str(body.get("details") or "").strip()[:1500]
    error_logs.append({
        "error": message,
        "path": path,
        "method": "CLIENT",
        "source": "client",
        "level": "err",
        "stack": stack,
        "details": details,
        "time": datetime.now().isoformat(),
    })
    stats["total_errors"] += 1
    logger.error("Client error: %s | %s", path, message)
    return {"ok": True}


@app.post("/api/errors/clear")
async def clear_errors(_=Depends(require_owner)):
    count = len(error_logs)
    error_logs.clear()
    stats["total_errors"] = 0
    log_activity("system", f"مرکز پیام پاک شد؛ {count} خطا حذف شد", "warn" if count else "info")
    return {"ok": True, "cleared": count}


@app.get("/api/activity")
async def get_activity(
    _=Depends(require_auth),
):

    return {
        "logs":
            list(
                activity_logs
            )[-150:]
    }


# ============================================================
# CONNECTIONS
# ============================================================

@app.get("/api/connections")
async def get_connections(
    _=Depends(require_auth),
):

    async with LINKS_LOCK:
        snapshot = dict(LINKS)

    grouped = {}

    for connection in connections.values():

        ip = connection.get(
            "ip",
            "نامشخص",
        )

        link = snapshot.get(
            connection.get(
                "uuid"
            )
        )

        label = (
            link.get(
                "label"
            )
            if link
            else "نامشخص"
        )

        group = grouped.get(ip)

        if group is None:

            group = {
                "ip":
                    ip,

                "sessions":
                    0,

                "bytes":
                    0,

                "labels":
                    set(),

                "transports":
                    set(),

                "first_connected_at":
                    connection.get(
                        "connected_at"
                    ),

                "last_connected_at":
                    connection.get(
                        "connected_at"
                    ),
            }

            grouped[ip] = group

        group["sessions"] += 1

        group["bytes"] += int(
            connection.get(
                "bytes",
                0,
            )
            or 0
        )

        group["labels"].add(
            label
        )

        group["transports"].add(
            connection.get(
                "transport",
                DEFAULT_PROTOCOL,
            )
        )

    result = []

    for group in grouped.values():

        result.append(
            {
                "ip":
                    group["ip"],

                "sessions":
                    group["sessions"],

                "labels":
                    sorted(
                        group["labels"]
                    ),

                "label":
                    (
                        " · ".join(
                            sorted(
                                group["labels"]
                            )
                        )
                        if group["labels"]
                        else "نامشخص"
                    ),

                "transports":
                    sorted(
                        group["transports"]
                    ),

                "bytes":
                    group["bytes"],

                "bytes_fmt":
                    fmt_bytes(
                        group["bytes"]
                    ),

                "connected_at":
                    group[
                        "first_connected_at"
                    ],

                "last_connected_at":
                    group[
                        "last_connected_at"
                    ],
            }
        )

    result.sort(
        key=lambda item:
            item.get(
                "last_connected_at"
            )
            or "",
        reverse=True,
    )

    return {
        "connections":
            result,

        "count":
            len(result),

        "raw_count":
            len(connections),
    }


# ============================================================
# OPTIONAL EXISTING PROJECT MODULES
# ============================================================

# ============================================================
# IMPORTANT:
# DO NOT REPLACE THIS VLESS CORE.
# ============================================================

try:

    from relay_vless import (
        RELAY_BUF,
        parse_vless_header,
        check_and_use,
        relay_ws_to_tcp,
        relay_tcp_to_ws,
        websocket_tunnel,
    )

    app.add_api_websocket_route(
        "/ws/{uuid}",
        websocket_tunnel,
    )

    logger.info(
        "VLESS relay loaded."
    )

except Exception as exc:

    logger.warning(
        "VLESS relay module unavailable: %s",
        exc,
    )


# ============================================================
# XHTTP
# ============================================================

try:

    from xhttp_siz10 import (
        router as xhttp_router
    )

    app.include_router(
        xhttp_router
    )

    logger.info(
        "XHTTP module loaded."
    )

except Exception as exc:

    logger.warning(
        "XHTTP module unavailable: %s",
        exc,
    )


# ============================================================
# TELEGRAM
# ============================================================

try:

    from telegram_bot import (
        start_bot as _tg_start_bot,
        stop_bot as _tg_stop_bot,
    )

except Exception:

    async def _tg_start_bot():
        return None

    async def _tg_stop_bot():
        return None


@app.on_event("startup")
async def start_optional_telegram():

    try:

        await _tg_start_bot()

        logger.info(
            "Telegram module initialized."
        )

    except Exception as exc:

        logger.warning(
            "Telegram bot disabled/error: %s",
            exc,
        )


# ============================================================
# HTTP PROXY
# ============================================================

_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-encoding",
    "content-length",
}


@app.api_route(
    "/proxy/{target_url:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
    ],
)
async def http_proxy(
    target_url: str,
    request: Request,
):

    if not target_url.startswith("http"):
        target_url = (
            "https://"
            + target_url
        )

    if http_client is None:
        raise HTTPException(
            status_code=503,
            detail="HTTP client not ready",
        )

    try:

        body = await request.body()

        headers = {
            key: value
            for key, value
            in request.headers.items()
            if (
                key.lower()
                not in _HOP
            )
            and (
                key.lower()
                != "host"
            )
        }

        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )

        stats["total_bytes"] += len(
            response.content
        )

        bump_daily_stat("traffic_bytes", len(response.content))

        stats["total_requests"] += 1

        hourly_traffic[
            now_ir().strftime(
                "%H:00"
            )
        ] += len(
            response.content
        )

        output_headers = {
            key: value
            for key, value
            in response.headers.items()
            if key.lower() not in _HOP
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=output_headers,
        )

    except Exception as exc:

        stats["total_errors"] += 1

        error_logs.append(
            {
                "error":
                    str(exc),

                "url":
                    target_url,

                "time":
                    datetime.now().isoformat(),
            }
        )

        logger.exception(
            "Proxy error: %s",
            target_url,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Proxy error: "
                f"{exc}"
            ),
        )


# ============================================================
# DASHBOARD
# ============================================================

from pages import DASHBOARD_HTML


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):

    if not await is_valid_session(
        request.cookies.get(
            SESSION_COOKIE
        )
    ):
        return RedirectResponse(
            "/login"
        )

    await ensure_default_categories()
    await ensure_default_link()

    return HTMLResponse(
        DASHBOARD_HTML
    )


# ============================================================
# TEST
# ============================================================

@app.get(
    "/test-ws",
    response_class=HTMLResponse,
)
async def test_ws():

    return HTMLResponse(
        """
        <script>
        location.href='/dashboard'
        </script>
        """
    )


# ============================================================
# ADMIN MANAGEMENT (multi-admin / sub-admins)
# ============================================================

def _admin_public(admin_id: str, admin: dict) -> dict:
    return {
        "id": admin_id,
        "username": admin.get("username", admin_id),
        "role": admin.get("role", "admin"),
        "permissions": sorted(admin.get("permissions") or {"dashboard"}),
        "active": admin.get("active", True),
        "created_at": admin.get("created_at"),
        "last_login_at": admin.get("last_login_at"),
        "last_login_ip": admin.get("last_login_ip"),
        "credit_stars": admin.get("credit_stars", 0),
        "full_name": admin.get("full_name", ""),
        "telegram_id": admin.get("telegram_id", ""),
    }


@app.get("/api/admins")
async def api_list_admins(token=Depends(require_owner)):
    owner_entry = {
        "id": "owner",
        "username": AUTH.get("username", DEFAULT_ADMIN_USERNAME),
        "role": "owner",
        "active": True,
        "created_at": None,
        "last_login_at": None,
        "last_login_ip": None,
    }
    admins = [owner_entry] + [
        _admin_public(aid, a) for aid, a in ADMINS.items()
    ]
    return {"ok": True, "admins": admins}


@app.post("/api/admins")
async def api_create_admin(request: Request, token=Depends(require_owner)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()

    if not username or username.lower() == "owner":
        raise HTTPException(status_code=400, detail="نام کاربری نامعتبر است")

    if len(password) < LOGIN_MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"رمز عبور باید حداقل {LOGIN_MIN_PASSWORD_LENGTH} کاراکتر باشد",
        )

    if username.lower() == AUTH.get("username", DEFAULT_ADMIN_USERNAME).lower():
        raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")
    for a in ADMINS.values():
        if a.get("username", "").lower() == username.lower():
            raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")

    admin_id = secrets.token_hex(6)

    ADMINS[admin_id] = {
        "username": username,
        "password_hash": hash_password(password),
        "role": "admin",
        "permissions": list(body.get("permissions") or {"dashboard", "inbounds", "subscriptions"}),
        "active": True,
        "created_at": datetime.now().isoformat(),
        "last_login_at": None,
        "last_login_ip": None,
    }

    await save_state()

    log_activity("auth", f"ادمین جدید «{username}» ایجاد شد", "ok")

    return {"ok": True, "admin": _admin_public(admin_id, ADMINS[admin_id])}


@app.patch("/api/admins/{admin_id}")
async def api_update_admin(admin_id: str, request: Request, token=Depends(require_owner)):
    admin = ADMINS.get(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="ادمین یافت نشد")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    if "username" in body:
        new_username = str(body["username"]).strip()
        if not new_username or new_username.lower() == "owner":
            raise HTTPException(status_code=400, detail="نام کاربری نامعتبر است")
        for aid, a in ADMINS.items():
            if aid != admin_id and a.get("username", "").lower() == new_username.lower():
                raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")
        admin["username"] = new_username

    password_changed = False
    if "password" in body and str(body["password"]).strip():
        new_password = str(body["password"]).strip()
        if len(new_password) < LOGIN_MIN_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"رمز عبور باید حداقل {LOGIN_MIN_PASSWORD_LENGTH} کاراکتر باشد",
            )
        admin["password_hash"] = hash_password(new_password)
        password_changed = True

    if "permissions" in body:
        raw_permissions = body.get("permissions") or []
        if not isinstance(raw_permissions, list):
            raise HTTPException(status_code=400, detail="لیست دسترسی‌ها نامعتبر است")
        admin["permissions"] = [p for p in raw_permissions if p in ALL_PERMISSIONS]

    if "active" in body:
        admin["active"] = bool(body["active"])

    # Password changes must invalidate existing sessions for that account.
    # Otherwise an old stolen/remembered session would remain usable after a
    # credential reset. Deactivation also revokes every session.
    if password_changed or not admin.get("active", True):
        async with SESSIONS_LOCK:
            for tok in [t for t, info in SESSIONS.items()
                        if isinstance(info, dict) and info.get("admin_id") == admin_id]:
                SESSIONS.pop(tok, None)

    await save_state()

    log_activity("auth", f"اطلاعات ادمین «{admin.get('username')}» ویرایش شد", "ok")

    return {"ok": True, "admin": _admin_public(admin_id, admin)}


@app.delete("/api/admins/{admin_id}")
async def api_delete_admin(admin_id: str, token=Depends(require_owner)):
    admin = ADMINS.pop(admin_id, None)
    if not admin:
        raise HTTPException(status_code=404, detail="ادمین یافت نشد")

    async with SESSIONS_LOCK:
        for tok in [t for t, info in SESSIONS.items() if isinstance(info, dict) and info.get("admin_id") == admin_id]:
            SESSIONS.pop(tok, None)

    await save_state()

    log_activity("auth", f"ادمین «{admin.get('username')}» حذف شد", "warn")

    return {"ok": True}


# ============================================================
# ADMIN REGISTRATION REQUESTS ("ثبت‌نام ادمینی" روی صفحه لاگین)
# ============================================================

def _admin_request_public(req_id: str, req: dict) -> dict:
    return {
        "id": req_id,
        "full_name": req.get("full_name", ""),
        "telegram_id": req.get("telegram_id", ""),
        "note": req.get("note", ""),
        "status": req.get("status", "pending"),
        "created_at": req.get("created_at"),
        "decided_at": req.get("decided_at"),
        "admin_id": req.get("admin_id"),
        "ip": req.get("ip"),
    }


@app.post("/api/admin-requests")
async def api_submit_admin_request(request: Request):
    """صفحه لاگین این را صدا می‌زند؛ نیازی به احراز هویت ندارد."""

    ip = request.client.host if request.client else "unknown"

    now = time.time()
    last = ADMIN_REQUEST_RATE.get(ip, 0)
    if now - last < ADMIN_REQUEST_COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=429,
            detail="کمی صبر کنید و دوباره تلاش کنید",
        )

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    full_name = str(body.get("full_name", "")).strip()
    telegram_id = str(body.get("telegram_id", "")).strip().lstrip("@")
    note = str(body.get("note", "")).strip()[:500]

    if not full_name or len(full_name) < 3:
        raise HTTPException(status_code=400, detail="نام و نام خانوادگی را کامل وارد کنید")
    if not telegram_id or len(telegram_id) < 3:
        raise HTTPException(status_code=400, detail="آیدی تلگرام معتبر وارد کنید")

    ADMIN_REQUEST_RATE[ip] = now

    async with ADMIN_REQUESTS_LOCK:
        req_id = secrets.token_hex(6)
        ADMIN_REQUESTS[req_id] = {
            "full_name": full_name[:120],
            "telegram_id": telegram_id[:120],
            "note": note,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "decided_at": None,
            "admin_id": None,
            "ip": ip,
        }

    await save_state()

    log_activity(
        "auth",
        f"درخواست ثبت‌نام ادمین جدید از «{full_name}» (@{telegram_id})",
        "info",
    )

    return {"ok": True, "id": req_id}


@app.get("/api/admin-requests")
async def api_list_admin_requests(token=Depends(require_owner)):
    pending = sum(1 for r in ADMIN_REQUESTS.values() if r.get("status") == "pending")
    requests_list = sorted(
        (_admin_request_public(rid, r) for rid, r in ADMIN_REQUESTS.items()),
        key=lambda r: r.get("created_at") or "",
        reverse=True,
    )
    return {"ok": True, "requests": requests_list, "pending": pending}


@app.post("/api/admin-requests/{req_id}/approve")
async def api_approve_admin_request(req_id: str, request: Request, token=Depends(require_owner)):
    """مالک اینجا تصمیم می‌گیرد چه نام‌کاربری/رمز/دسترسی/شارژی به درخواست‌کننده بدهد
    و همان لحظه حساب ادمین واقعی برایش ساخته می‌شود."""

    req = ADMIN_REQUESTS.get(req_id)
    if not req:
        raise HTTPException(status_code=404, detail="درخواست یافت نشد")
    if req.get("status") != "pending":
        raise HTTPException(status_code=409, detail="این درخواست قبلاً بررسی شده است")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()

    if not username or username.lower() == "owner":
        raise HTTPException(status_code=400, detail="نام کاربری نامعتبر است")
    if len(password) < LOGIN_MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"رمز عبور باید حداقل {LOGIN_MIN_PASSWORD_LENGTH} کاراکتر باشد",
        )
    if username.lower() == AUTH.get("username", DEFAULT_ADMIN_USERNAME).lower():
        raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")
    for a in ADMINS.values():
        if a.get("username", "").lower() == username.lower():
            raise HTTPException(status_code=409, detail="این نام کاربری قبلاً استفاده شده است")

    credit_stars = safe_int(body.get("credit_stars"), default=0, minimum=0)

    admin_id = secrets.token_hex(6)
    ADMINS[admin_id] = {
        "username": username,
        "password_hash": hash_password(password),
        "role": "admin",
        "permissions": list(body.get("permissions") or {"dashboard", "inbounds", "subscriptions"}),
        "active": True,
        "created_at": datetime.now().isoformat(),
        "last_login_at": None,
        "last_login_ip": None,
        "credit_stars": credit_stars,
        "full_name": req.get("full_name", ""),
        "telegram_id": req.get("telegram_id", ""),
    }

    req["status"] = "approved"
    req["decided_at"] = datetime.now().isoformat()
    req["admin_id"] = admin_id

    await save_state()

    log_activity(
        "auth",
        f"درخواست «{req.get('full_name')}» تایید و حساب ادمین «{username}» ساخته شد",
        "ok",
    )

    delivery_message = (
        f"سلام {req.get('full_name','')} عزیز 👋\n\n"
        f"حساب ادمین شما در VodiWalker فعال شد.\n\n"
        f"نام کاربری: {username}\n"
        f"رمز عبور: {password}\n\n"
        f"از طریق صفحه ورود پنل وارد شوید و رمز خود را در اولین فرصت تغییر دهید."
    )

    return {
        "ok": True,
        "admin": _admin_public(admin_id, ADMINS[admin_id]),
        "telegram_id": req.get("telegram_id", ""),
        "delivery_message": delivery_message,
    }


@app.post("/api/admin-requests/{req_id}/reject")
async def api_reject_admin_request(req_id: str, request: Request, token=Depends(require_owner)):
    req = ADMIN_REQUESTS.get(req_id)
    if not req:
        raise HTTPException(status_code=404, detail="درخواست یافت نشد")
    if req.get("status") != "pending":
        raise HTTPException(status_code=409, detail="این درخواست قبلاً بررسی شده است")

    try:
        body = await request.json()
    except Exception:
        body = {}

    reason = str((body or {}).get("reason", "")).strip()[:300]

    req["status"] = "rejected"
    req["decided_at"] = datetime.now().isoformat()
    req["note"] = reason or req.get("note", "")

    await save_state()

    log_activity("auth", f"درخواست ادمینی «{req.get('full_name')}» رد شد", "warn")

    return {"ok": True}


@app.delete("/api/admin-requests/{req_id}")
async def api_delete_admin_request(req_id: str, token=Depends(require_owner)):
    if req_id not in ADMIN_REQUESTS:
        raise HTTPException(status_code=404, detail="درخواست یافت نشد")
    ADMIN_REQUESTS.pop(req_id, None)
    await save_state()
    return {"ok": True}


# ============================================================
# BOT CONTROL CENTER
@app.get("/api/bot/texts")
async def api_bot_texts(token=Depends(require_owner)):
    return {"ok": True, "texts": BOT_TEXTS}

@app.post("/api/bot/texts")
async def api_bot_texts_save(request: Request, token=Depends(require_owner)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")
    texts = body.get("texts") if isinstance(body, dict) else None
    if not isinstance(texts, dict):
        raise HTTPException(status_code=400, detail="ساختار متن‌ها نامعتبر است")
    for key in list(BOT_TEXTS):
        if key in texts:
            BOT_TEXTS[key] = str(texts[key])[:4000]
    await save_state()
    log_activity("bot", "متن‌های ربات از پنل بروزرسانی شد", "ok")
    return {"ok": True, "texts": BOT_TEXTS}

# PANEL SETTINGS (آدرس عمومی پنل + مدیریت ربات فروش از داخل پنل)
# ============================================================

@app.get("/api/settings")
async def api_get_settings(request: Request, token=Depends(require_owner)):
    bot_cfg = _bot_settings_snapshot()
    override_scheme, override_host = _split_base_url(CONFIG.get("public_base_url"))
    return {
        "ok": True,
        "public_base_url": CONFIG.get("public_base_url", ""),
        "effective_host": get_host(request),
        "effective_scheme": get_scheme(),
        "tcp_public_host": CONFIG.get("tcp_public_host", ""),
        "tcp_public_port": CONFIG.get("tcp_public_port", ""),
        "tcp_listen_port": _tcp_listen_port_snapshot(),
        "bot_token": bot_cfg.get("bot_token", ""),
        "bot_admin_ids": bot_cfg.get("admin_ids", ""),
        "bot_running": bot_cfg.get("running", False),
        "bot_auto_start": bool(CONFIG.get("bot_auto_start", False)),
        "admin_username": AUTH.get("username", DEFAULT_ADMIN_USERNAME),
        "sub_remark_show_name": bool(CONFIG.get("sub_remark_show_name", True)),
        "sub_remark_show_volume": bool(CONFIG.get("sub_remark_show_volume", False)),
        "sub_remark_show_id": bool(CONFIG.get("sub_remark_show_id", False)),
        "sub_remark_show_inbound": bool(CONFIG.get("sub_remark_show_inbound", False)),
    }


@app.post("/api/settings")
async def api_update_settings(request: Request, token=Depends(require_owner)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    bot_settings_changed = False

    if "public_base_url" in body:
        raw = str(body.get("public_base_url") or "").strip()
        # اعتبارسنجی سبک: اگه چیزی وارد شده، باید حداقل یک هاست معتبر ازش دربیاد
        if raw:
            _, parsed_host = _split_base_url(raw)
            if not parsed_host:
                raise HTTPException(status_code=400, detail="آدرس عمومی نامعتبر است (مثال درست: https://panel.example.com)")
        CONFIG["public_base_url"] = raw

    if "bot_auto_start" in body:
        CONFIG["bot_auto_start"] = bool(body.get("bot_auto_start"))

    if "tcp_public_host" in body:
        CONFIG["tcp_public_host"] = str(body.get("tcp_public_host") or "").strip()

    if "tcp_public_port" in body:
        raw_port = str(body.get("tcp_public_port") or "").strip()
        if raw_port and not raw_port.isdigit():
            raise HTTPException(status_code=400, detail="پورت عمومی TCP باید عدد باشد")
        CONFIG["tcp_public_port"] = raw_port

    for flag in ("sub_remark_show_name", "sub_remark_show_volume", "sub_remark_show_id", "sub_remark_show_inbound"):
        if flag in body:
            CONFIG[flag] = bool(body.get(flag))

    try:
        import telegram_bot

        if "bot_token" in body or "bot_admin_ids" in body:
            new_token = body.get("bot_token")
            new_admin_ids = body.get("bot_admin_ids")
            telegram_bot.configure(
                token=(str(new_token).strip() if new_token is not None else None),
                admin_ids_raw=(str(new_admin_ids).strip() if new_admin_ids is not None else None),
            )
            bot_settings_changed = True
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Bot configure error: %s", exc)

    await save_state()

    # اگه ربات از قبل روشن بوده و توکن/آیدی‌ها عوض شده، برای اعمال شدنِ واقعی
    # باید دوباره راه‌اندازی بشه (وگرنه با کانکشن قدیمی به توکن قبلی وصل می‌مونه)
    restarted = False
    try:
        import telegram_bot
        if bot_settings_changed and telegram_bot.is_running():
            await telegram_bot.restart_bot()
            restarted = True
    except Exception as exc:
        logger.warning("Bot restart error: %s", exc)

    log_activity("system", "تنظیمات پنل (آدرس عمومی/ربات) به‌روزرسانی شد", "ok")

    return {"ok": True, "bot_restarted": restarted, **_bot_settings_snapshot()}


@app.post("/api/settings/bot/start")
async def api_bot_start(token=Depends(require_owner)):
    try:
        import telegram_bot
        await telegram_bot.start_bot()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"خطا در روشن کردن ربات: {exc}")
    log_activity("system", "ربات فروش از داخل پنل روشن شد", "ok")
    return {"ok": True, **_bot_settings_snapshot()}


@app.post("/api/settings/bot/stop")
async def api_bot_stop(token=Depends(require_owner)):
    try:
        import telegram_bot
        await telegram_bot.stop_bot()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"خطا در خاموش کردن ربات: {exc}")
    log_activity("system", "ربات فروش از داخل پنل خاموش شد", "warn")
    return {"ok": True, **_bot_settings_snapshot()}


# ============================================================
# PLAN MANAGEMENT (graphical, editable store plans)
# ============================================================

@app.get("/api/plans")
async def api_list_plans(token=Depends(require_auth)):
    import sales
    return {"ok": True, "plans": sales.list_plans()}


@app.post("/api/plans")
async def api_create_plan(request: Request, token=Depends(require_auth)):
    import sales

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    name = str(body.get("name", "")).strip() or "پلن جدید"

    raw_id = str(body.get("id") or name).strip().lower()
    plan_id = "".join(ch if (ch.isalnum() or ch == "-") else "-" for ch in raw_id.replace(" ", "-")).strip("-")
    plan_id = plan_id or f"plan-{secrets.token_hex(3)}"

    if sales.get_plan(plan_id):
        plan_id = f"{plan_id}-{secrets.token_hex(2)}"

    data = {
        "name": name,
        "days": safe_int(body.get("days"), default=30, minimum=0),
        "volume_gb": safe_float(body.get("volume_gb"), default=10, minimum=0),
        "speed_mbps": safe_float(body.get("speed_mbps"), default=0, minimum=0),
        "ip_limit": safe_int(body.get("ip_limit"), default=1, minimum=0),
        "stars": safe_int(body.get("stars"), default=99, minimum=0),
        "badge": str(body.get("badge", "")).strip(),
        "featured": bool(body.get("featured", False)),
        "order": safe_int(body.get("order"), default=len(sales.PLANS) + 1, minimum=0),
    }

    await sales.upsert_plan(plan_id, data)

    log_activity("plan", f"پلن «{name}» ایجاد شد", "ok")

    return {"ok": True, "plan": sales.get_plan(plan_id)}


@app.patch("/api/plans/{plan_id}")
async def api_update_plan(plan_id: str, request: Request, token=Depends(require_auth)):
    import sales

    existing = sales.get_plan(plan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="پلن یافت نشد")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="اطلاعات نامعتبر است")

    updated = dict(existing)

    if "name" in body:
        updated["name"] = str(body["name"]).strip() or updated.get("name")
    if "badge" in body:
        updated["badge"] = str(body["badge"]).strip()
    if "days" in body:
        updated["days"] = safe_int(body["days"], default=existing.get("days", 0), minimum=0)
    if "ip_limit" in body:
        updated["ip_limit"] = safe_int(body["ip_limit"], default=existing.get("ip_limit", 0), minimum=0)
    if "stars" in body:
        updated["stars"] = safe_int(body["stars"], default=existing.get("stars", 0), minimum=0)
    if "order" in body:
        updated["order"] = safe_int(body["order"], default=existing.get("order", 0), minimum=0)
    if "volume_gb" in body:
        updated["volume_gb"] = safe_float(body["volume_gb"], default=existing.get("volume_gb", 0), minimum=0)
    if "speed_mbps" in body:
        updated["speed_mbps"] = safe_float(body["speed_mbps"], default=existing.get("speed_mbps", 0), minimum=0)
    if "featured" in body:
        updated["featured"] = bool(body["featured"])

    await sales.upsert_plan(plan_id, updated)

    log_activity("plan", f"پلن «{updated.get('name')}» ویرایش شد", "ok")

    return {"ok": True, "plan": sales.get_plan(plan_id)}


@app.delete("/api/plans/{plan_id}")
async def api_delete_plan(plan_id: str, token=Depends(require_auth)):
    import sales

    existing = sales.get_plan(plan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="پلن یافت نشد")

    await sales.delete_plan(plan_id)

    log_activity("plan", f"پلن «{existing.get('name')}» حذف شد", "warn")

    return {"ok": True}


# ============================================================
# ADVANCED REPORTING
# ============================================================

@app.get("/api/reports/summary")
async def api_reports_summary(request: Request, token=Depends(require_auth)):
    days = safe_int(request.query_params.get("days"), default=14, minimum=1, maximum=180)

    today = datetime.now(IRAN_TZ) if IRAN_TZ else datetime.now()
    date_keys = [
        (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        for offset in range(days - 1, -1, -1)
    ]

    series = []
    for key in date_keys:
        bucket = DAILY_STATS.get(key, {})
        series.append({
            "date": key,
            "traffic_mb": round(bucket.get("traffic_bytes", 0) / (1024 ** 2), 2),
            "new_links": bucket.get("new_links", 0),
            "orders": bucket.get("orders", 0),
            "stars": bucket.get("stars", 0),
        })

    now_ts = time.time()
    active_links = 0
    expired_links = 0
    unlimited_links = 0
    protocol_counts = defaultdict(int)
    top_links = []

    for uid, link in LINKS.items():
        protocol_counts[protocol_display_label(link)] += 1

        expires_at = link.get("expires_at")
        is_expired = False
        if expires_at:
            try:
                is_expired = datetime.fromisoformat(expires_at).timestamp() < now_ts
            except Exception:
                is_expired = False

        if is_expired:
            expired_links += 1
        else:
            active_links += 1

        if not link.get("limit_bytes"):
            unlimited_links += 1

        top_links.append({
            "uid": uid,
            "label": link.get("label", ""),
            "used_bytes": link.get("used_bytes", 0),
            "limit_bytes": link.get("limit_bytes", 0),
            "protocol": link.get("protocol", DEFAULT_PROTOCOL),
        })

    top_links.sort(key=lambda x: x["used_bytes"], reverse=True)

    import sales
    sales_totals = sales.sales_stats()

    return {
        "ok": True,
        "series": series,
        "totals": {
            "links": len(LINKS),
            "active_links": active_links,
            "expired_links": expired_links,
            "unlimited_links": unlimited_links,
            "subs": len(SUBS),
            "admins": len(ADMINS) + 1,
            "orders": sales_totals.get("orders", 0),
            "stars": sales_totals.get("stars", 0),
            "customers": sales_totals.get("customers", 0),
        },
        "protocol_distribution": [
            {"protocol": proto, "count": count} for proto, count in protocol_counts.items()
        ],
        "top_links": top_links[:10],
    }


@app.get("/api/reports/export.csv")
async def api_reports_export_csv(token=Depends(require_auth)):
    lines = ["uid,label,protocol,used_bytes,limit_bytes,expires_at,created_at"]

    for uid, link in LINKS.items():
        row = [
            uid,
            str(link.get("label", "")).replace(",", " "),
            link.get("protocol", DEFAULT_PROTOCOL),
            str(link.get("used_bytes", 0)),
            str(link.get("limit_bytes", 0)),
            str(link.get("expires_at", "") or ""),
            str(link.get("created_at", "") or ""),
        ]
        lines.append(",".join(row))

    csv_content = "\n".join(lines)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vodiwalker-links-report.csv"},
    )


# ============================================================
# GLOBAL ERROR HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    stats[
        "total_errors"
    ] += 1

    error_logs.append(
        {
            "error": str(exc) or "internal server error",
            "path": str(request.url.path),
            "method": request.method,
            "source": "server",
            "level": "err",
            "time": datetime.now().isoformat(),
        }
    )

    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url,
    )

    # API requests
    if (
        request.url.path.startswith(
            "/api/"
        )
        or request.url.path == "/stats"
    ):

        return JSONResponse(
            {
                "ok": False,
                "error":
                    str(exc)
                or "internal server error",
            },
            status_code=500,
        )

    return HTMLResponse(
        """
        <html lang="fa" dir="rtl">
        <body style="
            background:#07070a;
            color:#fff;
            font-family:sans-serif;
            padding:40px;
        ">
            <h2>
            خطای داخلی VodiWalker
            </h2>

            <p>
            لطفاً لاگ Railway را بررسی کنید.
            </p>
        </body>
        </html>
        """,
        status_code=500,
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        workers=1,
    )
