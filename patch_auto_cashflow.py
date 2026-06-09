#!/usr/bin/env python3
"""
patch_auto_cashflow.py – Add "Catat ke Cashflow" checkbox to BTC DCA, Saham,
                         and Crypto buy forms, and update their submit functions.
"""

PATH = '/home/user/dashboard-investasi/index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ── A) BTC DCA form: add checkbox after submit button row ───────────────────
OLD_DCA_FORM = """      <div class="fg"><label>&nbsp;</label><button class="btn btn-gold btn-full" onclick="submitDca()"><i class="ti ti-plus"></i> Catat</button></div>
    </div>
    <div id="dca-toast" class="toast"></div>"""
NEW_DCA_FORM = """      <div class="fg"><label>&nbsp;</label><button class="btn btn-gold btn-full" onclick="submitDca()"><i class="ti ti-plus"></i> Catat</button></div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
      <input type="checkbox" id="dca-cf" checked style="width:16px;height:16px;accent-color:var(--gold);cursor:pointer"/>
      <label for="dca-cf" style="font-size:12px;color:var(--t2);cursor:pointer">Catat otomatis sebagai pengeluaran di Cashflow</label>
    </div>
    <div id="dca-toast" class="toast"></div>"""
assert OLD_DCA_FORM in content, "A) DCA form submit button anchor not found"
content = content.replace(OLD_DCA_FORM, NEW_DCA_FORM, 1)
print("A) BTC DCA form checkbox added")

# ── B) submitDca function body ───────────────────────────────────────────────
OLD_DCA_FN = """  const fd = fmtTgl(tgl);
  const tx = {id:'dca_'+Date.now(), tanggal:fd, beli, harga};
  STATE.btcDca.push(tx);
  document.getElementById('dca-tgl').value = today();
  document.getElementById('dca-beli').value='';
  document.getElementById('dca-harga').value='';
  renderPage('btcdca');
  const ok = await callSheet({action:'addBtcDca',tanggal:fd,beli,harga});
  showToast('dca-toast', ok.success?'✓ Tersimpan ke Sheets!':'⚠ Tersimpan lokal', ok.success?'ok':'warn');"""
NEW_DCA_FN = """  const fd = fmtTgl(tgl);
  const doCf = document.getElementById('dca-cf')?.checked !== false;
  const tx = {id:'dca_'+Date.now(), tanggal:fd, beli, harga};
  STATE.btcDca.push(tx);
  if(doCf){
    const d=new Date(tgl); const blnCf=BULAN_LIST[d.getMonth()]; const thnCf=String(d.getFullYear());
    const cfTx={id:'tx_'+Date.now(),tanggal:fd,tipe:'pengeluaran',deskripsi:'BTC DCA '+beli/harga.toFixed(8)+' BTC',kategori:'Investasi',subkategori:'BTC DCA',nominal:beli,akun:STATE.config.akun_default||getRekening()[0]||'',bulan:blnCf,tahun:thnCf,catatan:'auto-inv'};
    STATE.transactions.push(cfTx);
    callSheet({action:'addTransaction',...cfTx}).catch(()=>{});
  }
  document.getElementById('dca-tgl').value = today();
  document.getElementById('dca-beli').value='';
  document.getElementById('dca-harga').value='';
  renderPage('btcdca');
  const ok = await callSheet({action:'addBtcDca',tanggal:fd,beli,harga});
  showToast('dca-toast', ok.success?'✓ Tersimpan ke Sheets!'+(doCf?' · Cashflow dicatat':''):'⚠ Tersimpan lokal', ok.success?'ok':'warn');"""
assert OLD_DCA_FN in content, "B) submitDca function body not found"
content = content.replace(OLD_DCA_FN, NEW_DCA_FN, 1)
print("B) submitDca updated with cashflow recording")

# ── C) Saham form: add checkbox before submit button ────────────────────────
OLD_SH_FORM = """    <button class="btn btn-gold btn-full" onclick="submitSaham()" style="margin-bottom:8px"><i class="ti ti-plus"></i> Catat Pembelian</button>
    <div id="sh-toast" class="toast"></div>"""
NEW_SH_FORM = """    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
      <input type="checkbox" id="sh-cf" checked style="width:16px;height:16px;accent-color:var(--gold);cursor:pointer"/>
      <label for="sh-cf" style="font-size:12px;color:var(--t2);cursor:pointer">Catat otomatis sebagai pengeluaran di Cashflow</label>
    </div>
    <button class="btn btn-gold btn-full" onclick="submitSaham()" style="margin-bottom:8px"><i class="ti ti-plus"></i> Catat Pembelian</button>
    <div id="sh-toast" class="toast"></div>"""
assert OLD_SH_FORM in content, "C) Saham form submit button anchor not found"
content = content.replace(OLD_SH_FORM, NEW_SH_FORM, 1)
print("C) Saham form checkbox added")

# ── D) submitSaham function body ─────────────────────────────────────────────
OLD_SH_FN = """  const fd = fmtTgl(tgl);
  const modal = lot*100*harga;
  const inv = {id:'s'+Date.now(),tanggal:fd,kode,tipe:'Saham',lotQty:lot,hargaBeli:harga,modal,catatan:''};
  STATE.investasi.push(inv);
  renderPage('saham');
  const ok = await callSheet({action:'addInvestasi',tanggal:fd,kode,tipe:'Saham',lotQty:lot,hargaBeli:harga,modal,catatan:''});
  showToast('sh-toast',ok.success?'✓ Tersimpan ke Sheets!':'⚠ Tersimpan lokal',ok.success?'ok':'warn');"""
NEW_SH_FN = """  const fd = fmtTgl(tgl);
  const modal = lot*100*harga;
  const doCf = document.getElementById('sh-cf')?.checked !== false;
  const inv = {id:'s'+Date.now(),tanggal:fd,kode,tipe:'Saham',lotQty:lot,hargaBeli:harga,modal,catatan:''};
  STATE.investasi.push(inv);
  if(doCf){
    const d=new Date(tgl); const blnCf=BULAN_LIST[d.getMonth()]; const thnCf=String(d.getFullYear());
    const cfTx={id:'tx_'+Date.now(),tanggal:fd,tipe:'pengeluaran',deskripsi:'Beli Saham '+kode+' '+lot+' lot',kategori:'Investasi',subkategori:'Saham',nominal:modal,akun:STATE.config.akun_default||getRekening()[0]||'',bulan:blnCf,tahun:thnCf,catatan:'auto-inv'};
    STATE.transactions.push(cfTx);
    callSheet({action:'addTransaction',...cfTx}).catch(()=>{});
  }
  renderPage('saham');
  const ok = await callSheet({action:'addInvestasi',tanggal:fd,kode,tipe:'Saham',lotQty:lot,hargaBeli:harga,modal,catatan:''});
  showToast('sh-toast',ok.success?'✓ Tersimpan ke Sheets!'+(doCf?' · Cashflow dicatat':''):'⚠ Tersimpan lokal',ok.success?'ok':'warn');"""
assert OLD_SH_FN in content, "D) submitSaham function body not found"
content = content.replace(OLD_SH_FN, NEW_SH_FN, 1)
print("D) submitSaham updated with cashflow recording")

# ── E) Crypto form: add checkbox after submit button row ────────────────────
OLD_CRY_FORM = """      <div class="fg"><label>&nbsp;</label><button class="btn btn-gold btn-full" onclick="submitCrypto()"><i class="ti ti-plus"></i> Tambah</button></div>
    </div>
    <div id="cry-toast" class="toast"></div>"""
NEW_CRY_FORM = """      <div class="fg"><label>&nbsp;</label><button class="btn btn-gold btn-full" onclick="submitCrypto()"><i class="ti ti-plus"></i> Tambah</button></div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
      <input type="checkbox" id="cry-cf" checked style="width:16px;height:16px;accent-color:var(--gold);cursor:pointer"/>
      <label for="cry-cf" style="font-size:12px;color:var(--t2);cursor:pointer">Catat otomatis sebagai pengeluaran di Cashflow</label>
    </div>
    <div id="cry-toast" class="toast"></div>"""
assert OLD_CRY_FORM in content, "E) Crypto form submit button anchor not found"
content = content.replace(OLD_CRY_FORM, NEW_CRY_FORM, 1)
print("E) Crypto form checkbox added")

# ── F) submitCrypto function body ────────────────────────────────────────────
OLD_CRY_FN = """  const fd = fmtTgl(tgl);
  const inv = {id:'c'+Date.now(),tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:''};
  STATE.investasi.push(inv);
  renderPage('crypto');
  const ok = await callSheet({action:'addInvestasi',tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:''});
  showToast('cry-toast',ok.success?'✓ Tersimpan ke Sheets!':'⚠ Tersimpan lokal',ok.success?'ok':'warn');"""
NEW_CRY_FN = """  const fd = fmtTgl(tgl);
  const doCf = document.getElementById('cry-cf')?.checked !== false;
  const inv = {id:'c'+Date.now(),tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:''};
  STATE.investasi.push(inv);
  if(doCf){
    const d=new Date(tgl); const blnCf=BULAN_LIST[d.getMonth()]; const thnCf=String(d.getFullYear());
    const cfTx={id:'tx_'+Date.now(),tanggal:fd,tipe:'pengeluaran',deskripsi:'Beli Crypto '+kode+' '+qty,kategori:'Investasi',subkategori:'Crypto',nominal:modal,akun:STATE.config.akun_default||getRekening()[0]||'',bulan:blnCf,tahun:thnCf,catatan:'auto-inv'};
    STATE.transactions.push(cfTx);
    callSheet({action:'addTransaction',...cfTx}).catch(()=>{});
  }
  renderPage('crypto');
  const ok = await callSheet({action:'addInvestasi',tanggal:fd,kode,tipe:'Crypto',lotQty:qty,hargaBeli:harga,modal,catatan:''});
  showToast('cry-toast',ok.success?'✓ Tersimpan ke Sheets!'+(doCf?' · Cashflow dicatat':''):'⚠ Tersimpan lokal',ok.success?'ok':'warn');"""
assert OLD_CRY_FN in content, "F) submitCrypto function body not found"
content = content.replace(OLD_CRY_FN, NEW_CRY_FN, 1)
print("F) submitCrypto updated with cashflow recording")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. {original_len} → {len(content)} chars written to {PATH}")
