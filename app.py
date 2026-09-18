import streamlit as st
import pandas as pd
import datetime

# 1. KONFIGURASI HALAMAN UTAMA WEB
st.set_page_config(page_title="🔒 Secure Private Journal", layout="wide", initial_sidebar_state="expanded")

# --- FITUR KONTROL AKSES: HALAMAN LOGIN MULTI-USER ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Inisialisasi database privat di memori lokal browser
if 'jurnal_admin' not in st.session_state:
    st.session_state.jurnal_admin = pd.DataFrame(columns=[
        'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
        'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
    ])

if 'jurnal_guest' not in st.session_state:
    st.session_state.jurnal_guest = pd.DataFrame(columns=[
        'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
        'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
    ])

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

    # --- Fitur Unggulan Teks Ringkas (Aman Tanpa Error) ---
    st.markdown("---")
    st.header("✨ Fitur Unggulan Nata Mind Trading Journal")
    st.info("📈 **Kurva Akumulasi Profit:** Memetakan grafik pertumbuhan modal (Equity Curve) secara real-time.")
    st.warning("🧠 **Audit Psikologi Otomatis:** Mendeteksi dan membandingkan emosi manual Anda dengan matematika pasar.")
    st.success("🛡️ **Manajemen Risiko Terunci:** Kalkulator Lot otomatis terintegrasi berdasarkan batas toleransi kerugian.")

# Jika belum login, stop aplikasi dan tampilkan halaman login
if not st.session_state.authenticated:
    login()
    st.stop()

# --- PILIHAN DATABASE BERDASARKAN ROLE LOGIN ---
if st.session_state.user_role == "Admin":
    df_active = st.session_state.jurnal_admin
    role_text = "🔑 AKUN PEMILIK (ADMIN)"
    caption_text = "Status Keamanan: Akses Penuh. Data tersimpan di database privat Anda."
else:
    df_active = st.session_state.jurnal_guest
    role_text = "👥 AKUN TAMU (GUEST MODE)"
    caption_text = "Status: Mode Sandbox Sampel. Anda bisa mencoba input, data akan terhapus jika browser di-refresh."

# TOMBOL LOGOUT AMAN DI SIDEBAR KIRI
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
        
        # OPSI COMBOBOX PREMIUM UNIVERSAL
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

    if submit and simbol and ukuran > 0:
        multiplier = 1 if tipe == "BUY" else -1
        
        # LOGIKA LINEAR SEDERHANA (100% BEBAS DARI ERROR ELSE SPASI)
        pnl = (harga_keluar - harga_masuk) * ukuran * multiplier
        if "USD" in broker.upper() or "FOREX" in broker.upper():
            pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
            
        status = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        deteksi_otomatis = "Disiplin Plan"
        
        if r_sl == 0 and r_tp == 0:
            deteksi_otomatis = "FOMO / Terburu-buru"
            
        audit_komparasi = "✅ Sinkron (Anda Paham Diri Anda)"
        if emosi_manual != deteksi_otomatis:
            audit_komparasi = "⚠️ Denial (Penyangkalan Diri)"

        new_row = {
            'Tanggal': tanggal, 'Jam_Entry': jam_entry, 'Aset / Broker': broker if broker else "General Broker", 'Simbol': simbol, 
            'Tipe': tipe, 'Harga Masuk': harga_masuk, 'Harga Keluar': harga_keluar, 'Rencana_SL': r_sl, 
            'Rencana_TP': r_tp, 'Ukuran': ukuran, 'Net PnL': pnl, 'Emosi_Pilihan_Manual': emosi_manual, 
            'Deteksi_Otomatis_Sistem': deteksi_otomatis, 'Audit_Komparasi': audit_komparasi, 'Status': status
        }
        
        if st.session_state.user_role == "Admin":
            st.session_state.jurnal_admin = pd.concat([st.session_state.jurnal_admin, pd.DataFrame([new_row])], ignore_index=True)
            df_active = st.session_state.jurnal_admin
        if st.session_state.user_role == "Guest":
            st.session_state.jurnal_guest = pd.concat([st.session_state.jurnal_guest, pd.DataFrame([new_row])], ignore_index=True)
            df_active = st.session_state.jurnal_guest
            
        st.success(f"Transaksi {simbol} berhasil disimpan!")
        st.rerun()

st.markdown("---")

# 5. DASHBOARD UTAMA VISUALISASI DATA
st.header("📊 Dashboard Analisis & Komparasi Emosi Trading")

if not df_active.empty:
    st.subheader("📈 Kurva Pertumbuhan Modal Kumulatif (Equity Curve)")
    df_grafik = df_active.copy()
    df_grafik['Kumulatif PnL'] = df_grafik['Net PnL'].cumsum()
    st.line_chart(df_grafik, x='Tanggal', y='Kumulatif PnL', use_container_width=True)
    
    st.markdown("### 🔍 Komparasi Visual: Pilihan Manual Anda vs Deteksi Otomatis Robot")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.bar_chart(df_active['Emosi_Pilihan_Manual'].value_counts())
    with col_chart2:
        st.bar_chart(df_active['Audit_Komparasi'].value_counts())
        
    st.subheader("📜 Buku Riwayat Log Jurnal & Pengeditan Data")
    edited_df = st.data_editor(df_active, num_rows="dynamic", use_container_width=True, key="jurnal_editor")
    
    if st.session_state.user_role == "Admin":
        st.session_state.jurnal_admin = edited_df
    if st.session_state.user_role == "Guest":
        st.session_state.jurnal_guest = edited_df
    
    st.markdown("---")
    csv_data = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download Backup Data Jurnal ke Excel/CSV", data=csv_data, file_name="trading_journal_export.csv", mime="text/csv", use_container_width=True)
else:
    st.info("Buku jurnal privat Anda masih kosong. Masukkan data rekap dengan angka di atas (Contoh: Saham BBRI, Jumlah 500, Entry 4000, Exit 4500) lalu klik simpan untuk mengaktifkan grafik kurva modal secara instan!")
