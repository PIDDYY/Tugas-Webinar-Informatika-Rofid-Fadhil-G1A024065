# Studi Kasus dan Implementasi Kode Sederhana — Webinar 2

## Judul
**Simulasi Risiko Genangan pada Wilayah Bengkulu Menggunakan Monte Carlo dan Parallel Computing**

## Kaitan dengan materi webinar
Dalam webinar *Bridging Global Infrastructure to Address Local Challenges in HPC*, narasumber menjelaskan bahwa *High Performance Computing* (HPC) bukan hanya tentang superkomputer yang sangat cepat, melainkan cara memanfaatkan komputasi untuk menyelesaikan persoalan nyata. Salah satu contoh yang dijelaskan adalah prediksi banjir di Bangladesh. Narasumber juga menyinggung pekerjaan komputasi yang disiapkan lalu dijalankan di mesin HPC menggunakan Linux, SSH, dan penjadwal pekerjaan. Proyek ini mengambil **gagasannya**, bukan meniru sistem peringatan banjir profesional: banyak simulasi independen dibagi ke beberapa proses CPU lokal.

## Latar belakang dan masalah
Bagaimana jika sebuah kawasan ingin menguji banyak kemungkinan hujan untuk melihat seberapa sering genangan dapat melampaui batas ilustratif tertentu? Menghitung satu skenario sangat mudah, tetapi menjalankan ribuan skenario untuk beberapa wilayah menambah beban komputasi. Kita dapat memakai metode **Monte Carlo** (mengulang percobaan dengan input yang bervariasi) serta membandingkan pemrosesan **serial** dan **paralel**.

**Pertanyaan studi kasus:** (1) Berapa persentase skenario hujan sintetis yang menghasilkan genangan melebihi ambang yang ditetapkan? (2) Apakah membagi simulasi ke beberapa proses dapat mempercepat komputasi pada komputer yang digunakan?

## Dataset
CSV berisi 9 nama kecamatan di Kota Bengkulu, dengan parameter buatan yang berbeda pada tiap wilayah: curah hujan acuan per hari, kemampuan resapan per jam, drainase per jam, koefisien limpasan, serta ambang genangan. **Seluruh nilai parameter hanya asumsi pendidikan.** Tidak ada pengukuran lapangan, data curah hujan aktual, elevasi, atau keterhubungan aliran air antarwilayah.

## Metode sederhana
Untuk setiap kecamatan, program menjalankan banyak skenario hujan selama **24 jam**. Total hujan per skenario divariasikan secara acak di sekitar angka acuan. Hujan kemudian dibagi ke 24 jam dengan pola intensitas yang lebih besar di sekitar siang/sore. Program menghitung limpasan dan sisa air pada tiap jam:

```text
limpasan_jam        = hujan_jam × koefisien_limpasan
genangan_jam        = max(0, genangan_sebelumnya + limpasan_jam
                           − resapan_per_jam − kapasitas_drainase_per_jam)
genangan_puncak     = nilai genangan terbesar selama 24 jam
kejadian_melampaui = (genangan_puncak >= ambang_genangan)
persentase_simulasi = jumlah kejadian melampaui ambang / jumlah skenario × 100%
```

Nilai di atas **bukan rumus hidrologi yang telah divalidasi**. Model tidak mengalirkan air antarwilayah, tidak menggunakan peta permukaan tanah, dan tidak menggunakan periode ulang hujan. Karena distribusi hujannya dirancang sendiri, persentase yang dihasilkan **bukan probabilitas banjir yang sebenarnya**.

## Implementasi serial dan paralel
**Serial:** `main.py` memproses seluruh kecamatan satu demi satu menggunakan satu proses Python. **Paralel:** program memakai `ProcessPoolExecutor` untuk membagikan pekerjaan per kecamatan ke beberapa proses CPU. Setiap simulasi menggunakan *random seed* yang ditentukan berdasarkan kode wilayah, nomor skenario, dan seed dasar sehingga hasil **tetap sama** meskipun dijalankan dengan jumlah proses berbeda. Program menghitung waktu kedua cara tersebut untuk perbandingan.

Contoh menjalankan:

```bash
python main.py --skenario 6000 --workers 4 --mode bandingkan
```

Dengan data berukuran kecil, biaya membangkitkan proses tambahan bisa membuat mode paralel lebih lambat. Pada data yang cukup besar dan perangkat yang mendukung, pembagian pekerjaan berpotensi lebih efektif. Ini adalah eksperimen, bukan janji bahwa paralel selalu lebih cepat.

## Tahapan singkat penelitian
Program membaca CSV, memeriksa parameter, membentuk ribuan skenario hujan, menghitung genangan puncak, mengelompokkan hasil ke kategori ilustratif (Rendah <35%, Sedang 35–<65%, Tinggi >=65%), membandingkan waktu serial/paralel, dan menyimpan hasil dalam CSV, grafik SVG, serta laporan teks. Kategori hanya berlaku pada **model sintetis ini** dan tidak menggambarkan tingkat bahaya daerah sebenarnya.

## Interpretasi dan batasan
Semakin tinggi persentase, semakin sering kondisi genangan melampaui ambang **di dalam simulasi**, bukan bukti bahwa wilayah tertentu benar-benar lebih rawan. Untuk kajian banjir nyata diperlukan data curah hujan terukur, kondisi drainase, elevasi, jaringan sungai, pasang-surut, penggunaan lahan, serta kalibrasi dan validasi dengan pengamatan lapangan. Model juga harus mempertimbangkan aliran air antarwilayah dan ketidakpastian hasil.

## Kesimpulan
Studi kasus ini menunjukkan konsep inti HPC secara sederhana: permasalahan lokal diubah menjadi tugas komputasi yang dapat dibagi dan dikerjakan secara independen, lalu hasilnya dikumpulkan menjadi ringkasan yang mudah dibaca. Pada perangkat biasa, konsep tersebut dipelajari lewat **parallel computing** dan **simulasi Monte Carlo**. Jika dikembangkan menjadi sistem ilmiah, metode ini perlu data dan model yang jauh lebih memadai serta infrastruktur komputasi yang sesuai.
