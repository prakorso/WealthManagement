#!/usr/bin/env python3
"""Mobile UI/UX fixes"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\n{repr(old[:120])}"
    return content.replace(old, new, 1)

# ── M1: Add mobile CSS classes ────────────────────────────────────────────────
content = apply('M1',
  "@media(max-width:480px){",
  """/* ── MOBILE HELPER CLASSES ── */
.scorecard-3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.port-2col{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cashflow-3{display:flex;gap:10px;flex-wrap:wrap}
.cashflow-3>div{flex:1;min-width:calc(33% - 8px)}
.chip-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.inv-hdr-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end;max-width:180px}

@media(max-width:480px){""")

# ── M2: Add responsive rules inside the 480px block ──────────────────────────
content = apply('M2',
  "  .nw-row{flex-wrap:wrap;gap:8px}",
  """  .nw-row{flex-wrap:wrap;gap:8px}
  .scorecard-3{grid-template-columns:1fr!important}
  .cashflow-3{flex-wrap:wrap}
  .cashflow-3>div{flex:1;min-width:calc(50% - 6px)}
  .port-2col{grid-template-columns:1fr!important}
  .inv-hdr-actions{max-width:100%;flex-direction:row;flex-wrap:wrap;gap:6px}
  .inv-hdr{flex-wrap:wrap;gap:6px}
  .metrics-grid{grid-template-columns:repeat(2,1fr)}""")

# ── M3: Monthly Scorecard — replace inline grid with class ───────────────────
content = apply('M3',
  '    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">',
  '    <div class="scorecard-3">')

# ── M4: Overview Cashflow mini-stats — add flex-wrap ─────────────────────────
content = apply('M4',
  '      <div style="display:flex;gap:10px;margin-bottom:12px">\n        <div style="flex:1;background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">\n          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Income</div>\n          <div style="font-family:var(--mono);font-size:13px;color:var(--green);font-weight:500">${fRp(cf.income)}</div>\n        </div>\n        <div style="flex:1;background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">\n          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Spending</div>\n          <div style="font-family:var(--mono);font-size:13px;color:var(--rose);font-weight:500">${fRp(cf.spend)}</div>\n        </div>\n        <div style="flex:1;background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">\n          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Saving</div>\n          <div style="font-family:var(--mono);font-size:13px;color:var(--teal);font-weight:500">${fRp(cf.saving)}</div>\n        </div>\n      </div>',
  """      <div class="cashflow-3" style="margin-bottom:12px">
        <div style="background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">
          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Income</div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--green);font-weight:500">${fRp(cf.income)}</div>
        </div>
        <div style="background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">
          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Spending</div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--rose);font-weight:500">${fRp(cf.spend)}</div>
        </div>
        <div style="background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center">
          <div style="font-size:10px;color:var(--t3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">Saving</div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--teal);font-weight:500">${fRp(cf.saving)}</div>
        </div>
      </div>""")

# ── M5: Portfolio page chart grid — add class ────────────────────────────────
content = apply('M5',
  '  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px" class="ov-grid">',
  '  <div class="port-2col" style="margin-bottom:14px">')

# ── M6: Saham page — Jual button in inv-hdr — use class ─────────────────────
content = apply('M6',
  '      <div style="display:flex;align-items:center;gap:8px">\n        <span class="chip ${chipClass(s.ret)}">${fPct(s.ret)}</span>\n        <button class="btn btn-sm btn-rose" onclick="openSellModal(\'${s.kode}\',\'Saham\',${s.lotQty},${s.avgBeli||0})"><i class="ti ti-trending-down"></i> Jual</button>\n      </div>',
  '      <div class="inv-hdr-actions">\n        <span class="chip ${chipClass(s.ret)}">${fPct(s.ret)}</span>\n        <button class="btn btn-sm btn-rose" onclick="openSellModal(\'${s.kode}\',\'Saham\',${s.lotQty},${s.avgBeli||0})"><i class="ti ti-trending-down"></i> Jual</button>\n      </div>')

# ── M7: Crypto Jual button in others.map — same fix ──────────────────────────
content = apply('M7',
  '        <div style="display:flex;align-items:center;gap:8px">\n          <span class="chip ${chipClass(ret)}">${fPct(ret)}</span>\n        </div>',
  '        <div class="inv-hdr-actions">\n          <span class="chip ${chipClass(ret)}">${fPct(ret)}</span>\n        </div>')

# ── M8: Cost basis chip row in pagePortfolio — add chip-row class ────────────
content = apply('M8',
  '          <div style="display:flex;gap:6px">\n            <span class="chip neu" style="font-size:10px">${buyTxs.length} lot entry</span>',
  '          <div class="chip-row">\n            <span class="chip neu" style="font-size:10px">${buyTxs.length} lot entry</span>')

# ── M9: stat-val font-size reduction for very long numbers on mobile ──────────
content = apply('M9',
  "  .stat-val{font-size:14px}",
  "  .stat-val{font-size:13px}\n  .stat-val.gold,.stat-val.teal,.stat-val.rose{font-size:12px}\n  .nw-amount{word-break:break-all}")

# ── M10: Sell modal estimate grid — wrap on mobile ───────────────────────────
content = apply('M10',
  '<div id="sell-est-inner" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px"></div>',
  '<div id="sell-est-inner" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;font-size:12px"></div>')

# ── M11: 768px breakpoint — add inv-hdr flex-wrap ────────────────────────────
content = apply('M11',
  "  .ov-grid{grid-template-columns:1fr}",
  "  .ov-grid{grid-template-columns:1fr}\n  .inv-hdr{flex-wrap:wrap;gap:8px}")

print("All mobile fixes applied!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")
