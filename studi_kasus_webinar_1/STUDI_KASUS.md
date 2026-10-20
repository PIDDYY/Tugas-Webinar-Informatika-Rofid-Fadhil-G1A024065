# Studi Kasus: Deteksi Risiko Keterlambatan Pembayaran Pelanggan

## Latar belakang dan rumusan masalah

PT Maju Bersama adalah perusahaan fiktif yang menjual barang melalui pembayaran bertempo. Pemasukan di laporan penjualan belum tentu langsung menjadi uang kas apabila banyak pelanggan membayar terlambat. Tim administrasi ingin mengetahui **tagihan mana yang berisiko terlambat** supaya dapat memberi pengingat lebih awal.

**Pertanyaan:** Dapatkah data riwayat pelanggan dan rincian tagihan membantu memprediksi keterlambatan pembayaran?

## Tujuan

Membuat program sederhana yang membaca data transaksi, membersihkannya, lalu membandingkan tiga algoritma klasifikasi untuk memperkirakan apakah tagihan baru berisiko terlambat dibayar. Hasilnya dapat membantu menyusun prioritas pengingat, bukan digunakan untuk memberi sanksi otomatis.

## Alur CRISP-DM yang diterapkan

**1. Business understanding.** Masalah bisnisnya adalah ketidakpastian pembayaran dan potensi gangguan arus kas. Ukuran keberhasilan model tidak cukup hanya akurasi; kasus terlambat yang tidak terdeteksi juga penting.

**2. Data understanding.** Data dummy berisi ID tagihan, pelanggan, tanggal terbit, segmen pelanggan, nilai tagihan, termin pembayaran, riwayat keterlambatan, lama menjadi pelanggan, hari pembayaran aktual, dan status keterlambatan. Target: `terlambat`, 0 atau 1.

**3. Data preparation.** Duplikat berdasarkan `id_invoice` dibuang; nilai kosong pada angka diisi median, pada kategori diisi nilai paling sering; kategori dikonversi menjadi fitur numerik. Pelatihan dan pengujian dipisah 80:20.

**4. Modeling.** Gunakan Logistic Regression, Decision Tree, Random Forest, dan baseline prediksi kelas mayoritas. Semua model memakai fitur yang sama agar perbandingan lebih adil.

**5. Evaluation.** Hitung accuracy, precision, recall, dan F1-score. Bandingkan dengan baseline dan pilih model utama berdasarkan F1-score. *False negative* adalah tagihan yang nyata-nyata terlambat tetapi tidak terdeteksi.

**6. Deployment (simulasi).** Program menerima tiga contoh tagihan baru dan menampilkan label hasil prediksi. Pemakaian nyata perlu data yang terverifikasi, validasi berkala, pertimbangan keadilan keputusan, dan pemantauan perubahan pola pembayaran.

## Fitur model dan alasan

| Kolom | Fungsi |
|---|---|
| `nilai_tagihan` | Besar nilai transaksi |
| `termin_hari` | Lama jatuh tempo |
| `riwayat_telat_6bln` | Jumlah keterlambatan sebelumnya |
| `lama_pelanggan_bulan` | Lama hubungan pelanggan |
| `segmen_pelanggan` | Segmen Ritel, UMKM, atau Korporat |
| `terlambat` | **Label** yang ingin diprediksi |
| `hari_bayar_aktual` | **Tidak boleh menjadi fitur** karena baru diketahui setelah pembayaran |

`id_invoice`, `id_pelanggan`, dan `tanggal_invoice` hanya dicatat untuk konteks, bukan dimasukkan ke fitur model pada contoh sederhana ini.

## Kesimpulan yang bisa digunakan pada laporan

Proyek ini memperlihatkan bahwa analisis data dapat membantu perusahaan mengubah riwayat transaksi menjadi perkiraan risiko pembayaran. Tahap pembersihan data penting agar model tidak mempelajari data yang keliru. Model dengan akurasi paling tinggi belum tentu terbaik untuk menangkap pelanggan yang terlambat, sehingga metrik recall dan F1 perlu diperhatikan. Hasil model hanya digunakan sebagai masukan untuk keputusan petugas.

**Catatan akademik:** PT Maju Bersama dan semua hasil di ZIP ini adalah simulasi pembelajaran yang meniru tema dan konsep webinar, bukan data maupun hasil analisis asli narasumber.
