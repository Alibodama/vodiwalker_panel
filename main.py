# ============================================================
# VodiWalker 15.0.0
# Railway Ready
# ============================================================

import asyncio
import base64
import hashlib
import hmac
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

# ------------------------------------------------------------------
# رفع باگ امنیتی CORS: قبلاً allow_origins=["*"] همراه با allow_credentials=True
# بود. این ترکیب باعث می‌شه Starlette به‌جای "*"، مقدار Origin درخواست رو عیناً
# در پاسخ منعکس کنه (چون مرورگر wildcard+credentials رو قبول نمی‌کنه) و در عمل
# هر سایتی می‌تونه با کوکی نشست کاربر (که HttpOnly نیست/است ولی از طریق fetch
# credentials:'include' قابل استفاده‌ست) به API پنل درخواست بزنه — یعنی عملاً
# محدودیتی وجود نداشت. پنل روی همون origin سرو می‌شه (fetch های نسبی '/api/...')
# پس نیازی به CORS باز برای بخش ادمین نیست؛ فقط دامنه(های) صریح مجاز می‌شن.
_cors_env = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
_public_base_url_env = os.environ.get("PUBLIC_BASE_URL", "").strip()
_railway_domain_env = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()

CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]
if _public_base_url_env:
    CORS_ALLOWED_ORIGINS.append(_public_base_url_env.rstrip("/"))
if _railway_domain_env:
    CORS_ALLOWED_ORIGINS.append(f"https://{_railway_domain_env}")
# برای توسعه‌ی محلی
CORS_ALLOWED_ORIGINS += ["http://localhost:8000", "http://127.0.0.1:8000"]
CORS_ALLOWED_ORIGINS = sorted(set(CORS_ALLOWED_ORIGINS))

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
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
    # آدرس عمومی ثابت پنل (مثلاً https://panel.example.com) — اگر ست بشه (از تنظیمات
    # پنل یا env)، به جای Host header ناپایدار درخواست‌ها برای ساخت لینک ساب استفاده می‌شه.
    # این رفع اصلیِ باگ «لینک ساب باز نمی‌شه» است: قبلاً هر درخواست ورودی (حتی یک
    # هلث‌چک یا ربات مانیتورینگ با Host نادرست) می‌تونست CONFIG["host"] سراسری رو
    # خراب کنه و لینک‌های بعدی رو با دامنه/آی‌پی اشتباه بسازه.
    "public_base_url": os.environ.get("PUBLIC_BASE_URL", "").strip(),
    # آدرس/پورت عمومی TCP برای لینک‌های vless-tcp — چون این‌ها روی یک پورت جدا
    # (tcp_relay.py) سرو می‌شن که آدرس عمومیش با آدرس پنل فرق داره (مخصوصاً روی
    # Railway که برای TCP باید از قابلیت جداگانه‌ی «TCP Proxy» استفاده بشه).
    "tcp_public_host": os.environ.get("TCP_PUBLIC_HOST", "").strip(),
    "tcp_public_port": os.environ.get("TCP_PUBLIC_PORT", "").strip(),
}


# ============================================================
# STATE
# ============================================================

LINKS: dict = {}
SUBS: dict = {}
SESSIONS: dict = {}
connections: dict = {}
CATEGORIES: dict = {}
DAILY_STATS: dict = {}  # "YYYY-MM-DD" -> {"traffic_bytes":.., "new_links":..}
DAILY_STATS_LOCK = asyncio.Lock()


def _today_key() -> str:
    now = datetime.now(IRAN_TZ) if IRAN_TZ else datetime.now()
    return now.strftime("%Y-%m-%d")


def bump_daily_stat(field: str, amount=1):
    """Increment a counter in today's reporting bucket (best-effort, in-memory)."""
    try:
        key = _today_key()
        bucket = DAILY_STATS.setdefault(
            key, {"traffic_bytes": 0, "new_links": 0}
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

# توجه: قبلاً alias هایی مثل ss→shadowsocks / socks→socks5 / hy2,hysteria→hysteria2
# وجود داشت، ولی چون shadowsocks/socks5/hysteria2 اصلاً در PROTOCOLS تعریف
# نشده‌اند (این پنل هیچ‌کدام را واقعاً سرو نمی‌کند)، normalize_protocol همیشه
# این‌ها را به DEFAULT_PROTOCOL برمی‌گرداند — یعنی alias های مرده و گمراه‌کننده
# بودند. حذف شدند تا فقط alias هایی بمانند که واقعاً به یک مقدار معتبر در
# PROTOCOLS می‌رسند.
PROTOCOL_ALIASES = {
    "vmess": "vmess-ws",
    "trojan": "trojan-ws",
}

DEFAULT_PROTOCOL = "vless-ws"

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
# این‌ها فقط برای حالت protocol == "manual" استفاده می‌شن که در آن‌ها ادمین
# خودش شبکه (Network) و امنیت (Security) و بقیه‌ی فیلدها رو دستی وارد می‌کنه.
# این حالت به‌صورت جدا از PROTOCOLS قدیمی نگه داشته شده تا منوی ربات فروش
# (که از PROTOCOLS استفاده می‌کند) دست‌نخورده و برای مشتری‌ها ساده بماند.

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


# تبدیل میلادی به شمسی (الگوریتم استاندارد و متن‌باز؛ بدون نیاز به کتابخانه‌ی جدید)
_PERSIAN_MONTHS = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"]
_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def gregorian_to_jalali(gy: int, gm: int, gd: int):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + (days % 31)
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def jalali_date_str(dt: datetime, persian_digits: bool = True) -> str:
    """تاریخ شمسی خوانا برای نمایش در صفحات سابسکریپشن (مثل «۲۱ مهر ۱۴۰۴»)."""
    try:
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        text = f"{jd} {_PERSIAN_MONTHS[jm - 1]} {jy}"
        return text.translate(_PERSIAN_DIGITS) if persian_digits else text
    except Exception:
        return dt.strftime("%Y-%m-%d")


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

    if value < 1024 ** 4:
        return (
            f"{value / 1024 ** 3:.2f} GB"
        )

    return (
        f"{value / 1024 ** 4:.2f} TB"
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
    """رفع باگ: قبلاً اگر expires_at با timezone ذخیره شده بود، مقایسه‌ی
    naive/aware با TypeError مواجه می‌شد و except آن را می‌بلعید و همیشه
    False برمی‌گرداند (کانفیگ هرگز منقضی نمی‌شد). حالا هر دو طرف مقایسه
    را به همان timezone (یا هر دو naive) هم‌تراز می‌کنیم."""
    expiry = link.get(
        "expires_at"
    )

    if not expiry:
        return False

    try:
        expiry_dt = datetime.fromisoformat(str(expiry))
    except Exception:
        return False

    try:
        if expiry_dt.tzinfo is not None:
            now = datetime.now(expiry_dt.tzinfo)
        else:
            now = datetime.now()
        return now > expiry_dt
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


def link_block_reason(link: dict | None) -> str | None:
    """چرا یک لینک اجازه‌ی اتصال ندارد؟ برای نمایش ریمارک هشدار در سابسکریپشن
    (به‌جای حذف کامل کانفیگ از لیست) استفاده می‌شود."""
    if link is None:
        return "نامعتبر"
    if not link.get("active", True):
        return "غیرفعال"
    if is_link_expired(link):
        return "منقضی"
    limit = int(link.get("limit_bytes", 0) or 0)
    used = int(link.get("used_bytes", 0) or 0)
    if limit > 0 and used >= limit:
        return "حجم تمام‌شده"
    return None


def remark_with_status(label: str, link: dict | None) -> str:
    """برچسب کانفیگ را برمی‌گرداند؛ اگر لینک مسدود باشد، پیشوند هشدار اضافه
    می‌شود تا کاربر در کلاینت خودش بفهمد چرا وصل نمی‌شود (به‌جای این‌که
    کانفیگ بی‌هیچ توضیحی از لیست حذف شود)."""
    reason = link_block_reason(link)
    if reason:
        return f"⚠️ {reason} | {label}"
    return label


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

# ------------------------------------------------------------------
# رمزنگاری پسورد: PBKDF2-HMAC-SHA256 با salt تصادفی و ۲۴۰٬۰۰۰ تکرار.
# فرمت ذخیره‌سازی: "pbkdf2$<iterations>$<salt_hex>$<hash_hex>"
# سازگاری کامل با نسخه‌ی قدیمی: هش‌های قدیمی sha256(password+SECRET_KEY)
# که یک رشته‌ی hex ساده (بدون "$") هستند، همچنان با verify_password درست
# تشخیص داده می‌شوند — هیچ ادمین/سابسکریپشنی با این ارتقا قفل نمی‌شود.
# ------------------------------------------------------------------

PBKDF2_ITERATIONS = 240_000


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        (password or "").encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def _hash_password_legacy(password: str) -> str:
    """فرمت قدیمی — فقط برای verify_password (تطبیق با هش‌های ذخیره‌شده‌ی قبلی)."""
    payload = (password + SECRET_KEY).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_password(password: str, stored_hash: str | None) -> bool:
    """رمز ورودی را با هش ذخیره‌شده مقایسه می‌کند؛ هم فرمت جدید PBKDF2 و هم
    فرمت قدیمی sha256 را می‌شناسد تا هیچ حساب قدیمی از دسترس خارج نشود."""
    if not stored_hash:
        return False

    password = password or ""

    if stored_hash.startswith("pbkdf2$"):
        try:
            _, iterations_s, salt_hex, hash_hex = stored_hash.split("$", 3)
            iterations = int(iterations_s)
            salt = bytes.fromhex(salt_hex)
        except Exception:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        ).hex()
        return hmac.compare_digest(candidate, hash_hex)

    # فرمت قدیمی: هش hex ساده‌ی sha256(password + SECRET_KEY)
    return hmac.compare_digest(_hash_password_legacy(password), stored_hash)


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

ALL_PERMISSIONS = {
    "dashboard": "مشاهده داشبورد",
    "inbounds": "مدیریت اینباند و کلاینت",
    "subscriptions": "مدیریت سابسکریپشن",
    "categories": "مدیریت دسته‌بندی",
    "reports": "گزارش‌ها",
    "messages": "مرکز پیام و خطا",
    "bot": "مدیریت ربات",
    "admins": "مدیریت ادمین‌ها",
    "settings": "تنظیمات پنل",
}

BOT_TEXTS = {
    "welcome": "🛡 <b>VodiWalker Control Center</b>\n\nاز منوی زیر عملیات موردنظر را انتخاب کنید.",
    "admin_menu": "🛠 <b>مدیریت پنل</b>\n\nساخت اینباند، کلاینت و گروه ساب از همین‌جا در دسترس است.",
    "config_created": "✅ کانفیگ با موفقیت ساخته شد.",
    "config_deleted": "🗑 کانفیگ حذف شد.",
    "config_disabled": "⛔ کانفیگ غیرفعال شد.",
    "config_enabled": "✅ کانفیگ فعال شد.",
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
    """Returns (ok, admin_id, role, display_name).

    رفع باگ امنیتی: قبلاً اگر username خالی بود ولی password صحیح بود، به‌عنوان
    owner لاگین می‌شد (چون شرط اول با هر username خالی True می‌شد). حالا هم
    username و هم password باید غیرخالی باشند، وگرنه رد می‌شود.
    """
    username = (username or "").strip()
    password = password or ""

    # هر دو فیلد باید مقدار داشته باشند؛ خالی بودن هرکدام = رد فوری.
    if not username or not password:
        return False, None, None, None

    owner_username = AUTH.get("username", DEFAULT_ADMIN_USERNAME).lower()

    if username.lower() in {"owner", owner_username}:
        if verify_password(password, AUTH["password_hash"]):
            return True, "owner", "owner", AUTH.get("username", DEFAULT_ADMIN_USERNAME)
        return False, None, None, None

    for admin_id, admin in ADMINS.items():
        if not admin.get("active", True):
            continue
        if admin.get("username", "").lower() == username.lower():
            if verify_password(password, admin.get("password_hash") or ""):
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
    * 7
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

    remark = str(link.get("label") or "Config")
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
        "network": normalize_network(link.get("network")),
        "security": normalize_security(link.get("security")),
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

        DAILY_STATS.update(
            data.get("daily_stats", {})
        )

        # migration: فیلدهای قدیمی "stars" و "orders" (مربوط به سیستم فروش
        # حذف‌شده) را از باکت‌های روزانه‌ی قدیمی پاک می‌کنیم تا در state جدید
        # دیگر ذخیره نشوند و رفرنس یتیمی باقی نماند.
        for _bucket in DAILY_STATS.values():
            if isinstance(_bucket, dict):
                _bucket.pop("stars", None)
                _bucket.pop("orders", None)

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


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    global http_client

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

    if not verify_password(current_password, current_hash):
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


@app.get("/api/inbounds")
async def list_inbounds(
    request: Request,
    _=Depends(require_auth),
):
    """فقط اینباندها (لینک‌های بدون parent_inbound_id) را برمی‌گرداند، هرکدام
    همراه با آمار تجمیعی کلاینت‌های وابسته‌اش: تعداد کل/فعال/منقضی، مجموع
    ترافیک مصرفی همه‌ی کلاینت‌ها، و وضعیت live/link-only بر اساس پروتکل."""
    host = get_host(request)

    async with LINKS_LOCK:
        snapshot = dict(LINKS)

    result = []

    for uid, link in snapshot.items():

        if link.get("parent_inbound_id"):
            continue  # این یک کلاینت است، نه اینباند

        children = [x for x in snapshot.values() if x.get("parent_inbound_id") == uid]

        active_clients = sum(1 for x in children if is_link_allowed(x))
        expired_clients = sum(1 for x in children if is_link_expired(x))
        total_client_traffic = sum(int(x.get("used_bytes", 0) or 0) for x in children)

        protocol = link.get("protocol", DEFAULT_PROTOCOL)
        live_status = "live" if protocol in LIVE_PROTOCOLS else "link-only"

        info = get_link_info(link, uid, host)
        result.append({
            **info,
            "created_at": link.get("created_at"),
            "expired": is_link_expired(link),
            "client_count": len(children),
            "active_client_count": active_clients,
            "expired_client_count": expired_clients,
            "client_total_used_bytes": total_client_traffic,
            "client_total_used_fmt": fmt_bytes(total_client_traffic),
            "live_status": live_status,
            "connected_ips": len(unique_ips_for_uuid(uid)),
        })

    result.sort(key=lambda item: item.get("created_at", ""), reverse=True)

    return {"ok": True, "inbounds": result}


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
    force: bool = False,
    _=Depends(require_auth),
):
    # اگر این لینک یک «اینباند» با کلاینت‌های وابسته باشد، بدون تأیید صریح
    # (force=true) حذف نمی‌شود تا کلاینت‌ها به‌صورت ناخواسته/بی‌صاحب نمانند.
    async with LINKS_LOCK:
        dependent_clients = [
            cid for cid, x in LINKS.items() if x.get("parent_inbound_id") == uid
        ]

    if dependent_clients and not force:
        raise HTTPException(
            status_code=409,
            detail=f"این اینباند {len(dependent_clients)} کلاینت وابسته دارد. برای حذف قطعی (همراه با کلاینت‌ها) پارامتر force=true را ارسال کنید.",
        )

    for cid in dependent_clients:
        await remove_link(cid)

    label = await remove_link(uid)

    if label is None:
        raise HTTPException(
            status_code=404,
            detail="link not found",
        )

    if dependent_clients:
        log_activity("link", f"اینباند «{label}» به همراه {len(dependent_clients)} کلاینت وابسته حذف شد", "warn")

    return {
        "ok": True,
        "deleted": uid,
        "deleted_clients": dependent_clients,
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
# SINGLE SUB
# ============================================================

@app.get("/sub/{uuid}")
async def subscription_single(
    uuid: str,
    request: Request,
):

    async with LINKS_LOCK:
        link = LINKS.get(uuid)

    # رفع باگ: قبلاً کانفیگ منقضی/غیرفعال/تمام‌شده کاملاً ۴۰۴ می‌شد و کاربر
    # هیچ توضیحی نمی‌دید. حالا فقط در صورت نبود واقعی لینک ۴۰۴ برمی‌گردد؛
    # در غیر این صورت همان یک کانفیگ با ریمارک هشدار «⚠️ منقضی/...» نمایش
    # داده می‌شود (اتصال واقعی همچنان در لایه‌ی relay رد می‌شود).
    if link is None:
        raise HTTPException(
            status_code=404,
            detail="not found",
        )

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
    label = remark_with_status(label, link)
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
# SMART SUBSCRIPTION PORTAL
# ============================================================

async def render_subscription_portal(uuid: str, request: Request) -> HTMLResponse:
    """Premium customer-facing subscription portal with live usage dashboard.
    Shared by both /subscription/{uuid} and /info/{uid} so there's a single,
    well-maintained implementation instead of two diverging templates."""
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    # رفع باگ/بهبود: قبلاً کانفیگ منقضی/غیرفعال باعث ۴۰۴ کامل صفحه می‌شد.
    # حالا فقط نبود واقعی لینک ۴۰۴ می‌دهد؛ وضعیت منقضی/غیرفعال در همین صفحه
    # (بج وضعیت، رنگ قرمز/زرد) به‌وضوح نشان داده می‌شود.
    if link is None:
        raise HTTPException(status_code=404, detail="subscription not found")
    host = get_host(request)
    raw_url = f"{get_scheme()}://{host}/sub/{uuid}"
    info_url = f"{get_scheme()}://{host}/info/{uuid}"
    label = str(link.get("label") or "VodiWalker Subscription")
    protocol = protocol_display_label(link)
    used = int(link.get("used_bytes", 0) or 0); limit = int(link.get("limit_bytes", 0) or 0)
    pct = min(100, round((used / limit) * 100, 1)) if limit > 0 else 0
    remaining = fmt_bytes(max(0, limit-used)) if limit > 0 else "نامحدود"
    expires_raw = link.get("expires_at")
    if expires_raw:
        try:
            expires = jalali_date_str(datetime.fromisoformat(str(expires_raw)))
        except Exception:
            expires = str(expires_raw)[:16]
    else:
        expires = "نامحدود"
    ip_limit = int(link.get("ip_limit", 0) or 0); conn_limit = int(link.get("connection_limit", 0) or 0)
    active = is_link_allowed(link)
    pct_class = "crit" if pct >= 90 else ("warn" if pct >= 70 else "")
    ring_circ = 263.89
    ring_offset = round(ring_circ * (1 - (pct / 100)), 2)
    days_left = None
    expired_flag = False
    if link.get("expires_at"):
        try:
            exp_dt = datetime.fromisoformat(str(link.get("expires_at")))
            now_dt = datetime.now(exp_dt.tzinfo) if getattr(exp_dt, "tzinfo", None) else datetime.now()
            days_left = (exp_dt - now_dt).days
            expired_flag = is_link_expired(link)
        except Exception:
            days_left = None
    if expired_flag:
        days_text = "منقضی شده"; days_class = "crit"
    elif days_left is None:
        days_text = "نامحدود"; days_class = ""
    elif days_left <= 3:
        days_text = f"{max(days_left,0)} روز مانده"; days_class = "warn"
    else:
        days_text = f"{days_left} روز مانده"; days_class = ""
    support_url = f"https://t.me/{str(SUPPORT_USERNAME).lstrip('@')}"
    plan_badge = str(link.get("category_name") or "")
    safe={"label":escape_html(label),"protocol":escape_html(protocol),"raw":escape_html(raw_url),"info":escape_html(info_url),"uuid":escape_html(uuid),"remaining":escape_html(remaining),"expires":escape_html(expires[:19]),"status":"فعال" if active else "غیرفعال","pct":str(pct),"pctclass":pct_class,"ringoffset":str(ring_offset),"used":escape_html(fmt_bytes(used)),"limit":escape_html(fmt_bytes(limit) if limit else "نامحدود"),"ip":str(ip_limit or 0),"conn":str(conn_limit or 0),"days":escape_html(days_text),"daysclass":days_class,"support":escape_html(support_url),"plan":escape_html(plan_badge) if plan_badge else ""}
    qr=quote(raw_url,safe="")
    html = r"""<!doctype html><html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#070b13"><meta name="color-scheme" content="dark"><title>__LABEL__ · VodiWalker</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#060910;--panel:#0c111a;--panel2:#101725;--line:rgba(255,255,255,.085);--muted:#8c98ab;--soft:#5f6b7e;--text:#f5f7fb;--accent:#8b5cf6;--cyan:#35d6ff;--green:#35d399;--shadow:0 30px 90px rgba(0,0,0,.34)}*{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--text);font-family:Vazirmatn,Inter,sans-serif;background:radial-gradient(circle at 15% -5%,rgba(139,92,246,.20),transparent 28%),radial-gradient(circle at 90% 8%,rgba(53,214,255,.11),transparent 23%),linear-gradient(180deg,#080c14,#05070c);overflow-x:hidden}body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.45;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(to bottom,#000,transparent 90%)}.wrap{position:relative;z-index:1;width:min(1180px,calc(100% - 28px));margin:auto;padding:24px 0 60px}.topbar{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:15px}.brand{display:flex;align-items:center;gap:11px}.mark{width:43px;height:43px;border-radius:14px;display:grid;place-items:center;font-size:18px;font-weight:900;background:linear-gradient(145deg,#17142b,#0d1726);border:1px solid rgba(139,92,246,.32);box-shadow:0 0 35px rgba(139,92,246,.14),inset 0 0 25px rgba(139,92,246,.08);animation:markGlow 3.2s ease-in-out infinite}@keyframes markGlow{0%,100%{box-shadow:0 0 35px rgba(139,92,246,.14),inset 0 0 25px rgba(139,92,246,.08)}50%{box-shadow:0 0 46px rgba(139,92,246,.26),inset 0 0 30px rgba(139,92,246,.14)}}.brand b{display:block;font-size:14px}.brand small{display:block;color:var(--soft);font-size:8px;letter-spacing:.13em;margin-top:2px}.live{display:flex;align-items:center;gap:7px;padding:8px 11px;border:1px solid rgba(53,211,153,.24);background:rgba(53,211,153,.07);border-radius:999px;color:#7eeac0;font-size:9px;font-weight:800}.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 12px rgba(53,211,153,.9)}.hero{position:relative;overflow:hidden;border:1px solid var(--line);border-radius:28px;padding:28px;background:linear-gradient(135deg,rgba(16,23,35,.94),rgba(8,12,19,.90));box-shadow:var(--shadow);margin-bottom:13px}.hero:after{content:"";position:absolute;width:340px;height:340px;left:-160px;top:-230px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,.28),transparent 66%)}.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:25px;align-items:center}.eyebrow{font-size:9px;color:#8f9bae;letter-spacing:.16em;font-weight:900}.hero h1{margin:9px 0 7px;font-size:clamp(27px,5vw,48px);line-height:1.08;letter-spacing:-.04em}.hero p{margin:0;max-width:720px;color:var(--muted);font-size:11px;line-height:2}.chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:15px}.chip{padding:7px 9px;border-radius:10px;border:1px solid var(--line);background:rgba(255,255,255,.035);font-size:9px;color:#bac4d1}.chip b{color:#fff}.hero-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.btn{border:0;text-decoration:none;cursor:pointer;color:#fff;padding:10px 13px;border-radius:11px;background:linear-gradient(135deg,#8b5cf6,#4d7cff);font:800 10px Vazirmatn;box-shadow:0 12px 28px rgba(76,91,255,.18);transition:transform .15s ease,box-shadow .15s ease}.btn:hover{transform:translateY(-1px);box-shadow:0 16px 36px rgba(76,91,255,.3)}.btn.alt{background:#121a28;border:1px solid var(--line);box-shadow:none;color:#dfe6ef}.btn.alt:hover{border-color:rgba(139,92,246,.4);background:#16202f}.qrbox{padding:13px;border:1px solid var(--line);border-radius:21px;background:rgba(0,0,0,.18);text-align:center;transition:transform .2s ease}.qrbox:hover{transform:translateY(-2px)}.qrbox img{width:170px;height:170px;padding:8px;background:#fff;border-radius:14px}.qrbox small{display:block;color:var(--soft);font-size:8px;margin-top:7px}.grid{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(300px,.55fr);gap:13px}.panel{border:1px solid var(--line);border-radius:22px;background:rgba(12,17,26,.86);overflow:hidden;box-shadow:0 18px 60px rgba(0,0,0,.18)}.head{display:flex;align-items:center;justify-content:space-between;padding:15px 17px;border-bottom:1px solid var(--line)}.head b{font-size:11px}.head small{display:block;color:var(--soft);font-size:8px;margin-top:3px}.body{padding:16px}.usage{display:grid;grid-template-columns:1fr 100px;gap:18px;align-items:center}.usage-label{color:var(--soft);font-size:8px}.usage-number{font-size:24px;font-weight:900;margin-top:3px}.progress{height:9px;background:#182130;border-radius:99px;overflow:hidden;margin:13px 0 8px}.progress i{display:block;height:100%;width:__PCT__%;background:linear-gradient(90deg,var(--accent),var(--cyan));box-shadow:0 0 20px rgba(53,214,255,.18)}.progress i.warn{background:linear-gradient(90deg,#f5a524,#f59e0b);box-shadow:0 0 20px rgba(245,165,36,.2)}.progress i.crit{background:linear-gradient(90deg,#f24955,#ef4444);box-shadow:0 0 20px rgba(242,73,85,.22)}.usage-note{color:var(--soft);font-size:8px}.badge-days{display:inline-flex;padding:2px 8px;border-radius:99px;font-size:8px;font-weight:800;background:rgba(255,255,255,.06);color:var(--muted);margin-right:6px}.badge-days.warn{background:rgba(245,165,36,.15);color:#f5a524}.badge-days.crit{background:rgba(242,73,85,.15);color:#f24955}.ring{width:104px;height:104px;position:relative;margin:auto}.ring svg{width:100%;height:100%;transform:rotate(-90deg)}.ring-track{fill:none;stroke:#182130;stroke-width:9}.ring-bar{fill:none;stroke:url(#ringGrad);stroke-width:9;stroke-linecap:round;stroke-dasharray:263.89;transition:stroke-dashoffset .6s ease;filter:drop-shadow(0 0 6px rgba(53,214,255,.4))}.ring.warn .ring-bar{stroke:#f5a524;filter:drop-shadow(0 0 6px rgba(245,165,36,.38))}.ring.crit .ring-bar{stroke:#f24955;filter:drop-shadow(0 0 6px rgba(242,73,85,.38))}.ring-center{position:absolute;inset:0;display:grid;place-items:center;text-align:center}.ring-center strong{font-size:17px}.ring-center small{display:block;color:var(--soft);font-size:7px;margin-top:2px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}.stat{padding:11px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.018)}.stat small{display:block;color:var(--soft);font-size:8px;margin-bottom:5px}.stat b{font-size:10px}.url{padding:12px;border-radius:13px;background:#080d15;border:1px solid var(--line);direction:ltr;text-align:left;word-break:break-all;color:#b8c7ff;font:9px/1.8 ui-monospace,Consolas,monospace}.copyrow{display:grid;grid-template-columns:1fr 90px;gap:7px;margin-top:8px}.mini-btn{padding:10px;border-radius:11px;border:1px solid var(--line);background:#111a28;color:#e5eaf2;font:800 9px Vazirmatn;cursor:pointer}.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.fact{padding:11px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.018)}.fact small{display:block;color:var(--soft);font-size:8px}.fact b{display:block;margin-top:5px;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.notice{margin-top:10px;padding:11px;border:1px solid rgba(53,214,255,.13);background:rgba(53,214,255,.045);border-radius:13px;color:#9cb0c6;font-size:8px;line-height:2}.apps{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.app{padding:10px;border:1px solid var(--line);border-radius:12px;background:#0d141f;display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;text-decoration:none;transition:transform .18s ease,border-color .18s ease}.app:hover{transform:translateY(-2px);border-color:rgba(139,92,246,.4)}.app-ico{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:14px}.app b{display:block;font-size:9px}.app small{color:var(--soft);font-size:7px}.brand b{background:linear-gradient(135deg,#fff,#c3b3ff);-webkit-background-clip:text;background-clip:text;color:transparent}.trust-row{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px}.trust-row span{display:flex;align-items:center;gap:6px;font-size:9px;color:var(--muted)}@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}.hero,.panel{animation:fadeUp .55s ease both;backdrop-filter:blur(16px);transition:box-shadow .25s ease,border-color .25s ease;contain:layout style paint}.panel:hover{border-color:rgba(139,92,246,.22);box-shadow:0 22px 70px rgba(0,0,0,.28)}.bg-orb{position:fixed;border-radius:50%;filter:blur(48px);pointer-events:none;z-index:0;will-change:transform;contain:strict;transform:translateZ(0)}.bg-orb1{width:360px;height:360px;top:-140px;left:-110px;background:#8b5cf6;opacity:.28;animation:orbFloat1 15s ease-in-out infinite}.bg-orb2{width:300px;height:300px;top:35%;right:-130px;background:#35d6ff;opacity:.16;animation:orbFloat2 19s ease-in-out infinite}.bg-orb3{width:240px;height:240px;bottom:-110px;left:28%;background:#35d399;opacity:.14;animation:orbFloat2 22s ease-in-out infinite reverse}@keyframes orbFloat1{0%,100%{transform:translate(0,0)}50%{transform:translate(35px,45px)}}@keyframes orbFloat2{0%,100%{transform:translate(0,0)}50%{transform:translate(-45px,-30px)}}.fact{position:relative;cursor:pointer;transition:.15s ease}.fact:hover{border-color:rgba(139,92,246,.4);background:rgba(139,92,246,.06)}.fact-copy{position:absolute;top:8px;left:8px;opacity:.4;font-size:9px}.trust-row span{padding:6px 10px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.03)}.footer{text-align:center;color:#4f5a6c;font-size:8px;padding-top:20px}.toast{position:fixed;z-index:9;left:50%;bottom:20px;transform:translate(-50%,18px);opacity:0;padding:10px 13px;border-radius:11px;background:#111a28;border:1px solid var(--line);box-shadow:0 20px 50px rgba(0,0,0,.35);font-size:9px;transition:.2s}.toast.show{opacity:1;transform:translate(-50%,0)}@media(max-width:850px){.hero-grid,.grid{grid-template-columns:1fr}.qrbox{max-width:230px}.stats{grid-template-columns:1fr 1fr}}@media(max-width:520px){.wrap{width:calc(100% - 18px);padding-top:12px}.hero{padding:20px;border-radius:22px}.usage{grid-template-columns:1fr}.ring{display:none}.stats,.info-grid,.apps{grid-template-columns:1fr 1fr}.copyrow{grid-template-columns:1fr}.hero-actions .btn{flex:1}}@media(prefers-reduced-motion:reduce){.mark,.bg-orb,.hero,.panel{animation:none!important}}@media(max-width:820px),(pointer:coarse){.bg-orb{animation:none!important;filter:blur(26px);opacity:.14}.hero,.panel{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}.hero{background:linear-gradient(135deg,rgba(20,28,44,.98),rgba(9,13,21,.98))}.panel{background:rgba(12,17,26,.98)}#qrModal{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}}
</style></head><body><svg width="0" height="0" style="position:absolute"><defs><linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#35d6ff"/></linearGradient></defs></svg><div class="bg-orb bg-orb1"></div><div class="bg-orb bg-orb2"></div><div class="bg-orb bg-orb3"></div><main class="wrap">
<div class="topbar"><div class="brand"><div class="mark">✦</div><div><b>VodiWalker</b><small>PREMIUM SUBSCRIPTION CENTER</small></div></div><div class="live"><span class="dot"></span><span id="status">__STATUS__</span></div></div>
<section class="hero"><div class="hero-grid"><div><div class="eyebrow">SECURE PERSONAL ACCESS</div><h1>__LABEL__</h1><p>مرکز مدیریت اختصاصی اشتراک شما؛ مصرف، ظرفیت، وضعیت سرویس و لینک اتصال در یک صفحه سریع و حرفه‌ای.</p><div class="chips"><span class="chip">پروتکل <b>__PROTOCOL__</b></span>__PLAN_CHIP__<span class="chip">IP Limit <b>__IP__</b></span><span class="chip">Connection <b>__CONN__</b></span><span class="chip">UUID <b dir="ltr">__UUID_SHORT__</b></span><span class="badge-days __DAYSCLASS__" id="daysBadge">__DAYS__</span></div><div class="trust-row"><span>🔒 رمزنگاری TLS/Reality</span><span>⚡ لتنسی پایین</span><span>🛡️ پایش امنیتی ۲۴/۷</span></div><div class="hero-actions"><button class="btn" onclick="copyText(__RAW_JS__)">کپی Subscription</button><a class="btn alt" href="__INFO__">مشاهده جزئیات</a><a class="btn alt" href="__SUPPORT__" target="_blank">پشتیبانی</a><button class="btn alt" onclick="shareLink()">اشتراک‌گذاری</button></div></div><div class="qrbox"><img src="https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=__QR__" alt="Subscription QR"><small>اسکن برای افزودن اشتراک</small></div></div></section>
<div class="grid"><section><div class="panel"><div class="head"><div><b>مصرف و ظرفیت</b><small>Live subscription telemetry</small></div><span id="updated" style="font-size:8px;color:var(--soft)">—</span></div><div class="body"><div class="usage"><div><div class="usage-label">مصرف فعلی</div><div class="usage-number" id="traffic">__USED__ / __LIMIT__</div><div class="progress"><i id="progress" class="__PCTCLASS__"></i></div><div class="usage-note">باقی‌مانده: <b id="remaining">__REMAINING__</b></div></div><div class="ring __PCTCLASS__" id="ringBox"><svg viewBox="0 0 100 100"><circle class="ring-track" cx="50" cy="50" r="42"></circle><circle class="ring-bar" id="ringBar" cx="50" cy="50" r="42" style="stroke-dashoffset:__RINGOFFSET__"></circle></svg><div class="ring-center"><strong id="pct">__PCT__%</strong><small>مصرف</small></div></div></div><div class="stats"><div class="stat"><small>وضعیت</small><b id="liveState">__STATUS__</b></div><div class="stat"><small>انقضا</small><b id="expiry">__EXPIRES__</b></div><div class="stat"><small>IP Limit</small><b>__IP__</b></div><div class="stat"><small>Connection</small><b>__CONN__</b></div></div></div></div><div class="panel" style="margin-top:13px"><div class="head"><div><b>لینک اشتراک</b><small>برای کلاینت‌های سازگار</small></div></div><div class="body"><div class="url" id="subUrl">__RAW__</div><div class="copyrow"><button class="mini-btn" onclick="copyText(__RAW_JS__)">کپی لینک</button><button class="mini-btn" onclick="downloadSub()">دریافت فایل</button></div><div class="notice">لینک Subscription را داخل کلاینت وارد کنید. آدرس عمومی با دامنه تنظیم‌شده پنل و شبکه Railway هماهنگ می‌ماند.</div></div></div></section>
<aside><div class="panel"><div class="head"><div><b>پروفایل اتصال</b><small>روی هر کارت بزن تا کپی بشه</small></div></div><div class="body"><div class="info-grid"><div class="fact" onclick="copyFact(this)"><small>Protocol</small><b dir="ltr">__PROTOCOL__</b><i class="fact-copy">⧉</i></div><div class="fact" onclick="copyFact(this)"><small>Network</small><b dir="ltr">__NETWORK__</b><i class="fact-copy">⧉</i></div><div class="fact" onclick="copyFact(this)"><small>Security</small><b dir="ltr">__SECURITY__</b><i class="fact-copy">⧉</i></div><div class="fact" onclick="copyFact(this)"><small>Address</small><b dir="ltr">__ADDRESS__</b><i class="fact-copy">⧉</i></div></div></div></div><div class="panel" style="margin-top:13px"><div class="head"><div><b>کلاینت‌های پیشنهادی</b><small>Import subscription in one step</small></div></div><div class="body"><div class="apps"><a class="app" href="https://github.com/2dust/v2rayNG/releases/latest" target="_blank"><div class="app-ico" style="background:rgba(34,197,139,.14);color:#22c58b">🤖</div><b>v2rayNG</b><small>Android</small></a><a class="app" href="https://github.com/2dust/v2rayN/releases/latest" target="_blank"><div class="app-ico" style="background:rgba(53,214,255,.14);color:#35d6ff">🖥️</div><b>v2rayN</b><small>Desktop</small></a><a class="app" href="https://github.com/hiddify/hiddify-app/releases/latest" target="_blank"><div class="app-ico" style="background:rgba(139,92,246,.14);color:#a997ff">🌐</div><b>Hiddify</b><small>Multi-platform</small></a></div></div></div></aside></div><div class="footer">VodiWalker · Premium Subscription Center · Live update enabled</div></main><div class="toast" id="toast">کپی شد ✓</div>
<script>const raw=__RAW_JS__;function toast(t,icon){const e=document.getElementById('toast');e.innerHTML=(icon||'✓')+' '+t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1700)}async function copyText(v){try{await navigator.clipboard.writeText(v);toast('کپی شد')}catch(e){const x=document.createElement('textarea');x.value=v;document.body.appendChild(x);x.select();document.execCommand('copy');x.remove();toast('کپی شد')}}function copyFact(el){const b=el.querySelector('b');if(b)copyText(b.textContent.trim())}async function shareLink(){if(navigator.share){try{await navigator.share({title:'VodiWalker Subscription',text:'اشتراک اختصاصی من',url:raw})}catch(e){}}else{copyText(raw)}}function downloadSub(){location.href=raw}function fmt(n){if(!n)return'0 B';const u=['B','KB','MB','GB','TB'];let i=0,x=Number(n)||0;while(x>=1024&&i<u.length-1){x/=1024;i++}return(x>=100?Math.round(x):x>=10?x.toFixed(1):x.toFixed(2))+' '+u[i]}function pctCls(p){return p>=90?'crit':(p>=70?'warn':'')}
const RING_CIRC=263.89;
async function refresh(){try{const r=await fetch('/api/subscription/__UUID__',{cache:'no-store'});if(!r.ok)return;const d=await r.json();const lim=Number(d.traffic_limit||0),used=Number(d.traffic_used||0),p=lim?Math.min(100,Math.round(used/lim*100)):0,cls=pctCls(p);document.getElementById('traffic').textContent=lim?fmt(used)+' / '+fmt(lim):fmt(used)+' / نامحدود';document.getElementById('remaining').textContent=lim?fmt(Math.max(0,lim-used)):'نامحدود';const pr=document.getElementById('progress');pr.style.width=p+'%';pr.className=cls;const rb=document.getElementById('ringBox');if(rb)rb.className='ring '+cls;const rBar=document.getElementById('ringBar');if(rBar)rBar.style.strokeDashoffset=(RING_CIRC*(1-p/100)).toFixed(2);document.getElementById('pct').textContent=p+'%';document.getElementById('liveState').textContent=d.active?'فعال':'غیرفعال';document.getElementById('status').textContent=d.active?'فعال':'غیرفعال';document.getElementById('updated').textContent='بروزرسانی '+new Date().toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}catch(e){}}refresh();setInterval(()=>{if(!document.hidden)refresh()},15000)</script></body></html>"""
    plan_chip = f'<span class="chip">پلن <b>{safe["plan"]}</b></span>' if safe["plan"] else ""
    replacements={"__LABEL__":safe["label"],"__STATUS__":safe["status"],"__PROTOCOL__":safe["protocol"],"__IP__":safe["ip"],"__CONN__":safe["conn"],"__UUID_SHORT__":escape_html(uuid[:18])+"…","__INFO__":safe["info"],"__RAW__":safe["raw"],"__RAW_JS__":repr(raw_url),"__QR__":qr,"__PCT__":safe["pct"],"__PCTCLASS__":safe["pctclass"],"__RINGOFFSET__":safe["ringoffset"],"__USED__":safe["used"],"__LIMIT__":safe["limit"],"__REMAINING__":safe["remaining"],"__EXPIRES__":safe["expires"],"__UUID__":escape_html(uuid),"__NETWORK__":escape_html(str(link.get("network") or "tcp")),"__SECURITY__":escape_html(str(link.get("security") or "none")),"__ADDRESS__":escape_html(str(link.get("address") or host)),"__DAYS__":safe["days"],"__DAYSCLASS__":safe["daysclass"],"__SUPPORT__":safe["support"],"__PLAN_CHIP__":plan_chip}
    for k,v in replacements.items(): html=html.replace(k,v)
    return HTMLResponse(html)


@app.get("/subscription/{uuid}", response_class=HTMLResponse)
async def subscription_portal(uuid: str, request: Request):
    return await render_subscription_portal(uuid, request)


@app.get("/api/subscription/{uuid}")
async def subscription_api(uuid: str):
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    if not is_link_allowed(link):
        raise HTTPException(status_code=404, detail="not found")
    used = int(link.get("used_bytes", 0) or 0)
    limit = int(link.get("limit_bytes", 0) or 0)
    return {
        "service": APP_NAME, "uuid": uuid, "label": link.get("label"),
        "active": bool(link.get("active", True)), "protocol": link.get("protocol"),
        "traffic_used": used, "traffic_limit": limit,
        "traffic_remaining": max(0, limit-used) if limit else None,
        "expires_at": link.get("expires_at"), "ip_limit": int(link.get("ip_limit", 0) or 0),
        "config_count": max(1, min(40, int(link.get("config_count") or 1))),
        "subscription": f"/sub/{uuid}", "portal": f"/subscription/{uuid}",
    }

# ============================================================
# SUB ALL
# ============================================================

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
    """صفحه‌ی اطلاعات تک‌کانفیگ. برای این‌که فقط یک نسخه‌ی حرفه‌ای و به‌روز
    نگه‌داری شود (به‌جای دو قالب متفاوت که به مرور از هم عقب می‌افتند)، این
    مسیر از همان پرتال کامل /subscription/{uuid} استفاده می‌کند."""
    async with LINKS_LOCK:
        exists = uid in LINKS
    if not exists:
        return HTMLResponse(
            "<html lang=\"fa\" dir=\"rtl\"><body style=\"margin:0;background:#070a10;color:#fff;font-family:sans-serif;padding:40px\"><h2>سرویس پیدا نشد</h2></body></html>",
            status_code=404,
        )
    return await render_subscription_portal(uid, request)

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

        if not verify_password(password, sub["password_hash"]):

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

            if not link:
                continue

            # رفع باگ: قبلاً لینک‌های منقضی/غیرفعال/تمام‌شده کاملاً از سابسکریپشن
            # حذف می‌شدند و کاربر بدون هیچ توضیحی می‌دید که کانفیگ وصل نمی‌شود.
            # حالا کانفیگ در لیست باقی می‌ماند ولی با ریمارک هشدار مشخص می‌شود؛
            # اتصال واقعی همچنان توسط is_link_allowed در لایه‌ی relay رد می‌شود.
            label = remark_with_status(str(link.get("label") or "Config"), link)
            lines.append(
                vless_link_for_link(
                    {**link, "label": label},
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
const key=location.pathname.split('/').pop();const qs=location.search||'';function esc(s){return String(s??'').replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[m]))}function toast(t){const e=document.getElementById('toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1600)}async function copy(v){try{await navigator.clipboard.writeText(v);toast('لینک کپی شد ✓')}catch(e){prompt('کپی کنید:',v)}}function fmt(n){if(!n)return'0 B';const u=['B','KB','MB','GB','TB'];let i=0,x=Number(n)||0;while(x>=1024&&i<u.length-1){x/=1024;i++}return(x>=100?Math.round(x):x>=10?x.toFixed(1):x.toFixed(2))+' '+u[i]}function render(d){if(d.locked){document.getElementById('app').innerHTML='<section class="panel locked"><div class="body"><div class="eyebrow">Protected subscription</div><h2>'+esc(d.name||'اشتراک')+'</h2><p style="color:var(--muted);font-size:11px;line-height:2">این اشتراک با رمز محافظت می‌شود. رمز را وارد کنید تا اطلاعات و لینک‌ها نمایش داده شوند.</p><form class="field" onsubmit="event.preventDefault();location.search=\'?pw=\'+encodeURIComponent(document.getElementById(\'pw\').value)"><input id="pw" type="password" placeholder="Subscription password"><button class="btn">ورود</button></form></div></section>';return}const links=d.links||[];const qr='https://api.qrserver.com/v1/create-qr-code/?size=220x220&data='+encodeURIComponent(d.sub_url||'');document.getElementById('app').innerHTML='<section class="hero"><div class="eyebrow">Subscription center</div><h1>'+esc(d.name||'Subscription')+'</h1><p>'+esc(d.desc||'مدیریت متمرکز کانفیگ‌ها و لینک اشتراک در یک صفحه حرفه‌ای.')+'</p><div class="stats"><div class="stat"><label>کانفیگ فعال</label><b>'+links.filter(x=>x.active).length+'</b></div><div class="stat"><label>اتصال فعال</label><b>'+Number(d.active_connections||0)+'</b></div><div class="stat"><label>مصرف کل</label><b>'+esc(d.total_used_fmt||'0 B')+'</b></div></div></section><section class="layout"><div class="panel"><div class="head"><div><b>کانفیگ‌های این اشتراک</b><small>وضعیت هر مسیر و مصرف آن</small></div><span style="color:var(--soft);font-size:9px">'+links.length+' مورد</span></div><div class="body">'+(links.length?links.map(l=>'<article class="link"><div class="linktop"><div><div class="linkname">'+esc(l.label||'Config')+'</div><div class="proto">'+esc(l.protocol||'VLESS')+'</div></div><span class="online '+(l.active?'':'offline')+'">'+(l.active?'فعال':(l.block_reason?('⚠️ '+l.block_reason):'غیرفعال'))+'</span></div><div class="linkmeta"><div class="mini"><small>مصرف</small><b>'+esc(l.used_fmt||'0 B')+' / '+esc(l.limit_fmt||'∞')+'</b></div><div class="mini"><small>اتصال</small><b>'+Number(l.connections||0)+' / '+(Number(l.connection_limit||0)||'∞')+'</b></div><div class="mini"><small>انقضا</small><b>'+esc((l.expires_at||'نامحدود').toString().slice(0,16))+'</b></div></div><div class="actions"><button class="btn" onclick="copy('+JSON.stringify(l.sub_url||'')+')">کپی ساب</button><a class="btn alt" href="'+esc(l.info_url||'#')+'">جزئیات</a></div></article>').join(''):'<div style="padding:35px;text-align:center;color:var(--soft);font-size:11px">کانفیگ فعالی برای این اشتراک وجود ندارد.</div>')+'</div></div><aside class="panel"><div class="head"><div><b>لینک اصلی اشتراک</b><small>مناسب برای کلاینت‌های سازگار</small></div></div><div class="body"><div class="qr"><img src="'+qr+'" alt="QR"></div><div class="url">'+esc(d.sub_url||'')+'</div><div class="actions"><button class="btn" onclick="copy('+JSON.stringify(d.sub_url||'')+')">کپی لینک</button><a class="btn alt" href="'+esc(d.sub_url||'#')+'">دریافت</a></div><div class="notice">برای استفاده، لینک بالا را در بخش Subscription کلاینت خود وارد کنید. لینک خام و API بدون تغییر باقی می‌مانند تا سازگاری حفظ شود.</div></div></aside></section>'}async function load(){try{const r=await fetch('/api/public/sub/'+encodeURIComponent(key)+qs,{cache:'no-store'});const d=await r.json();if(!r.ok)throw Error(d.detail||'خطا');render(d)}catch(e){document.getElementById('app').innerHTML='<section class="panel"><div class="body"><h2>اشتراک پیدا نشد</h2><p style="color:var(--muted)">لینک اشتراک منقضی شده، حذف شده یا در دسترس نیست.</p></div></section>'}}load();
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

        if not verify_password(password, sub["password_hash"]):

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

    active_connections = 0

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

        connection_count = sum(
            1
            for item in connections.values()
            if item.get("uuid") == link_id
        )

        active_connections += (
            connection_count
        )

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

                "block_reason":
                    link_block_reason(link),

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
            active_connections,

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

# PANEL SETTINGS (آدرس عمومی پنل + مدیریت ربات از داخل پنل)
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
