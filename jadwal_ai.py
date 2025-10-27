import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- Kumpulan Fungsi "Otak" AI v5.0 ---

def time_ke_menit(waktu_dt):
    """(Helper) Mengubah '09:00' menjadi 540 menit."""
    if waktu_dt is None:
        return 0
    return waktu_dt.hour * 60 + waktu_dt.minute

def menit_ke_time_str(total_menit):
    """(Helper) Mengubah 540 menit menjadi string '09:00'."""
    jam = (total_menit // 60) % 24
    menit = total_menit % 60
    return f"{jam:02d}:{menit:02d}"

def cari_celah_waktu(jadwal_harian, durasi_menit, search_range_list):
    """
    Inti "Otak AI" untuk meramal.
    Memindai 'jadwal_harian' (list 1440 menit) untuk menemukan celah kosong.
    """
    for start_menit in search_range_list:
        akhir_menit = start_menit + durasi_menit
        
        # Cek jika melewati tengah malam (untuk tidur)
        if akhir_menit > 1439: # 1439 = 23:59
            slot_satu = jadwal_harian[start_menit : 1440]
            slot_dua = jadwal_harian[0 : akhir_menit % 1440]
            slot_penuh = slot_satu + slot_dua
        else:
            slot_penuh = jadwal_harian[start_menit : akhir_menit]
            
        # Cek apakah seluruh slot 'False' (Kosong)
        if not any(slot_penuh): 
            return start_menit, akhir_menit
            
    return None, None # Gagal menemukan celah

def buat_grafik_timeline(df_plot):
    """
    FASILITAS BARU: Membuat Grafik Timeline 24 Jam dengan Plotly.
    """
    # Menambahkan 'dummy_date' karena plotly timeline butuh tanggal
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    df_plot['start_time'] = pd.to_datetime(df_plot['start_time'])
    df_plot['finish_time'] = pd.to_datetime(df_plot['finish_time'])
    
    # Menentukan urutan kategori di grafik
    category_order = ["Tidur 😴", "Makan 🍎", "Wajib 🔴", "Tugas 🟡", "Olahraga 🏃‍♀️", "Sosial 💚", "Hobi 💜"]
    
    fig = px.timeline(
        df_plot, 
        x_start="start_time", 
        x_end="finish_time", 
        y="Kategori",
        color="Kategori",
        title="Visualisasi Jadwal Harianmu",
        text="Aktivitas",
        category_orders={"Kategori": category_order} # Mengurutkan legenda
    )
    
    # Atur sumbu X agar HANYA menampilkan 24 jam (dari 00:00 hari ini s/d 00:00 besok)
    fig.update_xaxes(
        tickformat="%H:%M", 
        range_breaks=[dict(pattern="day of week")], # Sembunyikan label tanggal
        range=[
            datetime.datetime.strptime(f"{today_str} 00:00", "%Y-%m-%d %H:%M"),
            datetime.datetime.strptime(f"{today_str} 23:59", "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1)
        ]
    )
    
    fig.update_yaxes(visible=False) # Sembunyikan label "Kategori" di sumbu Y
    fig.update_layout(showlegend=True, legend_title_text='Tipe Aktivitas')
    
    return fig

# --- Inisialisasi State (Fasilitas) ---
if "hasil_disimpan" not in st.session_state:
    st.session_state.hasil_disimpan = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# --- Tampilan Aplikasi (Web App) v5.0 ---

st.set_page_config(page_title="AI Penjadwal Holistik", page_icon="💖", layout="wide")

# --- DESAIN 1: Personalisasi Sapaan ---
nama_user = st.text_input("Siapa nama panggilan Anda?", "Sayang")
st.title(f"💖 AI Penjadwal Holistik untuk {nama_user}")
st.caption("Sekarang dengan Analisis Psikologis & Grafik Timeline!")

# --- FASILITAS: Sidebar Pengaturan (dari v4.0) ---
st.sidebar.header("⚙️ Preferensi Idealmu")
pref_jam_mulai_tidur = st.sidebar.time_input("Jam ideal mulai tidur?", datetime.time(22, 0))
pref_durasi_tidur_jam = st.sidebar.number_input("Durasi tidur ideal (jam)?", 6.0, 10.0, 8.0, 0.5)
pref_durasi_makan_siang = st.sidebar.slider("Durasi makan siang ideal (menit)?", 30, 90, 60)
pref_min_aktivitas_jam = st.sidebar.slider("Batas minimum aktivitas sehat (jam)?", 2.0, 6.0, 4.0, 0.5)

# --- DESAIN 2: Tampilan Tabs ---
tab_input, tab_hasil = st.tabs(["🗓️ 1. Input Jadwal & Perasaan", "🧠 2. Lihat Hasil Analisis AI"])

with tab_input:
    st.subheader(f"Bagaimana perasaanmu hari ini, {nama_user}?")
    
    # --- INPUT BARU 1: DATA PSIKOLOGIS ---
    col1, col2 = st.columns(2)
    with col1:
        input_level_stres = st.slider("Level Stres-mu Hari Ini?", 1, 5, 3, help="1=Sangat Santai 😌, 5=Sangat Stres 🤯")
    with col2:
        input_level_energi = st.radio("Level Energi-mu Hari Ini?", ["Rendah 🔋", "Sedang ⚡", "Tinggi 🔥"], index=1)
    
    st.markdown("---")
    st.subheader("Masukkan semua aktivitas terstrukturmu:")
    
    # --- INPUT BARU 2: DATA KONTEKSTUAL (EDITOR DATA) ---
    # Ini menggantikan st.text_area yang lama
    
    # Siapkan data default untuk editor
    contoh_data = [
        {"Aktivitas": "Kelas Pagi", "Jam Mulai": "07:00", "Jam Selesai": "09:00", "Tipe": "Wajib 🔴"},
        {"Aktivitas": "Kelas Siang", "Jam Mulai": "10:00", "Jam Selesai": "12:00", "Tipe": "Wajib 🔴"},
        {"Aktivitas": "Persiapan Lomba", "Jam Mulai": "19:00", "Jam Selesai": "21:00", "Tipe": "Tugas 🟡"},
        {"Aktivitas": "Urusan Malam", "Jam Mulai": "23:00", "Jam Selesai": "00:00", "Tipe": "Wajib 🔴"},
    ]
    
    # Buat DataFrame dari data contoh
    df_input = pd.DataFrame(contoh_data)

    st.info("Gunakan tabel di bawah ini. Klik '➕' di baris terakhir untuk menambah jadwal baru.")
    
    # Tampilkan st.data_editor
    edited_df = st.data_editor(
        df_input,
        num_rows="dynamic", # Izinkan user menambah/menghapus baris
        column_config={
            "Aktivitas": st.column_config.TextColumn("Nama Aktivitas", required=True),
            "Jam Mulai": st.column_config.TextColumn("Mulai (HH:MM)", required=True),
            "Jam Selesai": st.column_config.TextColumn("Selesai (HH:MM)", required=True),
            "Tipe": st.column_config.SelectboxColumn(
                "Tipe Aktivitas",
                options=["Wajib 🔴", "Tugas 🟡", "Hobi 💜", "Sosial 💚", "Olahraga 🏃‍♀️"],
                required=True
            )
        },
        use_container_width=True,
        key="editor_jadwal"
    )

    if st.button("🔮 Ramalkan & Visualisasikan Jadwalku!", type="primary", use_container_width=True):
        st.session_state.show_results = True
        hasil = {}
        
        # --- PROSES BERPIKIR AI DIMULAI (v5.0) ---
        
        # 1. Inisialisasi Peta Rel 24 Jam & Daftar Plot Grafik
        jadwal_harian = [False] * 1440 
        daftar_plot_grafik = []
        
        # Tanggal hari ini (untuk plotly)
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        
        # 2. Proses Input dari st.data_editor
        total_beban_menit = 0
        ada_hobi_sosial = False
        tugas_fleksibel_gagal = []
        
        # Pisahkan tugas: Wajib harus di-plot dulu, sisanya fleksibel
        tugas_wajib = edited_df[edited_df['Tipe'] == 'Wajib 🔴']
        tugas_fleksibel = edited_df[edited_df['Tipe'] != 'Wajib 🔴']

        # --- Plot Aktivitas WAJIB 🔴 (Prioritas 0) ---
        for _, row in tugas_wajib.iterrows():
            try:
                mulai_dt = datetime.datetime.strptime(row['Jam Mulai'], '%H:%M').time()
                selesai_dt = datetime.datetime.strptime(row['Jam Selesai'], '%H:%M').time()
                mulai_menit = time_ke_menit(mulai_dt)
                selesai_menit = time_ke_menit(selesai_dt)
                
                durasi = 0
                if selesai_menit <= mulai_menit:
                    durasi = ((24*60) - mulai_menit) + selesai_menit
                    for m in range(mulai_menit, 1440): jadwal_harian[m] = True
                    for m in range(0, selesai_menit): jadwal_harian[m] = True
                else:
                    durasi = selesai_menit - mulai_menit
                    for m in range(mulai_menit, selesai_menit): jadwal_harian[m] = True
                
                total_beban_menit += durasi
                # Tambahkan ke daftar plot
                daftar_plot_grafik.append({
                    "Aktivitas": row['Aktivitas'], 
                    "start_time": f"{today_str} {row['Jam Mulai']}", 
                    "finish_time": f"{today_str} {row['Jam Selesai']}" if selesai_menit > mulai_menit else f"{today_str} {row['Jam Selesai']}" + " +1 day",
                    "Kategori": row['Tipe']
                })
            except Exception as e:
                st.error(f"Format jam salah di aktivitas '{row['Aktivitas']}': {e}")
        
        # 3. Jadwalkan Prioritas AI
        # Prioritas 1: Makan Siang (dari preferensi)
        durasi_makan = pref_durasi_makan_siang
        mulai_makan, selesai_makan = cari_celah_waktu(jadwal_harian, durasi_makan, list(range(720, 841)))
        
        if mulai_makan is not None:
            hasil['makan_pesan'] = f"✅ AI memplot Makan Siang ({durasi_makan} menit): **{menit_ke_time_str(mulai_makan)} - {menit_ke_time_str(selesai_makan)}**"
            for m in range(mulai_makan, selesai_makan): jadwal_harian[m] = True
            daftar_plot_grafik.append({
                "Aktivitas": "Makan Siang 🍎", "start_time": f"{today_str} {menit_ke_time_str(mulai_makan)}", 
                "finish_time": f"{today_str} {menit_ke_time_str(selesai_makan)}", "Kategori": "Makan 🍎"
            })
        else:
            hasil['makan_pesan'] = "⚠️ AI tidak menemukan slot makan siang ideal (12:00-14:00)."
            
        # Prioritas 2: Tidur (dari preferensi)
        durasi_tidur = int(pref_durasi_tidur_jam * 60)
        menit_mulai_pref = time_ke_menit(pref_jam_mulai_tidur)
        search_range_tidur = [(m % 1440) for m in range(menit_mulai_pref - 120, menit_mulai_pref + 121)] # Cari 2 jam sblm/ssdh
        
        mulai_tidur, selesai_tidur_panjang = cari_celah_waktu(jadwal_harian, durasi_tidur, search_range_tidur)
        
        if mulai_tidur is not None:
            waktu_bangun = menit_ke_time_str(selesai_tidur_panjang)
            hasil['tidur_tipe'] = "success"
            hasil['tidur_pesan'] = f"🎉 **RAMALAN AI: WAKTU TIDUR ({pref_durasi_tidur_jam} JAM):**"
            hasil['tidur_mulai'] = menit_ke_time_str(mulai_tidur)
            hasil['tidur_selesai'] = waktu_bangun
            for i in range(durasi_tidur): jadwal_harian[(mulai_tidur + i) % 1440] = True
            daftar_plot_grafik.append({
                "Aktivitas": "Tidur 😴", "start_time": f"{today_str} {menit_ke_time_str(mulai_tidur)}", 
                "finish_time": f"{today_str} {waktu_bangun}" + (" +1 day" if selesai_tidur_panjang > 1439 else ""), 
                "Kategori": "Tidur 😴"
            })
        else:
            hasil['tidur_tipe'] = "error"
            hasil['tidur_pesan'] = f"🚨 **PERINGATAN OVERWORK!** AI tidak dapat menemukan celah {pref_durasi_tidur_jam} jam untuk tidur di sekitar jam {pref_jam_mulai_tidur.strftime('%H:%M')}."

        # Prioritas 3: Plot aktivitas fleksibel (Tugas 🟡, Hobi 💜, dll.)
        for _, row in tugas_fleksibel.iterrows():
            try:
                mulai_dt = datetime.datetime.strptime(row['Jam Mulai'], '%H:%M').time()
                selesai_dt = datetime.datetime.strptime(row['Jam Selesai'], '%H:%M').time()
                mulai_menit = time_ke_menit(mulai_dt)
                selesai_menit = time_ke_menit(selesai_dt)
                
                # Cek apakah slot ini MASIH KOSONG (tidak ditabrak Tidur/Makan)
                slot_penuh = jadwal_harian[mulai_menit:selesai_menit]
                if not any(slot_penuh):
                    # Jika masih kosong, plot!
                    for m in range(mulai_menit, selesai_menit): jadwal_harian[m] = True
                    daftar_plot_grafik.append({
                        "Aktivitas": row['Aktivitas'], "start_time": f"{today_str} {row['Jam Mulai']}", 
                        "finish_time": f"{today_str} {row['Jam Selesai']}", "Kategori": row['Tipe']
                    })
                    total_beban_menit += (selesai_menit - mulai_menit)
                    if row['Tipe'] in ["Hobi 💜", "Sosial 💚", "Olahraga 🏃‍♀️"]:
                        ada_hobi_sosial = True
                else:
                    # GAGAL PLOT, jadwalnya tabrakan!
                    tugas_fleksibel_gagal.append(row['Aktivitas'])
            except:
                continue # Abaikan jika format jam salah

        # 4. Buat Grafik
        if not daftar_plot_grafik:
            st.error("Tidak ada data jadwal valid untuk digambar.")
            hasil['grafik'] = None
        else:
            df_final_plot = pd.DataFrame(daftar_plot_grafik)
            hasil['grafik'] = buat_grafik_timeline(df_final_plot)

        # 5. Buat Analisis Holistik (Menggunakan Data Psikologis)
        total_waktu_luang_menit = jadwal_harian.count(False)
        MIN_BEBAN_MENIT = int(pref_min_aktivitas_jam * 60)
        
        analisis_final = []
        
        # Analisis Stres & Energi
        if input_level_stres >= 4: # Stres 4 atau 5
            analisis_final.append(f"error: 🚨 **Mode Protektif: Stres Tinggi Terdeteksi!**\n{nama_user}, AI melihat level stres-mu sangat tinggi. AI **sangat menyarankan** kamu untuk **menghapus 1 'Tugas 🟡'** hari ini dan menggantinya dengan 'Hobi 💜' atau 'Waktu Tenang 🧘‍♀️' (misal: meditasi, dengerin musik) minimal 30 menit.")
        elif input_level_energi == "Rendah 🔋":
            analisis_final.append(f"warning: ⚠️ **Mode Recovery: Energi Rendah Terdeteksi!**\nEnergimu sedang rendah. Jangan paksakan diri. Pastikan kamu mengambil **istirahat mikro (Pomodoro)** 10-15 menit setiap 1 jam bekerja. AI juga menyarankan tidur 30 menit lebih awal malam ini jika memungkinkan.")
        else:
             analisis_final.append(f"success: ✅ **Status Psikologis: Stabil!**\nStres dan energimu hari ini terlihat seimbang. Pertahankan!")
             
        # Analisis Overwork / Underwork
        if hasil.get('tidur_tipe') == 'error' or len(tugas_fleksibel_gagal) > 0:
            analisis_final.append(f"error: 🚨 **Peringatan OVERWORK!**\nJadwalmu terlalu padat. AI gagal memplot jadwal tidur ATAU aktivitas berikut: **{', '.join(tugas_fleksibel_gagal)}**. Kamu **wajib** mengurangi/menggeser beban tugas hari ini.")
        elif total_beban_menit < MIN_BEBAN_MENIT:
            analisis_final.append(f"warning: ⚠️ **Peringatan UNDERWORK!**\nTotal aktivitas terstrukturmu hanya **{total_beban_menit // 60} jam**. Ini di bawah batas sehat {pref_min_aktivitas_jam} jam. AI merekomendasikan menambah aktivitas 'Olahraga 🏃‍♀️' atau 'Hobi 💜' agar harimu lebih seimbang.")
        
        # Analisis Keseimbangan Hidup (Work-Life Balance)
        if not ada_hobi_sosial and total_beban_menit >= MIN_BEBAN_MENIT:
             analisis_final.append(f"info: ℹ️ **Catatan Keseimbangan Hidup:**\nAI mendeteksi harimu sangat fokus pada 'Wajib 🔴' dan 'Tugas 🟡'. Kamu belum memplot waktu untuk 'Hobi 💜', 'Sosial 💚', atau 'Olahraga 🏃‍♀️'. Jangan lupa untuk bersantai ya!")
        
        hasil['analisis_teks'] = analisis_final
        
        # Simpan semua hasil ke session state
        st.session_state.hasil_disimpan = hasil
        st.success("Analisis Holistik Selesai! Cek tab '🧠 2. Lihat Hasil Analisis AI'")


with tab_hasil:
    st.header(f"Hasil Analisis Holistik & Grafik untuk {nama_user}")

    if not st.session_state.show_results:
        st.info("Silakan masukkan jadwal di tab 1 dan klik tombol 'Ramalkan' untuk melihat hasil di sini.")
    else:
        # Ambil hasil dari session state
        hasil = st.session_state.hasil_disimpan
        
        # --- TAMPILKAN GRAFIK (FASILITAS BARU) ---
        st.subheader("Visualisasi Timeline 24 Jam")
        if hasil.get('grafik'):
            st.plotly_chart(hasil['grafik'], use_container_width=True)
        else:
            st.warning("Tidak ada data untuk ditampilkan di grafik.")
            
        st.markdown("---")
        
        # --- TAMPILKAN ANALISIS HOLISTIK (AI BARU) ---
        st.subheader("Analisis & Saran dari AI")
        
        # Tampilkan hasil plot tidur & makan
        if hasil.get('tidur_tipe') == 'success':
            st.success(hasil['tidur_pesan'])
            col1, col2 = st.columns(2)
            col1.metric("Mulai Tidur 😴", hasil['tidur_mulai'])
            col2.metric("Bangun Tidur ☀️", hasil['tidur_selesai'])
        elif hasil.get('tidur_tipe') == 'error':
            st.error(hasil['tidur_pesan'])
            
        st.info(hasil.get('makan_pesan', ''))
        st.markdown("---")

        # Tampilkan analisis utama (Stres, Energi, Keseimbangan)
        if 'analisis_teks' in hasil:
            for pesan in hasil['analisis_teks']:
                tipe, teks = pesan.split(':', 1)
                if tipe == 'error':
                    st.error(teks)
                elif tipe == 'warning':
                    st.warning(teks)
                elif tipe == 'success':
                    st.success(teks)
                else:
                    st.info(teks)