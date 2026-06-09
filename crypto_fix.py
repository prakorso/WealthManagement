#!/usr/bin/env python3
"""Crypto & BTC DCA enhancements: avg cost basis, sell, edit, tx history"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── Locate pageCrypto start and end ──────────────────────────────────────────
START = "function pageCrypto(){\n"
END   = "// ─── SAHAM ────────────────────────────────────────────────────\n"
assert START in content, "pageCrypto start not found"
assert END in content, "pageCrypto end not found"
idx_s = content.index(START)
idx_e = content.index(END)

NEW_CRYPTO_PAGE = r'''function pageCrypto(){
  const btcDca = calcDCA();

  // All crypto positions via calcPortfolio (proper avg cost basis, includes BTC Spot)
  const positions = calcPortfolio().filter(p=>p.tipe==='Crypto');
  const btcPos    = positions.find(p=>p.kode==='BTC');
  const others    = positions.filter(p=>p.kode!=='BTC'&&p.totalQty>0);

  // Transaction list (global index for GAS rowIndex)
  const cryptoTxs = STATE.investasi
    .map((inv,gi)=>({...inv,_gi:gi}))
    .filter(x=>x.tipe==='Crypto');

  const totalModal    = positions.reduce((a,p)=>a+p.modal,0);
  const totalCur      = positions.reduce((a,p)=>a+(p.cur||p.modal),0);
  const totalPnl      = totalCur-totalModal;
  const totalRet      = totalModal>0?totalPnl/totalModal*100:0;
  const totalRealized = positions.reduce((a,p)=>a+(p.realizedPnl||0),0);

  function posCard(p){
    const jBtn = `<button class="btn btn-sm btn-rose" onclick="openSellModal('${p.kode}','Crypto',${p.totalQty},${p.avgBeli||0})"><i class="ti ti-trending-down"></i> Jual ${p.kode}</button>`;
    return `<div class="inv-card">
      <div class="inv-hdr">
        <div>
          <div class="inv-name">${p.kode} <span style="font-size:10px;background:var(--gold-bg);color:var(--gold);padding:2px 8px;border-radius:4px;font-weight:500">SPOT</span></div>
          <div class="inv-sub">${p.totalQty.toFixed(p.kode==='BTC'?8:6)} ${p.kode} · Avg ${fRp(p.avgBeli)}</div>
        </div>
        <div class="inv-hdr-actions">
          <span class="chip ${chipClass(p.ret)}">${fPct(p.ret)}</span>
          ${jBtn}
        </div>
      </div>
      <div class="metrics-grid">
        <div class="metric"><div class="metric-lbl">Harga saat ini</div><div class="metric-val gold">${p.live?fRp(p.live):'—'}</div></div>
        <div class="metric"><div class="metric-lbl">Modal Aktif</div><div class="metric-val">${fRp(p.modal)}</div></div>
        <div class="metric"><div class="metric-lbl">Nilai saat ini</div><div class="metric-val">${fRp(p.cur||p.modal)}</div></div>
        <div class="metric"><div class="metric-lbl">Unrealized P/L</div><div class="metric-val ${gls(p.pnl)}">${fRp(p.pnl)}</div></div>
        <div class="metric"><div class="metric-lbl">Realized P/L</div><div class="metric-val ${gls(p.realizedPnl||0)}">${fRp(p.realizedPnl||0)}</div></div>
        <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(p.ret)}">${fPct(p.ret)}</div></div>
      </div>
    </div>`;
  }

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat gold"><div class="stat-lbl">Harga BTC Live</div><div class="stat-val gold">${fRp(STATE.btcPrice)}</div><div class="stat-hint">CoinGecko</div></div>
    <div class="stat"><div class="stat-lbl">Total Modal Aktif</div><div class="stat-val">${fRp(totalModal)}</div></div>
    <div class="stat"><div class="stat-lbl">Unrealized P/L</div><div class="stat-val ${gls(totalPnl)}">${fRp(totalPnl)}</div></div>
    <div class="stat"><div class="stat-lbl">Realized P/L</div><div class="stat-val ${gls(totalRealized)}">${fRp(totalRealized)}</div></div>
    <div class="stat"><div class="stat-lbl">Return</div><div class="stat-val ${gls(totalRet)}">${fPct(totalRet)}</div></div>
  </div>

  <div class="section-lbl">BTC — Dollar Cost Averaging</div>
  <div class="inv-card" style="margin-bottom:10px">
    <div class="inv-hdr">
      <div>
        <div class="inv-name">Bitcoin DCA <span style="font-size:10px;background:var(--gold-bg);color:var(--gold);padding:2px 8px;border-radius:4px;font-weight:500">DCA</span></div>
        <div class="inv-sub">${STATE.btcDca.length}x pembelian · Total ${btcDca.qty.toFixed(8)} BTC · Avg ${fRp(btcDca.avg)}</div>
      </div>
      <div class="inv-hdr-actions">
        <span class="chip ${chipClass(btcDca.ret)}">${fPct(btcDca.ret)}</span>
        <button class="btn btn-sm btn-rose" onclick="openSellModal('BTC','Crypto',${btcDca.qty},${btcDca.avg||0})"><i class="ti ti-trending-down"></i> Jual BTC</button>
      </div>
    </div>
    <div class="metrics-grid">
      <div class="metric"><div class="metric-lbl">Harga BTC</div><div class="metric-val gold">${fRp(STATE.btcPrice)}</div></div>
      <div class="metric"><div class="metric-lbl">Total Investasi</div><div class="metric-val">${fRp(btcDca.inv)}</div></div>
      <div class="metric"><div class="metric-lbl">Nilai Saat Ini</div><div class="metric-val">${fRp(btcDca.cur)}</div></div>
      <div class="metric"><div class="metric-lbl">Floating P/L</div><div class="metric-val ${gls(btcDca.pnl)}">${fRp(btcDca.pnl)}</div></div>
      <div class="metric"><div class="metric-lbl">Return</div><div class="metric-val ${gls(btcDca.ret)}">${fPct(btcDca.ret)}</div></div>
    </div>
    <div style="margin-top:10px">
      <button class="btn btn-sm" onclick="gotoPage('btcdca')"><i class="ti ti-list"></i> Lihat Riwayat DCA</button>
    </div>
  </div>

  ${btcPos&&btcPos.totalQty>0?`
  <div class="section-lbl" style="margin-top:16px">BTC Spot</div>
  ${posCard(btcPos)}`:''}

  ${others.length>0?`
  <div class="section-lbl" style="margin-top:16px">Crypto Lainnya</div>
  ${others.map(p=>posCard(p)).join('')}`:''}

  <hr style="border:none;border-top:1px solid var(--border);margin:20px 0"/>
  <div class="card">
    <div class="card-title">Tambah Crypto</div>
    <div class="fgrid fgrid-4" style="margin-bottom:8px">
      <div class="fg"><label>Tanggal</label><input type="date" id="cry-tgl" value="${today()}"/></div>
      <div class="fg"><label>Kode</label><input type="text" id="cry-kode" placeholder="BTC / ETH / SOL" style="text-transform:uppercase"/></div>
      <div class="fg"><label>Qty</label><input type="number" id="cry-qty" placeholder="0.01" step="0.00000001"/></div>
      <div class="fg"><label>Harga beli / unit (Rp)</label><input type="number" id="cry-harga" placeholder="auto"/></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:8px">
      <div class="fg"><label>Modal total (Rp)</label><input type="number" id="cry-modal" placeholder="Auto dari qty × harga"/></div>
      <div class="fg"><label>&nbsp;</label><button class="btn btn-gold btn-full" onclick="submitCrypto()"><i class="ti ti-plus"></i> Tambah</button></div>
    </div>
    <div id="cry-toast" class="toast"></div>

    <hr style="border:none;border-top:1px solid var(--border);margin:16px 0"/>
    <div class="section-lbl">Riwayat Transaksi</div>
    <div class="tbl-wrap"><div class="tbl-scroll">
      <table>
        <thead><tr><th>Tanggal</th><th>Kode</th><th>Tipe</th><th style="text-align:right">Qty</th><th style="text-align:right">Harga</th><th style="text-align:right">Nilai</th><th></th></tr></thead>
        <tbody>
          ${cryptoTxs.length===0?'<tr><td colspan="7" style="text-align:center;color:var(--t3);padding:20px">Belum ada transaksi.</td></tr>'
          :cryptoTxs.map(tx=>{
            const isSell=isSellTx(tx);
            const nota=isSell?String(tx.catatan||'').replace(/^JUAL\|fee:\d+\|?/,''):'';
            return `<tr>
              <td class="td-mono">${tx.tanggal}</td>
              <td><strong>${tx.kode}</strong>${nota?` <span style="font-size:9px;color:var(--t3)">${nota}</span>`:''}</td>
              <td><span class="chip ${isSell?'chip-rose':'neu'}" style="font-size:10px">${isSell?'JUAL':'BELI'}</span></td>
              <td style="text-align:right;font-family:var(--mono)">${tx.lotQty}</td>
              <td style="text-align:right;font-family:var(--mono)">${fRp(tx.hargaBeli)}</td>
              <td style="text-align:right;font-family:var(--mono)">${fRp(tx.modal)}</td>
              <td><div class="td-act">
                ${!isSell?`<button class="btn btn-ghost btn-xs" onclick="editCryptoTx(${JSON.stringify({id:tx.id,tanggal:tx.tanggal,kode:tx.kode,lotQty:tx.lotQty,hargaBeli:tx.hargaBeli,catatan:tx.catatan||''}).replace(/"/g,'&quot;')},${tx._gi})"><i class="ti ti-edit"></i></button>`:''}
                <button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteCryptoTx(${tx._gi})"><i class="ti ti-trash"></i></button>
              </div></td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div></div>
  </div>`;
}

'''

content = content[:idx_s] + NEW_CRYPTO_PAGE + content[idx_e:]

# ── Add editCryptoTx + saveEditCryptoTx + deleteCryptoTx before submitCrypto ─
OLD_SUBMIT = "async function submitCrypto(){"
assert OLD_SUBMIT in content, "submitCrypto anchor not found"

NEW_FUNCS = r'''function editCryptoTx(inv, gi){
  document.getElementById('modal-title').textContent = 'Edit Crypto — '+inv.kode;
  document.getElementById('modal-body').innerHTML = `
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Tanggal</label><input type="date" id="ecry-tgl" value="${tglToISO(inv.tanggal)}"/></div>
      <div class="fg"><label>Kode</label><input type="text" id="ecry-kode" value="${inv.kode}" style="text-transform:uppercase"/></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Qty</label><input type="number" id="ecry-qty" value="${inv.lotQty}" step="0.00000001"/></div>
      <div class="fg"><label>Harga Beli / Unit (Rp)</label><input type="number" id="ecry-harga" value="${inv.hargaBeli}"/></div>
    </div>
    <div class="fg" style="margin-bottom:14px"><label>Catatan</label><input type="text" id="ecry-cat" value="${inv.catatan||''}"/></div>
    <button class="btn btn-gold btn-full" onclick="saveEditCryptoTx('${inv.id||''}',${gi})">Simpan Perubahan</button>`;
  openModal();
}

async function saveEditCryptoTx(id, gi){
  const tgl   = document.getElementById('ecry-tgl')?.value;
  const kode  = document.getElementById('ecry-kode')?.value.trim().toUpperCase();
  const qty   = parseFloat(document.getElementById('ecry-qty')?.value)||0;
  const harga = parseFloat(document.getElementById('ecry-harga')?.value)||0;
  const cat   = document.getElementById('ecry-cat')?.value||'';
  if(!tgl||!kode||!qty){ showToast('modal-toast','Lengkapi semua field.','err'); return; }
  const fd    = fmtTgl(tgl);
  const modal = qty*harga||0;
  const updated = {id,tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:cat};
  const ei = id ? STATE.investasi.findIndex(i=>i.id===id) : gi;
  if(ei>-1) STATE.investasi[ei]=updated; else STATE.investasi[gi]=updated;
  closeModal(); renderPage('crypto');
  const ok = await callSheet({action:'editInvestasi',rowIndex:gi,tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:cat});
  showToast('cry-toast', ok.success?'✓ Tersimpan!':'⚠ Update lokal saja', ok.success?'ok':'warn');
}

async function deleteCryptoTx(gi){
  if(!confirm('Hapus transaksi ini?')) return;
  STATE.investasi.splice(gi,1);
  renderPage('crypto');
  await callSheet({action:'deleteInvestasi',rowIndex:gi});
}

async function submitCrypto(){'''

content = content.replace(OLD_SUBMIT, NEW_FUNCS, 1)

print("All crypto patches applied!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")
