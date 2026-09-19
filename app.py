import streamlit as st
import pandas as pd
import datetime
import os

# 1. KONFIGURASI HALAMAN UTAMA WEB
st.set_page_config(page_title="🔒 Secure Private Journal", layout="wide", initial_sidebar_state="expanded")

# --- FITUR KONTROL AKSES: HALAMAN LOGIN MULTI-USER ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Nama File Database Lokal Permanen di Server Streamlit Cloud
FILE_DB = "database_jurnal.csv"

def login():
    st.title("🔒 Nata Mind Trading Journal - Gateway")
    st.markdown("Selamat datang! Silakan login sebagai Pemilik untuk mengisi data riwayat, atau gunakan Akun Tamu untuk mencoba fitur simulasi sampel.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("🚀 Log In Pemilik (Admin)", use_container_width=True):
            if username == "trader123" and password == "rahasia2026":
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.success("Akses Pemilik Diterima!")
                st.rerun()
            else:
                st.error("Username atau Password Admin salah!")
                
    with col_l2:
        if st.button("👥 Masuk Sebagai Tamu (Coba Sandbox)", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = "Guest"
            st.rerun()

    st.markdown("---")
    st.header("✨ Fitur Unggulan Nata Mind Trading Journal")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.info("📈 **Kurva Akumulasi Profit**\n\nMemetakan grafik pertumbuhan modal (Equity Curve) secara real-time.")
    with col_f2:
        st.warning("🧠 **Audit Psikologi Otomatis**\n\nMendeteksi emosi manual vs matematika pasar.")
    with col_f3:
        st.success("🛡️ **Manajemen Risiko Terunci**\n\nKalkulator Lot otomatis terintegrasi.")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- SINKRONISASI BASIS DATA FILE CSV PERMANEN ---
@st.cache_data(ttl="0d")
def muat_database_permanen():
    if os.path.exists(FILE_DB):
        try:
            df = pd.read_csv(FILE_DB)
            # Pastikan tipe data Tanggal seragam
            df['Tanggal'] = df['Tanggal'].astype(str)
            return df
        except Exception:
            pass
    # Jika file belum ada, buat struktur tabel baru kosong
    return pd.DataFrame(columns=[
        'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
        'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
    ])

# Inisialisasi penyimpanan sesi aplikasi
if 'jurnal_data' not in st.session_state or st.session_state.jurnal_data is None:
    if st.session_state.user_role == "Admin":
        st.session_state.jurnal_data = muat_database_permanen()
    else:
        st.session_state.jurnal_guest_db = pd.DataFrame(columns=[
            'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
            'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
        ])

# Penentuan alur tabel data aktif berdasarkan hak login
if st.session_state.user_role == "Admin":
    df_active = st.session_state.jurnal_data
    role_text = "🔑 AKUN PEMILIK (ADMIN)"
    caption_text = "Status Keamanan: Akses Penuh Pemilik. Data tersimpan permanen di cloud server pribadi Anda."
else:
    df_active = st.session_state.jurnal_guest_db
    role_text = "👥 AKUN TAMU (GUEST MODE)"
    caption_text = "Status: Mode Sandbox Sampel. Anda bisa mencoba input, data akan terhapus jika browser di-refresh."

# TOMBOL LOGOUT AMAN DI SIDEBAR KIRI
st.sidebar.markdown(f"### Status Sesi:\n**{role_text}**")
if st.sidebar.button("🔒 Log Out / Kunci Jurnal", type="primary", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.jurnal_data = None
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

max_risk_idr = modal_idr * (persen_risiko / 100)
max_risk_usd = modal_usd * (persen_risiko / 100)
st.sidebar.info(f"💡 **Batas Toleransi Los Maksimal:**\n* Saham: Rp {max_risk_idr:,.0f}\n* Forex: ${max_risk_usd:,.2f}")

# FORMULIR INPUT REKAP TRANSAKSI
st.header("📝 Catat Riwayat Transaksi")

with st.form("form_dual_mode", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", value=datetime.date.today())
        jam_entry = st.time_input("Jam Masuk Posisi", value=datetime.time(0, 0))
        pilihan_broker_standar = ["Stockbit IDR", "Ajaib IDR", "Gotrade USD", "Exness USD", "XM Forex USD", "Lainnya (Ketik Manual)..."]
        broker_pilih = st.selectbox("Platform / Broker", pilihan_broker_standar)
        if broker_pilih == "Lainnya (Ketik Manual)...":
            broker = st.text_input("Ketik Nama Broker Anda").strip()
        else:
            broker = broker_pilih
            
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
    emosi_manual = st.selectbox("🧠 Apa strategi atau emosi yang Anda rasakan saat membuka posisi ini?", 
                                ["Disiplin Plan", "FOMO / Terburu-buru", "Revenge Trading", "Breakout Setup", "Buy on Weakness"])

    submit = st.form_submit_button("⚡ Simpan & Jalankan Audit Sistem")

# --- PROSES EKSEKUSI DATA KETIKA TOMBOL SUBMIT DIKLIK ---
if submit and simbol and ukuran > 0:
    multiplier = 1 if tipe == "BUY" else -1
    
    if "USD" in broker.upper() or "FOREX" in broker.upper():
        pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
    else:
        # Saham Indonesia (1 Lot = 100 Lembar)
        pnl = (harga_keluar - harga_masuk) * (ukuran * 100) * multiplier
        
    status_aktif = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
    
    if emosi_manual != "Disiplin Plan":
        audit_komparasi = f"⚠️ Emosi Terdeteksi: {emosi_manual}"
        deteksi_otomatis = "Impulsif Berisiko"
    else:
        audit_komparasi = "✅ Sesuai Trading Plan"
        deteksi_otomatis = "Sesuai Aturan"

    new_row = pd.DataFrame([{
        'Tanggal': str(tanggal),
        'Jam_Entry': str(jam_entry),
        'Aset / Broker': broker if broker else "General Broker",
        'Simbol': simbol,
        'Tipe': tipe,
        'Harga Masuk': float(harga_masuk),
        'Harga Keluar': float(harga_keluar),
        'Rencana_SL': float(r_sl),
        'Rencana_TP': float(r_tp),
        'Ukuran': float(ukuran),
        'Net PnL': float(pnl),
        'Emosi_Pilihan_Manual': emosi_manual,
        'Deteksi_Otomatis_Sistem': deteksi_otomatis,
        'Audit_Komparasi': audit_komparasi,
        'Status': status_aktif
    }])
    
    if st.session_state.user_role == "Admin":
        # Gabungkan baris data baru ke database aktif pemilik
        st.session_state.jurnal_data = pd.concat([st.session_state.jurnal_data, new_row], ignore_index=True)
        # Amankan secara permanen ke file CSV penyimpanan awan
        st.session_state.jurnal_data.to_csv(FILE_DB, index=False)
        st.success("🔥 Data sukses disimpan permanen ke Database CSV Jurnal Pemilik!")
        df_active = st.session_state.jurnal_data
    else:
        st.session_state.jurnal_guest_db = pd.concat([st.session_state.jurnal_guest_db, new_row], ignore_index=True)
        df_active = st.session_state.jurnal_guest_db
        st.success("⚡ Data masuk ke Sandbox Tamu (Sesi Sementara)!")
        
    st.rerun()

# --- 📊 BAGIAN DASHBOARD GRAFIK KINERJA (EQUITY CURVE) ---
st.header("📊 Analisis Performa & Grafik Modal")

if df_active is not None and not df_active.empty:
    df_active['Net PnL'] = pd.to_numeric(df_active['Net PnL'], errors='coerce').fillna(0)
    df_active['Kumulatif_Profit'] = df_active['Net PnL'].cumsum()
    
    # 1. Grafik Kurva Akumulasi Pertumbuhan Modal
    st.line_chart(df_active, x='Tanggal', y='Kumulatif_Profit', use_container_width=True)
    
    # 2. Grafik Audit Psikologi Terintegrasi (Distribusi Diagram Batang)
    st.markdown("### 🧠 Audit Distribusi Kontrol Emosi & Psikologi")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write("**Emosi Pilihan Manual Anda:**")
        emosi_manual_counts = df_active['Emosi_Pilihan_Manual'].value_counts()
        st.bar_chart(emosi_manual_counts, use_container_width=True)
    with col_g2:
        st.write("**Hasil Analisis Deteksi Otomatis Sistem:**")
