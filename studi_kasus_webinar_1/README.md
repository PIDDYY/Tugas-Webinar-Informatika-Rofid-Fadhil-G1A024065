# Studi Kasus Webinar 1 — Make Sense of Data with Analysis and AI

**Kasus:** Prediksi keterlambatan pembayaran tagihan pelanggan PT Maju Bersama (perusahaan fiktif).

Proyek ini terinspirasi dari webinar pertama, terutama alur **data → informasi → insight → keputusan**, metode **CRISP-DM**, serta contoh perbandingan model **Logistic Regression, Decision Tree, dan Random Forest**. Implementasi dibuat **menggunakan Python**, bukan file workflow KNIME. Dataset sepenuhnya **dummy** dan dibuat untuk latihan.

## Cara menjalankan di Windows

1. Ekstrak ZIP, lalu buka folder proyek di VS Code.
2. Pastikan Python 3 terpasang. Buka terminal pada folder tersebut.
3. Ketik perintah berikut:

```bash
python -m pip install -r requirements.txt
python main.py
```

Jika perintah `python` tidak dikenali di Windows, coba `py`:

```bash
py -m pip install -r requirements.txt
py main.py
```

Jika ingin membuat ulang dataset (opsional):

```bash
python buat_data.py
python main.py
```

## Isi folder

- `STUDI_KASUS.md` — penjelasan kasus, tahapan, dan kaitannya dengan webinar.
- `buat_data.py` — generator data simulasi yang sengaja berisi beberapa duplikat dan nilai kosong.
- `main.py` — pembersihan data, visualisasi, pelatihan, evaluasi, dan prediksi.
- `data/tagihan_dummy.csv` — data dummy, tersedia sejak awal tanpa perlu membuat ulang.
- `hasil/ringkasan_hasil.txt` — ringkasan otomatis setelah kode dijalankan.
- `hasil/perbandingan_model.csv` — akurasi, precision, recall, dan F1.
- `hasil/grafik_status_tagihan.png` — gambaran data.
- `hasil/grafik_perbandingan_model.png` — membandingkan akurasi dan recall.
- `hasil/hasil_prediksi_data_uji.csv` — prediksi atas data uji.
- `hasil/contoh_prediksi_tagihan_baru.csv` — 3 contoh tagihan baru.

## Hal utama yang perlu dijelaskan saat presentasi

Data memiliki 600 tagihan unik dari pelanggan fiktif. Target `terlambat` berisi **1 = terlambat** dan **0 = tepat waktu**. Beberapa data kosong ditangani menggunakan imputasi; duplikat dibuang. Kami membandingkan model klasifikasi untuk mencari pola risiko keterlambatan. **Jangan hanya melihat akurasi**: cek juga *recall* agar tagihan terlambat tidak banyak terlewat. Hasilnya hanya simulasi dan bukan keputusan final terhadap pelanggan.

**Penting:** kolom `hari_bayar_aktual` menunjukkan hari pembayaran yang baru diketahui setelah transaksi. Kolom tersebut **sengaja tidak dipakai sebagai fitur** untuk menghindari *data leakage*.
