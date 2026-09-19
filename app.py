import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

# 1. KONFIGURASI HALAMAN UTAMA WEB
st.set_page_config(page_title="🔒 Secure Private Journal", layout="wide", initial_sidebar_state="expanded")

# --- FITUR KONTROL AKSES: HALAMAN LOGIN MULTI-USER ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Inisialisasi penyimpanan lokal yang aman di memori aplikasi agar data tidak hilang saat rerun
if 'jurnal_data' not in st.session_state:
    st.session_state.jurnal_data = None

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
    st.markdown("Sistem asisten pintar ini dirancang untuk mendeteksi kesehatan psikologi dan performa trading Anda secara otomatis:")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.info("📈 **Kurva Akumulasi Profit**\n\nMemetakan grafik pertumbuhan modal (Equity Curve) secara real-time dari gabungan portofolio saham maupun forex Anda.")
    with col_f2:
        st.warning("🧠 **Audit Psikologi Otomatis**\n\nMendeteksi dan membandingkan emosi manual Anda dengan matematika pasar untuk menangkap gejala FOMO atau Revenge Trading.")
    with col_f3:
        st.success("🛡️ **Manajemen Risiko Terunci**\n\nKalkulator Lot otomatis terintegrasi di dalam sistem berdasarkan batas toleransi kerugian modal Anda.")

# Jika belum login, stop aplikasi dan tampilkan halaman login
if not st.session_state.authenticated:
    login()
    st.stop()

# --- INSTANSIASI KONEKSI DATABASE PERMANEN ---
if st.session_state.jurnal_data is None:
    if st.session_state.user_role == "Admin":
        try:
            url_spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_load = conn.read(spreadsheet=url_spreadsheet, ttl="0d")
            st.session_state.jurnal_data = df_load.dropna(how="all")
        except Exception as e:
            st.sidebar.error(f"⚠️ Gagal load GSheets, memakai basis data lokal: {e}")
            st.session_state.jurnal_data = pd.DataFrame(columns=[
                'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
                'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
            ])
    else:
        st.session_state.jurnal_data = pd.DataFrame(columns=[
            'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
            'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
        ])

df_active = st.session_state.jurnal_data

if st.session_state.user_role == "Admin":
    role_text = "🔑 AKUN PEMILIK (ADMIN)"
    caption_text = "Status Keamanan: Akses Penuh. Data tersimpan otomatis di Google Drive GSheets Anda."
else:
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

# SIDEBAR: MONEY MANAGEMENT & KALKULATOR LOT
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
        jam_entry = st.time_input("Jam Masuk Posisi (Isi seadanya jika malas/ribet)", value=datetime.time(0, 0))
        pilihan_broker_standar = ["Stockbit IDR", "Ajaib IDR", "Gotrade USD", "Exness USD", "XM Forex USD", "Lainnya (Ketik Manual)..."]
        broker_pilih = st.selectbox("Platform / Broker", pilihan_broker_standar)
        
        if broker_pilih == "Lainnya (Ketik Manual)...":
            broker = st.text_input("Ketik Nama Broker Anda (Contoh: Indo Premier IDR, Binance USD)").strip()
        else:
            broker = broker_pilih
            
    with col2:
        simbol = st.text_input("Simbol / Kode Aset (Misal: BBRI / AAPL / XAUUSD)").upper()
        tipe = st.selectbox("Arah Posisi", ["BUY", "SELL"])
        ukuran = st.number_input("Jumlah Ukuran (Lot / Lembar Saham)", min_value=0.0, step=1.0, format="%f", value=0.0)
        
    with col3:
        harga_masuk = st.number_input("Harga Masuk (Rata-rata)", min_value=0.0, step=1.0, format="%f", value=0.0)
        harga_keluar = st.number_input("Harga Keluar (Rata-rata)", min_value=0.0, step=1.0, format="%f", value=0.0)
        r_sl = st.number_input("Rencana Stop Loss (Isi 0 jika tidak ada plan)", min_value=0.0, step=1.0, format="%f", value=0.0)
        r_tp = st.number_input("Rencana Take Profit (Isi 0 jika tidak ada plan)", min_value=0.0, step=1.0, format="%f", value=0.0)
        
    st.markdown("---")
    emosi_manual = st.selectbox("🧠 Apa strategi atau emosi yang Anda rasakan saat membuka posisi ini?", 
                                ["Disiplin Plan", "FOMO / Terburu-buru", "Revenge Trading", "Breakout Setup", "Buy on Weakness"])

    submit = st.form_submit_button("⚡ Simpan & Jalankan Audit Sistem")

# --- PROSES EKSEKUSI DATA KETIKA TOMBOL SUBMIT DIKLIK ---
if submit and simbol and ukuran > 0:
    multiplier = 1 if tipe == "BUY" else -1
    
    # Perhitungan PnL otomatis berdasarkan jenis broker dan aset
    if "USD" in broker.upper() or "FOREX" in broker.upper():
        pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
    else:
        # Saham Indonesia: Mengalikan dengan jumlah lembar riil (1 Lot = 100 lembar)
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
    
    # Kunci langsung ke memori lokal aktif aplikasi
    st.session_state.jurnal_data = pd.concat([st.session_state.jurnal_data, new_row], ignore_index=True)
    df_active = st.session_state.jurnal_data
    
    # Kirim cadangan ke Google Sheets di background jika login sebagai Admin
    if st.session_state.user_role == "Admin":
        try:
            url_spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(spreadsheet=url_spreadsheet, data=st.session_state.jurnal_data)
            st.success("🔥 Data sukses disimpan permanen ke Google Sheets Pemilik!")
        except Exception as e:
            st.warning(f"⚠️ Data tersimpan di aplikasi, namun gagal sinkron ke cloud Google Sheets: {e}")
    else:
        st.success("⚡ Data masuk ke Sandbox Tamu (Sesi Sementara)!")
        
    st.rerun()
# --- 📊 BAGIAN DASHBOARD GRAFIK KINERJA (EQUITY CURVE) ---
st.header("📊 Analisis Performa & Grafik Modal")

if df_active is not None and not df_active.empty:
    # Memastikan kolom Net PnL terbaca sebagai angka bersih
    df_active['Net PnL'] = pd.to_numeric(df_active['Net PnL'], errors='coerce').fillna(0)
    
    # Kalkulasi kurva akumulasi profit
    df_active['Kumulatif_Profit'] = df_active['Net PnL'].cumsum()
    
    # Tampilkan grafik garis performa portofolio
    st.line_chart(df_active, x='Tanggal', y='Kumulatif_Profit', use_container_width=True)
    
    # Tampilkan ringkasan tabel data log riwayat di bawahnya
    st.dataframe(df_active, use_container_width=True)
else:
    st.info("ℹ️ Belum ada data transaksi yang tersimpan. Grafik kurva pertumbuhan modal akan muncul di sini setelah Anda memasukkan data pertama.")
