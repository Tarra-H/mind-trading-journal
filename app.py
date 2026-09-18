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
    st.header("✨ Fitur Utama Nata Mind Trading Journal")
    st.info("📈 **Kurva Akumulasi Profit:** Memetakan grafik pertumbuhan modal (Equity Curve) secara real-time.")
    st.warning("🧠 **Audit Psikologi Otomatis:** Mendeteksi dan membandingkan emosi manual Anda dengan matematika pasar.")
    st.success("🛡️ **Manajemen Risiko Terunci:** Kalkulator Lot otomatis terintegrasi berdasarkan batas toleransi kerugian.")

# Jika belum login, stop aplikasi dan tampilkan halaman login
if not st.session_state.authenticated:
    login()
    st.stop()

# --- SUNTIKAN KREDENSIAL JSON ASLI (ANTI-BENTROK FORMAT TOML SECARA ABSOLUT) ---
kredensial_json = {
  "type": "service_account",
  "project_id": "nata-trading-journal",
  "private_key_id": "14d9a91d1035ea3908c102506a054e28bc8e7769",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCWnR/m5qrnIOU8\ngpIPzHo4YwZMiH/dn9/iLB7gqppocwesn8rXLIsVosxSYHG01ctfozlVEeqBCbKH\nrgVuJbGzFbTUb5x9XemaOfldPRxRqycDn3ogpjD0NTCncp8WGkvYWYKKL6zDSctW\nt6lhZq3cblg7MA6ehiy8CDIuXLhQfrPKJxNmIFkNIu3mfj0Scwi0t78T5G5MC3f2\ngOP3LCFHwavtr+NGc+ldPTHDQNCjp4WDr5PV87i/bJ5gompw7kduF57wn99XMBKC\nQboi43qoVXb0K3lSHuHLYLZKg7WBYQ6X+dvptypLgD/tv98BXUecOd+MMcFoDv7M\nmjjLUUl5AgMBAAECggEAEw05Fdoj0CzHEopps3noE+3ixBeYJQ6uIUv3c+/grEmw\ntNNZszI9PbVkJx9wArHwkd5xyCMGCOCTJrqKkU5PVhnuz9h2cR1KCWo/8t1iEaqW\nusyXhD3Bf4Ki7ut+2CrnYSyhaJ1zOxjAke2VjW6Rm4qRuprvnnnWesqGnnq4DeZn\nZgD824Y9aXfpFiZvlRdeaFr169mGtKx5jWTFJ/oMKJ37JDYOXWMKUzS/yUmVzoNs\nCxcwKRhNq4jYXXchqpbyyrSwtxO7HBIpFS+lx7mPvKs+bzY1H0Sil8dXQWDSxrQT\n1d6aMvCg4zX6kRhj9ei6TQLvX5HXhS099dXkq3ICSQKBgQDFx0KkOOyyIVXwl7YP\nvCe4k+vk0dz6dqXVrWcZy2VA8UV989UGYOl7AFx35EvIL53rRrr1RYZpXfi3gaSl\nw947yjDdG8UeCPmO6A+RjKZm0o719XlX0sRikUDNsN3SPsh7swGIPaOsuXiDrGb2\nN05gfowjvB7nWqPdUqvbYfYYiwKBgQDC84B6Zrqx3KDf+CVSOR0RwgMumUC/6sqr\nD0hHZkoNhscqQ68uEWjXiNGQXcWwsAgKkNnWkqLVWHtBKAIuHGYo3SuD5GeQlQOG\nhni4wb0f/rFY9airzAGwUHv2aZhrRdfM85gKAVe97jZ+1N16WeDyLeI3/7c576BF\nopMQ+L6iiwKBgQCu+cwmuEoIil+a/M3Q+/j0XsIbbeQgHuo2sjP96SnKm+qMNTX\npnb8IA1V/5nhvBnwcKyUfMiVcST1YlG+iL008A/K/gXpo1KWGIohxr+9CYNX7Pcf6J\nyWl/ftyjXe/R+0Op1MPtQgNVY72QWO26tVF9I1heoSeCLXm97E8pR3DPYwKBgCGY\nkQWG+pl4Kgku3E+lJAtRYfb/1ha8wZxlD9GuIQjftybjbycDPQwXufWlE1J1o40e\nlUvTDViy3NrHqEiGAFz+cGdUTzytUWQ3fEpqqMsAu1NXUm/4wjm+RP6cB/ZEnQHm\n4MaooJRMnvuQd3KEVq2llpyL5umHEBmwAKQmGcQtAoGATkn0s/K0fUCX7M5cH5cN\n2nm01NiLClxUEkFrzsVeeZWtaeC1Vycs3qZeJ/P0NgBmso4MmladFGUSwTiADmT3\nxgs7ycIMhgpk/ZnoaALioglnIMi0F+iteQvdLKrG7CwPdr7mCKArHhtB5YAjo5hC\nAbF3PqYA4IJXcMk61VY6T28=\n-----END PRIVATE KEY-----\n",
  "client_email": "natajurnal-bot@://gserviceaccount.com",
  "client_id": "107675104282005081162",
  "auth_uri": "https://google.com",
  "token_uri": "https://googleapis.com",
  "auth_provider_x509_cert_url": "https://googleapis.com",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/natajurnal-bot%40://gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# --- CONNECT TO GOOGLE SHEETS DATABASE ---
try:
    # Membaca link langsung dari brankas Secrets khusus link URL saja
    url_spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection, **kredensial_json)
    df_gsheets = conn.read(spreadsheet=url_spreadsheet, ttl="0d")
    df_gsheets = df_gsheets.dropna(how="all")
except Exception as e:
    df_gsheets = pd.DataFrame(columns=['Tanggal', 'Jam_Entry', 'Aset / Broker', 'Simbol', 'Tipe', 'Harga Masuk', 'Harga Keluar', 'Rencana_SL', 'Rencana_TP', 'Ukuran', 'Net PnL', 'Emosi_Pilihan_Manual', 'Deteksi_Otomatis_Sistem', 'Audit_Komparasi', 'Status'])

# Mode Pemisahan Sesi
if st.session_state.user_role == "Admin":
    df_active = df_gsheets
    role_text = "🔑 AKUN PEMILIK (ADMIN)"
    caption_text = "Status Keamanan: Koneksi Enkripsi GSheets Aktif. Data tersimpan otomatis di Google Drive Anda."
else:
    if 'jurnal_guest' not in st.session_state:
        st.session_state.jurnal_guest = df_gsheets.copy()
    df_active = st.session_state.jurnal_guest
    role_text = "👥 AKUN TAMU (GUEST MODE)"
    caption_text = "Status: Mode Sandbox Sampel. Pengunjung bisa mencoba input, namun data tidak akan masuk ke Google Sheets Anda."

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
        pilihan_broker_standar = ["Stockbit IDR", "Ajaib IDR", "Gotrade USD", "Exness USD", "XM Forex USD", "Lainnya (Ketik Manual)..."]
        broker_pilih = st.selectbox("Platform / Broker", pilihan_broker_standar)
        if broker_pilih == "Lainnya (Ketik Manual)...":
            broker = st.text_input("Ketik Nama Broker Anda (Contoh: Indo Premier IDR, Binance USD)").strip()
        else:
            broker = broker_pilih
            
    with col2:
        simbol = st.text_input("Simbol / Kode Aset (Misal: BBRI / AAPL / XAUUSD)").upper()
        tipe = st.selectbox("Arah Posisi", ["BUY", "SELL"])
        ukuran = st.number_input("Jumlah Ukuran (Lot / Volume Forex)", min_value=0.0, step=1.0, format="%f", value=0.0)
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
        
        if "USD" in broker.upper() or "FOREX" in broker.upper():
            pnl = (harga_keluar - harga_masuk) * ukuran * 100 * multiplier if "XAU" in simbol else (harga_keluar - harga_masuk) * ukuran * 100000 * multiplier
        elif "IDR" in broker.upper() or "STOCKBIT" in broker.upper() or "AJAIB" in broker.upper():
            pnl = (harga_keluar - harga_masuk) * (ukuran * 100) * multiplier
        else:
            pnl = (harga_keluar - harga_masuk) * ukuran * multiplier
            
        status = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        deteksi_otomatis = "Disiplin Plan"
        if r_sl == 0 and r_tp == 0:
            deteksi_otomatis = "FOMO / Terburu-buru"
            
        audit_komparasi = "✅ Sinkron (Anda Paham Diri Anda)"
        if emosi_manual != deteksi_otomatis:
            audit_komparasi = "⚠️ Denial (Penyangkalan Diri)"

        new_row = pd.DataFrame([{
            'Tanggal': str(tanggal), 'Jam_Entry': str(jam_entry), 'Aset / Broker': broker if broker else "General Broker", 'Simbol': simbol, 
