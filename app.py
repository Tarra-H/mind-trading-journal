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
FILE_DB = "database_jurnal_v2.csv"

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

if st.session_state.user_role == "Admin":
    df_dashboard = st.session_state.jurnal_data
else:
    df_dashboard = st.session_state.jurnal_guest_db

if df_dashboard is not None and not df_dashboard.empty:
    # Memastikan kolom Net PnL terbaca sebagai angka bersih
    df_dashboard['Net PnL'] = pd.to_numeric(df_dashboard['Net PnL'], errors='coerce').fillna(0)
    
    # -----------------------------------------------------------------
    # 📅 FITUR EKSTRAKSI & FILTER PER BULAN & TAHUN
    # -----------------------------------------------------------------
    # Mengonversi kolom Tanggal ke format datetime untuk ekstraksi bulan/tahun
    df_dashboard['Datetime_Obj'] = pd.to_datetime(df_dashboard['Tanggal'], errors='coerce')
    
    # Buat kolom label pengelompokan (Contoh: "2026 - September")
    df_dashboard['Bulan_Tahun'] = df_dashboard['Datetime_Obj'].dt.strftime('%Y - %B')
    # Mengisi baris kosong jika ada tanggal tidak valid
    df_dashboard['Bulan_Tahun'] = df_dashboard['Bulan_Tahun'].fillna("Format Tanggal Salah")
    
    # Ambil daftar unik kelompok bulan & tahun untuk dijadikan pilihan drop-down
    list_kelompok = ["Semua Data"] + sorted(list(df_dashboard['Bulan_Tahun'].unique()))
    
    st.markdown("### 📅 Filter Kategori Riwayat Waktu")
    kategori_pilih = st.selectbox("Pilih Kelompok Bulan & Tahun yang Ingin Dilihat:", list_kelompok)
    
    # Menyaring data berdasarkan kategori yang dipilih pengguna
    if kategori_pilih != "Semua Data":
        df_filtered = df_dashboard[df_dashboard['Bulan_Tahun'] == kategori_pilih].copy()
    else:
        df_filtered = df_dashboard.copy()
        
    # Perhitungan ulang akumulasi profit khusus untuk data yang lolos filter
    df_filtered['Kumulatif_Profit'] = df_filtered['Net PnL'].cumsum()
    
    # 1. Tampilkan Grafik Garis Pertumbuhan Modal
    st.line_chart(df_filtered, x='Tanggal', y='Kumulatif_Profit', use_container_width=True)
    
    # 2. Tampilkan Grafik Audit Psikologi (Distribusi Kontrol Emosi)
    st.markdown("### 🧠 Audit Distribusi Kontrol Emosi & Psikologi")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write("**Emosi Pilihan Manual Anda:**")
        emosi_manual_counts = df_filtered['Emosi_Pilihan_Manual'].value_counts()
        st.bar_chart(emosi_manual_counts, use_container_width=True)
            
    with col_g2:
        st.write("**Hasil Analisis Deteksi Otomatis Sistem:**")
        sistem_counts = df_filtered['Deteksi_Otomatis_Sistem'].value_counts()
        st.bar_chart(sistem_counts, use_container_width=True)

    # -----------------------------------------------------------------
    # 📝 TABEL RIWAYAT INTERAKTIF (EDIT SEPERTI EXCEL & HAPUS TOMBOL)
    # -----------------------------------------------------------------
    st.markdown("### 📝 Log Riwayat Tabel Jurnal Transaksi")
    st.caption("💡 **Tips Premium:** Klik 2x pada kotak sel mana saja (Simbol, Lot, Harga) untuk mengedit typo langsung. Centang kotak kolom paling kanan lalu tekan tombol Hapus di bawah untuk mendelete baris.")
    
    # Menyiapkan DataFrame untuk tampilan tabel interaktif
    df_tampilan = df_filtered.copy()
    
    # Hapus kolom pembantu agar tidak mengotori tabel utama trader
    if 'Datetime_Obj' in df_tampilan.columns: df_tampilan = df_tampilan.drop(columns=['Datetime_Obj'])
    if 'Bulan_Tahun' in df_tampilan.columns: df_tampilan = df_tampilan.drop(columns=['Bulan_Tahun'])
    if 'Kumulatif_Profit' in df_tampilan.columns: df_tampilan = df_tampilan.drop(columns=['Kumulatif_Profit'])
    
    # Mengubah penomoran awal indeks tabel agar dimulai dari Angka 1 (Bukan 0)
    df_tampilan.index = range(1, len(df_tampilan) + 1)
    
    # Menambahkan kolom centang khusus untuk fitur hapus baris massal
    df_tampilan["Pilih Hapus"] = False
    
    # Menampilkan tabel editor interaktif super canggih
    edited_df = st.data_editor(
        df_tampilan, 
        use_container_width=True,
        num_rows="dynamic"  # Mengaktifkan tombol pensil/tambah/hapus baris bawaan
    )
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # TOMBOL 1: SIMPAN PERUBAHAN EDIT LANGSUNG (PENSIL KOREKSI)
        if st.button("💾 Simpan Semua Koreksi / Perubahan Edit Sel", use_container_width=True, type="primary"):
            # Mengembalikan indeks penomoran ke data dasar asli untuk kalkulasi mesin
            df_save = edited_df.copy()
            df_save = df_save.drop(columns=["Pilih Hapus"])
            
            # Menghitung ulang Net PnL secara otomatis jika pengguna mengedit harga/ukuran
            for idx in df_save.index:
                m_type = 1 if df_save.loc[idx, 'Tipe'] == "BUY" else -1
                h_masuk = float(df_save.loc[idx, 'Harga Masuk'])
                h_keluar = float(df_save.loc[idx, 'Harga Keluar'])
                vol = float(df_save.loc[idx, 'Ukuran'])
                brk = str(df_save.loc[idx, 'Aset / Broker']).upper()
                smb = str(df_save.loc[idx, 'Simbol']).upper()
                
                if "USD" in brk or "FOREX" in brk:
                    res_pnl = (h_keluar - h_masuk) * vol * 100 * m_type if "XAU" in smb else (h_keluar - h_masuk) * vol * 100000 * m_type
                else:
                    res_pnl = (h_keluar - h_masuk) * (vol * 100) * m_type
                
                df_save.loc[idx, 'Net PnL'] = res_pnl
                df_save.loc[idx, 'Status'] = "WIN" if res_pnl > 0 else "LOSS" if res_pnl < 0 else "BREAKEVEN"
            
            # Terapkan perubahan ke database utama
            if st.session_state.user_role == "Admin":
                st.session_state.jurnal_data = df_save.reset_index(drop=True)
                st.session_state.jurnal_data.to_csv(FILE_DB, index=False)
            else:
                st.session_state.jurnal_guest_db = df_save.reset_index(drop=True)
                
            st.success("✅ Semua koreksi salah ketik berhasil diperbarui ke database!")
            st.rerun()
            
    with col_btn2:
        # TOMBOL 2: HAPUS BARIS YANG DICENTANG PERMANEN
        if st.button("🗑️ Hapus Semua Baris Transaksi yang Dicentang", use_container_width=True):
            # Mencari baris mana saja yang diberi centang TRUE oleh pengguna
            indeks_tercentang = edited_df[edited_df["Pilih Hapus"] == True].index
            
            if len(indeks_tercentang) > 0:
                # Sesuaikan indeks tampilan (mulai dari 1) kembali ke indeks list Python asli (mulai dari 0)
                indeks_asli_hapus = [i - 1 for i in indeks_tercentang]
                
                if st.session_state.user_role == "Admin":
                    st.session_state.jurnal_data = st.session_state.jurnal_data.drop(indeks_asli_hapus).reset_index(drop=True)
                    st.session_state.jurnal_data.to_csv(FILE_DB, index=False)
                else:
                    st.session_state.jurnal_guest_db = st.session_state.jurnal_guest_db.drop(indeks_asli_hapus).reset_index(drop=True)
                    
                st.success("🗑️ Baris transaksi terpilih berhasil dihapus!")
                st.rerun()
            else:
                st.error("Silakan centang kolom 'Pilih Hapus' pada tabel di atas terlebih dahulu!")

    # -----------------------------------------------------------------
    # 📥 EKSPOR UNDUH DATABASE
    # -----------------------------------------------------------------
    st.markdown("---")
    csv_excel = df_filtered.to_csv(index=False, sep=";")
    st.download_button(
        label="📥 Ekspor Riwayat Kategori Waktu Ini ke Excel (.csv)",
        data=csv_excel,
        file_name=f"Nata_Jurnal_{kategori_pilih.replace(' ', '')}_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("ℹ️ Belum ada data transaksi yang tersimpan. Grafik kurva pertumbuhan modal serta kategori bulanan akan muncul di sini setelah Anda memasukkan data pertama.")
