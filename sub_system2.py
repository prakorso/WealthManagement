#!/usr/bin/env python3
"""Subscription system — replace Commitments with Subscriptions"""

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\n{repr(old[:120])}"
    return content.replace(old, new, 1)

# ── K1: Add subscriptions to STATE ───────────────────────────────────────────
content = apply('K1',
  "  commitments: [], liabilities: [], perkasa: null,",
  "  commitments: [], liabilities: [], subscriptions: [], perkasa: null,")

# ── K2: Load subscriptions in loadSheet ──────────────────────────────────────
content = apply('K2',
  "    if(d.liabilities?.length)  STATE.liabilities = d.liabilities;",
  "    if(d.liabilities?.length)  STATE.liabilities = d.liabilities;\n    if(d.subscriptions?.length) STATE.subscriptions = d.subscriptions;")

# ── K3+K4: Replace lines 1928-2059 (pageKewajiban + sectionCommitments + commitment actions)
# We do this by splitting on the known start/end markers at line level

MARKER_START = "function pageKewajiban(){\n"
MARKER_END   = "function pageBisnis(){\n"

assert MARKER_START in content, "MARKER_START not found"
assert MARKER_END in content, "MARKER_END not found"

idx_start = content.index(MARKER_START)
idx_end   = content.index(MARKER_END)

NEW_SECTION = r'''function pageKewajiban(){
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
}

function sectionSubscriptions(){
  const subs = STATE.subscriptions || [];
  const active = subs.filter(s=>s.aktif!==false);
  const totalMonthly = active.reduce((a,s)=>a+(s.nominal||0),0);
  const kategoriOpts = ['Streaming','SaaS','Fitness','Utilitas','Pendidikan','Cloud','Gaming','Lifestyle','Lainnya'];
  const todayDate = new Date();
  const todayTgl = todayDate.getDate();

  const cards = subs.length===0
    ? '<div style="text-align:center;padding:32px;color:var(--t3)"><div style="font-size:28px;margin-bottom:8px">🔄</div><div style="font-size:13px">Belum ada subscription. Tambah di atas.</div></div>'
    : subs.map(s=>{
        const isActive = s.aktif!==false;
        const daysLeft = s.billingDate ? (s.billingDate>=todayTgl ? s.billingDate-todayTgl : 30-(todayTgl-s.billingDate)) : null;
        const urgency = daysLeft!=null && daysLeft<=3;
        return `<div class="inv-card" style="${isActive?'':'opacity:.5'}">
  <div class="inv-hdr">
    <div>
      <div class="inv-name">${s.nama}</div>
      <div class="inv-sub">${s.kategori||'—'} ${s.billingDate?'· tgl '+s.billingDate:''}${s.keterangan?' · '+s.keterangan:''}</div>
    </div>
    <div class="inv-hdr-actions">
      <span class="chip ${isActive?'neu':'rose'}" style="font-size:10px">${isActive?'Aktif':'Nonaktif'}</span>
      ${urgency?'<span class="chip gold" style="font-size:10px">'+daysLeft+'h lagi</span>':''}
    </div>
  </div>
  <div class="metrics-grid" style="margin:10px 0">
    <div class="metric"><div class="metric-lbl">Nominal/Bulan</div><div class="metric-val rose">${fRp(s.nominal)}</div></div>
    <div class="metric"><div class="metric-lbl">Billing Tgl</div><div class="metric-val">${s.billingDate||'—'}</div></div>
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    ${isActive?`<button class="btn btn-sm btn-teal" onclick="bayarSubscription('${s.id}')"><i class="ti ti-check"></i> Bayar & Catat</button>`:''}
    <button class="btn btn-ghost btn-xs" onclick="editSubscription('${s.id}')"><i class="ti ti-edit"></i></button>
    <button class="btn btn-ghost btn-xs" onclick="toggleSubscription('${s.id}')" title="${isActive?'Nonaktifkan':'Aktifkan'}"><i class="ti ti-${isActive?'player-pause':'player-play'}"></i></button>
    <button class="btn btn-ghost btn-xs" style="color:var(--rose)" onclick="deleteSubscription('${s.id}')"><i class="ti ti-trash"></i></button>
  </div>
</div>`;
      }).join('');

  return `
  <div class="stat-grid" style="margin-bottom:16px">
    <div class="stat"><div class="stat-lbl">Total Subscriptions</div><div class="stat-val">${subs.length}</div><div class="stat-hint">${active.length} aktif</div></div>
    <div class="stat rose"><div class="stat-lbl">Total /Bulan</div><div class="stat-val rose">${fRp(totalMonthly)}</div></div>
    <div class="stat"><div class="stat-lbl">Total /Tahun</div><div class="stat-val">${fRp(totalMonthly*12)}</div></div>
  </div>

  <div class="card" style="margin-bottom:14px">
    <div class="card-title">Tambah Subscription</div>
    <div class="fgrid fgrid-4" style="margin-bottom:8px">
      <div class="fg"><label>Nama</label><input type="text" id="sb-nama" placeholder="Netflix, Spotify, dll"/></div>
      <div class="fg"><label>Nominal (Rp/bln)</label><input type="number" id="sb-nom" placeholder="79000"/></div>
      <div class="fg"><label>Billing Tgl</label><input type="number" id="sb-tgl" min="1" max="31" placeholder="1-31"/></div>
      <div class="fg"><label>Kategori</label><select id="sb-kat">${kategoriOpts.map(k=>'<option>'+k+'</option>').join('')}</select></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:8px">
      <div class="fg"><label>Keterangan (opsional)</label><input type="text" id="sb-ket" placeholder="plan, akun, dll"/></div>
    </div>
    <button class="btn btn-gold btn-full" onclick="addSubscription()"><i class="ti ti-plus"></i> Tambah Subscription</button>
    <div id="sb-toast" class="toast"></div>
  </div>

  <div class="card">
    <div class="card-title">Daftar Subscription</div>
    ${cards}
  </div>`;
}

async function addSubscription(){
  const nama = document.getElementById('sb-nama')?.value.trim();
  const nom  = parseFloat(document.getElementById('sb-nom')?.value)||0;
  const tgl2 = parseInt(document.getElementById('sb-tgl')?.value)||1;
  const kat  = document.getElementById('sb-kat')?.value;
  const ket  = document.getElementById('sb-ket')?.value.trim();
  if(!nama||!nom){ showToast('sb-toast','Nama dan nominal wajib diisi.','err'); return; }
  const s = {id:'sb_'+Date.now(), nama, nominal:nom, billingDate:tgl2, kategori:kat, keterangan:ket, aktif:true};
  STATE.subscriptions.push(s);
  renderPage('kewajiban');
  const ok = await callSheet({action:'addSubscription',...s});
  showToast('sb-toast', ok.success?'✓ Tersimpan ke Sheets!':'⚠ Tersimpan lokal', ok.success?'ok':'warn');
}

function editSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id);
  if(!s) return;
  const kategoriOpts = ['Streaming','SaaS','Fitness','Utilitas','Pendidikan','Cloud','Gaming','Lifestyle','Lainnya'];
  document.getElementById('modal-title').textContent='Edit Subscription';
  document.getElementById('modal-body').innerHTML=`
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Nama</label><input type="text" id="esb-nama" value="${s.nama||''}"/></div>
      <div class="fg"><label>Nominal (Rp/bln)</label><input type="number" id="esb-nom" value="${s.nominal||0}"/></div>
    </div>
    <div class="fgrid fgrid-2" style="margin-bottom:10px">
      <div class="fg"><label>Billing Tgl</label><input type="number" id="esb-tgl" min="1" max="31" value="${s.billingDate||1}"/></div>
      <div class="fg"><label>Kategori</label><select id="esb-kat">${kategoriOpts.map(k=>`<option${k===s.kategori?' selected':''}>${k}</option>`).join('')}</select></div>
    </div>
    <div class="fgrid fgrid-1" style="margin-bottom:14px">
      <div class="fg"><label>Keterangan</label><input type="text" id="esb-ket" value="${s.keterangan||''}"/></div>
    </div>
    <button class="btn btn-gold btn-full" onclick="saveEditSubscription('${id}')">Simpan</button>`;
  openModal();
}

async function saveEditSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id);
  if(!s) return;
  s.nama        = document.getElementById('esb-nama')?.value.trim() || s.nama;
  s.nominal     = parseFloat(document.getElementById('esb-nom')?.value)||s.nominal;
  s.billingDate = parseInt(document.getElementById('esb-tgl')?.value)||s.billingDate;
  s.kategori    = document.getElementById('esb-kat')?.value;
  s.keterangan  = document.getElementById('esb-ket')?.value.trim();
  closeModal(); renderPage('kewajiban');
  const ok = await callSheet({action:'updateSubscription',...s});
  showToast('sb-toast', ok.success?'✓ Tersimpan!':'⚠ Update lokal', ok.success?'ok':'warn');
}

async function toggleSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id);
  if(!s) return;
  s.aktif = !s.aktif;
  renderPage('kewajiban');
  await callSheet({action:'updateSubscription',...s});
}

async function deleteSubscription(id){
  if(!confirm('Hapus subscription ini?')) return;
  STATE.subscriptions = STATE.subscriptions.filter(x=>x.id!==id);
  renderPage('kewajiban');
  await callSheet({action:'deleteSubscription',id});
}

async function bayarSubscription(id){
  const s = STATE.subscriptions.find(x=>x.id===id);
  if(!s) return;
  const tgl = new Date();
  const bln = BULAN_LIST[tgl.getMonth()];
  const thn = String(tgl.getFullYear());
  const tglStr = String(tgl.getDate()).padStart(2,'0')+'/'+String(tgl.getMonth()+1).padStart(2,'0')+'/'+thn;
  const rekening = getRekening();
  const tx = {
    id:'tx_'+Date.now(), tanggal:tglStr, tipe:'pengeluaran',
    deskripsi:'Subscription: '+s.nama, kategori:'Lifestyle',
    subkategori:s.kategori, nominal:s.nominal,
    akun:(STATE.config.akun_default||rekening[0]||''),
    bulan:bln, tahun:thn, catatan:'auto-sub'
  };
  STATE.transactions.push(tx);
  const ok = await callSheet({action:'addTransaction',...tx});
  if(ok.success) alert('✓ Pembayaran '+fRp(s.nominal)+' untuk "'+s.nama+'" dicatat ke cashflow '+bln+' '+thn+'.');
  else alert('⚠ Dicatat lokal. Sync ke Sheets gagal.');
}

async function toggleCommitment(id){
  const c = STATE.commitments.find(x=>x.id===id);
  if(!c) return;
  c.status = c.status==='lunas'?'pending':'lunas';
  await callSheet({action:'updateCommitment',id,status:c.status});
}

async function deleteCommitment(id){
  if(!confirm('Hapus kewajiban ini?')) return;
  STATE.commitments = STATE.commitments.filter(x=>x.id!==id);
  await callSheet({action:'deleteCommitment',id});
}

'''

content = content[:idx_start] + NEW_SECTION + content[idx_end:]

print("All subscription patches applied!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")
