#!/usr/bin/env python3
"""
patch_mobile_pwa.py – Add favicon/PWA meta tags, bottom nav CSS, modal mobile fix,
                      bottom nav HTML, and bottom nav JS to index.html.
"""

PATH = '/home/user/dashboard-investasi/index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── A) Add favicon + PWA meta tags after <title> ────────────────────────────
OLD_TITLE = '<title>Wealth Management</title>'
NEW_TITLE = r"""<title>Wealth Management</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23d4a84b'/%3E%3Ctext y='.9em' font-size='72' font-family='serif' font-weight='700' fill='%2308090b' x='50%25' text-anchor='middle' dominant-baseline='hanging'%3EW%3C/text%3E%3C/svg%3E"/>
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23d4a84b'/%3E%3Ctext y='.9em' font-size='72' font-family='serif' font-weight='700' fill='%2308090b' x='50%25' text-anchor='middle' dominant-baseline='hanging'%3EW%3C/text%3E%3C/svg%3E"/>
<meta name="theme-color" content="#08090b"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="apple-mobile-web-app-title" content="Wealth"/>
<link rel="manifest" href="manifest.json"/>"""
assert OLD_TITLE in content, "A) <title> not found"
content = content.replace(OLD_TITLE, NEW_TITLE, 1)
print("A) Favicon + PWA meta tags added")

# ── B) Add bottom nav CSS before @keyframes spin ────────────────────────────
SPIN_ANCHOR = '@keyframes spin'
assert SPIN_ANCHOR in content, "B) @keyframes spin not found"
idx_spin = content.index(SPIN_ANCHOR)

BOTTOM_NAV_CSS = r"""/* ── BOTTOM NAV (mobile) ── */
.bottom-nav{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--bg1);border-top:1px solid var(--border2);z-index:200;padding-bottom:env(safe-area-inset-bottom,0px)}
.bottom-nav-inner{display:flex;align-items:stretch;height:56px}
.bn-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;color:var(--t3);font-size:9px;font-weight:500;border:none;background:none;padding:6px 4px;transition:color .15s;-webkit-tap-highlight-color:transparent;text-transform:uppercase;letter-spacing:.04em}
.bn-item i{font-size:20px}
.bn-item.active{color:var(--gold)}
.bn-more-menu{display:none;position:fixed;bottom:64px;left:0;right:0;background:var(--bg2);border-top:1px solid var(--border2);z-index:199;padding:8px;grid-template-columns:repeat(3,1fr);gap:6px}
.bn-more-menu.open{display:grid}
.bn-more-item{display:flex;flex-direction:column;align-items:center;gap:4px;padding:12px 8px;border-radius:var(--r);cursor:pointer;color:var(--t2);font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.04em;border:none;background:none}
.bn-more-item i{font-size:20px}
.bn-more-item:active,.bn-more-item.active{background:var(--gold-bg);color:var(--gold)}
.bn-overlay{display:none;position:fixed;inset:0;z-index:198;background:rgba(0,0,0,.5)}
.bn-overlay.open{display:block}

/* safe-area padding */
.content{padding-bottom:calc(80px + env(safe-area-inset-bottom,0px))}

@media(max-width:768px){
  .bottom-nav{display:block}
  .content{padding-bottom:calc(72px + env(safe-area-inset-bottom,0px))}
}

"""

content = content[:idx_spin] + BOTTOM_NAV_CSS + content[idx_spin:]
print("B) Bottom nav CSS added")

# ── C) Add modal mobile fix CSS inside @media(max-width:480px) ──────────────
METRICS_ANCHOR = '  .metrics-grid{grid-template-columns:repeat(2,1fr)}'
assert METRICS_ANCHOR in content, "C) .metrics-grid rule not found"
idx_metrics = content.index(METRICS_ANCHOR) + len(METRICS_ANCHOR)

MODAL_FIX = """
  .modal{max-height:85vh;overflow-y:auto;margin:auto 12px}
  .overlay{align-items:flex-end;padding-bottom:0}"""

content = content[:idx_metrics] + MODAL_FIX + content[idx_metrics:]
print("C) Modal mobile fix CSS added")

# ── D) Add bottom nav HTML before <!-- ═══ MODAL ═══ --> ────────────────────
MODAL_COMMENT = '<!-- ═══ MODAL ═'
# Try with the exact comment as it may appear
assert MODAL_COMMENT in content, "D) MODAL comment not found"
idx_modal = content.index(MODAL_COMMENT)

BOTTOM_NAV_HTML = """<!-- ═══ BOTTOM NAV (mobile) ══════════════════════════ -->
<div class="bn-overlay" id="bn-overlay" onclick="closeBnMore()"></div>
<div class="bn-more-menu" id="bn-more-menu">
  <button class="bn-more-item" data-page="btcdca" onclick="bnGoto('btcdca')"><i class="ti ti-currency-bitcoin"></i>BTC DCA</button>
  <button class="bn-more-item" data-page="aset" onclick="bnGoto('aset')"><i class="ti ti-building-bank"></i>Aset</button>
  <button class="bn-more-item" data-page="bisnis" onclick="bnGoto('bisnis')"><i class="ti ti-building-store"></i>Bisnis</button>
  <button class="bn-more-item" data-page="kewajiban" onclick="bnGoto('kewajiban')"><i class="ti ti-checklist"></i>Kewajiban</button>
  <button class="bn-more-item" data-page="budget" onclick="bnGoto('budget')"><i class="ti ti-chart-pie"></i>Alokasi</button>
  <button class="bn-more-item" data-page="goals" onclick="bnGoto('goals')"><i class="ti ti-target"></i>Goals</button>
  <button class="bn-more-item" data-page="analisa" onclick="bnGoto('analisa')"><i class="ti ti-chart-bar"></i>Analisa</button>
  <button class="bn-more-item" data-page="settings" onclick="bnGoto('settings')"><i class="ti ti-settings"></i>Settings</button>
</div>
<nav class="bottom-nav" id="bottom-nav">
  <div class="bottom-nav-inner">
    <button class="bn-item active" data-page="overview" onclick="bnGoto('overview')"><i class="ti ti-layout-dashboard"></i>Home</button>
    <button class="bn-item" data-page="cashflow" onclick="bnGoto('cashflow')"><i class="ti ti-arrows-exchange"></i>Cashflow</button>
    <button class="bn-item" data-page="portfolio" onclick="bnGoto('portfolio')"><i class="ti ti-briefcase"></i>Portfolio</button>
    <button class="bn-item" data-page="saham" onclick="bnGoto('saham')"><i class="ti ti-chart-candle"></i>Saham</button>
    <button class="bn-item" id="bn-more-btn" onclick="toggleBnMore()"><i class="ti ti-dots"></i>Lainnya</button>
  </div>
</nav>

"""

content = content[:idx_modal] + BOTTOM_NAV_HTML + content[idx_modal:]
print("D) Bottom nav HTML added")

# ── E) Add bottom nav JS before function gotoPage( ──────────────────────────
GOTO_ANCHOR = 'function gotoPage('
assert GOTO_ANCHOR in content, "E) function gotoPage( not found"
idx_goto = content.index(GOTO_ANCHOR)

BOTTOM_NAV_JS = r"""// ── Bottom Nav ────────────────────────────────────────────
function bnGoto(page){
  closeBnMore();
  gotoPage(page);
  document.querySelectorAll('.bn-item').forEach(b=>b.classList.toggle('active', b.dataset.page===page));
  document.querySelectorAll('.bn-more-item').forEach(b=>b.classList.toggle('active', b.dataset.page===page));
}
function toggleBnMore(){
  const m=document.getElementById('bn-more-menu');
  const o=document.getElementById('bn-overlay');
  const isOpen=m.classList.contains('open');
  if(isOpen){closeBnMore();}else{m.classList.add('open');o.classList.add('open');}
}
function closeBnMore(){
  document.getElementById('bn-more-menu')?.classList.remove('open');
  document.getElementById('bn-overlay')?.classList.remove('open');
}

"""

content = content[:idx_goto] + BOTTOM_NAV_JS + content[idx_goto:]
print("E) Bottom nav JS added")

# ── E2) Update gotoPage to sync bottom nav active state ─────────────────────
OLD_NAV_SYNC = "  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));"
NEW_NAV_SYNC = """  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.querySelectorAll('.bn-item').forEach(b=>b.classList.toggle('active', b.dataset.page===page));
  document.querySelectorAll('.bn-more-item').forEach(b=>b.classList.toggle('active', b.dataset.page===page));"""
assert OLD_NAV_SYNC in content, "E2) nav-item forEach line not found in gotoPage"
content = content.replace(OLD_NAV_SYNC, NEW_NAV_SYNC, 1)
print("E2) gotoPage updated to sync bottom nav active state")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. {original_len} → {len(content)} chars written to {PATH}")
