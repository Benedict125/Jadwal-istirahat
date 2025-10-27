import streamlit as st
import datetime

# --- Kumpulan Fungsi "Otak" AI ---
# (Semua fungsi ... parse_input_beban, cari_celah_waktu ... tetap sama
# dari v3.0, jadi kita copy-paste saja)

def time_ke_menit(waktu_dt):
    return waktu_dt.hour * 60 + waktu_dt.minute

def menit_ke_time_str(total_menit):
    jam = (total_menit // 60) % 24
    menit = total_menit % 60
    return f"{jam:02d}:{menit:02d}"

def parse_input_beban(teks_input):
    daftar_sibuk = []
    total_beban_menit = 0
    baris_input = teks_input.split('\n')
    
    for baris in baris_input:
        if '-' in baris: 
            try:
                jam_str = baris.strip().split(' ')[0]
                mulai_str, selesai_str = jam_str.split('-')
                
                mulai_dt = datetime.datetime.strptime(mulai_str, '%H:%M').time()
                selesai_dt = datetime.datetime.strptime(selesai_str, '%H:%M').time()
                
                mulai_menit = time_ke_menit(mulai_dt)
                selesai_menit = time_ke_menit(selesai_dt)
                
                daftar_sibuk.append((mulai_menit, selesai_menit))
                
                durasi_menit = 0
                if selesai_menit <= mulai_menit:
                    if selesai_menit == 0:
                        durasi_menit = (24 * 60) - mulai_menit
                    else:
                        durasi_menit = ( (24 * 60) - mulai_menit) + selesai_menit
                else:
                    durasi_menit = selesai_menit - mulai_menit
                
                total_beban_menit += durasi_menit
                
            except ValueError:
                st.warning(f"Format baris salah, mengabaikan: '{baris}'")
                continue
                
    return daftar_sibuk, total_beban_menit

def cari_celah_waktu(jadwal_harian, durasi_menit, search_range_list):
    for start_menit in search_range_list:
        akhir_menit = start_menit + durasi_menit
        
        if akhir_menit > 1439: 
            slot_satu = jadwal_harian[start_menit : 1440]
            slot_dua = jadwal_harian[0 : akhir_menit % 1440] 
            slot_penuh = slot_satu + slot_dua
        else:
            slot_penuh = jadwal_harian[start_menit : akhir_menit]
            
        if not any(slot_penuh): 
            return start_menit, akhir_menit
            
    return None, None 

# --- Inisialisasi State (Fasilitas Baru) ---
# Ini agar AI "ingat" hasilnya saat ganti tab
if "hasil_disimpan" not in st.session_state:
    st.session_state.hasil_disimpan = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# --- Tampilan Aplikasi (Web App) v4.0 ---

st.set_page_config(page_title="AI Penjadwal Istirahat untuk Rebecca", page_icon="💖", layout="wide")

# --- DESAIN 1: Personalisasi Sapaan ---
nama_user = st.text_input("Siapa nama panggilan Anda?", "AKUU REBECCAAA")
st.title(f"💖 AI Penjadwal Istirahat untuk {nama_user} YANG CANTIK NAN LUCU")

# --- FASILITAS: Sidebar Pengaturan (dari v3.0) ---
st.sidebar.header("⚙️ Pengaturan Preferensi")
pref_jam_mulai_tidur = st.sidebar.time_input("Jam ideal mulai tidur?", datetime.time(22, 0))
pref_durasi_tidur_jam = st.sidebar.number_input("Durasi tidur ideal (jam)?", 6.0, 10.0, 8.0, 0.5)
pref_durasi_makan_siang = st.sidebar.slider("Durasi makan siang ideal (menit)?", 30, 90, 60)
# --- LOGIKA BARU: Batas Aktivitas Minimum ---
pref_min_aktivitas_jam = st.sidebar.slider("Batas minimum aktivitas sehat (jam)?", 2.0, 6.0, 4.0, 0.5)


# --- DESAIN 2: Tampilan Tabs ---
tab_input, tab_hasil = st.tabs(["🗓️ 1. SINI DiInput Jadwal pada Hari Ini", "🧠 2. YUU Lihat Hasil Analisis dari AI nya disini"])

with tab_input:
    st.header("Masukkin dong Beban Tugas Harian hari ini")
    st.info(f"""
    Hai {nama_user}, masukkan semua jadwal sibuk Rebecca.
    AI nya nanti akan otomatis mencari jadwal istirahat terbaik di harimu.
    **Contoh Format:**
    07:00-09:00 Kelas Pagi
    19:00-21:00 Tugas Lomba
    23:00-00:00 Twitter
    """)
    
    default_input = "07:00-09:00 Kelas\n10:00-12:00 Kelas\n13:00-15:00 Kelas\n15:00-17:00 Kelas\n19:00-21:00 Persiapan Lomba"
    input_beban = st.text_area("Jadwal Sibuk Hari Ini:", height=175, value=default_input, key="input_jadwal")

    if st.button("Ramalkan Jadwal Istirahat untuk kamuuu!", type="primary", use_container_width=True):
        st.session_state.show_results = True # Set flag untuk tampilkan tab hasil
        hasil = {} # Reset hasil
        
        # --- PROSES BERPIKIR AI DIMULAI ---
        jadwal_harian = [False] * 1440 
        daftar_sibuk, total_beban_menit = parse_input_beban(input_beban)
        
        for (mulai, selesai) in daftar_sibuk:
            if selesai <= mulai:
                if selesai == 0: 
                    for menit in range(mulai, 1440): jadwal_harian[menit] = True
                else:
                    for menit in range(mulai, 1440): jadwal_harian[menit] = True
                    for menit in range(0, selesai): jadwal_harian[menit] = True
            else:
                for menit in range(mulai, selesai): jadwal_harian[menit] = True
        
        # 1. Cari Makan Siang (Sesuai Preferensi)
        durasi_makan = pref_durasi_makan_siang
        search_range_makan = list(range(720, 841)) # 12:00-14:00
        mulai_makan, selesai_makan = cari_celah_waktu(jadwal_harian, durasi_makan, search_range_makan)
        
        if mulai_makan is not None:
            hasil['makan_tipe'] = "success"
            hasil['makan_pesan'] = f"✅ AI nya menemukan slot Makan Siang ({durasi_makan} menit): **{menit_ke_time_str(mulai_makan)} - {menit_ke_time_str(selesai_makan)}**"
            for menit in range(mulai_makan, selesai_makan): jadwal_harian[menit] = True
        else:
            hasil['makan_tipe'] = "warning"
            hasil['makan_pesan'] = "⚠️ AI nya tidak menemukan slot 60 menit untuk makan siang antara 12:00-14:00."

        # 2. Cari Tidur (Sesuai Preferensi)
        durasi_tidur = int(pref_durasi_tidur_jam * 60)
        menit_mulai_pref = time_ke_menit(pref_jam_mulai_tidur)
        search_range_tidur = [(m % 1440) for m in range(menit_mulai_pref - 60, menit_mulai_pref + 121)] # Cari 1 jam sblm & 2 jam ssdh
        
        mulai_tidur, selesai_tidur_panjang = cari_celah_waktu(jadwal_harian, durasi_tidur, search_range_tidur)
        
        if mulai_tidur is not None:
            waktu_bangun = menit_ke_time_str(selesai_tidur_panjang) 
            hasil['tidur_tipe'] = "success"
            hasil['tidur_pesan'] = f"🎉 **AI MERAMAL NIHH: WAKTU TIDUR TERBAIK YAITU ({pref_durasi_tidur_jam} JAM):**"
            hasil['tidur_mulai'] = menit_ke_time_str(mulai_tidur)
            hasil['tidur_selesai'] = waktu_bangun
            for i in range(durasi_tidur): jadwal_harian[(mulai_tidur + i) % 1440] = True
        else:
            hasil['tidur_tipe'] = "error"
            hasil['tidur_pesan'] = f"🚨 **PERINGATAN OVERWORK!** AI tidak dapat nemuin celah {pref_durasi_tidur_jam} jam untuk tidur di sekitar jam {pref_jam_mulai_tidur.strftime('%H:%M')}."

        # 3. Analisis Beban Kerja (Overwork & Underwork)
        total_waktu_luang_menit = jadwal_harian.count(False)
        hasil['beban_total'] = f"{total_beban_menit // 60} jam {total_beban_menit % 60} mnt"
        hasil['luang_total'] = f"{total_waktu_luang_menit // 60} jam {total_waktu_luang_menit % 60} mnt"

        # --- LOGIKA BARU: DETEKTOR "UNDERWORK" ---
        MIN_BEBAN_MENIT = int(pref_min_aktivitas_jam * 60)
        
        if total_beban_menit < MIN_BEBAN_MENIT:
            hasil['analisis_tipe'] = "warning"
            hasil['analisis_pesan'] = f"⚠️ **PERINGATAN 'UNDERWORK'** ⚠️\nTotal aktivitas terstruktur Becca hari ini hanya **{hasil['beban_total']}**. Ini menyisakan **{hasil['luang_total']}** waktu luang. \n\nTerlalu banyak waktu pasif juga tidak sehat. AI merekomendasikan untuk menambahkan aktivitas nihh seperti: \n- Bertemu Benedict\n- 🏃‍♀️ Olahraga/GYM \n- 📚 Baca buku\n- 🧹 Bersihkan kamar"
        elif hasil['tidur_tipe'] == 'error':
            # Jika overwork (terdeteksi dari gagalnya plot tidur)
            hasil['analisis_tipe'] = "error"
            hasil['analisis_pesan'] = "🚨 **PERINGATAN 'OVERWORK'** 🚨\nJadwal Rebecca terlalu padat sehingga AI tidak bisa menemukan slot tidur. Kamu **wajib** mengurangi atau menggeser beban tugas hari ini nih."
        else:
            hasil['analisis_tipe'] = "success"
            hasil['analisis_pesan'] = f"✅ **JADWAL SEIMBANG!**\nKerja bagus, {nama_user}! Kamu punya **{hasil['beban_total']}** beban tugas dan **{hasil['luang_total']}** waktu luang. Gunakan waktu luang itu untuk planning untuk kedepanya di sela-sela tugas ya. Semangat Rebeccaa Sayang! ❤️"
        
        # Simpan semua hasil ke session state
        st.session_state.hasil_disimpan = hasil
        st.success("Analisis Selesai! Coba Cek tab '🧠 2. Lihat Hasil Analisis AI'")


with tab_hasil:
    st.header(f"Analisis Keseimbangan Harian untuk {nama_user}")

    if not st.session_state.show_results:
        st.info("Silakan masukkan jadwal Rebecca di tab 1 dan klik tombol 'Ramalkan' untuk melihat hasilnya di sini.")
    else:
        # Ambil hasil dari session state
        hasil = st.session_state.hasil_disimpan
        
        # 1. Tampilkan Hasil Makan Siang
        if hasil.get('makan_tipe') == 'success':
            st.success(hasil['makan_pesan'])
        elif hasil.get('makan_tipe') == 'warning':
            st.warning(hasil['makan_pesan'])
            
        # 2. Tampilkan Hasil Tidur
        if hasil.get('tidur_tipe') == 'success':
            st.success(hasil['tidur_pesan'])
            col1, col2 = st.columns(2)
            col1.metric("Mulai Tidur 😴", hasil['tidur_mulai'])
            col2.metric("Bangun Tidur ☀️", hasil['tidur_selesai'])
        elif hasil.get('tidur_tipe') == 'error':
            st.error(hasil['tidur_pesan'])

        st.markdown("---")
        
        # 3. Tampilkan Analisis Beban Kerja
        st.subheader("Analisis Beban Kerja Harian")
        
        col1, col2 = st.columns(2)
        col1.metric("Total Beban Tugas Terstruktur", hasil.get('beban_total', '0 jam 0 mnt'))
        col2.metric("Total Waktu Luang (u/ Istirahat Mikro)", hasil.get('luang_total', '0 jam 0 mnt'))
        
        if hasil.get('analisis_tipe') == 'success':
            st.success(hasil['analisis_pesan'])
        elif hasil.get('analisis_tipe') == 'warning':
            st.warning(hasil['analisis_pesan'])
        elif hasil.get('analisis_tipe') == 'error':
            st.error(hasil['analisis_pesan'])