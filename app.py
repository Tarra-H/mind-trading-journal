import streamlit as st
import pandas as pd
import datetime
import requests

# 1. KONFIGURASI HALAMAN UTAMA WEB
st.set_page_config(page_title="🔒 Secure Private Journal", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI MODUL SUPABASE (ANTI-HILANG & ANTI-RESET) ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- FITUR KONTROL AKSES ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def login():
    st.title("🔒 Nata Mind Trading Journal - Gateway")
    st.markdown("Selamat datang! Silakan login sebagai Pemilik untuk mengisi data riwayat.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("🚀 Log In Pemilik (Admin)", use_container_width=True):
            if username == "trader123" and password == "rahasia2026":
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("Username atau Password Admin salah!")
    with col_l2:
        if st.button("👥 Masuk Sebagai Tamu (Coba Sandbox)", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = "Guest"
            st.rerun()

if not st.session_state.authenticated:
    login()
    st.stop()

# --- 🌐 FUNGSI DATA ENGINE SUPABASE REAL-TIME (TANPA CACHE AGAR ANTI-STUCK) ---
def muat_data_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return pd.DataFrame()
    url = f"{SUPABASE_URL}/rest/v1/jurnal?select=*"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and len(res.json()) > 0:
            df = pd.DataFrame(res.json())
            if 'id' in df.columns:
                df = df.sort_values(by='id').reset_index(drop=True)
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=[
        'id', 'Tanggal', 'Jam_Entry', 'Aset_Broker', 'Simbol', 'Tipe', 'Harga_Masuk', 'Harga_Keluar', 
        'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net_PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
    ])

# Sesi Memori Utama Aplikasi
if st.session_state.user_role == "Admin":
    df_dashboard = muat_data_supabase()
    role_text = "🔑 AKUN PEMILIK (ADMIN)"
    caption_text = "Status: Terhubung Permanen ke Serverless Supabase Cloud. Data 100% Abadi & Aman."
else:
    if 'guest_db' not in st.session_state:
        st.session_state.guest_db = pd.DataFrame(columns=[
            'Tanggal', 'Jam_Entry', 'Aset_Broker', 'Simbol', 'Tipe', 'Harga_Masuk', 'Harga_Keluar', 
            'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net_PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
        ])
    df_dashboard = st.session_state.guest_db
    role_text = "👥 AKUN TAMU (GUEST MODE)"
    caption_text = "Status: Mode Sandbox Tamu Sementara."

# SIDEBAR UTAMA
st.sidebar.markdown(f"### Status Sesi:\n**{role_text}**")
if st.sidebar.button("🔒 Log Out / Kunci Jurnal", type="primary", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.rerun()
st.sidebar.markdown("---")

st.title("🧠 Nata Mind Trading Journal & Visual Audit")
st.caption(caption_text)
st.markdown("---")

# SIDEBAR: MONEY MANAGEMENT
st.sidebar.header("🛡️ Proteksi Risiko & Uang")
modal_idr = st.sidebar.number_input("Modal Saham Aktif (IDR)", min_value=0.0, value=10000000.0, step=1000000.0)
modal_usd = st.sidebar.number_input("Modal Forex Aktif (USD)", min_value=0.0, value=1000.0, step=100.0)
persen_risiko = st.sidebar.slider("Batas Risiko Maksimal per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
st.sidebar.info(f"💡 **Toleransi Los Maksimal:**\n* Saham: Rp {modal_idr * (persen_risiko / 100):,.0f}\n* Forex: ${modal_usd * (persen_risiko / 100):,.2f}")

# FORMULIR INPUT REKAP TRANSAKSI
st.header("📝 Catat Riwayat Transaksi")

with st.form("form_dual_mode", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", value=datetime.date.today())
        jam_entry = st.time_input("Jam Masuk Posisi", value=datetime.time(0, 0))
        pilihan_broker_standar = ["Stockbit IDR", "Ajaib IDR", "Gotrade USD", "Exness USD", "XM Forex USD", "Lainnya (Ketik Manual)..."]
        broker_pilih = st.selectbox("Platform / Broker", pilihan_broker_standar)
        broker = st.text_input("Ketik Nama Broker Anda").strip() if broker_pilih == "Lainnya (Ketik Manual)..." else broker_pilih
            
    with col2:
        simbol = st.text_input("Simbol / Kode Aset").upper()
        tipe = st.selectbox("Arah Posisi", ["BUY", "SELL"])
        ukuran = st.number_input("Jumlah Ukuran (Lot / Lembar)", min_value=0.0, step=1.0, format="%f", value=0.0)
        
    with col3:
        harga_masuk = st.number_input("Harga Masuk", min_value=0.0, step=1.0, format="%f", value=0.0)
        harga_keluar = st.number_input("Harga Keluar", min_value=0.0, step=1.0, format="%f", value=0.0)
        r_sl = st.number_input("Rencana Stop Loss", min_value=0.0, step=1.0, format="%f", value=0.0)
        r_tp = st.number_input("Rencana Take Profit", min_value=0.0, step=1.0, format="%f", value=0.0)
        
    st.markdown("---")
    emosi_manual = st.selectbox("🧠 Apa emosi yang Anda rasakan saat membuka posisi ini?", 
                                ["Disiplin Plan", "FOMO / Terburu-buru", "Revenge Trading", "Breakout Setup", "Buy on Weakness"])

    submit = st.form_submit_button("⚡ Simpan & Jalankan Audit Sistem")

# --- PROSES SIMPAN TRANSAKSI ---
if submit and simbol and ukuran > 0:
    multiplier = 1 if tipe == "BUY" else -1
    if "USD" in broker.upper() or "FOREX" in broker.upper():
        pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
    else:
        pnl = (harga_keluar - harga_masuk) * (ukuran * 100) * multiplier
        
    status_aktif = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
    audit_komparasi = f"⚠️ Emosi Terdeteksi: {emosi_manual}" if emosi_manual != "Disiplin Plan" else "✅ Sesuai Trading Plan"
    deteksi_otomatis = "Impulsif Berisiko" if emosi_manual != "Disiplin Plan" else "Sesuai Aturan"

    payload_data = {
        'Tanggal': str(tanggal), 'Jam_Entry': str(jam_entry), 'Aset_Broker': str(broker), 'Simbol': str(simbol), 'Tipe': str(tipe),
        'Harga_Masuk': str(float(harga_masuk)), 'Harga_Keluar': str(float(harga_keluar)), 'Rencana_SL': str(float(r_sl)), 'Rencana_TP': str(float(r_tp)),
        'Ukuran': str(float(ukuran)), 'Net_PnL': str(float(pnl)), 'Emosi_Pilihan_Manual': str(emosi_manual), 'Deteksi_Otomatis_Sistem': str(deteksi_otomatis),
        'Audit_Komparasi': str(audit_komparasi), 'Status': str(status_aktif)
    }
    
    if st.session_state.user_role == "Admin":
        url = f"{SUPABASE_URL}/rest/v1/jurnal"
        requests.post(url, headers=headers, json=payload_data)
        st.success("🔥 Data sukses disimpan permanen ke Cloud Supabase!")
    else:
        new_row = pd.DataFrame([payload_data])
        st.session_state.guest_db = pd.concat([st.session_state.guest_db, new_row], ignore_index=True)
        
    st.rerun()

# --- 📊 BAGIAN DASHBOARD VISUALISASI ---
st.header("📊 Analisis Performa & Grafik Modal")

if df_dashboard is not None and not df_dashboard.empty:
    df_dashboard['Net_PnL'] = pd.to_numeric(df_dashboard['Net_PnL'], errors='coerce').fillna(0)
    
    # FILTER KATEGORI WAKTU BULAN TAHUN
    df_dashboard['Datetime_Obj'] = pd.to_datetime(df_dashboard['Tanggal'], errors='coerce')
    df_dashboard['Bulan_Tahun'] = df_dashboard['Datetime_Obj'].dt.strftime('%Y - %B').fillna("Format Salah")
    list_kelompok = ["Semua Data"] + sorted(list(df_dashboard['Bulan_Tahun'].unique()))
    
    kategori_pilih = st.selectbox("📅 Pilih Kelompok Bulan & Tahun yang Ingin Dilihat:", list_kelompok)
    df_filtered = df_dashboard if kategori_pilih == "Semua Data" else df_dashboard[df_dashboard['Bulan_Tahun'] == kategori_pilih]
    
    df_filtered['Kumulatif_Profit'] = df_filtered['Net_PnL'].cumsum()
    st.line_chart(df_filtered, x='Tanggal', y='Kumulatif_Profit', use_container_width=True)
    
    # GRAFIK AUDIT EMOSI
    st.markdown("### 🧠 Audit Distribusi Kontrol Emosi & Psikologi")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.bar_chart(df_filtered['Emosi_Pilihan_Manual'].value_counts(), use_container_width=True)
    with col_g2:
        st.bar_chart(df_filtered['Deteksi_Otomatis_Sistem'].value_counts(), use_container_width=True)

    # 📝 TABEL INTERAKTIF EDIT SEPERTI EXCEL & HAPUS CENTANG (INDEX DARI 1)
    st.markdown("### 📝 Log Riwayat Tabel Jurnal Transaksi")
    df_tampilan = df_filtered.copy().reset_index(drop=True)
    df_tampilan.index = range(1, len(df_tampilan) + 1)
    df_tampilan["Pilih Hapus"] = False
    
    pembantu_kolom = ['Datetime_Obj', 'Bulan_Tahun', 'Kumulatif_Profit']
    for pk in pembantu_kolom:
        if pk in df_tampilan.columns: df_tampilan = df_tampilan.drop(columns=[pk])
        
    edited_df = st.data_editor(df_tampilan, use_container_width=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Simpan Semua Perubahan Koreksi Sel", use_container_width=True, type="primary"):
            if st.session_state.user_role == "Admin":
                for idx in edited_df.index:
                    db_id = edited_df.loc[idx, 'id']
