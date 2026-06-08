#!/usr/bin/env python3
"""Apply all pending patches to index.html"""
import re, sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\nLooking for: {repr(old[:80])}"
    return content.replace(old, new, 1)

# ── P1: Add isSellTx / parseSellFee helpers ──────────────────────────────────
content = apply('P1',
'function calcPortfolio(){',
'''function isSellTx(inv){ return String(inv.catatan||'').startsWith('JUAL|'); }
function parseSellFee(inv){ const m=String(inv.catatan||'').match(/fee:(\\d+)/); return m?parseInt(m[1]):0; }

function calcPortfolio(){''')

# ── P2: Rewrite calcPortfolio body ────────────────────────────────────────────
content = apply('P2',
'''function calcPortfolio(){
  const byKode = {};
  STATE.investasi.forEach(inv=>{
    const k = inv.kode;
    if(!byKode[k]) byKode[k]={kode:k,tipe:inv.tipe,modal:0,lotQty:0,txs:[]};
    byKode[k].txs.push(inv);
    byKode[k].modal  += inv.modal||(inv.lotQty*100*inv.hargaBeli);
    byKode[k].lotQty += inv.lotQty;
  });
  return Object.values(byKode).map(p=>{
    let live = null;
    if(p.tipe==='Saham')  live = STATE.sahamLive[p.kode]||null;
    if(p.tipe==='Crypto') live = p.kode==='BTC'?STATE.btcPrice:(STATE.sahamLive[p.kode]||null);
    const mul = p.tipe==='Saham'?p.lotQty*100:p.lotQty;
    const cur = live?mul*live:null;
    const pnl = cur!=null?cur-p.modal:null;
    const ret = pnl!=null&&p.modal>0?pnl/p.modal*100:null;
    const avgBeli = p.modal/mul;
    return {...p,live,cur,pnl,ret,avgBeli};
  });
}''',
'''function calcPortfolio(){
  const byKode={};
  STATE.investasi.forEach(inv=>{
    const k=inv.kode;
    if(!byKode[k]) byKode[k]={kode:k,tipe:inv.tipe,txs:[]};
    byKode[k].txs.push(inv);
  });
  return Object.values(byKode).map(p=>{
    const mul=p.tipe==='Saham'?100:1;
    const sorted=[...p.txs].sort((a,b)=>tglToISO(a.tanggal).localeCompare(tglToISO(b.tanggal)));
    let totalCost=0,totalQty=0,realizedPnl=0;
    sorted.forEach(tx=>{
      const qty=(tx.lotQty||0)*mul;
      if(!isSellTx(tx)){
        totalCost+=tx.modal||(qty*(tx.hargaBeli||0));
        totalQty+=qty;
      }else{
        const fee=parseSellFee(tx);
        const avgC=totalQty>0?totalCost/totalQty:0;
        const qs=Math.min(qty,totalQty);
        const proc=tx.modal||(qty*(tx.hargaBeli||0));
        realizedPnl+=proc-avgC*qs-fee;
        totalQty=Math.max(0,totalQty-qs);
        totalCost=totalQty*avgC;
      }
    });
    const modal=totalCost; const lotQty=totalQty/mul;
    let live=null;
    if(p.tipe==='Saham') live=STATE.sahamLive[p.kode]||null;
    if(p.tipe==='Crypto') live=p.kode==='BTC'?STATE.btcPrice:(STATE.sahamLive[p.kode]||null);
    const cur=live!=null?totalQty*live:null;
    const unrealizedPnl=cur!=null?cur-modal:null;
    const ret=unrealizedPnl!=null&&modal>0?unrealizedPnl/modal*100:null;
    const avgBeli=totalQty>0?totalCost/totalQty:0;
    return {...p,modal,lotQty,live,cur,pnl:unrealizedPnl,unrealizedPnl,realizedPnl,ret,avgBeli,totalQty};
  });
}''')

# ── P3: calcPortfolioSummary — add totalRealized ──────────────────────────────
content = apply('P3',
'  return {segments, totalModal, totalNilai, totalPnl, totalRet, byTipe:Object.values(byTipe)};',
'''  const totalRealized = port.reduce((s,p)=>s+(p.realizedPnl||0),0);
  return {segments, totalModal, totalNilai, totalPnl, totalRet, totalRealized, byTipe:Object.values(byTipe)};''')

# ── P4a: Portfolio page stat-grid — add Unrealized + Realized rows ────────────
content = apply('P4a',
'  <div class="stat-grid" style="margin-bottom:16px">\n    <div class="stat"><div class="stat-lbl">Total Invested Capital</div><div class="stat-val">${fRp(P.totalModal)}</div></div>\n    <div class="stat gold"><div class="stat-lbl">Current Portfolio Value</div><div class="stat-val gold">${fRp(P.totalNilai)}</div></div>\n    <div class="stat ${P.totalPnl>=0?\'\':\'\'}"><div class="stat-lbl">Total Gain/Loss</div><div class="stat-val ${gls(P.totalPnl)}">${fRp(P.totalPnl)}</div></div>\n    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div></div>\n  </div>',
'''  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Total Invested Capital</div><div class="stat-val">${fRp(P.totalModal)}</div></div>
    <div class="stat gold"><div class="stat-lbl">Current Portfolio Value</div><div class="stat-val gold">${fRp(P.totalNilai)}</div></div>
    <div class="stat ${P.totalPnl>=0?\'\':\'\'}"><div class="stat-lbl">Unrealized P/L</div><div class="stat-val ${gls(P.totalPnl)}">${fRp(P.totalPnl)}</div></div>
    <div class="stat ${(P.totalRealized||0)>=0?\'\':\'\'}"><div class="stat-lbl">Realized P/L</div><div class="stat-val ${gls(P.totalRealized||0)}">${fRp(P.totalRealized||0)}</div></div>
    <div class="stat"><div class="stat-lbl">Total Return</div><div class="stat-val ${gls(P.totalRet)}">${fPct(P.totalRet)}</div></div>
  </div>''')

# ── P5: pageSaham — rewrite using calcPortfolio, add Jual btn + edit cols ─────
content = apply('P5',
'''function pageSaham(){
  const sahamList = STATE.investasi.filter(i=>i.tipe===\'Saham\');
  const byKode={};
  sahamList.forEach(i=>{
    if(!byKode[i.kode]) byKode[i.kode]={kode:i.kode,modal:0,lot:0,txs:[]};
    byKode[i.kode].modal+=i.modal; byKode[i.kode].lot+=i.lotQty; byKode[i.kode].txs.push(i);
  });
  const positions=Object.values(byKode).map(s=>{
    const live=STATE.sahamLive[s.kode]||null;
    const lembar=s.lot*100;
    const avg=s.modal/lembar;
    const cur=live?lembar*live:null;
    const pnl=cur!=null?cur-s.modal:null;
    const ret=pnl!=null&&s.modal>0?pnl/s.modal*100:null;
    return {...s,live,lembar,avg,cur,pnl,ret};
  });

  const totalModal=positions.reduce((a,s)=>a+s.modal,0);
  const totalCur=positions.reduce((a,s)=>a+(s.cur||s.modal),0);
  const totalPnl=totalCur-totalModal;
  const totalRet=totalModal>0?totalPnl/totalModal*100:0;

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Total Modal Saham</div><div class="stat-val">${fRp(totalModal)}</div></div>
    <div class="stat ${totalPnl>=0?\'\':\'\'}"><div class="stat-lbl">Nilai Saat Ini</div><div class="stat-val ${gls(totalPnl)}">${fRp(totalCur)}</div></div>
    <div class="stat"><div class="stat-lbl">Floating P/L</div><div class="stat-val ${gls(totalPnl)}">${fRp(totalPnl)}</div></div>
    <div class="stat"><div class="stat-lbl">Return</div><div class="stat-val ${gls(totalRet)}">${fPct(totalRet)}</div></div>
  </div>

  <div class="section-lbl">Posisi Saham</div>
  ${positions.length===0?`<div class="card" style="text-align:center;padding:32px;color:var(--t3)">Belum ada posisi saham.</div>`
  :positions.map(s=>`
  <div class="inv-card">
    <div class="inv-hdr">
      <div>
        <div class="inv-name">${s.kode}</div>
        <div class="inv-sub">${s.lot} lot · ${s.lembar.toLocaleString(\'id-ID\')} lembar · Avg ${fRp(s.avg)}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <span class="chip ${chipClass(s.ret)}">${fPct(s.ret)}</span>
      </div>
    </div>
    <div class="metrics-grid">
      <div class="metric"><div class="metric-lbl">Harga saat ini</div><div class="metric-val gold">${s.live?fRp(s.live):\'—\'}</div><div style="font-size:9px;color:var(--t3);margin-top:3px">${s.live?\'Yahoo Finance\':\'Klik Update\'}</div></div>
      <div class="metric"><div class="metric-lbl">Modal</div><div class="metric-val">${fRp(s.modal)}</div></div>
      <div class="metric"><div class="metric-lbl">Nilai saat ini</div><div class="metric-val">${fRp(s.cur)}</div></div>
      <div class="metric"><div class="metric-lbl">Floating P/L</div><div class="metric-val ${gls(s.pnl)}">${fRp(s.pnl)}</div></div>
      <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(s.ret)}">${fPct(s.ret)}</div></div>
    </div>
  </div>`).join(\'\')}''',
'''function pageSaham(){
  const sahamList = STATE.investasi.filter(i=>i.tipe===\'Saham\');
  const allPort = calcPortfolio().filter(p=>p.tipe===\'Saham\');
  const positions = allPort.map(s=>{
    const lembar = s.totalQty;
    return {...s, lot:s.lotQty, lembar, avg:s.avgBeli};
  });
  const buyList = sahamList.filter(i=>!isSellTx(i));

  const totalModal=positions.reduce((a,s)=>a+s.modal,0);
  const totalCur=positions.reduce((a,s)=>a+(s.cur||s.modal),0);
  const totalPnl=totalCur-totalModal;
  const totalRet=totalModal>0?totalPnl/totalModal*100:0;
  const totalRealized=positions.reduce((a,s)=>a+(s.realizedPnl||0),0);

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Total Modal Aktif</div><div class="stat-val">${fRp(totalModal)}</div></div>
    <div class="stat ${totalPnl>=0?\'\':\'\'}"><div class="stat-lbl">Nilai Saat Ini</div><div class="stat-val ${gls(totalPnl)}">${fRp(totalCur)}</div></div>
    <div class="stat"><div class="stat-lbl">Unrealized P/L</div><div class="stat-val ${gls(totalPnl)}">${fRp(totalPnl)}</div></div>
    <div class="stat ${totalRealized>=0?\'\':\'\'}"><div class="stat-lbl">Realized P/L</div><div class="stat-val ${gls(totalRealized)}">${fRp(totalRealized)}</div></div>
    <div class="stat"><div class="stat-lbl">Return</div><div class="stat-val ${gls(totalRet)}">${fPct(totalRet)}</div></div>
  </div>

  <div class="section-lbl">Posisi Saham</div>
  ${positions.filter(s=>s.totalQty>0).length===0?`<div class="card" style="text-align:center;padding:32px;color:var(--t3)">Belum ada posisi saham aktif.</div>`
  :positions.filter(s=>s.totalQty>0).map(s=>`
  <div class="inv-card">
    <div class="inv-hdr">
      <div>
        <div class="inv-name">${s.kode}</div>
        <div class="inv-sub">${s.lotQty} lot · ${s.lembar.toLocaleString(\'id-ID\')} lembar · Avg ${fRp(s.avgBeli)}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <span class="chip ${chipClass(s.ret)}">${fPct(s.ret)}</span>
        <button class="btn btn-sm btn-rose" onclick="openSellModal(\'${s.kode}\',\'Saham\',${s.lotQty},${s.avgBeli||0})"><i class="ti ti-trending-down"></i> Jual</button>
      </div>
    </div>
    <div class="metrics-grid">
      <div class="metric"><div class="metric-lbl">Harga saat ini</div><div class="metric-val gold">${s.live?fRp(s.live):\'—\'}</div><div style="font-size:9px;color:var(--t3);margin-top:3px">${s.live?\'Yahoo Finance\':\'Klik Update\'}</div></div>
      <div class="metric"><div class="metric-lbl">Modal Aktif</div><div class="metric-val">${fRp(s.modal)}</div></div>
      <div class="metric"><div class="metric-lbl">Nilai saat ini</div><div class="metric-val">${fRp(s.cur)}</div></div>
      <div class="metric"><div class="metric-lbl">Unrealized P/L</div><div class="metric-val ${gls(s.pnl)}">${fRp(s.pnl)}</div></div>
      <div class="metric"><div class="metric-lbl">Realized P/L</div><div class="metric-val ${gls(s.realizedPnl||0)}">${fRp(s.realizedPnl||0)}</div></div>
      <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(s.ret)}">${fPct(s.ret)}</div></div>
    </div>
  </div>`).join(\'\')}''')

# ── P5b: pageSaham history table — add BELI/JUAL chip + edit button ───────────
content = apply('P5b',
'''        <thead><tr><th>Tanggal</th><th>Kode</th><th style="text-align:right">Lot</th><th style="text-align:right">Harga Beli</th><th style="text-align:right">Modal</th><th></th></tr></thead>
        <tbody>
          ${sahamList.map((s,i)=>`<tr>
            <td class="td-mono">${s.tanggal}</td>
            <td><strong>${s.kode}</strong></td>
            <td style="text-align:right">${s.lotQty}</td>
            <td style="text-align:right;font-family:var(--mono)">${fRp(s.hargaBeli)}</td>
            <td style="text-align:right;font-family:var(--mono)">${fRp(s.modal)}</td>
            <td><div class="td-act"><button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteSahamTx(${i})"><i class="ti ti-trash"></i></button></div></td>
          </tr>`).join(\'\')}''',
'''        <thead><tr><th>Tanggal</th><th>Kode</th><th>Tipe</th><th style="text-align:right">Lot/Qty</th><th style="text-align:right">Harga</th><th style="text-align:right">Nilai</th><th></th></tr></thead>
        <tbody>
          ${sahamList.map((s,i)=>{
            const isSell=isSellTx(s);
            const chipCls=isSell?\'chip chip-rose\':\'chip neu\';
            const chipTxt=isSell?\'JUAL\':\'BELI\';
            const nota=isSell?String(s.catatan||\'\').replace(/^JUAL\\|fee:\\d+\\|?/,\'\'):\'\';
            return `<tr>
            <td class="td-mono">${s.tanggal}</td>
            <td><strong>${s.kode}</strong>${nota?` <span style="font-size:9px;color:var(--t3)">${nota}</span>`:\'\'}</td>
            <td><span class="${chipCls}" style="font-size:10px">${chipTxt}</span></td>
            <td style="text-align:right">${s.lotQty}</td>
            <td style="text-align:right;font-family:var(--mono)">${fRp(s.hargaBeli)}</td>
            <td style="text-align:right;font-family:var(--mono)">${fRp(s.modal)}</td>
            <td><div class="td-act">
              ${!isSell?`<button class="btn btn-ghost btn-xs" onclick="editSahamTx(STATE.investasi.filter(x=>x.tipe===\'Saham\')[${i}],${i})"><i class="ti ti-edit"></i></button>`:\'\'}
              <button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteSahamTx(${i})"><i class="ti ti-trash"></i></button>
            </div></td>
          </tr>`;}).join(\'\')}''')

# ── P6a: pageCrypto others — rewrite to use calcPortfolio ─────────────────────
content = apply('P6a',
'''  // Other crypto
  const otherCrypto = STATE.investasi.filter(i=>i.tipe===\'Crypto\'&&i.kode!==\'BTC\');
  const byKode={};
  otherCrypto.forEach(i=>{
    if(!byKode[i.kode]) byKode[i.kode]={kode:i.kode,modal:0,qty:0,txs:[]};
    byKode[i.kode].modal+=i.modal; byKode[i.kode].qty+=i.lotQty; byKode[i.kode].txs.push(i);
  });
  const others=Object.values(byKode);''',
'''  // Other crypto — use calcPortfolio for avg cost basis
  const others=calcPortfolio().filter(p=>p.tipe===\'Crypto\'&&p.kode!==\'BTC\'&&p.totalQty>0);''')

print("All patches applied successfully!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars to index.html")
