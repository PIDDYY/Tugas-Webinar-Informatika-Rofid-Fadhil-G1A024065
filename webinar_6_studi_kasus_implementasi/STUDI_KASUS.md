# Studi Kasus Webinar 6: Menentukan Penyebab Gangguan Hutan

## Latar Belakang

Hutan tropis penting untuk menjaga cadangan karbon, keseimbangan air, dan keanekaragaman hayati. Dalam webinar, Dr. Bart dari Wageningen University & Research menjelaskan pemantauan kehilangan tutupan hutan dengan citra satelit. Sistem peringatan mampu menunjukkan **lokasi terjadinya perubahan**, tetapi tidak otomatis memberi tahu **penyebab langsungnya**. Perubahan tersebut dapat terjadi karena pertanian, pertambangan, penebangan, pembangunan jalan, kebakaran, ataupun gangguan alami. Dalam riset narasumber, data satelit Sentinel-1 (radar) dan Sentinel-2 (optik) digabungkan menggunakan *deep learning* berbasis **CNN** untuk mengklasifikasikan penyebab langsungnya.

## Permasalahan

Bagaimana menerapkan **contoh sederhana** klasifikasi penyebab gangguan hutan agar mahasiswa memahami tahap persiapan data, pembagian data latih dan uji, prediksi, pengukuran hasil, dan visualisasi?

## Tujuan

Membuat program Python sederhana yang membaca dataset berlabel, mempelajari pola tujuh jenis gangguan menggunakan KNN, menguji model pada data yang tidak dipakai untuk pelatihan, dan memprediksi alert baru dalam bentuk tabel serta dashboard interaktif.

## Data yang Digunakan

Program memakai data sintetis yang dibangun oleh `buat_dataset.py`, yaitu **420 baris data berlabel** (60 contoh per kelas) dan **35 alert baru**. Fitur sintetisnya adalah indeks kehilangan vegetasi, perubahan radar, ketidakteraturan bentuk, bentuk memanjang, indikasi api, indikasi air, indikasi galian, kedekatan jalan, dan luas area (ha). Nilai 0–1 digunakan sebagai intensitas indikator simulasi; luas area memakai satuan hektare. **Data bukan observasi satelit ataupun hasil survei lapangan.** Keluaran grid_x/grid_y adalah koordinat buatan untuk menampilkan ilustrasi titik, bukan koordinat Bumi.

## Metode dan Alur Implementasi

Program membagi data berlabel menjadi sekitar 80% data latih dan 20% data uji **secara stratifikasi** agar setiap kategori terwakili. Fitur angka dinormalisasi menggunakan rata-rata dan simpangan baku **dari data latih saja**. Setelah itu digunakan algoritma **K-Nearest Neighbors (KNN)** dengan nilai `k=5`. Model mencari lima contoh data latih yang paling dekat dengan setiap alert baru dan memilih kategori yang paling banyak muncul di lima tetangga tersebut. Jika jumlah suara kategori sama, model memilih kategori dengan jumlah jarak yang lebih kecil. Angka `skor_tetangga` berarti proporsi suara tetangga terpilih, **bukan probabilitas terkalibrasi**.

Pengujian dilakukan pada 84 data uji sintetis yang tidak muncul di data latih. Program menghitung *accuracy*, *precision*, *recall*, dan *macro F1*, serta *confusion matrix*. Hasil prediksi 35 alert baru ditulis ke CSV. Program menghasilkan berkas HTML yang menampilkan metrik, jumlah prediksi menurut kategori, titik pada grid simulasi, dan tabel hasil yang bisa difilter. **Tidak ada klaim hasil akurasi tertentu sebelum skrip dijalankan**, karena angka hasil harus dihitung oleh program.

## Contoh Interpretasi

Jika sebuah alert buatan memiliki indikasi galian tinggi dan pola area yang luas, model mungkin mengelompokkannya sebagai **pertambangan**. Jika indikasi api tinggi, model mungkin menghasilkan kategori **kebakaran hutan**. Namun interpretasi sebenarnya juga bergantung pada seluruh fitur dan jarak terhadap data latih. Dengan demikian, hasil model harus dipahami sebagai **prediksi berdasarkan pola dalam dataset simulasi**, bukan kepastian tentang kegiatan nyata di lokasi tertentu.

## Kesimpulan

Studi kasus ini mencontohkan bagaimana gagasan klasifikasi gangguan hutan dalam webinar dapat diterapkan melalui program yang ringan. Mahasiswa dapat mempelajari tahap pengumpulan data (simulasi), pelatihan klasifikasi, evaluasi, hingga penyajian hasil. **Batasan utama:** riset webinar memakai analisis citra Sentinel dan CNN, sedangkan latihan ini memakai fitur numerik sintetis dan KNN. Keduanya tidak setara dalam tingkat kesulitan maupun validitas ilmiah. Pada penelitian sesungguhnya dibutuhkan citra asli, label terverifikasi, evaluasi lebih ketat, dan pengamatan lapangan agar hasil dapat dipertanggungjawabkan.
