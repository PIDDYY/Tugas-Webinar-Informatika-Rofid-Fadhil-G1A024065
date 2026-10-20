# Webinar 4 — Introduction to Machine Learning

**Studi kasus:** Klasifikasi pesan *spam* dan *normal* dengan Python, menggunakan algoritma **Multinomial Naive Bayes** sederhana.

Terinspirasi materi **Taniza binti Tajuddin (UiTM Kedah, Malaysia)** pada webinar *Introduction to Machine Learning*, khususnya contoh klasifikasi spam (*supervised learning*) dan alur data → persiapan → pelatihan → evaluasi → prediksi.

## Syarat

- Python 3.9 atau lebih baru.
- **Tidak perlu menginstal library tambahan** (hanya pustaka bawaan Python).

## Cara menjalankan

1. Ekstrak file ZIP.
2. Buka terminal / Command Prompt di folder `studi_kasus_webinar_4`.
3. Ketik:

   ```bash
   python main.py
   ```

   Di beberapa Windows, dapat menggunakan `py main.py`. Di Linux/macOS, dapat menggunakan `python3 main.py`.

4. Coba prediksi pesan sendiri:

   ```bash
   python main.py --pesan "Dapatkan promo voucher gratis hari ini"
   ```

5. Lihat hasil di folder `output/`:
   - `laporan_evaluasi.txt` — accuracy, precision, recall, F1 score, confusion matrix.
   - `hasil_pengujian.csv` — perbandingan label asli dan hasil prediksi setiap pesan uji.

## Isi berkas

```text
studi_kasus_webinar_4/
├── README.md
├── STUDI_KASUS.md
├── main.py
├── data/
│   └── email_dummy.csv
├── output/
│   ├── laporan_evaluasi.txt
│   └── hasil_pengujian.csv
└── tests/
    └── test_main.py
```

## Ringkasan metode

- **Dataset**: 80 contoh pesan Bahasa Indonesia, dibuat khusus secara sintetis untuk latihan (40 spam, 40 normal).
- **Fitur**: kemunculan kata dalam pesan setelah huruf dibuat kecil dan tanda baca dibuang.
- **Pembagian**: 80% latih dan 20% uji, diacak dengan seed tetap agar hasil konsisten.
- **Algoritma**: Multinomial Naive Bayes yang menghitung peluang kemunculan kata dalam setiap kelas, dengan Laplace smoothing.
- **Evaluasi**: accuracy, precision, recall, F1 score, dan confusion matrix pada data uji yang tidak dipakai melatih model.

Ini adalah **prototipe edukasi**, bukan filter email produksi. Data sengaja kecil dan pola katanya sederhana, sehingga hasil uji tidak membuktikan kualitas untuk email dunia nyata.

## Jalankan pengujian kode (opsional)

```bash
python -m unittest discover -s tests -v
```
