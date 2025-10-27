import streamlit as st
import datetime

# --- Kumpulan Fungsi "Otak" AI ---

def time_ke_menit(waktu_dt):
    """(Helper) Mengubah '09:00' menjadi 540 menit."""
    return waktu_dt.hour * 60 + waktu_dt.minute

def menit_ke_time_str(total_menit):
    """
    (Helper) Mengubah total menit menjadi string jam (cth: 1860 -> '07:00')
    Ini sudah diperbaiki untuk menangani waktu > 24 jam.
    """
    jam = (total_menit // 60) % 24 # Modulo 24 untuk jam hari berikutnya
    menit = total_menit % 60
    return f"{jam:02d}:{menit:02d}"

def parse_input_beban(teks_input):
    """
    Membaca input teks dari user.
    SUDAH DIPERBAIKI: Bisa menghitung durasi lembur (overnight).
    """
    daftar_sibuk = []
    total_beban_menit = 0
    baris_input = teks_input.split('\n') # Pisahkan per baris
    
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
                
                # --- LOGIKA BARU UNTUK HITUNG DURASI ---
                durasi_menit = 0
                if selesai_menit <= mulai_menit:
                    # Kasus 23:00-00:00 (selesai_menit = 0)
                    if selesai_menit == 0:
                        durasi_menit = (24 * 60) - mulai_menit
                    # Kasus 23:00-01:00 (selesai_menit = 60)
                    else:
                        durasi_menit = ( (24 * 60) - mulai_menit) + selesai_menit
                else:
                    # Tugas normal (09:00-11:00)
                    durasi_menit = selesai_menit - mulai_menit
                
                total_beban_menit += durasi_menit
                
            except ValueError:
                st.warning(f"Format baris salah, mengabaikan: '{baris}'")
                continue
                
    return daftar_sibuk, total_beban_menit

def cari_celah_waktu(jadwal_harian, durasi_menit, search_range_list):
    """
    Inti "Otak AI" untuk meramal.
    AI akan memindai 'jadwal_harian' menggunakan 'search_range_list'
    search_range_list: Daftar menit untuk memulai pencarian (cth: [1260, ... 1439, 0, ... 60])
    """
    for start_menit in search_range_list:
        akhir_menit = start_menit + durasi_menit
        
        # Cek apakah jadwal melewati tengah malam (untuk tidur)
        if akhir_menit > 1439: # 1439 adalah menit 23:59
            # Ambil slot dari start_menit s/d 23:59
            slot_satu = jadwal_harian[start_menit : 1440]
            # Ambil slot dari 00:00 s/d sisa durasi
            slot_dua = jadwal_harian[0 : akhir_menit % 1440] # Modulo 1440
            slot_penuh = slot_satu + slot_dua
        else:
            # Pengecekan normal (tidak melewati tengah malam)
            slot_penuh = jadwal_harian[start_menit : akhir_menit]
            
        # Cek apakah seluruh slot 'False' (Kosong)
        if not any(slot_penuh): # 'not any(True)' -> artinya semua False
            # KETEMU! Kembalikan waktu mulai dan selesainya
            return start_menit, akhir_menit # akhir_menit bisa > 1440
            
    # Jika loop selesai dan tidak ketemu
    return None, None # Tidak menemukan celah

# --- Tampilan Aplikasi (Web App) ---

st.set_page_config(page_title="AI Penjadwal Istirahat", page_icon="💖")
st.title("💖 AI Penjadwal Istirahat (v2.0)")
st.caption(f"Dibuat khusus untukmu. Hari ini: {datetime.date.today().strftime('%A, %d %B %Y')}")

st.header("1. Masukkan Beban Tugas Harian")
st.info("""
Masukkan semua jadwal sibuk Anda, termasuk jika ada urusan/lembur malam.
**Contoh Format:**
07:00-09:00 Kelas Pagi
10:00-12:00 Kelas Siang
19:00-21:00 Tugas Lomba
23:00-00:00 Urusan Malam
""")

# Kotak input teks
default_input = "07:00-09:00 Kelas\n10:00-12:00 Kelas\n13:00-15:00 Kelas\n15:00-17:00 Kelas Lanjutan\n19:00-21:00 Persiapan Lomba\n23:00-00:00 Urusan Malam"
input_beban = st.text_area("Jadwal Sibuk Hari Ini:", height=175, value=default_input)

if st.button("Ramalkan Jadwal Istirahat Saya!", type="primary"):
    
    # --- PROSES BERPIKIR AI DIMULAI ---
    
    st.header("2. Hasil Analisis & Ramalan AI")
    
    # 1. Buat Peta Rel 24 Jam (1440 menit, semua Kosong/False)
    jadwal_harian = [False] * 1440 
    
    # 2. Tandai "Gerbong Barang" (Input User)
    daftar_sibuk, total_beban_menit = parse_input_beban(input_beban)
    
    # --- LOGIKA BARU UNTUK MENANDAI JADWAL OVERNIGHT ---
    for (mulai, selesai) in daftar_sibuk:
        if selesai <= mulai:
            # Kasus 23:00-00:00 (selesai = 0) atau 23:00-01:00 (selesai = 60)
            if selesai == 0: 
                # Jika 00:00, anggap 24:00. Tandai s/d 23:59
                for menit in range(mulai, 1440):
                    jadwal_harian[menit] = True
            else:
                # Jika 01:00 (60)
                # 1. Tandai dari 'mulai' s/d 23:59
                for menit in range(mulai, 1440):
                    jadwal_harian[menit] = True
                # 2. Tandai dari 00:00 s/d 'selesai'
                for menit in range(0, selesai):
                    jadwal_harian[menit] = True
        else:
            # Ini tugas normal (siang hari)
            for menit in range(mulai, selesai):
                jadwal_harian[menit] = True
            
    # 3. AI Mencari "Gerbong Istirahat" (Komprehensif)
    st.subheader("Mencari Jadwal Istirahat Siang...")
    search_range_makan = list(range(720, 841)) # 12:00 s/d 14:00
    mulai_makan_siang, selesai_makan_siang = cari_celah_waktu(jadwal_harian, 60, search_range_makan)
    
    if mulai_makan_siang is not None:
        st.success(f"✅ AI menemukan slot Makan Siang: **{menit_ke_time_str(mulai_makan_siang)} - {menit_ke_time_str(selesai_makan_siang)}**")
        # Tandai jadwal makan siang sebagai Sibuk
        for menit in range(mulai_makan_siang, selesai_makan_siang):
            jadwal_harian[menit] = True
    else:
        st.warning("⚠️ AI tidak menemukan slot 60 menit untuk makan siang antara 12:00-14:00.")

    # 4. AI "Meramalkan" Waktu Tidur (Prioritas Utama & Fleksibel)
    st.subheader("Meramalkan Waktu Tidur (Minimal 8 Jam)")
    durasi_tidur = 8 * 60 # 480 menit
    
    # --- LOGIKA BARU: Rentang pencarian fleksibel ---
    # AI akan mencari slot tidur yang mulainya antara 21:00 s/d 01:00
    search_range_tidur = list(range(1260, 1440)) + list(range(0, 61)) # 21:00->23:59, lalu 00:00->01:00
    
    mulai_tidur, selesai_tidur_panjang = cari_celah_waktu(jadwal_harian, durasi_tidur, search_range_tidur)
    
    if mulai_tidur is not None:
        # selesai_tidur_panjang bisa > 1440 (cth: 1860)
        waktu_bangun = menit_ke_time_str(selesai_tidur_panjang) 
        
        st.success(f"🎉 **RAMALAN AI: WAKTU TIDUR TERBAIK ANDA (8 JAM):**")
        
        col1, col2 = st.columns(2)
        col1.metric(label="Mulai Tidur", value=menit_ke_time_str(mulai_tidur))
        col2.metric(label="Bangun Tidur", value=waktu_bangun)
        
        st.info("AI sudah mengunci jadwal ini untuk Anda. Selamat istirahat! 😴")
        # Tandai jadwal tidur sebagai Sibuk
        for i in range(durasi_tidur):
            menit = (mulai_tidur + i) % 1440
            jadwal_harian[menit] = True
            
    else:
        st.error("🚨 **PERINGATAN OVERWORK!** 🚨")
        st.error("AI tidak dapat menemukan celah 8 jam untuk tidur yang dimulai antara 21:00-01:00. Jadwal Anda terlalu padat. Mohon kurangi beban tugas agar bisa istirahat.")

    # 5. Analisis Sisa Waktu (Jawaban dari Riset)
    st.subheader("Analisis Beban Kerja Harian Anda")
    # Hitung sisa waktu luang (yang masih False)
    total_waktu_luang_menit = jadwal_harian.count(False)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Beban Tugas (Input Anda)", 
                f"{total_beban_menit // 60} jam {total_beban_menit % 60} mnt")
    col2.metric("Total Waktu Luang (Untuk Istirahat Mikro)", 
                f"{total_waktu_luang_menit // 60