# Studi Kasus — Deteksi Pesan Spam Menggunakan Machine Learning

## Latar belakang

Saat menerima banyak pesan, pengguna perlu membedakan pesan biasa dengan pesan promosi yang tidak diinginkan. Pengecekan manual akan menyita waktu. Contoh kecil ini menunjukkan bagaimana komputer dapat **belajar dari data berlabel**, bukan melalui daftar panjang aturan `if-else` untuk setiap pesan.

## Rumusan masalah

Bagaimana membuat program Python sederhana yang mempelajari contoh pesan berlabel `spam` dan `normal`, lalu memprediksi label pesan baru?

## Tujuan

Menerapkan **supervised learning** berupa klasifikasi teks, dengan seluruh tahapan dasar yang dipaparkan dalam webinar: mengumpulkan dan membersihkan data, membagi data, memilih model, melatih model, menguji hasil, lalu membuat prediksi.

## Data dan fitur

Dataset `data/email_dummy.csv` dibuat sendiri untuk latihan, berisi **80 pesan sintetis** dalam Bahasa Indonesia: 40 spam dan 40 normal. Dua kolom tersedia, yaitu `label` sebagai kelas target dan `pesan` sebagai input. Program mengubah teks menjadi huruf kecil dan memecahnya menjadi kata-kata. Frekuensi kata digunakan sebagai fitur. Pesan pada data uji sengaja tidak diperlihatkan kepada model ketika latihan.

## Alur implementasi

1. **Load data:** membaca CSV dan memeriksa bahwa setiap pesan memiliki label valid.
2. **Preprocessing:** mengubah huruf menjadi kecil dan mengambil kata-kata.
3. **Split:** memisahkan data per label menjadi 80% pelatihan dan 20% pengujian (stratified).
4. **Training:** menghitung frekuensi kata berdasarkan label dan mempelajari peluang dengan Naive Bayes.
5. **Evaluasi:** membandingkan label prediksi dengan label asli menggunakan confusion matrix, accuracy, precision, recall, dan F1 score.
6. **Prediksi:** memasukkan kalimat baru menggunakan argumen `--pesan`.

## Mengapa Naive Bayes?

Naive Bayes mudah dipelajari untuk klasifikasi teks, relatif singkat ditulis dengan pustaka standar Python, serta memperlihatkan konsep **belajar dari contoh berlabel** yang dibahas dalam webinar. Laplace smoothing dipakai agar peluang kata yang belum muncul pada satu kelas tidak otomatis menjadi nol. Pilihan ini adalah **contoh implementasi tambahan**, bukan klaim bahwa narasumber mendemonstrasikan kode Naive Bayes yang sama.

## Membaca hasil

- **Accuracy**: proporsi seluruh prediksi yang benar.
- **Precision (spam)**: dari pesan yang diprediksi spam, berapa bagian yang benar spam.
- **Recall (spam)**: dari pesan yang benar-benar spam, berapa bagian yang terdeteksi.
- **F1 Score**: ukuran gabungan precision dan recall.
- **Confusion matrix**: jumlah prediksi benar dan salah pada tiap kelas.

Output tersimpan sebagai berkas teks dan CSV agar mudah diperiksa atau dijadikan bukti tugas. Untuk percobaan lanjutan, ubah isi dataset, tambah pesan dengan variasi kata lebih luas, lalu bandingkan metriknya. Jangan memakai data pribadi orang lain tanpa izin.

## Kesimpulan

Program membuktikan alur dasar *Machine Learning*: data berlabel dipakai untuk membangun model dan data yang tidak dilatih digunakan untuk menguji kemampuan generalisasinya. Kualitas prediksi tetap bergantung pada data, pilihan fitur, dan pengujian; hasil dari dataset sederhana ini belum cukup untuk penerapan nyata.
