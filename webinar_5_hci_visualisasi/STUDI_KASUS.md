# Studi Kasus & Implementasi — Webinar 5

## A. Identitas materi
**Webinar:** Informatics Practitioner Lecture Series 2026  
**Tema:** Human Computer Interaction and Data Visualization  
**Narasumber:** Arafat Febriandirza, Badan Riset dan Inovasi Nasional (BRIN)

## B. Masalah

Pemilik toko simulasi **Toko Sahabat** memiliki catatan harian dari tiga wilayah: **Bengkulu, Curup, dan Mukomuko**. Catatan berisi kategori barang, jumlah transaksi, omzet penjualan, dan jumlah keluhan. Ketika semua informasi berbentuk tabel CSV, pemilik membutuhkan waktu untuk menemukan perubahan omzet dan kategori dengan penjualan tertinggi. Data yang lengkap belum tentu mudah dipahami oleh orang yang harus cepat mengambil keputusan.

Studi kasus ini berfokus pada rancangan **dashboard penjualan yang mudah digunakan**, bukan sekadar kode untuk menjumlahkan angka. Hal ini berkaitan langsung dengan dua materi webinar: **Human Computer Interaction (HCI/IMK)** dan **Data Visualization**.

## C. Pengguna dan kebutuhannya

**Persona simulasi:** Rina (32 tahun), pengelola toko yang harus memeriksa performa beberapa cabang sebelum rapat pagi. Ia membuka dashboard lewat laptop, tetapi kadang menggunakan telepon seluler. Rina ingin mengetahui omzet periode tertentu, membandingkan kategori produk, dan mengambil data hasil filter tanpa perlu membuka banyak berkas.

**Tugas utama pengguna:**
1. Melihat total omzet, transaksi, keluhan, dan rasio keluhan.
2. Membandingkan omzet harian berdasarkan periode yang dipilih.
3. Mengetahui kategori penjualan paling tinggi.
4. Menyaring data berdasarkan periode, wilayah, atau kategori.
5. Mengunduh data yang sudah disaring sebagai CSV.

**Kebutuhan nonfungsional:** tampilan sederhana, teks terbaca, navigasi keyboard, kontras yang memadai, responsif untuk layar kecil, dan tersedianya tabel angka sebagai alternatif grafik.

## D. Solusi dan pilihan visualisasi

Dashboard menyajikan **empat kartu KPI** agar pengguna segera memahami gambaran umum. **Grafik garis** digunakan untuk melihat perubahan omzet menurut waktu; **grafik batang horizontal** digunakan untuk membandingkan nilai antar-kategori. Keduanya dipilih berdasarkan tujuan analisis, bukan sekadar agar tampil menarik. **Tabel harian** memberikan nilai tepat bagi pengguna yang membutuhkan rincian atau menggunakan teknologi pembaca layar.

**Siklus desain berdasarkan webinar:** analisis kebutuhan → rancangan antarmuka → prototipe → evaluasi. Contoh ini merupakan prototipe fungsional. *Usability testing* dengan pengguna sungguhan **belum dilakukan**, sehingga tidak ada klaim bahwa antarmukanya sudah terbukti optimal.

Beberapa penerapan prinsip IMK:
- **Visibility:** status menyebut jumlah baris dan filter yang sedang aktif; empat KPI diperbarui otomatis.
- **Consistency:** semua filter menggunakan bentuk pilihan yang seragam; satuan omzet selalu Rp.
- **Recognition rather than recall:** pengguna dapat melihat opsi filter, tidak perlu mengingat perintah.
- **User control:** tombol Atur ulang dapat mengembalikan seluruh pilihan.
- **Accessibility:** label form eksplisit, konten semantik, fokus keyboard terlihat, ringkasan tekstual melalui tabel.
- **Minimalism:** hanya dua grafik utama tanpa hiasan 3D yang mengganggu pembacaan data.

## E. Data dan proses perhitungan

Dataset `data/penjualan.csv` adalah **600 baris data buatan** untuk rentang 1 September–20 Oktober 2026 (50 hari × 3 wilayah × 4 kategori). Kolomnya:

| Kolom | Arti |
|---|---|
| tanggal | Tanggal transaksi agregat (YYYY-MM-DD) |
| wilayah | Bengkulu, Curup, atau Mukomuko |
| kategori | Makanan, Minuman, ATK, Perlengkapan |
| transaksi | Jumlah transaksi pada kombinasi tanggal, wilayah, kategori |
| omzet | Nilai penjualan kotor, rupiah |
| keluhan | Banyaknya keluhan pelanggan pada kombinasi tersebut |

Filter diproses dengan menyeleksi baris yang sesuai. Setelah itu dihitung:

- Total omzet = jumlah seluruh `omzet` terpilih.
- Total transaksi = jumlah seluruh `transaksi` terpilih.
- Total keluhan = jumlah seluruh `keluhan` terpilih.
- Rasio keluhan = (total keluhan / total transaksi) × 100%; jika transaksi 0, hasilnya 0%.
- Grafik tren = total omzet setiap tanggal.
- Grafik batang = total omzet setiap kategori.

Contoh: jika pengguna memilih **September 2026 + wilayah Bengkulu + kategori Minuman**, maka sistem hanya memproses baris yang memenuhi ketiga kondisi itu. Indikator, grafik, dan tabel akan menampilkan hasil agregasi dari baris tersebut.

## F. Cara kerja kode

`server.py` menjalankan server HTTP lokal dengan pustaka Python standar. `web/index.html` menyediakan struktur halaman dan label yang dapat diakses, `web/style.css` menata layout yang konsisten dan responsif, sedangkan `web/app.js` membaca CSV, memfilter data, menghitung ringkasan, menggambar SVG grafik garis, menggambar batang per kategori, dan menampilkan tabel rincian. Tombol **Unduh CSV** mengekspor baris yang sedang aktif. `analisis.py` memberi cara alternatif memperoleh ringkasan dari terminal.

Teknologi digunakan tanpa framework eksternal agar penerapan dasar IMK dan visualisasi dapat diamati dengan jelas dan proyek mudah dicoba.

## G. Rencana pengujian pengguna

Untuk evaluasi sederhana (belum dilakukan), ajak 3–5 teman mencoba dashboard tanpa petunjuk rinci dan amati apakah mereka mampu:

1. Menemukan omzet Bengkulu untuk September 2026.
2. Membandingkan omzet kategori Makanan dan Minuman.
3. Mengembalikan filter ke kondisi semula.
4. Mengunduh hasil filter.
5. Menemukan nilai omzet pada tanggal tertentu melalui tabel.

Catat durasi tugas, tingkat keberhasilan, kesalahan klik, dan masukan dari pengguna. Hasilnya bisa dipakai untuk revisi prototipe. Jangan mengarang nilai uji usability; catat hasil setelah pengujian nyata.

## H. Kesimpulan

Kasus ini memperlihatkan bahwa **visualisasi data** bukan hanya membuat grafik, melainkan membantu orang menjawab pertanyaan dari data. Prinsip **HCI** membuat informasi tersebut lebih mudah diakses dan dipahami melalui filter yang jelas, umpan balik, desain konsisten, dan penyediaan alternatif tabel. Dashboard telah dapat dijalankan secara lokal untuk mendemonstrasikan konsep, tetapi data yang dipakai sepenuhnya simulasi dan belum diuji kepada pengguna nyata.
