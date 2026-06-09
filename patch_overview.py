#!/usr/bin/env python3
"""
patch_overview.py – Patch pageOverview() in index.html:
  A) Remove sparkline from hero card
  B) Replace dual FIRE progress bar with single target bar
  C) Slim stat grid to 4 cards
  D) Move Monthly Scorecard to right after stat grid (before Asset Allocation)
"""

PATH = '/home/user/dashboard-investasi/index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── A) Remove sparkline line from hero card ─────────────────────────────────
OLD_SPARK = "    ${sparkData.length>1?`<div style=\"margin-top:14px;opacity:.7\">${buildSparkline(sparkData)}</div>`:''}\n"
assert OLD_SPARK in content, "A) sparkline line not found"
content = content.replace(OLD_SPARK, '', 1)
print("A) Sparkline removed")

# ── B) Replace dual progress grid with single target bar ────────────────────
OLD_PROG = """    <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px" class="hero-prog-grid">
      <div>
        <div class="progress-lbl"><span>🎯 Target Rp1M</span><span style="color:var(--gold)">${pctTarget}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>
      </div>
      <div>
        <div class="progress-lbl"><span>🔥 FIRE Progress</span><span style="color:var(--teal)">${firePct.toFixed(1)}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${firePct}%;background:linear-gradient(90deg,var(--teal),#2dd4bf88)"></div></div>
      </div>
    </div>"""
NEW_PROG = """    <div style="margin-top:14px">
      <div class="progress-lbl"><span>🎯 Target Rp1M</span><span style="color:var(--gold)">${pctTarget}%</span></div>
      <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>
    </div>"""
assert OLD_PROG in content, "B) dual progress grid not found"
content = content.replace(OLD_PROG, NEW_PROG, 1)
print("B) FIRE progress bar replaced with single target bar")

# ── C) Slim stat grid to 4 cards ────────────────────────────────────────────
STAT_START = '  <div class="stat-grid" style="margin-bottom:16px">\n    <div class="stat gold">\n      <div class="stat-lbl">Net Worth</div>\n      <div class="stat-val gold">${fRp(nw.netWorth)}</div>\n      ${nwHint}\n    </div>'
assert STAT_START in content, "C) stat-grid start not found"
idx_start = content.index(STAT_START)

STAT_END_MARKER = "    ${fireTarget>0?`\n    <div class=\"stat teal\">\n      <div class=\"stat-lbl\">FIRE Progress</div>\n      <div class=\"stat-val teal\">${firePct.toFixed(1)}%</div>\n      <div class=\"stat-hint\">${yearsToFire===0?'🎉 FIRE achieved!':yearsToFire!=null?'~'+yearsToFire+' tahun lagi':'Set target di Settings'}</div>\n    </div>`:''}\n  </div>"
assert STAT_END_MARKER in content, "C) stat-grid end (FIRE conditional) not found"
idx_end = content.index(STAT_END_MARKER) + len(STAT_END_MARKER)

NEW_STAT_GRID = """  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat gold">
      <div class="stat-lbl">Net Worth</div>
      <div class="stat-val gold">${fRp(nw.netWorth)}</div>
      ${nwHint}
    </div>
    <div class="stat teal">
      <div class="stat-lbl">Available Cash</div>
      <div class="stat-val ${availableCash>=0?'teal':'rose'}">${fRp(availableCash)}</div>
      <div class="stat-hint">${getAllAccounts().filter(a=>!a.disabled).length} rekening aktif</div>
    </div>
    <div class="stat ${savingRate>=30?'teal':''}">
      <div class="stat-lbl">Savings Rate</div>
      <div class="stat-val ${savingRate>=30?'teal':savingRate>=20?'':'rose'}">${savingRate}%</div>
      <div class="stat-hint">${savingRate>=30?'Excellent 🔥':savingRate>=20?'Good 👍':'Perlu ditingkatkan'}</div>
    </div>
    <div class="stat">
      <div class="stat-lbl">Investasi</div>
      <div class="stat-val">${fRp(nw.totalInv)}</div>
      <div class="stat-hint">${totalInvPct.toFixed(0)}% dari NW</div>
    </div>
  </div>"""

content = content[:idx_start] + NEW_STAT_GRID + content[idx_end:]
print("C) Stat grid slimmed to 4 cards")

# ── D) Move Monthly Scorecard before Asset Allocation ───────────────────────
# Find the Asset Allocation card start
ALLOC_ANCHOR = '  <div class="card" style="margin-bottom:14px">\n    <div class="card-title" style="margin-bottom:4px">🍕 Asset Allocation</div>'
assert ALLOC_ANCHOR in content, "D) Asset Allocation card not found"
idx_alloc = content.index(ALLOC_ANCHOR)

# Find the Monthly Scorecard card start
SCORECARD_ANCHOR = '  <div class="card" style="margin-bottom:14px">\n    <div class="card-title">📊 Monthly Scorecard'
assert SCORECARD_ANCHOR in content, "D) Monthly Scorecard card not found"
idx_sc_start = content.index(SCORECARD_ANCHOR)

# Find the end of the Monthly Scorecard block (just before \n\n  ${commitHtml})
COMMIT_ANCHOR = '\n\n  ${commitHtml}'
assert COMMIT_ANCHOR in content, "D) commitHtml anchor not found"
idx_commit = content.index(COMMIT_ANCHOR)
# The scorecard block ends right before \n\n  ${commitHtml}
# We need to include up to and including the blank line before commitHtml
# Actually the scorecard ends just before that double-newline, so idx_sc_end = idx_commit
idx_sc_end = idx_commit

scorecard_block = content[idx_sc_start:idx_sc_end]

# Remove scorecard from its current location (plus the trailing \n if any)
# The scorecard is followed by \n\n  ${commitHtml}, so after removing scorecard block
# we leave the \n\n  ${commitHtml} in place
content_without_sc = content[:idx_sc_start] + content[idx_sc_end:]

# Recalculate idx_alloc after removal
assert ALLOC_ANCHOR in content_without_sc, "D) Asset Allocation not found after scorecard removal"
idx_alloc_new = content_without_sc.index(ALLOC_ANCHOR)

# Insert scorecard_block + \n\n before alloc
content = content_without_sc[:idx_alloc_new] + scorecard_block + '\n\n' + content_without_sc[idx_alloc_new:]
print("D) Monthly Scorecard moved before Asset Allocation")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. {original_len} → {len(content)} chars written to {PATH}")
