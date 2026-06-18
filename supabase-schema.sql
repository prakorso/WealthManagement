-- ═══════════════════════════════════════════════════════════════
-- WEALTH MANAGEMENT — Supabase Schema
-- Jalankan di Supabase SQL Editor: https://supabase.com/dashboard
-- Project: pefkfuoowzfnbkmygzxo
-- ═══════════════════════════════════════════════════════════════

-- NOTE: Jalankan bagian per bagian jika perlu

-- ── 1. TRANSACTIONS ──────────────────────────────────────────
create table if not exists transactions (
  id text primary key,
  user_id uuid references auth.users not null default auth.uid(),
  tanggal date,
  tipe text not null check (tipe in ('pemasukan','pengeluaran','tabungan')),
  deskripsi text,
  kategori text,
  subkategori text,
  nominal numeric default 0,
  akun text,
  bulan text,
  tahun text,
  catatan text,
  periode_bulan text,
  periode_tahun text,
  created_at timestamptz default now()
);
alter table transactions enable row level security;
create policy "own_transactions" on transactions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 2. BUDGET ────────────────────────────────────────────────
create table if not exists budget (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  bulan text not null,
  tahun text not null,
  kategori text not null,
  tipe_kategori text,
  alokasi numeric default 0,
  unique (user_id, bulan, tahun, kategori)
);
alter table budget enable row level security;
create policy "own_budget" on budget for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 3. BTC DCA ───────────────────────────────────────────────
create table if not exists btc_dca (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  tanggal date,
  beli numeric,
  harga numeric,
  created_at timestamptz default now()
);
alter table btc_dca enable row level security;
create policy "own_btc_dca" on btc_dca for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 4. INVESTASI ─────────────────────────────────────────────
create table if not exists investasi (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  tanggal date,
  kode text,
  tipe text,
  lot_qty numeric,
  harga_beli numeric,
  modal numeric,
  catatan text,
  created_at timestamptz default now()
);
alter table investasi enable row level security;
create policy "own_investasi" on investasi for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 5. ASET ──────────────────────────────────────────────────
create table if not exists aset (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  nama text not null,
  kategori text,
  modal numeric default 0,
  nilai_saat_ini numeric,
  tanggal_update date,
  catatan text,
  unique (user_id, nama)
);
alter table aset enable row level security;
create policy "own_aset" on aset for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 6. LIABILITIES ───────────────────────────────────────────
create table if not exists liabilities (
  id text primary key,
  user_id uuid references auth.users not null default auth.uid(),
  nama text,
  total_pinjaman numeric default 0,
  sisa_pokok numeric default 0,
  cicilan_bulan numeric default 0,
  kreditur text,
  catatan text,
  tanggal_update date default current_date
);
alter table liabilities enable row level security;
create policy "own_liabilities" on liabilities for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 7. COMMITMENTS ───────────────────────────────────────────
create table if not exists commitments (
  id text primary key,
  user_id uuid references auth.users not null default auth.uid(),
  due_date text,
  deskripsi text,
  nominal numeric default 0,
  kategori text,
  status text default 'pending'
);
alter table commitments enable row level security;
create policy "own_commitments" on commitments for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 8. SUBSCRIPTIONS ─────────────────────────────────────────
create table if not exists subscriptions (
  id text primary key,
  user_id uuid references auth.users not null default auth.uid(),
  nama text,
  nominal numeric default 0,
  billing_date integer,
  kategori text,
  keterangan text,
  aktif boolean default true
);
alter table subscriptions enable row level security;
create policy "own_subscriptions" on subscriptions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 9. RENCANA ───────────────────────────────────────────────
create table if not exists rencana (
  id text primary key,
  user_id uuid references auth.users not null default auth.uid(),
  bulan text,
  tahun text,
  tipe text,
  deskripsi text,
  kategori text,
  nominal numeric default 0,
  akun text,
  liability_id text references liabilities(id),
  status text default 'pending',
  tx_id text references transactions(id)
);
alter table rencana enable row level security;
create policy "own_rencana" on rencana for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 10. GOALS ────────────────────────────────────────────────
create table if not exists goals (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  tipe text,
  no integer,
  goal text,
  info text,
  kategori text,
  deadline text,
  done boolean default false,
  unique (user_id, tipe, no)
);
alter table goals enable row level security;
create policy "own_goals" on goals for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 11. SNAPSHOTS ────────────────────────────────────────────
create table if not exists snapshots (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  date date not null,
  net_worth numeric default 0,
  total_aset numeric default 0,
  total_inv numeric default 0,
  port_val numeric default 0,
  dca_val numeric default 0,
  aset_val numeric default 0,
  bisnis_val numeric default 0,
  cash_val numeric default 0,
  total_hutang numeric default 0,
  unique (user_id, date)
);
alter table snapshots enable row level security;
create policy "own_snapshots" on snapshots for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 12. HARGA CACHE ──────────────────────────────────────────
create table if not exists harga_cache (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  kode text not null,
  harga numeric,
  updated date default current_date,
  unique (user_id, kode)
);
alter table harga_cache enable row level security;
create policy "own_harga_cache" on harga_cache for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 13. CONFIG ───────────────────────────────────────────────
create table if not exists config (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  key text not null,
  value text,
  unique (user_id, key)
);
alter table config enable row level security;
create policy "own_config" on config for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── 14. CASH ACCOUNTS ────────────────────────────────────────
create table if not exists cash_accounts (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users not null default auth.uid(),
  nama text not null,
  tipe text default 'Bank',
  saldo_manual numeric default 0,
  override_saldo boolean default false,
  urutan integer default 0,
  aktif boolean default true,
  unique (user_id, nama)
);
alter table cash_accounts enable row level security;
create policy "own_cash_accounts" on cash_accounts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ═══════════════════════════════════════════════════════════════
-- SETELAH MENJALANKAN SQL INI:
-- 1. Buka Authentication → Users di Supabase Dashboard
-- 2. Klik "Add user" → tambah email + password untuk kamu
-- 3. Ulangi untuk pasangan (email + password berbeda)
-- 4. Update kode dashboard untuk pakai Supabase
-- ═══════════════════════════════════════════════════════════════
