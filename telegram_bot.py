# telegram_bot.py
# ══════════════════════════════════════════════════════════════════════════════
# ربات مدیریت تلگرام — ساخت/حذف/فعال‌غیرفعال/مشاهده‌ی کانفیگ‌ها، فقط برای ادمین‌های
# مجاز (TELEGRAM_ADMIN_IDS). با long polling کار می‌کنه، نیازی به دامنه/webhook نداره.
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import os
import re

import httpx

from datetime import datetime, timedelta

from sales import PLANS, get_plan, create_payload, fulfill_payment, load_sales, user_orders, sales_stats

from main import (
    LINKS,
    make_link,
    remove_link,
    set_link_active,
    vless_link_for_link,
    get_host,
    fmt_bytes,
    is_link_allowed,
    logger,
    PROTOCOLS,
    DEFAULT_PROTOCOL,
    FINGERPRINTS,
    DEFAULT_FINGERPRINT,
    DEFAULT_ALPN_BY_PROTOCOL,
    DEFAULT_PORT,
    DEFAULT_SPEED_LIMIT,
    MIN_PORT,
    MAX_PORT,
    parse_size_to_bytes,
    parse_speed_to_bytes,
    SUBS,
    create_sub_group,
    set_link_sub,
    remove_sub_group,
    get_bot_text,
    add_client_to_inbound,
    remove_inbound_client,
)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
# فروش اشتراک فعلاً عمداً خاموش است؛ فقط مدیریت سرویس از ربات فعال می‌ماند.
SALES_ENABLED = os.environ.get("VODIWALKER_SALES_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on")
_admin_ids_raw = os.environ.get("TELEGRAM_ADMIN_IDS", "").strip()
ADMIN_IDS = {int(x) for x in _admin_ids_raw.replace(" ", "").split(",") if x.isdigit()} if _admin_ids_raw else set()

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def configure(token: str = None, admin_ids_raw: str = None):
    """توکن/آیدی‌ ادمین‌های ربات رو در زمان اجرا (مثلاً از تنظیمات پنل وب) تغییر می‌ده.
    اگر ربات در حال اجرا باشه، لازمه بعدش stop_bot() و start_bot() دوباره صدا زده بشه
    تا تغییرات اعمال بشه (این کار در روت /api/settings انجام می‌شه)."""
    global BOT_TOKEN, API_BASE, ADMIN_IDS
    if token is not None:
        BOT_TOKEN = (token or "").strip()
        API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
    if admin_ids_raw is not None:
        raw = (admin_ids_raw or "").strip()
        ADMIN_IDS = {int(x) for x in raw.replace(" ", "").split(",") if x.isdigit()} if raw else set()


def is_running() -> bool:
    return bool(_running)


def current_config() -> dict:
    return {
        "bot_token": BOT_TOKEN,
        "admin_ids": ",".join(str(x) for x in sorted(ADMIN_IDS)),
        "running": is_running(),
    }
PAGE_SIZE = 6

_client: httpx.AsyncClient | None = None
_poll_task: asyncio.Task | None = None
_running = False
_pending: dict = {}   # chat_id -> {"action": "wizard", "step": "...", "data": {...}}

# ── Config creation wizard ────────────────────────────────────────────────────
# مراحل ساخت کانفیگ جدید، دقیقاً هم‌راستا با فیلدهایی که پنل وب موقع ساخت کاربر می‌گیره:
# برچسب، پروتکل، fingerprint، ALPN، پورت، محدودیت حجم، محدودیت سرعت، محدودیت آی‌پی، روز انقضا.
WIZARD_STEPS = ["label", "protocol", "fingerprint", "alpn", "port", "volume", "speed", "iplimit", "days"]

PROTOCOL_LABELS = {
    "vless-ws": "VLESS + WebSocket",
    "xhttp-packet-up": "XHTTP (packet-up)",
    "xhttp-stream-up": "XHTTP (stream-up)",
    "xhttp-stream-one": "XHTTP (stream-one)",
}

def _protocol_label(p: str) -> str:
    return PROTOCOL_LABELS.get(p, p)

def _fp_label(fp: str) -> str:
    return fp.capitalize()

_VOLUME_RE = re.compile(r"^([\d.]+)\s*(GB|MB|KB)?$", re.IGNORECASE)
_SPEED_RE = re.compile(r"^([\d.]+)\s*(MBIT|MBPS|MB|KB)?$", re.IGNORECASE)

def _parse_volume_text(text: str):
    """ورودی مثل '10GB' یا '500 MB' رو به بایت تبدیل می‌کنه. اگه نامعتبر بود None برمی‌گردونه."""
    m = _VOLUME_RE.match(text.strip())
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    if value <= 0:
        return 0
    unit = (m.group(2) or "GB").upper()
    return parse_size_to_bytes(value, unit)

def _parse_speed_text(text: str):
    """ورودی مثل '20' یا '20Mbit' رو به بایت‌بر‌ثانیه تبدیل می‌کنه (پیش‌فرض واحد Mbit)."""
    m = _SPEED_RE.match(text.strip())
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    if value <= 0:
        return 0
    unit_raw = (m.group(2) or "MBIT").upper()
    unit = "MBIT" if unit_raw in ("MBIT", "MBPS") else unit_raw
    return parse_speed_to_bytes(value, unit)

def _parse_nonneg_int(text: str):
    try:
        n = int(text.strip())
    except ValueError:
        return None
    return max(0, n)

# ── Telegram API helpers ────────────────────────────────────────────────────
async def _call(method: str, **params):
    if _client is None:
        return None
    try:
        r = await _client.post(f"{API_BASE}/{method}", json=params, timeout=40)
        data = r.json()
        if not data.get("ok"):
            logger.warning(f"Telegram API {method} failed: {data}")
        return data
    except Exception as e:
        logger.warning(f"Telegram API {method} error: {e}")
        return None

async def _send(chat_id: int, text: str, kb: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if kb:
        payload["reply_markup"] = kb
    return await _call("sendMessage", **payload)

async def _edit(chat_id: int, message_id: int, text: str, kb: dict | None = None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if kb:
        payload["reply_markup"] = kb
    res = await _call("editMessageText", **payload)
    if res is None or not res.get("ok"):
        # اگه ادیت به هر دلیلی نشد (مثلاً پیام قدیمی/حذف‌شده)، پیام جدید بفرست
        await _send(chat_id, text, kb)

async def _answer_cb(cb_id: str, text: str = ""):
    await _call("answerCallbackQuery", callback_query_id=cb_id, text=text)

def _is_admin(chat_id: int) -> bool:
    return chat_id in ADMIN_IDS

# ── Keyboards ────────────────────────────────────────────────────────────────
def _main_menu_kb():
    rows = [
        [{"text": "📊 داشبورد زنده", "callback_data": "stats"}],
        [{"text": "📋 اینباندها و کانفیگ‌ها", "callback_data": "list:0"}, {"text": "➕ ساخت اینباند", "callback_data": "newcfg"}],
        [{"text": "👥 کلاینت‌ها", "callback_data": "list:0"}, {"text": "🗂 سابسکریپشن‌ها", "callback_data": "subs:0"}],
    ]
    if SALES_ENABLED:
        rows.append([{ "text": "🛒 فروشگاه و پلن‌ها", "callback_data": "store" }])
    rows.append([{ "text": "⚙️ وضعیت مدیریت", "callback_data": "menu" }])
    return {"inline_keyboard": rows}

def _links_list_kb(page: int):
    items = sorted(LINKS.items(), key=lambda kv: kv[1].get("created_at", ""), reverse=True)
    total = len(items)
    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]
    rows = []
    for uid, l in chunk:
        dot = "🟢" if is_link_allowed(l) else "🔴"
        rows.append([{"text": f"{dot} {l.get('label','?')[:28]}", "callback_data": f"view:{uid}"}])
    nav = []
    if start > 0:
        nav.append({"text": "◀ قبلی", "callback_data": f"list:{page-1}"})
    if start + PAGE_SIZE < total:
        nav.append({"text": "بعدی ▶", "callback_data": f"list:{page+1}"})
    if nav:
        rows.append(nav)
    rows.append([{"text": "➕ ساخت کانفیگ جدید", "callback_data": "newcfg"}])
    rows.append([{"text": "⬅ منوی اصلی", "callback_data": "menu"}])
    return {"inline_keyboard": rows}

def _link_detail_kb(uid: str, active: bool):
    return {"inline_keyboard": [
        [{"text": "🔗 نمایش لینک اتصال", "callback_data": f"link:{uid}"}],
        [{"text": "👥 کاربران این اینباند", "callback_data": f"clients:{uid}:0"}],
        [{"text": "🗂 گروه ساب (لینک حرفه‌ای)", "callback_data": f"cfggroup:{uid}"}],
        [{"text": ("⛔ غیرفعال‌سازی" if active else "✅ فعال‌سازی"), "callback_data": f"toggle:{uid}"}],
        [{"text": "🗑 حذف کانفیگ", "callback_data": f"del:{uid}"}],
        [{"text": "⬅ بازگشت به لیست", "callback_data": "list:0"}],
    ]}

# ── Client (user) management under an inbound ────────────────────────────────
def _clients_list_kb(parent_uid: str, page: int = 0):
    children = [(cid, l) for cid, l in LINKS.items() if l.get("parent_inbound_id") == parent_uid]
    children.sort(key=lambda kv: kv[1].get("created_at", ""), reverse=True)
    total = len(children)
    start = page * PAGE_SIZE
    chunk = children[start:start + PAGE_SIZE]
    rows = []
    for cid, l in chunk:
        dot = "🟢" if is_link_allowed(l) else "🔴"
        rows.append([
            {"text": f"{dot} {l.get('label','?')[:24]}", "callback_data": f"view:{cid}"},
            {"text": "🗑", "callback_data": f"delclient:{parent_uid}:{cid}"},
        ])
    nav = []
    if start > 0:
        nav.append({"text": "◀ قبلی", "callback_data": f"clients:{parent_uid}:{page-1}"})
    if start + PAGE_SIZE < total:
        nav.append({"text": "بعدی ▶", "callback_data": f"clients:{parent_uid}:{page+1}"})
    if nav:
        rows.append(nav)
    rows.append([{"text": "➕ افزودن کاربر جدید", "callback_data": f"addclient:{parent_uid}"}])
    rows.append([{"text": "⬅ بازگشت به اینباند", "callback_data": f"view:{parent_uid}"}])
    return {"inline_keyboard": rows}

def _format_clients_list(parent_uid: str) -> str:
    parent = LINKS.get(parent_uid)
    children = [l for l in LINKS.values() if l.get("parent_inbound_id") == parent_uid]
    lines = [f"👥 <b>کاربران اینباند «{parent.get('label','?') if parent else '؟'}»</b>", f"تعداد کاربر: {len(children)}"]
    limit = int((parent or {}).get("client_limit") or 0)
    if limit:
        lines.append(f"ظرفیت مجاز: {limit}")
    if not children:
        lines.append("\nهنوز کاربری اضافه نشده. با دکمه‌ی زیر یک کاربر جدید بساز.")
    return "\n".join(lines)

def _confirm_delete_client_kb(parent_uid: str, client_id: str):
    return {"inline_keyboard": [
        [{"text": "✅ بله، حذف کن", "callback_data": f"delclientok:{parent_uid}:{client_id}"},
         {"text": "❌ انصراف", "callback_data": f"clients:{parent_uid}:0"}],
    ]}

def _wizard_client_prompt(step: str, data: dict) -> str:
    if step == "label":
        return "👤 نام/برچسب کاربر جدید رو بفرست:"
    if step == "volume":
        return "📦 سقف حجم این کاربر رو بفرست (مثل <code>10GB</code> یا <code>500MB</code>)، یا برای ارث‌بری از اینباند دکمه زیر رو بزن:"
    if step == "days":
        return "📅 چند روز اعتبار داشته باشه؟ یه عدد بفرست، یا برای ارث‌بری از انقضای اینباند دکمه زیر رو بزن:"
    if step == "confirm":
        limit_txt = fmt_bytes(data["limit_bytes"]) if data.get("limit_bytes") else "ارث‌بری از اینباند"
        days_txt = f"{data['expires_days']} روز" if data.get("expires_days") else "ارث‌بری از اینباند"
        return (f"📋 <b>پیش‌نمایش کاربر جدید</b>\n\n"
                f"برچسب: {data.get('label')}\n"
                f"حجم: {limit_txt}\n"
                f"انقضا: {days_txt}\n\n"
                f"تایید می‌کنی؟")
    return ""

def _wizard_client_cancel_kb():
    return {"inline_keyboard": [[{"text": "❌ انصراف", "callback_data": "wc:cancel"}]]}

def _wizard_client_skip_kb(step_key: str, label: str):
    return {"inline_keyboard": [
        [{"text": label, "callback_data": f"wc:skip:{step_key}"}],
        [{"text": "❌ انصراف", "callback_data": "wc:cancel"}],
    ]}

def _wizard_client_confirm_kb():
    return {"inline_keyboard": [
        [{"text": "✅ ساخت کاربر", "callback_data": "wc:confirm"}],
        [{"text": "❌ انصراف", "callback_data": "wc:cancel"}],
    ]}

def _confirm_delete_kb(uid: str):
    return {"inline_keyboard": [
        [{"text": "✅ بله، حذف کن", "callback_data": f"delok:{uid}"},
         {"text": "❌ انصراف", "callback_data": f"view:{uid}"}],
    ]}

# ── Wizard keyboards ─────────────────────────────────────────────────────────
def _wizard_cancel_kb():
    return {"inline_keyboard": [[{"text": "❌ انصراف", "callback_data": "w:cancel"}]]}

def _wizard_protocol_kb():
    rows = [[{"text": _protocol_label(p), "callback_data": f"w:proto:{p}"}] for p in PROTOCOLS]
    rows.append([{"text": "❌ انصراف", "callback_data": "w:cancel"}])
    return {"inline_keyboard": rows}

def _wizard_fp_kb():
    rows, row = [], []
    for fp in FINGERPRINTS:
        row.append({"text": _fp_label(fp), "callback_data": f"w:fp:{fp}"})
        if len(row) == 3:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([{"text": "❌ انصراف", "callback_data": "w:cancel"}])
    return {"inline_keyboard": rows}

def _wizard_skip_kb(step_key: str, label: str):
    return {"inline_keyboard": [
        [{"text": label, "callback_data": f"w:skip:{step_key}"}],
        [{"text": "❌ انصراف", "callback_data": "w:cancel"}],
    ]}

ALPN_PRESET_MAP = {"p1": "http/1.1", "p2": "h2,http/1.1", "p3": "h2"}

def _wizard_alpn_kb():
    return {"inline_keyboard": [
        [{"text": "🔤 http/1.1 (پیشنهادی)", "callback_data": "w:alpnpreset:p1"}],
        [{"text": "🔤 h2,http/1.1", "callback_data": "w:alpnpreset:p2"}],
        [{"text": "🔤 h2", "callback_data": "w:alpnpreset:p3"}],
        [{"text": "⏭ پیش‌فرض پروتکل", "callback_data": "w:skip:alpn"}],
        [{"text": "❌ انصراف", "callback_data": "w:cancel"}],
    ]}

def _wizard_unlimited_kb(step_key: str):
    return _wizard_skip_kb(step_key, "♾ نامحدود")

def _wizard_confirm_kb():
    return {"inline_keyboard": [
        [{"text": "✅ ساخت کانفیگ", "callback_data": "w:confirm"}],
        [{"text": "❌ انصراف", "callback_data": "w:cancel"}],
    ]}

def _wizard_prompt(step: str, data: dict) -> str:
    n = WIZARD_STEPS.index(step) + 1 if step in WIZARD_STEPS else len(WIZARD_STEPS)
    head = f"🧩 ساخت کانفیگ جدید — مرحله {n}/{len(WIZARD_STEPS)}\n\n"
    if step == "label":
        return head + "✏️ اسم/برچسب کانفیگ رو بفرست:"
    if step == "protocol":
        return head + "🌐 پروتکل رو از دکمه‌های زیر انتخاب کن:"
    if step == "fingerprint":
        return head + "🖐 Fingerprint (uTLS) رو انتخاب کن:"
    if step == "alpn":
        return head + ("🔤 ALPN رو از دکمه‌های زیر انتخاب کن (پیشنهادی: <code>http/1.1</code>)\n"
                        "یا خودت هر مقدار دلخواهی رو تایپ و ارسال کن (مثلاً h2,http/1.1):")
    if step == "port":
        return head + f"🔌 شماره پورت (بین {MIN_PORT} تا {MAX_PORT}) رو بفرست\nیا پیش‌فرض ({DEFAULT_PORT}) رو انتخاب کن:"
    if step == "volume":
        return head + "📦 محدودیت حجم مصرفی رو بفرست، مثلاً:\n<code>10GB</code> یا <code>500MB</code>\nیا دکمه‌ی نامحدود رو بزن:"
    if step == "speed":
        return head + "🚀 محدودیت سرعت رو به مگابیت‌بر‌ثانیه بفرست، مثلاً <code>20</code>\nیا دکمه‌ی نامحدود رو بزن:"
    if step == "iplimit":
        return head + "👥 حداکثر تعداد آی‌پی/کاربر هم‌زمان مجاز رو بفرست\nیا دکمه‌ی نامحدود رو بزن:"
    if step == "days":
        return head + "📅 تعداد روزهای اعتبار کانفیگ رو بفرست\nیا دکمه‌ی نامحدود (بدون انقضا) رو بزن:"
    return head

def _wizard_summary(data: dict) -> str:
    limit = "نامحدود" if not data.get("limit_bytes") else fmt_bytes(data["limit_bytes"])
    speed = "نامحدود" if not data.get("speed_limit_bytes") else f"{data['speed_limit_bytes']*8/1024/1024:.1f} Mbps"
    iplim = data.get("ip_limit", 0) or "نامحدود"
    days = data.get("expires_days", 0)
    days_txt = "بدون انقضا" if not days else f"{days} روز"
    proto = data.get("protocol", DEFAULT_PROTOCOL)
    alpn = data.get("alpn") or f"پیش‌فرض ({DEFAULT_ALPN_BY_PROTOCOL.get(proto, 'http/1.1')})"
    return (
        "🧩 خلاصه‌ی کانفیگ جدید — تایید کن:\n\n"
        f"برچسب: <b>{data.get('label','?')}</b>\n"
        f"پروتکل: {_protocol_label(proto)}\n"
        f"Fingerprint: {_fp_label(data.get('fingerprint', DEFAULT_FINGERPRINT))}\n"
        f"ALPN: {alpn}\n"
        f"پورت: {data.get('port', DEFAULT_PORT)}\n"
        f"محدودیت حجم: {limit}\n"
        f"محدودیت سرعت: {speed}\n"
        f"محدودیت آی‌پی: {iplim}\n"
        f"انقضا: {days_txt}"
    )

# ── View builders ────────────────────────────────────────────────────────────
def _format_detail(uid: str, l: dict) -> str:
    status = "🟢 فعال" if is_link_allowed(l) else "🔴 غیرفعال/منقضی"
    limit_bytes = l.get("limit_bytes") or 0
    used_bytes = l.get("used_bytes", 0)
    limit = "نامحدود" if not limit_bytes else fmt_bytes(limit_bytes)
    speed = "نامحدود" if not l.get("speed_limit_bytes") else f"{l['speed_limit_bytes']*8/1024/1024:.1f} Mbps"
    exp = l.get("expires_at")
    exp_txt = exp.split("T")[0] if exp else "بدون انقضا"
    proto = l.get("protocol", DEFAULT_PROTOCOL)
    alpn = l.get("alpn") or f"پیش‌فرض ({DEFAULT_ALPN_BY_PROTOCOL.get(proto, 'http/1.1')})"
    usage_line = f"مصرف: {fmt_bytes(used_bytes)} / {limit}"
    if limit_bytes:
        pct = min(100, round((used_bytes / limit_bytes) * 100, 1))
        usage_line += f"\n{_progress_bar(pct)}  {pct}%"
    return (
        f"<b>{l.get('label','?')}</b>\n"
        f"وضعیت: {status}\n"
        f"{usage_line}\n"
        f"محدودیت سرعت: {speed}\n"
        f"محدودیت آی‌پی: {l.get('ip_limit',0) or 'نامحدود'}\n"
        f"پروتکل: {_protocol_label(proto)}\n"
        f"Fingerprint: {_fp_label(l.get('fingerprint', DEFAULT_FINGERPRINT))}\n"
        f"ALPN: {alpn}\n"
        f"پورت: {l.get('port', DEFAULT_PORT)}\n"
        f"انقضا: {exp_txt}\n"
        f"UUID: <code>{uid}</code>"
    )

# ── Sub-group (لینک ساب حرفه‌ای) view builders ────────────────────────────────
def _group_public_url(s: dict) -> str:
    host = get_host()
    return f"https://{host}/p/{s.get('uuid_key','')}"

def _subs_list_kb(page: int):
    items = sorted(SUBS.items(), key=lambda kv: kv[1].get("created_at", ""), reverse=True)
    total = len(items)
    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]
    rows = []
    for sid, s in chunk:
        cnt = len(s.get("link_ids", []))
        rows.append([{"text": f"🗂 {s.get('name','?')[:26]} ({cnt})", "callback_data": f"subview:{sid}"}])
    nav = []
    if start > 0:
        nav.append({"text": "◀ قبلی", "callback_data": f"subs:{page-1}"})
    if start + PAGE_SIZE < total:
        nav.append({"text": "بعدی ▶", "callback_data": f"subs:{page+1}"})
    if nav:
        rows.append(nav)
    rows.append([{"text": "➕ ساخت گروه جدید", "callback_data": "newsub"}])
    rows.append([{"text": "⬅ منوی اصلی", "callback_data": "menu"}])
    return {"inline_keyboard": rows}

def _format_sub_detail(sid: str, s: dict) -> str:
    cnt = len(s.get("link_ids", []))
    pw = "🔒 دارد" if s.get("password_hash") else "بدون رمز"
    desc = s.get("desc") or "—"
    return (
        f"🗂 <b>{s.get('name','?')}</b>\n"
        f"توضیحات: {desc}\n"
        f"تعداد کانفیگ‌های داخل گروه: {cnt}\n"
        f"رمز عبور: {pw}\n\n"
        f"🔗 لینک ساب حرفه‌ای این گروه:\n<code>{_group_public_url(s)}</code>"
    )

def _sub_detail_kb(sid: str):
    return {"inline_keyboard": [
        [{"text": "➕ افزودن کانفیگ به این گروه", "callback_data": f"subaddlink:{sid}:0"}],
        [{"text": "🗑 حذف گروه", "callback_data": f"subdel:{sid}"}],
        [{"text": "⬅ بازگشت به لیست گروه‌ها", "callback_data": "subs:0"}],
    ]}

def _confirm_subdel_kb(sid: str):
    return {"inline_keyboard": [
        [{"text": "✅ بله، حذف کن", "callback_data": f"subdelok:{sid}"},
         {"text": "❌ انصراف", "callback_data": f"subview:{sid}"}],
    ]}

def _pick_link_for_group_kb(sid: str, page: int):
    """لیست همه‌ی کانفیگ‌ها برای انتخاب و افزودن به یک گروه ساب مشخص."""
    items = sorted(LINKS.items(), key=lambda kv: kv[1].get("created_at", ""), reverse=True)
    total = len(items)
    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]
    rows = []
    for uid, l in chunk:
        in_this = "✅ " if l.get("sub_id") == sid else ""
        rows.append([{"text": f"{in_this}{l.get('label','?')[:28]}", "callback_data": f"subaddlinkdo:{uid}"}])
    nav = []
    if start > 0:
        nav.append({"text": "◀ قبلی", "callback_data": f"subaddlink:{sid}:{page-1}"})
    if start + PAGE_SIZE < total:
        nav.append({"text": "بعدی ▶", "callback_data": f"subaddlink:{sid}:{page+1}"})
    if nav:
        rows.append(nav)
    rows.append([{"text": "⬅ بازگشت به گروه", "callback_data": f"subview:{sid}"}])
    return {"inline_keyboard": rows}

# ── Per-config "group" (ساب لینک حرفه‌ای) view builders ───────────────────────
def _cfg_group_kb(uid: str):
    link = LINKS.get(uid, {})
    sid = link.get("sub_id")
    if sid and sid in SUBS:
        return {"inline_keyboard": [
            [{"text": "➖ خارج کردن از گروه", "callback_data": f"cfgungroup:{uid}"}],
            [{"text": "⬅ بازگشت", "callback_data": f"view:{uid}"}],
        ]}
    rows = []
    for sid2, s in sorted(SUBS.items(), key=lambda kv: kv[1].get("created_at", ""), reverse=True)[:8]:
        rows.append([{"text": f"➕ افزودن به «{s.get('name','?')[:24]}»", "callback_data": f"cfgaddgroup:{sid2}"}])
    rows.append([{"text": "🆕 ساخت گروه جدید و افزودن", "callback_data": f"cfgnewgroup:{uid}"}])
    rows.append([{"text": "⬅ بازگشت", "callback_data": f"view:{uid}"}])
    return {"inline_keyboard": rows}

def _format_cfg_group(uid: str) -> str:
    link = LINKS.get(uid, {})
    sid = link.get("sub_id")
    if sid and sid in SUBS:
        s = SUBS[sid]
        return (
            f"🗂 کانفیگ «{link.get('label','?')}» توی گروه «{s.get('name','?')}» هست.\n\n"
            f"🔗 لینک ساب حرفه‌ای این گروه:\n<code>{_group_public_url(s)}</code>"
        )
    return (
        f"کانفیگ «{link.get('label','?')}» توی هیچ گروهی نیست، یعنی فقط لینک ساب ساده داره.\n\n"
        "برای گرفتن لینک ساب حرفه‌ای (صفحه‌ی زیبا)، این کانفیگ رو به یک گروه اضافه کن یا یه گروه جدید بساز:"
    )

# ── Update handling ──────────────────────────────────────────────────────────

def _progress_bar(pct: float, width: int = 10) -> str:
    pct = max(0, min(100, pct))
    filled = round((pct / 100) * width)
    return "█" * filled + "░" * (width - filled)

def _plan_emoji(idx: int) -> str:
    return ["⚡", "🚀", "👑", "💎", "🔥", "🌟"][idx % 6]

def _store_kb():
    rows=[]
    for pid,p in PLANS.items():
        badge = f" ({p['badge']})" if p.get("featured") else ""
        rows.append([{"text": f"🛒 {p['name']}{badge} — {p['stars']} ⭐", "callback_data": f"buy:{pid}"}])
    rows.append([{"text":"🧾 خریدهای من","callback_data":"myorders"}])
    return {"inline_keyboard":rows}

def _store_text():
    plans = sorted(PLANS.values(), key=lambda p: p.get("order", 0))
    lines = ["🛍 <b>VodiWalker Store</b>",
              "",
              "پلن موردنظر رو انتخاب کن؛ بعد از پرداخت، کانفیگ اختصاصی خودت به‌صورت خودکار ساخته و همون‌جا تحویل داده می‌شه.",
              ""]
    for i, p in enumerate(plans):
        star = "⭐️ " + p.get("badge", "") if p.get("featured") else ""
        lines.append(
            f"{_plan_emoji(i)} <b>{p['name']}</b> {star}\n"
            f"  📅 {p['days']} روز  ·  📦 {p['volume_gb']}GB  ·  🚀 {p['speed_mbps']}Mbps  ·  👥 {p['ip_limit']} IP\n"
            f"  💳 {p['stars']} ⭐️ Stars"
        )
    lines.append("")
    lines.append("برای مشاهده‌ی خریدهای قبلی از دکمه‌ی «🧾 خریدهای من» استفاده کن.")
    return "\n".join(lines)

async def _send_invoice(chat_id, plan_id):
    plan=get_plan(plan_id)
    if not plan: return
    payload=create_payload(plan_id, chat_id)
    await _call("sendInvoice",
        chat_id=chat_id,
        title=f"VodiWalker {plan['name']}",
        description=f"اشتراک {plan['days']} روزه | {plan['volume_gb']}GB | تا {plan['speed_mbps']}Mbps",
        payload=payload,
        provider_token=os.environ.get("TELEGRAM_PAYMENT_PROVIDER_TOKEN",""),
        currency=os.environ.get("TELEGRAM_PAYMENT_CURRENCY","XTR"),
        prices=[{"label":f"VodiWalker {plan['name']}","amount":int(plan["stars"])}],
        start_parameter=f"buy_{plan_id}",
        need_name=False,
        need_phone_number=False,
        need_email=False,
        is_flexible=False,
    )

async def _handle_precheckout(q):
    qid=q.get("id")
    payload=str(q.get("invoice_payload",""))
    ok=payload.startswith("vw|")
    await _call("answerPreCheckoutQuery", pre_checkout_query_id=qid, ok=ok,
                error_message=None if ok else "سفارش نامعتبر است.")

async def _handle_successful_payment(msg):
    sp=msg.get("successful_payment") or {}
    payload=str(sp.get("invoice_payload",""))
    parts=payload.split("|")
    if len(parts)<4 or parts[0]!="vw":
        return
    plan_id=parts[1]
    try:
        order,link,uid,sub_url=await fulfill_payment(msg.get("from") or msg.get("chat") or {}, plan_id, sp.get("telegram_payment_charge_id",""))
        text=(f"✅ <b>پرداخت موفق بود!</b>\n\n"
              f"پلن: <b>{PLANS[plan_id]['name']}</b>\n"
              f"اعتبار: {PLANS[plan_id]['days']} روز\n"
              f"حجم: {PLANS[plan_id]['volume_gb']}GB\n"
              f"سرعت: {PLANS[plan_id]['speed_mbps']}Mbps\n\n"
              f"🔗 <b>لینک سابسکریپشن:</b>\n<code>{sub_url}</code>\n\n"
              "لینک را داخل کلاینت خود وارد کن. این لینک اختصاصی شماست.")
        await _send(msg["chat"]["id"],text,{"inline_keyboard":[
            [{"text":"📋 خریدهای من","callback_data":"myorders"}],
            [{"text":"🛒 خرید اشتراک جدید","callback_data":"store"}]
        ]})
    except Exception as exc:
        await _send(msg["chat"]["id"],"⚠️ پرداخت ثبت شد اما ساخت اشتراک با خطا مواجه شد. لطفاً با پشتیبانی تماس بگیرید.")
        logger.exception("sales fulfillment failed: %s", exc)

def _admin_welcome_text(base: str) -> str:
    total = len(LINKS)
    active = sum(1 for l in LINKS.values() if is_link_allowed(l))
    return f"{base}\n\n🌐 {total} کانفیگ ({active} فعال) · 🗂 {len(SUBS)} گروه ساب"

async def _handle_message(msg: dict):
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()
    if chat_id is None:
        return
    # فروشگاه برای همه کاربران فعال است؛ بخش مدیریت فقط برای ادمین‌هاست.
    if text.startswith("/start"):
        arg=text.split(maxsplit=1)[1] if len(text.split(maxsplit=1))>1 else ""
        if SALES_ENABLED and arg.startswith("buy_") and get_plan(arg[4:]):
            await _send_invoice(chat_id,arg[4:])
            return
        if _is_admin(chat_id):
            _pending.pop(chat_id, None)
            await _send(chat_id, _admin_welcome_text(get_bot_text("welcome", "👋 <b>VodiWalker Control Center</b>\nمدیریت کامل سرویس و فروشگاه:")), _main_menu_kb())
        else:
            await _send(chat_id, "🔒 <b>VodiWalker</b>\n\nفروش اشتراک در حال حاضر غیرفعال است و در نسخه‌های بعدی فعال می‌شود.")
        return

    if text in ("/plans", "/shop", "/store"):
        if not SALES_ENABLED:
            await _send(chat_id, "🔒 فروش اشتراک فعلاً غیرفعال است.\n\nاین ماژول در نسخه‌های بعدی VodiWalker فعال خواهد شد.")
        else:
            await _send(chat_id, _store_text(), _store_kb())
        return

    if text == "/my":
        orders=user_orders(chat_id)
        if not orders:
            await _send(chat_id,"🧾 هنوز خریدی ثبت نشده.",_store_kb()); return
        lines=["🧾 <b>خریدهای اخیر شما</b>\n"]
        for o in orders:
            lines.append(f"• {PLANS.get(o['plan_id'],{}).get('name',o['plan_id'])} — {o.get('created_at','')[:16]}\n  <code>https://{get_host()}/subscription/{o['link_uid']}</code>")
        await _send(chat_id,"\n".join(lines),_store_kb())
        return

    if not _is_admin(chat_id):
        await _send(chat_id, "🔒 فروش اشتراک فعلاً غیرفعال است.\n\nبرای مدیریت سرویس، فقط ادمین‌های مجاز دسترسی دارند.")
        return

    if text == "/admin":
        await _send(chat_id, _admin_welcome_text(get_bot_text("welcome", "🛠 <b>VodiWalker Control Center</b>")), _main_menu_kb())
        return

    if text == "/menu":
        _pending.pop(chat_id, None)
        await _send(chat_id, _admin_welcome_text(get_bot_text("welcome", "🛠 <b>VodiWalker Control Center</b>")), _main_menu_kb())
        return

    if text == "/cancel":
        _pending.pop(chat_id, None)
        await _send(chat_id, "لغو شد.", _main_menu_kb())
        return

    pending = _pending.get(chat_id)

    if pending and pending.get("action") == "newsub" and pending.get("step") == "name" and text:
        name = text[:60]
        sid, s = await create_sub_group(name=name)
        link_uid = pending.get("link_uid")
        _pending.pop(chat_id, None)
        if link_uid and link_uid in LINKS:
            await set_link_sub(link_uid, sid)
            await _send(chat_id, f"✅ گروه ساخته شد و کانفیگ به اون اضافه شد.\n\n{_format_cfg_group(link_uid)}", _cfg_group_kb(link_uid))
        else:
            await _send(chat_id, f"✅ گروه ساخته شد.\n\n{_format_sub_detail(sid, s)}", _sub_detail_kb(sid))
        return

    if pending and pending.get("action") == "newclient" and text:
        step = pending["step"]
        data = pending["data"]

        if step == "label":
            data["label"] = text[:60] or "کاربر جدید"
            pending["step"] = "volume"
            await _send(chat_id, _wizard_client_prompt("volume", data), _wizard_client_skip_kb("volume", "♾ ارث‌بری از اینباند"))
            return

        if step == "volume":
            parsed = _parse_volume_text(text)
            if parsed is None:
                await _send(chat_id, "❗️ فرمت درست نیست. مثلاً بفرست: <code>10GB</code> یا <code>500MB</code>", _wizard_client_skip_kb("volume", "♾ ارث‌بری از اینباند"))
                return
            data["limit_bytes"] = parsed
            pending["step"] = "days"
            await _send(chat_id, _wizard_client_prompt("days", data), _wizard_client_skip_kb("days", "♾ ارث‌بری از اینباند"))
            return

        if step == "days":
            try:
                d = int(text.strip())
                if d < 0:
                    raise ValueError
            except ValueError:
                await _send(chat_id, "❗️ یه عدد صحیح (روز) بفرست:", _wizard_client_skip_kb("days", "♾ ارث‌بری از اینباند"))
                return
            data["expires_days"] = d
            pending["step"] = "confirm"
            await _send(chat_id, _wizard_client_prompt("confirm", data), _wizard_client_confirm_kb())
            return

    if pending and pending.get("action") == "wizard" and text:
        step = pending["step"]
        data = pending["data"]

        if step == "label":
            data["label"] = text[:60] or "کانفیگ جدید"
            pending["step"] = "protocol"
            await _send(chat_id, _wizard_prompt("protocol", data), _wizard_protocol_kb())
            return

        if step in ("protocol", "fingerprint"):
            # این دو مرحله فقط با دکمه انتخاب می‌شن
            kb = _wizard_protocol_kb() if step == "protocol" else _wizard_fp_kb()
            await _send(chat_id, "لطفاً از دکمه‌های بالا یکی رو انتخاب کن 👆", kb)
            return

        if step == "alpn":
            data["alpn"] = text.strip()[:100]
            pending["step"] = "port"
            await _send(chat_id, _wizard_prompt("port", data), _wizard_skip_kb("port", f"⏭ پیش‌فرض ({DEFAULT_PORT})"))
            return

        if step == "port":
            try:
                p = int(text.strip())
            except ValueError:
                p = None
            if p is None or not (MIN_PORT <= p <= MAX_PORT):
                await _send(chat_id, f"❗️ عدد پورت نامعتبره. یه عدد بین {MIN_PORT} تا {MAX_PORT} بفرست:", _wizard_skip_kb("port", f"⏭ پیش‌فرض ({DEFAULT_PORT})"))
                return
            data["port"] = p
            pending["step"] = "volume"
            await _send(chat_id, _wizard_prompt("volume", data), _wizard_unlimited_kb("volume"))
            return

        if step == "volume":
            parsed = _parse_volume_text(text)
            if parsed is None:
                await _send(chat_id, "❗️ فرمت درست نیست. مثلاً بفرست: <code>10GB</code> یا <code>500MB</code>", _wizard_unlimited_kb("volume"))
                return
            data["limit_bytes"] = parsed
            pending["step"] = "speed"
            await _send(chat_id, _wizard_prompt("speed", data), _wizard_unlimited_kb("speed"))
            return

        if step == "speed":
            parsed = _parse_speed_text(text)
            if parsed is None:
                await _send(chat_id, "❗️ فرمت درست نیست. یه عدد بفرست، مثلاً <code>20</code> (Mbps)", _wizard_unlimited_kb("speed"))
                return
            data["speed_limit_bytes"] = parsed
            pending["step"] = "iplimit"
            await _send(chat_id, _wizard_prompt("iplimit", data), _wizard_unlimited_kb("iplimit"))
            return

        if step == "iplimit":
            n = _parse_nonneg_int(text)
            if n is None:
                await _send(chat_id, "❗️ یه عدد صحیح بفرست:", _wizard_unlimited_kb("iplimit"))
                return
            data["ip_limit"] = n
            pending["step"] = "days"
            await _send(chat_id, _wizard_prompt("days", data), _wizard_unlimited_kb("days"))
            return

        if step == "days":
            n = _parse_nonneg_int(text)
            if n is None:
                await _send(chat_id, "❗️ یه عدد صحیح بفرست (تعداد روز):", _wizard_unlimited_kb("days"))
                return
            data["expires_days"] = n
            pending["step"] = "confirm"
            await _send(chat_id, _wizard_summary(data), _wizard_confirm_kb())
            return

    # پیام ناشناخته → منو رو نشون بده
    await _send(chat_id, "از دکمه‌های زیر استفاده کن:", _main_menu_kb())

async def _handle_callback(cb: dict):
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    message_id = cb.get("message", {}).get("message_id")
    data = cb.get("data", "")
    cb_id = cb.get("id")

    if chat_id is None:
        return

    # Public storefront callbacks
    if data == "store":
        if not SALES_ENABLED:
            await _answer_cb(cb_id, "فروش اشتراک فعلاً غیرفعال است.")
            await _edit(chat_id, message_id, "🔒 <b>فروش اشتراک موقتاً غیرفعال است</b>\n\nاین بخش پس از آماده‌سازی ماژول فروش در نسخه‌های بعدی فعال می‌شود.\n\n🛠 مدیریت اینباند، کلاینت و سابسکریپشن همچنان فعال است.", _main_menu_kb())
            return
        await _answer_cb(cb_id)
        await _edit(chat_id, message_id, _store_text(), _store_kb())
        return
    if data.startswith("buy:"):
        if not SALES_ENABLED:
            await _answer_cb(cb_id, "فروش اشتراک فعلاً غیرفعال است.")
            return
        await _answer_cb(cb_id, "در حال آماده‌سازی فاکتور…")
        await _send_invoice(chat_id, data.split(":",1)[1])
        return
    if data == "myorders":
        await _answer_cb(cb_id)
        orders=user_orders(chat_id)
        if not orders:
            await _edit(chat_id,message_id,"🧾 هنوز خریدی ثبت نشده.",_store_kb())
        else:
            lines=["🧾 <b>خریدهای اخیر شما</b>\n"]
            for o in orders:
                plan=PLANS.get(o.get("plan_id"),{})
                lines.append(f"• {plan.get('name',o.get('plan_id'))} — {o.get('created_at','')[:16]}\n<code>https://{get_host()}/subscription/{o.get('link_uid')}</code>")
            await _edit(chat_id,message_id,"\n".join(lines),_store_kb())
        return

    if not _is_admin(chat_id):
        await _answer_cb(cb_id, "⛔ از فروشگاه استفاده کن")
        return
    await _answer_cb(cb_id)

    if data == "menu":
        _pending.pop(chat_id, None)
        await _edit(chat_id, message_id, _admin_welcome_text(get_bot_text("admin_menu", "🛠 <b>VodiWalker Control Center</b>")), _main_menu_kb())
        return

    if data == "stats":
        total = len(LINKS)
        active = sum(1 for l in LINKS.values() if is_link_allowed(l))
        total_used = sum(int(l.get("used_bytes", 0) or 0) for l in LINKS.values())
        st = sales_stats()
        await _edit(chat_id, message_id,
                    f"📊 <b>آمار کلی VodiWalker</b>\n\n"
                    f"🌐 کل کانفیگ‌ها: <b>{total}</b>\n"
                    f"🟢 فعال: <b>{active}</b>\n"
                    f"🔴 غیرفعال/منقضی: <b>{total-active}</b>\n"
                    f"📦 کل مصرف: <b>{fmt_bytes(total_used)}</b>\n"
                    f"🗂 گروه‌های ساب: <b>{len(SUBS)}</b>\n\n"
                    f"👥 مشتریان فروشگاه: <b>{st['customers']}</b>\n"
                    f"🧾 سفارش‌های موفق: <b>{st['orders']}</b>\n"
                    f"⭐ مجموع فروش: <b>{st['stars']}</b> Stars",
                    _main_menu_kb())
        return

    if data == "salesstats":
        if not SALES_ENABLED:
            await _edit(chat_id,message_id,"🔒 <b>گزارش فروش</b>\n\nماژول فروش فعلاً غیرفعال است و در نسخه‌های بعدی فعال می‌شود.",_main_menu_kb())
            return
        st=sales_stats()
        await _edit(chat_id,message_id,
                    f"📈 <b>گزارش فروش VodiWalker</b>\n\n"
                    f"👥 مشتریان: <b>{st['customers']}</b>\n"
                    f"🧾 سفارش‌های موفق: <b>{st['orders']}</b>\n"
                    f"⭐ مجموع فروش: <b>{st['stars']}</b> Stars",
                    _main_menu_kb())
        return

    if data.startswith("list:"):
        page = int(data.split(":", 1)[1] or 0)
        if not LINKS:
            await _edit(chat_id, message_id, "هنوز هیچ کانفیگی ساخته نشده.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, f"📋 لیست کانفیگ‌ها ({len(LINKS)} مورد):", _links_list_kb(page))
        return

    # ── گروه‌های ساب (لینک حرفه‌ای) ────────────────────────────────────────────
    if data.startswith("subs:"):
        page = int(data.split(":", 1)[1] or 0)
        if not SUBS:
            await _edit(chat_id, message_id, "هنوز هیچ گروهی ساخته نشده.\n\nبرای گرفتن لینک ساب حرفه‌ای (صفحه‌ی زیبا)، اول یه گروه بساز و کانفیگ مورد نظرت رو داخلش بذار.", _subs_list_kb(0))
            return
        await _edit(chat_id, message_id, f"🗂 گروه‌های ساب ({len(SUBS)} مورد):", _subs_list_kb(page))
        return

    if data == "newsub":
        _pending[chat_id] = {"action": "newsub", "step": "name", "link_uid": None}
        await _edit(chat_id, message_id, "✏️ اسم گروه رو بفرست (این اسم فقط برای خودت توی مدیریت گروه‌هاست):", _wizard_cancel_kb())
        return

    if data.startswith("subview:"):
        sid = data.split(":", 1)[1]
        s = SUBS.get(sid)
        if not s:
            await _edit(chat_id, message_id, "این گروه دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, _format_sub_detail(sid, s), _sub_detail_kb(sid))
        return

    if data.startswith("subaddlink:"):
        _, sid, page_s = data.split(":", 2)
        if sid not in SUBS:
            await _edit(chat_id, message_id, "این گروه دیگه وجود نداره.", _main_menu_kb())
            return
        if not LINKS:
            await _edit(chat_id, message_id, "هنوز هیچ کانفیگی نداری که به گروه اضافه کنی.", _sub_detail_kb(sid))
            return
        _pending[chat_id] = {"action": "subaddlink_ctx", "sid": sid}
        await _edit(chat_id, message_id, "کدوم کانفیگ رو به این گروه اضافه کنم؟\n(کانفیگ‌هایی که علامت ✅ دارن همین الان توی این گروهن)", _pick_link_for_group_kb(sid, int(page_s or 0)))
        return

    if data.startswith("subaddlinkdo:"):
        uid = data.split(":", 1)[1]
        ctx = _pending.get(chat_id) or {}
        sid = ctx.get("sid") if ctx.get("action") == "subaddlink_ctx" else None
        if not sid or sid not in SUBS:
            await _answer_cb(cb_id, "این عملیات منقضی شده، از منوی گروه‌ها دوباره امتحان کن.")
            return
        ok = await set_link_sub(uid, sid)
        if not ok:
            await _answer_cb(cb_id, "این کانفیگ دیگه وجود نداره")
            return
        _pending.pop(chat_id, None)
        s = SUBS.get(sid)
        await _edit(chat_id, message_id, f"✅ کانفیگ به گروه اضافه شد.\n\n{_format_sub_detail(sid, s)}", _sub_detail_kb(sid))
        return

    if data.startswith("subdel:"):
        sid = data.split(":", 1)[1]
        s = SUBS.get(sid)
        if not s:
            await _edit(chat_id, message_id, "این گروه دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, f"❗️ از حذف گروه «{s.get('name')}» مطمئنی؟ لینک ساب حرفه‌ای‌اش دیگه کار نمی‌کنه (کانفیگ‌ها حذف نمی‌شن، فقط از گروه خارج می‌شن).", _confirm_subdel_kb(sid))
        return

    if data.startswith("subdelok:"):
        sid = data.split(":", 1)[1]
        name = await remove_sub_group(sid)
        if name is None:
            await _edit(chat_id, message_id, "این گروه قبلاً حذف شده بود.", _main_menu_kb())
        else:
            await _edit(chat_id, message_id, f"🗑 گروه «{name}» حذف شد.", _main_menu_kb())
        return

    # ── گروه یک کانفیگ خاص (از صفحه‌ی جزئیات کانفیگ) ───────────────────────────
    if data.startswith("cfggroup:"):
        uid = data.split(":", 1)[1]
        if uid not in LINKS:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        _pending[chat_id] = {"action": "cfg_group_ctx", "uid": uid}
        await _edit(chat_id, message_id, _format_cfg_group(uid), _cfg_group_kb(uid))
        return

    if data.startswith("cfgungroup:"):
        uid = data.split(":", 1)[1]
        await set_link_sub(uid, None)
        l = LINKS.get(uid)
        if not l:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, _format_detail(uid, l), _link_detail_kb(uid, l["active"]))
        return

    if data.startswith("cfgaddgroup:"):
        sid = data.split(":", 1)[1]
        ctx = _pending.get(chat_id) or {}
        uid = ctx.get("uid") if ctx.get("action") == "cfg_group_ctx" else None
        if not uid or uid not in LINKS:
            await _answer_cb(cb_id, "این عملیات منقضی شده، از روی کانفیگ دوباره وارد این بخش شو.")
            return
        ok = await set_link_sub(uid, sid)
        if not ok:
            await _answer_cb(cb_id, "این گروه دیگه وجود نداره")
            return
        _pending.pop(chat_id, None)
        await _edit(chat_id, message_id, f"✅ کانفیگ به گروه اضافه شد.\n\n{_format_cfg_group(uid)}", _cfg_group_kb(uid))
        return

    if data.startswith("cfgnewgroup:"):
        uid = data.split(":", 1)[1]
        if uid not in LINKS:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        _pending[chat_id] = {"action": "newsub", "step": "name", "link_uid": uid}
        await _edit(chat_id, message_id, "✏️ اسم گروه جدید رو بفرست؛ بعد از ساخته شدن، همین کانفیگ خودکار داخلش قرار می‌گیره:", _wizard_cancel_kb())
        return

    if data == "newcfg":
        _pending[chat_id] = {"action": "wizard", "step": "label", "data": {}}
        await _edit(chat_id, message_id, _wizard_prompt("label", {}), _wizard_cancel_kb())
        return

    if data == "w:cancel":
        _pending.pop(chat_id, None)
        await _edit(chat_id, message_id, "ساخت کانفیگ لغو شد.", _main_menu_kb())
        return

    if data.startswith("w:"):
        pending = _pending.get(chat_id)
        if not pending or pending.get("action") != "wizard":
            await _edit(chat_id, message_id, "این مرحله دیگه معتبر نیست، از منوی زیر دوباره شروع کن.", _main_menu_kb())
            return

        step = pending["step"]
        wdata = pending["data"]

        if data.startswith("w:proto:") and step == "protocol":
            proto = data.split(":", 2)[2]
            wdata["protocol"] = proto if proto in PROTOCOLS else DEFAULT_PROTOCOL
            pending["step"] = "fingerprint"
            await _edit(chat_id, message_id, _wizard_prompt("fingerprint", wdata), _wizard_fp_kb())
            return

        if data.startswith("w:fp:") and step == "fingerprint":
            fp = data.split(":", 2)[2]
            wdata["fingerprint"] = fp if fp in FINGERPRINTS else DEFAULT_FINGERPRINT
            pending["step"] = "alpn"
            await _edit(chat_id, message_id, _wizard_prompt("alpn", wdata), _wizard_alpn_kb())
            return

        if data.startswith("w:alpnpreset:") and step == "alpn":
            code = data.split(":", 2)[2]
            wdata["alpn"] = ALPN_PRESET_MAP.get(code, "")
            pending["step"] = "port"
            await _edit(chat_id, message_id, _wizard_prompt("port", wdata), _wizard_skip_kb("port", f"⏭ پیش‌فرض ({DEFAULT_PORT})"))
            return

        if data == "w:skip:alpn" and step == "alpn":
            wdata["alpn"] = ""
            pending["step"] = "port"
            await _edit(chat_id, message_id, _wizard_prompt("port", wdata), _wizard_skip_kb("port", f"⏭ پیش‌فرض ({DEFAULT_PORT})"))
            return

        if data == "w:skip:port" and step == "port":
            wdata["port"] = DEFAULT_PORT
            pending["step"] = "volume"
            await _edit(chat_id, message_id, _wizard_prompt("volume", wdata), _wizard_unlimited_kb("volume"))
            return

        if data == "w:skip:volume" and step == "volume":
            wdata["limit_bytes"] = 0
            pending["step"] = "speed"
            await _edit(chat_id, message_id, _wizard_prompt("speed", wdata), _wizard_unlimited_kb("speed"))
            return

        if data == "w:skip:speed" and step == "speed":
            wdata["speed_limit_bytes"] = 0
            pending["step"] = "iplimit"
            await _edit(chat_id, message_id, _wizard_prompt("iplimit", wdata), _wizard_unlimited_kb("iplimit"))
            return

        if data == "w:skip:iplimit" and step == "iplimit":
            wdata["ip_limit"] = 0
            pending["step"] = "days"
            await _edit(chat_id, message_id, _wizard_prompt("days", wdata), _wizard_unlimited_kb("days"))
            return

        if data == "w:skip:days" and step == "days":
            wdata["expires_days"] = 0
            pending["step"] = "confirm"
            await _edit(chat_id, message_id, _wizard_summary(wdata), _wizard_confirm_kb())
            return

        if data == "w:confirm" and step == "confirm":
            expires_days = wdata.get("expires_days", 0)
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat() if expires_days > 0 else None
            uid, link = await make_link(
                label=wdata.get("label") or "کانفیگ جدید",
                limit_bytes=wdata.get("limit_bytes", 0),
                expires_at=expires_at,
                protocol=wdata.get("protocol", DEFAULT_PROTOCOL),
                fingerprint=wdata.get("fingerprint", DEFAULT_FINGERPRINT),
                alpn=wdata.get("alpn", ""),
                port=wdata.get("port", DEFAULT_PORT),
                ip_limit=wdata.get("ip_limit", 0),
                speed_limit_bytes=wdata.get("speed_limit_bytes", 0),
            )
            _pending.pop(chat_id, None)
            await _edit(chat_id, message_id, f"✅ کانفیگ ساخته شد.\n\n{_format_detail(uid, link)}", _link_detail_kb(uid, link["active"]))
            return

        # هیچ‌کدوم از حالت‌های بالا مچ نشد (مثلاً روی دکمه‌ی مرحله‌ی قبلی که دیگه معتبر نیست زده)
        await _answer_cb(cb_id, "این دکمه دیگه معتبر نیست.")
        return

    if data.startswith("view:"):
        uid = data.split(":", 1)[1]
        l = LINKS.get(uid)
        if not l:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, _format_detail(uid, l), _link_detail_kb(uid, l["active"]))
        return

    if data.startswith("toggle:"):
        uid = data.split(":", 1)[1]
        l = await set_link_active(uid, not LINKS.get(uid, {}).get("active", True))
        if not l:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, _format_detail(uid, l), _link_detail_kb(uid, l["active"]))
        return

    if data.startswith("link:"):
        uid = data.split(":", 1)[1]
        l = LINKS.get(uid)
        if not l:
            await _answer_cb(cb_id, "کانفیگ پیدا نشد")
            return
        host = get_host()
        vless = vless_link_for_link(l, uid, host)
        sub_url = f"https://{host}/subscription/{uid}"
        msg = f"🔗 لینک اتصال «{l.get('label')}»:\n\n<code>{vless}</code>\n\nلینک ساب ساده (فقط متن کانفیگ):\n<code>{sub_url}</code>"
        sid = l.get("sub_id")
        if sid and sid in SUBS:
            msg += f"\n\n✨ لینک ساب حرفه‌ای گروه «{SUBS[sid].get('name','?')}»:\n<code>{_group_public_url(SUBS[sid])}</code>"
        else:
            msg += "\n\nℹ️ این کانفیگ توی هیچ گروهی نیست. برای گرفتن لینک ساب حرفه‌ای، از دکمه‌ی «🗂 گروه ساب» توی صفحه‌ی کانفیگ استفاده کن."
        await _send(chat_id, msg)
        return

    if data.startswith("del:"):
        uid = data.split(":", 1)[1]
        l = LINKS.get(uid)
        if not l:
            await _edit(chat_id, message_id, "این کانفیگ دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, f"❗️ از حذف «{l.get('label')}» مطمئنی؟ این عمل برگشت‌ناپذیره.", _confirm_delete_kb(uid))
        return

    if data.startswith("delok:"):
        uid = data.split(":", 1)[1]
        label = await remove_link(uid)
        if label is None:
            await _edit(chat_id, message_id, "این کانفیگ قبلاً حذف شده بود.", _main_menu_kb())
        else:
            await _edit(chat_id, message_id, f"🗑 کانفیگ «{label}» حذف شد.", _main_menu_kb())
        return

    # ── مدیریت کاربران (کلاینت‌های) یک اینباند ──────────────────────────────────
    if data.startswith("clients:"):
        _, uid, page_s = data.split(":", 2)
        if uid not in LINKS:
            await _edit(chat_id, message_id, "این اینباند دیگه وجود نداره.", _main_menu_kb())
            return
        await _edit(chat_id, message_id, _format_clients_list(uid), _clients_list_kb(uid, int(page_s or 0)))
        return

    if data.startswith("addclient:"):
        uid = data.split(":", 1)[1]
        if uid not in LINKS:
            await _edit(chat_id, message_id, "این اینباند دیگه وجود نداره.", _main_menu_kb())
            return
        _pending[chat_id] = {"action": "newclient", "step": "label", "data": {"parent_uid": uid}}
        await _edit(chat_id, message_id, _wizard_client_prompt("label", {}), _wizard_client_cancel_kb())
        return

    if data.startswith("delclient:"):
        _, uid, cid = data.split(":", 2)
        child = LINKS.get(cid)
        if not child or child.get("parent_inbound_id") != uid:
            await _edit(chat_id, message_id, "این کاربر دیگه وجود نداره.", _clients_list_kb(uid, 0))
            return
        await _edit(chat_id, message_id, f"❗️ از حذف کاربر «{child.get('label')}» مطمئنی؟", _confirm_delete_client_kb(uid, cid))
        return

    if data.startswith("delclientok:"):
        _, uid, cid = data.split(":", 2)
        try:
            await remove_inbound_client(uid, cid)
            await _edit(chat_id, message_id, "🗑 کاربر حذف شد.", _clients_list_kb(uid, 0))
        except ValueError:
            await _edit(chat_id, message_id, "این کاربر قبلاً حذف شده بود.", _clients_list_kb(uid, 0))
        return

    if data == "wc:cancel":
        _pending.pop(chat_id, None)
        await _edit(chat_id, message_id, "ساخت کاربر لغو شد.", _main_menu_kb())
        return

    if data.startswith("wc:"):
        pending = _pending.get(chat_id)
        if not pending or pending.get("action") != "newclient":
            await _edit(chat_id, message_id, "این مرحله دیگه معتبر نیست، از منوی کاربران دوباره شروع کن.", _main_menu_kb())
            return
        step = pending["step"]
        wdata = pending["data"]

        if data == "wc:skip:volume" and step == "volume":
            wdata["limit_bytes"] = 0
            pending["step"] = "days"
            await _edit(chat_id, message_id, _wizard_client_prompt("days", wdata), _wizard_client_skip_kb("days", "♾ ارث‌بری از اینباند"))
            return

        if data == "wc:skip:days" and step == "days":
            wdata["expires_days"] = 0
            pending["step"] = "confirm"
            await _edit(chat_id, message_id, _wizard_client_prompt("confirm", wdata), _wizard_client_confirm_kb())
            return

        if data == "wc:confirm" and step == "confirm":
            parent_uid = wdata["parent_uid"]
            try:
                cid, child = await add_client_to_inbound(
                    parent_uid,
                    label=wdata.get("label"),
                    limit_bytes=wdata.get("limit_bytes") or None,
                    expires_days=int(wdata.get("expires_days") or 0),
                )
            except ValueError as exc:
                await _edit(chat_id, message_id, f"❌ {exc}", _clients_list_kb(parent_uid, 0))
                _pending.pop(chat_id, None)
                return
            _pending.pop(chat_id, None)
            await _edit(chat_id, message_id, f"✅ کاربر جدید ساخته شد.\n\n{_format_detail(cid, child)}", _link_detail_kb(cid, child["active"]))
            return

        await _edit(chat_id, message_id, "این مرحله دیگه معتبر نیست.", _main_menu_kb())
        return

# ── Polling loop ─────────────────────────────────────────────────────────────
async def _poll_loop():
    global _running
    offset = 0
    logger.info(f"🤖 Telegram bot polling started (admins: {len(ADMIN_IDS)})")
    while _running:
        try:
            res = await _call("getUpdates", offset=offset, timeout=30, allowed_updates=["message", "callback_query", "pre_checkout_query"])
            if not res or not res.get("ok"):
                await asyncio.sleep(3)
                continue
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    if "pre_checkout_query" in upd:
                        await _handle_precheckout(upd["pre_checkout_query"])
                    elif "message" in upd:
                        if upd["message"].get("successful_payment"):
                            await _handle_successful_payment(upd["message"])
                        else:
                            await _handle_message(upd["message"])
                    elif "callback_query" in upd:
                        await _handle_callback(upd["callback_query"])
                except Exception as e:
                    logger.warning(f"Telegram update handling error: {e}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Telegram poll loop error: {e}")
            await asyncio.sleep(3)

# ── Lifecycle ────────────────────────────────────────────────────────────────
async def start_bot():
    global _client, _poll_task, _running
    if _running:
        # از بالا اومدنِ چند حلقه‌ی polling هم‌زمان جلوگیری می‌کنه (مثلاً اگه از پنل
        # چند بار دکمه‌ی «شروع» زده بشه)
        logger.info("Telegram bot: از قبل در حال اجراست، دوباره استارت نشد.")
        return
    if not BOT_TOKEN:
        logger.info("Telegram bot: توکن تنظیم نشده، ربات غیرفعاله.")
        return
    if not ADMIN_IDS:
        logger.warning("Telegram bot: هیچ آیدی ادمینی تنظیم نشده، هیچ‌کس اجازه‌ی مدیریت نداره (ربات روشنه ولی همه رد می‌شن).")
    load_sales()
    _client = httpx.AsyncClient(timeout=httpx.Timeout(40.0, connect=10.0))
    _running = True
    _poll_task = asyncio.create_task(_poll_loop())

async def stop_bot():
    global _running, _client, _poll_task
    _running = False
    if _poll_task:
        _poll_task.cancel()
        _poll_task = None
    if _client:
        await _client.aclose()
        _client = None

async def restart_bot():
    """برای اعمال توکن/آیدی جدید: ربات رو متوقف و با تنظیمات فعلی دوباره روشن می‌کنه."""
    await stop_bot()
    await start_bot()
