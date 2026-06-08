// ============================================================
//  FINTRACK — Personal Finance Dashboard
//  Google Apps Script Backend
//
//  Setup:
//  1. Ganti SHEET_ID dengan ID spreadsheet kamu
//  2. Run initSheets() untuk setup semua sheet
//  3. Run testKoneksi() untuk authorize
//  4. Run setupTrigger() untuk cron harian
//  5. Deploy → New deployment → Web app → Anyone → Deploy
// ============================================================

const SHEET_ID = '1ngaW3_lvUdCSrnDjTAeHahS88UDy6OcgLoe7snuVq34';

// ── Helpers ─────────────────────────────────────────────────
function SS() { return SpreadsheetApp.openById(SHEET_ID); }

function getSheet(ss, name, headers) {
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    if (headers && headers.length) sh.appendRow(headers);
  }
  return sh;
}

function out(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function parseNum(v) {
  if (typeof v === 'number') return v;
  return parseFloat(String(v).replace(/[^0-9.\-]/g, '')) || 0;
}

function todayStr() {
  return Utilities.formatDate(new Date(), 'Asia/Jakarta', 'yyyy-MM-dd');
}

// ════════════════════════════════════════════════════════════
//  SETUP — Jalankan ini pertama kali
// ════════════════════════════════════════════════════════════
function testKoneksi() {
  const ss = SS();
  Logger.log('✓ Terhubung ke: ' + ss.getName());
  Logger.log('Sheets: ' + ss.getSheets().map(s => s.getName()).join(', '));
}

function initSheets() {
  const ss = SS();
  getSheet(ss, 'Transactions', ['id','tanggal','tipe','deskripsi','kategori','subkategori','nominal','akun','bulan','tahun','catatan']);
  getSheet(ss, 'Budget',       ['bulan','tahun','kategori','tipe_kategori','alokasi']);
  getSheet(ss, 'BTC_DCA',      ['tanggal','beli','harga_btc']);
  getSheet(ss, 'Investasi',    ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']);
  getSheet(ss, 'Aset',         ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']);
  getSheet(ss, 'Goals',        ['tipe','no','goal','info','kategori','deadline','done']);
  getSheet(ss, 'Snapshot',     ['date','net_worth','total_aset','total_investasi','total_tabungan','total_hutang']);
  getSheet(ss, 'Harga_Cache',  ['kode','harga','updated']);
  getSheet(ss, 'Cash_Accounts',['nama','tipe','saldo_manual','override','urutan','aktif']);
  getSheet(ss, 'Commitments',  ['id','due_date','deskripsi','nominal','kategori','status']);
  getSheet(ss, 'Subscriptions',['id','nama','nominal','billing_date','kategori','keterangan','aktif']);
  getSheet(ss, 'Liabilities',  ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']);
  getSheet(ss, 'Config',       ['key','value']);

  // Seed default cash accounts kalau masih kosong
  const ca = ss.getSheetByName('Cash_Accounts');
  if (ca.getLastRow() <= 1) {
    [['BCA','Bank',0,false,1,true],
     ['Jago','Bank',0,false,2,true],
     ['Dana','E-Wallet',0,false,3,true],
     ['Cash','Tunai',0,false,4,true]
    ].forEach(r => ca.appendRow(r));
  }

  const cfg = ss.getSheetByName('Config');
  const existing = cfg.getDataRange().getValues().map(r => String(r[0]));
  const defaults = [
    ['password',  'fintrack2024'],
    ['target_nw', '1000000000'],
    ['gaji_tanggal', '26'],
    ['rekening',  'BCA,Mandiri,Blu BCA,Pegadaian,Poems'],
    ['kategori_needs',  'Uang Ibu,Kebutuhan Rumah,Service,Infaq/Shodaqoh,BPJS,Beras,Wifi,Transportasi,Kesehatan,Lainnya'],
    ['kategori_wants',  'Entertainment,Travel,Makan Luar,Shopping,Subscriptions,Hobi'],
    ['kategori_savings','Tabungan,Investasi,Darurat,Bitcoin,Emas,Saham'],
    ['kategori_income', 'Gaji,Freelance,RevoU,Bonus,Side Income,Lainnya'],
    ['alloc_living',  '30'],
    ['alloc_investment','40'],
    ['alloc_business','20'],
    ['alloc_reserve', '10'],
  ];
  defaults.forEach(([k, v]) => {
    if (!existing.includes(k)) cfg.appendRow([k, v]);
  });

  Logger.log('✓ initSheets selesai');
}

function setupTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'dailySnapshot') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('dailySnapshot')
    .timeBased()
    .inTimezone('Asia/Jakarta')
    .everyDays(1)
    .atHour(18)
    .create();
  Logger.log('✓ Trigger terpasang: dailySnapshot jam 18:00 WIB');
}

// ════════════════════════════════════════════════════════════
//  PRICE FETCHERS
// ════════════════════════════════════════════════════════════
function fetchBTC() {
  let usdIdr = 16500;
  try {
    const r = UrlFetchApp.fetch('https://open.er-api.com/v6/latest/USD', {muteHttpExceptions:true});
    if (r.getResponseCode() === 200)
      usdIdr = JSON.parse(r.getContentText()).rates?.IDR || 16500;
  } catch(e) {}
  try {
    const r = UrlFetchApp.fetch('https://api.kraken.com/0/public/Ticker?pair=XBTUSD', {muteHttpExceptions:true});
    if (r.getResponseCode() === 200) {
      const btcUsd = parseFloat(JSON.parse(r.getContentText()).result?.XXBTZUSD?.c?.[0]) || 0;
      if (btcUsd > 0) {
        const price = Math.round(btcUsd * usdIdr);
        Logger.log('BTC/USD: ' + btcUsd + ' × ' + usdIdr + ' = Rp' + price);
        return price;
      }
    }
  } catch(e) { Logger.log('Kraken error: ' + e.message); }
  return 0;
}

function fetchSaham(kode) {
  const urls = [
    'https://query1.finance.yahoo.com/v8/finance/chart/' + kode + '.JK?interval=1d&range=5d',
    'https://query2.finance.yahoo.com/v8/finance/chart/' + kode + '.JK?interval=1d&range=5d'
  ];
  for (const url of urls) {
    try {
      const r = UrlFetchApp.fetch(url, {muteHttpExceptions:true, headers:{'User-Agent':'Mozilla/5.0'}});
      if (r.getResponseCode() !== 200) continue;
      const res = JSON.parse(r.getContentText())?.chart?.result?.[0];
      if (!res) continue;
      let price = res.meta?.regularMarketPrice;
      if (!price || price <= 0) {
        const closes = (res?.indicators?.quote?.[0]?.close || []).filter(v => v != null && v > 0);
        if (closes.length) price = closes[closes.length - 1];
      }
      if (price > 0) { Logger.log(kode + ': ' + price); return price; }
    } catch(e) {}
  }
  return 0;
}

function updateCache(ss, kode, harga) {
  const sh = getSheet(ss, 'Harga_Cache', ['kode','harga','updated']);
  const vals = sh.getDataRange().getValues();
  const t = todayStr();
  for (let i = 1; i < vals.length; i++) {
    if (String(vals[i][0]).toUpperCase() === kode.toUpperCase()) {
      sh.getRange(i+1, 2).setValue(harga);
      sh.getRange(i+1, 3).setValue(t);
      return;
    }
  }
  sh.appendRow([kode, harga, t]);
}

function getCached(ss, kode) {
  const sh = getSheet(ss, 'Harga_Cache', ['kode','harga','updated']);
  const vals = sh.getDataRange().getValues();
  for (let i = 1; i < vals.length; i++) {
    if (String(vals[i][0]).toUpperCase() === kode.toUpperCase())
      return parseNum(vals[i][1]);
  }
  return 0;
}

// ════════════════════════════════════════════════════════════
//  CRON — Daily Snapshot jam 18:00 WIB
// ════════════════════════════════════════════════════════════
function dailySnapshot() {
  try {
    const ss = SS();
    const t  = todayStr();
    Logger.log('=== dailySnapshot ' + t + ' ===');

    // BTC DCA
    let dcaInv = 0, dcaQty = 0;
    const dcaRows = getSheet(ss, 'BTC_DCA', ['tanggal','beli','harga_btc']).getDataRange().getValues();
    for (let i = 1; i < dcaRows.length; i++) {
      const b = parseNum(dcaRows[i][1]), h = parseNum(dcaRows[i][2]);
      if (b && h) { dcaInv += b; dcaQty += b / h; }
    }

    // Investasi
    const sahamMap = {};
    let invModal = 0;
    const invRows = getSheet(ss, 'Investasi', ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']).getDataRange().getValues();
    for (let i = 1; i < invRows.length; i++) {
      const [,kode,tipe,lotQty,hargaBeli,modal] = invRows[i];
      if (!kode) continue;
      const m = parseNum(modal) || parseNum(lotQty) * 100 * parseNum(hargaBeli);
      invModal += m;
      if (String(tipe) === 'Saham') {
        if (!sahamMap[kode]) sahamMap[kode] = {modal:0, lembar:0};
        sahamMap[kode].modal  += m;
        sahamMap[kode].lembar += parseNum(lotQty) * 100;
      }
    }

    // Fetch harga BTC
    const btcPrice = fetchBTC();
    if (btcPrice > 0) updateCache(ss, 'BTC', btcPrice);

    // Fetch harga saham
    let sahamNilai = 0;
    Object.entries(sahamMap).forEach(([kode, s]) => {
      const price = fetchSaham(kode);
      if (price > 0) { updateCache(ss, kode, price); sahamNilai += price * s.lembar; }
      else sahamNilai += getCached(ss, kode) * s.lembar;
    });

    // Hitung nilai
    const dcaNilai      = btcPrice > 0 ? dcaQty * btcPrice : dcaInv;
    const totalInvestasi = dcaNilai + sahamNilai;

    // Aset
    let totalTabungan = 0;
    const asetRows = getSheet(ss, 'Aset', ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']).getDataRange().getValues();
    for (let i = 1; i < asetRows.length; i++) {
      if (!asetRows[i][0]) continue;
      totalTabungan += parseNum(asetRows[i][3]) || parseNum(asetRows[i][2]);
    }

    // Liabilities (utang) — kurangi net worth
    let totalHutang = 0;
    const liabRows = getSheet(ss, 'Liabilities', ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']).getDataRange().getValues();
    for (let i = 1; i < liabRows.length; i++) {
      if (!liabRows[i][0]) continue;
      totalHutang += parseNum(liabRows[i][3]); // sisa_pokok
    }

    const totalAset = totalInvestasi + totalTabungan;
    const netWorth  = totalAset - totalHutang;

    if (totalAset > 0) {
      const sh = getSheet(ss, 'Snapshot', ['date','net_worth','total_aset','total_investasi','total_tabungan','total_hutang']);
      const vals = sh.getDataRange().getValues();
      let found = false;
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === t) {
          sh.getRange(i+1, 2, 1, 5).setValues([[Math.round(netWorth), Math.round(totalAset), Math.round(totalInvestasi), Math.round(totalTabungan), Math.round(totalHutang)]]);
          found = true; break;
        }
      }
      if (!found) sh.appendRow([t, Math.round(netWorth), Math.round(totalAset), Math.round(totalInvestasi), Math.round(totalTabungan), Math.round(totalHutang)]);
      Logger.log('✓ Snapshot: NW=Rp' + Math.round(netWorth).toLocaleString());
    }

    // Sync Perkasa Motors otomatis tiap hari
    try { syncPerkasaMotors(); } catch(e) { Logger.log('Perkasa sync (cron) error: ' + e.message); }

  } catch(e) { Logger.log('❌ Error dailySnapshot: ' + e.message); }
}

// ════════════════════════════════════════════════════════════
//  PERKASA MOTORS SYNC — baca endpoint induk, simpan ke Perkasa_Sync
// ════════════════════════════════════════════════════════════
const PERKASA_URL = 'https://script.google.com/macros/s/AKfycbwY-188f1lAHKuTTNrzzyESmq0S2wzrf_jIs-1K6xbaI-U-1GUo3Dh7Ic68MDFyULhJDg/exec';

function syncPerkasaMotors() {
  const ss = SS();
  const resp = UrlFetchApp.fetch(PERKASA_URL, {muteHttpExceptions:true, followRedirects:true});
  if (resp.getResponseCode() !== 200) throw new Error('HTTP ' + resp.getResponseCode());
  const data = JSON.parse(resp.getContentText());
  if (!data.ok || !Array.isArray(data.units)) throw new Error('Format tidak valid');

  let modalAktif = 0, totalProfit = 0, unitAktif = 0, unitTerjual = 0;
  const aktifList = [];   // unit yang modalnya sedang nyangkut
  const history   = [];   // unit terjual: tanggal jual + profit Panji

  data.units.forEach(u => {
    const mPanji = parseNum(u.panji && u.panji.total != null ? u.panji.total : u.modalPanji);
    const bagiPanji = parseNum(u.bagiPanji);
    if (String(u.status) === 'aktif') {
      if (mPanji > 0) {
        modalAktif += mPanji;
        unitAktif++;
        aktifList.push({nama:u.nama, jenis:u.jenis, modal:mPanji, tglMasuk:u.tgl||'', plat:u.plat||''});
      }
    } else if (String(u.status) === 'terjual') {
      unitTerjual++;
      if (bagiPanji > 0) {
        totalProfit += bagiPanji;
        history.push({nama:u.nama, jenis:u.jenis, profit:bagiPanji, tglJual:u.tglJual||'', hargaJual:parseNum(u.hargaJual)});
      }
    }
  });

  // Urutkan history by tanggal jual
  history.sort((a,b)=> String(a.tglJual).localeCompare(String(b.tglJual)));

  const payload = {
    modalAktif: Math.round(modalAktif),
    totalProfit: Math.round(totalProfit),
    unitAktif, unitTerjual,
    aktifList, history,
    syncedAt: Utilities.formatDate(new Date(), 'Asia/Jakarta', 'yyyy-MM-dd HH:mm')
  };

  // Simpan ke sheet Perkasa_Sync (1 baris JSON) + ke Config untuk akses cepat
  const sh = getSheet(ss, 'Perkasa_Sync', ['key','value']);
  const vals = sh.getDataRange().getValues();
  let found = false;
  for (let i = 1; i < vals.length; i++) {
    if (String(vals[i][0]) === 'data') { sh.getRange(i+1,2).setValue(JSON.stringify(payload)); found = true; break; }
  }
  if (!found) sh.appendRow(['data', JSON.stringify(payload)]);

  // Auto-update aset bisnis "Perkasa Motors" → nilai = modal aktif (masuk Net Worth)
  const asetSh = getSheet(ss, 'Aset', ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']);
  const aVals = asetSh.getDataRange().getValues();
  let aFound = false;
  const catatan = 'Auto-sync Perkasa Motors · Profit terkumpul Rp' + Math.round(totalProfit).toLocaleString('id-ID');
  for (let i = 1; i < aVals.length; i++) {
    if (String(aVals[i][0]) === 'Perkasa Motors') {
      asetSh.getRange(i+1, 1, 1, 6).setValues([['Perkasa Motors','Bisnis', Math.round(modalAktif), Math.round(modalAktif), todayStr(), catatan]]);
      aFound = true; break;
    }
  }
  if (!aFound) asetSh.appendRow(['Perkasa Motors','Bisnis', Math.round(modalAktif), Math.round(modalAktif), todayStr(), catatan]);

  Logger.log('✓ Perkasa sync: modalAktif=Rp' + Math.round(modalAktif).toLocaleString() + ' profit=Rp' + Math.round(totalProfit).toLocaleString());
  return payload;
}

// ════════════════════════════════════════════════════════════
//  doGet — READ + handle write via ?data= param (bypass CORS)
// ════════════════════════════════════════════════════════════
function doGet(e) {
  try {
    const ss = SS();
    const p  = (e && e.parameter) ? e.parameter : {};
    const action = p.action || 'load';

    // ── Write via GET param (CORS-safe) ────────────────────
    if (p.data) {
      try {
        const data = JSON.parse(decodeURIComponent(p.data));
        return handleWrite(ss, data);
      } catch(err) {
        return out({ error: 'Invalid data param: ' + err.message });
      }
    }

    // ── Auth ────────────────────────────────────────────────
    if (action === 'checkAuth') {
      const pass  = p.pass || '';
      const vals  = getSheet(ss, 'Config', ['key','value']).getDataRange().getValues();
      const stored = vals.find(r => r[0] === 'password')?.[1] || 'fintrack2024';
      return out({ ok: pass === String(stored) });
    }

    // ── Saham prices realtime ───────────────────────────────
    if (action === 'sahamPrices') {
      const kodes = (p.kodes || '').toUpperCase().split(',').map(k => k.trim()).filter(Boolean);
      const prices = {};
      kodes.forEach(k => {
        const price = fetchSaham(k);
        if (price > 0) { prices[k] = price; updateCache(ss, k, price); }
        else { const c = getCached(ss, k); if (c > 0) prices[k] = c; }
      });
      return out({ prices });
    }

    // ── Manual sync Perkasa Motors ──────────────────────────
    if (action === 'syncPerkasa') {
      try {
        const payload = syncPerkasaMotors();
        return out({ success: true, perkasa: payload });
      } catch(err) {
        return out({ success: false, error: err.message });
      }
    }

    // ── Load all data ───────────────────────────────────────
    if (action === 'load') {

      // Transactions
      const transactions = [];
      const txRows = getSheet(ss, 'Transactions', ['id','tanggal','tipe','deskripsi','kategori','subkategori','nominal','akun','bulan','tahun','catatan']).getDataRange().getValues();
      for (let i = 1; i < txRows.length; i++) {
        const [id,tgl,tipe,desk,kat,subkat,nom,akun,bln,thn,cat] = txRows[i];
        if (!tgl || !nom) continue;
        transactions.push({
          id: String(id), tanggal: String(tgl).trim(), tipe: String(tipe),
          deskripsi: String(desk || ''), kategori: String(kat || ''),
          subkategori: String(subkat || ''), nominal: parseNum(nom),
          akun: String(akun || ''), bulan: String(bln || ''),
          tahun: String(thn || ''), catatan: String(cat || '')
        });
      }

      // Budget
      const budget = [];
      const bdgRows = getSheet(ss, 'Budget', ['bulan','tahun','kategori','tipe_kategori','alokasi']).getDataRange().getValues();
      for (let i = 1; i < bdgRows.length; i++) {
        const [bln,thn,kat,tipe,alokasi] = bdgRows[i];
        if (!kat) continue;
        budget.push({ bulan: String(bln), tahun: String(thn), kategori: String(kat), tipe: String(tipe || ''), alokasi: parseNum(alokasi) });
      }

      // BTC DCA
      const btcDca = [];
      const dcaRows = getSheet(ss, 'BTC_DCA', ['tanggal','beli','harga_btc']).getDataRange().getValues();
      for (let i = 1; i < dcaRows.length; i++) {
        const [tgl, beli, harga] = dcaRows[i];
        if (!tgl || !beli || !harga) continue;
        btcDca.push({ id: 'sh' + i, tanggal: String(tgl).trim(), beli: parseNum(beli), harga: parseNum(harga) });
      }

      // Investasi
      const investasi = [];
      const invRows = getSheet(ss, 'Investasi', ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']).getDataRange().getValues();
      for (let i = 1; i < invRows.length; i++) {
        const [tgl,kode,tipe,lotQty,hargaBeli,modal,cat] = invRows[i];
        if (!kode) continue;
        investasi.push({
          id: 'i' + i, tanggal: String(tgl).trim(), kode: String(kode).toUpperCase(),
          tipe: String(tipe), lotQty: parseNum(lotQty), hargaBeli: parseNum(hargaBeli),
          modal: parseNum(modal) || parseNum(lotQty) * 100 * parseNum(hargaBeli),
          catatan: String(cat || '')
        });
      }

      // Aset
      const aset = [];
      const asetRows = getSheet(ss, 'Aset', ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']).getDataRange().getValues();
      for (let i = 1; i < asetRows.length; i++) {
        const [nama,kat,modal,nilai,tglUpd,cat] = asetRows[i];
        if (!nama) continue;
        aset.push({
          id: 'a' + i, nama: String(nama), kategori: String(kat || ''),
          modal: parseNum(modal), nilaiSaatIni: parseNum(nilai) || parseNum(modal),
          tanggalUpdate: String(tglUpd || ''), catatan: String(cat || '')
        });
      }

      // Goals
      const goals = [];
      const goalRows = getSheet(ss, 'Goals', ['tipe','no','goal','info','kategori','deadline','done']).getDataRange().getValues();
      for (let i = 1; i < goalRows.length; i++) {
        const [tipe,no,goal,info,kat,deadline,done] = goalRows[i];
        if (!goal) continue;
        goals.push({
          id: 'g' + i, tipe: String(tipe), no: Number(no) || i,
          goal: String(goal), info: String(info || ''), kategori: String(kat || ''),
          deadline: String(deadline || ''), done: done === true || done === 'TRUE' || done === 'true'
        });
      }

      // Snapshots
      const snapshots = [];
      const snapRows = getSheet(ss, 'Snapshot', ['date','net_worth','total_aset','total_investasi','total_tabungan','total_hutang']).getDataRange().getValues();
      for (let i = 1; i < snapRows.length; i++) {
        const [date,nw,ta,ti,tt,th] = snapRows[i];
        if (!date) continue;
        snapshots.push({
          date: String(date), netWorth: parseNum(nw), totalAset: parseNum(ta),
          totalInvestasi: parseNum(ti), totalTabungan: parseNum(tt), totalHutang: parseNum(th) || 0
        });
      }

      // Config
      const config = {};
      getSheet(ss, 'Config', ['key','value']).getDataRange().getValues()
        .forEach(r => { if (r[0]) config[String(r[0])] = String(r[1] || ''); });

      // Harga Cache
      const hargaCache = {};
      getSheet(ss, 'Harga_Cache', ['kode','harga','updated']).getDataRange().getValues()
        .forEach((r, i) => { if (i > 0 && r[0]) hargaCache[String(r[0]).toUpperCase()] = parseNum(r[1]); });

      // Cash Accounts
      const cashAccounts = [];
      getSheet(ss, 'Cash_Accounts', ['nama','tipe','saldo_manual','override','urutan','aktif']).getDataRange().getValues()
        .forEach((r, i) => {
          if (i === 0 || !r[0]) return;
          cashAccounts.push({
            nama: String(r[0]), tipe: String(r[1] || 'Bank'),
            saldoManual: parseNum(r[2]),
            override: r[3] === true || r[3] === 'TRUE' || r[3] === 'true',
            urutan: parseNum(r[4]) || (i),
            aktif: r[5] === true || r[5] === 'TRUE' || r[5] === 'true' || r[5] === '' || r[5] == null
          });
        });

      // Commitments
      const commitments = [];
      getSheet(ss, 'Commitments', ['id','due_date','deskripsi','nominal','kategori','status']).getDataRange().getValues()
        .forEach((r, i) => {
          if (i === 0 || !r[0]) return;
          commitments.push({
            id: String(r[0]), dueDate: String(r[1] || ''), deskripsi: String(r[2] || ''),
            nominal: parseNum(r[3]), kategori: String(r[4] || ''), status: String(r[5] || 'pending')
          });
        });

      // Liabilities (Utang)
      const liabilities = [];
      getSheet(ss, 'Liabilities', ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']).getDataRange().getValues()
        .forEach((r, i) => {
          if (i === 0 || !r[0]) return;
          liabilities.push({
            id: String(r[0]), nama: String(r[1] || ''), totalPinjaman: parseNum(r[2]),
            sisaPokok: parseNum(r[3]), cicilanBulan: parseNum(r[4]), kreditur: String(r[5] || ''),
            catatan: String(r[6] || ''), tanggalUpdate: String(r[7] || '')
          });
        });

      // Perkasa Motors sync data
      let perkasa = null;
      try {
        const psSh = ss.getSheetByName('Perkasa_Sync');
        if (psSh && psSh.getLastRow() > 1) {
          const psVals = psSh.getDataRange().getValues();
          for (let i = 1; i < psVals.length; i++) {
            if (String(psVals[i][0]) === 'data' && psVals[i][1]) { perkasa = JSON.parse(psVals[i][1]); break; }
          }
        }
      } catch(e) {}

      // Subscriptions
      const subscriptions = [];
      getSheet(ss, 'Subscriptions', ['id','nama','nominal','billing_date','kategori','keterangan','aktif']).getDataRange().getValues()
        .forEach((r, i) => {
          if (i === 0 || !r[0]) return;
          subscriptions.push({
            id: String(r[0]), nama: String(r[1]||''), nominal: parseNum(r[2]),
            billingDate: parseInt(r[3])||1, kategori: String(r[4]||''), keterangan: String(r[5]||''),
            aktif: r[6]===false||r[6]==='FALSE'||r[6]===0 ? false : true
          });
        });

      return out({ transactions, budget, btcDca, investasi, aset, goals, snapshots, config, hargaCache, cashAccounts, commitments, liabilities, subscriptions, perkasa });
    }

    return out({ error: 'Unknown action: ' + action });

  } catch(err) {
    return out({ error: err.message });
  }
}

// ════════════════════════════════════════════════════════════
//  doPost — fallback POST
// ════════════════════════════════════════════════════════════
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    return handleWrite(SS(), data);
  } catch(err) {
    return out({ error: err.message });
  }
}

// ════════════════════════════════════════════════════════════
//  handleWrite — semua operasi tulis dipanggil dari doGet & doPost
// ════════════════════════════════════════════════════════════
function handleWrite(ss, data) {
  try {
    const action = data.action;

    // ── Transactions ───────────────────────────────────────
    if (action === 'addTransaction') {
      const sh = getSheet(ss, 'Transactions', ['id','tanggal','tipe','deskripsi','kategori','subkategori','nominal','akun','bulan','tahun','catatan']);
      const id = data.id || ('tx_' + Date.now());
      sh.appendRow([id, data.tanggal, data.tipe, data.deskripsi, data.kategori, data.subkategori || '', data.nominal, data.akun, data.bulan, data.tahun, data.catatan || '']);
      Logger.log('addTransaction: ' + data.deskripsi + ' Rp' + data.nominal);
      return out({ success: true, id });
    }

    if (action === 'deleteTransaction') {
      const sh = getSheet(ss, 'Transactions', ['id','tanggal','tipe','deskripsi','kategori','subkategori','nominal','akun','bulan','tahun','catatan']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) { sh.deleteRow(i + 1); return out({ success: true }); }
      }
      return out({ success: false, error: 'Not found' });
    }

    if (action === 'editTransaction') {
      const sh = getSheet(ss, 'Transactions', ['id','tanggal','tipe','deskripsi','kategori','subkategori','nominal','akun','bulan','tahun','catatan']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) {
          sh.getRange(i+1, 1, 1, 11).setValues([[data.id, data.tanggal, data.tipe, data.deskripsi, data.kategori, data.subkategori || '', data.nominal, data.akun, data.bulan, data.tahun, data.catatan || '']]);
          return out({ success: true });
        }
      }
      return out({ success: false, error: 'Not found' });
    }

    // ── Budget ─────────────────────────────────────────────
    if (action === 'setBudget') {
      const sh = getSheet(ss, 'Budget', ['bulan','tahun','kategori','tipe_kategori','alokasi']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.bulan) && String(vals[i][1]) === String(data.tahun) && String(vals[i][2]) === String(data.kategori)) {
          sh.getRange(i+1, 5).setValue(data.alokasi);
          return out({ success: true });
        }
      }
      sh.appendRow([data.bulan, data.tahun, data.kategori, data.tipe || '', data.alokasi]);
      return out({ success: true, created: true });
    }

    // ── BTC DCA ────────────────────────────────────────────
    if (action === 'addBtcDca') {
      const sh = getSheet(ss, 'BTC_DCA', ['tanggal','beli','harga_btc']);
      sh.appendRow([data.tanggal, data.beli, data.harga]);
      Logger.log('addBtcDca: ' + data.tanggal + ' Rp' + data.beli + ' @ Rp' + data.harga);
      return out({ success: true });
    }

    if (action === 'editBtcDca') {
      const sh = getSheet(ss, 'BTC_DCA', ['tanggal','beli','harga_btc']);
      const row = parseInt(data.rowIndex) + 2;
      sh.getRange(row, 1, 1, 3).setValues([[data.tanggal, data.beli, data.harga]]);
      return out({ success: true });
    }

    if (action === 'deleteBtcDca') {
      const sh = getSheet(ss, 'BTC_DCA', ['tanggal','beli','harga_btc']);
      sh.deleteRow(parseInt(data.rowIndex) + 2);
      return out({ success: true });
    }

    // ── Investasi ──────────────────────────────────────────
    if (action === 'addInvestasi') {
      const sh = getSheet(ss, 'Investasi', ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']);
      const modal = data.modal || (parseNum(data.lotQty) * 100 * parseNum(data.hargaBeli));
      sh.appendRow([data.tanggal, data.kode.toUpperCase(), data.tipe, data.lotQty, data.hargaBeli, modal, data.catatan || '']);
      Logger.log('addInvestasi: ' + data.kode + ' ' + data.lotQty + ' lot @ Rp' + data.hargaBeli);
      return out({ success: true });
    }

    if (action === 'deleteInvestasi') {
      const sh = getSheet(ss, 'Investasi', ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']);
      sh.deleteRow(parseInt(data.rowIndex) + 2);
      return out({ success: true });
    }

    if (action === 'editInvestasi') {
      const sh = getSheet(ss, 'Investasi', ['tanggal','kode','tipe','lot_qty','harga_beli','modal','catatan']);
      const row = parseInt(data.rowIndex) + 2;
      const modal = data.modal || (parseNum(data.lotQty) * 100 * parseNum(data.hargaBeli));
      sh.getRange(row, 1, 1, 7).setValues([[data.tanggal, String(data.kode).toUpperCase(), data.tipe, data.lotQty, data.hargaBeli, modal, data.catatan || '']]);
      return out({ success: true });
    }

    // ── Aset ───────────────────────────────────────────────
    if (action === 'saveAset') {
      const sh = getSheet(ss, 'Aset', ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.nama)) {
          sh.getRange(i+1, 1, 1, 6).setValues([[data.nama, data.kategori, data.modal, data.nilaiSaatIni, todayStr(), data.catatan || '']]);
          return out({ success: true, updated: true });
        }
      }
      sh.appendRow([data.nama, data.kategori, data.modal, data.nilaiSaatIni, todayStr(), data.catatan || '']);
      Logger.log('saveAset: ' + data.nama + ' Rp' + data.nilaiSaatIni);
      return out({ success: true, created: true });
    }

    if (action === 'deleteAset') {
      const sh = getSheet(ss, 'Aset', ['nama','kategori','modal','nilai_saat_ini','tanggal_update','catatan']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.nama)) { sh.deleteRow(i + 1); return out({ success: true }); }
      }
      return out({ success: false });
    }

    // ── Goals ──────────────────────────────────────────────
    if (action === 'saveGoal') {
      const sh = getSheet(ss, 'Goals', ['tipe','no','goal','info','kategori','deadline','done']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === data.tipe && Number(vals[i][1]) === Number(data.no)) {
          sh.getRange(i+1, 1, 1, 7).setValues([[data.tipe, data.no, data.goal, data.info || '', data.kategori || '', data.deadline || '', data.done || false]]);
          return out({ success: true });
        }
      }
      sh.appendRow([data.tipe, data.no, data.goal, data.info || '', data.kategori || '', data.deadline || '', data.done || false]);
      return out({ success: true, created: true });
    }

    if (action === 'toggleGoal') {
      const sh = getSheet(ss, 'Goals', ['tipe','no','goal','info','kategori','deadline','done']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === data.tipe && Number(vals[i][1]) === Number(data.no)) {
          sh.getRange(i+1, 7).setValue(data.done);
          return out({ success: true });
        }
      }
      return out({ success: false });
    }

    // ── Snapshot ───────────────────────────────────────────
    if (action === 'saveSnapshot') {
      const sh = getSheet(ss, 'Snapshot', ['date','net_worth','total_aset','total_investasi','total_tabungan','total_hutang']);
      const d  = data.date || todayStr();
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === d) {
          sh.getRange(i+1, 2, 1, 5).setValues([[data.netWorth || 0, data.totalAset || 0, data.totalInvestasi || 0, data.totalTabungan || 0, data.totalHutang || 0]]);
          return out({ success: true });
        }
      }
      sh.appendRow([d, data.netWorth || 0, data.totalAset || 0, data.totalInvestasi || 0, data.totalTabungan || 0, data.totalHutang || 0]);
      return out({ success: true });
    }

    // ── Remove Budget Category ────────────────────────────
    if (action === 'removeBudget') {
      const sh = getSheet(ss, 'Budget', ['bulan','tahun','kategori','tipe_kategori','alokasi']);
      const vals = sh.getDataRange().getValues();
      for (let i = vals.length - 1; i >= 1; i--) {
        if (String(vals[i][0])===String(data.bulan) && String(vals[i][1])===String(data.tahun) && String(vals[i][2])===String(data.kategori)) {
          sh.deleteRow(i + 1);
          return out({ success: true });
        }
      }
      return out({ success: false, error: 'Not found' });
    }

    // ── Commitments ────────────────────────────────────────
    if (action === 'addCommitment') {
      const sh = getSheet(ss, 'Commitments', ['id','due_date','deskripsi','nominal','kategori','status']);
      const id = data.id || ('cm_' + Date.now());
      sh.appendRow([id, data.dueDate, data.deskripsi, data.nominal, data.kategori || '', data.status || 'pending']);
      return out({ success: true, id });
    }
    if (action === 'updateCommitment') {
      const sh = getSheet(ss, 'Commitments', ['id','due_date','deskripsi','nominal','kategori','status']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) {
          if (data.status !== undefined) sh.getRange(i+1, 6).setValue(data.status);
          if (data.dueDate !== undefined) sh.getRange(i+1, 2).setValue(data.dueDate);
          if (data.deskripsi !== undefined) sh.getRange(i+1, 3).setValue(data.deskripsi);
          if (data.nominal !== undefined) sh.getRange(i+1, 4).setValue(data.nominal);
          if (data.kategori !== undefined) sh.getRange(i+1, 5).setValue(data.kategori);
          return out({ success: true });
        }
      }
      return out({ success: false, error: 'Not found' });
    }
    if (action === 'deleteCommitment') {
      const sh = getSheet(ss, 'Commitments', ['id','due_date','deskripsi','nominal','kategori','status']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) { sh.deleteRow(i+1); return out({ success: true }); }
      }
      return out({ success: false, error: 'Not found' });
    }

    // ── Liabilities (Utang) ────────────────────────────────
    if (action === 'addLiability') {
      const sh = getSheet(ss, 'Liabilities', ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']);
      const id = data.id || ('lb_' + Date.now());
      sh.appendRow([id, data.nama, data.totalPinjaman, data.sisaPokok, data.cicilanBulan, data.kreditur || '', data.catatan || '', todayStr()]);
      return out({ success: true, id });
    }
    if (action === 'updateLiability') {
      const sh = getSheet(ss, 'Liabilities', ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) {
          sh.getRange(i+1, 1, 1, 8).setValues([[data.id, data.nama, data.totalPinjaman, data.sisaPokok, data.cicilanBulan, data.kreditur || '', data.catatan || '', todayStr()]]);
          return out({ success: true });
        }
      }
      return out({ success: false, error: 'Not found' });
    }
    if (action === 'deleteLiability') {
      const sh = getSheet(ss, 'Liabilities', ['id','nama','total_pinjaman','sisa_pokok','cicilan_bulan','kreditur','catatan','tanggal_update']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) { sh.deleteRow(i+1); return out({ success: true }); }
      }
      return out({ success: false, error: 'Not found' });
    }

    // ── Subscriptions ──────────────────────────────────────
    if (action === 'addSubscription') {
      const sh = getSheet(ss, 'Subscriptions', ['id','nama','nominal','billing_date','kategori','keterangan','aktif']);
      const id = data.id || ('sb_' + Date.now());
      sh.appendRow([id, data.nama||'', data.nominal||0, data.billingDate||1, data.kategori||'Lainnya', data.keterangan||'', data.aktif!==false]);
      return out({ success: true, id });
    }
    if (action === 'updateSubscription') {
      const sh = getSheet(ss, 'Subscriptions', ['id','nama','nominal','billing_date','kategori','keterangan','aktif']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) {
          sh.getRange(i+1, 1, 1, 7).setValues([[data.id, data.nama||'', data.nominal||0, data.billingDate||1, data.kategori||'Lainnya', data.keterangan||'', data.aktif!==false]]);
          return out({ success: true });
        }
      }
      return out({ success: false, error: 'Not found' });
    }
    if (action === 'deleteSubscription') {
      const sh = getSheet(ss, 'Subscriptions', ['id','nama','nominal','billing_date','kategori','keterangan','aktif']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.id)) { sh.deleteRow(i+1); return out({ success: true }); }
      }
      return out({ success: false, error: 'Not found' });
    }

    // ── Config ─────────────────────────────────────────────
    if (action === 'setConfig') {
      const sh = getSheet(ss, 'Config', ['key','value']);
      const vals = sh.getDataRange().getValues();
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][0]) === String(data.key)) {
          sh.getRange(i+1, 2).setValue(data.value);
          return out({ success: true });
        }
      }
      sh.appendRow([data.key, data.value]);
      return out({ success: true, created: true });
    }

    return out({ error: 'Unknown action: ' + action });

  } catch(err) {
    Logger.log('handleWrite error: ' + err.message);
    return out({ error: err.message });
  }
}
