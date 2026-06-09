#!/usr/bin/env python3
"""
patch_overview.py — Changes to pageOverview() in index.html

A) Remove sparkline from hero card
B) Remove FIRE progress bar from hero card (replace dual grid with single target bar)
C) Slim stat grid to 4 cards
D) Move Monthly Scorecard to right after stat grid (before Asset Allocation)

Uses index-based approach for large block replacements (C, D)
and content.replace(old, new, 1) with assert for small ones (A, B).
"""

import sys

PATH = '/home/user/dashboard-investasi/index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── A) Remove sparkline line from hero card ──────────────────────────────────
# The line sits inside the nw-hero div, on its own line.
OLD_A = "\n    ${sparkData.length>1?`<div style=\"margin-top:14px;opacity:.7\">${buildSparkline(sparkData)}</div>`:''}"
if OLD_A in content:
    content = content.replace(OLD_A, '', 1)
    print('A) Sparkline line removed.')
else:
    print('A) Sparkline already absent — skipping.')

# ── B) Replace dual FIRE progress grid with single target bar ────────────────
OLD_B = ('    <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px" class="hero-prog-grid">\n'
         '      <div>\n'
         '        <div class="progress-lbl"><span>🎯 Target Rp1M</span><span style="color:var(--gold)">${pctTarget}%</span></div>\n'
         '        <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>\n'
         '      </div>\n'
         '      <div>\n'
         '        <div class="progress-lbl"><span>🔥 FIRE Progress</span><span style="color:var(--teal)">${firePct.toFixed(1)}%</span></div>\n'
         '        <div class="progress-bar"><div class="progress-fill" style="width:${firePct}%;background:linear-gradient(90deg,var(--teal),#2dd4bf88)"></div></div>\n'
         '      </div>\n'
         '    </div>')
NEW_B = ('    <div style="margin-top:14px">\n'
         '      <div class="progress-lbl"><span>🎯 Target Rp1M</span><span style="color:var(--gold)">${pctTarget}%</span></div>\n'
         '      <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>\n'
         '    </div>')
if OLD_B in content:
    content = content.replace(OLD_B, NEW_B, 1)
    print('B) Dual FIRE progress replaced with single target bar.')
else:
    # Check if new version already present
    if '    <div style="margin-top:14px">\n      <div class="progress-lbl"><span>🎯 Target Rp1M"' in content or \
       '    <div style="margin-top:14px">\n      <div class="progress-lbl">' in content:
        print('B) Single target bar already present — skipping.')
    else:
        print('B) WARNING: dual progress grid not found and new form not confirmed either.', file=sys.stderr)

# ── C) Slim stat grid to 4 cards ────────────────────────────────────────────
# Use index-based approach: find start anchor and end anchor, replace the whole block.
STAT_START = ('  <div class="stat-grid" style="margin-bottom:16px">\n'
              '    <div class="stat gold">\n'
              '      <div class="stat-lbl">Net Worth</div>\n'
              '      <div class="stat-val gold">${fRp(nw.netWorth)}</div>\n'
              '      ${nwHint}\n'
              '    </div>')

# The original end marker contains the FIRE conditional stat card
STAT_END_OLD = ("    ${fireTarget>0?`\n"
                "    <div class=\"stat teal\">\n"
                "      <div class=\"stat-lbl\">FIRE Progress</div>\n"
                "      <div class=\"stat-val teal\">${firePct.toFixed(1)}%</div>\n"
                "      <div class=\"stat-hint\">${yearsToFire===0?'🎉 FIRE achieved!':yearsToFire!=null?'~'+yearsToFire+' tahun lagi':'Set target di Settings'}</div>\n"
                "    </div>`:''}\n"
                "  </div>")

NEW_C = ('  <div class="stat-grid" style="margin-bottom:16px">\n'
         '    <div class="stat gold">\n'
         '      <div class="stat-lbl">Net Worth</div>\n'
         '      <div class="stat-val gold">${fRp(nw.netWorth)}</div>\n'
         '      ${nwHint}\n'
         '    </div>\n'
         '    <div class="stat teal">\n'
         '      <div class="stat-lbl">Available Cash</div>\n'
         '      <div class="stat-val ${availableCash>=0?\'teal\':\'rose\'}">${fRp(availableCash)}</div>\n'
         '      <div class="stat-hint">${getAllAccounts().filter(a=>!a.disabled).length} rekening aktif</div>\n'
         '    </div>\n'
         '    <div class="stat ${savingRate>=30?\'teal\':\'\'}">\n'
         '      <div class="stat-lbl">Savings Rate</div>\n'
         '      <div class="stat-val ${savingRate>=30?\'teal\':savingRate>=20?\'\':\\\'rose\'}">${savingRate}%</div>\n'
         '      <div class="stat-hint">${savingRate>=30?\'Excellent 🔥\':savingRate>=20?\'Good 👍\':\'Perlu ditingkatkan\'}</div>\n'
         '    </div>\n'
         '    <div class="stat">\n'
         '      <div class="stat-lbl">Investasi</div>\n'
         '      <div class="stat-val">${fRp(nw.totalInv)}</div>\n'
         '      <div class="stat-hint">${totalInvPct.toFixed(0)}% dari NW</div>\n'
         '    </div>\n'
         '  </div>')

# The NEW_C uses single-quotes inside template literals, so we write it verbatim
# instead of escaped — redefine cleanly:
NEW_C = """  <div class="stat-grid" style="margin-bottom:16px">
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

if STAT_START in content and STAT_END_OLD in content:
    idx_c_start = content.index(STAT_START)
    idx_c_end = content.index(STAT_END_OLD) + len(STAT_END_OLD)
    content = content[:idx_c_start] + NEW_C + content[idx_c_end:]
    print('C) Stat grid replaced with slim 4-card version.')
else:
    # Check if already the slim 4-card version (no FIRE conditional, has Available Cash)
    SLIM_CHECK = ('    <div class="stat teal">\n'
                  '      <div class="stat-lbl">Available Cash</div>')
    FIRE_CHECK = STAT_END_OLD[:60]
    if SLIM_CHECK in content and FIRE_CHECK not in content:
        print('C) Stat grid already slimmed — skipping.')
    else:
        print('C) WARNING: stat grid old pattern not found; manual check needed.', file=sys.stderr)

# ── D) Move Monthly Scorecard before Asset Allocation ────────────────────────
# Uses index-based find/splice.
ALLOC_ANCHOR = ('  <div class="card" style="margin-bottom:14px">\n'
                '    <div class="card-title" style="margin-bottom:4px">🍕 Asset Allocation</div>')
SCORECARD_ANCHOR = ('  <div class="card" style="margin-bottom:14px">\n'
                    '    <div class="card-title">📊 Monthly Scorecard')
COMMIT_ANCHOR = '\n\n  ${commitHtml}'

assert ALLOC_ANCHOR in content, 'D) Asset Allocation card anchor not found'
assert SCORECARD_ANCHOR in content, 'D) Monthly Scorecard card anchor not found'
assert COMMIT_ANCHOR in content, 'D) commitHtml anchor not found'

idx_sc_start = content.index(SCORECARD_ANCHOR)
idx_alloc = content.index(ALLOC_ANCHOR)

if idx_sc_start < idx_alloc:
    print('D) Monthly Scorecard already before Asset Allocation — skipping.')
else:
    # Scorecard is after alloc; move it before.
    # Scorecard block ends just before the \n\n  ${commitHtml} that follows it.
    idx_commit = content.index(COMMIT_ANCHOR, idx_sc_start)
    idx_sc_end = idx_commit  # block ends here; \n\n${commitHtml} stays

    scorecard_block = content[idx_sc_start:idx_sc_end]

    # Remove scorecard from old location.
    # It is preceded by a blank line (\n\n) that we also remove so we don't leave a gap.
    removal_start = idx_sc_start - 2  # back over the \n\n separator before scorecard
    assert content[removal_start:idx_sc_start] == '\n\n', \
        'D) Expected \\n\\n before scorecard block'
    content_without_sc = content[:removal_start] + content[idx_sc_end:]

    # Recalculate alloc position after removal
    assert ALLOC_ANCHOR in content_without_sc, 'D) Alloc anchor missing after scorecard removal'
    idx_alloc_new = content_without_sc.index(ALLOC_ANCHOR)

    # Insert: scorecard_block + \n\n + alloc_block...
    content = (content_without_sc[:idx_alloc_new]
               + scorecard_block
               + '\n\n'
               + content_without_sc[idx_alloc_new:])
    print('D) Monthly Scorecard moved before Asset Allocation.')

# ── Write back ────────────────────────────────────────────────────────────────
with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✓ patch_overview.py done. {original_len:,} → {len(content):,} chars written to {PATH}')

