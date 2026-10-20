# Webinar 5 — Human Computer Interaction and Data Visualization

**Studi kasus:** Dashboard pemantauan penjualan Toko Sahabat.
**Bahasa:** HTML, CSS, JavaScript, Python (standard library).
**Sifat data:** Seluruh data adalah SIMULASI, bukan data transaksi asli.

Proyek ini mencontohkan materi webinar Bapak Arafat Febriandirza tentang *user-centered design*, kebutuhan pengguna, evaluasi antarmuka, visualisasi data yang tepat, dan dashboard interaktif.

## Cara menjalankan (Windows)

1. Ekstrak file ZIP ke sebuah folder.
2. Pastikan Python 3 sudah terpasang. Periksa dengan `python --version`.
3. Klik dua kali **mulai_windows.bat** (atau jalankan `python server.py` dari terminal di folder ini).
4. Buka **http://localhost:8000/** di browser.
5. Selesai menggunakan, tekan **Ctrl+C** pada jendela terminal.

**Linux/macOS:** Buka terminal di folder ini, lalu jalankan `python3 server.py` atau `./mulai_linux_mac.sh`.

> Penting: jangan membuka `web/index.html` langsung dengan klik ganda, karena browser dapat memblokir pembacaan file CSV dari folder lokal. Gunakan server lokal di atas.

Jika port 8000 sudah dipakai, jalankan `python server.py --port 8001` lalu buka `http://localhost:8001/`.

## Apa yang bisa dicoba?

- Pilih **Periode**, **Wilayah**, dan **Kategori**; empat indikator, grafik garis, grafik batang, dan tabel harian akan ikut berubah.
- Klik **Atur ulang** untuk kembali ke seluruh data.
- Klik **Unduh CSV** untuk memperoleh data yang sudah difilter.
- Navigasi dengan tombol **Tab** dan gunakan **Enter** atau **Spasi** untuk mengoperasikan kontrol.
- Perkecil jendela browser: tampilan akan menyesuaikan layar kecil.

## Analisis versi Python (terminal)

Untuk menampilkan statistik ringkas secara tekstual:

```bash
python analisis.py
python analisis.py --bulan 2026-09 --wilayah Bengkulu
python analisis.py --kategori Minuman --json
```

Pengujian sederhana:

```bash
python -m unittest discover -s tests -v
```

Tidak perlu menginstal paket dari internet atau menyiapkan database.

## Struktur folder

```text
webinar_5_hci_visualisasi/
├── README.md                 # Panduan menjalankan
├── STUDI_KASUS.md            # Latar belakang, analisis, dan penjelasan implementasi
├── server.py                 # HTTP server lokal Python
├── analisis.py               # Analisis CSV di terminal
├── mulai_windows.bat         # Cara mudah menjalankan di Windows
├── mulai_linux_mac.sh        # Cara mudah menjalankan di Linux/macOS
├── data/
│   └── penjualan.csv         # Data simulasi 1 Sept - 20 Okt 2026
├── web/
│   ├── index.html            # Struktur dan label semantik
│   ├── style.css             # Desain responsif + kontras
│   └── app.js                # Filter, agregasi, visualisasi, ekspor CSV
└── tests/
    └── test_analisis.py      # Unit test ringkasan
```

**Catatan:** Aplikasi berjalan di `127.0.0.1` (komputer sendiri). Tidak mengirim data ke layanan luar. Ini merupakan demonstrasi sederhana, bukan sistem administrasi toko produksi.
