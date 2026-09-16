LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl" id="htmlRoot">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VodiWalker | Login</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Estedad:wght@400;500;600;700;800;900&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700;800&family=Shabnam:wght@400;500;700&family=Yekan+Bakh:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#08050f;--panel:rgba(255,255,255,.035);--line:rgba(255,255,255,.09);--line2:rgba(255,255,255,.16);
  --accent:#a855f7;--accent2:#7c3aed;--accent3:#22c55e;
  --text:#f3f0fa;--sub:#9c93b5;--sub2:#655d7e;
  --font-fa:'Vazirmatn',sans-serif;--font-en:'Inter',sans-serif;
}
html,body{background:var(--bg);color:var(--text);min-height:100%;font-family:var(--font-fa)}
html[data-lang="en"] body{font-family:var(--font-en)}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer}
body{
  min-height:100vh;min-height:100svh;min-height:100dvh;display:flex;align-items:center;justify-content:center;position:relative;overflow-x:hidden;overflow-y:auto;padding:24px;
  background:
    radial-gradient(48% 40% at 50% 8%, rgba(168,85,247,.30), transparent 60%),
    radial-gradient(40% 35% at 12% 85%, rgba(124,58,237,.22), transparent 60%),
    radial-gradient(40% 35% at 90% 80%, rgba(34,197,94,.10), transparent 60%),
    #08050f;
}
/* روی صفحات کوتاه (موبایل، زوم بالا، پنجره کوچک) اجازه می‌ده کاربر اسکرول کنه
   تا کل کارت (شامل دکمه‌ی «ثبت‌نام ادمینی» زیر کارت ورود) قابل دیدن و کلیک باشه؛
   وقتی محتوا داخل صفحه جا می‌شه ظاهر صفحه دقیقاً مثل قبل باقی می‌مونه. */
@media (max-height:760px){
  body{align-items:flex-start;padding-top:28px;padding-bottom:28px}
}
.grid-bg{position:absolute;inset:0;opacity:.35;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:38px 38px;mask-image:radial-gradient(65% 55% at 50% 30%,#000 20%,transparent 85%)}
 .grid-bg:before{content:"";position:absolute;inset:-2%;background:conic-gradient(from 0deg,transparent 0deg,rgba(168,85,247,.12) 65deg,transparent 130deg,rgba(62,166,255,.10) 210deg,transparent 290deg);filter:blur(24px);animation:ambientSpin 18s linear infinite;will-change:transform;contain:strict}
@keyframes ambientSpin{to{transform:rotate(360deg)}}
.scanline{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 0%,rgba(255,255,255,.025) 48%,transparent 52%);background-size:100% 180px;animation:scan 7s linear infinite;mix-blend-mode:screen}
@keyframes scan{to{background-position:0 180px}}
.ambient-orb{position:absolute;border-radius:50%;filter:blur(2px);opacity:.45;animation:floatOrb 9s ease-in-out infinite}
.ambient-orb.a{width:180px;height:180px;right:9%;top:12%;background:radial-gradient(circle,rgba(168,85,247,.35),transparent 70%)}
.ambient-orb.b{width:240px;height:240px;left:3%;bottom:3%;background:radial-gradient(circle,rgba(62,166,255,.22),transparent 70%);animation-delay:-3s}
@keyframes floatOrb{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(0,-18px,0)}}
.dot{position:absolute;width:3px;height:3px;border-radius:50%;background:#c9a8ff;opacity:.6;animation:twinkle 3.4s ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:.15;transform:scale(1)}50%{opacity:.9;transform:scale(1.6)}}

.lang-switch{position:absolute;top:22px;left:22px;z-index:5;display:flex;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:100px;padding:3px;gap:2px}
html[dir="rtl"] .lang-switch{left:auto;right:22px}
.lang-switch button{padding:6px 14px;border:0;background:transparent;color:var(--sub);font-size:12px;font-weight:700;border-radius:100px;transition:.15s}
.lang-switch button.on{background:linear-gradient(90deg,var(--accent2),var(--accent));color:#fff}

.wrap{position:relative;z-index:1;width:100%;max-width:420px;display:flex;flex-direction:column;align-items:center;animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.wrap{position:relative;z-index:1;width:100%;max-width:470px;display:flex;flex-direction:column;align-items:center;animation:rise .65s cubic-bezier(.2,.8,.2,1) both}
.login-status{display:flex;align-items:center;gap:8px;margin:0 0 12px;padding:7px 11px;border-radius:999px;border:1px solid rgba(62,166,255,.18);background:rgba(10,18,32,.58);box-shadow:0 8px 30px rgba(0,0,0,.18);font-size:9px;letter-spacing:.12em;color:#9ecfff;text-transform:uppercase}.login-status .live{width:7px;height:7px;border-radius:50%;background:#34d399;box-shadow:0 0 0 5px rgba(52,211,153,.08),0 0 14px rgba(52,211,153,.8);animation:statusPulse 1.8s ease-in-out infinite}@keyframes statusPulse{50%{transform:scale(1.25);opacity:.65}}
.security-strip{display:flex;justify-content:center;gap:7px;flex-wrap:wrap;margin-top:14px}.security-strip span{font-size:8.5px;color:var(--sub);padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:rgba(255,255,255,.025)}.security-strip i{color:#8fd9ff;margin-left:3px}
.login-card-glow{position:absolute;inset:-1px;border-radius:23px;background:conic-gradient(from 180deg,rgba(168,85,247,.0),rgba(168,85,247,.55),rgba(62,166,255,.35),rgba(168,85,247,.0));filter:blur(8px);opacity:.18;z-index:-1;animation:cardGlow 8s linear infinite;will-change:transform;contain:strict}@keyframes cardGlow{to{transform:rotate(360deg)}}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}

.badge-wrap{position:relative;width:92px;height:92px;margin:14px 0 30px}
.orbit-ring{position:absolute;inset:-24px;border-radius:50%;border:1px dashed rgba(168,85,247,.35);animation:orbitspin 7s linear infinite}
.orbit-ring2{position:absolute;inset:-38px;border-radius:50%;border:1px dashed rgba(62,166,255,.20);animation:orbitspin 12s linear infinite reverse}
.planet{position:absolute;top:-5px;left:50%;width:10px;height:10px;margin-left:-5px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#c9f0ff,#3ea6ff 55%,#1c5fa8 100%);box-shadow:0 0 12px 2px rgba(62,166,255,.85)}
.planet2{position:absolute;bottom:-4px;left:50%;width:6px;height:6px;margin-left:-3px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#f3d9ff,#a855f7 60%,#6425d6 100%);box-shadow:0 0 9px 2px rgba(168,85,247,.85)}
@keyframes orbitspin{to{transform:rotate(360deg)}}
.badge-glow{position:absolute;inset:-14px;border-radius:50%;background:radial-gradient(circle,rgba(168,85,247,.55),transparent 70%);filter:blur(6px);animation:pulseGlow 2.6s ease-in-out infinite;will-change:transform,opacity;contain:strict}
@keyframes pulseGlow{0%,100%{opacity:.6;transform:scale(1)}50%{opacity:1;transform:scale(1.08)}}
.badge{position:relative;width:92px;height:92px;border-radius:50%;overflow:hidden;border:2px solid rgba(255,255,255,.18);box-shadow:0 10px 40px -6px rgba(168,85,247,.7);background:#150c26;display:flex;align-items:center;justify-content:center}
.badge img{width:100%;height:100%;object-fit:cover}

.brand-caps{font-size:12px;font-weight:800;letter-spacing:.32em;color:#c9a8ff;margin-bottom:14px}
h1{font-size:29px;font-weight:900;text-align:center;line-height:1.5;color:var(--text)}
h1 .g{background:linear-gradient(90deg,#c9a8ff,#a855f7,#8fd9ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.subtitle{margin-top:10px;font-size:13.5px;color:var(--sub);text-align:center;line-height:1.9;max-width:340px}

.card{position:relative;
  width:100%;margin-top:28px;padding:30px 28px;border-radius:24px;
  background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.015));
  border:1px solid var(--line);backdrop-filter:none;
  box-shadow:0 36px 100px -26px rgba(0,0,0,.62), inset 0 1px 0 rgba(255,255,255,.05);
}
.field{margin-bottom:16px}
.field label{display:block;font-size:12px;font-weight:700;color:var(--sub);margin-bottom:8px}
.inp{position:relative}
.inp input{width:100%;padding:14px 44px;border-radius:12px;border:1px solid var(--line);background:rgba(0,0,0,.28);color:var(--text);font-size:14px;outline:none;transition:.15s;font-family:inherit}
.inp input::placeholder{color:var(--sub2)}
.inp input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(168,85,247,.20)}
.inp i.i-lead{position:absolute;right:14px;top:50%;transform:translateY(-50%);color:var(--sub);font-size:16px;pointer-events:none}
html[dir="ltr"] .inp i.i-lead{right:auto;left:14px}
html[dir="ltr"] .inp input{padding:13px 42px}
.toggle-eye{position:absolute;left:12px;top:50%;transform:translateY(-50%);background:none;border:0;color:var(--sub);font-size:16px;padding:4px;border-radius:6px;transition:.15s}
html[dir="ltr"] .toggle-eye{left:auto;right:12px}
.toggle-eye:hover{color:var(--text);background:rgba(255,255,255,.07)}
.remember{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--sub);margin:2px 0 20px;user-select:none;cursor:pointer}
.remember input{accent-color:var(--accent);width:15px;height:15px}
.error{display:flex;gap:8px;align-items:center;background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.30);color:#ff9b9b;border-radius:11px;padding:11px 13px;font-size:12.5px;margin-bottom:16px}
.error::before{content:"\ea87";font-family:"tabler-icons";font-size:15px;flex-shrink:0}
.btn-main{width:100%;padding:15px;border:0;border-radius:12px;background:linear-gradient(90deg,var(--accent2),var(--accent));color:#fff;font-weight:800;font-size:14.5px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:.18s;box-shadow:0 14px 30px -10px rgba(168,85,247,.65)}
.btn-main:hover{filter:brightness(1.08);transform:translateY(-1px)}
.btn-main:active{transform:translateY(0)}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{animation:spin .7s linear infinite}
.foot{margin-top:22px;text-align:center;font-size:11.5px;color:var(--sub2)}
.admin-reg-row{margin-top:16px;padding-top:14px;border-top:1px dashed var(--line);text-align:center}
.admin-reg-btn{width:100%;background:rgba(255,255,255,.03);border:1px dashed var(--line2);color:var(--sub);padding:11px;border-radius:12px;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:8px;transition:.15s}
.admin-reg-btn:hover{color:var(--text);border-color:var(--accent);background:rgba(168,85,247,.07)}
.areg-overlay{position:fixed;inset:0;z-index:50;display:none;align-items:center;justify-content:center;background:rgba(4,2,10,.72);backdrop-filter:blur(3px);padding:18px}
.areg-overlay.show{display:flex}
.areg-box{width:100%;max-width:420px;max-height:88vh;overflow:auto;padding:24px;border-radius:20px;background:#100a1e;border:1px solid var(--line2);box-shadow:0 40px 100px -20px rgba(0,0,0,.7);animation:rise .35s ease both}
.areg-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:16px}
.areg-badge{display:inline-flex;align-items:center;gap:6px;font-size:9.5px;font-weight:800;color:#c9a8ff;background:rgba(168,85,247,.12);border:1px solid rgba(168,85,247,.25);padding:5px 10px;border-radius:999px;margin-bottom:9px}
.areg-head h3{font-size:17px;font-weight:900;margin:0 0 6px}
.areg-head p{font-size:11.5px;color:var(--sub);line-height:1.8;margin:0;max-width:300px}
.areg-close{background:rgba(255,255,255,.06);border:1px solid var(--line);color:var(--sub);width:32px;height:32px;border-radius:10px;flex-shrink:0;display:grid;place-items:center}
.areg-close:hover{color:var(--text)}
.areg-msg{font-size:12px;border-radius:10px;padding:10px 12px;margin-bottom:14px;line-height:1.8}
.areg-msg.ok{background:rgba(34,197,94,.10);border:1px solid rgba(34,197,94,.28);color:#7cf0a8}
.areg-msg.err{background:rgba(239,68,68,.10);border:1px solid rgba(239,68,68,.30);color:#ff9b9b}
.areg-hint{margin-top:14px;font-size:10.5px;color:var(--sub2);line-height:1.9;text-align:center}
@media(max-width:480px){h1{font-size:24px}.card{padding:22px 18px}.login-status{font-size:7.5px}.security-strip span{font-size:7.5px}}
@media (prefers-reduced-motion: reduce){
  .grid-bg:before,.scanline,.ambient-orb,.dot,.login-card-glow,.orbit-ring,.orbit-ring2,.badge-glow,.login-status .live,.wrap{animation:none!important}
}
@media (max-width:820px), (pointer:coarse){
  /* Phones/low-end GPUs: the jank came from the blurred/filtered layers being
     repainted every frame (conic-gradient + blur, glow blur, scanline gradient
     shift) — those are the expensive ones and stay off on touch/small screens.
     .orbit-ring / .orbit-ring2 (the spinning "planet" rings) only animate a
     `transform`, which the compositor handles almost for free, so they keep
     spinning on mobile instead of being frozen along with the heavy effects. */
  .grid-bg:before,.scanline,.ambient-orb,.login-card-glow,.badge-glow{animation:none!important}
  .grid-bg:before{filter:blur(14px)}
  .login-card-glow{filter:blur(5px)}
  .badge-glow{filter:blur(4px)}
  .orbit-ring,.orbit-ring2{will-change:transform}
}
</style>
<style>
.perm-grid,.bot-text-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.perm-item{display:flex;align-items:center;gap:9px;padding:11px 12px;border:1px solid var(--line);background:var(--panel2);border-radius:13px;font-size:12px}.perm-item input{accent-color:var(--accent)}.bot-text-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.bot-text-grid textarea{width:100%;resize:vertical;min-height:90px;background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:12px;padding:11px;font:inherit;line-height:1.8}@media(max-width:700px){.perm-grid,.bot-text-grid{grid-template-columns:1fr}}
.tpl-studio-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap}
.tpl-badge{display:flex;align-items:center;gap:6px;padding:6px 11px;border-radius:99px;background:rgba(148,85,255,.12);color:#b79bff;border:1px solid rgba(148,85,255,.22);font-size:10.5px;font-weight:800;white-space:nowrap}
.tpl-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:14px;margin-top:14px}
.tpl-fields{display:flex;flex-direction:column;gap:8px}
.tpl-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 13px;border:1px solid var(--line);background:var(--panel2);border-radius:13px;cursor:pointer;transition:border-color .12s ease}
.tpl-row:hover{border-color:var(--line2)}
.tpl-row-main{display:flex;align-items:center;gap:10px;min-width:0}
.tpl-row-main i{width:32px;height:32px;flex-shrink:0;display:grid;place-items:center;border-radius:9px;background:rgba(148,85,255,.12);color:#a997ff;font-size:15px}
.tpl-row-main b{display:block;font-size:12px}
.tpl-row-main small{display:block;color:var(--sub2);font-size:9.5px;margin-top:2px}
input.tpl-switch{appearance:none;-webkit-appearance:none;width:36px;height:20px;border-radius:99px;background:var(--line2);border:1px solid var(--line);position:relative;cursor:pointer;flex-shrink:0;margin:0;transition:background-color .16s ease}
input.tpl-switch:after{content:'';position:absolute;width:14px;height:14px;top:2px;right:2px;border-radius:50%;background:#fff;transition:right .16s ease;box-shadow:0 1px 3px rgba(0,0,0,.3)}
input.tpl-switch:checked{background:linear-gradient(90deg,var(--accent),var(--accent-d));border-color:transparent}
input.tpl-switch:checked:after{right:18px}
.tpl-preview{padding:14px;border:1px dashed var(--line2);border-radius:14px;background:linear-gradient(155deg,rgba(148,85,255,.06),rgba(255,255,255,.015))}
.tpl-preview-label{display:flex;align-items:center;gap:7px;font-size:10.5px;color:var(--sub);font-weight:700;margin-bottom:10px}
.tpl-preview-row{display:flex;align-items:center;gap:9px;padding:11px 12px;border-radius:12px;background:var(--panel);border:1px solid var(--line)}
.tpl-preview-dot{width:9px;height:9px;border-radius:50%;background:var(--good);box-shadow:0 0 0 3px rgba(34,197,139,.18);flex-shrink:0}
.tpl-preview-text{flex:1;min-width:0;font-size:12px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;direction:ltr;text-align:left}
.tpl-preview-proto{font-size:9px;font-weight:800;color:var(--accent);background:rgba(148,85,255,.12);padding:3px 8px;border-radius:99px;flex-shrink:0}
@media(max-width:760px){.tpl-grid{grid-template-columns:1fr}}
.admin-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.admin-card{position:relative;overflow:hidden;padding:18px;border:1px solid var(--line);background:linear-gradient(155deg,var(--panel) 0%,var(--panel2) 100%);border-radius:18px;box-shadow:var(--shadow-sm);transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease}
.admin-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md);border-color:var(--line2)}
.admin-card.is-owner{border-color:rgba(245,165,36,.35);background:linear-gradient(155deg,rgba(245,165,36,.08) 0%,var(--panel2) 60%)}
.admin-card.is-inactive{opacity:.62}
.admin-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.admin-id{display:flex;align-items:center;gap:11px;min-width:0}
.admin-avatar{flex:none;width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent-d));box-shadow:0 6px 16px rgba(148,85,255,.28)}
.admin-card.is-owner .admin-avatar{background:linear-gradient(135deg,#f5a524,#c9820a);box-shadow:0 6px 16px rgba(245,165,36,.3)}
.admin-meta{min-width:0}
.admin-meta .admin-name{font-size:14px;font-weight:800;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.admin-meta .admin-sub{display:flex;align-items:center;gap:6px;margin-top:3px;font-size:11px;color:var(--sub)}
.admin-role-badge{flex:none;display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:999px;font-size:10px;font-weight:700;letter-spacing:.02em}
.admin-role-badge.owner{color:#f5a524;background:rgba(245,165,36,.14);border:1px solid rgba(245,165,36,.3)}
.admin-role-badge.admin{color:var(--accent);background:rgba(148,85,255,.12);border:1px solid rgba(148,85,255,.28)}
.admin-status-dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 3px rgba(34,197,139,.15)}
.admin-card.is-inactive .admin-status-dot{background:var(--bad);box-shadow:0 0 0 3px rgba(242,73,85,.15)}
.admin-perm-row{display:flex;flex-wrap:wrap;gap:5px;margin-top:14px}
.admin-perm-chip{font-size:10px;padding:3px 8px;border-radius:8px;background:var(--panel2);border:1px solid var(--line);color:var(--sub)}
.admin-perm-chip.all{color:#f5a524;border-color:rgba(245,165,36,.3);background:rgba(245,165,36,.1)}
.admin-card-foot{display:flex;align-items:center;justify-content:space-between;margin-top:16px;padding-top:12px;border-top:1px dashed var(--line)}
.admin-card-foot .admin-login{font-size:10.5px;color:var(--sub2)}
.admin-card-foot .row-actions{gap:6px}
.admins-hero{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center;margin-bottom:14px;padding:20px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(135deg,rgba(124,92,255,.11),rgba(57,214,255,.035));box-shadow:var(--shadow-sm)}.admins-hero h2{font-size:18px;margin:0 0 5px}.admins-hero p{font-size:10px;color:var(--sub);margin:0;line-height:1.9}.admins-summary{display:flex;gap:8px;flex-wrap:wrap}.admins-summary .sum{min-width:92px;padding:11px 13px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.025);text-align:center}.admins-summary b{display:block;font-size:18px}.admins-summary small{display:block;color:var(--sub2);font-size:8px;margin-top:3px}.admin-card{min-height:188px;display:flex;flex-direction:column}.admin-card-top{padding-bottom:13px;border-bottom:1px dashed var(--line)}.admin-id{flex:1}.admin-avatar{position:relative;overflow:hidden}.admin-avatar:after{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent 35%,rgba(255,255,255,.18) 50%,transparent 65%);transform:translateX(-130%);transition:transform .55s ease}.admin-card:hover .admin-avatar:after{transform:translateX(130%)}.admin-perm-row{min-height:45px;align-content:flex-start}.admin-perm-chip{transition:.15s ease}.admin-perm-chip:hover{border-color:var(--line2);color:var(--text)}.admin-card-foot{margin-top:auto}.admin-login{direction:ltr;text-align:left}.admin-actions-label{display:none}.admin-card-foot .row-actions{gap:8px}.admin-card-foot .iconbtn{width:38px;height:34px;border-radius:11px;font-size:15px;background:linear-gradient(145deg,var(--panel2),rgba(124,92,255,.08));border-color:var(--line2);box-shadow:0 7px 18px rgba(0,0,0,.10)}.admin-card-foot .iconbtn.danger{color:var(--bad)}.admin-card-foot .iconbtn.power{color:var(--accent)}.admin-card-foot .iconbtn:hover{transform:translateY(-1px);box-shadow:0 10px 24px rgba(124,92,255,.18)}.access-command-copy{min-width:0}.command-badge{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border-radius:999px;border:1px solid rgba(124,92,255,.28);background:rgba(124,92,255,.10);color:var(--accent);font-size:9px;font-weight:900;letter-spacing:.08em}.access-command-copy h2{font-size:22px;margin:12px 0 7px;letter-spacing:-.02em}.access-command-copy p{max-width:760px}.command-points{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}.command-points span{display:inline-flex;align-items:center;gap:5px;padding:6px 9px;border:1px solid var(--line);border-radius:9px;background:rgba(255,255,255,.025);font-size:9px;color:var(--sub)}.command-points i{color:var(--good)}.admin-directory{overflow:hidden}.directory-live{display:inline-flex;align-items:center;gap:6px;font-size:9px;color:var(--good);font-weight:800}.directory-live i{width:6px;height:6px;border-radius:50%;background:var(--good);box-shadow:0 0 0 4px rgba(34,197,139,.12)}.admin-directory .panel-head{border-bottom:1px solid var(--line)}@media(max-width:700px){.access-command-copy h2{font-size:18px}.command-points{display:grid;grid-template-columns:1fr}}.admin-login-block{display:flex;flex-direction:column;gap:4px}.admin-login-label{font-size:8px;color:var(--sub2)}.admin-card{position:relative;overflow:hidden}.admin-card:before{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:linear-gradient(90deg,var(--accent),transparent);opacity:.7}.admin-card.is-owner:before{background:linear-gradient(90deg,#f5a524,transparent)}.feature-lock{text-align:center;padding:16px 6px 8px}.feature-lock-icon{width:68px;height:68px;margin:0 auto 14px;display:grid;place-items:center;border-radius:20px;background:linear-gradient(145deg,rgba(124,92,255,.18),rgba(53,214,255,.08));border:1px solid rgba(124,92,255,.28);font-size:28px;color:var(--accent)}.feature-lock h3{margin:0 0 8px;font-size:18px}.feature-lock p{margin:0 auto;max-width:520px;line-height:2;color:var(--sub);font-size:11px}.feature-lock-note{display:inline-flex;gap:7px;align-items:center;margin-top:16px;padding:8px 11px;border-radius:999px;border:1px solid var(--line);background:var(--panel2);font-size:9px;color:var(--sub2)}@media(max-width:700px){.admins-hero{grid-template-columns:1fr}.admins-summary{justify-content:flex-start}}
.areq-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 14px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.02);margin-bottom:10px}
.areq-row:last-child{margin-bottom:0}
.areq-info{display:flex;flex-direction:column;gap:3px;min-width:0}
.areq-name{font-weight:800;font-size:12.5px}
.areq-meta{font-size:10px;color:var(--sub2);display:flex;gap:10px;flex-wrap:wrap}
.areq-meta span{display:inline-flex;align-items:center;gap:4px}
.areq-note{font-size:10.5px;color:var(--sub);margin-top:2px}
.areq-actions{display:flex;gap:8px;flex-shrink:0}
.areq-empty{text-align:center;padding:22px 10px;color:var(--sub2);font-size:11px}
.areq-status{font-size:9px;font-weight:800;padding:4px 9px;border-radius:999px}
.areq-status.approved{background:rgba(34,197,94,.10);color:#7cf0a8;border:1px solid rgba(34,197,94,.25)}
.areq-status.rejected{background:rgba(239,68,68,.10);color:#ff9b9b;border:1px solid rgba(239,68,68,.25)}
@media(max-width:700px){.admin-grid{grid-template-columns:1fr}}
</style></head>
<body>
<div class="grid-bg"></div><div class="scanline"></div><div class="ambient-orb a"></div><div class="ambient-orb b"></div>
<div class="dot" style="top:14%;left:20%"></div>
<div class="dot" style="top:22%;left:78%;animation-delay:-1s"></div>
<div class="dot" style="top:62%;left:10%;animation-delay:-2s"></div>
<div class="dot" style="top:70%;left:88%;animation-delay:-1.6s"></div>
<div class="dot" style="top:40%;left:6%;animation-delay:-2.4s"></div>
<div class="dot" style="top:85%;left:45%;animation-delay:-.6s"></div>

<div class="lang-switch">
  <button id="langFa" class="on" onclick="setLang('fa')">فارسی</button>
  <button id="langEn" onclick="setLang('en')">EN</button>
</div>

<div class="wrap">
  <div class="badge-wrap">
    <div class="orbit-ring2"></div>
    <div class="orbit-ring"><span class="planet"></span><span class="planet2"></span></div>
    <div class="badge-glow"></div>
    <div class="badge"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAACoT0lEQVR4nLT9d7Rl2VneC//mXHnnvU/OletU7O7qbnVUK2chIQmEMAauAQubYH98YK6N8cXmDuyL7zUIjA0GG2QJSSgjdUvdklrqnLuru0JXTienfXYOK875/bF2VbfAYPve+60xzqhxdp19ztprvvOdb3ie5xX8/+GSwtJCAEiUShgaGmd4aIzzF85jWyZKKRAgECAkUki01gihETIhUUBiUcmNkstnWasuEkQdUBIhBIZhYBgGXb/Oj3/oZ3njG97OieMnqBTLbFa3UcBfPvQXdMIGUoFhOsRSo7VPTIDSGkMKpABLOkRhej/SFGgUAgOUxJASKSBJFKCJkhg1uE/DMPEyORzHIoojUIIoCuj3O0RJhABAYEgJCKRhobWBlOn/aBRonf6LQmuF1hqlNKXCCI5rsr6xhBDpZ1ZKDd4Xif8318r8f+sXCSz92nfphwaNFCb1RpvJ0f1MDs+xtr2IbRtorZBCIjAxpIGUBmEUIDBQcUilXMayDZbXFxE6JuvlUIkBIiaOE+IkYsie5MDcUf73f/svWK8vcWTXzezadYjnX3yeQPUYHapQKY9xZXEZx4Jev4/EQAiQg/vTgCbGMIz0fgEhAANM08LzsriOhRACjaDf7+P7PQK/T6tZQ+kYyzSx7QyO41CpTBMEPu1WjyiK8eMeBgaGIRAIHNtFKYUiQcUKhUKrBCEkhgRh2EyOz3Ft8TJCCIR43XoLhcDU+saTjv8fG8P/o18ghaPTnZs+zBuvSxMQpHeqQZrY5Dh26A1cuHaGZmcb23IQWiBId5ppmiRK44d9yqUytu2ysrGMaQoMAbbtEgQRcRwghUEv6nP3/rfz5rvv5f/4s/8N2xIEUYRGkLOLCDSGtPA8j1anQaRCFDHSkBjSAm2Q+qAYpWKkFGgtkNIgSRKkMEBITMPEcTIIDCzbxjINpCGI44goCuj22oRhQBzHaK0xTBPXcbFsm5GRERzbZm1tg1qtgZQmuUwBAK0VcRKTqJBEJ0CCSqCYrxBFPu1uE2nowc/qG89SD56zGDxfIUCToLX6v7WW/7c8QOri011+3UJTq9SAAC0QwhgsfoIpIQ7brK0vcWT/zTzx/KN4bg60RukEQ5qoBIK+z+joBEOVYdY2V8m4Ln7UQylF1I0RhoEwBEJBxRvjRz7yUb714P1YwgQhsUwBQhPqLkLbmFoRtrsYloGpLBAehmGgdYKUAqU0psxw3VtpDSqBUrlMu90eGIYkSSRoTRT5NxYPkaT/ahNjsFCpq4Zut4/qdmi2G4wOjzE2PsH0zByNepPmdpsoiLAsGylAiQRLGsRxRMZ1QUPfb2GZkCgTrWMQqWEqlYDWGEZ6lKRGpwADgdQIjdbJ/5Qh/E9bjRCGBo2UktSRpoaQ3ohIjUJb2I6DUoo4jpFKYBoGQjh85D0f49KFy5y/fB7HM4hUAFqQzRUYHxunWCrx6tnTNLt1oqSPQOOYFlKaBEmMRhH0Fb/4o79I0Iv406/9CbaVEJEM9ofClAZSmOkZbkiUSg3TkKkrj2IfwxSoRCO1hWVZGIYkikOymQK3334PZ8+eSw3F0Ph+gNYQ+AGJSoiigCAMQKTnt1IKrRMADMNMvVkSEycxfuCj0IwNjTEzOUPGzVOtbrO+uUkUBZhW6vniKObokSOcu/gqvX4DKSFJJIp4sFCpAQghEFKgVDwwWvXXllQT/g+v6/+UBxBY+vpCK6WRQrzmkISR3hwmWqcPN040lfwUZafI0uYymJKnnniRD7/vI7RqfbZbW1gZk5HRClkvRxJpri0ssbm9ieUYFAtFbMsi8RX9oI+UEkNkEAJKpWHuf+obaCFRVoRQBqYArVOvZJoSKUw0AqUTLCv1SEkcY0iJUJJSrkKlMsTK2jWCsIfWCVHY4/KFc/jdHtKAfD5DrpynUCilOzaB7VqNVrtBt9Og53fQSQyGARp0ooh1iGk5ZLw8E6MZgiCkXqtzvn6BUqnMyMgo8/v2sb1dZWurStiP2LfrAH4/oNmp4znOwMuAFAZaaYQwME0TpRXoNFDV6DSAJk6PBi3S+EVLrfkfOxLk/8gPGdLRUppaCIEUBoL0K93xEvTgCwMp052HTm9ORgZ/9wM/zYGZ29E6odneJJ/N8nu//e/ZO3eA4coE/XbExUsX2N7aQAWwb+4Qh3YfZrwyiw4cIj/BFCZGbKK7YGubHTMzVCpFHCFxTAfP9HBlBtd0MQf3mCQarcCxLExpkcuU8NwcpjRxbA+VCAI/wrYyCGwyTpGsW6TXDkAbRKGi24rwO9BvKnRoEfchaw+xZ+4Ih/bdxp7ZQ4wPz5LxShjSBekhjAJxbBF0EpIuzI3t5paDdzA7sY+wD1cuLbGyvEkmk6eQy/OGm9/Au975LhaXFnDtDEmi0FriORkkBmiJZdl4mUx6DFyPt/T1sNVAIBFyYACYCGyNeH1g/jdt6v/OZZslrXSIUjFCmK/98cFbpUwXPw1SBKZpYRkmSZIAAhFJ5qduw3bznLz0JHmvyMFdd/Avfu3nabX7/KP/77/CT1YxPY/D87dgKEVCxOLKVVqdLgILrVugHKZHd3Fgz27efN+bsWyDf/M7v029v4UyfLSWaBIgpNPrYUgb185hmWkEnsSKjJcjidOzXGtFpVQh1oo4FghtouKYublZ4hgWlxfwXAe/HyMx8dwynpvBsiXoNGuxbZMwCDBNSawiqvV1ukEbPwpQscaRBiiNiUW5PEx5aBjTtljfWqNaX6fRqPKWN76Jf/hz/4B//du/xalXT4AUKJ0Gpbbt0um0MIz0KAvj6+uQBoZKqzSVBiBBixg0KGDwQ6nXUn9ztvC3GkDWG9O+30fpEFCD6H7wRiGQgz+SxgKpR7AsCyHMNMLXEMuQOBBkzAKWNHDcMnHUY3Z4B3/we3/EF774Zb720F+ye98eRspTnDt7nq3GKokIQCs824VEk3PL/MOf+jla9TZXVs/z4CP30+m1MVyDIAlIdITWfvqRNGQzBSYnplBRSK/XodPqMjY6hWU6tNsNRkbKFIsZnnrxSZSyOXrwDTiGy/TUNBub2ywsXGFsbIg777gTpTSLC5tsbdTodUO0MkAL/DDENExK2SJZbxghBH2/zub2Iq1ek1glGNLANix0ohGGzejoGG7WYGt7Ecd2+Xs/9dP86af+iBOnn2dkdAzH9ajXt+l0WlhWeu4bpkkQ+USxP6gjiNdlBumlidAkg3XQaJGgMWBwZKi/IWX8Gw3AMkraNC3C0EeTGsDrQwYp5eD8uB78WWlKZ5iYhotn50iShF6vjmlmcV2PWDXxfRPb0kzmD3L7kTfxy7/ykywurfKJ3/lTXOGx2d6ip32GSxPUqmsEvTq2LvPRH34Xh/Yd4ouff4SFxjV6YgHDUPT9AGGaCNNgx+QuPDvLtYUrCOkTCZ+19RUMoFIcI5MpUiqXsW1BdWuFa4sX2OysorRJ3htlx+R+xoamUJFB3/fJZiX/4T/8Lobp0Gg0kFKztdHg/i9/j8tXVun2e+hYEQUB/bjHRHkPcxP7KRWzVGvLnL3wKj2/j2mY2I6NYTmY0qbTqVKqGPzYj/84n//KV3juxKOYdkgSw+joGF7GZXHxCr1+B9M0MEwDP+gDCcKQJEoNCkN6YAxJmpWgQFkIbGzDJiEhTFoYhsY2MnTD2l9b778xCFQ6IghiDGmghUmiEgwE6vqCa4UWEgMJQqSvDlJCoTQZu0DY93FzJrZTput3cI0y2ZxBrxcSap9T507wpc8/xK/82se4evYHeeHRE/Q6fcLQJOkZ3LT3LsbHLI4cuIXbb9vN5z77DZRUzEyP0g4i+n6fmfEC3X6DWq3FLfPH0KGiaA3Ro8Gjzz5I4MeMDk8ipUexWCIRfZ5++Tl63R7ZTGZQE1B0+1UuLPi0+3V2Th0knytQKZW4fHEJ23YpFPNURrJMjk7zwJeeJOwJLGkwOj5Dz49pd2u0g21eOv0Uc2P7OHTwIMduOcLK4hLPP3MFrTNkHI/Q7zI7XuLt77mbRx9+lmuXlhkbHaPdruJlSjSqNZpSUymNIk2TXq+DAdiWjdIRcRINaicGSqcVRIFI6xrSIAHmR45y6MAtfPupLyHoEGsIor+aLfwtHkAKR0sjLYygLEwpAYXSMSqNPJBColAYwiJRCtMwyNmjCAyyVpbh4hSOdHEzNv3Ipxe0sIws+UyFMApQGoqZYfJmiZ/6h+/m7nuO8cDnTvLS8xdoJ3Wm5zze+9a30G618SPN4489w2OPP4NXyOHrTfy4zvT0DpaXlwjCLu96xwfodALOnj+B1hI/7ND2qyRac2D+Fmam57iycIqnX3iYbt8nly1iSGh3mmihQCeDzMZhpDjDu9/6fg7uvYlOq8tmtYqXsZmZGaNSnOT+Lz1Bpy3w+3VmRw+ysnkVTJNivohnucjEpFXrsW/vXt729pvIlTVnzi5y/rjP1UvXeO+HjrC0WuXRZx4nNgMa/UWE9PG8PO1+lV7Ywg+DNFVVCd1OA8M0EFIRhX1s2yZOEsI4QgNSpBmAQqOV5K497wAsXrr0KFo00VJiiRyamHa8If5WAzCEp9M6vUQjMQ0LqdJdHckEpRVSGhhSYJlZdBSTy5eo1+scnL4LW2dodpuMjA0ThjFh0KfZ3SSMewxXZhgqTdJubhMrSdEdJStHuenWef7Rv3g3w+M5rr66QqUwhFAmy+erdHt1vvvki3zq81+mXM4zNTlKrbFAN/ZZq66x1bzGLYfu4Yc//NM89+wTVFsrzM8f5cKZ8xyc348WilqrxuLKeZ4//iiYCkN62HYeKRXNVhVEgpQSlaROUWgD13J48z1v45/80j/Fc/Nksx6ImFdeOgmhw9kzi1w8s0Bvq8h2Y5VERpCYFLIuu3bspt8UWKqAJTPcdPMsd94zRq5scrG2yOjYEJ/6ty+wtLVOU1XpRlVsNyKKA3pRlZa/Sd/vYxo26Ag/6CANI60txH20TtJSslYoIZFJWlpOzAStTezERWuBaYEtBdJwkDjESUAvbNLX1Rvr/n1HgBQ5LYQ5aEyAEmnDIu+MUMqM0Y1bZLNZNAndTpuZyf2sb5wjl5/ESEokASRGgp2xaHTXqW83mJraQUFWcKxxXMdldfUiiQjJumPs3bOT2lKX2vo23W7IaEkzMlnhs7//Mi8+d4WsC/e+dY4Xnj3J/I6DjM+W6YctVjdCisUcb3vrT9JsNpid2YGIFCaSt939DnbuPIwrhxkbK/Pdxx7g/NVXWN+6hmlKEGbaiBJ6UH83SQZlVsOQ6WdH4ycJ93/vy5w+/zL/8Kd/jqOH7sSzS4SB5r43HuYHP/ZWGls9Lp9d4rHHXuL8qVVq64rt6janzlxkZHiCnTPjXD27QPSMz3OPXOMtH93Jj//aEa6dr2K4WfLWCFnLAWeUtr/NZm2ZfidGGJKMnaNSGKHdrSJiRSZToNPpYedK9IMWXb+JlGl/QQuBRKCUxDUyZJ0CfhwDCUIrolCjZY8g7IPUmBR0rFvir3kA08jrtEY+OC90gudlyRhjTOTm0bqLmVVUt2uU8gWKuVEanTX80Ma1M+jIJ9IRjdY2cewzUhnDcyuoJMHQklI5z8r6MkOVMQ7tvZ2yO0nsJ9x1307e8f5b8aMIEcNv/9qXOXG8ytveewvveO8uvvHVF/CDgMWtC/i6zv4DexkdruDZRebnj7GydpVvfuurbNW2MSyot+vUu1usVxfo9BtYtpnW9rVAColhGkhpgYZuL625K50MUqy0qKVU2gcIg4BEx4yX9rFv5hhFp4xreeRLWe6+51be+Y43UCwVCfuas69e4dHvvcDJk1u0VkNu2f8GWq02q+tNVL/AD35oFwcPFzCyFqVykZNPr7K1HXHy/AW6SQ0zKzh79XkavWtoEWObNpHu0w97hGGMgYllSIKkQ89vkZCghUhLxRqiULF7fJ6dM4fY2KzR69fp+lt0oyaNcBOlQwzpkCSKSDe+3wCkyGk1KCvatkPWKmDjIU2L4fIceWuU7fY1mu0mI0OzCEJsZZIoGBmZodlsUe8skYgQ18ri2SUM5ZAYMf2oj1QWc9M7WFm9yuToHA5DzM4M8ZN//+3Mz+/ixe+scfKZJfbfnmPH/jG+9+Bp7rjjJs5dvMQ3HnyIe95yiLve+AaEMFi8tsriyjaLK4tcvHKSU2ePE4Q+0jAQpqLR3aLR3sb1HAwpSVLfPtjlNjpRmNLCy2RotLdulHH1oD0rBvlNkiiEGOTgQcxIYYpb9t5NKTtBvVbHtkxGhybIF/JkSw533H4rBw/uwbJMTh+/xHe+9BKyP8vaeo13vncfI8M5Hr1/i3JhlDf9SI5b3z3Cy4+t8N0/X2Gj3qAmFlnvXKPWXaYbbBCFfXSa1RKGXQypkYZBFIdorYiSkIS0ZqCS672NNHXOOaNMjuynVC5z9vJxNlpX0YSEcUIU+wgRE+nWa73G6fKtOko6xDqi74eMFuaYHdnN0uoycZKwf988ZxdfxowFsxO7OXf5LHumDzBaGaLZbbPR3CTWHZIgIolM9u04DLFBo18lVBGuVaDiFZCEGFaZ2ck9/K+//iPUqg2e/M4SrarF6ZMnuO22YX7+N9+PVRa8/O1LPPC1F5jY6XD46FHcjOTS5XUee+x7fO/Jh+kEfYKwh5ASyzbxMiaNzhrVxiaum8EwXLRK3bsQOm2oDBbVsV0cx6XZrpKoiLSurm8YStp+l2m/QCqkqYiCmIw1xMzoPJXcFMXcECoJicKAZiuikp1irDLKrccOcfDm3eyZHWLzShMjZ3HzXRP84f9xgpNPQ8kxyZiCY/cUuf2HxtharPOpT5xjqdmklVxi2z+HMnz8fg+EwLNtoqhNKNo0uzWEFqjYIAh9hBmRqAilFBJBoVAhCHw0AtvI42VytNs1fL9JZXiIjt9is7GMJSWhaokbMUDGzJEvDxNGAWAS+wY6hHK+SEyfjfVFhrwJXFGk2wjYOT0LUnPm6mlq3Q2UVlRKIwjlMDo0h2ONksvlQZugE+44dg9Zx0Yrh5XqZT7y0Tt48pFTfOVzjzJUnMQre2z2L5L1drJwZYvJI3k261vM7hjj1bPXePTRL7JSPc/i2hUanU1cByzLBa0Igg5eNstWY41WdxvTMga1cT1w6Wm7WWuQUmNIE5DpsYCBlKCSJHWH4npnL/WGhpkaQRILDNOmG7W4vHKKdWsFS5rkMhly3ii53BDabLO+2eYvv3yJJx6d4y1338Mdd+5jaFISao1tCrZWLqFmHM6srLFen2SzuZN73jvHD//8Tr77tSZrqy7B6jpKhuQzJTL5PJvby7Q7LUJahFEPlWiGipMUMkXanWYaM2TzFAtZesEW2/UNlCFQeh3dNChmRhkfniZSCtfKUMqOIQVsd1ppEDhRPKQ3myts1DUmJoVcBRObbnebZreFdEw8q8RIcYKt7VXqzRo7yjvw7AIb9TViAnZOHmI4M0O1uc3OHXtp1tqcW7pMsZRjemSaqAsb9T69eIuP/PibOH3+Ko9/6yJKJDz36pMEnYBbDu/j0K27SboGz335Ki89tU6t2eTVC69Sa6/TDNYJZBNcQSeIEUENRMLO3bto1Os029tpqxQLQ1horZEyRRAJYaSdC5liELTSCJkGgUEQIaREiLSqCSli6HqejQStDLQGywJ0gOkppJZ0+i3qzSZ9dYqiV8GTBUrZUaxA8NWvb3Hq5K1Eqscb753nAx85huUlfO7T32O9toGVDbl0XnLi5XU+9FMH+Imf2ckf/vsFkosV+uoatiMpjFdY21qgH/fRIsbAJZfJUs4N0Wn12bfjCKZ26PTb9FSdlfoasRmitSZRUM6WqeRL9Ho+Sge0gy3iJEZKm6w1oQXAUGaXDsMIL+OmjRKziIoM3IxNpHu0enWGSuOMF2ZYXLxEJpuj1qxyeP8dxIHFhcsvMjM+j8QCS9FsthDAxPAMQ8UxGnWfTqfFG998iJ/6mQ/y5S88zZe++ACGsCjnh5CGoJT3+MAH7qBWb+I547TqLV468TJLW9eotq+RiD4Nf4Nu0BkAN9JaxNzcDoQpuXj5AlHSRhqksQAWQhiDDqI5wAGkKCTDcFLjMKDXbwy8XgrTSnEO13v76saxkJZe0xJ7HEW4do7hwi6ITJTu0w7aRHEXkXhkrSK24TKanWN8aBZbFKDv8OZ3HuWDH72PixeX+PM//R4byz26QR/XKTBW2MmP/70jDO+J+NY3llk+t8nl9VOYWYc4brDRuIRhC0qFYfqdmGK2SKu1SqxD5mYOc+HqGdrxJk1/k5ZfR4sIW3sUvGFMadHubiANCKIERYDW19v5wHhxXrc7baRM838VC0ZGJsDULKyeRssIrQRjuUmG84fIZDNcW32JRq/FHTvfw47heUI0Z5dOkqiIrFdhcmQGVxSQSZ58McPdb57lIx+7i+PPXuaz/+Vpmv4qjWYHicvd9x5mx9wMpnT55Kf+HD/sECYtqs0NpAVB0qPR2UQTY1suru2ihaZYLlEs5ahur7OysYQwNELqgYFYGIaZBnGkuDqtFNJIu2tKa2zLot5eIVEpFM0wbNApqESI76+330DkaNA6IY4Scu4QGbuCbTl4lkfgx4ShQumQIOqTtQp4tosky/TQPogsRkfmeM/7jnHT0V08/dwZPvlnX2M0f4iiXWLvjjk+8vG97DhY5jN/cJInHz1LvbdOI7lGN95GIkiCCNt02LN7D/XWBv2gx45dB3j8mYeod5fQMsKwLZASU0hcp4BpCbZrqyRxQpJESCMhSQTSMBFZY0oPV8Zptxq4joVtZdjc3sSwBJWhUSLVYbO6Rik3QylTpNdtknVHsV2LhbWzlOQQP3DvT6Ckw+lrZ4l1Qj5bppAtYCQm3W2fm2+b4v/zqx/l9CtLfPKPv0W1usXNNx9jfWuBXftm0E7Ec089j8MQ1eoqm+2rxFafTr9Orx+kRSdHYuJQzI7j5TJgB4RxlyjqUq2tI9J2PElyHZplp61rIW8ANLVOd3WU9DFNSdbJ0Oxu0+k1kYbEsZ10ZwwwBZoB+kcPqu4Do1ApDoQ4CTGkwJQOU+VdlPPTVLdqhKqLsCRJFNLuNjDNDMOFaTJGAUN45O0iH/7Bd/GWd93FmVMX+eKnvoMMxolDn13z47zrB25hdDjLkw9f5cSpC6wHK1xdOU8U9dixe4atjWVqrSqWbZLL5wiDPvXWOmHcwY8iioUK2UyZIGxhWnm2assUc8N0e1sEcRWVmDhODssxEUPeHj05tpMkism4Nt1uQkiHRnONOHAoDRWJky468kiSCNOQ5DNlHNdgYfUStmVSsndz5y334TkVVlaq9PohKMWeuX3smCvw4R+5g1Yr5JP/6VucPnOVWnudmw7t5SMffh+loRz/1+/+IY1aB8syEFbE0tZ5at01bM/Dki6OYeG5Ocq5ERw3A57PYvU89cYW/V4Xx3PJejniMCRWMUiBIey0cS1AJymCSWtBGPZJdIxluuSdMr1+n05vm0T4IBWmkeIZlVKD93ADsZseCxphCJJEk8QRSvugNbbhcnT3fVSyY2xubdDudej3mkQqJBaaKPRxzQKV/CzFbAEdRUyP7OEf/9wvMDwi+PLnXmBzU7G5sYwn8nzgI4d534eP8u2/vMzXv3WCy9dOMb7DY6W5yuWFV4jpohQkUYiU4LgWSI3t2Gg0hs7R6W0yNbWfhZUzuLZHECSEqo5hODiOQxD2EVOlo1rEFnmnzOjwKBERa7UlchkHv6Pp9/oo2piywMjQHNlMhXZvg4QeW81VwqSLocqUvSn2Tu/ltiPvpNuJ6DS6lCs2P/GzdxMEMQ9/4yLVtZBzl5+jMOqxZ/cMfqfPhdOXaTX6jExMcXnlNCuNi/SjOoYpyWcr5NwicRAxPbaTnTt30NWbfO/4g2xWV7ANC9O0yGRyaC0whDHYqenCiUExS2tBrNIcXxOilI0KbY7uuZV3v/Wd/Jf/+mnW2qdQRoCQaTqltRj8/AC+rUl7BdLAMCSxigkDH02EEKC0JmtVuOPAm5mb2Eu9UefqtSt0ej1Mx2R7a5UQyOWHcR2NjCP2Tx6jkp3hzffdx513HmF1Y4tP/slDTBan+OiPvgnH01w72+bhR0+Tydpstq7wnRe/hfDSIxKRQKKIdUSsQoRpgBFjGhrHGKLV2WZ8ZIZuVKPZbDA5Nkez18YwDVqNtbSxNFO5VatQMF6aYWZ8L5dXTxKqgEJ2iNGhCt1GhB80sWwHz83SDdusbl5lbGyCbuCztrmMZWZwpIeJZGb0IEf3v4nZqUl+4CMHyBc8Pv+ZJ3n6sXPccfst3HL7Tlq9Bl/44l9y6fwVMmaJA/OHObtwnHNLL6KNPhkng2Nm0InJ+NgEM1PT9Hs91psrnFt9hu32OhmngMTAcz00AsMwcZ0cUppIKUiSGJUkSGmgtSYcFE8MaaBDm2F3D//8l38VL+Pxub/4Jk++8kVa8Sax6KQgVaVJVHyjSASCQr6QwsKDfhoMDn5namlpxuAwwri3m+nxXeyc3U3fT1hd2WZ+5z4anRWePf8dOlEdQ9nsnttNr61wGeamg/v5+E/8NEvXqnztO9/GdQ3y0TS3HbiNO94+wZc+d5yHn3iSregqgaqh8emFDRJ8YvpEKsCwbDA03W6T0tAE9dYGtraQJowM76TTaNFLtlBJjIp6JGhM23QJ47S33PNrOLYLkSDq99lYXUUkecYnxumrbc5deRZMQaPTpN6rYRoOluFSyFVod+oYtk2z1+Lk2Rd57wd/gspohocfPMlDDz5MbbvDXffuwjJi+tWIraUqBg4HDh7l+KvPcGXjZYSdkLWLZIwsI+UxyuUhWu0G58+fpRd12PCvsd1dw7TMQdSuU9Cl1mSzOaIoxHGM9IzWBtIAhIlWSQpUwUIoF0PafOjdf5czp87xhW9+honh3dx97G08+dJjNII1zIwgET5JEqJVitBJySyKMOoTxwE3ENBI0CBQaAkxAdIxSRKXM6cWMAzJ3PQObOlx5eo1orCLEBDoDi9feY6iVyHvtHnwsTOodoUPf+Ad7N4zwfe+cwK77zM/N4Nt7GBiZJJydpLQDwkTG9MKWatHdFQn5RZoRRSHuI53o8AlTYWMLMpOgYKuIA2PZneJUAdYwsIQGnFw/O06k82jk5i+XydWFgYGvXYD27Q5fORWrqyd4NLiWWJiLCuHEA6GqbAwyFrDmNIjjhSem6Xk7uSnf+qjHDo8wSf+3SfJZ8scOXQbwmziZUyWzgTU1gI26ktIN2FxZYmrm69guzGl3CSeWWC4UmB0fIyLFy+SL7pURkpUuxs8+cpD+KoO2sCU9qCEPUDLSolrebhOHtfJYNk2Ak2cQKIDDGzy1jTTozu46dAtXL60yMtnH6UZLBN2Fffc9m7mZvbx1HOPstlcwGcbP2ohhUAlikTHJEmEMeAEJOo6HEsMwLAGSkSgJUV3BzsqtzKe3UGU9NmqLmGaBnbBptpYp+1v4sebxEmPRHvkvVkyUjGWm2OktJPDB/dyYNchetsO+YxFvd7j2PxdPPXkCZ4+8RL16AqNYBFftmn0F1AiINJd4iROoZkihYznXJdb9r+Zrc0NMlaOTC7DixcfJSLBtWziyEfms3k6rSa9oIPCIIi6AFQqo7zhrjvRTp8TV58ilhrbzGJIjS1NDGVgSgfTcClkC+Qzw9gMcdOheW46coA//o9f5vTpS5w6e4LRKY9bbz+EY5RY3dpko3cFo9jj5YuPsNg4iZs3KLojuEmJw/tvpjI0zMsnX2Lf/B527t5NtbFFs7dBL9jGFBLTkAMUjAYRpzBvQ2CYMiVTCJ0eAUph2wamJTGNDEPeOB//oY8zVZnh9IUniZwGiQyI3RZPvvw9wn6ff/wzv8JEaSc6TFvhKZTcQAoDw7AwpIllOTfg8IPTgUw2h2XYQEwrWKWnNljeWKLf1+ybv5l8dpyklWHH8M2U3AksVcYzhzAtg3qwSK1f42rtDM8vfIfHTz/MVm+B977/Nja3Ojzw0Dd48YUXOLJ3L/tm5nGNYRJskDauWUibXMgbdLtExdiWzdzUbqq1TdabK5xefoETV54iIULqhDjqoXWMKbSg3e3g5hwKuTyOlWWkPISXy3Bt7Srnr76ELTKUvCGiSKGSHqatMcwsUptIMowM7WK4uJNiPsv73vVGvvql73D+7AqGozh82yzPH/8ej3/PpLrRYbtVxc7YnHjxKSLdJZMpYBslJoZ2Mzo6ysWFM2RyHrfd9gbOn7vA0uoSH/rY2/mLB55AYqASgRwQQNCKKE6wLBfXyWIImzhWCBEihMC2bYI4Sqt4iWZ65yjPHH+O46dPoO0+Ku6nbVSdYNp9vvnwl2hsbzI0nOXqVoxAo1WKvZcYIMSNbMAwXsPpK5XQ67UGhRUTpQLW65e4e/4IZ08tsLJ1kYO7jlDKD3Nt+SqTIwcp5UfYrC2gknUiWScKephCIqXP8tIltrY6fP7rX2ZpbZtsbpb17S0mxqoMjxUpVSdpJzWqwRlsxyOIMyQ6xpCCWEUIrbAtm43tGu1WI61ryJiu30OIBAa4LkPaiKPT79WdoImbdciYBRyZA9nn4rXTdPwWSnYRSGwrjxiQG5UO8dxhStlR8pkR8vYOdk7v4ed+4QOcOnmSP/mjL+F6OSZ2WBx7w1EefvBJ1pfr5HN5hBtx9uIZEhrYlo1Bjt0Th9g5tZcrCxeojJawXZdXT59mo77FG9/8BhKrzl9+57OUcmP4QRs/6mAa5iAyT9G+juNiGGZ6PJgmjmOnOX8ckiRgG3mmxnbS70IUtej0FzEMg7bfodtrYksP2/CIQ0W+mCdQPYKoh1YRSTKoB0gxaBQlJEmcIp+FTtk7CNAWIuW7kiQRdx34EC7TnDn7KgDjwxOMj82xtdFicmKYRNU5ffkxuqJGGAeoOMYyDBzpsWf8blpbET/2Iz/Koak7eP6lU5w6/RLzM7ciGeHsleMsdV+mY6wRqA6t3ipKBKATYgIMw0XFIESMEBrTsIiiAGko4iREoTGkjezrLTrhJpu1VTrtBmND4/i9gESFOBkDaUqEkVq1ZRpIkcWxSiRR2q+2pEniR+zeMYJnuzz9+FmkNDhwcJbDhw9w6fxSihjqVvHFFifPP06omzi2i02eAzuPMTM5x6lzZxifmKG+HfHKSxeIQ4OpiWl27Bnj4Se+iW1ksUwb0FiGCaRFHinlgKcXEkXRgCeXEEYBsYqI4wi0wrCg7zeQskmUbNIPmpi2hTBMtIIo6hPQRXsBnahFohIcy00RzkKkrCOdvI4BdR15PegXoIAUmCkxsIwcZ6+cYWpykqI7jmeX2Nhe5+zF02RyNpevXAZtc+zAu8jpMUwhECZEcUQvaXKtepyRqWl6fZNI1Vjb3ESJLNtbARmzwM6xg1S8FMCqVYIpU3ymJVwsshjaxbWzSGGBtpA6ZUuhTMBGChutNOa1tVeJlcSz8nQTi5mJaYKwS7W9TqO3jtRpic2QEpUkYHQol/ZSysyhI4ktsuzatZ+77ryD+7/yHH7XINE17rx3P0tLLV4+/gqLaxcZGx/lyvKrKCIK7jhEkrmpvYyVxzl+6mW8UpEXTx3HSjzyxVFarRpveevd1Ftn6fjr2MYwnU6TRHdvtGoR6cNPVEQUp42eKNJEUYgxoIRJJOXyELlsSsqMQp9+2EFryGWzKKFptzdTzEAksISXsnClQmh5A3efIoeSQbonBrV0xY1qE4CIU36CypDPjdNst4mCPrcdegNPH3+BSjZHJ9ji2vKrlIplTl88ye033c5dR9/L4y/fjzS38VWfSEE37HB17XGa315kce6t7JieY+/0IbSfodVsEsQRppnDlRWi0Mc28oSJSDue2sDQNgYGyJSin6g+WgkMy8XUGmRMFPSQSidIkWAZkm7o8/wrj1Otr5MrZ4i1QoiUVWObWfLFMkIl9Lt9pif2cWjffeybewNvuvdennv+JC88d4J8Ic/tdxxleW2Fq0tXWFy7QK7gslZdIYgV+eIQGSvPdGUGx/V49qUXiZVme32bjJlhqDyGVDkmx3Zx15238MqJV3DNYaaH5/Acd0D9Smv+r13pAiQqIow6xEmfOI6QQlIuDeM5WdCSKIzoBT5+FIE0EYNMQmmFNByixAciEIpEgx/7aJFW/pDXWdApIvrGXxaDpoowBq/olKMQJeRliavXLvPWdx9hZnQWV09Q8kaQpkG1voHnWTz/yhPoJODmHW/FCF2yVh5DOPSSDtXwKlvBVZZaZzh54TGanWWE9FlvXkTZfWbKu9lRPkAxOwbKwyCDKRxMwyNrlRjKTuCaeZRKCJOYGEWkfBIdkSQapMC0zSJKKbKZErNTu/FbXXq9LvVoGzeTJQpjlFaEGowowDFL5DNDdFodCNu8601vw7I0Dzz0IFIq3n3rPUhnmt//j79DmHSRJjQ7dVrdBqZlE/YiRoouuYrD2UunyLoTWNIgn7MoZit41hT9usU737SHqfECWbWH23fvIVNMePb4w5jSJkpCRJp8Y5n2jaDsOrU7JajY2HaWIEzwvPRMjqKAwO+QxDGu6yGkxLZd0AJDWET0iOIQYdmDpUzxA0JBcl2gQacU1OucGK3VgFp+vWEkEEIRxCEVd5ZOt82db9zDC89c46Xn1slain6SgAmh3yebL/HtV77HG2/+AHvHbuZq9QyW1SOMY0It2I6uEixHlN05yuVpZsd2MRVUsNwcne0emy0TGwdbeiRKI6VJpBOKmTKul6ferYNIMAREKk6DRFKyKTJB7pk7QM7NE6uI9c11wjhmenoXw4UxjNgia3rEYRctfEjAdUoUCxMUMhXKOZeCZ3PmlbNIZRNEPpYXoEKPSmGSKAmRlkWz28DL2CmHz8hTLJY5e/UM0pRYloFtGthGDhGUKTkTzIzNgVSESciHf+CH0GGG1ZUtojhBaAPL9BDSQAr5fTsxClUqIqEtLMslChWmZWGaBn2/i9IxSaIpFIZw7ByZTJ5sNkscxySDYtF1GJgQaYB5PdgTrzv3X3+lxjDwDEIO4hIIVYum3+Dg/CFq1YgwlliWh0WFojuCZ+UQpiAKa0DEMye+mHIXslMY2sI1C0jhECc+fVWlES4jvIjSuEOzt86JV58jEH0y2RLjhT1MFvbg6TImHiV3iKI7SrfuYygTV3pYuFiGiRTJAFWsU9S33w/odtsYNnT6LbIyCwQI4bBn8ijlUoHLi2do9Vtk3BKeWUAlkAQJ+4/sZnt7m3MXLzI7O83kzG5yWYcXTp2n1qijhMV2cwUtYwQenlWgUhzh8vI1okgwVRkjjBIircm4GYaLs+jAQhZDvvH0E4TFg9w0fytnF15Gev0U+mXm0TKhH7XTHR+nXP+YBBVrLNvGdV20Uqm6h2vT7jZJkgTP8yhXSgR+mC64LWi0u1iWJE4iUAm25ZAk4Q22c5LcUA8YuP+0BnFj0RlgBzFvACyFEMS6hRZtJsfm+NR/vZ9ra1WGR/fS3mhgiiwZu0jQ7dALu2RtG4Hgytp5piZn6KtZutE2IV38SGCYAj/e5oWzj7K1ucXc1DxWy2FhdZGDew5T3XYwkIzkJ7m0+gokMRKN44FruxDk0IGFl/HY7vTTmMZwMCyJ9LsBleIwjlkm6wxRLI7iRxGb22u0ezXqzTqGkWFqYi9Zt0I+P4QpPKSQlEplXjj+CtvtBth93vL22yiXC2xVV2m2Nul0G8RxF8e00LFF1i7Q7fZQGsYKs+Ab6CgB4aJUQr/fw7aytIIaL59/gs2NNr1+gp2JaPtbZHN5Ctny4IELDGGmZFTLRSUa0zYpFkuYpkkUx9iOhSZmq7pOt9/Fckx6QYtGewvTUZw++xJnzp5AiAG7e7DjlU4IwxAwMQ0rDfpU+pWCTMzvU0URAw8khAQx0CPQkLEd6vVtltYX2GheQkgYqsxSKcwgdQbXcMASRELhOEUiOixvXSHnFbCljWPZDMjBKCKWG2c5ufgkjc4m+3bvoZwpkQQ+hXyeydGdTA7vYqQ8SV8FLLeusVi/xHpzmRiYHttLEl4P6F1M06Lv95CGMNk9N0/eK1LOjlLITxNENvsPHiCSXZarS8TaII5MbNNhx/Q+dk/t59abDxJFfba3a8RBzLGb56lUxvnGA0+xsrJBqTSEI3NMFHbhygLl4iiGbdPr+oxkR/FMDyUgUWmEHccgdbqAVi7Etvs023U+8+W/oDJcIFZdhkqj5LwiOpE4todlGeSyORzbwZAG+XwpdeOxwpAWSRzTaGxj2zaVSoXNrTW2tzdIVJ+FxYtsVZfRxIRhhFIxhmESxyn92rJMVKJfk2F5HRHzr36f8vhTipxGD0j3EkTMi2ceodZfxDIF/aBJu9fBNCwcJ0OChSNthIJ+3MbOmPSCGtvNZTIZD5ssRadIz++iRIQ0YgLdpBEskiso5g/MsVy9wuLGIvvndyBFjGXbtINtqt1VErpo1ef2227B9fJEocYSdkrajbtYpkS6TpZWPSTyBYZ0kdphcmgnsxN72Lt3P4aUFNwyprKRhs3G2jZTkyPcfectXL64gOO4VCp57rr9NjaXWpx6ZYlWp4dpOrh2hcN778KVFbRSbFQ3QVoEccB2Z42mXyNVtDBQSlAslbEcg2vLl7EzBs+feJyXzz6BtCMSHaTlV2VRzJUhAUOYkEAcJWQyWWzLIgwjTNNCCE29UQUShoZKOK5FGPaJ4z6dThOl0j66EAmItGCkVCq/EkXBACmsbqSa19U4Ui6eHGAFXuPpp0VYidAadJKikMyAzf551mqXsQwDw9RYlma7vkIU+3huAaFdBJIk6SNiRc7N4kd9ekEf28qRN0cp5UaIRESk+ih6XF4/yfNXHmKhe5yzi8fZbq6jzDZu1qTZ8HEtA1sahKrH7l1z7N23g4uLryANiWdOYQkb4hhLOpjZfJawr1BKE4YBRtJjz459HN5xjNn5YeLep4mbNt0gQuPiOUMY0qTRTMh5ExjGJrN7JgiDhJMvncc0FcoMuLp4ASki2p0Kc9M7ubTwKqgExzWJVZ922IDEJlccxjFcisUhqq0qoU7ox100BovrV1FEtAMTx8qSKoqZOKZJH5tKcZgg6KdM4CSm3WqTyXjEKiaKYiqVEp1undW1FYrFIn7QIoqDNHAj7e+/tps1cRIiVNpaVipCazAwsCxn4CUUhpEyoOOBdJwYpIBaywECOUUjG1LQ6m0TKJ9sCFNlA41PJuuxVfMJRB8nm8E2c4RxG4VPnIDn5Am1ptNtkSllcK0StmXRWK8TJiHoDp2ozrnVE3RHe2RHLVxD8PzLz7BjfD+mylDOzFDvrdKJ67z73e/i2rWrtKIliu4YleI0240eURiBspHrWytIGybGJ5kYn6BcqpD0FZurGxw4vI+/8xMfI1IxPd9ntDDGvtndHJnfx+mXryLJsHf/DH/nJ96FtDQvvfQq3aDB1dWXSWSXQmGE9Y01pDDJWgVKTgkLCykNLCtHIT+KZ5fIZ4skKmGjtk6PJr2kRqza9OM6ie7R6XaYmppCyDSCldpjemI3+dwQQagQ0iCJI1CaKAyJw5BMxsW2Tfr9Pkkcsrq2SN/vpnIGXJe2YVDQuU4VS7V+kiQaQMsU8cAzZLN5PC9DkmjiOBloB4IhrbSqpjVaS6R2sGQGx/UI4zRd7YRb+Gwg7BYIwez0XrLOMDqRmIaNZdhY0kVrSSwicl4OW9j4YR+sGL/Xo5wpkqiAKOnQ7tVZqS6x3V5jZLxAO9zkwqXzlEoFCl4W1cuiE4t733Avu3ZP8dgT30ZIiTQF1dZlulEdN1NEC4Vs97dZWblCs1kn7Cgmh8axjAxBqPncZz7HtZVzzOwbx7VdpoZ2cvutR5ibK+P3+iwsnaVYzGIoh2vnttm7ez9BFNANmxTzRYYqk1iZDCsbV1FaY9pF/DgkjGJsPDwjSxjE+L2I0fIkk8P78MM+frxNEPdQOhVz0lqQdSoUMkNU8jNUCuNIabK8vJyCHGUahNlOmgHkCgXa7SZrayv4fo9+0EGp6LXEbVDISQM3PUjt0qBODMAdcRwQxT6JiomikDiOcZyUTKIV6FhjCQPHyGDJDJoYA8g7w4wWZxkbmkThp7EACQvrlzFdDx1q8t44u3ccxpIZLCODI0q4Ript5/d7BKGPZXt0/Tbt7gaoBM/2EAISHaOVj1Idev0G/aTGWuMSgU5QZsKxm48xnJklYxf40b/7MR546EGanRaWcIniJG0b49MK1uiE20jDNtBWSNdv4LpZpHZxrSL57AinXj7H5z73SW678wAjw0VM6eF5aTv02O27mdvlkHFs1q5oXnnhEpvVS3TDdRy7SKOxTbV+BYyIreYmykwQTkKgfCzTIueUca0UymXbJcYrexktTqe9BSL8OBgokhhY0mEkO8vhnW9hdnI/kY5Z2bhGnLTQIqbbS1vY2WyefL4IA/fe63dJkmiA6nmN9fPav/8tzvzg/wcEkbSMGtD32/h+n0wmT6lUIZsrECsD186jtQEDWJhtZbjzDfeR80oDg0qQMqTZXcNyLPbuOUyvYdDYChkqTFP0Rinlxsl4QwhhDxpcEQg9UBlrodGEQUzGLZIkJrFOCSuN1iZOVlMadlGizdbWBrfefBDPLHD0yE1cuXKNx594nLw7hiOLGAIsI4tpeERJA02IjJKIOImxzBxepkA3SNEucQiGzHH58gKr61c5cHgviQiY3lGk3QoIunD3Xbdy263zbK5t0m632ayts7Z5hUJ2hHxmiEzWYrO+gumY+HGfemeThBApLaTwsESBfTuOMFyeY/FSA1s6QIJhpVp+glSPBy0J2gmH992CViGbtTVC3UbJED/oUSoWQUOnk8YArVbjRuGHGzv89dj+65W7NFrX+m+XSorigCjq0/e7RFGINKBULlEulfHjNobtA3FqjP0W991z36BxRVq6xkST0Ois4zoWlfw0WXuCufGjTA0dIGdNYeAhJEjDIlFpq9s2HaIkIE4CpGGR9YogBEHcxY98ekGPMIqYnBmj1l3g/LXzOAWY2lli94ExvvrA5+kHDTyryPTQPKa0UYmNKbJIHEyZQQ6XR7DIMVKepNls0A87DI+NEquYcnmYXK7MNx66n9k9oyhvjWzRZXFhi5dfOEej3sSxba5cvkyttUYuN4zjZJFGyOT4bnLeEO3uFradiksFfg8pBFEcoxXMTe1l345jxC0DxyoyNFZAyzCVVsVAYGJZJgjF+vY6h2+eYGwij0okrueSKJidmaNcriANEFJx6dJ5Ot0GSoeDNu3167XCTVq7T89uSOlhr6mevV748rUrVefo0fcb9Hod6ttNpid3sXfXAdAylczTCZ7r0e+ErK9sAmaaxGsDQ7pcWz2DEh1sy0KoDK1Wk5npMbJWASKTrJvFcwqpoSpBKV9Oqesy5TH4QQ/TGmgEigSkwPf7TE1PoJweZ5df5KXLz7L39gLNeI2rq+cwDBtbZNgxOU/smySRwrWzuEYFmyxycmyUkaEJVBIRR3U0CWEEyBhh+uSKDmcunGBp8xxju2yeeOY4l89uolSf0dEhuk2LfH4YhOTc5ZNoGeOHdVqtOr1+E6HT4ExKiSFtTJkljhTFUp7R0TGqG00mK7NMjI5hZyXCiDAxsAwHjR64cIVpmWw317nvzXfhGlkSXzAyPIFp2WitGBsfpe936PTrJCoAXlv864HfdeFltMA0LCzTw5TOgCP4ek/wVxtN6XuVSvCDNnHiE0Uxc1N7uOXIPWSMIQztYsgsY8MzXDyzCJGdIgZFmmFkMg4tf5312kWkEWNIm+WlVfJ5Bydfx8vaaFVAIxBG2rpNEg06lX2xLJMoitKupEoL05Yh2aqu0u00KZZt6v0FHn7+K0wd9Li6coFOr4HnFtDKwlQZJkd2khCRRDFGYjFSGUbWajXGJ0fo9tuoJMKzc7TbHdY2VlNCQclDiZiHvvMNDt4yz6e/8km2Wy127dmD1rC4sEGY9PCyWZTRQZOqbWbKWRbWLlMojiAMSRz3UrCEMNGGTRDHnDh9msXVdeyMw+xMGT9cZ33rCtlMljD0EYYmThJMaeHYHp/+879ESo+JsREO7buJ6Yk5pqYmyWQdVteW6fY7xOq6oNXrllCIG+lemq4ZmKZNIV/B83KvGcZ1kCfiRjB4nVk8MCGSJKHba9ELG5w4/Ry9XgvHzjE6upt948eYyO/myvIS2rBSYgkJiU4wTRPTUlxYepahUZuMlWW0Ms3Tz73MmcuXsPMgDU2swlRoS9q4VgbbdOj5XaSUmNLGsrxUHyhJ8AOfza0Nzpw7jed4BKrG0dt2Uxn1eOq5RzBNi3KlTKaQp1FvQmSg0ERhQDE/xC1Hb0U26n26YYtCOYvnFcnmi5i2IOOl6NmrVxdxrAznzl9gc2uV9330Ds5sPIZTilhZaXD61fNcW7jG0to5Yh2Ry5aIwrT75nglZqb3EscJWkPGLaGVgSElrV6danOJTthgfXsLz5O0+hfZql+lUCwQ6yjVzANM2wUz5uKVCzQaLf7Xf/bzvPVNb2HPrj00mg1eeuV5/KgziBsGIE3x2mK+ZggSx8pimR5xlAZstu2k3skwb7CFU5GMG85/4BH0IDBMgSFSRFxbO88jT3yHHTt2sWf2CO9923uZmhjmlQsvoMyUaKoHWUAc+xSyIzT7W3SSdaanKjhWhdXtRXqiwaWrpyjl8mTdIkoJHMvFNu0UsCJjwjiVnBUileLTQmOYAkxFlPSwHI9sweEjH/0An/3cZ2l1qxSKObyMS729TrO/hWWYGMpFaYMjR25mcXEVmXEKbG2us2v/LLGOaHWqhEkbQ2gc08YyLSzTxHUt/uN/+A/c98Y72Qpe5tTSQ7j5HJbrEiU9qq1Fqs01kIpCvkTod8hnihjCAhVjiCymzlPKTLBn8hby5gSGcslYWTzHo9lf49nTj5KruGQ9l+QGzEohZUKtvcjy9jm+9cRXeOt7b2Pf/E4uXTrPK6+8SJyExHHIde7e9Z2cLqi48SUGy5HN5LAMk3a7nRZ7jFRxK5Vhfb0QprhxNPzVQFHpBCEU261VFhbPsn/3ND/7yz+CrKRCGZ5t3hCaSIPqmEp+ik7QY2H7NG6px8b2y2QzHhmrgiNLDOWmGfLGyToVkkhgS5dctpIidwybnFtGRSI9HhNFkgQIEdHu19iqLfODH/wgZ86e54GHvkHGdSgVC3TbXRLVpdXboJQrIbTJkfmbQWhevXgS6Zkuyld0Og2m58ZYWbuMHzZptuuMVIYRClzHIUkClhau8p37H+fn/9Hf48UzT3D87NOcvvg41eYCSgaYrkW738K2TLQKGKkMY5CyczNOHkmCbcV4boE4cDGMEo5TZn5+iNn9gstbZxmeHEKTCjagFDpJMAxNs7dJIOsMz2Tpa58vfOVznDh1HEU8YAAN8nhSyTStxQ0U7/VF0EAYp0MdUuRwSBT7KBUTx1Hq6oUa7HRxI4KXwuT7g8iBYSBAhFTb1/je019nZW2RoaFhcjkPYaZMZDRIIYijhHJ+lEA0OXHxe2xsrzM9Mcsdh97PaHaWnJtHonENA8dwmRzbgSFzSFLuRRILRoamKOVGyLlFUIIkjogin9Wta+TKBm9757v5L3/2GXphj3wpTxgE1Ks1wqBPQsDU+DjD3igjlTFeOv48QkRI28pQzk9w/uxF7Jxg5+xOarV11psrbGw1UUmCEjFCCgzL4jNf+Dyzc7vYc3gXf/zZ32Kh9gpLjQu0+3UKmTwTQ3P0ej02t9do9apcvHYaR7rMTswzv/cWVCRYWVmlVKnguHmydgGbLJeWF+lHfYbyo6w1tgYGECG0wJCCKOgwMTZOqTLCb/z6v+HZp18kJiFKghu9+tRNp1LuAolS4Dp5TNMeuHIDIW3iOCEIQ4KkR6/XSgdVvE4x53qNXwqJadoDXOD1KMAaLHwKF9NK4ccdtrZX+Je//ptsbNaZGJ1AiwDTTDUKEJJINzEsiedp6sEKE6Nl7jx8H2OZaUruJD0/YK2a0sf8XoiKIhqtBnEUMVIaIecVkKYFGJimizQyCNMmkQmh8vnd3/89ep0aFy6cxvEMstkszXodx7BRWqBlSLnicvttN7G6dZVOr5lWMR0zhynyuGaWC+dPs+fAFEIqkkRh2RmKpVHCSOF6HnGi2Kpu8K9/67f4pV/6x4zN5Dm/dJy6v0Kjv0EQt4njmEIhj+dmqTda9CIfy7Qpe2X8doLvh/i9Bvvnprnn2DFGyhmCwODUqUtkrQKuk+PawiVAkCQKwzSJooSR0WlmZnbywrOv8PxTL6OkoBc2EBKUFq8L/NLdKYQYaP1rcpkKpszhmFkcy8MwrVRFRMcoPWj6XBe81oNZIlrjOBnQRtozeJ0fkVogtSKFj4GhM3T8mKur13j8iUcIW11KuXyKJRAGDOBi3d4qI+UpWn6Dmn+RbL5B0OkyXJolnx3CNvMMFcYpZocpFkcYH5qmnB9HYpDogESHA1BLmGIWpabZ2+Kf/pN/zvjYFL/+6/8cZBfbgSCICPyEjFdMPVii2Tk3i2nEnL38Ilm3gNQWEm3gOgXy3hDbW1Vq7TUqozmE1sSRwrWL+P1BXVz1sJyEF158kf/0R5/kV/7pr6LMgFpvA2ErQtVnc3sZIWF6aprxkQmybhGEhyvLeLZFL66hLZ+t+hK2bTB/cBKv0GVl8zxT01N0ey2a/fVU619aSJGqdleGhoijkEvnL2KSoddycfQYlrYHDRgzhWVjI4WDYaSEDpQga5WZHt2LaWQwDRPTGCih6eR13L/vP/cNkcGUOQT2oEZw3ThS168RaGEgqFDQu8npObq9BMezWa2uUCqVGClNo7U5eL/Jdv0qo5UpQmLWm68yf/sQIV3yXo77br2bilui22jiOQb1VpXRkQp516XdatBsNrAsA9c1iFVaeGr3tjmw72amJnfw8b//CzSbabZQKhXZ2tyiWBimXBwlTiL6kc9mp87pa2cIVIJQDp6dQ4ZxCqeeHNuJaxe4sHiRamuNJPbptLrkMiUMUn6d47h0ek28jMvnPv85xsfH+dNP/il+3CGIe0iZIKTPVnWdWq2K61iUsjna/Sr9pE0+O0IxO4VpZrm6ss2FS3WSrk1MjUZ7g5mZeS5ePkmKSNJpsKM1o6PjlHMV+p0WhgxY3DjL0X03cWTkvZTFEQyRQ0oPKWwENmgTQzpIaeE6HgYOc9N7yLgeiUoGCuevA3HciPYBYqS08JwxUHkYxAASEwMzJYikJoJBiYzexU2jb+O2vffQ6bVod+uUywVq2w3ecu97kNgILQGLRrtKr9slLwtcuHiei+er+IHPysoGm8sBI4Xd7Jy+mSR26fqaQnaE0eIUe3fexO6dh9na3KC6vUYSh/TDNrccvZNP/M4f8vDD3+O5Fx/HsgTZbJ4wSAjDHvlckb4fEaoWXj7h8sYFLq9fxjNK2HgIZSEhoNOrUS6PkstO0Gn1EaZAyQStI2bHduK6NlGUYJtZkkTjBx36/Sb/4B98nEzG4Td/438jUT6xCjBdg67fYL26zPrGBjOjBynlSyxXL5Joi6w9SiaTSz1DXxKFMbXWKtliDkXAwvopDCEwTRcNFAolRkfHWLiyQBSFbNVW2WhcZmHzZW65+VZ2Db8JR1VwrQKWmcMQRkrnGiCGLOlRyJYpZsvM7z2CJV2icMAXQKX6QdejdRGDkHhOBdfIoyKVIo0GHT+EgZKAMJAiQ0HMsK98hGM33clS7Tx+VGdzewkva7C5sUVzu8W+yVvIezkEgnavx1ZjlaxToFZvcenCErMzk3hZi2tr61xbWaK60WCkPMXhfTczNbGbYn4czxqh1wkAhe1Y1Ns1pid38MM//KN869vf4lsP34/n2ARJC8uWVKs1BCaO5RFEARBx9x1vpuV38P0eQ+5OLDNLP6kjU+aspLa9SSk/jgpMRkZGaPg1Gr0tRGRgSpMwDBHSwPOy9P0uUsLVpSv8k3/yy7zt7e/k1/7pP6fR2aIXNEEqDE8QKZ9KeYj3vPWjuE6B4ZEiNx84jCtLlLOjTI5P4+Q9Xr1yhlypwOLKhZTmLA08J4NGY9sute0q2YJHu1tju72BIQ1WG2f46tOfoDItmR3ZiUcR27BB6HQ8jbLI2GXKhTFUotnarKX6PW5lUJqVqCRO5+4wEIfSAoMsNhVM5eEKl4yVA0yUdlDSQQCGzGAyyqi3g5nZIb743H/i/NaL6cg7HbO6uUwm53Hy1EvkMxUcK4cQMWHUJ9Q+CX2CuM+19csYjgFGgpd1KA2VmJ/fyz133YFnmGS8LJXhIVzXwbIhV3Dp9XscOnSIf/d/fYLado3f+/f/ligOCMMQy7bodHqQOGTNAlnGiPqSqdE5Dh09xOXLZ8mLIqaUJIZPrANMx3HQmFy6fIG5HfsYKU1TyJTAVDT6NVxnL3lvhEanAYBtuVimQz/okHE8zl+4xK//89/gD/7g98jlLf7Xf/ZPGSnkyOSKdFttmt0NhqIyK6up277j5rciwhLV7YROv8fCxhW6SQPcPisblxCmQmlNEPgMlYdJohBfaQzbY2N7GSESlEr1fKrdZR4/8xe86egPM9lpcnntBA3fJFERhUwJgY0hJKVCHikFoR9SLo7Q7TdR0qTXa6QFpwGwA1xsI4+pHWTikneLhElAFK9gmG20jrB1jhwzjA3PMTYxwlOXvsZW9wpSqjQlFRZ+2KfZ2aKUG6LV22B0ZJxqa4FYx8QqJKBBJpNhYf0qI8V5so7L7YdvZf7AXmTW51vf/Ty1xga5vEOofbYbG3R6NarNBXbv2s2f/PF/puf3+MpXvzDASAhc12NkeJzN9RYZdxgXzWRxP93GRW69czfVziprq9cYye6j7W8QiRZZu4BsturEOiRbyOFloN2u0esG7Ns9T6S7JDIEZSKEQRgGRGGMbbsYhiCMA7yMxfce+Q6/8S9/g/e+74P82R9/ilD5bNe2cRyba6vn+MqDf0wgNljZXOLSwkUq5RI7J6bYuaNMX6xhF2PWapcJ4jqamHSupEHGyaKTGDdrsrx+hSgJBgEYKJUygTv9TR5/6QFKQyWOHXgLOypH2TN5GNctUshVmB7dwczETsLAp7q1htACz8kS+OlZL0SaWoFJxinhWNlU+SMBW2QwKZCzKrg6Q14XKZk7OLbvLRzce5DjF59iq7+EcQMImpIFhDDYbq6RmD1q3VTJa9/u2wmThCBqE6uAiDadYBOMBkcP7+fWo7dy/vwpvvGtrxHGIbEO2GwtcW3tIn7Sptba5OZbj/Lxj/8s3/nWd/nFX/xFrixcTKeJCEmpWKJaraI0uI6LwGNlYwErE3Lo4CFeOv4CftLB8jTFYYdu3KIbdpG12hbb2xs4Gc21lVc4dHQSaWnmZmbI5iTPvPIISsZImTZmwijCNAxcJ4PWmr7fQRgRn//C5/jMZ77AD374I/zZJ/+E6alRoqBHx6/TS5rEhsnltQUefPwLRDQZH3GZny+irDX6SY2FpXM4jsC2HUBSKY8Q9CIs2yEIe7Q6dYRMy7SCdFqJSAwM4dBPGjzw+INk3SHedNu7ObzrdnZMHmR8aAcTY3spF2Zw7SJxHFHf3sI00+xCa5AizRqksCExUCrtDLqum9bfDYFUggKzzGXu5iPv/jh7DhzgsWcehUDiyBFMMYQlSkhtcn2AhkKxvL6ONhIWl9e4944PsHv8MIgQaVo0+5ts9y9TnOqy9+gwJ84/z6uXnkETsbFVpdZucvriy1xduUSzV+NjP/ZRvvClz/K+972Pb37zm5w88wqu5RKEAZOTkwShT7vTxLYsgrBDrAWrzQvM7C1gWRavvnqGyckpxndkSXRIrCSR9pF7d95EzivQ7/bY3NzikWceYG5fiZ17J3jfu96Glj2SJMBzMukIOKmJ4hDTtHFdD6VilEqwbZvf/cQn+Pe//4fs3XmYj//kL3L7rfdS8oYwlIPE5vD8zcxO76Qy4jBzwKamrrGydZnN2hJh2Bnw8B2yGQ/LcfEyOVzXYWVtYZCbp3SGVAfIwh5IsGXtKfZN3MEj330Rvy2556Z38P43vYe3vfFe9u7bxZWFa6g4PTZ6fodut4djZ0CbmIbEEg6eUUArCIMulpmSRRE2JXecucIhbpm+l5/+0V9ksrSLh7/6DHsnbiNnz2KpYYa9PRiiMPAkcH1uYhh26PfbhH5M7Af8wLs/hIWN7Ug64TZdtcXx80+ztHGWu+/exd/92MeYm9iJZVooYoqlIaZnZrjvvnv5mb/3M/Rbil/91X/Gsy8+Q9bOEEQBE6PTxImiVk+VzgwBQT/FLhTLBX75l36Zte1FemEXw7RYWFui1exScSbIWC7yPW/7EEZoI2OHkeEhtqqb/O4f/Db/5VOfYHp2jEce/xbvfOfb6HW7BGEP0xCEfoDvh5jSJZ8dAp0eESqJ+Z1P/C6///v/kcceewLD0uzasYOb5u9iqDCKKy1uPfxWeuE2b/ngDpYar3J18wqNdhXDTOf2xbFiuDJOv91DE1Gvb6akjevTSMSgHKMVnj2EY2ZxmWLYPsD/8rG/y6OPPsHJZ87wwQ++nf/lH/4ArtB0Gm2q7XU6/RZaCsIkIIwiLMNCRRGWlIM+TyoXmyQRie7RbW9xaM9O/sU/+1V+/lf+Pq16wFc+/SA//bEf45Zdb8WmTDk3hmWl6aUe6AMIIdMehtD0gw6ODWfPv8TePbsp5Ebx/QZKhAQEnDj/CqUxwfy+aTpbESsLq+TzLlpHZDM283tnqW9u8ZUvfp1f/IVf5vN/+Rks26AX9imXhskXSmxuVAee0yBRmnbQZHpkjHfd/SNsrQY8/dIT9MM29e0qGXOIJJCUMxVcMYpcWl5k1+zNZJw8K8vrlPNTRGHM+Yun+c//+c946aUX+cTv/Rt+7dd+hUI+h5QiJV6EIVGS4DpZyuURojDGtA0arRoPPPgApm3w0ssvcH7pVWTORRkWj7/0Taq1BXJykvNntrl09WUsz6fVHsDDtSabLTA5MUelUqbT3abeqt4Qeno9SENpHx07ZNw8QjbZ3tzEkYI//qNf58LZRX73X30RO8xw9MBR5nfNE/Yi4jgeADt8wrCLShSmcDENhziJ0rKtTIikT6xhpLyLfTPHuO2WHSycWuWF777Cv/+PP8/BQ9OcPHkWpSIcy6Hr10hoAVEaw+gASFBao1RIQo/TF59naf0K73znu8nlMmgdIUVEvbnO5eVLrFdbvPrqFYTUBCpmZucM0mrz8He/hh90eeTRR3ngoa/jmA79sEsuV2Byco6FheUBI1lgSg8/6PPRD/wwv/mv/ncqpVE+8xef56VXnkIlDWYmpgh7IMmDTmMf+dUH/5xWv065VMExcxTcaTJmEcfKsLC4xC/9o1/mF37uH1EqjjA8PEKr1WTAgcA0NO1uE4FkZGSEMPIRMmGjusips69w5MhNNOoNjr/yCJ32FjOjU5w/e55rV7b5/Gcf5vLViySqS7/fQytBLptn7579xAnUW3W2G5skIkFxvb17XaEjxdqFUY2MWyJUDbS3ykPfOE3GLfKFJ36DPCP8u5/7OrGfxzGG2Vs5RiU/CQlILZHSxjBzZL1xtDJJIV0gcDB0jnJmF/tnbmV2aA/3/8mL+Gst/tO3P87kwRJf+PRjVMPL+FRBR/SCOpo+iLS2IITmRvNQaIK4R9uv8bkv/1cOHNrDofmb0Aj8uI1TMPnSV7/L17/2PJ49yuzsPgLdZGH9Ii8cf4GRiWEa3SrPvfwEwkjl4HKZPDPTcywtLd0oZkVxBBh4jsvIeIWTFy9y8tqzXFh4mTAIMKTEEsVU+EpGBHGIn2wjI9Hh2tpLrG5e5OC+m9g9eTPl3FwKTtSaTL7IiZNn+M1/9VtcunIWRFpfj5MQP+iSJAn1RgPDMDl66Biem0MammsLl1hcXOTWm24n53o0axtUG2uM7SjSSda5snQWw7NZ31pD6QTbylAuV2i2t1lZW6DZqRLrMN31Wt2o7183BIUkpIMKJVmnwtX6K7hFi//we49Tr7X4rS+8n9n9w3z6j77LTXtv47Yjb2bvxE3YoohIsth4pDObLaIkQUkLQ7h45ijzs2/j9v33cd8td3D1zDKy5PKLn30H0kr4P3/tQc5uX2AjPo2b7dNoL5KwNVj817eeX5urrHSEaQoW1i7xyCPfY3xoFoFFzw+x3Sx+L8TLmsROi8tbL3LmytNcvPwKu/bsQZoWzx5/BE2fWEU4tseeXfOsr67S7XZQcSpehRbYloMf9PnDP/5Dvv3Qd1Ciy9LaVUzDplSYw1BForhHJ16h3l8gERHS83L0/R5xpGjXEmydYdfUfkyyGNJhZW2d2bk53v72t1PIVtK5dUIiJERRPCBLKLY3tmhsdch4ecKoi2XDuaunOX3+VQ4fuZViucS19Vf55nOf4sT6d9G5NkPjedrtTTKex86duxDCoN7YZn1jAT9ocQOI8d9A7woBURKgVMKBHffgWSNc2HqMS8sX+M1/8Bhf+68n+Zl//RZ+8APHeOyBJ5mYmuHgzjfx7jt+hrmRm8iZO8noMmGQzvZzKFEwJrh71/t585F38eY73szll1eY3efyE790C6ceXeUPfvURTp8/z+X6cZxsKkbZjbaIaJEKR2hery/8+itRqaDkI489im1lGMqP4WZtWp0a2Rw8f/6bfPbR3+bbz3+KVjfgyJ572Tk+z0snX0LLhFgleG6OvXsOsLy8TLvdxJDJQOc4VUVPp6JYHDtyLx963w+xvraIH/Zx7QoZa4woTFBJhCkTQtXAsi3MSnYY4QkK2WGEypL4CVlRJmMME6kuSRzSbvb42Ed/lHarzWOPP4ppp/NsEWlWnsQ+lplnfW2D4nCBUnGIRrOGY+VZ3LhKkkjm9x9l8eo1aq01FlZf4djtP8LllWt0ewHTUxPk8zlWVleo1xtEcQ8totfRN17f7Ru8khho0WfbP4fkXvZNHOXVlae5uPUI7ajGxu8s8+1vHOfDH72HO+47wpc++2Xe8v67OXLgHbzr9jfyR3/6abZ6a3RFlUQleEaen/zhH2OisI9Gv8XD332WH3zLHdz+9in+6P98gpefuszV2qtcrJ/AEl08M0fLXyUUNZJUW5TvxxL+lUunR8N6bYlqrUrey2OKNgQxtm2wuHGFre46WbvC3Yfuopg3eeDxz+DrgEQZ5DI59uyZZ3FxkVazjpSpVrGQadZhyHTGYyE3xrve/BGiqMGrZy9RyFUwhIYkZm3rCsJQuGaGIPEplwrIbtenVBwh1pKrS5dA+AwXp9g5eZgwCLEtl+deOk4Sat799h/Ac3MILTGEiyltTOmQKPCjPkJqug2fseIco5UZwijAsgQb1RVOnzrNxPgcxcwoe+f2cGB+D9eureB6FTJeljNnT9FqtdEkIKJBj9/4vj799z1PQAhFP17j2Vf/gna4wuz4Dnpqi6Xaw1xpPcsjJ0/yL3/tM1y8tER5aoo//8Jn2N6+yIGZaX7hp36Eydw+RuR+htQBfv7Hf4q3vOFeOp0G3/jKtxlzxmi2Ovybf/EQTz9ziVdWnubExrP0xDr5gkeUtGiHKyQEpKihv3ntX28E3WidC9fOUCwOsbWxTqNVJQgCjh25g5HCKDumZ4mTHo8/9y16SRdiSaUwxb49h1laWqHRaGMaqZJpGvxJNAaGyKMik/e+5X285Y338e2H7ydOEvxewHBuGL/foafqBEGASBxM4ZLz8shQBSxtbOC4JrmCxcLqVZJYkrGKSMNMwRLK4ZN/+mmqm+vcdssx4iTENNKhzSpRSOGQIAfjXjWba23K2UnGRmcIowhhRLT9dV49dwI/DLnp1ltZ315ju77B6MhQOrcPgHT6x2vTSP/beP0UZBGncGwcmskVlusvsHt0JzfvvYeImGr/Al3/Ck1rmW8ef5AzS8/TCNb58v3fpG10eOsHj/KjH34PZT3MT//IR/joR96EVoJnnjtFp+3i9xM+840HOL35DC8sPcDF1hNgtxkaGUdmAxr+In7YQwo5kKXjRoxy/ez/61cCImB1/SpeLksuVySREcvVaxiWYn7vDEvbr/Kd019jI14FJZgcnmF+50EWryzTaXZwnbRDasp0FJxhemTcCiZlbtp3Jx95/0d5/rnHOX7iLBg9HCtEJnlQbgokwcJzsoyPTyEQmLNTs/R6sLG2hmu7VMqzWGQxVZFCfoyt+jlGc3NcvrRAu9tkZGiEyvAYtWoN13QJRQfXyBEnFuATqgBH2FQ3G0xMT5NzhlhcvkYsY+rhCq6SZHMm3/7ug0Rhn0I2R7W2BULQ7qWQ7vQBvh7g8f3b68aEUgyU1ggpqPvrLDRP8I43/hDSinjl/HP04mv49TWkdElUhmzJ48r2Ze7/xncpeu/mBz54iL0Hyxy+aZrqZp9nXzzFpYWz7Dl4gKvdl1nsP0did6l1NwjpMV46xGh5mKvVBZr9ajqbQA104f42938daTQAnvSDJrXGJvl8HrSg3atx8eopckWbzeZlTDsPoWRqZA875vbz6ulTBEGII5108DUDSRwMIMZQklK+wNGbDvLl+z/Hc8+9jDAdYgUT+Wk6nYCRoTn6nSbCjDFdA2kIGs0GpmVajA7nWF1cJY5MWs06o5k+lrQYys4iYoWIcxQyw2yuLtEPIryMhxSkWnwii44NSrkRer0uEelYWA9Be6NNzisyO7qXjcYSQVBlenYXF66dY2HxEtMTU+zbdYRa/Wn6/jZR3Pk+nt7fdgkspLRIVIhWGsMQHL/8LQwbZsaOUFx1qTeWME0PrTx6voltORi2ywOPPsQd+45RGna56a1j+FshS1dqfPX+r6MKTU5sfJ1qvQaWotfbxld1xks7GBsZYXH7VdY2l5Dy+hwBi1QVILzhnf5mD5AGr3Ecsrm1jlIJh/bfxuLVFbZqa4xOHcW1h4migNmhgwznJzh/6jI61tjSQhoGhnKIdJ9IpyNkJ4YmaNVCZid2cu7MOaqtDZI4S1aWQTcx9RBKCyxcEjMm0l2WNheYnpkkDDXmtaWrjAyNkyDJuFkWV69QyOTIZTPoasK+ibtYX1/FlhIzzuCHXeqdDbJZi65fZ3p6kqVra3R7TUxpY8gMftgiDAKUVLQaDUpDw8wO7+XSap+xkXGWlteZGp/lrjvuYtfOgzz9/JMEQQ+lo++TXvnbrut6fekcvIAkSTAMg5fOfo8gTLjlyJ2cOZ9hceMciWwjhUWvlyAMD6UkX7z/YSZ3/xgiI1i7EvBfP3c/i50FIrZptJewHQs/6hDrLkOFEeZ33cLq1jmWNk+CtFAq1QkQ/Pd2/1+9b01CiNIBQSDIZYrccmSSkydPsr6xSaUwTb/jk7NLLC+skGgfy5BEsYGUKTm1F9Tx4waH9h1KIZBRl2a3htI9er0usl9kR/lmMsXDbFU3yboeYa9Ns7tFJ95EmAG1xhq9doiM8Vnduko7rCEcgXAEa9vr5DMjqEChfNi7Y55Ovc1Yfo5eJwQliaIIP+zS6frMHzxCO24SJF1yTp4hb5qcO4rhuijHoNXoo9qS0ewEnU4HA4MD+46SqITzl0/SbG+9TmzpvxNNX3+QpFwDzy0hpTX4XqClyaWl09SaDfK5CbKFDAlNYtUBGYL28eUWLyy8wEMPPEV3JcPXHniSp889B9kG7e5iqjcYh0APUxvkzGGWly5wZeUcYCOvH09CIg3QxH/9/v5aVHidYZSS03u9FpYjePnUY1iW5NCBW1hausBYZRQRFGjVGiiV4LklXHsIzx5mZHgS07boxAF3H7mP8coU1xaW0MQsb1+hR5N2rcNIZoKf/fGf5Oj0Oymb84wVdlDMTaSSd1Jh2xnCMELIENnqt9IZN3GH84vHcXKKZrtKlCjGh3bR78dMl+Y5sucuiCVCO9hGnjhKkBJW1peZnd3F/r0HCROfvt8l4xQZz8+Bb+CZORzLItY+lfI0Sd/kTffdS2W0wJkLp3j2+SfwwwGR88aDIgVoft/uuv799Z6AThtRscQyM+nrAxi3H/Y5ceYZmu01klilMHHSppVWCX6yScu4zAPPfptPf/2rfOPJBwjcLWq9qyS6h8InUX3QGsdwSGLNZnM5hZNhpu1qYb/u76be6DUhqetUs+9f/BuGIRJiHRCEbbp+h+OnnufWYzeR9wq4rkvGS6FtFXeOkjlD1ihRyI1QazSo1tf40Ns+xM0Hb+OF4y/iZm3avQ4ZJ0Ot2ibrVuiGm1xdWKa61qXojjI1vIc4CLClS94cI+cMk6CJtUYmOqAX9tEyIlY9trfXMIwEofrM75qn062xeO08d936Rg7sPYDTy2DgkcsPg07ZQy+8+Bx3HLuLseFJpB1R76zTD/vkvQpZXWDP+D3smD2I4yluO3YLu3fu5tWzJzhz/gRXF8+jCBHir6J6rxM2ufFQhbZAm2n6M0ACB2Eb1/HIZSrXHz9SaoKkRqJ9cs4IEhuJiSYmkW1iGdBMFlmNT/On9/8XtpKLVINX6esGiYBkgNqRUmJaDr7q46s+QsZonSqM5LNlMl6BOEkQcrCwmkEzKCWFvIY3vP4Zrr+mgZgw7pFozfLWRc5dOc4tR+4l8U0yeYkUFkVrhLIzhi0LtFpNev0uH33/j/L2+97Bdx77Fn2axLKP7cYEURszgYQ2oexTq6Xzj0YrQxAr/F4byzAwDSsdGBFqbOEgbcNCaUE/7CEQ5LMpeubipQuUMhNYZOi2fbY3It5wxxsYH5mg3fbRONi2h2NLltYu0ag1ue+udzE8MsPwRIWIAKUlkzO7yVRMzi2+yPhUibvuuIOFhTX8fkg/6JPoEK3D73tI6YMyB4tsvG7npw/3BuVbKBQ9+kGX4eFxLNNNO5NIItWnF/QYq8yRtXMDLH8CpNrBCR1ayXnckQ5dvUoQt5BEaN1HESFEPFAQdQmSkFjHXGcI2qZHoVCh2+0g0Gk8IAZziUWanr1mvNc/l7ihdwASLTSQkOgQ6YQ89vSDzO8/zJH9x/ByFjF9cnkH01S0Wk2kofjZn/j73HPXm/mzz/8p1zYupoM4w5hMzqHbbWNqFz+MeevtH2Uys5O44zM1NsrQuIlSkiAKSWRIL6whjFReT5rCxrFMSGJswyIIAhIRUe1uE/iKo/vvQMos9a0mX/nyQ6w1q5StcVTLSWHPUcpkOf7y83Q7Dfbu3sP84QMMj5cGgkxtHn3p82yHV3jbe97NqbNnuHDxArFKpVjS1q58netM3aUU5kDoODUIQ7oYhpfCtPX1XZQKPIVhl0ajyvj4KBCSduWg1W8jdVrlVDpACoFU7uBUiQjiFlvNC/T9LUzMFM1DMGAapQRNnSjCsEfaOBAoLRkaGqbdrhMlfRDp4mtAaAMDCzBvcAFebwRpuVYOQC0pwjhOesRJTK/vc/rsCwwND3Po4BFq/jW2/AXWa+u4ruTv/dhP8kM//MM88tS3ee7MM2QyHq7KkM8WaXV72NrDJ2aouJsys3RrCcNDJba21njiuSfBiYmNiH7QI4pSwYwoTpBJHIAOUxUrKYmimF6/i697PHX8EfbPHUKiOHflBId23oZWHruGj7AzcxQvHmN65BDDhRma7Trfefx+zl8+zuRUhZtvOcKddx5jfm4HFXuCm/a+gfPnz/HY09+j1d1kefUK17l84vsWP71SjZ5k8JqB1ha2WSLjjADujfjguoxbo7WFlDA8XCBSXYTUxInPdnMN1y6mc4PRIOwb9C+Fpu+3SAhIhI9Goa+7b21hGnkEgjhpo3WAUhGFXAkhJK1ObUD9fm0wtSYdIWdbme/7LOlxwKAdPZCT1ddZyCqdUGYYXFo4xV8+9DmEYZIpCM5vv0RxbISf/4Vf4P3v+UEeeOjrfO1bX6bijVCwhnDcIk7epd6qYVgJ7aDFrvE7CXs5FrYvcPTYEUyZxQ9D2v1NFCGGZab0eG1T8caRSiXESRpBqxjKuXGyVoXZoR2EQZ/z5y8yMz2H34nJyhHu3f92Rp1Jfuidfwddl4zkpijlhshn84Ta59UrJ3jiqSeY2zlKpiRZrJ0nVyogsfjuw98in8/heiad7uABDlQ6ritzcuNxhmiREj7lQH0rjv5/pb1nlF3Xeab57JNuvrduRVQEUMgZIEASBAmQFIMkUhQlKgdbju3s8dhWy3E8nWR3u7udum3Jlu2WZdnKwaKYCQaQIAkiZxQq57q3bg4n7z0/TpGy17jD9GCt+gGsWnUXau9z9re/732f14+Enlr8H22YtUg3YGFhBd1IRrcCJRHKpdJaJgx1MrFekNFt4QcXjTW3r+TtAlIj/vZV1BDJSCcQlUwYWpJMuo9KpQ6wVriqtSXWESJOwupCw4qOL6VF+Ji34RNv8Yne0jW9VTRKPL/F8IZBVmrjnHjzKezQJddl0D1iMb4wznef+iaf++v/RIDLjtFD9Ga3k+vqYmV5mbgwWHWK3DJyhKObHkXYMTrTcaQT4jQhn+2JMDSqkxjZSEOh4vR0D2LoZgLDMAl90EUCQ1iRhz4UbOrfSrXS4K7Dd5K0e5iZnqGnt4udt+0n39/Nzm27ef3mi4SpOoGyicUMTNnBxNgUX/jin+A50LLbuL6N2YiKt9379lEpFfH8FrqhQahFn4e+9tCsTdPEWyCnNZo3IQKf0HeJmQnabvMfPX0Rz88PPGrVJtl0L9X6Ckqzcfw6jVaDdKIPL7Tx/CZKrOX9/GBojyAKlI7+TcM0zbcFnEIopArIZrtxHR/Hbb21g37wpCsdU88hZBIZtomi6zQE/4gzuPZJbxWC0eQw+rsXeiwXCsSTOl5QQIUKSzc4eep73JzcjO16OL5LKpEglD5mQlCq1/BtUHqMDfk93LrpLr79yufY2XGED77vGNWGIpnOsj6+GXu+TjyeJpVLMl25hmcsc2PuMpoXKBKJPP29GzC1GJZukUt3UGrUaLkhB4ZvZUNihDuP7sPxA4rVMnWryFee+WvOT56mEZRpOGVKtQKedFBKsmH9egqFAp50EZogVB6+FxB4NmPXrzI7NxcVQv/IjS3Q3459gx+ck7AWDqEElh5DVybIyDYWLdY/msELhePYCCwMPUmoJIFycIIGpp7FECkQ+trrV1tz/Wpvf0Wb0AAiPKwULlI5SBWiawmUUjSaq2twyQgMGdUo0Y94q27RUYi3uAJrES2RYVWg6zFMM/FPPje6QgoWV5axzAS+GyAwWSgsg+HjekU0pTE6tI8wVFyeeJ7FyjnaTY+M0UNeG+KOrfcyW5umYN9g34FuNo5mKBdXcfwWpUKVnNHJlvXb8WwPr90mZppYCYGh8KhUCrhmE01FqdvZZA95PYdOFsexCZpt9t/TzZzXw9ePP8Xf/bdnGcxvIp3rIFhxSGBhJXLU3GiUGwYu2zYd4NrEVTLpJMoGXSRx/SrT0xN0dvagiRRKBkAYiUE1ncCXaxCntxYfwMTQTYQEQyTJ5voo1ibXIF5vWbx0pAIIkDi02i0MPdLphYQ4fhXXGSSmZ2m79eiJJviBEZQ1yqcworUS0ZsgVB5oAZq0SFjdhKFC4q3dUhQI/W3IJJqJQsMy4wRBAkfFQIuCJdTaUSfWCkBDjxMGIYFas7ZLMI04iaRFsVCl1fKRhAhd0QrbBPUKI305FosT1OxVMsk48Xg3XlvS3zNAJm3x5OkvEktm2T94D8PDG3njxUWWrtk4gU/ayDEwso2qu4IvFdl0hoYn8XHR4mSiZodQeMqm3CxjaCk2dO2kPz3CVHWMM+WT2PEVblRf4PTCM+haEGUNx036ugbRZJK42Y2mxZG6ZHJukmyml0wqj+97xK30mssnRttrUGtUiBsZBHEEFqYVR4noXiylRNcMNC2GJsw1mFMcQ0tjCBPpRZs0euJ/0Cd4CwMDkjCwo6dt7RYhhIEbVpD4JMwOBIm3r2n/GPIcOYYMdH3NK7CWliKIk7TWATph6K4NfwDeKiijYyomUsT1LDLQsEhjkoxcRFo80jUiCaWD49ajtvfa5geTZCJJtbpKrbFCqHyk9Mmnu0haHVHHdOESxeYcuh6QjGdpVyTxmIlMelxeOEdT1ik1lrm2dIJa5jLakI+XrBFoHplUB5apsbA0DrqDpScxRYK41omRNftxaJBIxmjW63iyxlJ5BtPPM5wdJN8T43TxeY7/2hcp1Rr0ZTbS29XH5g2bOX3+BKlsmrzRy1JhFsuwUErHlw7XJ8+hkcZ3mmimQBPgBZKQgLbTJJHIEyqJH4b4fsT1UYRrVXe49mZQCEL8MEQ3OojpGdJGlraWwJZrNYNaUwytGTCjLRB1/1KJThqtctR392vETCsaqIRJpAx4K10MpaOtqXl13SCQ/tswSaUsujP9xOIB5dXS2xsnUgCLt7FzujRJax2kyGLHOhBI2oFDKB3eciK/Va+8lUWsCSO61uoWmtCo1laR+OgI0vEM0lH4YZTfhAowNEUinkb5JkpBJhdjevEqgddiZN0oiVicTQObeODRI/Su76LiXGP5+CqVhk1bT0QKaBWDOJhBQFIlMHKpYRqVK/R3ddFljFKsT1HxJrHLDSzuIqMnmVmY5YF33s5nfvPnqBRKfP+7r1OsVtHjipmla2wZ2o9u+DieTWdyAKUnaLZLBG4BQ4sR+CEKHV+GgI4feiiniWlYhNIkVJH65wdnskQRqXQV0UJ5KkSPdaFEG4MYGiZStNderyamHiNUDlK6kQ8vaJFIpDCMGEFoE8oWnhcSSj2qEbQEKmrhIZSJqcWjZBR/jTyqIkJXwsjR2dHN3MolQumsuY41pPQjNxA6kaWsE6l0mmEB36jTdlZxwzoQRE0tzLcLXbEGspBKEDMS5LJ5qvUV/NBeE7pEKDjXaxASkMvl0fwsjXYVQ7dot1rkentYKo3TbJfImAMM923kr/7bf+KvPvc1/ugPv0Q5mKQxFmAF23H9JrZt0JPZxLFd2zhz82W8lqIj1ou2efsQnYkenLIgEXaQt9YjQ3BVETsxz4Gjm1k/1MErp49z7fJVku4Aq3MuX/jKf2F1tQoqzsziNRJpAx8PpesM9G4gJtIE2DiyiVIBhgaGFhVJAkEYtPFch0yyi3QsyiAwNGvttWsi1rBrupYG4oShy3z9GrONi+gJRczsRIZRx02tDWcMLbH2FhAoHOrNFUzTxNAtAulFcCcFlq5hEsOQ6UgoIdIYpNAw15pPMVAJLL2Dnvw6Zleu0fbst6d/SkZMoejwMdFUCkvLEcQclp2rrLbnccLG2hGTQqgUmohHdY2KOpoaCWJmllQyRRDauH4zuqKiCFVAy6sT0MAXTXyp6EptYvfInUjXQI8JVupTrDZWSCY7ESJgfOwyn/1X/5Gdu/bwtcf/hr/56ueoNeuM7O9haONgdOMyA1q2TVrvoyexiaGuWzDGiyd4x8MPULhpU56xSZlp8h19ZLoCbr1/I6KzzPTKGHPVm3z7G8/Qb5V5+qkT5FM9NJ0mlhXH9oq4dQ/DMCnVV9CFgWUkMbU8jqygpL/2tEWswIiz7BIqH9fzsYhj6hIvbK/1BtaYfhiYRgIkeGGTQDVohUUML0a+YwNhFdreDEJ40c8UCUw9i1Q2SvmEMiAIog6gVDpSaZG5VElMPUXoBxh6Bn3tGNAjWQ8yjHAy+WwXtutge/XIlkYMpfS3tQDREWSSMFPEYxYNd4lWUERgoIs4Ah1DT0YbXrUiGsla9qKuaQhN0WxVcINmdLMg0vZJFQVXSaEhhKTWqLG1s5OuriznZ1/FikXOpVQ8g9d2CJWNoyyefuIEyklgxnVEwyDZG+dHf/levvntf+DFpy9hOZ3YYx7pVIJjx+6gVg0wLoyfplBbZevAblQ2iWlBaekGtPvI9wzx+qnXqVVhdN1Bbtt/N8szDi4lomwciVRtNEPhuHVMI4YQJo1Wjc5sPzEjgwp93KCNJ0N0ojl+zEgjgzie8LA9G00z8fGRBBi6gVDGWsdM4fs2lmYS0xMQBoTKpuGUkErRl++nWhNUnGmk5oLSMA0LXaVx/SaCqMESybZi0fRLF4Shj2V0YOoCzYrYB4oQoQUEgYehTEw9QbNdpekX0UQiAlyGIXv37mRi4jqNpgeEZGI9pOJ91Ow5HL+CUBaWlsHQ4gRhkzBsRoWoptDEGq9Hebh+a60zAEJEeYS6SEXJ5aEXvcWkhi5SbOjeRaNRYGr5DUJRp+W6kQg0iG4YEhNhmoSxEMcJ6M33UyjPMD65xNTYPGZc8OLVJ9jatY+H79lOEPpcXn6JS5evI3qzO1WlsYKvXDLxGKlEH7fsegcHdmzn0rXzXL26TMpKc/TwO6ituFy7domlxjVaYhFfRThzP2yvzc+j89QQKZLxblSoE9LElw1C6SElJK1u1vftpFiZZLU9gZAdDHTuoOEsUmvPrw1V4mvDk7VumlQYxEDTkbiEykUqQT42QldyPS1ZYqU+TqhaGJpJJtVPs1UkVI2o3/Y27SuOYSSRQUhK6yZt9uGHAZpu0vZW8FQNQSR2DXFxwjpKbxPXuwi9JDt3jbCuv4MnnnuCuIgz0LEdTcuwXL9CO6hEVBPNwtCSBIGPVB5CKELlIDQfQ4+CqsrVRXRdIZUGUoIWgDJIxPOEoYvjNXlL9JaJ9dLfuYNKeY66N40n/LeiKdeMrRo6MaQmkb5gfdcO2n4T26mik6K/u5MPPvphVkoFCtUVFleWuT52iXq7RCLegVFrldHMkIQwaHttWu4C18ZfxbVXmJttYpAgZei0SpKFhSJlZwVXNTAsi5gZo+5UsMwsSjmEYQuEj6/atP0icSOH4zRQwo++EHhBnWJ5GlNPoclcVE3LOJaRQ1FAECCVB0ohlY5ODNOMYxBHSDNKN9djeLSouDMoKenr2IzVkWWpcRU3qNG0axiGhfStqFkjIq6fwkfK6BrnyxZ+6JEye2h5BULZQBcmltEJekjbKaAbYFnr8L2AVELj3Q++g89//vOs69hAOtZDXM8yV7iKHa4iCNFVDA2DIIzeZroZYeeFEPihw4H9t9JoeJSqC+h6mrgeIwgkQehgWtGVNQzDNb4haJpJO6wyvnwWqWzQHZB6dIXTO9CIRcot6VNuFsgk09RrJUIEt+y8k0JlhrnCOH/zjb9lcHiQibmbzBdmMIRGIplC4aEFsonrNfB8B1NPY1qSqeVzPH/mOxRa46Dq3Lb3AYSKsVi7Sj2cpqXK6KaOlBoxI0XoR+e2rsVQysKy4vhBm7pTorujH0vLRvYrIQmFS6VVIFSQS68nbmVpuisMDw+SifWAiiOIIUQMgFC6eEELXzpoRpT2aepJYqoDU7OoBktMFc/TdAuk4+swzTReGI07E/E8qDhSRU0aqTxC6aBUgKvaOLIGBIShg64liVkZfFml7ZYR6OhYEIAT1PmhTz1CvVbkwN5bueeO+6nUatxcPEMrXEDHwlRZYloWpI5ULlK0cP0GCEEoIZ8b4I47jjE9O4uhpQkDRRCAZaYxjSRh6ON69bW3RlQLGLoZUcFEFbQw4jSoCFUniJOMd6KLFK4doJOg1FqlozvJo+99F/cefoitw7fhyoDF1g1eOvMdFgoT5DN5OjId+L5D265iCF2iy0hn7qkWQoCupUBIqu2bdCV7KNtlzl46xWLtElKro2mCRrOCLpJRNaxF0CQvFBy55QirhTLj8xd5+IH34TtJ3jj9CsoXKOFhGQl0GSMMXBLJOC23Td0pMD7ZwNBTxA0IpIsS4Q/aqEoQhIoWdRwkiXgXKdmBbSdpBGVcUcdpO5gkMKxoIhd4Gt35fnQcdFPD9et4Xp1QBijCKGlcOnhBC02zEEriyzaBrEcodT2HED4tr8D7H36Y+++/mxtXJ4hp3fz9338TTffp6++jtKqjSYOYkcCXFfzQwZctFB6GFsPQU+ga/Npnfos337iA7WgkGMDUNQIa2F51bdLordVUUSPMD2z8sIVhGFHkq2agVIxMOo9UEHoeLbeOagVkOpIIqfOzn/oxdgzv47994WtU0jF6+4fwvDaB3yCX6cI0U/ieQ6MZkVF0zcAIgmAtgFGiVPCDBofU0bQYs6XLVF5dxfd8pKYQmomUikB5GIZOQk/hhyZNr8At2/dy95G7eOaJ43zhP3+B11+5xteeexwsRcJKECqJ5zZRWkgYejitZkSv1iQtr4ap+Shp4EkPcNGIEddyxIwkfujRDGsQ2oS+RI8JctlOtLaB69mksylC6RKisGQKFcZoNl0QIZqukTQ6CFwQmksYOigRonAIcND1OCpo4gc2Qpjksjkcx8V2bR596D38yI9+Ek0YZFJ5/uPf/Rm27ZDOZmg3bQJfoy/fS9spY7vRm8fULRBGFD8XOHzw/R9j1849fOkLf8/H3/Up9u7cR7VR5M++/PvYdgNdi64UQRilmgQyYF3fMDu37+WVky8iCTANi3SyF8+TtO0Ku3dtZXmpyOHb72Db1m185IPv4cqFKX7vs3/O/OI0w/1lzk6VUYaDLmPUGjWgCBhkMyk6c71UVz2Mwa5NLJZmoqdNga6J6DWGQBGixXzqXo1UqgPXLhAGa8IGAwIVQBASM2Mc3XMHn/mXv8L4+Djf+OYX+Iv/+m2efeIEu3ZvYr4wRWG1hKZ56JpEShfDlLh+lNGnpEFAiyBs0ZHsZaBriP7Bddxz9z1053rw7RAZKuqtBmfOneWFl5+nbtfxAujq6AOporxgLYI+Bb7C9WsEqgKEmJ5FMp7mwQfu44UTx2nZQSQRUwJfNlG4hNgoFRCPpfG8FkHY5ld++efYt28/1ZKL5zT5vd//fVpeBV+5tGolLD3G3t072LNnJ1/62p+TSudJpTJUylXiiQSOV+ex93+YT3zy45x46QWG+tcx0N/D6uoir7z+PK12C13E0TVJKpVg/cgQpqmzb+9+fv7nf4Xf++wf4PkacTNLKp7CbtVpeg6/+LM/jeOWePe7H+bQwdtIJtN856vf43f/zRco1GaRsTaTy1Xa4TIgiWm9DA91MbJxgK7OPMMDI1QKdTYO7sQ4dutDfOe5L+MEq1ErVNNJJrLUmy2UjCEDHUWbtttGiQA0LUrRlnHC0MHH49577+MXf/7H2bp1lFtuO8Bf/+Xf8bm/+msyHRpNz8e0BN09vcwtz6IjCaiDK4hrKXpz3azfMMrdx+5i8+aNCCFIZ3L09vbSqNeRgaLdsBm7do3VYpFbDx5GqZCXT71IzZ2AVpOklaNUXSbEYWhwM80GdHZ3cmD/fXiuQzyWYOPwelCKZ56P+gIgERo4QQVESIhA00x0U1JprHBw127uu/cellerlCs1vv/97zC1fB3L0BkcGmJ041a2b9/O9u2beOqZxyOjqoqSy22/zR2338XhwwdJJlNcvzhGTM+wbece/upvPkfZXQYCDKERi8XZPLqND7zvfdx3/1Fee+MNHn73e1lcXOGJJ75NTLdIxjJ4TogX2Py73/otPv7JD+P7bXp61lEuVfjSF7/Iv//9P8SzLTRT4DkOnR0ZHrjjQ+zbfxsbhzawZdtG0DyW5pc49+YYekcHh/Ydxtgxuo/nradwgyoKD504qXiGRquFEJIgjCJkZLh2NKxJm6SUrOvOsXfvPn7pl36aXTu24tghx4+/zmf/w+/hCYdG3WO6XGeodwv5fA97d7+Tnt4eWk6TuZlJzp65QOA7mLri5o0x+tcNsHf/XoTScB2fVtvDNC00M0km34mPxsTkBIcOHOB9H36I//gHv8fk5Bhtt4Jm6IhQ58H738WLL55kpbyIaSQJHJPB3g0M94/y3IuPI4nooEIzCaWDZeo4fgMlLEw9QcNuIDSfY/feg+tJVAhj45e4dP0kmmZjmFk+8YlP0dfbx+zsPDeuT3FzbAZBjJZTp+1U0bAYGhqiVmkQ+BqtusaGDZv41rf+AxV3DsswCFRIELbJxZPUyhVmZ5YoFdsImWRluc43vv5Vmm6BuJnGdVuo0OQnfvhn+NjHPsHszCSHDh2i2Wrzq5/+Nb79xFeJaV0MDw+xeXQDu3bu4n3vfQ+HDh2g2XZoNOqUSmWeeuZZ/uHb32fzyD5+57f/L0wZw9i1axe9nUMU2/MILcAPXEqVpai9Kt/KxJOARNOjWTlKECifI7ffwW//1q+Ty2dZXinj2g5PPP49vMDFlVWsmMUPf/An+PAHP0pX1zrm5xdo1BvsvWUP05PjXL50lf/yZ3/M2YunaHke1XqNd7zjGMm0xfTMIql0Frvt4NgOuY5OhKGTzXXQ3dnB0NAwv/Gr/5Zf+cwv0Go3CWSIZcQZGR4mldCpN4rMzS4x1LcJnRhBoLFcXMYLKlhmAtdvMTq0hXyml+sTF7H9Gqam47gO+/fs5R33PcLyYplCcYHrY1dYLRUIpc+hWw6zc8ceapUymVQGu9VGNzQUXlQfhYpsOsvOnTuZmpgmk86RyXXw/ItPcPHGGxi6wl+7GsZjMYLAY2F5lt51vbRaLgKDa1ev8PRzT6ALI8o5FDrH7jzGXXfdSb3WYnGhxHnjKi+99DIzU8t85NGfYnTjFpLJNPv37mV4uJ+NG9cxPTWJFIK20+R7j3+bP/6TPyNmdvDbv/H7+KHP7OwCxobR9QwODHN5/jUEAilCfBn9Z5A6QjOQ0kPhE4QSQ+jRSFUTPPa+99HX04kSJgsL81w4d4Yr56eIG1nSScUjDz/Gp3/5N0lm0ozdnKBaqTM8OMjKQoGVxSojI1v44Ic/wuf/4k/p6xxg+44tfPUrX6Jl1+gfHOHr3/weBDHecddDDA8Nowudkc3DxGIxbl67iRHTufXgbTz34lPErBimpdFqNRkZ3kDcSrBx/XbymV5GBoZpNtusrhbR9RhC6MRMg/c98ijNakhnVxfPvvJNpHLRNXjkkUdx7ADdsKi3a1y4eIZQSfp6Rvjohz9JOpUhFjNR6IRK0WjUEcg1YBZ0dXZiGSaJRJrunj482eTU2RdQwiVUAoQe4WgTMRqNBv0DG+nr66FUWiWRSFCurbCyuoRu6GgCfvJHf4JcppdKtYzt2MQTCT777z5LZ0c3n/mVXyeUiouXL5NJpYibSYw1UY1hphm7Ocb1sUvMz62ybcsBDhw4xAsvPc03Vld59wPvwejr62Drxk08c0rAmnBBKR0lo/GlLmIgFIGU6IaFpaXxfcFD73oH73nPA9QqTZaXlygtrlJbDnHbGplMhg997CPcuDbO9x5/Ek8GtG2bnZu2s3XLdp5+9il8zyeXi3Prwbt48cVX8P0233v82+zYuo0tm7azc9s+Dt++zF/+xRcZvzFJb886DhzcxY/t/FGEAhkG6JrBur5uICAez3D44FGqJYdjd76TmblpqhWPof4hdOKM37zGaqmMJpIEHvzkD/8ct+07hlKS639+E40Ujlfn4P7b2bFtO57fwA9tnnrmu5SqBQA+8qFPcPTIXcwvLWN7bTo6uyiUigQyeFtpJIQgk05jmha7d+9meMMwf/e1LzI1Ox7Z2JT39vc1mi2C0OfOI3dy+223Mzu9iBWLc+bSSdpOFaUU/+JHfp59e27jie8/x4b1m1lcXuILf/k5TrzyIv/y079JpjNHMmlx5bqPDBx0JagWW7zw4lf5+2/8LZMzkxRXl0maPWzauJlvf/O7vOPoUX7yx3+adT39GKHy2L1jJyktR1u2Uci1wUSIJgSmaeG60S9bExZCGZi6yaPvfQSJhmMbzE8vsX3TCK88d4aplet84offS7UaEPg6L774Mj4BhmHy5snTzE4vsHnrKCCZmyvQaNh05wd45dTjxLUYv/Nb/5rbbrmdZtOhMzOMj4Mf1qgtzjC2eJJMJsU9d95HNtvJwsoCFy9exdTj6KTYPHIr3V2D1Os2zz7/LLfecpRctoPObJ4wCHACG4XNsTse5MitRyE0seIaN25eQSdEYvLO+x9lZHADpmnwve99n/PnzwCSdT3DvPeRR0kk4/T2dCFliGEkGGwN4DhOJEtYUwjt3bufoeERfC+gVCpw+vSbCGGia4IwiMbVoVQoKYmZGXbv2IuGRv+6fmrNGsdfeA6lFI898nG2bbmF8ZsL7NlzgGKxxB//8R8xMT3Gxz/+Qxy9+xier3HhynXGbk6jhVN89+tPU6rWmFy8RFsuATqGbiH1OpfH3iRr9PHog5+kP7cVu9JAKxWbbBgZpb97JIINqKjKf0uYGYQBShlROzWMsDBbN2xk49AWpm+uMjU+Q2duiBtjS3z1H/6ehx5+J+//wEdQnmD/3gPs2L6dmelxnnr2u7z6+nF+83d/mT/44/8ccQMU+J5LobCMELB5+y50LU295tLVmefKxUsE0kZpLroRCUTPXTjD9evXWSkWGBoYpSvfh1KC2/fdSzKWJ26kmbp5g/n5SYZHRsh39LFuoIdKbTWSRQvB/ffcTzbdQSqd5OrkZYqtWXwcto8e4pF3vpfObB/5XDfTk1NIERKzkvzcz/wfjK7fSCyuszS/SDqdIZ/P0Gw2aDRtdN0ilB67t+/l/Y99mEw2TTxmYOo6heXFCLQpA6IMwUgMqZD0dq1j66atmKZG/2APtXqB6emb/Oov/Ta//Eu/QX/fem49dJiR0T6+8e0vMz4xyZ2330t//wa++MUvc+XiZaSvOHz7Ea7ePMNLl7/L9YUL+MLFMpIINIIwxPaqgOTorQ9i0cHY1TlmJwpos1MVqhWXoXWb0Ygi1ISIIEdSQhAoNBVDhHGSRp6M2c3+PbfhOZLlhVVUmEAC//XzXyCWgh/6kY+jqRT3HDvGzq07WZwrUi6X0A0fV5ZB2IxPXyKRTDGyYT1bN4+SiKUQCD7xiY+R6+ikWCxy4uU3mZyeAQKkXBOHKoPFxQK7du1j6+bttFttdC1OOtHDwf23kTTjdOfyLC4ukk1n2b5hN50dOcJQ0W5F49bRwV3s234n1VWXuJllZamEVBKDNB9+9MN0d/aSjKc5d+o8Tzz9faRq89ijH+fHf/RfoKRibmaBx7/3FH29PXR1psnnMoRSEiFnNd5x331s3bqJ7q4uduzYzo3rV1gtF9B1QSjD6PuUGe1mDDaMjDI0NEgyGSeeNHnltZf59c/8Jj/+qX9BeaVOZ76TsZuX+bef/b85c+kUqazFwtIM/+73/hXS87j/3mPcfewwnV0pbk5fBzwCtYoflvGCNvmODvrX9aNhkTV7efDehymvVLlxaYqbE/MY589dJWYo8tkou5Y1LV2k0hEIqWMZKZSMkdA70MM4+WwPjaoPeCgZ8tpzL3P22uvccft+4kaWoK0z2DPKqydf4aWXT1CtV1Ba5P4VErZt2UF3fpDAdRno6ae3s4/erkHe/c6HsFQHTtPm+LNfZ2zyRkT1Vms+ASR7d+9mw8h6HMfFaQaEjsHm4b3cf+9DOHUPoXRu3hynt6eXno4u0okk1XqZlZU5UmaWT//CZ9g+uoMTc68RN5J47QBBwI6RI9y++xjlZQdL8/nK336NcmuVdHwd73/4A7QqDslElq/97V/h2DaGFZDP5ohb5prFwEDXUuzctpuEFSNA4jou3/7ON1EoZCgQ6Ig12Zpp6Pi+4uhd96ILg0azSSye4OiRo9xyyyHGr80QN5Jcv3GdP/qT/8ByZYp0soOGXaQ4McfmwZ386A/9EFFUveDJJ58gVJIdm/awdct2eno6CYTP0vIKFy9dJpSKvTsPsXPjThanC2iBw/jSNYxKrUBMmGzZuIf8mV5W7QV0TawJrRW60DCFhcTAsW0eedc9JBKKudkFurpzXL1ygaefepF9O3bwkz/2U3h1RS4bIyaSXL18laX6FIbuIUOJEFYkcCg71KsNhPTp7+nHb3vcf/cD9HUNoHxJseFTLjbxgjZo2popMyBmpnn/+z6AqccoVlbZsnEL3dk+BtdtpCPThY3Njas3KNRXufe+Iwz29bI4X2NiYo75wg12bTnISM8hFqcr7Ni6lc6uLpbmFlEYbBnZT2GmzeL0JDMTNzl3/jKgce/hd5HT+7h2Zpap2Qn+9itf4lM//EMEjk6hWeO5p4+jaZIwDNm/cz93Hj6KrjQyuQ6+/q2vc/by2Wg45vlomGuvfoGuRwqow4eP0NvXx5VrV8h3dHPrvtsiGXe2k/NnL/FHf/JHrFaWMXQD22mshWLCyMAoA30bqVQraLrBgd23sW/nraRiCarVFh09OV598ymOP/8yQajQyHLLzqMUZitYMkE25XHx5TcwJqbH2LP1EN2dWUYGN1Ecn0WJaOKECkELkUpDkxp9PXm2b9/O3OwCmpGnUVsltD0adpX+TUPUSjazpesMjKxj/Noyr772IobWIpQhaxMjZOiza9tuUkaGfEeS65dvcP7CVY7d/yOMXZuhI5NkeqzOjatXADeKXBEhMtQxjCyNksH3v/0yGzatI2nYLJcrfOrou1ANF7fV4vkXnsMVqyRifcxOV6ms2Fy4eJW4mefdd36U0gQIyyaVhtXFRWZm5+mLD7N79Bb00GBxvszJc6dZak6zLt/Pod2HKS/YBKHOt771LYrtORp1hzdPXMWMSeaXF5CyCaQ4cvud1AshVb9CvT7Ot771nQggjo8gHglCsIkZYCiT2w8fpVKocUMtYLcVdiug3bCZnVzgzTOX+Isvfp6au4Km+aBCQgmJZI4tG3ewZ+d+Go2AcrlFu+GikyaVSJEwTZaaJa6OXeXc9fMEqoWhd9ATW8/IuvVUKzbllQbNcIWB3j4M6Yf4rotlaWzbtI2z4y+hVBA9rajIN6dcBBZbNu1gamIO2/GoXLtMPpUjm03iyFVaTo7HH38STSXonejitVOvUGxPg6ZAWZhGAi/w2LPtVh564IM4LZtT16/w9W98i54Bk3YDjj/zOps3rueZJ45zY+50BJ3SLaKBo86jD34cK4ihDMHNsUW+8vXHWV5aJpMaYnaswuTsHK+8+TJKuazMVrj4xjiGbrG8vMrdtz7Exq7duC2XoBmwPG3jG3U0DR65+6Ok6ESXWdrODNdn3yBQLT747v+TzYNHqdYaXJ06x8krLwMxmrWQ10+cYaUyhWnAsSMPsLxQwghTTF8rkoqnuXDtIqdOnSJuZfD8OqYeQxNRGLQuNLau30E+1cPJl85y5GCerRt20Z4JWaqu8uLxVxjaMIJuBeB56LpJGEBHspvN27aTTSYpFRc5/twz7Np1C8vLK7QbIcXiFHPL81y4dAZftqi1qxFFNPQZ6B0iaOuEAlqNNql0L3fuej9Gf88ouVQOx7HZtGEbaa2TllpFiQCBIpAOumjRme6mWXfp6dHo6upkemaawb71vHn5FQxTItuKeFeGwcHNXLx0iuXyZTzRXDNCmOiaiSXgY4/9MCPrtvLayReRCpqtkB3b9+A1k1w6dYqliTIXr52jSRm0KK3ED+CuPe9kU88hSjMVcvk8r516jnMTr7KpZ5QbEzdxijYrxSKrjVUSZi/dqX6swKDaKJNNpjmwYw+V1RbV9jSNmkNfxw4assjuTYfZveF+2qs2169P8ey577HYusiuDXcx0rmblZllrLTB0vIN7jx8C4M9mxnu3gKh4vTEKQ4e2Um/ZrM89Rwb120iJkzmZ+eYnJvECV1MwwRpIUwNJQJUYCKMJK6ncfnNK2wZ2cnL1Rep7i4x3DNEIpMnbfVRr7bYtWUnJ88V10wlFnEjRaXQJjc8SNDMMHuzggjHmZ6cwW1Kzl57hguzrxLyFlxTYehpNg5t4vZb7sSpagRhm2wyh9uULFXrGMNDW/DaPjNzY2zePsRI73auLb+2xuYnOt+kT2dHNz1dfXR39yKEZF1vH+cunuLE5Rc4vPcwO4dvpzc/RLW2yuLKLBWntGbUMBGaxPbq9HeMEtoWywtFNo1u5drYdWYLN0nlD9K2Qjri/TTqHkuFAgpF3IjCD+/Z/07eeeSj1Isho/1baNllpG8TOD6H9zxItVAnZSUhVaetCvSkt9CVGSZoGwROnK7YCEuTbQzdYGL5Kts2biOVEjSqLsPZg9RWAgLZptBeYq5wha3DBzl2yyMYbozQg1qzwcN3vp8Dt23j9TfOs7i8SixjMLp+I9VShZdPvcye0TtJhCMsT1apew6vn3qdEA9DGZh6mlDqKOVhWC6271FedfjYAz9OV7yfSrPI86++QCqR5uPv+TFG+3dy4dob/OhHf46F5SITi9fJJtO0bYeubotMPMF9R+8j15nn8ee+yTef+nIEwKaGZiQx0IEQpSxSsQ4sLcHywirrN2q0GwFKF/ihTxC6GNVSmWa1zcpqiVw+w8jgRq4uv45GFPmOUpi6TndXHzEzsjSVqyV812ducYxYTGdkYDMx0UlluclSaZZqeyXS86PQMPADn3yyl+0bbuHqpUnqRcnE1CVev/gKDXeF3s73sH3LTkJH5+L46zS9CqZu4nuKHev38/FHfgqvlCBMtJiYXsT1Vqm3l+nJ9tGVGaa3O8v0wiIvvPYcIVXiFti2QngtEimNdLKPZtNnpjTNjfnz7Ni6jVa7hl9Pk89146kS1+evs9Ie5/6j72bfhmNogWB0aIQbYwvUym3ymQ5aZYPR0c00WwGNShu3GbCwNE3oS1JGJ34bTOIUlicolucxjMj0YumRAsggQEPh+B63HNjD1sE9pBnEb17k4qVL+IHLpr5t7Nq+mcP7DrGue5gjhx5g4YkVhG7i+R4rS3UG0gHd+Sy9g93MLszSCivELA0tjBMGCo0QibsmK4OFxQIHhrPs2bOe+YkGhaqNlUjRmF9C+8PvfEI0WmV8P0TXLe4+ejeWiEfiECGRyiOmmaSNDnpyw6zvH6VZdqgWapRqRfL5DMWFFW7euIFBgq6eAWyvTRTfbqFpUXPpjgPv4r1Hf4iM0cnY5QlWl2s4XpOD29/Bhs7dOBUdr+1RLhVwVZ1QQlJPs3XdAbR2B5pMUy5WKdsLfPulr3Bh+gx9XSP0dnSRMtJcuXaFQm0eMFCeolG1sdsuPd1ZlK/TsgOuzZ9lvjLG7Mwcvhtjw1AnmnQoF9tcmjrHa9e/j237OE2N1cUmp09P0G579PdtQFgJvnf8Kb7yza+hXJN4kGb90Eau3HwTXSn2bdnD+sF1xEnRatvYoYtBBiVNAgm6MLGli+0pBnPbefSex8joSeamFylXmhTtaezARmkh63p6EH6ME8+fQwuhN5+m0V7F9hu86+gj/PhH/g/efGWc//pf/oqLY+cBA9eDMNTp7x5gw+Bmjux/B4888D527NzC+v5NeHWYHFtkx94hLt44TsOv0NnRFTkw640ihpFica5OZ+cG+jM7mKmfReiR8rS/cwTNTbNhYDs3LlxA2tErxg0bBHUI0hq37buT1cUKWkZb63XHsawUMoDOXAeNqk2l5NGbGcZrhoQaaLOC4b4drMtspzg7R2i1mVq6Sahq7Fh/B3sH72TfhrupFxTnr72KLxwuTJxkyblCd6abfZvupCvbwfVrU8wvjeOJGpqCrtQWAjsgnhfUq9CoGcytjDNdOIVuKry2Rava4uC+YV547iLlehFfttgzuo9sbITKapOOVJabS9dYrEyQTvWwUBznyuyzpPQc6z+2k3wih5FfTzIe485b3kt5WeNCfZJNG4dYbS5gy1Usv5OuXJ5cOkfCyLNn78O4skFzNeTyhUl6TI2BnmEmyyu0WcXH5fip51ldbjDYvRHl6ejtDA/f/37+/Ct/TH9mC7vX30q77BCLd7JcLtMOWgwNjLJ1/U72bttDwkxSr3uMdA9i+xWeP/ss67s3c+/B++jM9PDcayd56drj1MKQ+3e9J9oA0kuQTGdwmoKZGxV6MxtYqN9ACh9DS7O+bzc7N+zFb0uW54t4muTSzOko/UrliIsMTi0kk8whkx4yCDBFAs9V7Ny6h+6OHorLJU5fe51sLMFKfYIrM9eIJVK06z6O65FKdWH2Smy/wife84uoRhJZTeI0A6aWLtHVmefa/HmW6tfwVZW4NordMKjUmly8dp16WCCgvSaYzpGwEmiaxs3JKbwwZKFygVo4wUBsH93ZTjLJOM8+Pk3LjVFy5vD0OhljBNM3SHVo9I6kePLiGV4ff5KkliVQbRzmWd83TGW1RefwOhZXbpCKZ+kwRlhZadG0ArqH0tTsKe6+7W664usZGdxOKpHFbgi2bhzGM2q0nDaTZ1bp1ePMzizxytXvoVAEosaFqVdoVB0evLULM4xh2V3cuvkuzm69hubHWJ6zubh8mvXru7ltz37e+dCt9HQPcPL4JZozGjKeIgws3rjxGr5RZm58hXz/7WzbOEjL0zn55HlWZY2F0hzlejlKTHx68t8IpxZSWi4x2LuR9z3yATRSIBWWnsNQXWTiCYKSy7pUP/iCUmsVJSQqMFBujGrBwWmBDE02b9zBcO8Wtg/vI003WquLZrPC9enXKDcWuDB5ikLrGv2dW8jH+nnllRM4QQOle7zr8EN8/N4f4b7b3oVpJbkwdg5puShLcmb8VarhDDHTYrhjHwOdo9y8ukA8nkQzJVL5WFoSFQa02i1aLcFqaZXVxgSLlWso2hiGReAbLBbqTK1OUrJnmVy8zlz5XFQUdo1y3zsOU3YXuDb3Orqo4IsSGC6CFCpIokKDN05f4PSVN8il+4mrDLlEGkNPcvPmIp9876f401/7IocG38vsaZ/Lr81x+ew4zzx5ktMnp/jml59lZbpBLOyk2W4zWxtfM6hruFRZrE1yc24czciweeQWxk+3ObL9Mfo7NzA7O082vo7SUoBopnn/PY+yIb+FwdxmUvHOqPIyA2S35MrcHPFmD4d3HsI0dJ56+mWuzBxHiSZ20OKzzz4o3jLhs75/lJn5WRamK4xsTtFhdbDitVjfsZM0g6RzGntu3UnXWIKT3zmBK5tExKw4G0e20mtsYrY0iRPUuevgu2lUS1QLbeqNBkP965meucyG0VGWVhZoB2UsXSfh9+CWYsRMQaE4Tf/Ido7s6qcv18OZ0zeoNMs0vBUmbpzDVTY1fwqEhyW7yBg92DWXpaUKKhVQqkwikFh6loTRgW3bVCgTS1kslK9T9G5ETj5Tp1RtYmkBYbxOuT7HVPs8o92bufeWD1FfMvjGV1/gmetfo+LOYQiBpWdBB8dvYRkxyqUqrXoN3TLZ0H2I1UWbfGcG1/NZmqtz8NB2OrNxspkODCtFubbE/oObqbkLvPbmGYbEMbZmHqC4XGaKC9iqgSkMlIpqrpZcYWF1mpGOXYStNKsrgtxALx1WjUY1RPNT1CouuXSKyxdmOfHyaTypmFy5zFxhmoZdYrk9SVoN8zuf+BU0r59/ePwC1UaVijeOVB5tO+Iyvr0BhjcM4rkGjVXFwK0b6eseRThJdq+/n2DVYs/+UTYfyPPtE1+h0B5H0kTTQppOg6VSgUynSygV7api5nyZmK6zf9c9XLhxkomJ6xzce4zuriEuXPoLHNUkq/UxnN9E3uoiDCvMLxRYKLzKO++5m+sXF1leqVB0l7g++wrtYAklXNDi6GGOzUP78X2P5co4iXSOqyuXqYVlFJDLDZKOd6NCm6XCIpneLhaa1/DEKkL1oqsUrXaRWKoDry2pBRUc5tnX9y/Ran3ku+D02RMsVs/AmgvHCxvI0It8y56gXg9Y37+RgVie4qKNEnGaLZ9ms0QiHicuunnjhSliKsb6gX5IVJgpTHFx4nW6E5vY1rWPjpzOzdIk5xZPElBHE0HkiJLgqTJVZ5qGU6Jc8enLjlKaneehD9zO+KUGS0uCWNJgw+ZhipUKr50/w3J9nJXWNTxqSHwUFoe37sWRcPbkGSrtIkviPK5sgabTChf/6Qb49a8cEf/6/jfVVLNCteGjGzo7Bw/QExtl6OA6FqaaPPn8V3np9depucXomqeieLOxlVfQVQLl5RAywZ4t+3Daq1y6doaZ0k3a4TIrN6YJA5OWWKS3a5Aj69/L4W33MHa+QIIMFa9Is23z9NMnuOfIrVgpk+nCVVrhMkpvIZWFjk4m0UWHtYXO5Aj5zhihL1mpXV9zCZvkUxmU7aHCGNs37+X8wtMU2jPoWhoNm56ePEYTBD7r1uV548I1Dmy+g30bj1Ap1GkqiWNVaYaL6IaJkhIvrCNESMrqY2RwG3o9TuAFFNoF6tUYPQkNRYgfNNA1n+88fZxau8zswjUC2aYlqkzW3iRpJPnAYz+JfQ1W3WUq1jwtuYJQPogIIBVNFdss1K8zV51if/+d9GY9DKuTmN5FpgPGl65TkDf50lNP0wxWmC+O0QyWCGiBJkATZNUgjaLg+InTdBmj5PJxTs1eRCgPgxg1/6T4JxsAYN+eXpo1mJ5awhR54k5/BDLsM3n5qRsEWojtOdhBMfK5qzSGIRgrv4SuC27d/GFkuwMrnqFYn6MUzFJwxyg1p/BCF0EcKdqsSx2mz9hLedlhtVLDCR1S2RRe0MZMC07eeIGXLn+XqloAAWGYwtA7iJsQ+G3CQGf9yABjC29y4eZpVt2JaNKoBGHoEk8YdKc7aVNjfPkiUvjomokmJauFeXZtvxtN9zg9/jKhscBA7/1UWiVWggrHX3+RpdYNdJEABYl4AtupI2WILlJIEZDttghEwI25MXaMHIEmOFoJOz7HqfFXadgtREzSdgtI7DWRjaSvZ5TFlWv0ZAYYL13h5PzXadiLkWVeScI1s4bAxBUViq1x/OQB2lrAfe85wj987TLKtJlqvszp2edo+VFSWbSISTQh0THRZZZErI8ARUe8m45clqKcQdIgQtj6b6/5P9kAj/7BevGf3j2mliouPdYusrIXzw4Yu1wglkzR1mcotseRookmYphCQ0oXJXwmSucxTJN3H/sI84XrXF44ybJznkJjEkkLNBnZxkQ/Xfp2En4/lZJHtjdJX7fBK5deYq5+Ey9oYgclPMqghcT0LtLJPIHfxPPb6CrOwMYeLs+fZGLlFNPt82i6G0GbRMj80gq33d1FvT3HS6eeo6KW1jC0MVzpYRgp9GTA2bGXuLx8EjNl06qYNLqrHL/yZWr+9QjopGkEoR0hXnQDX0psz+Xi+BsEg3EG8ltY3z+AiDssN+cYX3iBVjDDqj2LoSXQA+stbm1kmCVJteozubDA4O42N66+Sqk1iWmAkNH5j2ghlAXKRDd8Jgtnqbzm0xXLs/9IF4fv6ufx71zCynfjSYWlJ9GAjuQQBnEKrUvoQmJIi0w2w+4d27h13W6WK2WeOvsiba+EEhCqlvhnNwDArzy5Vfz01tdUJtjEzpHNtGWN2fklgkSdy3NnqHslhEigEcfSO/DDGoEK8ZXDpcVnGf/KZTKJERr2Im2WEdgoTWKIGIbMcGznB9mauYt6o43tNbASLqF0uF54nZaYAxw0TaGpJJboJRnLoJRNEBTxwha37fkATdvm9M1TEF9C0XybvBGGDptGN7JSn+H4ma+BUcVXHhoxWHMb9Q+s49LkKc7NnUTpVZQj2bJxC2+88SJV9waBXsPSOtCkQNd8Wm0bXdPR9Dia4bFqj3F1XjC6aRMz05eRtTGWS+OUmtcBH0GMUBqYRpp4PIcb2Lh+FStuUrVLGCmTlrHIVPU0lmGA8DFjSdp2PfInKBUleygDWzVw2q+y3Erw19/o4pEjH2LHjg0U2kmczXXOjR3HiIm1h2Y5stjL6E0Qz0ClOU/DbzAxN8VccQw0/Z8s/j+7AQA+N3aH+IWtJ1RvV5LTY2O4WpHVeoH50iyhcEBpEbTJAs+RpGLdKBmL+LpolN1xpNYAFa6xO2L4Ycgtmw6xoX+EZmWKOb+A67VprFQIii1CrYEgQFNxNBVD1xIIDRrtBXxZR9fA0ONsGtnL7MUSjlPEdpfQNLGWFRCBm/Yd3MWZN6/QVvOIsIkQHRhaHC+wScU76Rno4IXJ53HFKoQt3nnk/dS8Ra6WXgU9QFNpND1OQIuIA+xhmmlUEBBKGy+s0vSncY0VplcvYKYsms4yQtgITHQti6ml0XWdQDbxgyqDAz2sFiuARndXlnNjT+Izh0mKwA8RCrLJLrwAPC+awYYyYgQgfJRmc/LKCRama3zknR/jruwuzMsNrhgXaLhFcgmdSmAT13tJGjlCzebq+GVayRgP3JoithJikqMlr/6/ghj+2Q0AsGVLjo6eOGreJZZoY6QVLNsoO8QgR9zowA+r+IFPwsiS7xyiVFlEqoCYAcgkcb0Dx68QCp9jh4+xfWA/J15/gytLZzi4fT9muoOrM68R1strtwqxJpWSeGEZJR004sTNAZQMiSfjTE1NU6qV8VgllFHecMxKEYQeupbg7MUzTC1NAT6IDDErhfIC9u06QrFY5eyVNyi3FzA0HUsfYrUsefW1JwnwEGEekzi200QRw9INkFEOr2FYkXNKpJFSsFyYBsOmXFvEFDo6mbXsI59AlfGCgCDwufXAg7hem/nFeTLWIMmMwbUzZxHCQMMgZkRGnJSRwhVJVv0ySvqYhkkYKEIVbYBmWGKydo7Pf3eGn3/slzh6+2GWxAxPv/ENEqKb/ng3uqbT9pdoe0XidLB18BYGh1N866lxTCPkn4k1+O9vgF/8/l7xS7d/XY0tXCaZsVlYvkjdmUVHIy56ScWGqNqCVCyHJjOUShU85eKHEg2DnuQwXakB5svjdGcN3HqSr515noZfREvC4PAwr77xHJ42vZbbayJkDClsAqroWoqYuR7LSuN6DoYW4Dke1yZewzKiIkwjjtAUfuAQRbaaTM5NEkgbTUsiRBzbrvPQ/R9gebHEYuESmjAi/h8GetjBxM1F+jJbGI7F6e/rI5dKEwpFtVnh1OUT+JTRRRvft9H0yDDrBSZnL92g5QfoZgpdxfBDm1QyhpQGrisJwpDdW25lx6ZtfPkbX0Wjg56ebmYWxinXKhi6RcrqwJcOTXeFaitEJ0kmnqPtVtBljs5UP6XmAn5QQGplmqJE01niC4//JR+892O84+DdLC0tcnNhkqNbH+TmwgTFVhHD7CQmRzm45yDF8gqFUoNqcOqfjWH5724AgD9840Pitp7PKN1uMrc4iSvrmKKDfLwf00jgByHJ2FZ0Lwmqhk+abjPN+t71tLwiQjfIJDOUG4ssVV5B1+MkEiaaZnHi1Ms0Wi4GkcU8afajGya2s4JlZTCMJIIYrtPEl23aoYOlxwmVIMQgHe+jac8jVSsSZWrRDNxxq6AlietdtP0WP/zBT9FuaZy9+iSG5qOLFJsH9nHk0CHW924ln+xiQ/8wnfkuMtkElm5Sqwc4dovTV1/kz7/1BcaXLqLriiD0MUWSTRt302waiHYKjSaebKLwkIHElxoanRzYcZiPfeD9/OHn/gApPNJaB/W6TWH1HHHLxNJSBFKhNAFBREAPhY8gIJvoJPBMTMOiL7eRajtFWy4QygaGpphrXOGJ15/kiH0nxw4fY/57K3TnuohZGRp+GztcxVK9IDX+4emnGKv/+X83g+d/uAEAThX/vXhg+6dVM/TRtDSG7COfGqTtNkmrUfL+TkY7duAEVbxkm2SHYKk0zVJzCtOIGD12WI4IrCKNGxr4tkvc1EhZOQwnRiqdQGkatlchZsQJpUuzXY5gj4YZeeTR8KWDoVsMrdvM4lKEhFHKiTT3wkKqkFA5BD4Mdg3w6Y/+Brqm8W/+5HexNMnGgRE++cgvc3DX3QyuS6L8FKWiA44DbY3x+QKeZ5NPZfFWNW5f/25u3DLLxPcnkBKO3nIXH3jgE3RkB/ndP/ocGopAVlFYaELhuga+0vjQAw/z4fd/kuMvv0ixXEUTKkLQOW2csEQofXzhRIRZLU5/fhMpMUSptUTFm0OpBgJFo75KPt1HOp3Er6WQykUJj1CE2GHAhSs3OHrvLYzuzPH5V/8VPeZwlHgifUy9n1euf4+Xr//J/zCA6X+6AQCevf77AsDS+lVKDZKwesmlRzm86wAZlWb3YB+ZXIyXLlziuUtfoyTHcKniOwtrLH0VoV5jGlJJQs2ms3MzmpunI9mi4ZaotVfwVR0lAsKwvRYioREGa2x93UCpkMGuIfZu3cbUzFU0EV+jf5tIaYKeIAw0Dowc4Sc++rP09PTwp3/9Jwjdoyvfz2MP/iyb+/axeq1Coh3nyde+ytlLV9HcONVmk1W3yGp7ip96749x5+aHmJ+uUSu3EUKnL7GFT9z/S4ykt6BpGpsGu7lRqKEZBoQhGjGU6uLQxtv56Q/9LLYnuHr1ZgS7DiWxZJIwrCMDG12PEyo7OraQLFfGGczreGGJMGwihE9IgFAGq/UaBhlysT70IIkf+lixLupugZiW5qmnXuHd772HGzcvUKjMoTSTbn2YOf/zYu76/3xt/5c2wFt/vGBJpOO3q6XmaSrNJnPLUyTp4fylLkCnFqziamVcWULK1triR0ZI04hjuwWkCohbcRy5iONU8IM6drCK1NoRll0CIkTX4sStNK7bJpQuSuqkzRHed/uPc++972BidpmzN17A0CL+j7YmHds/eJSfefh3SIV5jh9/hptzN8hkEqwf3s7JNy5SnxTctvFeFmYrPP7KN7lZnCBFL20kcQTvuuM+9m07gu/BYm2KE2dPEKqQo7seJO9solaGjr4YOasXjUGELKHRRiNPytjAT3zg51G1FJOzY1y9cQOhCbTQRzc9Wm40PxFCIqRYo45qhKLJzOoZxFtQLEWEiyNE00IkVZqBwWDnLhzbodiexg4WUSrEbyZ45eUu3n3bz/L62ZepteaYbz/9P49d+9/ZAABTzndEn7FftWngOXUs1rEsYgTKB91HmA6IgECtRvEpIkvCzJJMJijWZhEoPDdgqXgDWANDCw2lnLXwCJO4lSEZ76Ftt0nEDVyvhhcINg3eyb7hRylP+Agnh04cpZqgGQShxqb8IT541y9gtJMs1Gc5fvoZVhrzmHF4/dxz9IiNPPzYJ0ibvTxz5otcLV4EdAJrlXv2HOG+ve9hfWon1HKs2iW+9PgXKbsFNmR3cfv2hwibYJk6+IodI3tJvtGFTQFEEiWzfPyBx9jStRvXbfD8iedpuS2wPJRoU20sEkgHRBiRQJSBaSSxrCSOW0FpAik1evLDmEaGQvkmUthAhI1zKVJtTKCRQ9cEbtim6sximjnOTJxg58gWDu7azd+8+IX/5cX/39oAACvN85HaLzGsXM/Hlg7JWBeuX8N16mSSOYbWHWRhYRo0F9sr4QQSTVPoWgIIo0haJdZwvyoCQxEdF0EQYpoxdK9J26mv3fEtkmYPC+MOmZyEYA2kplsEgcHG/CY+ee+n8Zb68DYrnn31cWaKF9HMJrbnk9A6+ci9P4Ms5ZlUE7x28wR7hw8x2ruPPetu49DGWxBKo9JqcnnuBN8//fdM1C7QmejmJx75VXKqmybL+HWd9Go/HUYnOTOFHWQIlcHD+9/JgzsfoV3xuVJ9jZcuPIcwV/H8SiQGlfZaBkLElte0GJnsOprN1TUwVIJccoT+zg0USpOo0EUTaaTQWNe1GdepUGsvookWlt5BXLNwggqesOnt2MGfHv/4/6eF//+1Ad76Y9tzb3+oaQ0oTc8ROE3C0GFo3Q7sWoDrN2nTwAmLaEgMLU3MSuH7QVQbRDjuNdjzWhq5DKhUF4m4RSFhaAIJOswO2iUwrCgDQGCilE5vYj0fuvPTtG/myfe0eObSM7w8/jy67uDLNprUODB8PxuzhylP28QTLg/e+kG6MsP4xQyqIBl3VqlbBW6sXOS1K08y506DaLB/42NQ7CfWa/LUlacxgl4OpB8jyCRJJ3tRtQJDyTwP7/0AblURGy3whb/6Oi42vpyLfjnK/MHiK4EQcUw9iQx9PM9D12LoxMjk4tycP0fbLaFrFqgYmtIYHNhEqbJMpVXHiukYKoYWprAZF6GChcr0//Ya/j8M7oobBCO4dQAAAABJRU5ErkJggg==" alt="logo"></div>
  </div>
  <div class="brand-caps">VODIWALKER</div>
  <h1 data-i18n="h1"></h1>
  <p class="subtitle" data-i18n="subtitle"></p>

  <div class="login-status"><span class="live"></span><span>VODIWALKER · SECURE ADMIN CONSOLE</span><span style="margin-right:auto;color:#6ee7b7">ONLINE</span></div>
  <div class="card">
    <div class="login-card-glow"></div>
    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px"><div><div style="font-size:10px;letter-spacing:.16em;color:#8fa1c0;font-weight:800">SECURE ADMIN</div><div style="font-size:16px;font-weight:900;margin-top:4px">ورود به مرکز کنترل</div></div><div style="width:38px;height:38px;border-radius:12px;display:grid;place-items:center;border:1px solid rgba(143,217,255,.18);background:rgba(62,166,255,.08);color:#8fd9ff;box-shadow:0 0 25px rgba(62,166,255,.12)"><i class="ti ti-shield-lock" style="font-size:18px"></i></div></div>
    <form method="post" action="/login" id="loginForm">
      <div class="field">
        <label data-i18n="emailLabel"></label>
        <div class="inp">
          <input type="text" name="username" id="username" data-i18n-placeholder="emailPh" autocomplete="username">
          <i class="ti ti-user-shield i-lead"></i>
        </div>
      </div>
      <div class="field">
        <label data-i18n="passLabel"></label>
        <div class="inp">
          <input type="password" name="password" id="password" placeholder="••••••••" autocomplete="current-password" required>
          <i class="ti ti-lock i-lead"></i>
          <button type="button" class="toggle-eye" onclick="togglePw()" id="pwToggle" tabindex="-1"><i class="ti ti-eye"></i></button>
        </div>
        <div id="capsWarn" style="display:none;align-items:center;gap:5px;margin-top:7px;font-size:11px;color:#fbbf24"><i class="ti ti-alert-triangle"></i> Caps Lock فعال است</div>
      </div>
      <label class="remember"><input type="checkbox" name="remember" value="1"><span data-i18n="remember"></span></label>
      <button class="btn-main" type="submit" id="submitBtn"><i class="ti ti-login-2"></i><span data-i18n="submit"></span></button>
    </form>
    <div class="security-strip"><span><i class="ti ti-shield-check"></i>Protected Session</span><span><i class="ti ti-lock"></i>Secure Cookie</span><span><i class="ti ti-activity"></i>System Monitor</span></div>
    <div class="admin-reg-row"><button type="button" class="admin-reg-btn" onclick="openAdminReg()"><i class="ti ti-user-plus"></i><span data-i18n="adminRegBtn"></span></button></div>
  </div>
  <div class="foot">VodiWalker Control Center &copy; <span data-i18n="rights"></span></div>
</div>

<div class="areg-overlay" id="aregOverlay" onclick="if(event.target===this)closeAdminReg()">
  <div class="areg-box">
    <div class="areg-head">
      <div>
        <div class="areg-badge"><i class="ti ti-user-shield"></i><span data-i18n="adminRegBadge"></span></div>
        <h3 data-i18n="adminRegTitle"></h3>
        <p data-i18n="adminRegDesc"></p>
      </div>
      <button type="button" class="areg-close" onclick="closeAdminReg()"><i class="ti ti-x"></i></button>
    </div>
    <div class="field">
      <label data-i18n="adminRegNameLabel"></label>
      <div class="inp"><input type="text" id="aregName" data-i18n-placeholder="adminRegNamePh"><i class="ti ti-id i-lead"></i></div>
    </div>
    <div class="field">
      <label data-i18n="adminRegTgLabel"></label>
      <div class="inp"><input type="text" id="aregTg" dir="ltr" data-i18n-placeholder="adminRegTgPh"><i class="ti ti-brand-telegram i-lead"></i></div>
    </div>
    <div class="field">
      <label data-i18n="adminRegNoteLabel"></label>
      <div class="inp"><input type="text" id="aregNote" data-i18n-placeholder="adminRegNotePh"><i class="ti ti-message i-lead"></i></div>
    </div>
    <div id="aregMsg" class="areg-msg" style="display:none"></div>
    <button class="btn-main" type="button" id="aregSubmitBtn" onclick="submitAdminReg()"><i class="ti ti-send"></i><span data-i18n="adminRegSubmit"></span></button>
    <p class="areg-hint" data-i18n="adminRegHint"></p>
  </div>
</div>

<script>
var I18N = {
  fa: {
    title: "ورود | VodiWalker",
    h1: 'ورود به <span class="g">Vodiwalker</span>',
    subtitle: "مرکز کنترل امن VodiWalker برای مدیریت سرویس‌ها و شبکه",
    emailLabel: "نام کاربری",
    emailPh: "admin",
    passLabel: "رمز عبور",
    remember: "مرا به خاطر بسپار",
    submit: "ورود به پنل",
    rights: "همه‌ی حقوق محفوظ است",
    adminRegBtn: "ثبت‌نام ادمینی",
    adminRegBadge: "درخواست همکاری",
    adminRegTitle: "ثبت‌نام ادمینی VodiWalker",
    adminRegDesc: "اطلاعاتت رو بفرست، مالک پنل درخواستت رو بررسی می‌کنه و اگر تایید بشه، نام کاربری و رمز از طریق تلگرام برات ارسال می‌شه.",
    adminRegNameLabel: "نام و نام خانوادگی",
    adminRegNamePh: "مثلاً: علی رضایی",
    adminRegTgLabel: "آیدی تلگرام",
    adminRegTgPh: "@username",
    adminRegNoteLabel: "توضیح (اختیاری)",
    adminRegNotePh: "چرا می‌خوای ادمین بشی؟",
    adminRegSubmit: "ارسال درخواست",
    adminRegHint: "پس از تایید مالک، اطلاعات ورود از طریق آیدی تلگرامی که وارد کردی برایت ارسال خواهد شد.",
    adminRegSent: "درخواست شما ثبت شد ✓ منتظر تایید مالک پنل بمانید.",
    adminRegNameErr: "نام و نام خانوادگی را کامل وارد کنید",
    adminRegTgErr: "آیدی تلگرام معتبر وارد کنید"
  },
  en: {
    title: "Login | VodiWalker",
    h1: 'Sign in to <span class="g">Vodiwalker</span>',
    subtitle: "Secure VodiWalker control center for services and network",
    emailLabel: "Username",
    emailPh: "admin",
    passLabel: "Password",
    remember: "Remember me",
    submit: "Sign in",
    rights: "All rights reserved",
    adminRegBtn: "Register as admin",
    adminRegBadge: "Collaboration request",
    adminRegTitle: "VodiWalker admin registration",
    adminRegDesc: "Send your details. The panel owner will review your request and, if approved, send you a username and password via Telegram.",
    adminRegNameLabel: "Full name",
    adminRegNamePh: "e.g. John Smith",
    adminRegTgLabel: "Telegram ID",
    adminRegTgPh: "@username",
    adminRegNoteLabel: "Note (optional)",
    adminRegNotePh: "Why do you want to be an admin?",
    adminRegSubmit: "Send request",
    adminRegHint: "Once approved by the owner, your login details will be sent to the Telegram ID you provided.",
    adminRegSent: "Your request was submitted ✓ wait for the owner's approval.",
    adminRegNameErr: "Please enter your full name",
    adminRegTgErr: "Please enter a valid Telegram ID"
  }
};
function applyLang(lang){
  var d = I18N[lang];
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var k = el.getAttribute('data-i18n');
    if(d[k] !== undefined) el.innerHTML = d[k];
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el){
    var k = el.getAttribute('data-i18n-placeholder');
    if(d[k] !== undefined) el.setAttribute('placeholder', d[k]);
  });
  document.title = d.title;
  var html = document.getElementById('htmlRoot');
  html.setAttribute('lang', lang);
  html.setAttribute('dir', lang === 'fa' ? 'rtl' : 'ltr');
  html.setAttribute('data-lang', lang);
  document.getElementById('langFa').classList.toggle('on', lang==='fa');
  document.getElementById('langEn').classList.toggle('on', lang==='en');
}
function setLang(lang){
  try{ localStorage.setItem('vw_lang', lang); }catch(e){}
  applyLang(lang);
}
(function(){
  var saved = 'fa';
  try{ saved = localStorage.getItem('vw_lang') || 'fa'; }catch(e){}
  applyLang(saved);
})();
function togglePw(){
  var inp = document.getElementById('password');
  var icon = document.getElementById('pwToggle').querySelector('i');
  if(inp.type === 'password'){ inp.type = 'text'; icon.className = 'ti ti-eye-off'; }
  else { inp.type = 'password'; icon.className = 'ti ti-eye'; }
}
(function(){
  var pwInput = document.getElementById('password');
  var warn = document.getElementById('capsWarn');
  if(!pwInput || !warn) return;
  function checkCaps(e){
    var isCaps = typeof e.getModifierState === 'function' && e.getModifierState('CapsLock');
    warn.style.display = isCaps ? 'flex' : 'none';
  }
  pwInput.addEventListener('keyup', checkCaps);
  pwInput.addEventListener('keydown', checkCaps);
})();
document.getElementById('loginForm').addEventListener('submit', function(){
  var btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2 spin"></i>';
});
function curLang(){ try{ return localStorage.getItem('vw_lang') || 'fa'; }catch(e){ return 'fa'; } }
function openAdminReg(){
  document.getElementById('aregMsg').style.display = 'none';
  document.getElementById('aregOverlay').classList.add('show');
}
function closeAdminReg(){
  document.getElementById('aregOverlay').classList.remove('show');
}
function aregShowMsg(text, ok){
  var el = document.getElementById('aregMsg');
  el.textContent = text;
  el.className = 'areg-msg ' + (ok ? 'ok' : 'err');
  el.style.display = 'block';
}
async function submitAdminReg(){
  var d = I18N[curLang()];
  var name = document.getElementById('aregName').value.trim();
  var tg = document.getElementById('aregTg').value.trim().replace(/^@/, '');
  var note = document.getElementById('aregNote').value.trim();
  if(name.length < 3){ aregShowMsg(d.adminRegNameErr, false); return; }
  if(tg.length < 3){ aregShowMsg(d.adminRegTgErr, false); return; }
  var btn = document.getElementById('aregSubmitBtn');
  btn.disabled = true;
  var originalHtml = btn.innerHTML;
  btn.innerHTML = '<i class="ti ti-loader-2 spin"></i>';
  try{
    var res = await fetch('/api/admin-requests', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({full_name: name, telegram_id: tg, note: note})
    });
    var data = {};
    try{ data = await res.json(); }catch(e){}
    if(!res.ok) throw new Error(data.detail || 'خطا');
    aregShowMsg(d.adminRegSent, true);
    document.getElementById('aregName').value = '';
    document.getElementById('aregTg').value = '';
    document.getElementById('aregNote').value = '';
  }catch(e){
    aregShowMsg(e.message || 'خطا', false);
  }finally{
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}
</script>
</body>
</html>
"""


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VodiWalker Control Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Estedad:wght@400;500;600;700;800;900&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700;800&family=Shabnam:wght@400;500;700&family=Yekan+Bakh:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:var(--font-ui,'Vazirmatn'),sans-serif}
:root{
  --bg:#0b0e14;--panel:#111623;--panel2:#161c2b;--line:#212838;--line2:#2a3348;
  --accent:#9455ff;--accent-d:#7b3ff0;--good:#22c58b;--warn:#f5a524;--bad:#f24955;
  --text:#e7ebf3;--sub:#8792a8;--sub2:#5b6478;
  --shadow-sm:0 2px 8px rgba(0,0,0,.18);--shadow-md:0 10px 28px rgba(0,0,0,.28);
}
[data-theme="light"]{
  --bg:#ffffff;--panel:#ffffff;--panel2:#f7f8fb;--line:#e5e7eb;--line2:#d1d5db;
  --accent:#7c3aed;--accent-d:#6425d6;--good:#17a673;--warn:#c9820a;--bad:#e0324a;
  --text:#191c2b;--sub:#666f8a;--sub2:#98a1b8;
  --shadow-sm:0 2px 8px rgba(30,34,60,.05);--shadow-md:0 14px 32px rgba(30,34,60,.08);
}
html{transition:background-color .2s ease}
html,body{background:var(--bg);color:var(--text);height:100%}
html{scrollbar-gutter:stable;overflow-anchor:none}
.body-wrap{overflow-anchor:none}
@media (prefers-reduced-motion: no-preference){
  /* Keep the original look, but avoid expensive perpetual compositor work. */
}
@media (max-width:1100px){
  *{scroll-behavior:auto!important}
}

/* Performance: never animate the entire DOM. Only interactive controls transition. */
button,.btn,.tab,.nav-btn,.icon-btn,input,select,textarea,.card,.drawer,.toast{
  transition:background-color .14s ease,border-color .14s ease,color .14s ease,box-shadow .14s ease;
}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:var(--line2);border-radius:8px}

/* ===== Shell ===== */
#app{display:flex;height:100vh;position:relative}

/* ============ SIDEBAR ============ */
.sidebar{
  width:252px;flex-shrink:0;height:100vh;display:flex;flex-direction:column;
  background:var(--panel);border-left:1px solid var(--line);position:relative;z-index:30;
  transition:transform .22s ease;
}
.sidebar-brand{display:flex;align-items:center;gap:10px;padding:20px 18px;border-bottom:1px solid var(--line)}
.sidebar-brand img{width:34px;height:34px;border-radius:9px;box-shadow:0 4px 14px rgba(148,85,255,.35)}
.sidebar-brand div{font-weight:800;font-size:14.5px}
.sidebar-brand small{display:block;font-weight:400;font-size:10.5px;color:var(--sub)}
.tabnav{flex:1;display:flex;flex-direction:column;gap:2px;padding:14px 12px;overflow-y:auto}
.tab{
  padding:10px 13px;border-radius:10px;font-size:13px;font-weight:600;color:var(--sub);
  display:flex;align-items:center;gap:10px;white-space:nowrap;transition:.14s;
  border:1px solid transparent;position:relative;
}
.tab i{font-size:17px;width:18px;text-align:center;flex-shrink:0}
.tab:hover{color:var(--text);background:rgba(255,255,255,.04)}
.tab.on{color:#fff;background:linear-gradient(90deg,var(--accent),#7b3ff0);box-shadow:0 6px 18px -4px rgba(148,85,255,.55)}
.tab .bd{background:rgba(255,255,255,.16);border-radius:100px;font-size:10px;padding:1px 7px;margin-right:auto}
.tab.on .bd{background:rgba(255,255,255,.28)}
.sidebar-foot{padding:14px 16px;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:10px}
.lang-mini{display:flex;background:var(--panel2);border:1px solid var(--line);border-radius:100px;padding:3px;gap:2px}
.lang-mini button{flex:1;padding:6px 10px;border:0;background:transparent;color:var(--sub);font-size:11px;font-weight:700;border-radius:100px;cursor:pointer}
.lang-mini button.on{background:linear-gradient(90deg,var(--accent-d),var(--accent));color:#fff}

/* ============ TOP BAR (slim) ============ */
.main-col{flex:1;min-width:0;display:flex;flex-direction:column;height:100vh;position:relative}
.topbar{
  height:60px;flex-shrink:0;display:flex;align-items:center;gap:16px;padding:0 22px;
  background:var(--panel);border-bottom:1px solid var(--line);position:relative;z-index:20;
}
.hamburger{display:none;width:34px;height:34px;border-radius:8px;background:var(--panel2);border:1px solid var(--line);align-items:center;justify-content:center;color:var(--sub);font-size:17px}
.page-title{font-weight:800;font-size:14.5px;color:var(--text)}
.page-title span{display:block;font-weight:400;font-size:11px;color:var(--sub);margin-top:1px}
.top-right{display:flex;align-items:center;gap:10px;flex-shrink:0;margin-right:auto}
.user-chip{display:flex;align-items:center;gap:9px;background:var(--panel2);border:1px solid var(--line);padding:6px 12px 6px 8px;border-radius:100px;font-size:12.5px;cursor:pointer}
.user-chip .av{width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#3ea6ff);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;color:#fff}
.icon-btn{width:36px;height:36px;border-radius:9px;background:var(--panel2);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;color:var(--sub);font-size:16px}
.icon-btn:hover{color:var(--text);border-color:var(--line2)}
.sidebar-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:29;display:none}
.wide-sidebar .sidebar{width:292px}
.wide-sidebar .main-col{min-width:0}
@media(max-width:980px){
  .hamburger{display:flex}
  .sidebar{position:fixed;top:0;right:0;transform:translateX(105%)}
  #app.sb-open .sidebar{transform:translateX(0)}
  #app.sb-open .sidebar-overlay{display:block}
}

.body-wrap{flex:1;overflow:auto;padding:22px 26px 70px}
.page{display:none;max-width:1320px;margin:0 auto}
.page.on{display:block;animation:fade .18s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{display:inline-block;animation:spin .7s linear infinite}
.no-motion .spin{animation:none}

.pg-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;margin-bottom:20px;flex-wrap:wrap}
.pg-head h1{font-size:19px;font-weight:800}
.pg-head p{font-size:12.5px;color:var(--sub);margin-top:3px}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.search{position:relative}
.search input{width:230px;padding:9px 34px 9px 12px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-size:13px;outline:none}
.search input:focus{border-color:var(--accent)}
.search i{position:absolute;right:11px;top:50%;transform:translateY(-50%);color:var(--sub2);font-size:15px}
select.sel{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-size:13px;outline:none}
.btn{padding:9px 16px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-size:13px;font-weight:600;display:inline-flex;align-items:center;gap:7px}
.btn:hover{border-color:var(--line2)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{background:var(--accent-d)}
.btn.danger{color:var(--bad);border-color:rgba(242,73,85,.3)}
.btn.danger:hover{background:rgba(242,73,85,.08)}
.btn.sm{padding:6px 11px;font-size:12px}
.btn:disabled{opacity:.5;cursor:not-allowed}

/* stat cards */
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin-bottom:22px}
.stat-card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.stat-card .sc-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.stat-card .sc-icon{width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px}
.stat-card .sc-val{font-size:22px;font-weight:800}
.stat-card .sc-label{font-size:11.5px;color:var(--sub);margin-top:2px}

/* table */
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{text-align:right;padding:12px 14px;background:var(--panel2);color:var(--sub);font-weight:700;font-size:11.5px;border-bottom:1px solid var(--line)}
tbody td{padding:11px 14px;border-bottom:1px solid var(--line);vertical-align:middle}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(255,255,255,.015)}
.mono{font-family:ui-monospace,Consolas,monospace;direction:ltr;text-align:left;font-size:12px;color:var(--sub)}
.badge{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:100px;font-size:11px;font-weight:700}
.badge.green{background:rgba(34,197,139,.14);color:var(--good)}
.badge.red{background:rgba(242,73,85,.14);color:var(--bad)}
.badge.gray{background:rgba(135,146,168,.14);color:var(--sub)}
.badge.orange{background:rgba(245,165,36,.14);color:var(--warn)}
.row-actions{display:flex;gap:6px;justify-content:flex-end}
.iconbtn{width:29px;height:29px;border-radius:7px;background:var(--panel2);border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;color:var(--sub);font-size:14px}
.iconbtn:hover{color:var(--text);border-color:var(--line2)}
.empty{padding:50px 20px;text-align:center;color:var(--sub2)}
.empty i{font-size:30px;display:block;margin-bottom:10px}
.bar-mini{width:70px;height:6px;background:var(--line2);border-radius:99px;overflow:hidden;display:inline-block;vertical-align:middle;margin-left:6px}
.bar-mini i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--good))}


/* ===== Appearance Studio ===== */
.appearance-studio{display:grid;grid-template-columns:1.25fr .75fr;gap:14px;margin-bottom:18px}.appearance-card{padding:18px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(145deg,rgba(124,92,255,.07),rgba(255,255,255,.018));overflow:hidden}.appearance-card h3{font-size:14px;margin-bottom:4px}.appearance-card p{font-size:10.5px;color:var(--sub);line-height:1.8}.appearance-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:14px}.appearance-field{padding:11px;border:1px solid var(--line);border-radius:12px;background:var(--panel2)}.appearance-field label{display:block;color:var(--sub);font-size:10px;margin-bottom:7px}.appearance-field select{width:100%;padding:9px 10px;border-radius:9px;border:1px solid var(--line);background:var(--panel);color:var(--text);outline:none}.theme-pills,.accent-pills{display:flex;gap:7px;flex-wrap:wrap}.theme-pill,.accent-pill{border:1px solid var(--line);background:var(--panel);color:var(--sub);border-radius:9px;padding:8px 11px;font-size:10px;cursor:pointer}.theme-pill.on,.accent-pill.on{color:#fff;border-color:var(--accent);background:rgba(124,92,255,.14)}.accent-pill{display:flex;align-items:center;gap:6px}.accent-dot{width:10px;height:10px;border-radius:50%;display:inline-block}.appearance-preview{min-height:100%;position:relative;display:flex;align-items:center;justify-content:center}.preview-window{width:100%;max-width:330px;border:1px solid var(--line);border-radius:15px;background:var(--panel);overflow:hidden;box-shadow:0 25px 60px rgba(0,0,0,.22)}.preview-top{height:36px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:6px;padding:0 10px}.preview-top i{font-size:10px;color:var(--sub)}.preview-main{display:grid;grid-template-columns:82px 1fr;min-height:140px}.preview-side{padding:10px;border-left:1px solid var(--line);background:var(--panel2)}.preview-side div{height:22px;border-radius:6px;margin-bottom:6px;background:rgba(255,255,255,.04)}.preview-side div.active{background:linear-gradient(90deg,var(--accent),var(--accent-d))}.preview-content{padding:12px}.preview-content .pv-title{font-size:12px;font-weight:800}.preview-content .pv-sub{font-size:8px;color:var(--sub);margin-top:3px}.pv-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:14px}.pv-cards span{height:45px;border-radius:9px;border:1px solid var(--line);background:rgba(255,255,255,.02)}.appearance-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}.appearance-toggle{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 11px;border:1px solid var(--line);border-radius:11px;background:var(--panel2);font-size:10.5px;color:var(--sub)}.switch{width:38px;height:21px;border-radius:99px;background:var(--line2);position:relative;cursor:pointer;border:0}.switch:after{content:'';position:absolute;width:15px;height:15px;top:2px;right:2px;border-radius:50%;background:#fff;transition:.16s}.switch.on{background:var(--accent)}.switch.on:after{right:21px}.density-compact .tab{padding-top:8px;padding-bottom:8px}.density-compact .body-wrap{padding-top:16px;padding-bottom:45px}.density-compact .card{border-radius:12px}.no-motion *, .no-motion *:before, .no-motion *:after{transition:none!important;animation:none!important;scroll-behavior:auto!important}
@media(max-width:900px){.appearance-studio{grid-template-columns:1fr}}@media(max-width:600px){.appearance-grid{grid-template-columns:1fr}.preview-window{max-width:none}}

.advanced-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:14px}.pro-action{border:1px solid var(--line);background:linear-gradient(145deg,var(--panel2),rgba(124,92,255,.05));color:var(--text);border-radius:14px;padding:15px;text-align:right;cursor:pointer;box-shadow:var(--ui-glow);}.pro-action i{font-size:20px;color:var(--accent);display:block;margin-bottom:10px}.pro-action b{display:block;font-size:11px}.pro-action small{display:block;color:var(--sub);font-size:9px;margin-top:4px}.accent-pills{max-height:92px;overflow:auto}.radius-sharp .card,.radius-sharp .appearance-card,.radius-sharp .appearance-field,.radius-sharp .btn,.radius-sharp .tab,.radius-sharp .search input{border-radius:6px}.radius-pill .card,.radius-pill .appearance-card,.radius-pill .appearance-field{border-radius:24px}.radius-pill .btn,.radius-pill .tab,.radius-pill .search input{border-radius:999px}.font-small{font-size:92%}.font-large{font-size:108%}.appearance-card,.card,.pro-action{box-shadow:var(--ui-glow)}
@media(max-width:900px){.advanced-grid{grid-template-columns:1fr 1fr}}@media(max-width:600px){.advanced-grid{grid-template-columns:1fr}}

.ib-quickstats{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 14px}.ib-quickstats>div{position:relative;overflow:hidden;display:flex;align-items:center;gap:10px;padding:12px 15px;border:1px solid var(--line);background:linear-gradient(155deg,rgba(255,255,255,.03),rgba(255,255,255,.01));border-radius:14px;flex:1;min-width:150px;transition:transform .15s ease,border-color .15s ease}.ib-quickstats>div:hover{transform:translateY(-2px);border-color:var(--line2)}.ib-quickstats i{width:32px;height:32px;display:grid;place-items:center;border-radius:9px;background:rgba(124,92,255,.12);color:#a997ff;font-size:15px;flex-shrink:0}.ib-quickstats b{display:block;font-size:17px;line-height:1.2}.ib-quickstats small{display:block;color:var(--sub2);font-size:9.5px;margin-top:2px}
/* ===== Inbound cards (grid) ===== */
.ib-listbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 12px;flex-wrap:wrap}
.ib-selectall{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--sub);cursor:pointer;user-select:none}
.ib-selectall input{width:15px;height:15px;accent-color:var(--accent);cursor:pointer}
.ib-count{font-size:11px;color:var(--sub2)}
.ib-bulkbar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 16px;background:linear-gradient(90deg,rgba(148,85,255,.12),rgba(148,85,255,.04));border:1px solid rgba(148,85,255,.28);border-radius:13px;font-size:11.5px;color:var(--sub);flex-wrap:wrap;margin-bottom:12px}
.ib-bulkbar b{color:var(--text)}.ib-bulkactions{display:flex;gap:6px}
.ib-check{width:15px;height:15px;accent-color:var(--accent);cursor:pointer}

.ib-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(328px,1fr));gap:14px}
.ib-card{position:relative;display:flex;flex-direction:column;gap:13px;padding:16px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(165deg,rgba(255,255,255,.035),rgba(255,255,255,.012));box-shadow:var(--shadow-sm);overflow:hidden;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}
.ib-card:before{content:'';position:absolute;inset:0 0 auto 0;height:3px;background:linear-gradient(90deg,var(--accent),#39d6ff)}
.ib-card:hover{border-color:var(--line2);box-shadow:var(--shadow-md)}
.ib-card.ib-off{opacity:.58}
.ib-card.ib-off:before{background:var(--sub2)}
.ib-card.ib-off:hover{opacity:.85}
.ib-card.ib-selected{border-color:var(--accent);box-shadow:0 0 0 3px rgba(148,85,255,.14)}

.ib-card-head{display:flex;align-items:flex-start;gap:11px}
.ib-card-check{position:absolute;top:14px;left:14px;opacity:0;pointer-events:none;transition:opacity .15s ease}
.ib-card:hover .ib-card-check,.ib-card.ib-selected .ib-card-check{opacity:1;pointer-events:auto}
.ib-avatar{width:40px;height:40px;border-radius:12px;flex-shrink:0;display:grid;place-items:center;font-size:17px;background:rgba(148,85,255,.14);color:#b79bff;border:1px solid rgba(148,85,255,.22)}
.ib-card-id{flex:1;min-width:0;padding-left:20px}
.ib-card-id .ib-name-top{display:flex;align-items:center;gap:6px}
.ib-card-id b{font-size:13px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;display:block}
.ib-card-id .mono{font-size:9.5px;color:var(--sub2);margin-top:2px}
.ib-card-controls{display:flex;flex-direction:column;align-items:flex-end;gap:7px;flex-shrink:0}

.ib-tagrow{display:flex;flex-wrap:wrap;gap:5px}
.ib-tagrow span{padding:3px 8px;border-radius:7px;background:var(--panel2);border:1px solid var(--line);font-size:9.5px;font-weight:700;letter-spacing:.01em;color:var(--sub);white-space:nowrap;transition:border-color .12s ease}
.ib-card:hover .ib-tagrow span{border-color:var(--line2)}
.ib-live-tag{background:rgba(34,197,139,.14)!important;color:var(--good)!important;border-color:transparent!important;display:inline-flex!important;align-items:center;gap:4px}
.ib-live-tag i{width:5px;height:5px;border-radius:50%;background:var(--good);animation:ibLivePulse 1.6s ease-in-out infinite;flex-shrink:0}
@keyframes ibLivePulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.35);opacity:.6}}
.no-motion .ib-live-tag i{animation:none}
.ib-linkonly-tag{background:rgba(242,73,85,.12)!important;color:var(--bad)!important;border-color:transparent!important}

.ib-card-addr{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 11px;border-radius:10px;background:var(--panel2);border:1px solid var(--line)}
.ib-card-addr span.mono{font-size:11px;color:var(--text)}
.ib-card-addr small{font-size:9px;color:var(--sub2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:110px}

.ib-card-traffic{display:flex;flex-direction:column;gap:6px}
.ib-card-traffic .ib-tf-top{display:flex;align-items:center;justify-content:space-between;font-size:9.5px;color:var(--sub2)}
.ib-card-traffic .ib-tf-top b{font-size:11.5px;color:var(--text);font-weight:800}
.ib-progress{height:6px;border-radius:99px;background:var(--line2);overflow:hidden;box-shadow:inset 0 0 0 1px var(--line)}
.ib-progress i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),#39d6ff);transition:width .3s ease}
.ib-progress i.warn{background:linear-gradient(90deg,#f5a524,#f59e0b)}
.ib-progress i.crit{background:linear-gradient(90deg,#f24955,#ef4444)}

.ib-card-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}
.ib-card-stats>div{padding:8px 9px;border-radius:10px;background:var(--panel2);border:1px solid var(--line);text-align:center}
.ib-card-stats small{display:block;color:var(--sub2);font-size:8.5px;margin-bottom:3px}
.ib-card-stats b{font-size:11px}
.ib-card-stats b.soon{color:var(--warn)}
.ib-card-stats b.expired{color:var(--bad)}

.ib-card-foot{display:flex;align-items:center;justify-content:space-between;gap:8px;padding-top:2px;border-top:1px dashed var(--line);padding-top:11px}
.ib-card-foot .ib-clientcell{display:flex;align-items:center;gap:7px;font-size:10.5px;color:var(--sub)}
.ib-card-foot .ib-clientcell .iconbtn{width:27px;height:27px;font-size:12px}
.ib-card-actions{display:flex;gap:5px}
.ib-card-actions .iconbtn{width:29px;height:29px;font-size:13px;border-radius:9px;transition:transform .12s ease,background-color .12s ease,color .12s ease}
.ib-card-actions .iconbtn:hover{transform:translateY(-1px);background:var(--panel2)}

.ib-switch{width:34px;height:19px;border-radius:99px;background:var(--line2);position:relative;cursor:pointer;border:0;flex-shrink:0;box-shadow:inset 0 0 0 1px var(--line)}
.ib-switch:after{content:'';position:absolute;width:13px;height:13px;top:3px;right:3px;border-radius:50%;background:#fff;transition:.16s}
.ib-switch.on{background:linear-gradient(90deg,var(--accent),#39d6ff);box-shadow:0 0 12px rgba(148,85,255,.35)}
.ib-switch.on:after{right:18px}
.ib-status-dot{width:8px;height:8px;border-radius:50%;background:#7688a9;flex-shrink:0}
.ib-status-dot.green{background:#22c58b;box-shadow:0 0 0 3px rgba(34,197,139,.18);animation:ibLivePulse 1.6s ease-in-out infinite}
.ib-status-dot.red{background:#f24955}
.no-motion .ib-status-dot{animation:none}
@media(max-width:560px){.ib-grid{grid-template-columns:1fr}}
.ov-quickstats>div{position:relative;overflow:hidden}
.ov-quickstats>div:nth-child(1) i{background:rgba(124,92,255,.14);color:#a997ff}
.ov-quickstats>div:nth-child(2) i{background:rgba(34,197,139,.14);color:#22c58b}
.ov-quickstats>div:nth-child(3) i{background:rgba(53,214,255,.14);color:#35d6ff}
.ov-quickstats>div:nth-child(4) i{background:rgba(245,165,36,.14);color:#f5a524}
.ov-toplinks{padding:14px 18px}
.ov-toplink-row{display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px dashed var(--line)}
.ov-toplink-row:last-child{border-bottom:none}
.ov-toplink-row .otl-rank{width:20px;height:20px;border-radius:6px;background:var(--panel2);display:grid;place-items:center;font-size:10px;color:var(--sub2);flex-shrink:0}
.ov-toplink-row .otl-info{flex:1;min-width:0}
.ov-toplink-row .otl-info b{font-size:11.5px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ov-toplink-row .otl-bar{height:4px;border-radius:99px;background:var(--line2);margin-top:5px;overflow:hidden}
.ov-toplink-row .otl-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),#39d6ff);border-radius:99px}
.ov-toplink-row .otl-val{font-size:10px;color:var(--sub2);white-space:nowrap;flex-shrink:0}
.ov-empty{padding:20px;text-align:center;color:var(--sub2);font-size:11px}
@media(max-width:900px){.ib-quickstats{flex-direction:column}}

/* drawer */
.overlay{position:fixed;inset:0;background:rgba(4,6,10,.55);backdrop-filter:blur(2px);z-index:90;display:none}
.overlay.show{display:block}
.drawer{position:fixed;top:0;left:0;bottom:0;width:680px;max-width:92vw;background:var(--panel);border-left:1px solid var(--line);z-index:91;transform:translateX(-105%);transition:transform .22s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column}
.drawer.show{transform:translateX(0)}
.dr-head{padding:18px 20px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}
.dr-head h3{font-size:15px;font-weight:800}
.dr-body{flex:1;overflow:auto;padding:18px 20px}
.dr-foot{padding:16px 20px;border-top:1px solid var(--line);display:flex;gap:10px}
.grp{margin-bottom:16px}
.grp label{display:block;font-size:12px;font-weight:600;color:var(--sub);margin-bottom:6px}
.grp input,.grp select,.grp textarea{width:100%;padding:10px 12px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--text);font-size:13px;outline:none}
.grp input:focus,.grp select:focus,.grp textarea:focus{border-color:var(--accent)}
.grp textarea{resize:vertical;min-height:64px;font-family:ui-monospace,monospace;direction:ltr;text-align:left}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.chk{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--text)}
.hint{font-size:11px;color:var(--sub2);margin-top:5px;line-height:1.7}
.divider{height:1px;background:var(--line);margin:18px 0}
.inbound-builder{display:flex;flex-direction:column;gap:16px}
.ib-hero{padding:16px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(135deg,rgba(79,124,255,.10),rgba(168,85,247,.07));display:flex;align-items:center;justify-content:space-between;gap:12px}
.ib-hero .ib-title{display:flex;align-items:center;gap:12px}.ib-hero .ib-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(135deg,var(--accent),#6d5dfc);color:#fff;font-size:20px;box-shadow:0 10px 24px rgba(79,124,255,.22)}
.ib-hero b{display:block;font-size:14px}.ib-hero small{display:block;color:var(--sub);font-size:11px;margin-top:3px}
.ib-section{border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.018);overflow:hidden}.ib-section-head{padding:12px 14px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}.ib-section-head b{font-size:12.5px}.ib-section-head small{font-size:10.5px;color:var(--sub2)}
.ib-section-body{padding:14px}.ib-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.ib-grid.three{grid-template-columns:1fr 1fr 1fr}.ib-full{grid-column:1/-1}
.ib-choice{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
/* Professional inbound protocol/transport matrix — renamed to .ib-opt (was
   accidentally reusing the .ib-card class name used by the main inbound
   dashboard cards above; that collision was overriding the dashboard card
   layout with these small radio-tile rules). */
.ib-matrix{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}
.ib-opt{position:relative;display:flex;align-items:center;gap:10px;padding:12px;border:1px solid var(--line);border-radius:12px;background:linear-gradient(145deg,rgba(255,255,255,.025),rgba(255,255,255,.01));cursor:pointer;transition:.16s;user-select:none}
.ib-opt:hover{border-color:rgba(168,85,247,.45);transform:translateY(-1px)}
.ib-opt.on{border-color:var(--accent);background:linear-gradient(145deg,rgba(124,58,237,.18),rgba(168,85,247,.08));box-shadow:0 8px 24px rgba(124,58,237,.12),inset 0 0 0 1px rgba(168,85,247,.18)}
.ib-opt.off{opacity:.42;cursor:not-allowed;filter:saturate(.5)}
.ib-opt input{position:absolute;opacity:0;pointer-events:none}
.ib-opt .ib-opt-icon{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:rgba(255,255,255,.05);color:var(--accent);font-size:17px;flex:0 0 auto}
.ib-opt b{display:block;font-size:11.5px}.ib-opt small{display:block;color:var(--sub2);font-size:8.5px;margin-top:2px}
.ib-step{display:flex;align-items:center;gap:8px;margin-bottom:11px}.ib-step .num{width:24px;height:24px;border-radius:8px;display:grid;place-items:center;background:rgba(124,58,237,.16);color:#c9a8ff;font-size:10px;font-weight:900}.ib-step b{font-size:12px}.ib-step small{display:block;color:var(--sub2);font-size:9px;margin-top:2px}
.ib-divider{height:1px;background:var(--line);margin:15px 0}
.ib-mode-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.ib-mini{padding:9px;border:1px solid var(--line);border-radius:10px;background:var(--panel2);font-size:10px;text-align:center;color:var(--sub)}
.ib-mini b{display:block;color:var(--text);font-size:11px;margin-bottom:2px}
.ib-mini.active{border-color:rgba(34,197,139,.35);background:rgba(34,197,139,.06)}
@media(max-width:700px){.ib-matrix{grid-template-columns:repeat(2,1fr)}.ib-mode-grid{grid-template-columns:repeat(2,1fr)}}
.ib-choice label{position:relative}.ib-choice input{position:absolute;opacity:0;pointer-events:none}.ib-choice span{display:flex;align-items:center;gap:8px;padding:10px 11px;border:1px solid var(--line);border-radius:10px;background:var(--panel2);font-size:12px;cursor:pointer;transition:.15s}.ib-choice span i{font-size:15px;color:var(--sub)}.ib-choice input:checked+span{border-color:var(--accent);background:rgba(79,124,255,.12);box-shadow:inset 0 0 0 1px rgba(79,124,255,.25)}.ib-choice input:checked+span i{color:var(--accent)}
.ib-status{padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:rgba(0,0,0,.12);font-size:11px;line-height:1.8}.ib-status.ok{border-color:rgba(34,197,139,.3);background:rgba(34,197,139,.07)}.ib-status.warn{border-color:rgba(245,165,36,.3);background:rgba(245,165,36,.07)}
.ib-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.ib-summary .sum{padding:9px 10px;border:1px solid var(--line);border-radius:9px;background:var(--panel2)}.ib-summary small{display:block;color:var(--sub2);font-size:9.5px}.ib-summary b{display:block;margin-top:3px;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ib-advanced{display:none}.ib-advanced.open{display:block}.ib-advanced-toggle{width:100%;justify-content:space-between}.ib-help{font-size:10.5px;color:var(--sub2);line-height:1.8;margin-top:6px}.ib-danger{color:#ff9b9b}
@media(max-width:600px){.ib-grid,.ib-grid.three,.ib-choice,.ib-summary{grid-template-columns:1fr}.ib-full{grid-column:auto}}

.section-title{font-size:12px;font-weight:800;color:var(--sub);text-transform:uppercase;letter-spacing:.03em;margin-bottom:10px}

/* ===== Message Center ===== */
.message-center{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}.message-stat{padding:15px;border:1px solid var(--line);border-radius:15px;background:linear-gradient(145deg,var(--panel),rgba(124,92,255,.04));position:relative;overflow:hidden}.message-stat:after{content:"";position:absolute;inset:auto -20px -30px auto;width:90px;height:90px;border-radius:50%;background:radial-gradient(circle,var(--accent),transparent 68%);opacity:.08}.message-stat .ms-icon{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:rgba(124,92,255,.12);color:var(--accent);margin-bottom:10px}.message-stat b{font-size:22px;display:block}.message-stat small{display:block;color:var(--sub);font-size:9px;margin-top:4px}.message-stat.danger .ms-icon{color:#fb7185;background:rgba(244,63,94,.11)}.message-stat.warn .ms-icon{color:#fbbf24;background:rgba(245,158,11,.11)}.message-stat.good .ms-icon{color:#34d399;background:rgba(16,185,129,.11)}.message-toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.message-filter{display:flex;gap:6px;flex-wrap:wrap}.message-filter button{padding:7px 10px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--sub);font-size:10px;cursor:pointer}.message-filter button.on{border-color:var(--accent);color:var(--text);background:rgba(124,92,255,.12)}.message-list{display:flex;flex-direction:column;gap:8px;padding:12px}.message-row{display:grid;grid-template-columns:38px 1fr auto;gap:10px;align-items:start;padding:12px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.015)}.message-row:hover{border-color:color-mix(in srgb,var(--accent) 40%,var(--line));background:rgba(255,255,255,.025)}.message-row .mi{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:rgba(255,255,255,.04);color:var(--sub)}.message-row.err .mi{color:#fb7185;background:rgba(244,63,94,.09)}.message-row.warn .mi{color:#fbbf24;background:rgba(245,158,11,.09)}.message-row.ok .mi{color:#34d399;background:rgba(16,185,129,.09)}.message-row .mt{min-width:0}.message-row .mt b{font-size:11px;display:block;line-height:1.8}.message-row .mt p{font-size:9px;color:var(--sub);margin-top:3px;word-break:break-word;line-height:1.8}.message-row .meta{text-align:left;direction:ltr;color:var(--sub2);font-size:8px;white-space:nowrap}.message-row .meta strong{display:block;color:var(--sub);font-size:9px;margin-bottom:3px}.error-detail{margin-top:8px;padding:9px;border-radius:9px;background:rgba(0,0,0,.16);border:1px dashed var(--line);font-family:ui-monospace,Consolas,monospace;font-size:8px;line-height:1.8;direction:ltr;text-align:left;white-space:pre-wrap;word-break:break-word;color:#aeb9d2;max-height:120px;overflow:auto}.message-empty{padding:45px 20px;text-align:center;color:var(--sub);font-size:11px}.message-empty i{display:block;font-size:34px;color:var(--good);margin-bottom:10px}.message-auto{font-size:9px;color:var(--sub2);margin-right:auto}@media(max-width:900px){.message-center{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.message-center{grid-template-columns:1fr 1fr}.message-row{grid-template-columns:34px 1fr}.message-row .meta{grid-column:2;text-align:right;direction:rtl}.message-auto{display:none}}
/* toast */
#toastWrap{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:200;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--panel2);border:1px solid var(--line2);padding:11px 18px;border-radius:10px;font-size:13px;display:flex;align-items:center;gap:9px;box-shadow:0 10px 30px rgba(0,0,0,.4);animation:up .18s ease}
.toast.ok{border-color:rgba(34,197,139,.4)}.toast.ok i{color:var(--good)}
.toast.err{border-color:rgba(242,73,85,.4)}.toast.err i{color:var(--bad)}
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

.qr-box{background:#fff;padding:10px;border-radius:12px;width:150px;height:150px;margin:0 auto 12px}
.qr-box img{width:100%;height:100%}
.copy-row{display:flex;gap:8px}
.copy-row input{flex:1}

.two-col{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}
@media(max-width:980px){.two-col{grid-template-columns:1fr}}
.status-dot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-left:6px}
.status-dot.on{background:var(--good);box-shadow:0 0 0 3px rgba(34,197,139,.18)}
.status-dot.off{background:var(--sub2)}
.settings-card{padding:20px}
.link-cell{display:flex;flex-direction:column;gap:2px}
.link-cell b{font-size:13px}
.link-cell span{font-size:11px;color:var(--sub2)}
.loading{opacity:.5;pointer-events:none}

/* VodiWalker 17 — original premium control-center skin */
body{background:radial-gradient(900px 500px at 75% -10%,rgba(124,92,255,.10),transparent 65%),var(--bg)}
/* رفع باگ اصلیِ «پوسته روشن»: پیش‌تر پس‌زمینه‌ی سایدبار و نوار بالا همیشه
   با رنگ ثابت تیره نوشته شده بود و data-theme را نادیده می‌گرفت؛ در نتیجه
   با فعال کردن پوسته‌ی روشن، فقط بدنه‌ی صفحه سفید می‌شد ولی سایدبار/تاپ‌بار
   تیره می‌ماند (ظاهر ناقص و دو رنگ). این‌جا هر دو حالت را صریحاً تعریف می‌کنیم. */
[data-theme="dark"] .sidebar,
:root:not([data-theme]) .sidebar{background:linear-gradient(180deg,#0d111b 0%,#0b0f17 100%);box-shadow:inset -1px 0 rgba(255,255,255,.04),20px 0 60px rgba(0,0,0,.16)}
[data-theme="light"] .sidebar{background:linear-gradient(180deg,#ffffff 0%,#f7f8fb 100%);box-shadow:inset -1px 0 rgba(0,0,0,.04),20px 0 50px rgba(30,34,60,.05)}
.sidebar{width:268px}
.sidebar-brand{padding:18px 20px 17px}.sidebar-brand img{width:38px;height:38px;border-radius:12px}.sidebar-brand div{font-size:15px}.sidebar-brand small{color:var(--sub2)}
.tab{padding:11px 14px;border-radius:11px;margin:2px 0}.tab-locked{opacity:.58}.tab-locked:hover{opacity:.85}.tab.on{background:linear-gradient(135deg,var(--accent),var(--accent-d));box-shadow:0 10px 25px -10px rgba(124,92,255,.55)}
[data-theme="dark"] .topbar,
:root:not([data-theme]) .topbar{height:68px;padding:0 26px;background:rgba(13,17,27,.88);backdrop-filter:none;box-shadow:0 1px 0 rgba(255,255,255,.025)}
[data-theme="light"] .topbar{height:68px;padding:0 26px;background:rgba(255,255,255,.88);backdrop-filter:none;box-shadow:0 1px 0 rgba(30,34,60,.04)}
.body-wrap{padding:24px 28px 70px}.page{max-width:1440px}
.pg-head{margin-bottom:18px}.pg-head h1{font-size:22px;letter-spacing:-.4px}.pg-head p{font-size:12px}
.eyebrow{font-size:10px;letter-spacing:.16em;color:#8d82c9;font-weight:800;margin-bottom:7px}.live-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#22c58b;box-shadow:0 0 0 4px rgba(34,197,139,.10);vertical-align:middle;margin-left:5px}
.stat-grid{gap:12px}.stat-card{border-radius:16px;padding:16px 18px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.018));box-shadow:var(--shadow-sm)}
.card{border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.018));box-shadow:var(--shadow-sm)}
.inbound-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 16px}.inbound-strip>div{display:flex;align-items:center;gap:11px;padding:13px 15px;border:1px solid var(--line);background:rgba(255,255,255,.018);border-radius:13px}.inbound-strip i{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:rgba(124,92,255,.12);color:#a997ff;font-size:17px}.inbound-strip b{display:block;font-size:12px}.inbound-strip small{display:block;color:var(--sub);font-size:10px;margin-top:2px}.btn-inbound{padding-left:20px;padding-right:20px;box-shadow:0 12px 30px -12px rgba(124,92,255,.75)}
.endpoint-input{display:flex;gap:7px;align-items:stretch}.endpoint-input input{flex:1;min-width:0}.endpoint-btn{white-space:nowrap;padding:9px 11px;font-size:11px}.endpoint-btn:disabled{opacity:.65}.ib-status.ok{border-color:rgba(34,197,139,.35)!important}.ib-status.warn{border-color:rgba(245,165,36,.35)!important}@media(max-width:800px){.inbound-strip{grid-template-columns:1fr}.body-wrap{padding:18px 14px 60px}}

.resource-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}.resource-card{min-height:126px;padding:13px 15px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.015));overflow:hidden}.rc-head{display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--sub);font-weight:800;letter-spacing:.08em}.rc-head i{margin-left:5px;color:#7688a9}.rc-head b{font-size:21px;color:var(--text);letter-spacing:0}.rc-sub{font-size:9px;color:var(--sub2);margin-top:6px}.spark{display:block;width:100%;height:44px;margin-top:9px}.spark polyline{fill:none;stroke:#557bff;stroke-width:2;vector-effect:non-scaling-stroke}.spark path{fill:rgba(85,123,255,.08);stroke:none}.traffic-layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(290px,.55fr);gap:14px;margin-bottom:14px}.traffic-card,.connection-card{padding:0}.panel-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--line)}.panel-head b{display:block;font-size:10px;letter-spacing:.09em}.panel-head small{display:block;color:var(--sub2);font-size:9px;margin-top:4px}.panel-head>i{color:var(--sub2)}.traffic-legend{display:flex;gap:14px;font-size:10px;color:var(--sub)}.traffic-legend b{color:var(--text)}.big-chart{height:250px;padding:10px 14px 0}.big-chart svg{width:100%;height:100%}.big-chart polyline{fill:none;stroke:#5b78d9;stroke-width:2;vector-effect:non-scaling-stroke}.big-chart .area{fill:rgba(91,120,217,.07);stroke:none}.traffic-foot{display:grid;grid-template-columns:1fr 1fr 1.5fr;padding:12px 16px;border-top:1px solid var(--line)}.traffic-foot small{display:block;color:var(--sub2);font-size:8px}.traffic-foot b{font-size:12px}.connection-number{font-size:28px;font-weight:900;padding:16px 18px 0}.connection-label{font-size:8px;color:var(--sub2);padding:2px 18px}.conn-chart{width:100%;height:120px;padding:0 12px}.conn-chart polyline{fill:none;stroke:#4f7cff;stroke-width:2;vector-effect:non-scaling-stroke}.conn-chart .area{fill:rgba(79,124,255,.08);stroke:none}.conn-foot{display:flex;justify-content:space-between;padding:10px 16px;border-top:1px solid var(--line);font-size:9px;color:var(--sub)}.conn-foot b{color:var(--text)}.bottom-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}.mini-panel{padding-bottom:10px}.health-row{display:flex;justify-content:space-between;padding:10px 16px;border-bottom:1px solid var(--line);font-size:11px}.health-row:last-child{border-bottom:0}.health-row span{color:var(--sub)}.health-row b{max-width:68%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.mono{direction:ltr;text-align:left}.mini-panel .panel-head .badge{font-size:8px}.inbound-head{align-items:center}@media(max-width:1050px){.resource-grid{grid-template-columns:repeat(2,1fr)}.traffic-layout{grid-template-columns:1fr}.bottom-grid{grid-template-columns:1fr}}@media(max-width:560px){.resource-grid{grid-template-columns:1fr}.traffic-foot{grid-template-columns:1fr;gap:10px}.big-chart{height:190px}}

.client-manager{display:flex;flex-direction:column;gap:12px}.client-hero{display:flex;justify-content:space-between;gap:12px;padding:14px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(135deg,rgba(124,92,255,.12),rgba(57,214,255,.04))}.client-hero b{display:block;font-size:13px}.client-hero small{display:block;color:var(--sub);font-size:10px;line-height:1.8;margin-top:4px}.client-create{padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--panel2)}.client-list{display:flex;flex-direction:column;gap:8px}.client-row{display:flex;align-items:center;gap:10px;padding:11px;border:1px solid var(--line);border-radius:13px;background:rgba(255,255,255,.018)}.client-avatar{width:38px;height:38px;display:grid;place-items:center;border-radius:11px;background:rgba(124,92,255,.12);color:var(--accent);font-size:17px}.client-main{flex:1;min-width:0}.client-main b{display:block;font-size:11px}.client-main small{display:block;color:var(--sub2);font-size:8px;margin-top:3px;overflow:hidden;text-overflow:ellipsis}.client-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.client-tags span{font-size:8px;color:var(--sub);padding:4px 6px;border:1px solid var(--line);border-radius:7px}.client-actions{display:flex;gap:5px}.empty-client{padding:24px;text-align:center;color:var(--sub2);font-size:10px}.danger-note{border-color:rgba(239,68,68,.3)!important}
.pro-diagnostics{overflow:hidden}.diag-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:14px}.diag-item{border:1px solid var(--line);border-radius:13px;padding:12px;background:rgba(255,255,255,.018)}.diag-item small,.diag-item span{display:block;color:var(--sub2);font-size:9px}.diag-item b{display:block;font-size:18px;margin:5px 0}.diag-empty{grid-column:1/-1;padding:22px;text-align:center;color:var(--sub2)}@media(max-width:900px){.diag-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.diag-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<script>(function(){
  // نکته (رفع باگ): قبلاً این اسکریپت اولیه از کلید localStorage جداگانه‌ای
  // به‌نام «vw_theme» می‌خواند که هیچ‌جای برنامه هرگز در آن چیزی نمی‌نوشت
  // (تنظیمات واقعی همیشه زیر کلید «vw_appearance» ذخیره می‌شود)، پس همیشه
  // مقدار پیش‌فرض «dark» اعمال می‌شد و باعث یک فلاش کوتاهِ پوسته‌ی اشتباه
  // در بارگذاری اولیه‌ی صفحه می‌شد، تا وقتی اسکریپت اصلی اجرا شود.
  try{
    var raw = localStorage.getItem('vw_appearance');
    var pref = raw ? (JSON.parse(raw).theme || 'dark') : 'dark';
    var resolved = pref === 'system'
      ? (matchMedia('(prefers-color-scheme:light)').matches ? 'light' : 'dark')
      : pref;
    document.documentElement.setAttribute('data-theme', resolved);
  }catch(e){ document.documentElement.setAttribute('data-theme','dark'); }
})();</script>
<div id="app">
  <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
  <div class="sidebar">
    <div class="sidebar-brand"><img src="data:image/png;base64,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"><div><span data-i18n="brand">VodiWalker</span><small>Control Center</small></div></div>
    <div class="tabnav" id="tabnav">
      <div class="tab on" data-pg="overview"><i class="ti ti-layout-dashboard"></i><span data-i18n="nav_overview">داشبورد</span></div>
      <div class="tab" data-pg="links"><i class="ti ti-network"></i><span data-i18n="nav_links">اینباندها</span><span class="bd" id="nb-links">0</span></div>
      <div class="tab" data-pg="clientmgr"><i class="ti ti-user-plus"></i><span data-i18n="nav_clientmgr">ساخت کلاینت</span></div>
      <div class="tab" data-pg="categories"><i class="ti ti-category"></i><span data-i18n="nav_categories">دسته‌بندی‌ها</span></div>
      <div class="tab" data-pg="subgroups"><i class="ti ti-folders"></i><span data-i18n="nav_subgroups">گروه‌های ساب</span><span class="bd" id="nb-subs">0</span></div>
      <div class="tab tab-locked" data-pg="plans" title="در نسخه‌های بعد فعال می‌شود"><i class="ti ti-lock"></i><span data-i18n="nav_plans">پلن‌های فروش</span><span class="bd">بعداً</span></div>
      <div class="tab" data-pg="reports"><i class="ti ti-chart-histogram"></i><span data-i18n="nav_reports">گزارش‌ها</span></div>
      <div class="tab" data-pg="admins"><i class="ti ti-users-group"></i><span data-i18n="nav_admins">ادمین‌ها</span></div>
      <div class="tab" data-pg="activity"><i class="ti ti-history"></i><span data-i18n="nav_activity">فعالیت‌ها</span></div>
      <div class="tab" data-pg="messages"><i class="ti ti-bell-ringing"></i><span data-i18n="nav_messages">پیام‌ها</span><span class="bd danger-bd" id="nb-errors">0</span></div>
      <div class="tab" data-pg="settings"><i class="ti ti-settings"></i><span data-i18n="nav_settings">تنظیمات</span></div>
    </div>
    <div class="sidebar-foot">
      <div class="lang-mini">
        <button id="dashLangFa" class="on" onclick="setDashLang('fa')">فا</button>
        <button id="dashLangEn" onclick="setDashLang('en')">EN</button>
      </div>
      <div class="user-chip" id="userChip"><div class="av">V</div><span id="userName">...</span></div>
    </div>
  </div>

  <div class="main-col">
  <div class="topbar">
    <button class="hamburger" onclick="toggleSidebar()"><i class="ti ti-menu-2"></i></button>
    <div class="page-title"><span id="pageTitleMain" data-i18n="nav_overview">داشبورد</span><span id="pageTitleSub" data-i18n="pt_overview">وضعیت لحظه‌ای سرویس، کانفیگ‌ها و ربات فروش</span></div>
    <div class="top-right">
      <button class="icon-btn" id="themeToggle" onclick="toggleTheme()" title="تغییر پوسته"><i class="ti ti-moon"></i></button>
      <a class="icon-btn" href="/logout" title="خروج"><i class="ti ti-logout"></i></a>
    </div>
  </div>

  <div class="body-wrap">

    <!-- OVERVIEW -->
    <div class="page on" id="pg-overview">
      <div class="pg-head"><div><div class="eyebrow"><span class="live-dot"></span> LIVE SYSTEM MONITOR</div><h1>مرکز کنترل VodiWalker</h1><p>نمای لحظه‌ای منابع سرور، ترافیک، اتصال‌ها و سرویس فروش.</p></div>
        <div class="toolbar"><button class="btn" onclick="refreshOverview()"><i class="ti ti-refresh"></i>بروزرسانی</button><button class="btn primary" onclick="gotoPage('links')"><i class="ti ti-network"></i>اینباندها</button></div></div>
      <div class="ib-quickstats ov-quickstats" id="ovBizStats"></div>
      <div class="resource-grid" id="resourceGrid">
        <div class="resource-card"><div class="rc-head"><span><i class="ti ti-cpu"></i> CPU</span><b id="cpuVal">—</b></div><div class="rc-sub" id="cpuSub">در حال دریافت...</div><svg class="spark" id="cpuSpark" viewBox="0 0 240 46" preserveAspectRatio="none"></svg></div>
        <div class="resource-card"><div class="rc-head"><span><i class="ti ti-device-ram"></i> RAM</span><b id="ramVal">—</b></div><div class="rc-sub" id="ramSub">—</div><svg class="spark" id="ramSpark" viewBox="0 0 240 46" preserveAspectRatio="none"></svg></div>
        <div class="resource-card"><div class="rc-head"><span><i class="ti ti-bolt"></i> SWAP</span><b id="swapVal">—</b></div><div class="rc-sub" id="swapSub">—</div><svg class="spark" id="swapSpark" viewBox="0 0 240 46" preserveAspectRatio="none"></svg></div>
        <div class="resource-card"><div class="rc-head"><span><i class="ti ti-database"></i> STORAGE</span><b id="storageVal">—</b></div><div class="rc-sub" id="storageSub">—</div><svg class="spark" id="storageSpark" viewBox="0 0 240 46" preserveAspectRatio="none"></svg></div>
      </div>
      <div class="traffic-layout">
        <div class="card traffic-card"><div class="panel-head"><div><b>OVERALL SPEED</b><small id="speedMeta">Network throughput</small></div><div class="traffic-legend"><span>↑ <b id="txRate">0 B/s</b></span><span>↓ <b id="rxRate">0 B/s</b></span></div></div><div class="big-chart"><svg id="trafficChart" viewBox="0 0 900 260" preserveAspectRatio="none"></svg></div><div class="traffic-foot"><div><small>SENT</small><b id="sentTotal">0 B</b></div><div><small>RECEIVED</small><b id="recvTotal">0 B</b></div><div><small>LIVE THROUGHPUT</small><b id="liveRate">↑ 0 B/s ↓ 0 B/s</b></div></div></div>
        <div class="card connection-card"><div class="panel-head"><div><b>CONNECTION STATS</b><small>Open sockets</small></div><i class="ti ti-plug-connected"></i></div><div class="connection-number" id="connVal">0</div><div class="connection-label">OPEN CONNECTIONS</div><svg class="conn-chart" id="connChart" viewBox="0 0 340 150" preserveAspectRatio="none"></svg><div class="conn-foot"><span>REQUESTS <b id="reqVal">0</b></span><span>ERRORS <b id="errVal">0</b></span></div></div>
      </div>
      <div class="bottom-grid">
        <div class="card mini-panel"><div class="panel-head"><div><b>SERVICE HEALTH</b><small>Runtime status</small></div><span class="badge green">ONLINE</span></div><div class="health-row"><span>Uptime</span><b id="uptimeVal">—</b></div><div class="health-row"><span>CPU Cores</span><b id="coresVal">—</b></div><div class="health-row"><span>Panel RAM</span><b id="procRamVal">—</b></div></div>
        <div class="card mini-panel"><div class="panel-head"><div><b>BOT SERVICES</b><small>Sales + management</small></div><span id="ovBotStatus" class="badge gray">CHECKING</span></div><div class="health-row"><span>Telegram Bot</span><b id="botStateText">—</b></div><div class="health-row"><span>Public URL</span><b class="mono" id="ovBaseUrl">—</b></div></div>
        <div class="card mini-panel"><div class="panel-head"><div><b>NETWORK</b><small>Host load</small></div><i class="ti ti-world"></i></div><div class="health-row"><span>Load</span><b id="loadVal">—</b></div><div class="health-row"><span>Traffic</span><b id="trafficTotalVal">0 B</b></div></div>
      </div>
      <div class="card mini-panel" style="margin-top:14px"><div class="panel-head"><div><b>TOP CONFIGS BY USAGE</b><small>پرمصرف‌ترین کانفیگ‌های ۷ روز اخیر</small></div><i class="ti ti-trending-up"></i></div><div id="ovTopLinks" class="ov-toplinks"></div></div>
    </div>

    <!-- LINKS -->
    <div class="page" id="pg-links">
      <div class="pg-head inbound-head"><div><div class="eyebrow"><span class="live-dot"></span> VODIWALKER CORE · <span id="ibLiveTag">LIVE</span></div><h1>اینباندها</h1><p>مرکز مدیریت اینباند، ساخت کلاینت و کنترل دسترسی؛ با پایش زنده هر ۵ ثانیه.</p></div>
        <div class="toolbar">
          <div class="search"><input id="linkSearch" placeholder="جستجوی اینباند / UUID..." oninput="renderLinks()"><i class="ti ti-search"></i></div>
          <select class="sel" id="linkFilterCat" onchange="renderLinks()"><option value="">همه دسته‌ها</option></select>
          <span id="ibUpdatedAt" style="font-size:9px;color:var(--sub2);align-self:center;white-space:nowrap">—</span>
          <button class="btn" id="ibRefreshBtn" onclick="refreshAllInbounds()"><i class="ti ti-refresh" id="ibRefreshIcon"></i>بروزرسانی همه</button>
          <button class="btn" onclick="openAutoLink()"><i class="ti ti-bolt"></i>ساخت سریع</button>
          <button class="btn primary btn-inbound" onclick="openLinkDrawer()"><i class="ti ti-plus"></i>اینباند جدید</button>
        </div>
      </div>
      <div class="ib-quickstats" id="ibQuickStats"></div>
      <div class="ib-listbar">
        <label class="ib-selectall"><input type="checkbox" id="ibSelAll" onchange="toggleAllLinks(this.checked)"><span>انتخاب همه</span></label>
        <span class="ib-count" id="ibCountLabel">0 اینباند</span>
      </div>
      <div class="ib-bulkbar" id="ibBulkBar" style="display:none">
        <span><b id="ibSelCount">0</b> مورد انتخاب شده</span>
        <div class="ib-bulkactions">
          <button class="btn sm" onclick="bulkToggleLinks(true)"><i class="ti ti-power"></i>فعال‌سازی</button>
          <button class="btn sm" onclick="bulkToggleLinks(false)"><i class="ti ti-power"></i>غیرفعال‌سازی</button>
          <button class="btn sm" style="color:var(--bad)" onclick="bulkDeleteLinks()"><i class="ti ti-trash"></i>حذف</button>
        </div>
      </div>
      <div class="ib-grid" id="ibGrid"></div>
      <div class="empty" id="linksEmpty" style="display:none"><i class="ti ti-inbox"></i>کانفیگی یافت نشد</div>
    </div>

    <!-- CLIENT MANAGER (بخش جدای ساخت کلاینت از روی اینباند) -->
    <div class="page" id="pg-clientmgr">
      <div class="pg-head"><div><div class="eyebrow"><span class="live-dot"></span> VODIWALKER · CLIENT MANAGER</div><h1>ساخت کلاینت</h1><p>یک اینباند را انتخاب کن و از روی همان کلاینت‌های واقعی (زیرمجموعه) بساز؛ بدون نیاز به رفتن به صفحه اینباندها.</p></div>
        <div class="toolbar"><button class="btn" onclick="loadClientManager()"><i class="ti ti-refresh"></i>بروزرسانی</button></div>
      </div>
      <div class="card" style="padding:18px;margin-bottom:14px">
        <div class="grp"><label>انتخاب اینباند</label>
          <select class="sel" id="cmInboundSelect" style="width:100%" onchange="loadClientManagerClients(this.value)"><option value="">— انتخاب کنید —</option></select>
        </div>
        <div id="cmInboundInfo"></div>
      </div>
      <div id="cmBody"></div>
    </div>

    <!-- CATEGORIES -->
    <div class="page" id="pg-categories">
      <div class="pg-head"><div><h1>دسته‌بندی‌ها</h1><p>پیش‌فرض‌های حجم، انقضا و محدودیت برای گروه‌های کانفیگ</p></div>
        <div class="toolbar"><button class="btn primary" onclick="openCategoryDrawer()"><i class="ti ti-plus"></i>دسته جدید</button></div>
      </div>
      <div class="card"><table><thead><tr><th>نام</th><th>حجم پیش‌فرض</th><th>انقضا (روز)</th><th>محدودیت IP</th><th></th></tr></thead><tbody id="catsBody"></tbody></table></div>
    </div>

    <!-- SUBGROUPS -->
    <div class="page" id="pg-subgroups">
      <div class="pg-head"><div><h1>گروه‌های ساب</h1><p>ترکیب چند کانفیگ در یک لینک اشتراک واحد</p></div>
        <div class="toolbar"><button class="btn primary" onclick="openSubGroupDrawer()"><i class="ti ti-plus"></i>گروه جدید</button></div>
      </div>
      <div class="card"><table><thead><tr><th>نام گروه</th><th>تعداد کانفیگ</th><th>لینک عمومی</th><th></th></tr></thead><tbody id="subsBody"></tbody></table></div>
    </div>

    <!-- PLANS -->
    <div class="page" id="pg-plans">
      <div class="pg-head"><div><h1>پلن‌های فروش</h1><p>پلن‌هایی که در ربات فروش تلگرام نمایش داده می‌شوند</p></div>
        <div class="toolbar"><button class="btn primary" onclick="openPlanDrawer()"><i class="ti ti-plus"></i>پلن جدید</button></div>
      </div>
      <div class="card"><table><thead><tr><th>نام</th><th>مدت</th><th>حجم</th><th>سرعت</th><th>قیمت (⭐)</th><th>ویژه</th><th></th></tr></thead><tbody id="plansBody"></tbody></table></div>
    </div>

    <!-- REPORTS -->
    <div class="page" id="pg-reports">
      <div class="pg-head"><div><h1>گزارش‌ها</h1><p>خلاصه‌ی عملکرد فروش و کانفیگ‌ها</p></div>
        <div class="toolbar">
          <select class="sel" id="repDays" onchange="loadReports()"><option value="7">۷ روز اخیر</option><option value="14" selected>۱۴ روز اخیر</option><option value="30">۳۰ روز اخیر</option></select>
          <a class="btn" href="/api/reports/export.csv"><i class="ti ti-download"></i>خروجی CSV</a>
        </div>
      </div>
      <div class="stat-grid" id="repStats"></div>
      <div class="card">
        <div style="padding:16px 18px;border-bottom:1px solid var(--line)"><b style="font-size:13px">پرمصرف‌ترین کانفیگ‌ها</b></div>
        <table><thead><tr><th>برچسب</th><th>پروتکل</th><th>مصرف</th></tr></thead><tbody id="repTopBody"></tbody></table>
      </div>
    </div>

    <!-- ADMINS -->
    <div class="page" id="pg-admins">
      <div class="pg-head"><div><div class="eyebrow"><span class="live-dot"></span> VODIWALKER · مدیریت حساب</div><h1>مدیریت حساب‌ها</h1><p>اینجا همه حساب‌های مدیریتی پنل را مرتب و دقیق مدیریت می‌کنیم؛ از ساخت ادمین تا تعیین دسترسی و کنترل وضعیت حساب.</p></div>
        <div class="toolbar"><button class="btn" onclick="loadAdmins()"><i class="ti ti-refresh"></i>همگام‌سازی</button><button class="btn primary" onclick="openAdminDrawer()"><i class="ti ti-user-plus"></i>ایجاد حساب مدیریتی</button></div>
      </div>
      <div class="admins-hero">
        <div class="access-command-copy"><div class="command-badge"><i class="ti ti-shield-lock"></i> مدیریت حساب‌ها</div><h2>مدیریت کامل ادمین‌ها</h2><p>حساب اصلی پنل دسترسی کامل دارد و برای هر ادمین می‌توان دسترسی‌های موردنیاز را جداگانه تعیین کرد. وضعیت هر حساب و آخرین ورود نیز از همین بخش قابل بررسی است.</p><div class="command-points"><span><i class="ti ti-check"></i> تفکیک دسترسی</span><span><i class="ti ti-check"></i> ثبت آخرین ورود</span><span><i class="ti ti-check"></i> امنیت حساب‌ها</span></div></div>
        <div class="admins-summary" id="adminsSummary"><div class="sum"><b id="adminTotal">—</b><small>حساب مدیریتی</small></div><div class="sum"><b id="adminActive">—</b><small>حساب فعال</small></div><div class="sum"><b id="adminOwner">1</b><small>مالک پنل</small></div></div>
      </div>
      <div class="card admin-directory" id="adminReqCard" style="margin-bottom:14px;display:none"><div class="panel-head"><div><b>درخواست‌های ثبت‌نام ادمینی</b><small>افرادی که از صفحه ورود درخواست همکاری داده‌اند؛ بررسی کن و تصمیم بگیر.</small></div><span class="command-badge" id="adminReqBadge">۰ درخواست</span></div><div id="adminReqBody" style="padding:14px 18px"></div></div>
      <div class="card admin-directory"><div class="panel-head"><div><b>فهرست ادمین‌ها</b><small>وضعیت، دسترسی و فعالیت هر ادمین را از یکجا بررسی و مدیریت کن.</small></div><span class="directory-live"><i></i> کنترل فعال</span></div><div class="admin-grid" id="adminsBody"></div></div>
    </div>

    <!-- ACTIVITY -->
    <div class="page" id="pg-activity">
      <div class="pg-head"><div><h1>لاگ فعالیت‌ها</h1><p>۱۵۰ رویداد اخیر پنل</p></div>
        <div class="toolbar"><button class="btn" onclick="loadActivity()"><i class="ti ti-refresh"></i>بروزرسانی</button></div>
      </div>
      <div class="card"><table><thead><tr><th>زمان</th><th>نوع</th><th>پیام</th></tr></thead><tbody id="activityBody"></tbody></table></div>
    </div>

    <!-- MESSAGES -->
    <div class="page" id="pg-messages">
      <div class="pg-head"><div><div class="eyebrow"><span class="live-dot"></span> MESSAGE CENTER</div><h1>مرکز پیام و خطا</h1><p>تمام خطاهای سرور، خطاهای مرورگر و رویدادهای مهم اینجا جمع می‌شوند تا هیچ خطایی گم نشود.</p></div><div class="toolbar"><span class="message-auto" id="messageLastSync">همگام‌سازی خودکار</span><button class="btn" onclick="loadMessages()"><i class="ti ti-refresh"></i>بروزرسانی</button><button class="btn danger" onclick="clearErrors()"><i class="ti ti-trash"></i>پاک‌کردن خطاها</button></div></div>
      <div class="message-center" id="messageStats"></div>
      <div class="card">
        <div class="panel-head"><div><b>خطاهای ثبت‌شده</b><small>خطاهای Backend و Frontend با جزئیات مسیر و زمان</small></div><div class="message-filter"><button class="on" data-message-filter="all" onclick="setMessageFilter('all')">همه</button><button data-message-filter="err" onclick="setMessageFilter('err')">خطا</button><button data-message-filter="warn" onclick="setMessageFilter('warn')">هشدار</button><button data-message-filter="client" onclick="setMessageFilter('client')">مرورگر</button></div></div>
        <div class="message-list" id="messageList"></div>
      </div>
      <div class="card" style="margin-top:14px"><div class="panel-head"><div><b>رویدادهای مهم</b><small>آخرین فعالیت‌های پنل برای عیب‌یابی سریع</small></div></div><div class="message-list" id="messageActivityList"></div></div>
    </div>

    <!-- SETTINGS -->
    <div class="page" id="pg-settings">
      <div class="pg-head"><div><div class="eyebrow">CONTROL CENTER / PERSONALIZATION</div><h1>تنظیمات و استودیو ظاهر</h1><p>ظاهر، فونت، رنگ، تراکم، زبان و تنظیمات عملیاتی پنل را از یکجا کنترل کن.</p></div><div class="toolbar"><button class="btn" onclick="resetAppearance()"><i class="ti ti-refresh"></i>بازنشانی ظاهر</button></div></div>

      <div class="appearance-studio">
        <div class="appearance-card">
          <h3>Appearance Studio</h3><p>تنظیمات ظاهری فقط برای همین مرورگر ذخیره می‌شوند و بدون دست‌زدن به اطلاعات سرور قابل تغییرند.</p>
          <div class="appearance-grid">
            <div class="appearance-field"><label>فونت رابط کاربری</label><select id="appearanceFont" onchange="setFont(this.value)"><option value="Vazirmatn">Vazirmatn</option><option value="Estedad">Estedad</option><option value="IBM Plex Sans Arabic">IBM Plex Sans Arabic</option><option value="Shabnam">Shabnam</option><option value="Yekan Bakh">Yekan Bakh</option><option value="Inter">Inter</option></select></div>
            <div class="appearance-field"><label>اندازه متن</label><div class="theme-pills"><button class="theme-pill" data-font-size="small" onclick="setFontSize('small')">Small</button><button class="theme-pill" data-font-size="normal" onclick="setFontSize('normal')">Normal</button><button class="theme-pill" data-font-size="large" onclick="setFontSize('large')">Large</button></div></div>
            <div class="appearance-field"><label>تراکم پنل</label><div class="theme-pills"><button class="theme-pill" data-density="comfortable" onclick="setDensity('comfortable')">Comfort</button><button class="theme-pill" data-density="compact" onclick="setDensity('compact')">Compact</button></div></div>
            <div class="appearance-field"><label>گوشه‌ها</label><div class="theme-pills"><button class="theme-pill" data-radius="soft" onclick="setRadius('soft')">Soft</button><button class="theme-pill" data-radius="sharp" onclick="setRadius('sharp')">Sharp</button><button class="theme-pill" data-radius="pill" onclick="setRadius('pill')">Pill</button></div></div>
            <div class="appearance-field"><label>پوسته</label><div class="theme-pills"><button class="theme-pill" data-theme-choice="dark" onclick="setAppearanceTheme('dark')">Dark</button><button class="theme-pill" data-theme-choice="light" onclick="setAppearanceTheme('light')">Light</button><button class="theme-pill" data-theme-choice="system" onclick="setAppearanceTheme('system')">System</button></div></div>
            <div class="appearance-field"><label>رنگ اصلی</label><div class="accent-pills"><button class="accent-pill" data-accent="purple" onclick="setAccent('purple')"><span class="accent-dot" style="background:#8b5cf6"></span>Purple</button><button class="accent-pill" data-accent="blue" onclick="setAccent('blue')"><span class="accent-dot" style="background:#3b82f6"></span>Blue</button><button class="accent-pill" data-accent="cyan" onclick="setAccent('cyan')"><span class="accent-dot" style="background:#06b6d4"></span>Cyan</button><button class="accent-pill" data-accent="green" onclick="setAccent('green')"><span class="accent-dot" style="background:#10b981"></span>Green</button><button class="accent-pill" data-accent="orange" onclick="setAccent('orange')"><span class="accent-dot" style="background:#f59e0b"></span>Orange</button><button class="accent-pill" data-accent="pink" onclick="setAccent('pink')"><span class="accent-dot" style="background:#ec4899"></span>Pink</button><button class="accent-pill" data-accent="red" onclick="setAccent('red')"><span class="accent-dot" style="background:#ef4444"></span>Red</button><button class="accent-pill" data-accent="indigo" onclick="setAccent('indigo')"><span class="accent-dot" style="background:#6366f1"></span>Indigo</button><button class="accent-pill" data-accent="teal" onclick="setAccent('teal')"><span class="accent-dot" style="background:#14b8a6"></span>Teal</button><button class="accent-pill" data-accent="gold" onclick="setAccent('gold')"><span class="accent-dot" style="background:#eab308"></span>Gold</button></div></div>
          </div>
          <div class="appearance-actions">
            <div class="appearance-toggle"><span>انیمیشن‌های پنل</span><button id="motionSwitch" class="switch" onclick="toggleMotion()"></button></div>
            <div class="appearance-toggle"><span>سایدبار باز در دسکتاپ</span><button id="wideSwitch" class="switch" onclick="toggleWideSidebar()"></button></div>
            <div class="appearance-toggle"><span>Glow / نورپردازی</span><button id="glowSwitch" class="switch" onclick="toggleGlow()"></button></div>
          </div>
        </div>
        <div class="appearance-card appearance-preview"><div class="preview-window"><div class="preview-top"><i class="ti ti-circle-filled"></i><i class="ti ti-circle-filled"></i><i class="ti ti-circle-filled"></i></div><div class="preview-main"><div class="preview-side"><div class="active"></div><div></div><div></div><div></div></div><div class="preview-content"><div class="pv-title">VodiWalker Control Center</div><div class="pv-sub">Live system overview</div><div class="pv-cards"><span></span><span></span><span></span></div></div></div></div></div>
      </div>

      <div class="card pro-diagnostics" style="margin-top:14px">
        <div class="panel-head"><div><b>SYSTEM HEALTH / LIVE DIAGNOSTICS</b><small>Live server, resource, object and security telemetry</small></div><div class="toolbar"><span id="diagStatus" class="badge green">READY</span><button class="btn" onclick="loadDiagnostics()"><i class="ti ti-activity"></i>Refresh</button></div></div>
        <div class="diag-grid" id="diagGrid"><div class="diag-empty">Press Refresh to inspect the live system.</div></div>
      </div>

      <div class="two-col">
        <div class="card settings-card">
          <div class="section-title">آدرس عمومی پنل</div>
          <p class="hint" style="margin-bottom:12px">برای لینک‌های Subscription، دامنه واقعی پنل را ثابت کن. روی Railway بهتر است دامنه عمومی سرویس را اینجا قرار بدهی.</p>
          <div class="grp"><input id="setBaseUrl" placeholder="https://panel.example.com"></div>
          <button class="btn primary" onclick="saveBaseUrl()"><i class="ti ti-device-floppy"></i>ذخیره آدرس</button>
          <div class="divider"></div><div class="section-title">امنیت حساب</div>
          <div class="grp"><label>نام کاربری پنل</label><div class="row2"><input type="text" id="adminUsername" autocomplete="username" maxlength="40" placeholder="admin"><button class="btn primary" onclick="changeUsername()"><i class="ti ti-user-edit"></i>تغییر نام کاربری</button></div><div class="hint">نام کاربری جدید بدون فاصله و بین ۳ تا ۴۰ کاراکتر.</div></div>
          <div class="divider"></div>
          <div class="grp"><label>رمز فعلی</label><div style="position:relative"><input type="password" id="curPass" autocomplete="current-password"><button type="button" class="iconbtn" style="position:absolute;left:7px;top:6px" onclick="toggleSettingsPass('curPass',this)"><i class="ti ti-eye"></i></button></div></div><div class="row2"><div class="grp"><label>رمز جدید</label><div style="position:relative"><input type="password" id="newPass" autocomplete="new-password" oninput="passwordMeter()"><button type="button" class="iconbtn" style="position:absolute;left:7px;top:6px" onclick="toggleSettingsPass('newPass',this)"><i class="ti ti-eye"></i></button></div><div id="passMeter" style="height:4px;background:var(--line);border-radius:99px;margin-top:7px;overflow:hidden"><i id="passMeterBar" style="display:block;height:100%;width:0;background:var(--bad);transition:.2s"></i></div><div id="passHint" class="hint">حداقل ۸ کاراکتر، ترجیحاً ترکیب حروف، عدد و نماد.</div></div><div class="grp"><label>تکرار رمز جدید</label><div style="position:relative"><input type="password" id="repPass" autocomplete="new-password"><button type="button" class="iconbtn" style="position:absolute;left:7px;top:6px" onclick="toggleSettingsPass('repPass',this)"><i class="ti ti-eye"></i></button></div></div></div>
          <button class="btn primary" onclick="changePassword()"><i class="ti ti-key"></i>تغییر امن رمز</button><button class="btn" style="margin-right:7px" onclick="revokeOtherSessions()"><i class="ti ti-shield-lock"></i>لغو نشست‌های قبلی</button>
        </div>
        <div class="card settings-card">
          <div class="section-title">Railway Network Center</div>
          <p class="hint" style="margin-bottom:12px">دامنه و پورت TCP عمومی Railway را اینجا مدیریت کن. Railway دامنه و پورت TCP Proxy را خودش تولید می‌کند و باید همان مقدار استفاده شود.</p>
          <div class="row2"><div class="grp"><label>TCP Host</label><input id="setTcpHost" placeholder="roundhouse.proxy.rlwy.net" class="mono" style="direction:ltr;text-align:left"></div><div class="grp"><label>TCP Port</label><input id="setTcpPort" placeholder="11105" class="mono" style="direction:ltr;text-align:left"></div></div>
          <p class="hint" id="tcpListenHint">—</p><button class="btn primary" onclick="saveTcpSettings()"><i class="ti ti-device-floppy"></i>ذخیره شبکه</button>
          <div class="divider"></div><div class="section-title">Sales & Management Bot</div>
          <div class="grp"><label>Bot Token</label><input id="setBotToken" placeholder="123456:ABC-DEF..." class="mono" style="direction:ltr;text-align:left"></div><div class="grp"><label>Admin IDs</label><input id="setBotAdmins" placeholder="123456789,987654321"></div>
          <div style="display:flex;gap:10px;align-items:center;margin-top:8px"><span class="status-dot off" id="botDot"></span><span id="botStatusText" style="font-size:13px">وضعیت نامشخص</span></div><div style="display:flex;gap:10px;margin-top:14px"><button class="btn primary" onclick="saveBotSettings()"><i class="ti ti-device-floppy"></i>ذخیره</button><button class="btn" id="botStartBtn" onclick="botStart()"><i class="ti ti-player-play"></i>شروع</button><button class="btn danger" id="botStopBtn" onclick="botStop()"><i class="ti ti-player-stop"></i>توقف</button></div>
        </div>
      </div>
      <div class="card settings-card tpl-studio" style="margin-top:14px">
        <div class="tpl-studio-head"><div><div class="section-title">Subscription Template</div><p class="hint">همان یک لینک ساب که به کاربر می‌دهی؛ فقط تعیین کن نام کانفیگ داخل اپ او دقیقاً چه چیزهایی را نشان دهد.</p></div><div class="tpl-badge"><i class="ti ti-wand"></i>Template Studio</div></div>
        <div class="tpl-grid">
          <div class="tpl-fields">
            <label class="tpl-row"><div class="tpl-row-main"><i class="ti ti-tag"></i><div><b>نام کانفیگ</b><small>نام دلخواه یا برند شما</small></div></div><input type="checkbox" class="tpl-switch" id="subTplName"></label>
            <label class="tpl-row"><div class="tpl-row-main"><i class="ti ti-database"></i><div><b>حجم اختصاص‌یافته</b><small>مثلاً ۵۰ گیگابایت</small></div></div><input type="checkbox" class="tpl-switch" id="subTplVolume"></label>
            <label class="tpl-row"><div class="tpl-row-main"><i class="ti ti-fingerprint"></i><div><b>شناسه کانفیگ (ID)</b><small>شناسه کوتاه یکتا</small></div></div><input type="checkbox" class="tpl-switch" id="subTplId"></label>
            <label class="tpl-row"><div class="tpl-row-main"><i class="ti ti-router"></i><div><b>نام اینباند</b><small>نام اینباند مادر این کانفیگ</small></div></div><input type="checkbox" class="tpl-switch" id="subTplInbound"></label>
          </div>
          <div class="tpl-preview">
            <div class="tpl-preview-label"><i class="ti ti-device-mobile"></i>پیش‌نمایش داخل اپ کاربر</div>
            <div class="tpl-preview-row"><span class="tpl-preview-dot"></span><div class="tpl-preview-text" id="subTplPreview">MyConfig</div><span class="tpl-preview-proto">VLESS</span></div>
            <p class="hint" style="margin-top:10px">ترتیب نمایش دقیقاً همین ترتیب بالاست؛ بین هر بخش یک خط جداکننده (|) قرار می‌گیرد.</p>
          </div>
        </div>
        <button class="btn primary" style="margin-top:14px" onclick="saveSubTemplate()"><i class="ti ti-device-floppy"></i>ذخیره الگوی ساب</button>
      </div>

      <div class="card settings-card" style="margin-top:14px"><div class="section-title">Bot Text Studio</div><p class="hint">تمام پیام‌های کلیدی ربات را از همین پنل ویرایش کن؛ تغییرات روی ربات در اجرای بعدی/ری‌استارت اعمال می‌شوند.</p><div class="bot-text-grid"><div class="grp"><label>پیام خوش‌آمد</label><textarea id="botTxtWelcome" rows="4"></textarea></div><div class="grp"><label>منوی مدیریت</label><textarea id="botTxtAdmin" rows="4"></textarea></div><div class="grp"><label>پیام ساخت کانفیگ</label><textarea id="botTxtCreated" rows="3"></textarea></div><div class="grp"><label>پیام فروشگاه</label><textarea id="botTxtStore" rows="3"></textarea></div><div class="grp"><label>پیام پرداخت موفق</label><textarea id="botTxtPayment" rows="3"></textarea></div></div><button class="btn primary" onclick="saveBotTexts()"><i class="ti ti-device-floppy"></i>ذخیره متن‌های ربات</button></div>

      <div class="card advanced-settings" style="margin-top:14px"><div class="panel-head"><div><b>CONTROL CENTER PRO</b><small>ابزارهای حرفه‌ای برای شخصی‌سازی و نگهداری پنل</small></div><span class="badge green">PRO</span></div><div class="advanced-grid"><button class="pro-action" onclick="refreshOverview();toast('داده‌های زنده بروزرسانی شد ✓')"><i class="ti ti-activity-heartbeat"></i><b>Live Refresh</b><small>مانیتورینگ فوری منابع</small></button><button class="pro-action" onclick="loadSettings();toast('تنظیمات دوباره بارگذاری شد ✓')"><i class="ti ti-refresh"></i><b>Reload Settings</b><small>دریافت تنظیمات واقعی سرور</small></button><button class="pro-action" onclick="location.reload()"><i class="ti ti-reload"></i><b>Hard Reload</b><small>بارگذاری کامل رابط</small></button><button class="pro-action" onclick="navigator.clipboard?.writeText(location.origin);toast('دامنه پنل کپی شد ✓')"><i class="ti ti-world-copy"></i><b>Copy Panel URL</b><small>دامنه فعلی پنل</small></button></div></div>
    </div>

  </div>
  </div>
</div>

<div class="overlay" id="overlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer">
  <div class="dr-head"><h3 id="drTitle">—</h3><button class="iconbtn" onclick="closeDrawer()"><i class="ti ti-x"></i></button></div>
  <div class="dr-body" id="drBody"></div>
  <div class="dr-foot" id="drFoot"></div>
</div>

<div id="toastWrap"></div>

<script>
// ============================================================
// Core helpers
// ============================================================
const $ = (id) => document.getElementById(id);
function toast(msg, ok=true){
  const t = document.createElement('div');
  t.className = 'toast ' + (ok?'ok':'err');
  const safeMsg = dashTranslateValue(String(msg ?? ''), typeof getDashLang === 'function' ? getDashLang() : 'fa');
  t.innerHTML = `<i class="ti ti-${ok?'circle-check':'alert-circle'}"></i><span>${escapeHtml(safeMsg)}</span>`;
  $('toastWrap').appendChild(t);
  setTimeout(()=>t.remove(), 3800);
}
async function api(path, opts={}){
  const res = await fetch(path, {credentials:'same-origin', headers:{'Content-Type':'application/json'}, ...opts});
  let data = {};
  try{ data = await res.json(); }catch(e){}
  if(!res.ok){
    const message = data.detail || data.error || data.message || ('خطا ' + res.status);
    throw new Error(message);
  }
  return data;
}

let MESSAGE_FILTER='all';
let messageTimer=null;
let reportingClientError=false;
async function reportClientError(message, source='browser', extra={}){
  if(reportingClientError) return;
  reportingClientError=true;
  try{
    await fetch('/api/errors/client',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},keepalive:true,body:JSON.stringify({message:String(message||'Unknown client error').slice(0,1200),source:String(source||'browser').slice(0,40),path:location.pathname,stack:String(extra.stack||'').slice(0,4000),details:String(extra.details||'').slice(0,1500)})});
  }catch(e){} finally{reportingClientError=false;}
}
window.addEventListener('error',e=>{ if(e?.message) reportClientError(e.message,'browser',{stack:e.error?.stack,details:`${e.filename||''}:${e.lineno||''}:${e.colno||''}`}); });
window.addEventListener('unhandledrejection',e=>{ const r=e?.reason; reportClientError(r?.message||String(r||'Unhandled promise rejection'),'promise',{stack:r?.stack}); });
function fmtBytes(n){
  n = Number(n||0);
  if(n<=0) return '0';
  const u=['B','KB','MB','GB','TB']; let i=0;
  while(n>=1024 && i<u.length-1){n/=1024;i++;}
  return n.toFixed(n<10&&i>0?1:0)+' '+u[i];
}
function escapeHtml(s){ return String(s??'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// ============================================================
// Nav
// ============================================================
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click', ()=> gotoPage(t.dataset.pg));
});
function gotoPage(pg){
  if(pg==='plans'){ openDrawer('پلن‌های فروش', `<div class=\"feature-lock\"><div class=\"feature-lock-icon\"><i class=\"ti ti-lock-star\"></i></div><h3>این بخش در حال توسعه است</h3><p>ماژول فروش اشتراک در نسخه‌های بعدی VodiWalker فعال خواهد شد. فعلاً مدیریت سرویس، اینباند، کلاینت و سابسکریپشن بدون وابستگی به فروش در دسترس است.</p><div class=\"feature-lock-note\"><i class=\"ti ti-sparkles\"></i> Coming in a future release</div></div>`, `<button class=\"btn\" style=\"flex:1\" onclick=\"closeDrawer()\"><i class=\"ti ti-check\"></i>متوجه شدم</button>`); return; }
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on', t.dataset.pg===pg));
  document.querySelectorAll('.page').forEach(p=>p.classList.toggle('on', p.id==='pg-'+pg));
  CURRENT_PAGE = pg;
  updatePageTitle(pg);
  document.getElementById('app').classList.remove('sb-open');
  const loaders = {overview:refreshOverview, links:loadLinks, clientmgr:loadClientManager, categories:loadCategories, subgroups:loadSubGroups,
    reports:loadReports, admins:()=>{loadAdmins();loadAdminRequests();}, activity:loadActivity, messages:loadMessages, settings:()=>{loadSettings();loadDiagnostics();}};
  if(loaders[pg]) loaders[pg]();
}

// ============================================================
// Drawer
// ============================================================
function openDrawer(title, bodyHtml, footHtml){
  $('drTitle').textContent = title;
  $('drBody').innerHTML = bodyHtml;
  $('drFoot').innerHTML = footHtml;
  $('overlay').classList.add('show');
  $('drawer').classList.add('show');
}
function closeDrawer(){
  $('overlay').classList.remove('show');
  $('drawer').classList.remove('show');
}

// ============================================================
// Appearance Studio
// ============================================================
const APPEARANCE_DEFAULTS={font:'Vazirmatn',theme:'dark',accent:'purple',density:'comfortable',motion:true,wide:false,radius:'soft',glow:true,fontSize:'normal'};
const ACCENTS={purple:['#8b5cf6','#6d28d9'],blue:['#3b82f6','#1d4ed8'],cyan:['#06b6d4','#0e7490'],green:['#10b981','#047857'],orange:['#f59e0b','#b45309'],pink:['#ec4899','#be185d'],red:['#ef4444','#b91c1c'],indigo:['#6366f1','#4338ca'],teal:['#14b8a6','#0f766e'],gold:['#eab308','#a16207']};
function getAppearance(){try{return {...APPEARANCE_DEFAULTS,...JSON.parse(localStorage.getItem('vw_appearance')||'{}')}}catch(e){return {...APPEARANCE_DEFAULTS}}}
function saveAppearance(a){try{localStorage.setItem('vw_appearance',JSON.stringify(a))}catch(e){} applyAppearance()}
function applyAppearance(){const a=getAppearance();const root=document.documentElement;root.style.setProperty('--font-ui',`'${a.font}',sans-serif`);const theme=a.theme==='system'?(matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'):a.theme;root.setAttribute('data-theme',theme);const c=ACCENTS[a.accent]||ACCENTS.purple;root.style.setProperty('--accent',c[0]);root.style.setProperty('--accent-d',c[1]);root.style.setProperty('--ui-glow',a.glow?`0 14px 40px -18px ${c[0]}88`:'none');document.body.classList.toggle('density-compact',a.density==='compact');document.body.classList.toggle('no-motion',!a.motion);document.body.classList.toggle('wide-sidebar',!!a.wide);document.body.classList.toggle('radius-sharp',a.radius==='sharp');document.body.classList.toggle('radius-pill',a.radius==='pill');document.body.classList.toggle('font-small',a.fontSize==='small');document.body.classList.toggle('font-large',a.fontSize==='large');if($('appearanceFont'))$('appearanceFont').value=a.font;document.querySelectorAll('[data-theme-choice]').forEach(x=>x.classList.toggle('on',x.dataset.themeChoice===a.theme));document.querySelectorAll('[data-accent]').forEach(x=>x.classList.toggle('on',x.dataset.accent===a.accent));document.querySelectorAll('[data-density]').forEach(x=>x.classList.toggle('on',x.dataset.density===a.density));document.querySelectorAll('[data-radius]').forEach(x=>x.classList.toggle('on',x.dataset.radius===a.radius));document.querySelectorAll('[data-font-size]').forEach(x=>x.classList.toggle('on',x.dataset.fontSize===a.fontSize));if($('motionSwitch'))$('motionSwitch').classList.toggle('on',a.motion);if($('wideSwitch'))$('wideSwitch').classList.toggle('on',a.wide);if($('glowSwitch'))$('glowSwitch').classList.toggle('on',a.glow);updateThemeIcon()}
function setFont(v){const a=getAppearance();a.font=v;saveAppearance(a);toast('فونت پنل تغییر کرد ✓')}
function setAppearanceTheme(v){const a=getAppearance();a.theme=v;saveAppearance(a)}
function setAccent(v){const a=getAppearance();a.accent=v;saveAppearance(a)}
function setDensity(v){const a=getAppearance();a.density=v;saveAppearance(a)}
function setRadius(v){const a=getAppearance();a.radius=v;saveAppearance(a)}
function setFontSize(v){const a=getAppearance();a.fontSize=v;saveAppearance(a)}
function toggleMotion(){const a=getAppearance();a.motion=!a.motion;saveAppearance(a)}
function toggleWideSidebar(){const a=getAppearance();a.wide=!a.wide;saveAppearance(a)}
function toggleGlow(){const a=getAppearance();a.glow=!a.glow;saveAppearance(a)}
try{matchMedia('(prefers-color-scheme:light)').addEventListener('change',()=>{if(getAppearance().theme==='system')applyAppearance()})}catch(e){}
function resetAppearance(){try{localStorage.removeItem('vw_appearance');localStorage.removeItem('vw_theme')}catch(e){};applyAppearance();toast('ظاهر پنل به حالت پیش‌فرض برگشت ✓')}
applyAppearance();

// ============================================================
// Bootstrapping / current user
// ============================================================
let CATEGORIES = [];
let LINKS = [];
let PROTOCOLS = [];
let MANUAL_META = {};
let ADMIN_CACHE = [];

function toggleTheme(){
  const a=getAppearance(); a.theme=(a.theme==='light'?'dark':'light'); saveAppearance(a); toast(a.theme==='light'?'پوسته روشن و کاملاً سفید فعال شد ✓':'پوسته تیره فعال شد ✓');
}
function updateThemeIcon(){
  const btn = document.getElementById('themeToggle');
  if(!btn) return;
  const cur = document.documentElement.getAttribute('data-theme') || 'dark';
  btn.innerHTML = cur === 'light' ? '<i class="ti ti-sun"></i>' : '<i class="ti ti-moon"></i>';
}
updateThemeIcon();

function toggleSidebar(){
  document.getElementById('app').classList.toggle('sb-open');
}

var DASH_I18N = {
  fa: {
    dir:'rtl', brand:'VodiWalker',
    nav_overview:'داشبورد', nav_links:'اینباندها', nav_clientmgr:'ساخت کلاینت', nav_categories:'دسته‌بندی‌ها', nav_subgroups:'گروه‌های ساب',
    nav_plans:'پلن‌های فروش', nav_reports:'گزارش‌ها', nav_admins:'ادمین‌ها', nav_activity:'فعالیت‌ها', nav_messages:'پیام‌ها', nav_settings:'تنظیمات',
    pt_overview:'وضعیت لحظه‌ای سرویس، کانفیگ‌ها و ربات فروش',
    pt_links:'مدیریت حرفه‌ای اینباندها، کلاینت‌ها و لینک‌های اشتراک',
    pt_clientmgr:'ساخت کلاینت واقعی از روی اینباند دلخواه، جدا از صفحه اینباندها',
    pt_categories:'پیش‌فرض‌های حجم، انقضا و محدودیت برای گروه‌های کانفیگ',
    pt_subgroups:'ترکیب چند کانفیگ در یک لینک اشتراک واحد',
    pt_plans:'پلن‌هایی که در ربات فروش تلگرام نمایش داده می‌شوند',
    pt_reports:'خلاصه‌ی عملکرد فروش و کانفیگ‌ها',
    pt_admins:'حساب‌های دسترسی جانبی به پنل (فقط مالک)',
    pt_activity:'۱۵۰ رویداد اخیر پنل',
    pt_messages:'مرکز خطاها، هشدارها و پیام‌های سیستم',
    pt_settings:'آدرس عمومی پنل، ربات فروش تلگرام و رمز عبور'
  },
  en: {
    dir:'ltr', brand:'VodiWalker',
    nav_overview:'Overview', nav_links:'Inbounds', nav_clientmgr:'Create Client', nav_categories:'Categories', nav_subgroups:'Sub Groups',
    nav_plans:'Sale Plans', nav_reports:'Reports', nav_admins:'Admins', nav_activity:'Activity', nav_messages:'Messages', nav_settings:'Settings',
    pt_overview:'Live status of the service, configs and sales bot',
    pt_links:'Manage inbounds, clients and subscription links',
    pt_clientmgr:'Create a real client from any inbound, separate from the inbounds page',
    pt_categories:'Default traffic, expiry and IP-limit presets for config groups',
    pt_subgroups:'Combine several configs into one subscription link',
    pt_plans:'Plans shown in the Telegram sales bot',
    pt_reports:'Summary of sales and config performance',
    pt_admins:'Secondary panel access accounts (owner only)',
    pt_activity:'Last 150 panel events',
    pt_messages:'Errors, warnings and system messages',
    pt_settings:'Panel public URL, Telegram sales bot and password'
  }
};
var CURRENT_PAGE = 'overview';
const DASH_EN_TERMS = {
  // Navigation / pages
  'داشبورد':'Dashboard','اینباندها':'Inbounds','اینباند':'Inbound','دسته‌بندی‌ها':'Categories','دسته‌بندی':'Category',
  'گروه‌های ساب':'Subscription Groups','گروه ساب':'Subscription Group','گروه جدید':'New Group','پلن‌های فروش':'Sales Plans','پلن فروش':'Sales Plan','پلن جدید':'New Plan',
  'گزارش‌ها':'Reports','ادمین‌ها':'Admins','ادمین':'Admin','ادمین جدید':'New Admin','مالک':'Owner','فعالیت‌ها':'Activity','فعالیت':'Activity','پیام‌ها':'Messages','تنظیمات':'Settings',
  'مرکز کنترل':'Control Center','مرکز پیام و خطا':'Message & Error Center','مدیریت حساب‌ها':'Admin Management','مدیریت حساب':'Admin Management',
  'تنظیمات و استودیو ظاهر':'Settings & Appearance Studio','استودیو ظاهر':'Appearance Studio',

  // Common actions / states
  'فعال':'Active','غیرفعال':'Inactive','فعال/غیرفعال':'Enable/Disable','خاموش':'Stopped','در حال اجرا':'Running','روشن':'Online','آنلاین':'Online','آفلاین':'Offline',
  'در دسترس نیست':'Unavailable','وضعیت نامشخص':'Unknown status','در حال دریافت...':'Loading...','بروزرسانی':'Refresh','بروزرسانی زنده':'Live Refresh',
  'ذخیره':'Save','ذخیره تغییرات':'Save Changes','ذخیره آدرس':'Save URL','ذخیره شبکه':'Save Network','ذخیره متن‌های ربات':'Save Bot Texts','حذف':'Delete','ویرایش':'Edit','ساخت':'Create','ساخت سریع':'Quick Create','لغو':'Cancel','تأیید':'Confirm','انصراف':'Cancel','بازگشت':'Back','نمایش':'View','کپی':'Copy','کپی لینک':'Copy Link','کپی لینک ساب':'Copy Subscription Link','دریافت فایل':'Download','خروجی CSV':'CSV Export','جستجو':'Search','فیلتر':'Filter','همه':'All','پاک‌کردن خطاها':'Clear Errors','لغو نشست‌های قبلی':'Revoke Previous Sessions',
  'شروع':'Start','توقف':'Stop','فعال‌سازی':'Enable','غیرفعال‌سازی':'Disable','عملیات':'Actions','کنترل':'Control','جزئیات':'Details','بستن':'Close','بارگذاری کامل رابط':'Hard Reload','بازنشانی ظاهر':'Reset Appearance','بارگذاری دوباره':'Reload',

  // Titles / descriptions
  'وضعیت لحظه‌ای سرویس، کانفیگ‌ها و ربات فروش':'Live service, configuration and sales-bot status',
  'مدیریت حرفه‌ای اینباندها، کلاینت‌ها و لینک‌های اشتراک':'Professional inbound, client and subscription management',
  'پیش‌فرض‌های حجم، انقضا و محدودیت برای گروه‌های کانفیگ':'Traffic, expiry and limit presets for config groups',
  'ترکیب چند کانفیگ در یک لینک اشتراک واحد':'Combine multiple configs into one subscription link',
  'پلن‌هایی که در ربات فروش تلگرام نمایش داده می‌شوند':'Plans shown in the Telegram sales bot',
  'خلاصه‌ی عملکرد فروش و کانفیگ‌ها':'Sales and configuration performance',
  'حساب‌های دسترسی جانبی به پنل (فقط مالک)':'Secondary panel access accounts (owner only)',
  '۱۵۰ رویداد اخیر پنل':'Latest 150 panel events',
  'مرکز خطاها، هشدارها و پیام‌های سیستم':'Errors, warnings and system messages',
  'آدرس عمومی پنل، ربات فروش تلگرام و رمز عبور':'Panel public URL, Telegram sales bot and account security',
  'نمای لحظه‌ای منابع سرور، ترافیک، اتصال‌ها و سرویس فروش.':'Live server resources, traffic, connections and sales service.',
  'مرکز مدیریت اینباند، ساخت کلاینت و کنترل دسترسی؛ با پایش زنده هر ۵ ثانیه.':'Inbound management, client creation and access control with live monitoring every 5 seconds.',
  'تمام خطاهای سرور، خطاهای مرورگر و رویدادهای مهم اینجا جمع می‌شوند تا هیچ خطایی گم نشود.':'All server errors, browser errors and important events are collected here.',
  'ظاهر، فونت، رنگ، تراکم، زبان و تنظیمات عملیاتی پنل را از یکجا کنترل کن.':'Control appearance, font, colors, density, language and operational settings from one place.',
  'برای لینک‌های Subscription، دامنه واقعی پنل را ثابت کن. روی Railway بهتر است دامنه عمومی سرویس را اینجا قرار بدهی.':'Set the real panel domain for subscription links. On Railway, use the service public domain here.',
  'دامنه و پورت TCP عمومی Railway را اینجا مدیریت کن. Railway دامنه و پورت TCP Proxy را خودش تولید می‌کند و باید همان مقدار استفاده شود.':'Manage the public Railway TCP domain and port here. Railway generates the TCP Proxy values.',
  'تمام پیام‌های کلیدی ربات را از همین پنل ویرایش کن؛ تغییرات روی ربات در اجرای بعدی/ری‌استارت اعمال می‌شوند.':'Edit the bot messages here; changes apply on the next bot start/restart.',
  'حداقل ۸ کاراکتر، ترجیحاً ترکیب حروف، عدد و نماد.':'At least 8 characters; a mix of letters, numbers and symbols is recommended.',
  'نام کاربری جدید بدون فاصله و بین ۳ تا ۴۰ کاراکتر.':'New username without spaces, between 3 and 40 characters.',
  'ابزارهای حرفه‌ای برای شخصی‌سازی و نگهداری پنل':'Professional tools for panel personalization and maintenance',

  // Dashboard metrics
  'کل اینباندها':'Total Inbounds','مشتریان فروشگاه':'Store Customers','فروش (Stars)':'Sales (Stars)','پرمصرف‌ترین کانفیگ‌های ۷ روز اخیر':'Top configs from the last 7 days',
  'پرمصرف‌ترین کانفیگ‌ها':'Top Configs by Usage','خطاهای ثبت‌شده':'Recorded Errors','خطاهای Backend و Frontend با جزئیات مسیر و زمان':'Backend and frontend errors with route and time details',
  'رویدادهای مهم':'Important Events','آخرین فعالیت‌های پنل برای عیب‌یابی سریع':'Recent panel activity for quick troubleshooting',
  'وضعیت سیستم':'System Status','سیستم سالم است.':'System is healthy.','خطای ثبت‌شده‌ای وجود ندارد. سیستم سالم است.':'No recorded errors. System is healthy.','رویدادی وجود ندارد.':'No events found.','لاگی وجود ندارد':'No activity logs.','داده‌ای موجود نیست':'No data available.','هنوز داده‌ی مصرفی ثبت نشده':'No usage data recorded yet.','کانفیگی یافت نشد':'No configs found.','گروهی وجود ندارد':'No groups found.','پلنی وجود ندارد':'No plans found.',
  'همگام‌سازی خودکار':'Auto Sync','آخرین بروزرسانی':'Last Updated','۳۰ روز اخیر':'Last 30 days','۱۴ روز اخیر':'Last 14 days','۷ روز اخیر':'Last 7 days',
  'در حال ذخیره...':'Saving...','تغییر امن رمز':'Change Password','تغییر نام کاربری':'Change Username','نام کاربری پنل':'Panel Username','نام کاربری جدید':'New Username','رمز عبور':'Password','رمز فعلی':'Current Password','رمز جدید':'New Password','تکرار رمز جدید':'Repeat New Password','تکرار رمز عبور':'Repeat Password','امنیت حساب':'Account Security',
  'پیام خوش‌آمد':'Welcome Message','منوی مدیریت':'Admin Menu','پیام ساخت کانفیگ':'Config Created Message','پیام فروشگاه':'Store Message','پیام پرداخت موفق':'Payment Success Message',
  'آدرس عمومی پنل':'Panel Public URL','دامنه فعلی پنل':'Current panel domain','ذخیره شد':'Saved','ذخیره شد ✓':'Saved ✓','ساخته شد':'Created','حذف شد':'Deleted','بروزرسانی شد':'Updated','کپی شد':'Copied','کپی شد ✓':'Copied ✓','تنظیمات دوباره بارگذاری شد ✓':'Settings reloaded ✓','داده‌های زنده بروزرسانی شد ✓':'Live data refreshed ✓','دامنه پنل کپی شد ✓':'Panel URL copied ✓','نام کاربری با موفقیت تغییر کرد ✓':'Username changed successfully ✓','رمز عبور با موفقیت تغییر کرد ✓':'Password changed successfully ✓',

  // Tables / forms
  'نام کاربری':'Username','نام':'Name','نام گروه':'Group Name','برچسب':'Label','نقش':'Role','وضعیت':'Status','زمان':'Time','نوع':'Type','پیام':'Message','تعداد':'Count','تعداد کانفیگ':'Config Count','لینک عمومی':'Public Link',
  'پروتکل':'Protocol','آدرس':'Address','آدرس / Domain':'Address / Domain','پورت':'Port','سرعت':'Speed','حجم':'Traffic','حجم مصرفی':'Usage','حجم پیش‌فرض (GB)':'Default Traffic (GB)','انقضا':'Expiry','انقضا (روز)':'Expiry (Days)','اعتبار (روز)':'Validity (Days)','زمان دقیق انقضا':'Exact Expiry','محدودیت IP':'IP Limit','Connection Limit':'Connection Limit','تعداد کاربر':'Client Limit','تعداد خروجی':'Output Count','توضیحات':'Description','یادداشت داخلی':'Internal Note',
  'مدت':'Duration','قیمت (⭐)':'Price (⭐)','ویژه':'Featured','آخرین ورود':'Last Login','کل':'Total','روز':'Days','ساعت':'Hours','دقیقه':'Minutes','نامحدود':'Unlimited','پیش‌فرض':'Default','اختیاری':'Optional','اجباری':'Required','مصرف':'Usage','اتصال':'Connection','اتصالات':'Connections','کلاینت‌ها':'Clients','کلاینت':'Client','مشتریان':'Customers','مشتری‌ها':'Customers',
  'کپی VLESS':'Copy VLESS','اشتراک':'Subscription','مدیریت کلاینت‌های واقعی':'Real Client Manager','ساخت کلاینت واقعی':'Create Client','کنترل پنل':'Panel Control','مدیریت ربات':'Bot Management','ربات':'Bot',

  // Inbound builder
  'ساخت اینباند':'Create Inbound','ویرایش اینباند':'Edit Inbound','ساخت کلاینت':'Create Client','ویرایش کلاینت':'Edit Client','انتخاب پروتکل':'Select Protocol','پروتکل پایه':'Base Protocol','انتقال':'Transport','لایه انتقال':'Transport Layer','امنیت':'Security','تنظیمات اتصال':'Connection Settings','تنظیمات پیشرفته':'Advanced Settings','خلاصه':'Summary','قبل از ذخیره ترکیب نهایی را بررسی کن':'Review the final combination before saving',
  'ترکیب نهایی':'Final Combination','شبکه':'Network','روش رمزنگاری':'Encryption Method','رمز / Secret':'Password / Secret','کلید عمومی':'Public Key','شناسه کوتاه':'Short ID','مسیر Spider':'Spider X','تولید کلید Reality':'Generate Reality Keypair','تست پینگ':'Ping Test','در حال تست':'Testing...','ابتدا آدرس یا دامنه را وارد کنید':'Enter an address or domain first','پورت نامعتبر است':'Invalid port','اتصال برقرار نشد':'Connection failed',
  'این ترکیب آماده استفاده است.':'This combination is ready to use.','این ترکیب برای ساخت لینک و مدیریت سرویس آماده شده است.':'This combination is prepared for link and service management.','Shadowsocks به‌صورت TCP-only در این Builder ارائه می‌شود.':'Shadowsocks is provided as TCP-only in this builder.','Transport فقط مسیر انتقال است و جدا از پروتکل پایه انتخاب می‌شود.':'Transport is only the transfer layer and is selected separately from the base protocol.',
  'VLESS':'VLESS','VMess':'VMess','Trojan':'Trojan','Shadowsocks':'Shadowsocks','TCP':'TCP','WebSocket':'WebSocket','WS':'WebSocket','gRPC':'gRPC','XHTTP':'XHTTP','TLS':'TLS','Reality':'Reality','None':'None','امنیت بدون رمزنگاری':'No encryption','بدون رمزنگاری':'No encryption',

  // Settings / appearance
  'فونت رابط کاربری':'Interface Font','اندازه متن':'Text Size','تراکم پنل':'Panel Density','گوشه‌ها':'Corners','پوسته':'Theme','رنگ اصلی':'Accent Color','انیمیشن‌های پنل':'Panel Animations','سایدبار باز در دسکتاپ':'Open sidebar on desktop','نورپردازی':'Glow','Appearance Studio':'Appearance Studio','ظاهر پنل به حالت پیش‌فرض برگشت ✓':'Appearance reset ✓','فونت پنل تغییر کرد ✓':'Panel font updated ✓',
  'پوسته تاریک':'Dark Theme','پوسته روشن':'Light Theme','سیستم':'System','فونت پیش‌فرض':'Default Font','کوچک':'Small','متوسط':'Medium','بزرگ':'Large','فشرده':'Compact','راحت':'Comfortable','گرد':'Rounded','تیز':'Sharp',

  // Messages / diagnostics
  'خطا':'Error','هشدار':'Warning','اطلاعات':'Info','مرورگر':'Browser','پاک‌کردن':'Clear','مرکز خطاها':'Error Center','مرکز پیام و خطا':'Message & Error Center','خطا در پردازش اطلاعات ورود.':'Login data could not be processed.',
  'آدرس TCP ذخیره شد':'TCP address saved','آدرس ذخیره شد':'Address saved','ربات روشن شد':'Bot started','ربات خاموش شد':'Bot stopped','ربات در حال اجراست':'Bot is running','ربات خاموش است':'Bot is stopped',
  'Caps Lock فعال است':'Caps Lock is on','قدرت رمز':'Password strength','حداقل ۸ کاراکتر، ترکیب حروف بزرگ/کوچک، عدد و نماد پیشنهاد می‌شود.':'At least 8 characters; uppercase/lowercase letters, numbers and symbols are recommended.',

  // Railway / service
  'دامنه عمومی Railway وارد شد؛ برای TCP خام باید TCP Proxy فعال باشد':'Railway public domain loaded; raw TCP requires TCP Proxy.','اطلاعات TCP Proxy ریل‌وی در این سرویس پیدا نشد':'Railway TCP Proxy information was not found for this service.',
  'همه دسته‌ها':'All categories','مورد انتخاب شده':'selected','اینباند جدید':'New Inbound','دسته جدید':'New Category','وضعیت':'Status','آدرس':'Address','ترافیک':'Traffic','کلاینت / اتصال':'Client / Connection','عملیات':'Actions','نام گروه':'Group Name','تعداد کانفیگ':'Config Count','لینک عمومی':'Public Link','حجم پیش‌فرض':'Default Traffic','قیمت (⭐)':'Price (⭐)','خروجی CSV':'CSV Export','برچسب':'Label','مدیریت حساب‌ها':'Admin Management','ادمین جدید':'New Admin','نقش':'Role','آخرین ورود':'Last Login','مرکز پیام و خطا':'Message & Error Center','پاک‌کردن خطاها':'Clear Errors','خطاهای ثبت‌شده':'Recorded Errors','خطاهای Backend و Frontend با جزئیات مسیر و زمان':'Backend and frontend errors with route and time details','همه':'All','هشدار':'Warning','مرورگر':'Browser','بازنشانی ظاهر':'Reset Appearance','اندازه متن':'Text Size','تراکم پنل':'Panel Density','گوشه‌ها':'Corners','پوسته':'Theme','رنگ اصلی':'Accent Color','انیمیشن‌های پنل':'Panel Animations','سایدبار باز در دسکتاپ':'Open sidebar on desktop','Glow / نورپردازی':'Glow / Lighting','امنیت حساب':'Account Security','رمز فعلی':'Current Password','رمز جدید':'New Password','تکرار رمز جدید':'Repeat New Password','تغییر امن رمز':'Change Password','لغو نشست‌های قبلی':'Revoke Previous Sessions','توقف':'Stop','منوی مدیریت':'Admin Menu','پیام ساخت کانفیگ':'Config Created Message','پیام فروشگاه':'Store Message','پیام پرداخت موفق':'Payment Success Message','مانیتورینگ فوری منابع':'Instant resource monitoring','دریافت تنظیمات واقعی سرور':'Load real server settings','بارگذاری کامل رابط':'Hard Reload','دامنه فعلی پنل':'Current panel domain','در حال دریافت...':'Loading...','بروزرسانی':'Refresh','ساخت سریع':'Quick Create','کانفیگی یافت نشد':'No configs found','دسته‌بندی‌ها':'Categories','پلن‌های فروش':'Sales Plans','گروه‌های ساب':'Subscription Groups','ادمین‌ها':'Admins','پیام‌ها':'Messages','تنظیمات':'Settings',

  // --- Added: fill remaining gaps found across dashboard toasts, confirm()
  // dialogs, inbound builder, client manager and admin permission matrix ---
  'اینباند حذف شود؟':'inbound(s) be deleted?','این کلاینت حذف شود؟':'Delete this client?','این کانفیگ حذف شود؟':'Delete this config?','این دسته حذف شود؟':'Delete this category?','این گروه حذف شود؟':'Delete this group?','این پلن حذف شود؟':'Delete this plan?','این ادمین حذف شود؟':'Delete this admin?','همه خطاهای ثبت‌شده پاک شوند؟':'Clear all recorded errors?','همه نشست‌های قبلی این حساب لغو شوند؟':'Revoke all previous sessions for this account?','دسته‌بندی‌ای وجود ندارد':'No categories found','بروزرسانی گروهی انجام شد':'Bulk update completed','حذف گروهی انجام شد':'Bulk delete completed','کانفیگ خودکار ساخته شد':'Auto config created','اینباند بروزرسانی شد':'Inbound updated','اینباند با موفقیت ساخته شد':'Inbound created successfully','خطا در ذخیره اینباند':'Error saving inbound','خطا در دریافت اطلاعات Railway':'Error fetching Railway information','کلاینت واقعی ساخته شد ✓':'Client created ✓','متن‌های ربات ذخیره شد ✓':'Bot texts saved ✓','خطاها پاک شدند ✓':'Errors cleared ✓','ذخیره شد و ربات با تنظیمات جدید ری‌استارت شد':'Saved — the bot restarted with the new settings','ذخیره شد — برای اعمال، ربات را روشن کنید':'Saved — turn the bot on to apply the changes','کلید Reality ساخته شد. Private Key را روی نود خودتان نگه دارید.':'Reality keypair generated. Keep the private key on your own node.','پورت باید بین 1 تا 65535 باشد':'Port must be between 1 and 65535','Shadowsocks فقط با TCP ساخته می‌شود':'Shadowsocks can only be created over TCP','رمز جدید باید حداقل ۸ کاراکتر باشد':'New password must be at least 8 characters','رمز جدید باید با رمز فعلی متفاوت باشد':'New password must be different from the current password','تکرار رمز یکسان نیست':'Password confirmation does not match','همه‌ی فیلدهای رمز عبور را پر کنید':'Please fill in all password fields','نام کاربری باید ۳ تا ۴۰ کاراکتر و بدون فاصله باشد':'Username must be 3–40 characters with no spaces','نام کاربری را وارد کنید':'Please enter a username','هر کلاینت UUID مستقل دارد و برای پروتکل‌های Live مستقیماً توسط Relay قابل احراز است.':'Each client has its own UUID and, for Live protocols, is authenticated directly by the relay.','این اینباند فعلاً فقط لینک تولید می‌کند. برای Client واقعی، ابتدا یک ترکیب Live مثل VLESS + WS/TCP/XHTTP انتخاب کنید.':'This inbound currently only generates links. For a real client, first choose a Live combination such as VLESS + WS/TCP/XHTTP.','مدیریت کلاینت‌ها':'Manage Clients','حجم (GB، خالی = والد)':'Traffic (GB, empty = parent)','انقضا (روز، 0 = والد)':'Expiry (days, 0 = parent)','بدون تغییر خالی بگذار':'Leave empty for no change','والد':'parent','ساخت اینباند حرفه‌ای':'Create Professional Inbound','پروتکل پایه، ترنسپورت و امنیت کاملاً تفکیک‌شده':'Base protocol, transport and security are fully separated','اول مشخص کن با چه پروتکلی کانفیگ ساخته شود':'First decide which protocol the config will use','حالا مسیر انتقال را جداگانه انتخاب کن':'Now choose the transport layer separately','TLS / Reality / None را مستقل از ترنسپورت انتخاب کن':'Choose TLS / Reality / None independently of the transport','فقط فیلدهای مرتبط با انتخاب بالا نمایش داده می‌شوند':'Only fields relevant to the selection above are shown','لینک اشتراک':'Subscription Link','اگر این لینک برای مشتری باز نمی‌شود، ابتدا از تب «تنظیمات» آدرس عمومی پنل را درست تنظیم کنید.':'If this link doesn\'t open for the customer, first set the panel\'s public URL correctly under the “Settings” tab.','دسته':'Category','گروه ساب جدید':'New Subscription Group','پلن':'Plan','پیشنهاد ویژه':'Featured offer','در حال اتصال':'Connecting','غیرفعال/منقضی':'Disabled/Expired','فعال - بدون اتصال':'Active – No connection','منقضی شده':'Expired','روز مانده':'days left','بدون انقضا':'No expiry','اتصال زنده':'Live connections','کل کانفیگ‌ها':'Total Configs','تعداد سفارش':'Order Count','ساخت و مدیریت اینباند':'Create & manage inbounds','سابسکریپشن':'Subscription','پیام‌ها و خطاها':'Messages & Errors','اینباند و کلاینت':'Inbounds & Clients','هشدارهای اخیر':'Recent Warnings','خطاهای مرورگر':'Browser Errors','خطای نامشخص':'Unknown error','سرور TCP روی پورت داخلی':'TCP server on internal port','گوش می‌دهد — این را در Railway به همین پورت داخلی متصل کن، نه به':'is listening — in Railway, point this at the same internal port, not at the main HTTP','مثلاً':'e.g.','اصلی':'main','همه‌ی اینباندها بروزرسانی شدند ✓':'All inbounds refreshed ✓','بروزرسانی همه':'Refresh All','الگوی نام کانفیگ‌های ساب ذخیره شد ✓':'Subscription remark template saved ✓','نام کانفیگ':'Config Name','حجم اختصاص‌یافته':'Assigned Traffic','شناسه کانفیگ (ID)':'Config ID','نام اینباند':'Inbound Name','پیش‌نمایش: ':'Preview: ','همان یک لینک ساب که به کاربر می‌دهی؛ فقط تعیین کن نام کانفیگ داخل اپ او دقیقاً چه چیزهایی را نشان دهد.':'It\'s still the same single subscription link you hand out — just choose exactly what shows in the config name inside their app.','ذخیره الگوی ساب':'Save Template','Subscription Template':'Subscription Template'
};

// ============================================================
// Stable dashboard language engine
// ============================================================
// The dashboard contains both static DOM and HTML that is created later by
// drawers, tables, API responses and toast messages.  Translation therefore
// uses one stateful engine for the whole dashboard document (not only #app).
// Each text node/attribute remembers its Persian source and its last rendered
// value.  This prevents EN -> FA loss and also lets dynamically updated nodes
// refresh correctly while English mode is active.
const DASH_NODE_STATE = new WeakMap();
const DASH_ATTR_STATE = new WeakMap();
const DASH_TERM_LIST = Object.keys(DASH_EN_TERMS).sort((a,b)=>b.length-a.length);
const DASH_TRANSLATABLE_ATTRS = ['placeholder','title','aria-label'];
let DASH_TRANSLATING = false;

// Word-safe substring replace: a term is only replaced when the character
// right before/after it is NOT another Persian letter. Without this guard a
// short dictionary entry like 'کل' ("total") would also match *inside* an
// unrelated word such as 'کلید' ("key") -> 'Totalید', silently corrupting
// text that has nothing to do with the term. Persian suffixes attached with
// a ZWNJ (e.g. 'کلاینت‌ها') still match correctly because \u200c is not a
// Persian letter and is left outside this guard.
const DASH_FA_LETTER_RE = /[\u0600-\u06FF]/;
function dashReplaceTermSafely(out, term, replacement){
  if(!out.includes(term)) return out;
  let result = '';
  let i = 0;
  const len = term.length;
  while(i < out.length){
    if(out.startsWith(term, i)){
      const before = i > 0 ? out[i - 1] : '';
      const after = out[i + len] || '';
      if(!DASH_FA_LETTER_RE.test(before) && !DASH_FA_LETTER_RE.test(after)){
        result += replacement;
        i += len;
        continue;
      }
    }
    result += out[i];
    i++;
  }
  return result;
}

function dashTranslateValue(value, lang){
  if(lang !== 'en' || !value) return value || '';
  let out = String(value);
  for(const term of DASH_TERM_LIST){
    out = dashReplaceTermSafely(out, term, DASH_EN_TERMS[term]);
  }
  return out;
}

// Shorthand for one-off strings that never live in the DOM long enough for
// the tree-walker/observer to reach them — native confirm()/prompt() dialogs
// in particular. Translates against the current dashboard language.
function t(fa){
  return dashTranslateValue(fa, typeof getDashLang === 'function' ? getDashLang() : 'fa');
}

function dashShouldTranslateElement(el){
  if(!el) return false;
  if(/^(SCRIPT|STYLE|NOSCRIPT)$/i.test(el.tagName)) return false;
  if(el.closest('[data-no-translate],.mono,[data-i18n]')) return false;
  return true;
}

function dashRenderTextNode(textNode, lang){
  if(!textNode || !textNode.parentElement || !dashShouldTranslateElement(textNode.parentElement)) return;
  const current = textNode.nodeValue || '';
  let state = DASH_NODE_STATE.get(textNode);
  if(!state){
    state = {fa: current, last: current};
    DASH_NODE_STATE.set(textNode, state);
  }else if(current !== state.last){
    // The node was changed by application code. Treat the new value as the
    // canonical Persian source rather than translating an old snapshot.
    state.fa = current;
  }
  const next = lang === 'en' ? dashTranslateValue(state.fa,'en') : state.fa;
  state.last = next;
  if(current !== next) textNode.nodeValue = next;
}

function dashRenderAttr(el, attr, lang){
  if(!el || el.matches('[data-no-translate],.mono,[data-i18n]')) return;
  if(!el.hasAttribute(attr)) return;
  const current = el.getAttribute(attr) || '';
  let attrs = DASH_ATTR_STATE.get(el);
  if(!attrs){ attrs = {}; DASH_ATTR_STATE.set(el, attrs); }
  let state = attrs[attr];
  if(!state){
    state = {fa: current, last: current};
    attrs[attr] = state;
  }else if(current !== state.last){
    state.fa = current;
  }
  const next = lang === 'en' ? dashTranslateValue(state.fa,'en') : state.fa;
  state.last = next;
  if(current !== next) el.setAttribute(attr,next);
}

function translateDashTree(lang){
  const root=document.body;
  if(!root || DASH_TRANSLATING) return;
  DASH_TRANSLATING = true;
  try{
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    const nodes=[];
    let node;
    while((node=walker.nextNode())) nodes.push(node);
    for(const textNode of nodes) dashRenderTextNode(textNode,lang);

    root.querySelectorAll('input,textarea,button,[aria-label],select').forEach(el=>{
      for(const attr of DASH_TRANSLATABLE_ATTRS) dashRenderAttr(el,attr,lang);
    });

    root.querySelectorAll('option').forEach(option=>dashRenderTextNode(option.firstChild || option,lang));
  }finally{
    DASH_TRANSLATING = false;
  }
}

function setDashI18nElement(el, key, lang){
  if(!el || !key) return;
  const fa = DASH_I18N.fa?.[key];
  const en = DASH_I18N.en?.[key];
  if(fa === undefined && en === undefined) return;
  if(fa !== undefined) el.dataset.vwFa = String(fa);
  if(en !== undefined) el.dataset.vwEn = String(en);
  const next = lang === 'en' ? (en ?? fa ?? '') : (fa ?? '');
  el.textContent = String(next);
}

function updatePageTitle(pg){
  const mainEl = document.getElementById('pageTitleMain');
  const subEl = document.getElementById('pageTitleSub');
  const lang = getDashLang();
  if(mainEl) setDashI18nElement(mainEl, 'nav_'+pg, lang);
  if(subEl) setDashI18nElement(subEl, 'pt_'+pg, lang);
}

function applyDashLang(lang){
  lang = lang === 'en' ? 'en' : 'fa';
  const dictionary = DASH_I18N[lang] || DASH_I18N.fa;
  document.documentElement.setAttribute('dir', dictionary.dir || (lang==='fa'?'rtl':'ltr'));
  document.documentElement.setAttribute('lang', lang);
  document.body.classList.toggle('dash-en', lang==='en');
  document.getElementById('dashLangFa')?.classList.toggle('on', lang==='fa');
  document.getElementById('dashLangEn')?.classList.toggle('on', lang==='en');

  document.querySelectorAll('#app [data-i18n]').forEach(el=>{
    setDashI18nElement(el, el.getAttribute('data-i18n'), lang);
  });
  updatePageTitle(CURRENT_PAGE);
  translateDashTree(lang);
  try{ localStorage.setItem('vw_dash_lang',lang); }catch(e){}
}

function getDashLang(){
  try{ return localStorage.getItem('vw_dash_lang') === 'en' ? 'en' : 'fa'; }
  catch(e){ return 'fa'; }
}

function setDashLang(lang){
  applyDashLang(lang);
}

let dashTranslateObserver=null;
let dashTranslateQueued=false;
function enableDashTranslation(){
  if(dashTranslateObserver) dashTranslateObserver.disconnect();
  const root=document.getElementById('app') || document.body;
  if(!root) return;
  dashTranslateObserver=new MutationObserver(mutations=>{
    if(getDashLang()!=='en' || DASH_TRANSLATING || dashTranslateQueued) return;
    let hasAdded=false;
    for(const m of mutations){
      if(m.type==='childList' && m.addedNodes && m.addedNodes.length){ hasAdded=true; break; }
    }
    if(!hasAdded) return;
    dashTranslateQueued=true;
    const run=()=>{ dashTranslateQueued=false; if(getDashLang()==='en' && !DASH_TRANSLATING) translateDashTree('en'); };
    if(window.requestIdleCallback) requestIdleCallback(run,{timeout:120});
    else requestAnimationFrame(run);
  });
  dashTranslateObserver.observe(root,{subtree:true,childList:true});
}

// Apply the saved language only after the dashboard DOM exists.
applyDashLang(getDashLang());
enableDashTranslation();

async function boot(){
  try{
    const me = await api('/api/me');
    if(!me.authenticated){ location.href='/login'; return; }
    $('userName').textContent = me.admin.username;
    $('userChip').querySelector('.av').textContent = (me.admin.username||'?').slice(0,1).toUpperCase();
    if(me.admin.role !== 'owner'){
      document.querySelector('.tab[data-pg="admins"]').style.display='none';
      document.querySelector('.tab[data-pg="settings"]').style.display='none';
      if(!(me.admin.permissions||[]).includes('clients')){
        document.querySelector('.tab[data-pg="clientmgr"]').style.display='none';
      }
    } else {
      loadAdminRequests();
    }
  }catch(e){ location.href='/login'; return; }
  try{ const p = await api('/api/protocols'); PROTOCOLS = p.protocols||[]; MANUAL_META = p.manual||{}; }catch(e){}
  refreshOverview();
}
boot();

// ============================================================
// OVERVIEW
// ============================================================
async function refreshOverview(){
  try{
    const [stats, linksRes] = await Promise.all([api('/stats'), api('/api/links')]);
    LINKS = linksRes.links || [];
    $('nb-links').textContent = LINKS.filter(x=>!x.is_client).length;
    $('trafficTotalVal').textContent = fmtBytes(stats.total_traffic_bytes || 0);
  }catch(e){ toast(e.message, false); }
  try{
    const s = await api('/api/settings');
    $('ovBaseUrl').textContent = s.public_base_url || s.effective_host || '—';
    const running = !!s.bot_running;
    $('ovBotStatus').className = 'badge ' + (running?'green':'red');
    $('ovBotStatus').textContent = running?'ONLINE':'OFFLINE';
    $('botStateText').textContent = running?'در حال اجرا':'خاموش';
  }catch(e){}
  try{
    const rep = await api('/api/reports/summary?days=7');
    const t = rep.totals || {};
    $('ovBizStats').innerHTML = `
      <div><i class="ti ti-network"></i><span><b>${t.links||0}</b><small>کل اینباندها</small></span></div>
      <div><i class="ti ti-circle-check"></i><span><b>${t.active_links||0}</b><small>فعال</small></span></div>
      <div><i class="ti ti-users"></i><span><b>${t.customers||0}</b><small>مشتریان فروشگاه</small></span></div>
      <div><i class="ti ti-star"></i><span><b>${t.stars||0}</b><small>فروش (Stars) · ${t.orders||0} سفارش</small></span></div>`;
    const top = (rep.top_links||[]).slice(0,6);
    if(!top.length){
      $('ovTopLinks').innerHTML = '<div class="ov-empty">هنوز داده‌ی مصرفی ثبت نشده</div>';
    }else{
      const maxUsed = Math.max(1, ...top.map(l=>l.used_bytes||0));
      $('ovTopLinks').innerHTML = top.map((l,i)=>{
        const pct = Math.round((l.used_bytes||0)/maxUsed*100);
        return `<div class="ov-toplink-row"><div class="otl-rank">${i+1}</div><div class="otl-info"><b>${escapeHtml(l.label||'—')}</b><div class="otl-bar"><i style="width:${pct}%"></i></div></div><div class="otl-val">${fmtBytes(l.used_bytes||0)}</div></div>`;
      }).join('');
    }
  }catch(e){}
  await refreshTelemetry();
}
let TEL={cpu:[],ram:[],swap:[],storage:[],traffic:[],conn:[]};
function pushSeries(arr,v,max=36){arr.push(Number(v)||0);while(arr.length>max)arr.shift();}
function drawSpark(id,arr){const el=$(id);if(!el||!arr.length)return;const max=Math.max(100, ...arr), min=Math.min(0,...arr);const pts=arr.map((v,i)=>{const x=(i/Math.max(1,arr.length-1))*240;const y=44-((v-min)/(max-min||1))*38;return `${x.toFixed(1)},${y.toFixed(1)}`}).join(' ');el.innerHTML=`<polyline points="${pts}"/>`; }
function drawChart(id,arr,maxY){const el=$(id);if(!el||!arr.length)return;const w=id==='trafficChart'?900:340,h=id==='trafficChart'?260:150;const max=maxY||Math.max(1,...arr);const pts=arr.map((v,i)=>{const x=(i/Math.max(1,arr.length-1))*w;const y=h-8-(Math.min(max,v)/max)*(h-20);return `${x.toFixed(1)},${y.toFixed(1)}`}).join(' ');const area=`0,${h} ${pts} ${w},${h}`;el.innerHTML=`<polygon class="area" points="${area}"/><polyline points="${pts}"/>`; }
async function refreshTelemetry(){
  try{const t=await api('/api/telemetry');
    $('cpuVal').textContent=t.cpu+'%'; $('cpuSub').textContent=(t.cpu_cores||1)+' logical cores';
    $('ramVal').textContent=t.ram.percent+'%'; $('ramSub').textContent=fmtBytes(t.ram.used)+' / '+fmtBytes(t.ram.total);
    $('swapVal').textContent=t.swap.percent+'%'; $('swapSub').textContent=fmtBytes(t.swap.used)+' / '+fmtBytes(t.swap.total);
    $('storageVal').textContent=t.storage.percent+'%'; $('storageSub').textContent=fmtBytes(t.storage.used)+' / '+fmtBytes(t.storage.total);
    $('txRate').textContent=fmtBytes(t.network.tx_bps)+'/s'; $('rxRate').textContent=fmtBytes(t.network.rx_bps)+'/s'; $('liveRate').textContent='↑ '+fmtBytes(t.network.tx_bps)+'/s ↓ '+fmtBytes(t.network.rx_bps)+'/s';
    $('connVal').textContent=t.connections; $('reqVal').textContent=t.requests; $('errVal').textContent=t.errors; $('uptimeVal').textContent=t.uptime; $('coresVal').textContent=t.cpu_cores; $('procRamVal').textContent=fmtBytes(t.process.rss); $('loadVal').textContent=(t.load||[]).join('  '); $('sentTotal').textContent=fmtBytes(t.network.bytes_sent); $('recvTotal').textContent=fmtBytes(t.network.bytes_recv);
    const hist=Array.isArray(t.history)?t.history:[];
    if(hist.length){
      TEL.cpu=hist.map(x=>Number(x.cpu)||0); TEL.ram=hist.map(x=>Number(x.ram)||0); TEL.swap=hist.map(x=>Number(x.swap)||0); TEL.storage=hist.map(x=>Number(x.storage)||0);
      TEL.traffic=hist.map(x=>(Number(x.tx_bps)||0)+(Number(x.rx_bps)||0)); TEL.conn=hist.map(x=>Number(x.connections)||0);
    }else{
      pushSeries(TEL.cpu,t.cpu);pushSeries(TEL.ram,t.ram.percent);pushSeries(TEL.swap,t.swap.percent);pushSeries(TEL.storage,t.storage.percent);pushSeries(TEL.traffic,(t.network.tx_bps+t.network.rx_bps));pushSeries(TEL.conn,t.connections);
    }
    drawSpark('cpuSpark',TEL.cpu);drawSpark('ramSpark',TEL.ram);drawSpark('swapSpark',TEL.swap);drawSpark('storageSpark',TEL.storage);drawChart('trafficChart',TEL.traffic);drawChart('connChart',TEL.conn);
  }catch(e){}
}
let telemetryTimer=null;
function startTelemetryLoop(){ if(telemetryTimer) clearInterval(telemetryTimer); telemetryTimer=setInterval(()=>{ if(!document.hidden) refreshTelemetry(); },8000); }
startTelemetryLoop();

function statCard(icon,color,val,label){
  return `<div class="stat-card"><div class="sc-top"><div class="sc-icon" style="background:${color}22;color:${color}"><i class="ti ${icon}"></i></div></div>
    <div class="sc-val">${val ?? 0}</div><div class="sc-label">${label}</div></div>`;
}
function protoLabel(l){
  if(l && typeof l === 'object'){
    if(l.protocol_display) return l.protocol_display;
    const found = PROTOCOLS.find(x=>x.id===l.protocol);
    return found ? found.label : (l.protocol||'—');
  }
  const found = PROTOCOLS.find(x=>x.id===l);
  return found ? found.label : (l||'—');
}
function statusBadge(l){
  if(l.expired || !l.active) return `<span class="badge red">غیرفعال/منقضی</span>`;
  if(l.status_color==='green') return `<span class="badge green">متصل</span>`;
  return `<span class="badge gray">فعال</span>`;
}

// ============================================================
// LINKS
// ============================================================
async function loadLinks(silent){
  try{
    const [linksRes, catsRes] = await Promise.all([api('/api/links'), api('/api/categories')]);
    const selectedBefore = silent ? selectedLinkUuids() : [];
    LINKS = linksRes.links || [];
    CATEGORIES = catsRes.categories || [];
    const sel = $('linkFilterCat');
    const prevCatVal = sel.value;
    sel.innerHTML = '<option value="">همه دسته‌ها</option>' + CATEGORIES.map(c=>`<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
    sel.value = prevCatVal;
    $('nb-links').textContent = LINKS.filter(x=>!x.is_client).length;
    renderLinks();
    if(silent && selectedBefore.length){
      selectedBefore.forEach(uid=>{const c=document.querySelector(`.ib-row-check[data-uid="${uid}"]`); if(c) c.checked=true;});
      updateLinksBulkBar();
    }
    if($('ibUpdatedAt')) $('ibUpdatedAt').textContent = 'بروزرسانی ' + new Date().toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  }catch(e){ if(!silent) toast(e.message, false); }
}
let linksTimer=setInterval(()=>{if(!document.hidden && CURRENT_PAGE==='links') loadLinks(true)},12000);
async function refreshAllInbounds(){
  const btn=$('ibRefreshBtn'), icon=$('ibRefreshIcon');
  if(btn) btn.disabled=true;
  if(icon) icon.classList.add('spin');
  try{
    await loadLinks();
    await refreshOverview();
    toast('همه‌ی اینباندها بروزرسانی شدند ✓');
  }catch(e){ toast(e.message, false); }
  finally{ if(btn) btn.disabled=false; if(icon) icon.classList.remove('spin'); }
}
function renderQuickStats(list){
  const total=list.length, active=list.filter(l=>l.active && !l.expired).length, live=list.filter(l=>l.live_status==='live').length, clients=list.reduce((s,l)=>s+Number(l.client_count||0),0);
  $('ibQuickStats').innerHTML = `
    <div><i class="ti ti-network"></i><span><b>${total}</b><small>کل اینباندها</small></span></div>
    <div><i class="ti ti-circle-check"></i><span><b>${active}</b><small>فعال</small></span></div>
    <div><i class="ti ti-bolt"></i><span><b>${live}</b><small>LIVE</small></span></div>
    <div><i class="ti ti-users"></i><span><b>${clients}</b><small>کل کلاینت‌ها</small></span></div>`;
}
function ibCardHtml(l){
  const pct=l.limit_bytes>0?Math.min(100,Math.round((l.used_bytes/l.limit_bytes)*100)):0; const port=l.port||443;
  const pctClass = pct>=90?'crit':(pct>=70?'warn':'');
  const isLive = l.live_status==='live';
  const daysLeft = l.expires_at ? Math.ceil((new Date(l.expires_at).getTime()-Date.now())/86400000) : null;
  const expClass = l.expired ? 'expired' : (daysLeft!==null && daysLeft<=3 ? 'soon' : '');
  const expSub = l.expires_at ? (l.expired ? 'منقضی شده' : (daysLeft!==null ? daysLeft+' روز مانده' : '')) : 'بدون انقضا';
  return `<article class="ib-card ${l.active?'':'ib-off'}" data-uid="${l.uuid}">
    <label class="ib-card-check"><input type="checkbox" class="ib-check ib-row-check" data-uid="${l.uuid}" onchange="updateLinksBulkBar()"></label>
    <div class="ib-card-head">
      <div class="ib-avatar"><i class="ti ti-router"></i></div>
      <div class="ib-card-id">
        <div class="ib-name-top"><b title="${escapeHtml(l.label||'Unnamed Inbound')}">${escapeHtml(l.label||'Unnamed Inbound')}</b>${l.expired?'<span class="badge red">منقضی</span>':''}</div>
        <div class="mono">${escapeHtml((l.uuid||'').slice(0,18))}…</div>
      </div>
      <div class="ib-card-controls">
        <button class="ib-switch ${l.active?'on':''}" title="فعال/غیرفعال" onclick="toggleLink('${l.uuid}', ${!l.active})"></button>
        <span class="ib-status-dot ${l.status_color||'gray'}" title="${l.status_color==='green'?'در حال اتصال':(l.status_color==='red'?'غیرفعال/منقضی':'فعال - بدون اتصال')}"></span>
      </div>
    </div>
    <div class="ib-tagrow"><span>${protoLabel(l)}</span><span>${l.network||'tcp'}/${l.security||'none'}</span>${isLive?'<span class="ib-live-tag"><i></i>LIVE</span>':'<span class="ib-linkonly-tag">LINK-ONLY</span>'}<span>${escapeHtml(l.category_name||'بدون دسته')}</span></div>
    <div class="ib-card-addr"><span class="mono">${escapeHtml(l.address||'0.0.0.0')}:${port}</span><small>${expSub}</small></div>
    <div class="ib-card-traffic">
      <div class="ib-tf-top"><span>مصرف</span><b>${fmtBytes(l.used_bytes||0)}${l.limit_bytes>0?' / '+fmtBytes(l.limit_bytes):' / ∞'}</b></div>
      <div class="ib-progress"><i class="${pctClass}" style="width:${pct}%"></i></div>
    </div>
    <div class="ib-card-stats">
      <div><small>کلاینت</small><b>${Number(l.client_count||0)}</b></div>
      <div><small>اتصال</small><b>${Number(l.connected_ips||0)}/${Number(l.connection_limit||0)||'∞'}</b></div>
      <div><small>انقضا</small><b class="${expClass}">${l.expires_at?escapeHtml(l.expires_at.slice(0,10)):'∞'}</b></div>
    </div>
    <div class="ib-card-foot">
      <div class="ib-clientcell"><button class="iconbtn" title="مدیریت کلاینت‌ها" onclick="openClients('${l.uuid}')"><i class="ti ti-users"></i></button><span>مدیریت کلاینت</span></div>
      <div class="ib-card-actions">
        <button class="iconbtn" title="اشتراک" onclick="showSubLink('${l.uuid}')"><i class="ti ti-qrcode"></i></button>
        <button class="iconbtn" title="ویرایش" onclick="openLinkDrawer('${l.uuid}')"><i class="ti ti-pencil"></i></button>
        <button class="iconbtn" title="تعویض لینک (UUID جدید)" onclick="regenerateLink('${l.uuid}')"><i class="ti ti-replace"></i></button>
        <button class="iconbtn" title="ریست حجم مصرفی" onclick="resetLinkUsage('${l.uuid}')"><i class="ti ti-refresh"></i></button>
        <button class="iconbtn" title="حذف" onclick="deleteLink('${l.uuid}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button>
      </div>
    </div>
  </article>`;
}
function renderLinks(){
  const q = ($('linkSearch').value||'').toLowerCase(); const cat = $('linkFilterCat').value;
  const all = LINKS.filter(l=>!l.is_client);
  renderQuickStats(all);
  const filtered = all.filter(l=>{ if(cat && String(l.category_id)!==String(cat)) return false; if(q && !(`${l.label||''} ${l.uuid||''} ${l.protocol||''}`).toLowerCase().includes(q)) return false; return true; });
  $('linksEmpty').style.display = filtered.length ? 'none' : 'block';
  $('ibGrid').innerHTML = filtered.map(ibCardHtml).join('');
  if($('ibCountLabel')) $('ibCountLabel').textContent = `${filtered.length} اینباند`;
  updateLinksBulkBar();
}
function toggleAllLinks(checked){
  document.querySelectorAll('.ib-row-check').forEach(c=>c.checked=checked);
  updateLinksBulkBar();
}
function selectedLinkUuids(){
  return Array.from(document.querySelectorAll('.ib-row-check:checked')).map(c=>c.dataset.uid);
}
function updateLinksBulkBar(){
  const sel = selectedLinkUuids();
  $('ibBulkBar').style.display = sel.length ? 'flex' : 'none';
  if($('ibSelCount')) $('ibSelCount').textContent = sel.length;
  const all = document.querySelectorAll('.ib-row-check');
  if($('ibSelAll')) $('ibSelAll').checked = all.length>0 && sel.length===all.length;
  document.querySelectorAll('.ib-card').forEach(card=>{
    const cb = card.querySelector('.ib-row-check');
    card.classList.toggle('ib-selected', !!(cb && cb.checked));
  });
}
async function bulkToggleLinks(active){
  const sel = selectedLinkUuids(); if(!sel.length) return;
  try{ await Promise.all(sel.map(uid=>api(`/api/links/${uid}`, {method:'PATCH', body: JSON.stringify({active})}))); toast('بروزرسانی گروهی انجام شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
async function bulkDeleteLinks(){
  const sel = selectedLinkUuids(); if(!sel.length) return;
  if(!confirm(`${sel.length} ${t('اینباند حذف شود؟')}`)) return;
  try{ await Promise.all(sel.map(uid=>api(`/api/links/${uid}`, {method:'DELETE'}))); toast('حذف گروهی انجام شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
async function openClients(uid){
  const inbound=LINKS.find(x=>x.uuid===uid); if(!inbound) return;
  try{
    const d=await api(`/api/links/${uid}/clients`);
    const clients=d.clients||[];
    openDrawer(`Client Manager · ${escapeHtml(inbound.label||'Inbound')}`, `
      <div class="client-manager">
        <div class="client-hero"><div><b>مدیریت کلاینت‌های واقعی</b><small>هر کلاینت UUID مستقل دارد و برای پروتکل‌های Live مستقیماً توسط Relay قابل احراز است.</small></div><span class="badge ${inbound.live_status==='live'?'green':'red'}">${inbound.live_status==='live'?'LIVE':'LINK-ONLY'}</span></div>
        ${inbound.live_status!=='live'?`<div class="notice danger-note">این اینباند فعلاً فقط لینک تولید می‌کند. برای Client واقعی، ابتدا یک ترکیب Live مثل VLESS + WS/TCP/XHTTP انتخاب کنید.</div>`:''}
        <div class="client-create"><div class="grp"><label>نام کلاینت</label><input id="clientName" placeholder="مثلاً iPhone · User 01"></div><div class="row2"><div class="grp"><label>حجم (GB، خالی = والد)</label><input id="clientLimit" type="number" min="0" placeholder="0"></div><div class="grp"><label>انقضا (روز، 0 = والد)</label><input id="clientDays" type="number" min="0" placeholder="0"></div></div><button class="btn primary" style="width:100%" onclick="createClient('${uid}')"><i class="ti ti-user-plus"></i>ساخت کلاینت واقعی</button></div>
        <div class="client-list">${clients.length?clients.map(c=>`<article class="client-row"><div class="client-avatar"><i class="ti ti-device-laptop"></i></div><div class="client-main"><b>${escapeHtml(c.label||'Client')}</b><small class="mono">${escapeHtml(c.uuid)}</small><div class="client-tags"><span>${c.active?'فعال':'خاموش'}</span><span>${fmtBytes(c.used_bytes||0)}${c.limit_bytes?' / '+fmtBytes(c.limit_bytes):''}</span><span>${c.expires_at?escapeHtml(c.expires_at.slice(0,10)):'∞'}</span></div></div><div class="client-actions"><button class="iconbtn" title="لینک اشتراک" onclick="showClientSubLink(${escapeHtml(JSON.stringify(c.sub||''))})"><i class="ti ti-qrcode"></i></button><button class="iconbtn" title="کپی VLESS" onclick="copyText(${escapeHtml(JSON.stringify(c.vless_full||''))})"><i class="ti ti-copy"></i></button><button class="iconbtn" title="تعویض لینک (UUID جدید)" onclick="regenerateClient('${uid}','${c.uuid}')"><i class="ti ti-replace"></i></button><button class="iconbtn" title="ریست حجم مصرفی" onclick="resetClientUsage('${uid}','${c.uuid}')"><i class="ti ti-refresh"></i></button><button class="iconbtn" title="حذف" onclick="deleteClient('${uid}','${c.uuid}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button></div></article>`).join(''):'<div class="empty-client">هنوز کلاینتی برای این اینباند ساخته نشده.</div>'}</div>
      </div>
  `, `<button class="btn" style="width:100%" onclick="loadLinks();openClients('${uid}')"><i class="ti ti-refresh"></i>بروزرسانی</button>`);
  }catch(e){toast(e.message,false)}
}
async function createClient(uid){
  const label=$('clientName')?.value||''; const limit=Number($('clientLimit')?.value||0); const days=Number($('clientDays')?.value||0);
  try{await api(`/api/links/${uid}/clients`,{method:'POST',body:JSON.stringify({label,limit_bytes:limit?limit*1024*1024*1024:0,expires_days:days})});toast('کلاینت واقعی ساخته شد ✓');openClients(uid);loadLinks();}catch(e){toast(e.message,false)}
}
async function deleteClient(uid,cid){
  if(!confirm(t('این کلاینت حذف شود؟'))) return;
  try{await api(`/api/links/${uid}/clients/${cid}`,{method:'DELETE'});toast('کلاینت حذف شد');openClients(uid);loadLinks();}catch(e){toast(e.message,false)}
}
async function regenerateClient(uid,cid){
  if(!confirm(t('یک لینک/UUID جدید برای این کلاینت صادر شود؟ لینک قبلی بلافاصله از کار می‌افتد و باید لینک جدید را دوباره برای کاربر بفرستید.'))) return;
  try{await api(`/api/links/${cid}/regenerate`,{method:'POST'});toast('لینک کلاینت تعویض شد ✓');openClients(uid);loadLinks();}catch(e){toast(e.message,false)}
}
async function resetClientUsage(uid,cid){
  if(!confirm(t('حجم مصرفی این کلاینت از صفر شروع شود؟'))) return;
  try{await api(`/api/links/${cid}/reset-usage`,{method:'POST'});toast('حجم مصرف ریست شد ✓');openClients(uid);loadLinks();}catch(e){toast(e.message,false)}
}

// ============================================================
// Standalone Client Manager page (بخش جدای ساخت کلاینت)
// ============================================================
let CM_INBOUNDS = [];
let CM_SELECTED_UID = '';
async function loadClientManager(){
  try{
    const res = await api('/api/links');
    CM_INBOUNDS = res.links || [];
    const sel = $('cmInboundSelect');
    const keep = CM_SELECTED_UID;
    sel.innerHTML = '<option value="">— انتخاب کنید —</option>' + CM_INBOUNDS.map(l=>
      `<option value="${l.uuid}">${escapeHtml(l.label||'Inbound')} · ${escapeHtml(protoLabel(l))} ${l.live_status==='live'?'(LIVE)':'(LINK-ONLY)'}</option>`
    ).join('');
    if(keep && CM_INBOUNDS.some(l=>l.uuid===keep)){
      sel.value = keep;
      loadClientManagerClients(keep);
    } else {
      $('cmInboundInfo').innerHTML = '';
      $('cmBody').innerHTML = `<div class="empty"><i class="ti ti-router"></i>ابتدا یک اینباند را از بالا انتخاب کن</div>`;
    }
  }catch(e){ toast(e.message, false); }
}
async function loadClientManagerClients(uid){
  CM_SELECTED_UID = uid || '';
  if(!uid){
    $('cmInboundInfo').innerHTML = '';
    $('cmBody').innerHTML = `<div class="empty"><i class="ti ti-router"></i>ابتدا یک اینباند را از بالا انتخاب کن</div>`;
    return;
  }
  const inbound = CM_INBOUNDS.find(x=>x.uuid===uid);
  try{
    const d = await api(`/api/links/${uid}/clients`);
    const clients = d.clients || [];
    $('cmInboundInfo').innerHTML = inbound ? `
      <div class="client-hero" style="margin-top:12px"><div><b>${escapeHtml(inbound.label||'Inbound')}</b><small>${escapeHtml(protoLabel(inbound))} · ${escapeHtml(inbound.address||'')}:${inbound.port||443}</small></div><span class="badge ${inbound.live_status==='live'?'green':'red'}">${inbound.live_status==='live'?'LIVE':'LINK-ONLY'}</span></div>
      ${inbound.live_status!=='live'?`<div class="notice danger-note" style="margin-top:10px">این اینباند فعلاً فقط لینک تولید می‌کند. برای Client واقعی، ابتدا یک ترکیب Live مثل VLESS + WS/TCP/XHTTP انتخاب کنید.</div>`:''}
    ` : '';
    $('cmBody').innerHTML = `
      <div class="card" style="padding:16px;margin-bottom:14px">
        <div class="client-create">
          <div class="grp"><label>نام کلاینت</label><input id="cmClientName" placeholder="مثلاً iPhone · User 01"></div>
          <div class="row2">
            <div class="grp"><label>حجم (GB، خالی = والد)</label><input id="cmClientLimit" type="number" min="0" placeholder="0"></div>
            <div class="grp"><label>انقضا (روز، 0 = والد)</label><input id="cmClientDays" type="number" min="0" placeholder="0"></div>
          </div>
          <button class="btn primary" style="width:100%" onclick="createClientMgr('${uid}')"><i class="ti ti-user-plus"></i>ساخت کلاینت واقعی</button>
        </div>
      </div>
      <div class="card" style="padding:16px">
        <div class="panel-head" style="padding:0 0 12px;border:0"><div><b>کلاینت‌های این اینباند</b><small>${clients.length} کلاینت</small></div></div>
        <div class="client-list">${clients.length ? clients.map(c=>`<article class="client-row"><div class="client-avatar"><i class="ti ti-device-laptop"></i></div><div class="client-main"><b>${escapeHtml(c.label||'Client')}</b><small class="mono">${escapeHtml(c.uuid)}</small><div class="client-tags"><span>${c.active?'فعال':'خاموش'}</span><span>${fmtBytes(c.used_bytes||0)}${c.limit_bytes?' / '+fmtBytes(c.limit_bytes):''}</span><span>${c.expires_at?escapeHtml(c.expires_at.slice(0,10)):'∞'}</span></div></div><div class="client-actions"><button class="iconbtn" title="لینک اشتراک" onclick="showClientSubLink(${escapeHtml(JSON.stringify(c.sub||''))})"><i class="ti ti-qrcode"></i></button><button class="iconbtn" title="کپی VLESS" onclick="copyText(${escapeHtml(JSON.stringify(c.vless_full||''))})"><i class="ti ti-copy"></i></button><button class="iconbtn" title="تعویض لینک (UUID جدید)" onclick="regenerateClientMgr('${uid}','${c.uuid}')"><i class="ti ti-replace"></i></button><button class="iconbtn" title="ریست حجم مصرفی" onclick="resetClientMgrUsage('${uid}','${c.uuid}')"><i class="ti ti-refresh"></i></button><button class="iconbtn" title="حذف" onclick="deleteClientMgr('${uid}','${c.uuid}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button></div></article>`).join('') : '<div class="empty-client">هنوز کلاینتی برای این اینباند ساخته نشده.</div>'}</div>
      </div>
    `;
  }catch(e){ toast(e.message, false); }
}
async function createClientMgr(uid){
  const label = $('cmClientName').value.trim();
  const limit = Number($('cmClientLimit').value) || 0;
  const days = Number($('cmClientDays').value) || 0;
  try{
    await api(`/api/links/${uid}/clients`, {method:'POST', body: JSON.stringify({label, limit_bytes: limit ? limit*1024*1024*1024 : 0, expires_days: days})});
    toast('کلاینت واقعی ساخته شد ✓');
    loadClientManagerClients(uid);
  }catch(e){ toast(e.message, false); }
}
async function deleteClientMgr(uid, cid){
  if(!confirm(t('این کلاینت حذف شود؟'))) return;
  try{ await api(`/api/links/${uid}/clients/${cid}`, {method:'DELETE'}); toast('کلاینت حذف شد'); loadClientManagerClients(uid); }
  catch(e){ toast(e.message, false); }
}
async function regenerateClientMgr(uid, cid){
  if(!confirm(t('یک لینک/UUID جدید برای این کلاینت صادر شود؟ لینک قبلی بلافاصله از کار می‌افتد و باید لینک جدید را دوباره برای کاربر بفرستید.'))) return;
  try{ await api(`/api/links/${cid}/regenerate`, {method:'POST'}); toast('لینک کلاینت تعویض شد ✓'); loadClientManagerClients(uid); }
  catch(e){ toast(e.message, false); }
}
async function resetClientMgrUsage(uid, cid){
  if(!confirm(t('حجم مصرفی این کلاینت از صفر شروع شود؟'))) return;
  try{ await api(`/api/links/${cid}/reset-usage`, {method:'POST'}); toast('حجم مصرف ریست شد ✓'); loadClientManagerClients(uid); }
  catch(e){ toast(e.message, false); }
}
async function copyText(v){
  v = v || '';
  if(window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText){
    try{ await navigator.clipboard.writeText(v); toast('کپی شد ✓'); return; }catch(e){ /* برو سراغ روش قدیمی */ }
  }
  if(legacyCopy(v)){ toast('کپی شد ✓'); } else { prompt('کپی کنید:', v); }
}
function showClientSubLink(subUrl){
  if(!subUrl){ toast('لینک ساب برای این کلاینت در دسترس نیست', false); return; }
  const qr = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + encodeURIComponent(subUrl);
  openDrawer('لینک اشتراک کلاینت', `
    <div class="qr-box"><img src="${qr}"></div>
    <div class="grp"><label>لینک ساب</label><div class="copy-row"><input readonly value="${escapeHtml(subUrl)}" id="clientSubLinkInp"></div></div>
    <p class="hint">اگر این لینک برای مشتری باز نمی‌شود، ابتدا از تب «تنظیمات» آدرس عمومی پنل را درست تنظیم کنید.</p>
  `, `<button class="btn primary" style="width:100%" onclick="copyInput('clientSubLinkInp')"><i class="ti ti-copy"></i>کپی لینک ساب</button>`);
}

function showSubLink(uid){
  const l = LINKS.find(x=>x.uuid===uid);
  if(!l) return;
  const qr = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + encodeURIComponent(l.sub_url || l.sub);
  openDrawer('لینک اشتراک', `
    <div class="qr-box"><img src="${qr}"></div>
    <div class="grp"><label>لینک ساب</label><div class="copy-row"><input readonly value="${escapeHtml(l.sub_url||l.sub)}" id="subLinkInp"></div></div>
    <div class="grp"><label>صفحه‌ی نمایش اشتراک (برای مشتری)</label><div class="copy-row"><input readonly value="${escapeHtml((l.sub_url||l.sub||'').replace('/sub/','/subscription/'))}" id="subPortalInp"></div></div>
    <p class="hint">اگر این لینک برای مشتری باز نمی‌شود، ابتدا از تب «تنظیمات» آدرس عمومی پنل را درست تنظیم کنید.</p>
  `, `<button class="btn primary" style="width:100%" onclick="copyInput('subLinkInp')"><i class="ti ti-copy"></i>کپی لینک ساب</button>`);
}
function legacyCopy(text){
  // execCommand روی همه‌ی مرورگرها حتی بدون HTTPS (secure context) کار می‌کند.
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.top = '-9999px';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  let ok = false;
  try{ ok = document.execCommand('copy'); }catch(e){ ok = false; }
  document.body.removeChild(ta);
  return ok;
}
async function copyInput(id){
  const el = $(id);
  if(!el) return;
  const value = el.value || '';
  el.focus();
  el.select();
  // navigator.clipboard فقط در HTTPS (secure context) در دسترسه؛ اگر پنل با HTTP
  // (بدون دامنه/SSL) باز شده باشه این آبجکت اصلاً وجود نداره و باید مستقیم به
  // روش قدیمی (execCommand) یا در آخرین حالت به prompt دستی سوییچ کنیم.
  if(window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText){
    try{
      await navigator.clipboard.writeText(value);
      toast('کپی شد ✓');
      return;
    }catch(e){ /* برو سراغ روش قدیمی */ }
  }
  if(legacyCopy(value)){
    toast('کپی شد ✓');
  } else {
    prompt('کپی کنید:', value);
  }
}
async function toggleLink(uid, active){
  try{ await api(`/api/links/${uid}`, {method:'PATCH', body: JSON.stringify({active})}); toast('بروزرسانی شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
async function deleteLink(uid){
  if(!confirm(t('این کانفیگ حذف شود؟'))) return;
  try{ await api(`/api/links/${uid}`, {method:'DELETE'}); toast('حذف شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
async function resetLinkUsage(uid){
  if(!confirm(t('حجم مصرفی این کانفیگ از صفر شروع شود؟'))) return;
  try{ await api(`/api/links/${uid}/reset-usage`, {method:'POST'}); toast('حجم مصرف ریست شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
async function regenerateLink(uid){
  if(!confirm(t('یک لینک/UUID جدید صادر شود؟ لینک قبلی بلافاصله از کار می‌افتد و باید لینک جدید را دوباره برای کاربر بفرستید.'))) return;
  try{ const r = await api(`/api/links/${uid}/regenerate`, {method:'POST'}); toast('لینک جدید صادر شد'); loadLinks(); showSubLink(r.uuid); }
  catch(e){ toast(e.message, false); }
}
async function openAutoLink(){
  try{ await api('/api/links/auto', {method:'POST', body: JSON.stringify({profile:'balanced'})}); toast('کانفیگ خودکار ساخته شد'); loadLinks(); }
  catch(e){ toast(e.message, false); }
}
// Single source of truth for turning a link's stored fields into
// {base_protocol, network, security}. Both the builder's initial render and
// the edit-drawer's hidden-field sync must agree, or the visible transport
// card and the value that actually gets submitted can diverge (this used to
// happen for links whose `protocol` was a legacy shortcut like "vless-ws":
// the card correctly showed WebSocket, but the hidden #mNetwork field fell
// back to a stale/defaulted "tcp" a moment later).
function deriveManualParts(l){
  l = l || {};
  const proto = l.protocol || 'manual';
  if(proto === 'manual'){
    // Created by the advanced builder: base_protocol/network/security were
    // explicitly written by the backend and are always reliable.
    return {bp: l.base_protocol || 'vless', net: l.network || 'ws', sec: l.security || 'tls'};
  }
  if(proto==='vless-ws') return {bp:'vless',net:'ws',sec:'tls'};
  if(proto==='vless-tcp') return {bp:'vless',net:'tcp',sec:'none'};
  if(proto.startsWith('xhttp-')) return {bp:'vless',net:'xhttp',sec:'tls'};
  if(proto==='vmess-ws') return {bp:'vmess',net:'ws',sec:'tls'};
  if(proto==='trojan-ws') return {bp:'trojan',net:'ws',sec:'tls'};
  return {bp: l.base_protocol || 'vless', net: l.network || 'ws', sec: l.security || 'tls'};
}
function manualBuilderHtml(l){
  l = l || {};
  const parts = deriveManualParts(l);
  let bp = parts.bp, net = parts.net, sec = parts.sec;
  const methods = MANUAL_META.shadowsocks_methods || ['chacha20-ietf-poly1305','aes-128-gcm','aes-256-gcm'];
  const icons = {vless:'ti-bolt',vmess:'ti-brand-vscode',trojan:'ti-shield-lock',shadowsocks:'ti-brand-shield'};
  const bpLabels = {vless:'VLESS',vmess:'VMess',trojan:'Trojan',shadowsocks:'Shadowsocks'};
  const nets = [
    ['tcp','TCP','Raw / direct','ti-arrows-right-left'],
    ['ws','WebSocket','WS over HTTP','ti-world'],
    ['grpc','gRPC','HTTP/2 transport','ti-transfer'],
    ['xhttp','XHTTP','Modern HTTP transport','ti-brand-xamarin']
  ];
  const secs = (MANUAL_META.securities||[]);
  const fpOpts=(MANUAL_META.fingerprints||['chrome','firefox','safari','ios','android','edge','random']).map(x=>`<option value="${x}" ${(l.fingerprint||'chrome')===x?'selected':''}>${x}</option>`).join('');
  const methodOpts=methods.map(x=>`<option value="${x}" ${(l.ss_method||methods[0])===x?'selected':''}>${x}</option>`).join('');
  const conn=Number(l.connection_limit||0), speed=Number(l.speed_limit_bytes||0), speedMbit=speed?Math.max(1,Math.round(speed*8/1000000)):'';
  return `
    <div class="inbound-builder">
      <div class="ib-hero">
        <div class="ib-title"><div class="ib-icon"><i class="ti ti-adjustments-horizontal"></i></div><div><b>${l.uuid?'ویرایش اینباند':'ساخت اینباند حرفه‌ای'}</b><small>پروتکل پایه، ترنسپورت و امنیت کاملاً تفکیک‌شده</small></div></div>
        <span class="badge gray">INBOUND BUILDER</span>
      </div>

      <div class="ib-section">
        <div class="ib-section-body">
          <div class="ib-step"><span class="num">1</span><div><b>پروتکل پایه</b><small>اول مشخص کن با چه پروتکلی کانفیگ ساخته شود</small></div></div>
          <div id="ibProtocolCards" class="ib-matrix">
            ${Object.entries(bpLabels).map(([id,label])=>`<label class="ib-opt ${bp===id?'on':''}" data-proto-card="${id}"><input type="radio" name="ibBaseProtocol" value="${id}" ${bp===id?'checked':''} onchange="selectBaseProtocol('${id}')"><span class="ib-opt-icon"><i class="ti ${icons[id]||'ti-network'}"></i></span><span><b>${label}</b><small>${id==='vless'?'UUID / XTLS ecosystem':id==='vmess'?'Legacy-compatible':id==='trojan'?'Password-style auth':'AEAD proxy'}</small></span></label>`).join('')}
          </div>
        </div>
      </div>

      <div class="ib-section">
        <div class="ib-section-body">
          <div class="ib-step"><span class="num">2</span><div><b>Transport / Network</b><small>حالا مسیر انتقال را جداگانه انتخاب کن</small></div></div>
          <div id="ibTransportCards" class="ib-matrix">
            ${nets.map(([id,label,sub,icon])=>`<label class="ib-opt ${net===id?'on':''}" data-net-card="${id}"><input type="radio" name="ibNetwork" value="${id}" ${net===id?'checked':''} onchange="selectTransport('${id}')"><span class="ib-opt-icon"><i class="ti ${icon}"></i></span><span><b>${label}</b><small>${sub}</small></span></label>`).join('')}
          </div>
          <div id="ibTransportNote" class="ib-status" style="margin-top:10px"></div>
        </div>
      </div>

      <div class="ib-section">
        <div class="ib-section-body">
          <div class="ib-step"><span class="num">3</span><div><b>Security</b><small>TLS / Reality / None را مستقل از ترنسپورت انتخاب کن</small></div></div>
          <div id="ibSecurityCards" class="ib-matrix">
            ${secs.map(x=>`<label class="ib-opt ${sec===x.id?'on':''}" data-sec-card="${x.id}"><input type="radio" name="ibSecurity" value="${x.id}" ${sec===x.id?'checked':''} onchange="selectSecurity('${x.id}')"><span class="ib-opt-icon"><i class="ti ${x.id==='reality'?'ti-key':x.id==='tls'?'ti-lock':'ti-lock-open'}"></i></span><span><b>${x.label}</b><small>${x.id==='reality'?'Reality public-key mode':x.id==='tls'?'Standard TLS':'No TLS wrapper'}</small></span></label>`).join('')}
          </div>
          <div id="mLiveHint" class="ib-status" style="margin-top:10px"></div>
        </div>
      </div>

      <div class="ib-section">
        <div class="ib-section-head"><div><b>4. Endpoint & Advanced Parameters</b><small>فقط فیلدهای مرتبط با انتخاب بالا نمایش داده می‌شوند</small></div><i class="ti ti-server-2"></i></div>
        <div class="ib-section-body">
          <div class="ib-grid">
            <div class="grp"><label>نام / Remark</label><input id="fLabel" value="${escapeHtml(l.label||'')}" placeholder="مثلاً: VIP-01"></div>
            <div class="grp"><label>دسته‌بندی</label><select id="fCategory"><option value="0">بدون دسته</option>${CATEGORIES.map(c=>`<option value="${c.id}" ${String(l.category_id)===String(c.id)?'selected':''}>${escapeHtml(c.name)}</option>`).join('')}</select></div>
            <div class="grp"><label>آدرس / Domain</label><div class="endpoint-input"><input id="mAddress" placeholder="example.com" value="${escapeHtml(l.address||'')}" oninput="updateBuilderSummary()"><button type="button" class="btn endpoint-btn" onclick="loadRailwayEndpoint()"><i class="ti ti-cloud"></i>Railway</button></div></div>
            <div class="grp"><label>Port</label><div class="endpoint-input"><input id="mPort" type="number" min="1" max="65535" value="${l.port||443}" oninput="updateBuilderSummary()"><button type="button" class="btn endpoint-btn" onclick="testCurrentTcp()"><i class="ti ti-activity"></i>Ping</button></div></div>
            <div class="grp"><label>Fingerprint</label><select id="mFingerprint">${fpOpts}</select></div>
            <div class="grp"><label>ALPN</label><input id="mAlpn" value="${escapeHtml(l.alpn||'')}" placeholder="h2,http/1.1"></div>
            <div id="mWsXhttpWrap" class="ib-grid ib-full">
              <div class="grp"><label>Path</label><input id="mPath" placeholder="/ws" value="${escapeHtml(l.path||'')}"></div>
              <div class="grp"><label>Host Header</label><input id="mHost" placeholder="domain.com" value="${escapeHtml(l.host_header||'')}"></div>
            </div>
            <div id="mXhttpModeWrap" class="grp ib-full"><label>XHTTP Mode</label><select id="mXhttpMode">${(MANUAL_META.xhttp_modes||['auto','packet-up','stream-up','stream-one']).map(x=>`<option value="${x}" ${(l.xhttp_mode||'auto')===x?'selected':''}>${x}</option>`).join('')}</select></div>
            <div id="mGrpcWrap" class="ib-grid ib-full"><div class="grp"><label>Service Name</label><input id="mGrpcService" placeholder="service" value="${escapeHtml(l.grpc_service_name||'')}"></div><div class="grp"><label>gRPC Mode</label><select id="mGrpcMode"><option value="gun" ${(l.grpc_mode||'gun')==='gun'?'selected':''}>gun</option><option value="multi" ${l.grpc_mode==='multi'?'selected':''}>multi</option></select></div></div>
            <div id="mTcpWrap" class="ib-grid ib-full"><div class="grp"><label>Header Type</label><select id="mHeaderType"><option value="" ${!l.header_type?'selected':''}>none</option><option value="http" ${l.header_type==='http'?'selected':''}>http</option></select></div><div class="grp"><label>Flow</label><select id="mFlow"><option value="" ${!l.flow?'selected':''}>—</option><option value="xtls-rprx-vision" ${l.flow==='xtls-rprx-vision'?'selected':''}>xtls-rprx-vision</option></select></div></div>
            <div id="mTlsWrap" class="ib-grid ib-full"><div class="grp"><label>SNI</label><input id="mSni" value="${escapeHtml(l.sni||'')}" placeholder="example.com"></div><label class="chk" style="align-self:end;margin-bottom:16px"><input id="mAllowInsecure" type="checkbox" ${l.allow_insecure?'checked':''}> Allow Insecure</label></div>
            <div id="mRealityWrap" class="ib-grid ib-full"><div class="grp"><label>Reality SNI</label><input id="mRealitySni" value="${escapeHtml(l.sni||'')}" placeholder="www.example.com"></div><div class="grp"><label>Public Key</label><input id="mRealityPbk" value="${escapeHtml(l.reality_public_key||'')}" placeholder="public key"></div><div class="grp"><label>Short ID</label><input id="mRealitySid" value="${escapeHtml(l.reality_short_id||'')}" placeholder="short id"></div><div class="grp"><label>Spider X</label><input id="mRealitySpx" value="${escapeHtml(l.reality_spider_x||'/')}" placeholder="/"></div><div class="ib-full"><button type="button" class="btn" onclick="generateRealityKeys()"><i class="ti ti-key"></i>Generate Reality Keypair</button></div></div>
            <div id="mShadowWrap" class="ib-grid ib-full"><div class="grp"><label>Encryption Method</label><select id="mSsMethod">${methodOpts}</select></div><div class="grp"><label>Password</label><input id="mSsPassword" type="password" value="${escapeHtml(l.ss_password||'')}" placeholder="Password / secret"></div></div>
            <div class="grp"><label>حجم (GB)</label><input id="fLimitVal" type="number" min="0" value="${l.limit_bytes?Math.round(l.limit_bytes/1073741824):''}"></div>
            <div class="grp"><label>اعتبار (روز)</label><input id="fDays" type="number" min="0" value="${l.expires_at?Math.max(0,Math.ceil((new Date(l.expires_at).getTime()-Date.now())/86400000)):''}"></div>
            <div class="grp"><label>زمان دقیق انقضا</label><input id="fExpiresAt" type="datetime-local" value="${l.expires_at?new Date(l.expires_at).toISOString().slice(0,16):''}"></div>
            <div class="grp"><label>IP Limit</label><input id="fIpLimit" type="number" min="0" value="${l.ip_limit||0}"></div>
            <div class="grp"><label>Connection Limit</label><input id="fConnLimit" type="number" min="0" value="${conn}"></div>
            <div class="grp"><label>تعداد کاربر</label><input id="fClientLimit" type="number" min="0" max="1000" value="${l.client_limit||0}" placeholder="0 = نامحدود"></div>
            <div class="grp"><label>تعداد خروجی</label><input id="fConfigCount" type="number" min="1" max="40" value="${l.config_count||1}"></div>
            <div class="grp"><label>Speed (Mbit/s)</label><input id="fSpeed" type="number" min="0" value="${speedMbit}" placeholder="0 = نامحدود"></div>
            <div class="grp ib-full"><label>یادداشت داخلی</label><input id="fNote" value="${escapeHtml(l.note||'')}" placeholder="توضیحات اختیاری"></div>
          </div>
        </div>
      </div>

      <div class="ib-section">
        <div class="ib-section-body"><div class="ib-step"><span class="num">5</span><div><b>Summary</b><small>قبل از ذخیره ترکیب نهایی را بررسی کن</small></div></div>
          <div class="ib-summary"><div class="sum"><small>PROTOCOL</small><b id="sumProtocol">${bp.toUpperCase()}</b></div><div class="sum"><small>NETWORK</small><b id="sumNetwork">${net.toUpperCase()}</b></div><div class="sum"><small>SECURITY</small><b id="sumSecurity">${sec.toUpperCase()}</b></div><div class="sum"><small>PORT</small><b id="sumPort">${l.port||443}</b></div><div class="sum"><small>TRAFFIC</small><b id="sumTraffic">—</b></div><div class="sum"><small>LIMITS</small><b id="sumLimits">—</b></div></div>
        </div>
      </div>
    </div>`;
}

function refreshInboundCards(){
  const bp=$('mBase')?.value || document.querySelector('input[name="ibBaseProtocol"]:checked')?.value || 'vless';
  const net=$('mNetwork')?.value || document.querySelector('input[name="ibNetwork"]:checked')?.value || 'ws';
  const sec=$('mSecurity')?.value || document.querySelector('input[name="ibSecurity"]:checked')?.value || 'tls';
  document.querySelectorAll('[data-proto-card]').forEach(e=>e.classList.toggle('on',e.dataset.protoCard===bp));
  document.querySelectorAll('[data-net-card]').forEach(e=>e.classList.toggle('on',e.dataset.netCard===net));
  document.querySelectorAll('[data-sec-card]').forEach(e=>e.classList.toggle('on',e.dataset.secCard===sec));
}
function selectBaseProtocol(id){
  let hidden=document.getElementById('mBase'); if(!hidden){hidden=document.createElement('input');hidden.type='hidden';hidden.id='mBase';document.body.appendChild(hidden)} hidden.value=id;
  const ss=id==='shadowsocks';
  const secWrap=document.getElementById('ibSecurityCards');
  if(secWrap){document.querySelectorAll('[data-sec-card]').forEach(e=>{const sid=e.dataset.secCard; e.classList.toggle('off',ss && sid!=='none'); const inp=e.querySelector('input'); if(inp) inp.disabled=ss&&sid!=='none';}); if(ss){selectSecurity('none');}}
  if(ss && document.querySelector('input[name="ibNetwork"]:checked')?.value!=='tcp') selectTransport('tcp');
  document.getElementById('mShadowWrap')?.style.setProperty('display',ss?'':'none');
  refreshInboundCards(); onManualChange(); updateBuilderSummary();
}
function selectTransport(id){
  let hidden=document.getElementById('mNetwork'); if(!hidden){hidden=document.createElement('input');hidden.type='hidden';hidden.id='mNetwork';document.body.appendChild(hidden)} hidden.value=id;
  const ss=document.getElementById('mBase')?.value==='shadowsocks';
  if(ss && id!=='tcp'){toast('Shadowsocks در این سازنده فقط با TCP پشتیبانی می‌شود',false);hidden.value='tcp';return selectTransport('tcp');}
  refreshInboundCards(); onManualChange(); updateBuilderSummary();
}
function selectSecurity(id){
  let hidden=document.getElementById('mSecurity'); if(!hidden){hidden=document.createElement('input');hidden.type='hidden';hidden.id='mSecurity';document.body.appendChild(hidden)} hidden.value=id;
  refreshInboundCards(); onManualChange(); updateBuilderSummary();
}

function updateBuilderSummary(){
  const val=id=>$(id)?.value || '—'; const set=(id,v)=>{const e=$(id);if(e)e.textContent=v};
  set('sumProtocol',(val('mBase')||'vless').toUpperCase()); set('sumNetwork',(val('mNetwork')||'tcp').toUpperCase()); set('sumSecurity',(val('mSecurity')||'none').toUpperCase()); set('sumPort',val('mPort'));
  const traffic=Number(val('fLimitVal'))||0; set('sumTraffic',traffic?`${traffic} GB`:'نامحدود');
  const ip=Number(val('fIpLimit'))||0, conn=Number(val('fConnLimit'))||0; set('sumLimits',`IP ${ip||'∞'} / CONN ${conn||'∞'}`);
}
function onManualChange(){
  const base=$('mBase')?.value || 'vless', net=$('mNetwork')?.value || 'ws', sec=$('mSecurity')?.value || 'tls';
  const show=(id,yes)=>{const e=$(id);if(e)e.style.display=yes?'':'none'};
  show('mWsXhttpWrap',net==='ws'||net==='xhttp'); show('mXhttpModeWrap',net==='xhttp'); show('mGrpcWrap',net==='grpc'); show('mTcpWrap',net==='tcp'); show('mTlsWrap',sec==='tls'); show('mRealityWrap',sec==='reality'); show('mShadowWrap',base==='shadowsocks');
  if(base==='shadowsocks'){ if($('mNetwork') && $('mNetwork').value!=='tcp') $('mNetwork').value='tcp'; if($('mSecurity')) $('mSecurity').value='none'; }
  const hint=$('mLiveHint');
  if(hint){
    const live=base!=='shadowsocks' && (MANUAL_META.live_combos||[]).some(c=>c[0]===net&&c[1]===sec) && !(net==='xhttp'&&($('mXhttpMode')?.value||'auto')==='stream-one');
    hint.className='ib-status '+(live?'ok':'warn'); hint.innerHTML=live?'<i class="ti ti-circle-check"></i> این ترکیب آماده استفاده است.':'<i class="ti ti-alert-triangle"></i> این ترکیب برای ساخت لینک و مدیریت سرویس آماده شده است.';
  }
  const tn=$('ibTransportNote');
  if(tn){tn.innerHTML=base==='shadowsocks'?'<i class="ti ti-info-circle"></i> Shadowsocks به‌صورت TCP-only در این Builder ارائه می‌شود.':'<i class="ti ti-adjustments-horizontal"></i> Transport فقط مسیر انتقال است و جدا از پروتکل پایه انتخاب می‌شود.';}
  refreshInboundCards(); updateBuilderSummary();
}

async function testCurrentTcp(){
  const host=($('mAddress')?.value||'').trim();
  const port=Number($('mPort')?.value||0);
  if(!host){toast('ابتدا آدرس یا دامنه را وارد کنید',false);return}
  if(!Number.isInteger(port)||port<1||port>65535){toast('پورت نامعتبر است',false);return}
  const btn=document.querySelector('.endpoint-btn[onclick="testCurrentTcp()"]');
  if(btn){btn.disabled=true;btn.innerHTML='<i class="ti ti-loader-2 spin"></i> در حال تست'}
  try{
    const r=await api('/api/network/tcp-ping',{method:'POST',body:JSON.stringify({host,port,timeout:4})});
    if(r.ok) toast(`TCP OK • ${r.latency_ms}ms • ${host}:${port}`);
    else toast(r.message||'اتصال برقرار نشد',false);
  }catch(e){toast(e.message||'خطا در تست TCP',false)}
  finally{if(btn){btn.disabled=false;btn.innerHTML='<i class="ti ti-activity"></i> تست پینگ'}}
}

async function loadRailwayEndpoint(){
  try{
    const r=await api('/api/network/railway');
    if(!r.is_railway && !r.tcp_proxy_domain){toast('اطلاعات TCP Proxy ریل‌وی در این سرویس پیدا نشد',false);return}
    if(r.tcp_proxy_domain){$('mAddress').value=r.tcp_proxy_domain; if(r.tcp_proxy_port) $('mPort').value=r.tcp_proxy_port; updateBuilderSummary(); toast(`Railway TCP Proxy: ${r.tcp_proxy_domain}:${r.tcp_proxy_port||'?'}`)}
    else if(r.public_domain){$('mAddress').value=r.public_domain; updateBuilderSummary(); toast('دامنه عمومی Railway وارد شد؛ برای TCP خام باید TCP Proxy فعال باشد')}
  }catch(e){toast(e.message||'خطا در دریافت اطلاعات Railway',false)}
}

async function generateRealityKeys(){
  try{ const r=await api('/api/reality-keypair'); $('mRealityPbk').value=r.public_key; $('mRealitySid').value=r.short_id; toast('کلید Reality ساخته شد. Private Key را روی نود خودتان نگه دارید.'); }
  catch(e){ toast(e.message, false); }
}

function onProtocolModeChange(){
  // Kept for compatibility with older inline handlers; the new builder is always advanced.
  const wrap=$('manualBuilderWrap'); if(wrap) wrap.style.display='block'; const quick=$('quickFieldsWrap'); if(quick) quick.style.display='none';
}
function openLinkDrawer(uid){
  const editing=!!uid, l=editing?(LINKS.find(x=>x.uuid===uid)||{}):{};
  openDrawer(editing?'ویرایش اینباند':'ساخت اینباند', `${manualBuilderHtml(l)}`,
    `${editing?`<button class="btn danger" onclick="deleteLink('${uid}');closeDrawer()"><i class="ti ti-trash"></i>حذف</button>`:''}<button class="btn primary" style="flex:1" onclick="submitLink('${uid||''}')"><i class="ti ti-device-floppy"></i>${editing?'ذخیره تغییرات':'ساخت اینباند'}</button>`);
  setTimeout(()=>{
    let bp=document.getElementById('mBase'); if(!bp){bp=document.createElement('input');bp.type='hidden';bp.id='mBase';document.querySelector('.drawer .dr-body')?.appendChild(bp)}
    let net=document.getElementById('mNetwork'); if(!net){net=document.createElement('input');net.type='hidden';net.id='mNetwork';document.querySelector('.drawer .dr-body')?.appendChild(net)}
    let sec=document.getElementById('mSecurity'); if(!sec){sec=document.createElement('input');sec.type='hidden';sec.id='mSecurity';document.querySelector('.drawer .dr-body')?.appendChild(sec)}
    let proto=l.protocol||'manual'; const parts=deriveManualParts(l);
    bp.value=parts.bp;
    net.value=parts.net;
    sec.value=parts.sec;
    if(bp.value==='shadowsocks'){net.value='tcp';sec.value='none'}
    refreshInboundCards(); onManualChange(); updateBuilderSummary();
  },0);
}

async function submitLink(uid){
  const base=$('mBase')?.value || 'vless', net=$('mNetwork')?.value || 'ws', sec=$('mSecurity')?.value || 'tls';
  const port=Number($('mPort')?.value||443);
  if(!Number.isInteger(port)||port<1||port>65535){toast('پورت باید بین 1 تا 65535 باشد',false);return}
  if(base==='shadowsocks' && net!=='tcp'){toast('Shadowsocks فقط با TCP ساخته می‌شود',false);return}
  const num=id=>Math.max(0,Number($(id)?.value||0));
  const body={label:($('fLabel')?.value||'').trim(),protocol:'manual',category_id:$('fCategory')?.value||'0',limit_value:num('fLimitVal'),limit_unit:'GB',expires_days:num('fDays'),expires_at:$('fExpiresAt')?.value||'',ip_limit:num('fIpLimit'),connection_limit:num('fConnLimit'),client_limit:num('fClientLimit'),config_count:Math.max(1,Math.min(40,num('fConfigCount')||1)),speed_limit_value:num('fSpeed'),speed_limit_unit:'MBIT',note:($('fNote')?.value||'').trim(),port,fingerprint:$('mFingerprint')?.value||'chrome',alpn:$('mAlpn')?.value||''};
  body.manual={base_protocol:base,network:net,security:base==='shadowsocks'?'none':sec,address:$('mAddress')?.value||'',path:$('mPath')?.value||'',host_header:$('mHost')?.value||'',sni:sec==='reality'?($('mRealitySni')?.value||''):($('mSni')?.value||''),alpn:$('mAlpn')?.value||'',flow:$('mFlow')?.value||'',grpc_service_name:$('mGrpcService')?.value||'',grpc_mode:$('mGrpcMode')?.value||'gun',xhttp_mode:$('mXhttpMode')?.value||'auto',header_type:$('mHeaderType')?.value||'',allow_insecure:!!$('mAllowInsecure')?.checked,reality_public_key:$('mRealityPbk')?.value||'',reality_short_id:$('mRealitySid')?.value||'',reality_spider_x:$('mRealitySpx')?.value||'/',ss_method:$('mSsMethod')?.value||'chacha20-ietf-poly1305',ss_password:$('mSsPassword')?.value||''};
  try{if(uid) await api(`/api/links/${uid}`,{method:'PATCH',body:JSON.stringify(body)});else await api('/api/links',{method:'POST',body:JSON.stringify(body)});toast(uid?'اینباند بروزرسانی شد':'اینباند با موفقیت ساخته شد');closeDrawer();loadLinks();}
  catch(e){toast(e.message||'خطا در ذخیره اینباند',false)}
}

// ============================================================
// CATEGORIES
// ============================================================
async function loadCategories(){
  try{
    const res = await api('/api/categories');
    CATEGORIES = res.categories||[];
    $('catsBody').innerHTML = CATEGORIES.map(c=>`
      <tr><td>${escapeHtml(c.name)}</td><td>${c.limit_bytes?fmtBytes(c.limit_bytes):'نامحدود'}</td>
      <td>${c.expires_days||'—'}</td><td>${c.ip_limit||'—'}</td>
      <td><div class="row-actions">
        <button class="iconbtn" onclick="openCategoryDrawer('${c.id}')"><i class="ti ti-pencil"></i></button>
        ${['0','1'].includes(String(c.id))?'':`<button class="iconbtn" onclick="deleteCategory('${c.id}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button>`}
      </div></td></tr>
    `).join('') || `<tr><td colspan="5" class="empty">دسته‌بندی‌ای وجود ندارد</td></tr>`;
  }catch(e){ toast(e.message, false); }
}
function openCategoryDrawer(cid){
  const editing = !!cid;
  const c = editing ? CATEGORIES.find(x=>String(x.id)===String(cid)) : {};
  openDrawer(editing?'ویرایش دسته':'دسته جدید', `
    <div class="grp"><label>نام</label><input id="cName" value="${escapeHtml(c.name||'')}"></div>
    <div class="row2">
      <div class="grp"><label>حجم پیش‌فرض (GB)</label><input id="cLimit" type="number" min="0" value="${c.limit_bytes?Math.round(c.limit_bytes/1073741824):''}"></div>
      <div class="grp"><label>انقضا (روز)</label><input id="cDays" type="number" min="0" value="${c.expires_days||''}"></div>
    </div>
    <div class="grp"><label>محدودیت IP</label><input id="cIp" type="number" min="0" value="${c.ip_limit||''}"></div>
  `, `<button class="btn primary" style="flex:1" onclick="submitCategory('${cid||''}')"><i class="ti ti-device-floppy"></i>ذخیره</button>`);
}
async function submitCategory(cid){
  const body = {name:$('cName').value, limit_value:$('cLimit').value||0, limit_unit:'GB', expires_days:$('cDays').value||0, ip_limit:$('cIp').value||0};
  try{
    if(cid){ await api(`/api/categories/${cid}`, {method:'PATCH', body:JSON.stringify(body)}); }
    else{ await api('/api/categories', {method:'POST', body:JSON.stringify(body)}); }
    toast('ذخیره شد'); closeDrawer(); loadCategories();
  }catch(e){ toast(e.message, false); }
}
async function deleteCategory(cid){
  if(!confirm(t('این دسته حذف شود؟'))) return;
  try{ await api(`/api/categories/${cid}`, {method:'DELETE'}); toast('حذف شد'); loadCategories(); }
  catch(e){ toast(e.message, false); }
}

// ============================================================
// SUB GROUPS
// ============================================================
async function loadSubGroups(){
  try{
    const res = await api('/api/subs');
    const subs = res.subs || [];
    $('nb-subs').textContent = subs.length;
    $('subsBody').innerHTML = subs.map(s=>`
      <tr><td>${escapeHtml(s.name||'—')}</td><td>${s.links_count||0}</td>
      <td class="mono">${escapeHtml(s.sub_url||'')}</td>
      <td><div class="row-actions"><button class="iconbtn" onclick="deleteSubGroup('${s.sub_id}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button></div></td></tr>
    `).join('') || `<tr><td colspan="4" class="empty">گروهی وجود ندارد</td></tr>`;
  }catch(e){ $('subsBody').innerHTML = `<tr><td colspan="4" class="empty">در دسترس نیست</td></tr>`; }
}
function openSubGroupDrawer(){
  openDrawer('گروه ساب جدید', `<div class="grp"><label>نام گروه</label><input id="sgName" placeholder="مثلاً: بسته-VIP"></div>
  <p class="hint">بعد از ساخت گروه، از صفحه‌ی کانفیگ‌ها می‌توانید کانفیگ‌ها را به این گروه اضافه کنید.</p>`,
  `<button class="btn primary" style="flex:1" onclick="submitSubGroup()"><i class="ti ti-device-floppy"></i>ساخت</button>`);
}
async function submitSubGroup(){
  try{ await api('/api/subs', {method:'POST', body: JSON.stringify({name: $('sgName').value})}); toast('ساخته شد'); closeDrawer(); loadSubGroups(); }
  catch(e){ toast(e.message, false); }
}
async function deleteSubGroup(id){
  if(!confirm(t('این گروه حذف شود؟'))) return;
  try{ await api(`/api/subs/${id}`, {method:'DELETE'}); toast('حذف شد'); loadSubGroups(); }
  catch(e){ toast(e.message, false); }
}

// ============================================================
// PLANS
// ============================================================
async function loadPlans(){
  try{
    const res = await api('/api/plans');
    const plans = res.plans||[];
    $('plansBody').innerHTML = plans.map(p=>`
      <tr><td>${escapeHtml(p.name)}</td><td>${p.days} روز</td><td>${p.volume_gb} GB</td><td>${p.speed_mbps||0} Mbps</td>
      <td>⭐ ${p.stars}</td><td>${p.featured?'<span class="badge green">بله</span>':'—'}</td>
      <td><div class="row-actions">
        <button class="iconbtn" onclick="openPlanDrawer('${p.id}')"><i class="ti ti-pencil"></i></button>
        <button class="iconbtn" onclick="deletePlan('${p.id}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button>
      </div></td></tr>
    `).join('') || `<tr><td colspan="7" class="empty">پلنی وجود ندارد</td></tr>`;
  }catch(e){ toast(e.message, false); }
}
function openPlanDrawer(pid){
  openDrawer(pid?'ویرایش پلن':'پلن جدید', `
    <div class="grp"><label>نام</label><input id="pName"></div>
    <div class="row2"><div class="grp"><label>مدت (روز)</label><input id="pDays" type="number" value="30"></div>
    <div class="grp"><label>حجم (GB)</label><input id="pVolume" type="number" value="50"></div></div>
    <div class="row2"><div class="grp"><label>سرعت (Mbps، 0=نامحدود)</label><input id="pSpeed" type="number" value="0"></div>
    <div class="grp"><label>قیمت (Stars)</label><input id="pStars" type="number" value="99"></div></div>
    <label class="chk"><input type="checkbox" id="pFeatured"> پیشنهاد ویژه</label>
  `, `<button class="btn primary" style="flex:1" onclick="submitPlan('${pid||''}')"><i class="ti ti-device-floppy"></i>ذخیره</button>`);
}
async function submitPlan(pid){
  const body = {name:$('pName').value, days:$('pDays').value, volume_gb:$('pVolume').value, speed_mbps:$('pSpeed').value, stars:$('pStars').value, featured:$('pFeatured').checked};
  try{
    if(pid){ await api(`/api/plans/${pid}`, {method:'PATCH', body:JSON.stringify(body)}); }
    else{ await api('/api/plans', {method:'POST', body:JSON.stringify(body)}); }
    toast('ذخیره شد'); closeDrawer(); loadPlans();
  }catch(e){ toast(e.message, false); }
}
async function deletePlan(pid){
  if(!confirm(t('این پلن حذف شود؟'))) return;
  try{ await api(`/api/plans/${pid}`, {method:'DELETE'}); toast('حذف شد'); loadPlans(); }
  catch(e){ toast(e.message, false); }
}

// ============================================================
// REPORTS
// ============================================================
async function loadReports(){
  try{
    const days = $('repDays').value;
    const res = await api(`/api/reports/summary?days=${days}`);
    const t = res.totals||{};
    $('repStats').innerHTML = `
      ${statCard('ti-link','#4f7cff', t.links, 'کل کانفیگ‌ها')}
      ${statCard('ti-shopping-cart','#22c58b', t.orders, 'تعداد سفارش')}
      ${statCard('ti-star','#f5a524', t.stars, 'مجموع ⭐ فروش')}
      ${statCard('ti-users','#4f7cff', t.customers, 'مشتری‌ها')}
    `;
    $('repTopBody').innerHTML = (res.top_links||[]).map(l=>`
      <tr><td>${escapeHtml(l.label)}</td><td><span class="badge gray">${protoLabel(l)}</span></td><td class="mono">${fmtBytes(l.used_bytes)}</td></tr>
    `).join('') || `<tr><td colspan="3" class="empty">داده‌ای موجود نیست</td></tr>`;
  }catch(e){ toast(e.message, false); }
}

// ============================================================
// ADMINS
// ============================================================
const ADMIN_PERM_LABELS = {dashboard:'داشبورد',inbounds:'اینباند و کلاینت',clients:'ساخت کلاینت (بخش جدا)',subscriptions:'سابسکریپشن',categories:'دسته‌بندی',plans:'پلن فروش',reports:'گزارش‌ها',messages:'پیام‌ها و خطاها',bot:'ربات',admins:'مدیریت حساب',settings:'تنظیمات'};
async function loadAdmins(){
  try{
    const res = await api('/api/admins');
    ADMIN_CACHE = res.admins || [];
    const adminRows = res.admins || [];
    const activeAdmins = adminRows.filter(a=>a.active).length;
    if($('adminTotal')) $('adminTotal').textContent = adminRows.length;
    if($('adminActive')) $('adminActive').textContent = activeAdmins;
    $('adminsBody').innerHTML = adminRows.map(a=>{
      const isOwner = a.role==='owner';
      const initials = (a.username||'?').replace(/[^A-Za-z0-9آ-ی]/g,'').slice(0,2).toUpperCase() || '?';
      const lastLogin = a.last_login_at ? a.last_login_at.slice(0,16).replace('T',' ') : 'بدون ورود';
      const chips = isOwner
        ? '<span class="admin-perm-chip all"><i class="ti ti-shield-star"></i> دسترسی کامل</span>'
        : ((a.permissions||[]).length
            ? (a.permissions||[]).map(p=>`<span class="admin-perm-chip">${ADMIN_PERM_LABELS[p]||p}</span>`).join('')
            : '<span class="admin-perm-chip">بدون دسترسی</span>');
      const actions = isOwner ? '' : `
        <button class="iconbtn edit" title="ویرایش دسترسی" aria-label="ویرایش دسترسی" onclick="editAdmin('${a.id}')"><i class="ti ti-edit"></i></button>
        <button class="iconbtn power" title="${a.active?'غیرفعال‌سازی':'فعال‌سازی'}" onclick="toggleAdmin('${a.id}', ${!a.active})"><i class="ti ti-power"></i></button>
        <button class="iconbtn danger" title="حذف ادمین" aria-label="حذف ادمین" onclick="deleteAdmin('${a.id}')"><i class="ti ti-trash" style="color:var(--bad)"></i></button>`;
      return `
      <div class="admin-card ${isOwner?'is-owner':''} ${a.active?'':'is-inactive'}">
        <div class="admin-card-top">
          <div class="admin-id">
            <div class="admin-avatar">${escapeHtml(initials)}</div>
            <div class="admin-meta">
              <div class="admin-name">${escapeHtml(a.username)}</div>
              <div class="admin-sub"><span class="admin-status-dot"></span>${a.active?'فعال':'غیرفعال'}</div>
            </div>
          </div>
          <span class="admin-role-badge ${isOwner?'owner':'admin'}"><i class="ti ti-${isOwner?'crown':'shield-check'}"></i>${isOwner?'مالک':'ادمین'}</span>
        </div>
        <div class="admin-perm-row">${chips}</div>
        <div class="admin-card-foot">
          <div class="admin-login-block"><span class="admin-login-label">آخرین فعالیت</span><span class="admin-login mono"><i class="ti ti-clock"></i> ${escapeHtml(lastLogin)}</span></div>
          <div class="row-actions"><span class="admin-actions-label">کنترل حساب</span>${actions}</div>
        </div>
      </div>`;
    }).join('');
  }catch(e){ toast(e.message, false); }
}
function openAdminDrawer(){
  openDrawer('ادمین جدید', `
    <div class="grp"><label>نام کاربری</label><input id="aUser"></div>
    <div class="grp"><label>رمز عبور</label><input type="password" id="aPass"></div>
    <div class="perm-grid">${Object.entries({dashboard:'داشبورد',inbounds:'ساخت و مدیریت اینباند',clients:'ساخت کلاینت (بخش جدا)',subscriptions:'سابسکریپشن',categories:'دسته‌بندی',plans:'پلن فروش',reports:'گزارش‌ها',messages:'پیام‌ها و خطاها',bot:'ربات',admins:'مدیریت حساب',settings:'تنظیمات'}).map(([k,v])=>`<label class="perm-item"><input type="checkbox" data-perm="${k}" ${['dashboard','inbounds','subscriptions'].includes(k)?'checked':''}>${v}</label>`).join('')}</div>
  `, `<button class="btn primary" style="flex:1" onclick="submitAdmin()"><i class="ti ti-device-floppy"></i>ساخت</button>`);
}
function editAdmin(id){
  const a = ADMIN_CACHE.find(x=>x.id===id); if(!a || a.role==='owner') return;
  const perms=['dashboard','inbounds','clients','subscriptions','categories','plans','reports','messages','bot','admins','settings'];
  const labels={dashboard:'داشبورد',inbounds:'اینباند و کلاینت',clients:'ساخت کلاینت (بخش جدا)',subscriptions:'سابسکریپشن',categories:'دسته‌بندی',plans:'پلن فروش',reports:'گزارش‌ها',messages:'پیام‌ها و خطاها',bot:'ربات',admins:'مدیریت حساب',settings:'تنظیمات'};
  openDrawer('ویرایش ادمین', `
    <div class="grp"><label>نام کاربری</label><input id="eUser" value="${escapeHtml(a.username||'')}"></div>
    <div class="grp"><label>رمز جدید <small>(اختیاری)</small></label><input type="password" id="ePass" placeholder="بدون تغییر خالی بگذار"></div>
    <div class="perm-grid">${perms.map(k=>`<label class="perm-item"><input type="checkbox" data-eperm="${k}" ${((a.permissions||[]).includes(k)?'checked':'')}>${labels[k]}</label>`).join('')}</div>
  `, `<button class="btn primary" style="flex:1" onclick="saveAdminEdit('${a.id}')"><i class="ti ti-device-floppy"></i>ذخیره تغییرات</button>`);
}
async function saveAdminEdit(id){
  try{ const permissions=[...document.querySelectorAll('[data-eperm]:checked')].map(x=>x.dataset.eperm); const body={username:$('eUser').value.trim(),permissions}; if($('ePass').value) body.password=$('ePass').value; await api(`/api/admins/${id}`,{method:'PATCH',body:JSON.stringify(body)}); toast('اطلاعات ادمین بروزرسانی شد ✓'); closeDrawer(); loadAdmins(); }catch(e){toast(e.message,false)}
}

async function submitAdmin(){
  try{ await api('/api/admins', {method:'POST', body: JSON.stringify({username:$('aUser').value, password:$('aPass').value, permissions:[...document.querySelectorAll('[data-perm]:checked')].map(x=>x.dataset.perm)})}); toast('ساخته شد'); closeDrawer(); loadAdmins(); }
  catch(e){ toast(e.message, false); }
}
async function toggleAdmin(id, active){
  try{ await api(`/api/admins/${id}`, {method:'PATCH', body:JSON.stringify({active})}); loadAdmins(); }
  catch(e){ toast(e.message, false); }
}
async function deleteAdmin(id){
  if(!confirm(t('این ادمین حذف شود؟'))) return;
  try{ await api(`/api/admins/${id}`, {method:'DELETE'}); toast('حذف شد'); loadAdmins(); }
  catch(e){ toast(e.message, false); }
}

// ============================================================
// Admin registration requests
// ============================================================
let ADMIN_REQ_CACHE = [];
async function loadAdminRequests(){
  try{
    const res = await api('/api/admin-requests');
    ADMIN_REQ_CACHE = res.requests || [];
    const card = $('adminReqCard');
    const pending = ADMIN_REQ_CACHE.filter(r=>r.status==='pending');
    $('adminReqBadge').textContent = pending.length + ' درخواست';
    if(!ADMIN_REQ_CACHE.length){ card.style.display='none'; return; }
    card.style.display = '';
    const rows = [...pending, ...ADMIN_REQ_CACHE.filter(r=>r.status!=='pending')].slice(0, 30);
    $('adminReqBody').innerHTML = rows.length ? rows.map(r=>{
      const date = r.created_at ? r.created_at.slice(0,16).replace('T',' ') : '';
      let statusHtml = '';
      let actions = '';
      if(r.status==='pending'){
        actions = `<button class="btn primary" style="padding:8px 12px;font-size:11px" onclick="approveAdminReq('${r.id}')"><i class="ti ti-check"></i>تایید و ساخت ادمین</button>
                   <button class="btn" style="padding:8px 12px;font-size:11px" onclick="rejectAdminReq('${r.id}')"><i class="ti ti-x"></i>رد</button>`;
      } else {
        statusHtml = `<span class="areq-status ${r.status}">${r.status==='approved'?'تایید شده':'رد شده'}</span>`;
      }
      return `<div class="areq-row">
        <div class="areq-info">
          <div class="areq-name">${escapeHtml(r.full_name||'-')}</div>
          <div class="areq-meta"><span><i class="ti ti-brand-telegram"></i>@${escapeHtml(r.telegram_id||'-')}</span><span><i class="ti ti-clock"></i>${escapeHtml(date)}</span></div>
          ${r.note ? `<div class="areq-note">${escapeHtml(r.note)}</div>` : ''}
        </div>
        <div class="areq-actions">${actions}${statusHtml}</div>
      </div>`;
    }).join('') : `<div class="areq-empty">درخواستی ثبت نشده است</div>`;
  }catch(e){ /* silent: پنل قدیمی‌تر ممکنه این endpoint رو نداشته باشه */ }
}
function approveAdminReq(id){
  const r = ADMIN_REQ_CACHE.find(x=>x.id===id); if(!r) return;
  const suggestedUser = (r.telegram_id||'admin').replace(/[^A-Za-z0-9_]/g,'').toLowerCase() || 'admin';
  openDrawer('تایید ادمین: ' + r.full_name, `
    <div class="grp"><label>درخواست‌کننده</label><input value="${escapeHtml(r.full_name)} (@${escapeHtml(r.telegram_id)})" disabled></div>
    <div class="grp"><label>نام کاربری</label><input id="arUser" value="${escapeHtml(suggestedUser)}"></div>
    <div class="grp"><label>رمز عبور</label><input id="arPass" value="${Math.random().toString(36).slice(-8)}"></div>
    <div class="grp"><label>شارژ اولیه (استارز)</label><input id="arCredit" type="number" min="0" value="0"></div>
    <div class="perm-grid">${Object.entries({dashboard:'داشبورد',inbounds:'ساخت و مدیریت اینباند',clients:'ساخت کلاینت (بخش جدا)',subscriptions:'سابسکریپشن',categories:'دسته‌بندی',plans:'پلن فروش',reports:'گزارش‌ها',messages:'پیام‌ها و خطاها',bot:'ربات',admins:'مدیریت حساب',settings:'تنظیمات'}).map(([k,v])=>`<label class="perm-item"><input type="checkbox" data-arperm="${k}" ${['dashboard','inbounds','subscriptions'].includes(k)?'checked':''}>${v}</label>`).join('')}</div>
  `, `<button class="btn primary" style="flex:1" onclick="confirmApproveAdminReq('${r.id}')"><i class="ti ti-check"></i>تایید و ساخت حساب</button>`);
}
async function confirmApproveAdminReq(id){
  try{
    const permissions=[...document.querySelectorAll('[data-arperm]:checked')].map(x=>x.dataset.arperm);
    const body={
      username: $('arUser').value.trim(),
      password: $('arPass').value,
      permissions,
      credit_stars: Number($('arCredit').value)||0,
    };
    const res = await api(`/api/admin-requests/${id}/approve`, {method:'POST', body: JSON.stringify(body)});
    closeDrawer();
    const msg = res.delivery_message || '';
    openDrawer('اطلاعات ورود ادمین', `
      <p style="font-size:11.5px;color:var(--sub);line-height:1.9">این متن را برای <b>@${escapeHtml(res.telegram_id||'')}</b> در تلگرام ارسال کن:</p>
      <textarea id="arDeliveryMsg" readonly style="width:100%;min-height:150px;background:var(--panel2);border:1px solid var(--line);color:var(--text);border-radius:12px;padding:12px;font:inherit;line-height:1.9">${escapeHtml(msg)}</textarea>
    `, `<button class="btn primary" style="flex:1" onclick="copyDeliveryMsg()"><i class="ti ti-copy"></i>کپی متن</button><button class="btn" style="flex:1" onclick="closeDrawer()">بستن</button>`);
    loadAdmins(); loadAdminRequests();
  }catch(e){ toast(e.message, false); }
}
function copyDeliveryMsg(){
  const el = document.getElementById('arDeliveryMsg');
  if(!el) return;
  el.select();
  try{ navigator.clipboard.writeText(el.value); toast('کپی شد ✓'); }catch(e){ document.execCommand('copy'); toast('کپی شد ✓'); }
}
async function rejectAdminReq(id){
  if(!confirm('این درخواست رد شود؟')) return;
  try{ await api(`/api/admin-requests/${id}/reject`, {method:'POST', body: JSON.stringify({})}); toast('درخواست رد شد'); loadAdminRequests(); }
  catch(e){ toast(e.message, false); }
}

// ============================================================
// ACTIVITY
// ============================================================
async function loadActivity(){
  try{
    const res = await api('/api/activity');
    $('activityBody').innerHTML = (res.logs||[]).slice().reverse().map(l=>`
      <tr><td class="mono">${(l.time||l.ts||'').toString().slice(0,16).replace('T',' ')}</td>
      <td><span class="badge ${l.level==='err'?'red':l.level==='warn'?'orange':'green'}">${l.type||l.kind||'—'}</span></td>
      <td>${escapeHtml(l.message||l.text||'')}</td></tr>
    `).join('') || `<tr><td colspan="3" class="empty">لاگی وجود ندارد</td></tr>`;
  }catch(e){ toast(e.message, false); }
}

// ============================================================
// MESSAGE CENTER
// ============================================================
function setMessageFilter(filter){
  MESSAGE_FILTER=filter;
  document.querySelectorAll('[data-message-filter]').forEach(b=>b.classList.toggle('on',b.dataset.messageFilter===filter));
  loadMessages();
}
function messageIcon(level, source){
  if(source==='client') return 'browser';
  if(level==='warn') return 'alert-triangle';
  if(level==='err') return 'alert-circle';
  return 'info-circle';
}
async function clearErrors(){
  if(!confirm(t('همه خطاهای ثبت‌شده پاک شوند؟'))) return;
  try{await api('/api/errors/clear',{method:'POST'});toast('خطاها پاک شدند ✓');loadMessages();}
  catch(e){toast(e.message,false);}
}
async function loadMessages(){
  try{
    const [er,act]=await Promise.all([api('/api/errors'),api('/api/activity')]);
    const errors=(er.errors||[]).slice().reverse();
    const filtered=errors.filter(x=>MESSAGE_FILTER==='all' || x.level===MESSAGE_FILTER || x.source===MESSAGE_FILTER);
    $('messageStats').innerHTML=`
      <div class="message-stat ${er.total_errors?'danger':'good'}"><div class="ms-icon"><i class="ti ti-alert-circle"></i></div><b>${Number(er.total_errors||0)}</b><small>کل خطاهای ثبت‌شده</small></div>
      <div class="message-stat warn"><div class="ms-icon"><i class="ti ti-alert-triangle"></i></div><b>${Number(er.warnings||0)}</b><small>هشدارهای اخیر</small></div>
      <div class="message-stat"><div class="ms-icon"><i class="ti ti-browser"></i></div><b>${Number(er.client_errors||0)}</b><small>خطاهای مرورگر</small></div>
      <div class="message-stat good"><div class="ms-icon"><i class="ti ti-heartbeat"></i></div><b>${er.healthy?'OK':'CHECK'}</b><small>وضعیت سیستم</small></div>`;
    $('nb-errors').textContent=String(Math.min(99,Number(er.total_errors||0)));
    $('nb-errors').style.display=Number(er.total_errors||0)?'inline-flex':'none';
    $('messageLastSync').textContent='آخرین بروزرسانی '+new Date().toLocaleTimeString('fa-IR',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
    $('messageList').innerHTML=filtered.length?filtered.map(x=>{
      const lvl=x.level||'err'; const src=x.source||'server';
      return `<article class="message-row ${lvl}"><div class="mi"><i class="ti ti-${messageIcon(lvl,src)}"></i></div><div class="mt"><b>${escapeHtml(x.error||x.message||'خطای نامشخص')}</b><p>${escapeHtml(src==='client'?'Frontend / Browser':(x.method||'SERVER')+' · '+(x.path||''))}</p>${x.stack||x.details?`<div class="error-detail">${escapeHtml(x.stack||x.details||'')}</div>`:''}</div><div class="meta"><strong>${escapeHtml(x.time||'—')}</strong><span>${escapeHtml(src)}</span></div></article>`;
    }).join(''):`<div class="message-empty"><i class="ti ti-shield-check"></i>خطای ثبت‌شده‌ای وجود ندارد. سیستم سالم است.</div>`;
    const logs=(act.logs||[]).slice().reverse().slice(0,25);
    $('messageActivityList').innerHTML=logs.length?logs.map(l=>`<article class="message-row ${l.level==='err'?'err':l.level==='warn'?'warn':'ok'}"><div class="mi"><i class="ti ti-${l.level==='err'?'alert-circle':l.level==='warn'?'alert-triangle':'circle-check'}"></i></div><div class="mt"><b>${escapeHtml(l.message||l.text||'')}</b><p>${escapeHtml(l.kind||l.type||'system')}</p></div><div class="meta"><strong>${escapeHtml((l.time||l.ts||'').toString().replace('T',' ').slice(0,19))}</strong></div></article>`).join(''):'<div class="message-empty">رویدادی وجود ندارد.</div>';
  }catch(e){toast(e.message,false);reportClientError(e.message,'messages',{stack:e.stack});}
}
if(messageTimer) clearInterval(messageTimer);
let messagesTimer=setInterval(()=>{if(!document.hidden && CURRENT_PAGE==='messages') loadMessages()},15000);

// ============================================================
// SETTINGS
// ============================================================
function setBotDot(running){
  $('botDot').className = 'status-dot ' + (running?'on':'off');
  $('botStatusText').textContent = running ? 'ربات در حال اجراست' : 'ربات خاموش است';
  $('botStartBtn').disabled = !!running;
  $('botStopBtn').disabled = !running;
}
async function loadSettings(){
  try{
    const s = await api('/api/settings');
    $('setBaseUrl').value = s.public_base_url || '';
    if($('adminUsername')) $('adminUsername').value = s.admin_username || '';
    $('setTcpHost').value = s.tcp_public_host || '';
    $('setTcpPort').value = s.tcp_public_port || '';
    $('tcpListenHint').textContent = `سرور TCP روی پورت داخلی ${s.tcp_listen_port} گوش می‌دهد — این را در Railway به همین پورت داخلی متصل کن، نه به PORT اصلی HTTP.`;
    $('setBotToken').value = s.bot_token || '';
    $('setBotAdmins').value = s.bot_admin_ids || '';
    setBotDot(s.bot_running);
    if($('subTplName')) $('subTplName').checked = s.sub_remark_show_name !== false;
    if($('subTplVolume')) $('subTplVolume').checked = !!s.sub_remark_show_volume;
    if($('subTplId')) $('subTplId').checked = !!s.sub_remark_show_id;
    if($('subTplInbound')) $('subTplInbound').checked = !!s.sub_remark_show_inbound;
    updateSubTemplatePreview();
    try{ const bt=await api('/api/bot/texts'); const x=bt.texts||{}; if($('botTxtWelcome'))$('botTxtWelcome').value=x.welcome||''; if($('botTxtAdmin'))$('botTxtAdmin').value=x.admin_menu||''; if($('botTxtCreated'))$('botTxtCreated').value=x.config_created||''; if($('botTxtStore'))$('botTxtStore').value=x.store_intro||''; if($('botTxtPayment'))$('botTxtPayment').value=x.payment_success||''; }catch(_){}
  }catch(e){ toast(e.message, false); }
}
function updateSubTemplatePreview(){
  const parts=[];
  if($('subTplName')?.checked) parts.push('MyConfig');
  if($('subTplVolume')?.checked) parts.push('50 GB');
  if($('subTplId')?.checked) parts.push('a1b2c3d4');
  if($('subTplInbound')?.checked) parts.push('Inbound-1');
  const el=$('subTplPreview'); if(el) el.textContent = parts.join(' | ') || 'MyConfig';
}
document.addEventListener('change', e=>{ if(['subTplName','subTplVolume','subTplId','subTplInbound'].includes(e.target?.id)) updateSubTemplatePreview(); });
async function saveSubTemplate(){
  try{
    await api('/api/settings', {method:'POST', body: JSON.stringify({
      sub_remark_show_name: !!$('subTplName')?.checked,
      sub_remark_show_volume: !!$('subTplVolume')?.checked,
      sub_remark_show_id: !!$('subTplId')?.checked,
      sub_remark_show_inbound: !!$('subTplInbound')?.checked,
    })});
    toast('الگوی نام کانفیگ‌های ساب ذخیره شد ✓');
  }catch(e){ toast(e.message, false); }
}
async function saveTcpSettings(){
  try{
    await api('/api/settings', {method:'POST', body: JSON.stringify({tcp_public_host: $('setTcpHost').value, tcp_public_port: $('setTcpPort').value})});
    toast('آدرس TCP ذخیره شد');
  }catch(e){ toast(e.message, false); }
}
async function saveBaseUrl(){
  try{ await api('/api/settings', {method:'POST', body: JSON.stringify({public_base_url: $('setBaseUrl').value})}); toast('آدرس ذخیره شد'); refreshOverview(); }
  catch(e){ toast(e.message, false); }
}
async function saveBotSettings(){
  try{
    const r = await api('/api/settings', {method:'POST', body: JSON.stringify({bot_token: $('setBotToken').value, bot_admin_ids: $('setBotAdmins').value})});
    toast(r.bot_restarted ? 'ذخیره شد و ربات با تنظیمات جدید ری‌استارت شد' : 'ذخیره شد — برای اعمال، ربات را روشن کنید');
    setBotDot(r.running);
  }catch(e){ toast(e.message, false); }
}
async function botStart(){
  try{ const r = await api('/api/settings/bot/start', {method:'POST'}); toast('ربات روشن شد'); setBotDot(r.running); }
  catch(e){ toast(e.message, false); }
}
async function botStop(){
  try{ const r = await api('/api/settings/bot/stop', {method:'POST'}); toast('ربات خاموش شد'); setBotDot(r.running); }
  catch(e){ toast(e.message, false); }
}
async function saveBotTexts(){
  try{ await api('/api/bot/texts',{method:'POST',body:JSON.stringify({texts:{welcome:$('botTxtWelcome').value,admin_menu:$('botTxtAdmin').value,config_created:$('botTxtCreated').value,store_intro:$('botTxtStore').value,payment_success:$('botTxtPayment').value}})}); toast('متن‌های ربات ذخیره شد ✓'); }catch(e){toast(e.message,false)}
}
function toggleSettingsPass(id, btn){
  const inp = $(id);
  if(!inp) return;
  const icon = btn ? btn.querySelector('i') : null;
  if(inp.type === 'password'){ inp.type = 'text'; if(icon) icon.className = 'ti ti-eye-off'; }
  else { inp.type = 'password'; if(icon) icon.className = 'ti ti-eye'; }
}
function passwordMeter(){
  const val = $('newPass') ? $('newPass').value : '';
  const bar = $('passMeterBar'), hint = $('passHint');
  if(!bar) return;
  let score = 0;
  if(val.length >= 8) score++;
  if(val.length >= 12) score++;
  if(/[a-z]/.test(val) && /[A-Z]/.test(val)) score++;
  if(/[0-9]/.test(val)) score++;
  if(/[^A-Za-z0-9]/.test(val)) score++;
  const levels = [
    {pct:4,  color:'var(--bad)',  label:'خیلی ضعیف'},
    {pct:25, color:'var(--bad)',  label:'ضعیف'},
    {pct:50, color:'var(--warn)', label:'متوسط'},
    {pct:75, color:'var(--warn)', label:'خوب'},
    {pct:100,color:'var(--good)', label:'قوی'},
    {pct:100,color:'var(--good)', label:'خیلی قوی'},
  ];
  const lv = levels[Math.min(score, levels.length-1)];
  bar.style.width = (val ? lv.pct : 0) + '%';
  bar.style.background = lv.color;
  if(hint) hint.textContent = val ? `قدرت رمز: ${lv.label} — حداقل ۸ کاراکتر، ترکیب حروف بزرگ/کوچک، عدد و نماد پیشنهاد می‌شود.` : 'حداقل ۸ کاراکتر، ترجیحاً ترکیب حروف، عدد و نماد.';
}
async function revokeOtherSessions(){
  if(!confirm(t('همه نشست‌های قبلی این حساب لغو شوند؟'))) return;
  try{const r=await api('/api/security/revoke-other-sessions',{method:'POST'});toast(`${r.revoked||0} نشست قبلی لغو شد ✓`)}catch(e){toast(e.message,false)}
}
function fmtDiagBytes(n){return fmtBytes(Number(n||0))}
async function loadDiagnostics(){
  const box=$('diagGrid'), st=$('diagStatus'); if(!box) return;
  st.textContent='CHECKING'; st.className='badge orange';
  try{
    const d=await api('/api/system/diagnostics'); const r=d.resources||{}, o=d.objects||{}, b=d.bot||{}, sec=d.security||{};
    box.innerHTML=`<div class="diag-item"><small>Service</small><b>${escapeHtml(d.service?.status||'—')}</b><span>${escapeHtml(d.uptime||'—')}</span></div><div class="diag-item"><small>CPU</small><b>${Number(r.cpu_percent||0).toFixed(1)}%</b><span>Process load</span></div><div class="diag-item"><small>Memory</small><b>${Number(r.memory_percent||0).toFixed(1)}%</b><span>${fmtDiagBytes(r.memory_rss)}</span></div><div class="diag-item"><small>Disk</small><b>${Number(r.disk_percent||0).toFixed(1)}%</b><span>Root filesystem</span></div><div class="diag-item"><small>Inbounds</small><b>${o.inbounds||0}</b><span>${o.active_links||0} active</span></div><div class="diag-item"><small>Clients</small><b>${o.clients||0}</b><span>${o.subscriptions||0} subscriptions</span></div><div class="diag-item"><small>Bot</small><b>${b.running?'ONLINE':'OFFLINE'}</b><span>${b.admin_count||0} bot admins</span></div><div class="diag-item"><small>Sessions</small><b>${sec.session_count||0}</b><span>${escapeHtml(sec.username||'—')}</span></div>`;
    st.textContent='HEALTHY'; st.className='badge green';
  }catch(e){box.innerHTML=`<div class="diag-empty">${escapeHtml(e.message||'Diagnostics unavailable')}</div>`;st.textContent='ERROR';st.className='badge red';}
}

async function changeUsername(){
  const username = ($('adminUsername')?.value || '').trim();
  if(!username){ toast('نام کاربری را وارد کنید', false); return; }
  if(username.length < 3 || username.length > 40 || /\s/.test(username)){ toast('نام کاربری باید ۳ تا ۴۰ کاراکتر و بدون فاصله باشد', false); return; }
  const btn = document.activeElement && document.activeElement.tagName === 'BUTTON' ? document.activeElement : null; const originalHtml = btn ? btn.innerHTML : '';
  if(btn){ btn.disabled=true; btn.innerHTML='<i class="ti ti-loader-2 spin"></i>در حال ذخیره...'; }
  try{
    const r = await api('/api/change-username',{method:'POST',body:JSON.stringify({username})});
    if($('userName')) $('userName').textContent=r.username;
    if($('userChip')?.querySelector('.av')) $('userChip').querySelector('.av').textContent=(r.username||'?').slice(0,1).toUpperCase();
    toast('نام کاربری با موفقیت تغییر کرد ✓');
  }catch(e){ toast(e.message,false); }
  finally{ if(btn){btn.disabled=false;btn.innerHTML=originalHtml;} }
}
async function changePassword(){
  const current_password = $('curPass').value, new_password = $('newPass').value, repeat_password = $('repPass').value;
  if(!current_password || !new_password || !repeat_password){ toast('همه‌ی فیلدهای رمز عبور را پر کنید', false); return; }
  if(new_password.length < 8){ toast('رمز جدید باید حداقل ۸ کاراکتر باشد', false); return; }
  if(new_password !== repeat_password){ toast('تکرار رمز یکسان نیست', false); return; }
  if(new_password === current_password){ toast('رمز جدید باید با رمز فعلی متفاوت باشد', false); return; }
  const btn = document.activeElement && document.activeElement.tagName === 'BUTTON' ? document.activeElement : null;
  const originalHtml = btn ? btn.innerHTML : '';
  if(btn){ btn.disabled = true; btn.innerHTML = '<i class="ti ti-loader-2 spin"></i>در حال ذخیره...'; }
  try{
    await api('/api/change-password', {method:'POST', body: JSON.stringify({current_password, new_password, repeat_password})});
    toast('رمز عبور با موفقیت تغییر کرد ✓');
    $('curPass').value=$('newPass').value=$('repPass').value='';
    passwordMeter();
  }catch(e){ toast(e.message, false); }
  finally{ if(btn){ btn.disabled = false; btn.innerHTML = originalHtml; } }
}
</script>
</body>
</html>
"""
