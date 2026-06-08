#!/usr/bin/env python3
"""Kewajiban page: remove Commitments, add Subscriptions system"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\n{repr(old[:120])}"
    return content.replace(old, new, 1)

# ── K1: Add subscriptions to STATE ───────────────────────────────────────────
content = apply('K1',
  "  transactions: [], budget: [], btcDca: [], investasi: [],\n  aset: [], goals: [], snapshots: [], config: {}, hargaCache: {},\n  commitments: [], liabilities: [], perkasa: null,",
  "  transactions: [], budget: [], btcDca: [], investasi: [],\n  aset: [], goals: [], snapshots: [], config: {}, hargaCache: {},\n  commitments: [], liabilities: [], subscriptions: [], perkasa: null,")

# ── K2: Load subscriptions in loadSheet ──────────────────────────────────────
content = apply('K2',
  "    if(d.perkasa)              STATE.perkasa = d.perkasa;",
  """    if(d.subscriptions?.length) STATE.subscriptions = d.subscriptions;
    if(d.perkasa)              STATE.perkasa = d.perkasa;""")

# ── K3: Rewrite pageKewajiban ─────────────────────────────────────────────────
content = apply('K3',
  """function pageKewajiban(){
  return `
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
    <div style="font-size:15px;font-weight:600;color:var(--t1)">📅 Upcoming Commitments</div>
    <div style="flex:1;height:1px;background:var(--border)"></div>
  </div>
  ${sectionCommitments()}

  <div style="display:flex;align-items:center;gap:10px;margin:28px 0 16px">
    <div style="font-size:15px;font-weight:600;color:var(--t1)">💳 Outstanding Debt</div>
    <div style="flex:1;height:1px;background:var(--border)"></div>
  </div>
  ${sectionUtang()}
  `;
}""",
  """function pageKewajiban(){
  return `
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
    <div style="font-size:15px;font-weight:600;color:var(--t1)">🔄 Subscriptions</div>
    <div style="flex:1;height:1px;background:var(--border)"></div>
  </div>
  ${sectionSubscriptions()}

  <div style="display:flex;align-items:center;gap:10px;margin:28px 0 16px">
    <div style="font-size:15px;font-weight:600;color:var(--t1)">💳 Outstanding Debt</div>
    <div style="flex:1;height:1px;background:var(--border)"></div>
  </div>
  ${sectionUtang()}
  `;
}""")

# ── K4: Replace sectionCommitments with sectionSubscriptions ─────────────────
content = apply('K4',
  """function sectionCommitments(){
  const {pending,total} = calcCommitments();
  const availableCash = calcAvailableCash();
  const cashAfter = availableCash - total;
  const sorted = [...STATE.commitments].sort((a,b)=>{
    const da=parseDueDate(a.dueDate), db=parseDueDate(b.dueDate);
    if(!da) return 1; if(!db) return -1; return da-db;
  });

  const kategoriOpts = ['Gaji Karyawan','Pajak','Maintenance','Cicilan','Vendor','Tagihan Rutin','Sewa','Lainnya'];

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Available Cash</div><div class="stat-val teal">${fRp(availableCash)}</div></div>
    <div class="stat rose"><div class="stat-lbl">Total Commitments</div><div class="stat-val rose">${fRp(total)}</div><div class="stat-hint">${pending.length} kewajiban pending</div></div>
    <div class="stat"><div class="stat-lbl">Estimasi Cash Setelah Bayar</div><div class="stat-val ${cashAfter>=0?'teal':'rose'}">${fRp(cashAfter)}</div></div>
    <div class="stat"><div class="stat-lbl">Status</div><div class="stat-val ${cashAfter>=0?'green':'rose'}" style="font-size:13px">${cashAfter>=0?'Aman':'Defisit'}</div></div>
  </div>

  <div class="card" style="margin-bottom:14px">
    <div class="card-title">Tambah Kewajiban</div>
    <div class="fgrid fgrid-4" style="margin-bottom:8px">
      <div class="fg"><label>Due Date</label><input type="date" id="cm-due" value="${today()}"/></div>
      <div class="fg"><label>Deskripsi</label><input type="text" id="cm-desk" placeholder="Gaji karyawan, pajak motor, dll"/></div>
      <div class="fg"><label>Nominal (Rp)</label><input type="number" id="cm-nom" placeholder="3000000"/></div>
      <div class="fg"><label>Kategori</label><select id="cm-kat">${kategoriOpts.map(k=>'<option>'+k+'</option>').join('')}</select></div>
    </div>
    <button class="btn btn-gold btn-full" onclick="submitCommitment()" style="margin-bottom:8px"><i class="ti ti-plus"></i> Tambah Kewajiban</button>
    <div id="cm-toast" class="toast"></div>
  </div>

  <div class="card">
    <div class="card-title">Daftar Kewajiban Mendatang</div>
    ${sorted.length===0
      ? '<div style="text-align:center;padding:32px;color:var(--t3)"><div style="font-size:24px;margin-bottom:8px">📅</div><div style="font-size:13px">Belum ada kewajiban tercatat.</div></div>'
      : '<div class="tbl-wrap"><div class="tbl-scroll"><table><thead><tr><th>Due Date</th><th>Sisa Hari</th><th>Deskripsi</th><th>Kategori</th><th style="text-align:right">Nominal</th><th>Status</th><th></th></tr></thead><tbody>'+
        sorted.map(c=>{
          const dleft = daysUntil(c.dueDate);
          const dueChip = dleft==null ? '<span class="chip neu" style="font-size:10px">—</span>'
            : dleft<0 ? '<span class="chip dn" style="font-size:10px">Telat '+Math.abs(dleft)+'h</span>'
            : dleft===0 ? '<span class="chip dn" style="font-size:10px">Hari ini</span>'
            : dleft<=7 ? '<span class="chip gold" style="font-size:10px">'+dleft+' hari</span>'
            : '<span class="chip neu" style="font-size:10px">'+dleft+' hari</span>';
          const isLunas = c.status==='lunas';
          const statusChip = isLunas ? '<span class="chip up" style="font-size:10px">Lunas</span>' : '<span class="chip gold" style="font-size:10px">Pending</span>';
          return '<tr style="'+(isLunas?'opacity:.5':'')+'"><td class="td-mono" style="white-space:nowrap">'+fmtTgl(c.dueDate)+'</td><td>'+dueChip+'</td><td style="font-weight:500">'+(c.deskripsi||'—')+'</td><td><span class="chip neu" style="font-size:10px">'+(c.kategori||'—')+'</span></td><td style="text-align:right;font-family:var(--mono);color:var(--rose)">'+fRp(c.nominal)+'</td><td>'+statusChip+'</td><td><div class="td-act"><button class="btn btn-ghost btn-xs" onclick="editCommitment(\''+c.id+'\')" title="Edit"><i class="ti ti-edit"></i></button><button class="btn btn-ghost btn-xs" onclick="toggleCommitment(\''+c.id+'\')" title="'+(isLunas?'Tandai pending':'Tandai lunas')+'"><i class="ti ti-'+(isLunas?'rotate':'check')+'"></i></button><button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteCommitment(\''+c.id+'\')"><i class="ti ti-trash"></i></button></div></td></tr>';
        }).join('')+
        '</tbody></table></div></div>'
    }
  </div>`;
}""",
  """function sectionSubscriptions(){
  const subs = (STATE.subscriptions||[]).sort((a,b)=>a.nama.localeCompare(b.nama));
  const activeSubs = subs.filter(s=>s.aktif!==false);
  const totalPerBulan = activeSubs.reduce((a,s)=>a+(s.nominal||0),0);
  const totalPerTahun = totalPerBulan * 12;
  const katOpts = ['Hiburan','Produktivitas','Cloud & Storage','Kesehatan','Berita & Edukasi','Bisnis','Lainnya'];

  const cards = subs.map(s=>{
    const nonaktif = s.aktif===false;
    const billingDay = s.billingDate||1;
    const now = new Date();
    const nextBill = new Date(now.getFullYear(), now.getMonth(), billingDay);
    if(nextBill <= now) nextBill.setMonth(nextBill.getMonth()+1);
    const dLeft = Math.round((nextBill-now)/(1000*60*60*24));
    const urgentChip = nonaktif
      ? '<span class="chip neu" style="font-size:10px">Nonaktif</span>'
      : dLeft<=3
        ? '<span class="chip dn" style="font-size:10px">'+dLeft+'h lagi</span>'
        : dLeft<=7
          ? '<span class="chip gold" style="font-size:10px">'+dLeft+'h lagi</span>'
          : '<span class="chip neu" style="font-size:10px">Tgl '+billingDay+' tiap bulan</span>';

    return `<div class="card" style="margin-bottom:10px;${nonaktif?'opacity:.55':''}">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px">
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px">
            <span style="font-size:14px;font-weight:600">${s.nama}</span>
            <span class="chip neu" style="font-size:10px">${s.kategori||'Lainnya'}</span>
            ${urgentChip}
          </div>
          ${s.keterangan?`<div style="font-size:11px;color:var(--t3)">${s.keterangan}</div>`:''}
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0">
          <div style="font-family:var(--mono);font-size:15px;font-weight:600;color:var(--rose)">${fRp(s.nominal)}<span style="font-size:10px;font-weight:400;color:var(--t3)">/bln</span></div>
          <div style="display:flex;gap:4px">
            ${!nonaktif?`<button class="btn btn-sm btn-teal" onclick="bayarSubscription('${s.id}')" title="Tandai bayar bulan ini → masuk Cashflow"><i class="ti ti-cash"></i> Bayar</button>`:''}
            <button class="btn btn-ghost btn-xs" onclick="editSubscription('${s.id}')" title="Edit"><i class="ti ti-edit"></i></button>
            <button class="btn btn-ghost btn-xs" onclick="toggleSubscription('${s.id}')" title="${nonaktif?'Aktifkan':'Nonaktifkan'}"><i class="ti ti-${nonaktif?'player-play':'pause'}"></i></button>
            <button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteSubscription('${s.id}')" title="Hapus"><i class="ti ti-trash"></i></button>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat rose"><div class="stat-lbl">Total per Bulan</div><div class="stat-val rose">${fRp(totalPerBulan)}</div><div class="stat-hint">${activeSubs.length} subscription aktif</div></div>
    <div class="stat"><div class="stat-lbl">Total per Tahun</div><div class="stat-val">${fRp(totalPerTahun)}</div></div>
    <div class="stat"><div class="stat-lbl">Semua Subscription</div><div class="stat-val">${subs.length}</div><div class="stat-hint">${subs.length-activeSubs.length} nonaktif</div></div>
  </div>

  <div class="info-note" style="margin-bottom:14px">
    <i class="ti ti-info-circle" style="font-size:13px;flex-shrink:0"></i>
    Klik <strong>Bayar</strong> untuk menandai pembayaran bulan ini — nominal otomatis tercatat sebagai pengeluaran di Cashflow. Tidak perlu input dua kali.
  </div>

  <div id="sub-toast" class="toast" style="margin-bottom:10px"></div>

  <div style="display:flex;justify-content:flex-end;margin-bottom:14px">
    <button class="btn btn-gold btn-sm" onclick="addSubscription()"><i class="ti ti-plus"></i> Tambah Subscription</button>
  </div>

  ${subs.length===0
    ? '<div class="card" style="text-align:center;padding:32px;color:var(--t3)"><div style="font-size:28px;margin-bottom:12px">🔄</div><div style="font-weight:600;margin-bottom:6px">Belum ada subscription</div><div style="font-size:12px">Tambahkan tagihan berulang seperti Netflix, Spotify, domain, hosting, dll</div></div>'
    : cards}
  `;
}

function addSubscription(){
  const katOpts = ['Hiburan','Produktivitas','Cloud & Storage','Kesehatan','Berita & Edukasi','Bisnis','Lainnya'];
  document.getElementById('modal-title').textContent = 'Tambah Subscription';
  document.getElementById('modal-body').innerHTML = `
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Nama Layanan</label><input type="text" id="sb-nama" placeholder="Netflix, Spotify, AWS..." autofocus/></div>
      <div class="fg"><label>Nominal / Bulan (Rp)</label><input type="number" id="sb-nom" placeholder="54000"/></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Tanggal Billing (1-31)</label><input type="number" id="sb-tgl" min="1" max="31" placeholder="1"/></div>
      <div class="fg"><label>Kategori</label><select id="sb-kat">${katOpts.map(k=>'<option>'+k+'</option>').join('')}</select></div>
    </div>
    <div class="fg" style="margin-bottom:14px"><label>Keterangan (opsional)</label><input type="text" id="sb-ket" placeholder="Plan Premium, shared 2 orang, dll"/></div>
    <button class="btn btn-gold btn-full" onclick="saveNewSubscription()"><i class="ti ti-plus"></i> Tambah</button>`;
  openModal();
}

async function saveNewSubscription(){
  const nama = document.getElementById('sb-nama')?.value.trim();
  const nom  = parseFloat(document.getElementById('sb-nom')?.value)||0;
  const tgl  = parseInt(document.getElementById('sb-tgl')?.value)||1;
  const kat  = document.getElementById('sb-kat')?.value||'Lainnya';
  const ket  = document.getElementById('sb-ket')?.value.trim()||'';
  if(!nama||!nom){ showToast('modal-toast','Isi nama dan nominal.','err'); return; }
  const s = {id:'sb_'+Date.now(), nama, nominal:nom, billingDate:Math.min(28,Math.max(1,tgl)), kategori:kat, keterangan:ket, aktif:true};
  STATE.subscriptions.push(s);
  closeModal();
  renderPage('kewajiban');
  const ok = await callSheet({action:'addSubscription',...s});
  showToast('sub-toast', ok.success?'✓ Tersimpan!':'⚠ Tersimpan lokal', ok.success?'ok':'warn');
}

function editSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id); if(!s) return;
  const katOpts = ['Hiburan','Produktivitas','Cloud & Storage','Kesehatan','Berita & Edukasi','Bisnis','Lainnya'];
  document.getElementById('modal-title').textContent = 'Edit — '+s.nama;
  document.getElementById('modal-body').innerHTML = `
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Nama Layanan</label><input type="text" id="sb-nama" value="${s.nama}"/></div>
      <div class="fg"><label>Nominal / Bulan (Rp)</label><input type="number" id="sb-nom" value="${s.nominal}"/></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Tanggal Billing</label><input type="number" id="sb-tgl" min="1" max="28" value="${s.billingDate||1}"/></div>
      <div class="fg"><label>Kategori</label><select id="sb-kat">${katOpts.map(k=>'<option'+(k===s.kategori?' selected':'')+'>'+k+'</option>').join('')}</select></div>
    </div>
    <div class="fg" style="margin-bottom:14px"><label>Keterangan</label><input type="text" id="sb-ket" value="${s.keterangan||''}"/></div>
    <button class="btn btn-gold btn-full" onclick="saveEditSubscription('${id}')">Simpan</button>`;
  openModal();
}

async function saveEditSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id); if(!s) return;
  s.nama       = document.getElementById('sb-nama')?.value.trim()||s.nama;
  s.nominal    = parseFloat(document.getElementById('sb-nom')?.value)||s.nominal;
  s.billingDate= Math.min(28,Math.max(1,parseInt(document.getElementById('sb-tgl')?.value)||1));
  s.kategori   = document.getElementById('sb-kat')?.value||s.kategori;
  s.keterangan = document.getElementById('sb-ket')?.value.trim()||'';
  closeModal();
  renderPage('kewajiban');
  const ok = await callSheet({action:'updateSubscription',...s});
  showToast('sub-toast', ok.success?'✓ Disimpan!':'⚠ Gagal simpan', ok.success?'ok':'err');
}

async function toggleSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id); if(!s) return;
  s.aktif = s.aktif===false ? true : false;
  renderPage('kewajiban');
  await callSheet({action:'updateSubscription',...s});
}

async function deleteSubscription(id){
  if(!confirm('Hapus subscription ini?')) return;
  STATE.subscriptions = STATE.subscriptions.filter(x=>x.id!==id);
  renderPage('kewajiban');
  await callSheet({action:'deleteSubscription', id});
}

async function bayarSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id); if(!s) return;
  const now   = new Date();
  const bln   = now.toLocaleString('id-ID',{month:'long'});
  const thn   = String(now.getFullYear());
  const tgl   = now.toISOString().split('T')[0];
  const tx = {
    id:'tx_'+Date.now(), tanggal:fmtTgl(tgl), tipe:'pengeluaran',
    deskripsi:'Subscription: '+s.nama, kategori:'Lifestyle',
    subkategori:s.kategori, nominal:s.nominal,
    akun: (STATE.config.akun_default||getRekening()[0]||''),
    bulan:bln, tahun:thn, catatan:'auto-sub'
  };
  STATE.transactions.push(tx);
  renderPage('kewajiban');
  const ok = await callSheet({action:'addTransaction',...tx});
  showToast('sub-toast', ok.success?'✓ Bayar '+fRp(s.nominal)+' → tercatat di Cashflow!':'⚠ Gagal simpan', ok.success?'ok':'err');
}""")

print("Subscription section created!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")
