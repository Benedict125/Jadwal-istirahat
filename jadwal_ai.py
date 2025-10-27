import streamlit as st
import datetime

# --- Kumpulan Fungsi "Otak" AI ---
# Ini adalah bagian "AI" yang berpikir dan meramal

def time_ke_menit(waktu_dt):
    """(Helper) Mengubah '09:00' menjadi 540 menit."""
    return waktu_dt.hour * 60 + waktu_dt.minute

def menit_ke_time_str(total_menit):
    """(Helper) Mengubah 540 menit menjadi string '09:00'."""
    # Menangani jika waktu melewati tengah malam (cth: 1800 menit -> 30:00)
    jam = (total_menit // 60) % 24 
    menit = total_menit % 60
    return f"{jam:02d}:{menit:02d}"

def parse_input_beban(teks_input):
    """Membaca input teks dari user dan mengubahnya jadi daftar slot sibuk."""
    daftar_sibuk = []
    total_beban_menit = 0
    baris_input = teks_input.split('\n') # Pisahkan per baris
    
    for baris in baris_input:
        if '-' in baris: # Pastikan ada format jam (cth: '07:00-09:00')
            try:
                # Ambil bagian jam saja, abaikan deskripsi (cth: "Kelas")
                jam_str = baris.strip().split(' ')[0]
                mulai_str, selesai_str = jam_str.split('-')
                
                mulai_dt = datetime.datetime.strptime(mulai_str, '%H:%M').time()
                selesai_dt = datetime.datetime.strptime(selesai_str, '%H:%M').time()
                
                mulai_menit = time_ke_menit(mulai_dt)
                selesai_menit = time_ke_menit(selesai_dt)
                
                # Tambahkan ke daftar slot sibuk
                daftar_sibuk.append((mulai_menit, selesai_menit))
                # Akumulasi total beban kerja
                total_beban_menit += (selesai_menit - mulai_menit)
                
            except ValueError:
                # Abaikan baris yang formatnya salah
                st.warning(f"Format baris salah, mengabaikan: '{baris}'")
                continue
                
    return daftar_sibuk, total_beban_menit

def cari_celah_waktu(jadwal_harian, durasi_menit, mulai_cari_menit, selesai_cari_menit):
    """
    Inti "Otak AI" untuk meramal.
    AI akan memindai 'jadwal_harian' untuk menemukan celah kosong.
    """
    for start_menit in range(mulai_cari_menit, selesai_cari_menit + 1):
        akhir_menit = start_menit + durasi_menit
        
        # Cek apakah jadwal melewati tengah malam (khusus untuk tidur)
        # 1439 adalah menit 23:59
        if akhir_menit > 1439: 
            # Cek slot dari start_menit s/d 23:59
            slot_satu = jadwal_harian[start_menit : 1440]
            # Cek slot dari 00:00 s/d sisa durasi
            sisa_durasi = akhir_menit - 1440
            slot_dua = jadwal_harian[0 : sisa_durasi]
            
            slot_penuh = slot_satu + slot_dua
        else:
            # Pengecekan normal (tidak melewati tengah malam)
            slot_penuh = jadwal_harian[start_menit : akhir_menit]
            
        # Cek apakah seluruh slot 'False' (Kosong)
        # 'not any(slot_penuh)' berarti tidak ada 'True' di dalam slot itu
        if not any(slot_penuh): 
            # KETEMU! Kembalikan waktu mulai dan selesainya
            return start_menit, akhir_menit # akhir_menit bisa > 1440
            
    # Jika loop selesai dan tidak ketemu
    return None, None # Tidak menemukan celah

# --- Tampilan Aplikasi (Web App) ---

st.set_page_config(page_title="AI Penjadwal Istirahat", page_icon="💖")
st.title("💖 AI Penjadwal Istirahat")
st.caption(f"Dibuat khusus untukmu. Hari ini: {datetime.date.today().strftime('%A, %d %B %Y')}")

st.header("1. Masukkan Beban Tugas Harian")
st.info("""
Masukkan semua jadwal sibuk Anda, satu per baris.
AI akan otomatis mencari jadwal istirahat terbaik.

**Contoh Format:**
07:00-09:00 Kelas Pagi
10:00-12:00 Kelas Siang
13:00-15:00 Kelas Lagi
19:00-21:00 Tugas Lomba
""")

# Kotak input teks
# Kita isi value default sesuai contoh Anda
default_input = "07:00-09:00 Kelas\n10:00-12:00 Kelas\n13:00-15:00 Kelas\n15:00-17:00 Kelas Lanjutan\n19:00-21:00 Persiapan Lomba"
input_beban = st.text_area("Jadwal Sibuk Hari Ini:", height=175, value=default_input)

if st.button("Ramalkan Jadwal Istirahat Saya!", type="primary"):
    
    # --- PROSES BERPIKIR AI DIMULAI ---
    
    # 1. Buat Peta Rel 24 Jam (1440 menit, semua Kosong/False)
    # False = Kosong, True = Sibuk
    jadwal_harian = [False] * 1440 
    
    # 2. Tandai "Gerbong Barang" (Input User)
    daftar_sibuk, total_beban_menit = parse_input_beban(input_beban)
    for (mulai, selesai) in daftar_sibuk:
        for menit in range(mulai, selesai):
            if menit < 1440: # Pastikan tidak error jika input 23:00-01:00
                jadwal_harian[menit] = True # Tandai sebagai Sibuk
            
    st.header("2. Hasil Analisis & Ramalan AI")
    
    # 3. AI Mencari "Gerbong Istirahat" (Komprehensif)
    # Kita cari antara jam 12:00 (menit 720) s/d 13:00 (menit 780)
    st.subheader("Mencari Jadwal Istirahat Siang...")
    mulai_makan_siang, selesai_makan_siang = cari_celah_waktu(jadwal_harian, 60, 720, 780)
    
    if mulai_makan_siang is not None:
        st.success(f"✅ AI menemukan slot Makan Siang: **{menit_ke_time_str(mulai_makan_siang)} - {menit_ke_time_str(selesai_makan_siang)}**")
        # Tandai jadwal makan siang sebagai Sibuk agar tidak ditabrak jadwal tidur
        for menit in range(mulai_makan_siang, selesai_makan_siang):
            jadwal_harian[menit] = True
    else:
        st.warning("⚠️ AI tidak menemukan slot 60 menit untuk makan siang antara 12:00-13:00.")

    # 4. AI "Meramalkan" Waktu Tidur (Prioritas Utama)
    # Kita penuhi target 8 Jam (480 Menit)
    # Kita cari slot yang mulainya antara 22:00 (menit 1320) s/d 23:30 (menit 1410)
    # Ini sesuai dengan contoh Anda yang ingin mulai jam 22:00
    st.subheader("Meramalkan Waktu Tidur (Minimal 8 Jam)")
    durasi_tidur = 8 * 60 # 480 menit
    mulai_tidur, selesai_tidur_panjang = cari_celah_waktu(jadwal_harian, durasi_tidur, 1320, 1410)
    
    if mulai_tidur is not None:
        # selesai_tidur_panjang akan > 1440 (misal 1800)
        # Kita pakai % 24 untuk mendapatkan jam di hari berikutnya
        waktu_bangun = menit_ke_time_str(selesai_tidur_panjang) 
        
        st.success(f"🎉 **RAMALAN AI: WAKTU TIDUR TERBAIK ANDA (8 JAM):**")
        
        col1, col2 = st.columns(2)
        col1.metric(label="Mulai Tidur Malam Ini", value=menit_ke_time_str(mulai_tidur))
        col2.metric(label="Bangun Tidur Besok Pagi", value=waktu_bangun)
        
        st.info("AI sudah mengunci jadwal ini untuk Anda. Selamat istirahat! 😴")
        # Tandai jadwal tidur sebagai Sibuk
        for i in range(durasi_tidur):
            menit = (mulai_tidur + i) % 1440
            jadwal_harian[menit] = True
            
    else:
        st.error("🚨 **PERINGATAN OVERWORK!** 🚨")
        st.error("AI tidak dapat menemukan celah 8 jam untuk tidur yang dimulai antara 22:00-23:30. Jadwal Anda terlalu padat. Mohon kurangi beban tugas agar bisa istirahat.")

    # 5. Analisis Sisa Waktu (Jawaban dari Riset)
    st.subheader("Analisis Beban Kerja Harian Anda")
    # Hitung sisa waktu luang (yang masih False)
    total_waktu_luang_menit = jadwal_harian.count(False)
    total_waktu_sibuk_menit = 1440 - total_waktu_luang_menit
    
    col1, col2 = st.columns(2)
    col1.metric("Total Waktu Sibuk (Tugas + Istirahat Terplot)", 
                f"{total_waktu_sibuk_menit // 60} jam {total_waktu_sibuk_menit % 60} mnt")
    col2.metric("Total Waktu Luang (Untuk Istirahat Mikro)", 
                f"{total_waktu_luang_menit // 60} jam {total_waktu_luang_menit % 60} mnt")

    st.markdown("---")
    st.markdown("#### **Catatan dari AI (Berdasarkan Riset):**")
    st.markdown(f"Anda memiliki **{total_waktu_luang_menit // 60} jam** waktu luang tersisa. Riset ilmiah (seperti *Teknik Pomodoro*) menyarankan untuk menggunakan waktu ini **bukan** untuk bekerja, tapi untuk **istirahat mikro** (5-15 menit) di antara sesi tugas Anda untuk menjaga fokus dan mengurangi stres. Semangat!")