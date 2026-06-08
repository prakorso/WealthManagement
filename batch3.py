#!/usr/bin/env python3
"""Batch 3 — Portfolio Center Restructure"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\n{repr(old[:120])}"
    return content.replace(old, new, 1)

# ── B3-1: Add totalCombinedPnl to calcPortfolioSummary ───────────────────────
content = apply('B3-1',
  "  const totalRealized = port.reduce((s,p)=>s+(p.realizedPnl||0),0);\n  return {segments, totalModal, totalNilai, totalPnl, totalRet, totalRealized, byTipe:Object.values(byTipe)};",
  """  const totalRealized    = port.reduce((s,p)=>s+(p.realizedPnl||0),0);
  const totalCombinedPnl = totalPnl + totalRealized;
  const totalCombinedRet = totalModal>0 ? totalCombinedPnl/totalModal*100 : 0;
  return {segments, totalModal, totalNilai, totalPnl, totalRet, totalRealized, totalCombinedPnl, totalCombinedRet, byTipe:Object.values(byTipe)};""")

# ── B3-2: Enhance stat grid — add Combined P/L ───────────────────────────────
content = apply('B3-2',
  '    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div></div>\n  </div>',
  """    <div class="stat ${gls(P.totalCombinedPnl)}">
      <div class="stat-lbl">Total P/L (Combined)</div>
      <div class="stat-val ${gls(P.totalCombinedPnl)}">${fRp(P.totalCombinedPnl)}</div>
      <div class="stat-hint">Unrealized + Realized</div>
    </div>
    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div></div>
  </div>""")

# ── B3-3: Improve breakdown cards with Realized P/L ──────────────────────────
content = apply('B3-3',
  """  const breakdownRows = P.byTipe.map(b=>{
    const pnl = b.nilai-b.modal;
    const ret = b.modal>0?pnl/b.modal*100:0;
    const pctAlokasi = P.totalNilai>0?(b.nilai/P.totalNilai*100):0;
    return `<div class="inv-card">
      <div class="inv-hdr">
        <div><div class="inv-name"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${b.color};margin-right:6px"></span>${b.tipe}</div>
        <div class="inv-sub">${pctAlokasi.toFixed(1)}% dari portfolio</div></div>
        <span class="chip ${chipClass(ret)}">${fPct(ret)}</span>
      </div>
      <div class="metrics-grid">
        <div class="metric"><div class="metric-lbl">Modal</div><div class="metric-val">${fRp(b.modal)}</div></div>
        <div class="metric"><div class="metric-lbl">Nilai Saat Ini</div><div class="metric-val gold">${fRp(b.nilai)}</div></div>
        <div class="metric"><div class="metric-lbl">Gain/Loss</div><div class="metric-val ${gls(pnl)}">${fRp(pnl)}</div></div>
        <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(ret)}">${fPct(ret)}</div></div>
      </div>
    </div>`;
  }).join('');""",
  """  const portPositions = calcPortfolio();
  const breakdownRows = P.byTipe.map(b=>{
    const pnl = b.nilai-b.modal;
    const ret = b.modal>0?pnl/b.modal*100:0;
    const pctAlokasi = P.totalNilai>0?(b.nilai/P.totalNilai*100):0;
    const tipeKey = b.tipe==='Bitcoin'?'BTC':b.tipe;
    const realized = portPositions.filter(p=>{
      if(tipeKey==='BTC') return p.kode==='BTC';
      return p.tipe===tipeKey;
    }).reduce((s,p)=>s+(p.realizedPnl||0),0);
    return `<div class="inv-card">
      <div class="inv-hdr">
        <div><div class="inv-name"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${b.color};margin-right:6px"></span>${b.tipe}</div>
        <div class="inv-sub">${pctAlokasi.toFixed(1)}% dari portfolio</div></div>
        <span class="chip ${chipClass(ret)}">${fPct(ret)}</span>
      </div>
      <div class="metrics-grid">
        <div class="metric"><div class="metric-lbl">Modal Aktif</div><div class="metric-val">${fRp(b.modal)}</div></div>
        <div class="metric"><div class="metric-lbl">Nilai Saat Ini</div><div class="metric-val gold">${fRp(b.nilai)}</div></div>
        <div class="metric"><div class="metric-lbl">Unrealized P/L</div><div class="metric-val ${gls(pnl)}">${fRp(pnl)}</div></div>
        <div class="metric"><div class="metric-lbl">Realized P/L</div><div class="metric-val ${gls(realized)}">${fRp(realized)}</div></div>
        <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(ret)}">${fPct(ret)}</div></div>
      </div>
    </div>`;
  }).join('');""")

# ── B3-4: Add rebalancing panel + cost basis section after detail table ───────
content = apply('B3-4',
  '  <div class="info-note" style="margin-top:14px"><i class="ti ti-info-circle" style="font-size:13px;flex-shrink:0"></i> Portfolio adalah halaman ringkasan. Input transaksi dilakukan di tab BTC DCA, Crypto, Saham, atau Aset (untuk reksa dana/obligasi/emas).</div>',
  """  ${(()=>{
    // Rebalancing panel
    let allocPlan2;
    try{ allocPlan2=JSON.parse(STATE.config.alokasi_plan||'null'); }catch(e){ allocPlan2=null; }
    if(!allocPlan2||!allocPlan2.length) return '';
    const nwVal = calcNetWorth().netWorth;
    if(nwVal<=0) return '';
    const rows = allocPlan2.map(p=>{
      const targetPct  = p.persen;
      const targetVal  = nwVal * targetPct / 100;
      // Find actual value from byTipe
      const match = P.byTipe.find(b=>b.tipe.toLowerCase().includes(p.kategori.toLowerCase())||p.kategori.toLowerCase().includes(b.tipe.toLowerCase()));
      const actualVal  = match ? match.nilai : 0;
      const actualPct  = nwVal>0 ? actualVal/nwVal*100 : 0;
      const gap        = targetVal - actualVal;
      const gapPct     = targetPct - actualPct;
      const barActual  = Math.min(100, actualPct/targetPct*100);
      return `<div style="margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
          <span style="font-size:12px;font-weight:500;display:flex;align-items:center;gap:6px">
            <span style="width:8px;height:8px;border-radius:2px;background:${p.warna||'var(--gold)'};display:inline-block"></span>
            ${p.kategori}
          </span>
          <span style="font-size:11px;font-family:var(--mono);color:var(--t2)">${actualPct.toFixed(1)}% / ${targetPct}%</span>
        </div>
        <div style="background:var(--bg3);border-radius:4px;height:8px;overflow:hidden;position:relative">
          <div style="height:100%;width:${barActual}%;background:${p.warna||'var(--gold)'};border-radius:4px;opacity:.85;transition:width .5s"></div>
          <div style="position:absolute;top:0;right:0;height:100%;width:2px;background:var(--border3)"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:10px;color:var(--t3)">
          <span>Aktual: ${fRp(actualVal)}</span>
          <span style="color:${gap>0?'var(--teal)':'var(--rose)'}">
            ${gap>0?'Tambah '+fRp(gap):'Lebih '+fRp(Math.abs(gap))}
          </span>
        </div>
      </div>`;
    }).join('');
    return `<div class="card" style="margin-top:14px">
      <div class="card-title">⚖️ Rebalancing Guide
        <button class="btn btn-ghost btn-xs" onclick="gotoPage('budget')" style="font-size:10px;color:var(--t3)">Atur plan →</button>
      </div>
      <div style="font-size:11px;color:var(--t3);margin-bottom:14px">Target alokasi dari Capital Allocation plan vs posisi aktual</div>
      ${rows}
    </div>`;
  })()}

  ${(()=>{
    // Cost basis per kode saham
    const sahamPort = calcPortfolio().filter(p=>p.tipe==='Saham'&&p.txs.length>0);
    if(!sahamPort.length) return '';
    const rows = sahamPort.map(s=>{
      const buyTxs = s.txs.filter(tx=>!isSellTx(tx)).sort((a,b)=>tglToISO(a.tanggal).localeCompare(tglToISO(b.tanggal)));
      const sellTxs = s.txs.filter(tx=>isSellTx(tx));
      if(!buyTxs.length) return '';
      const lotRows = buyTxs.map(tx=>{
        const lembar = (tx.lotQty||0)*100;
        const modal = tx.modal||(lembar*(tx.hargaBeli||0));
        const live = STATE.sahamLive[s.kode]||null;
        const cur = live?lembar*live:null;
        const pnl = cur!=null?cur-modal:null;
        return `<tr>
          <td class="td-mono">${tx.tanggal}</td>
          <td style="text-align:right">${tx.lotQty} lot</td>
          <td style="text-align:right;font-family:var(--mono)">${fRp(tx.hargaBeli)}</td>
          <td style="text-align:right;font-family:var(--mono)">${fRp(modal)}</td>
          <td style="text-align:right;font-family:var(--mono);color:${pnl==null?'var(--t3)':pnl>=0?'var(--green)':'var(--rose)'}">${pnl!=null?fRp(pnl):'—'}</td>
        </tr>`;
      }).join('');
      return `<div style="margin-bottom:10px">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
          <span style="font-size:12px;font-weight:700">${s.kode}</span>
          <div style="display:flex;gap:6px">
            <span class="chip neu" style="font-size:10px">${buyTxs.length} lot entry</span>
            ${sellTxs.length?`<span class="chip chip-rose" style="font-size:10px;background:var(--rose-bg);color:var(--rose)">${sellTxs.length} jual</span>`:''}
            <span style="font-size:11px;font-family:var(--mono);color:var(--t2)">Avg: ${fRp(s.avgBeli)}</span>
          </div>
        </div>
        <div class="tbl-wrap"><div class="tbl-scroll" style="max-height:200px">
          <table>
            <thead><tr><th>Tanggal</th><th style="text-align:right">Qty</th><th style="text-align:right">Harga Beli</th><th style="text-align:right">Modal</th><th style="text-align:right">P/L saat ini</th></tr></thead>
            <tbody>${lotRows}</tbody>
          </table>
        </div></div>
      </div>`;
    }).join('');
    if(!rows.trim()) return '';
    return `<div class="card" style="margin-top:14px">
      <div class="card-title">📋 Cost Basis History — Saham</div>
      <div style="font-size:11px;color:var(--t3);margin-bottom:14px">Rincian tiap lot pembelian dengan P/L berdasarkan harga live</div>
      ${rows}
    </div>`;
  })()}

  <div class="info-note" style="margin-top:14px"><i class="ti ti-info-circle" style="font-size:13px;flex-shrink:0"></i> Portfolio adalah halaman ringkasan. Input transaksi dilakukan di tab BTC DCA, Crypto, Saham, atau Aset (untuk reksa dana/obligasi/emas).</div>""")

print("All Batch 3 patches applied!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")
