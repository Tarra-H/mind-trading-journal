import streamlit as st
import pandas as pd
import datetime

# 1. KONFIGURASI HALAMAN UTAMA WEB
st.set_page_config(page_title="🔒 Secure Private Journal", layout="wide", initial_sidebar_state="expanded")

# --- FITUR KONTROL AKSES: HALAMAN LOGIN AMAN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔒 Private Access Control")
    st.markdown("Aplikasi ini dilindungi. Silakan masukkan kredensial untuk membuka jurnal.")
    
    # SILAKAN GANTI USERNAME DAN PASSWORD SESUAI KEINGINAN ANDA DI BAWAH INI
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        if username == "trader123" and password == "rahasia2026":
            st.session_state.authenticated = True
            st.success("Akses diterima! Memuat data...")
            st.rerun()
        else:
            st.error("Username atau Password salah! Akses ditolak.")

# Jika belum login, stop aplikasi dan tampilkan halaman login saja
if not st.session_state.authenticated:
    login()
    st.stop()

# --- [BATAS KODE LOGIN] JIKA BERHASIL LOGIN, SEMUA KODE DI BAWAH INI BARU TERBUKA ---

# Inisialisasi database privat di memori lokal browser (Session State)
if 'jurnal' not in st.session_state:
    st.session_state.jurnal = pd.DataFrame(columns=[
        'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
        'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
    ])

# TOMBOL LOGOUT AMAN DI SIDEBAR KIRI (BARU)
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Log Out / Kunci Jurnal", type="primary"):
    st.session_state.authenticated = False
    st.rerun()
st.sidebar.markdown("---")

st.title("🧠 Nata Mind Trading Journal & Visual Audit")
st.caption("Sistem Jurnal Fleksibel: Menggunakan Input Manual Saat Ini, Siap untuk Deteksi Otomatis Masa Depan Tanpa Saling Mengganggu")
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
        broker = st.selectbox("Platform / Broker", ["Stockbit (Saham IDR)", "Gotrade (Saham USD)", "Exness MT5 (Forex USD)"])
    with col2:
        simbol = st.text_input("Simbol / Kode Aset (Misal: BBRI / XAUUSD)").upper()
        tipe = st.selectbox("Arah Posisi", ["BUY", "SELL"])
        ukuran = st.number_input("Jumlah Ukuran (Lot / Lembar Saham)", min_value=0.0, format="%.2f")
    with col3:
        harga_masuk = st.number_input("Harga Masuk (Rata-rata)", min_value=0.0, format="%.5f")
        harga_keluar = st.number_input("Harga Keluar (Rata-rata)", min_value=0.0, format="%.5f")
        r_sl = st.number_input("Rencana Stop Loss (Isi 0 jika tidak ada plan)", min_value=0.0, format="%.5f")
        r_tp = st.number_input("Rencana Take Profit (Isi 0 jika tidak ada plan)", min_value=0.0, format="%.5f")
        
    st.markdown("---")
    emosi_manual = st.selectbox("🧠 Apa strategi atau emosi yang Anda rasakan saat membuka posisi ini?", 
                                ["Disiplin Plan", "FOMO / Terburu-buru", "Revenge Trading", "Breakout Setup", "Buy on Weakness"])

    submit = st.form_submit_button("⚡ Simpan & Jalankan Audit Sistem")

    if submit and simbol and ukuran > 0:
        multiplier = 1 if tipe == "BUY" else -1
        if "Exness" in broker:
            pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
        else:
            pnl = (harga_keluar - harga_masuk) * ukuran * multiplier
            
        status = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        
        deteksi_otomatis = "Belum Terbaca (Butuh Data Presisi)"
        df_hist = st.session_state.jurnal
        
        if jam_entry != datetime.time(0, 0):
            if (status == "LOSS" or (not df_hist.empty and df_hist.iloc[-1]['Status'] == "LOSS")) and not df_hist.empty:
                waktu_lalu = datetime.datetime.combine(df_hist.iloc[-1]['Tanggal'], df_hist.iloc[-1]['Jam_Entry'])
                waktu_kini = datetime.datetime.combine(tanggal, jam_entry)
                selisih_menit = abs((waktu_kini - waktu_lalu).total_seconds() / 60)
                if selisih_menit <= 30 and df_hist.iloc[-1]['Aset / Broker'] == broker:
                    deteksi_otomatis = "Revenge Trading"
            
            if r_sl == 0 and r_tp == 0:
                deteksi_otomatis = "FOMO / Terburu-buru"
            elif deteksi_otomatis == "Belum Terbaca (Butuh Data Presisi)":
                deteksi_otomatis = "Disiplin Plan"
        
        if deteksi_otomatis == "Belum Terbaca (Butuh Data Presisi)":
            audit_komparasi = "ℹ️ Mode Manual Aktif (Otomatis Off)"
        elif emosi_manual == deteksi_otomatis:
            audit_komparasi = "✅ Sinkron (Anda Paham Diri Anda)"
        elif emosi_manual == "Disiplin Plan" and deteksi_otomatis in ["Revenge Trading", "FOMO / Terburu-buru"]:
            audit_komparasi = "⚠️ Denial (Penyangkalan Diri)"
        else:
            audit_komparasi = "🧠 Evaluasi Mandiri"

        new_row = {
            'Tanggal': tanggal, 'Jam_Entry': jam_entry, 'Aset / Broker': broker, 'Simbol': simbol, 
            'Tipe': tipe, 'Harga Masuk': harga_masuk, 'Harga Keluar': harga_keluar, 'Rencana_SL': r_sl, 
            'Rencana_TP': r_tp, 'Ukuran': ukuran, 'Net PnL': pnl, 'Emosi_Pilihan_Manual': emosi_manual, 
            'Deteksi_Otomatis_Sistem': deteksi_otomatis, 'Audit_Komparasi': audit_komparasi, 'Status': status
        }
        st.session_state.jurnal = pd.concat([st.session_state.jurnal, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"Transaksi {simbol} berhasil disimpan!")

st.markdown("---")

# 5. DASHBOARD UTAMA VISUALISASI DATA
st.header("📊 Dashboard Analisis & Komparasi Emosi Trading")
df = st.session_state.jurnal

if not df.empty:
    st.subheader("📈 Kurva Pertumbuhan Modal Kumulatif (Equity Curve)")
    df_grafik = df.copy()
    df_grafik['Kumulatif PnL'] = df_grafik['Net PnL'].cumsum()
    st.line_chart(df_grafik, x='Tanggal', y='Kumulatif PnL', use_container_width=True)
    
    st.markdown("### 🔍 Komparasi Visual: Pilihan Manual Anda vs Deteksi Otomatis Robot")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**1. Distribusi Emosi / Strategi Pilihan Manual Anda (Aktif):**")
        st.bar_chart(df['Emosi_Pilihan_Manual'].value_counts())
    with col_chart2:
        st.markdown("**2. Hasil Audit Tingkat Kesadaran Mental (Komparasi):**")
        st.bar_chart(df['Audit_Komparasi'].value_counts())
        
    st.subheader("📜 Buku Riwayat Log Jurnal & Audit Gabungan")
    st.dataframe(df[['Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi']], use_container_width=True)
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Backup Data Jurnal ke Excel/CSV", data=csv_data, file_name="private_trading_journal.csv", mime="text/csv")
    with col_btn2:
        if st.button("🗑️ Reset / Hapus Semua Data", type="primary"):
            st.session_state.jurnal = pd.DataFrame(columns=[
                'Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 
                'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'
            ])
            st.rerun()
else:
    st.info("Buku jurnal privat Anda masih kosong. Masukkan data rekap Anda di atas.")
