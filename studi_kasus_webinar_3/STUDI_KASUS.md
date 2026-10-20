# Studi Kasus: Analisis Lokasi Toko Baru dengan Konsep GIS

## 1. Latar Belakang

Webinar ketiga *Informatics Practitioner Lecture Series 2026*, bertema *Career and Competition in Industrial Era with GIS*, menunjukkan bahwa Geographic Information System (GIS) dapat dimanfaatkan dalam pengambilan keputusan bisnis. Salah satu contohnya adalah pemilihan lokasi gerai ritel dengan memperhatikan jarak antartoko, jumlah penduduk, serta biaya dan jarak distribusi barang. Mahasiswa Informatika dapat memanfaatkan kemampuan pemrograman untuk melakukan analisis geospasial sederhana bahkan tanpa aplikasi GIS khusus.

## 2. Permasalahan

Sebuah usaha ritel fiktif berencana membuka satu gerai tambahan. Terdapat sepuluh calon lokasi, tiga gerai eksisting, dan satu gudang pusat **semuanya fiktif**. Usaha ingin memilih kandidat paling sesuai dengan mempertimbangkan potensi pasar, persaingan internal antargerai, kemudahan pasokan, dan biaya sewa.

**Pertanyaan studi kasus:** Lokasi simulasi manakah yang paling layak diprioritaskan berdasarkan kriteria dan pembobotan yang ditetapkan?

## 3. Tujuan

Menghitung jarak antar titik geografis menggunakan koordinat lintang-bujur, menerapkan aturan kelayakan, mengurutkan alternatif menggunakan skor terbobot, menyimpan laporan dalam CSV dan TXT, dan membuat visualisasi skematis dalam SVG.

## 4. Data dan Variabel

Data CSV di folder `data/` memuat kandidat lokasi (`kode`, `nama`, `lat`, `lon`, `penduduk_1km`, `sewa_juta_bulan`), gerai yang sudah ada (`kode`, `nama`, `lat`, `lon`), dan lokasi gudang. Contoh di sekitar Bengkulu hanya dipakai sebagai konteks geografis. Tidak ada hasil survei ataupun data kependudukan asli di proyek ini.

## 5. Metode

**Langkah pertama:** gunakan rumus *Haversine* untuk menghitung jarak garis lurus di permukaan Bumi antara calon gerai dengan toko terdekat, serta antara calon gerai dengan gudang.

**Langkah kedua:** lakukan penyaringan kelayakan: lokasi dinyatakan *tidak layak* jika jarak ke toko terdekat kurang dari **0,7 km** atau jarak ke gudang lebih dari **10 km**. Batas ini hanya asumsi simulasi.

**Langkah ketiga:** hitung empat skor terstandar antara 0 sampai 100. Skor penduduk naik dari 0 pada 3.000 orang ke 100 pada 10.000 orang; skor jarak toko naik dari 0 pada 0,7 km ke 100 pada 3 km; skor logistik turun dari 100 pada 0 km ke 0 pada 8 km; skor sewa turun dari 100 pada Rp3 juta/bulan ke 0 pada Rp12 juta/bulan. Nilai dibatasi antara 0 dan 100.

Rumus skor total:

`Skor = 0,40 × skor_penduduk + 0,25 × skor_jarak_toko + 0,20 × skor_logistik + 0,15 × skor_sewa`

**Langkah keempat:** urutkan kandidat **yang layak** dari skor tertinggi ke terendah. Kandidat tidak layak tetap dicantumkan beserta alasan penolakannya. Skor total tidak dianggap sebagai perkiraan keuntungan usaha.

## 6. Implementasi dan Hasil

Jalankan `python main.py` dari folder proyek. Program membaca tiga file CSV, menghitung jarak dan skor, menyeleksi kandidat, lalu menghasilkan tiga file di `output/`. Buka `output/laporan_rekomendasi.txt` untuk melihat rekomendasi dan `output/peta_lokasi.svg` untuk memeriksa sebaran titik secara visual.

Peta merupakan visualisasi skematis berorientasi utara dan bukan peta jalan. Lingkaran hijau menunjukkan kandidat layak, merah menunjukkan tidak layak, kotak jingga menunjukkan toko yang sudah ada, dan berlian ungu menunjukkan gudang. Kandidat peringkat tertinggi diberi lingkaran biru.

## 7. Interpretasi Hasil

Kandidat dengan skor terbesar di antara yang memenuhi syarat menjadi prioritas pada **skenario simulasi** ini. Hasil dapat berubah jika bobot kriteria, biaya sewa, titik gudang, atau batas jarak diubah. Lakukan percobaan dengan menaikkan `--min-jarak-toko` dari `0.7` menjadi `1.0` untuk melihat perubahan jumlah kandidat layak. Perbandingan ini menjadi contoh *what-if analysis* dalam GIS.

## 8. Kesimpulan

Analisis GIS sederhana dapat membantu mengolah informasi posisi dan atribut lokasi menjadi pertimbangan pemilihan tempat usaha yang lebih terstruktur. Pemrograman Python memungkinkan perhitungan jarak dan pemeringkatan dilakukan otomatis, sedangkan keluaran CSV dan peta membantu memahami hasil. Proyek ini menghubungkan materi webinar dengan penerapan praktis analisis spasial, pengolahan data, dan pengambilan keputusan berbasis informasi.

## 9. Keterbatasan dan Pengembangan

Seluruh angka bersifat sintetis. Jarak lurus tidak menggambarkan jarak tempuh kendaraan; populasi juga tidak mewakili jumlah pelanggan yang sesungguhnya. Model belum menghitung konektivitas jalan, pola pergerakan warga, izin lokasi, persaingan usaha sebenarnya, atau banjir. Pada proyek lanjutan, pengolahan dapat dipindahkan ke QGIS, menggunakan data resmi, peta jalan serta analisis jaringan/rute dan divalidasi dengan survei lapangan.
