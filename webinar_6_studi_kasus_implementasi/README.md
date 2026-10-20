# Webinar 6 — Studi Kasus & Implementasi Python

**Topik webinar:** Pemantauan perubahan hutan tropis menggunakan citra satelit dan Artificial Intelligence.  
**Narasumber:** Dr. Bart (Wageningen University & Research, Belanda).  
**Studi kasus:** *Klasifikasi Penyebab Langsung Gangguan Hutan dengan K-Nearest Neighbors (KNN)*.

## Apa yang dikerjakan proyek ini?

Program belajar sederhana ini mengklasifikasikan **penyebab langsung** gangguan hutan menjadi tujuh kategori, yaitu pertanian skala kecil, pertanian skala besar, penebangan selektif, pertambangan, pembangunan jalan, kebakaran hutan, dan banjir/gangguan alami. Program juga mengukur kinerja pada data uji serta membuat dashboard HTML yang dapat dibuka **tanpa internet**.

**PENTING:** dataset yang disertakan adalah **data sintetis (buatan)**. Kolom perubahan radar, kehilangan vegetasi, indikasi api, dan sebagainya adalah *fitur simulasi* yang terinspirasi konsep pemantauan satelit, **bukan hasil perhitungan citra Sentinel-1 atau Sentinel-2 yang nyata**. Titik grid pada dashboard juga acak, **bukan koordinat geografis**. Jangan memakai prediksinya untuk pemantauan operasional, penyelidikan ilegalitas, atau kebijakan nyata.

## Cara menjalankan (Windows, macOS, Linux)

1. Pastikan **Python 3.9 atau lebih baru** sudah terpasang.
2. Ekstrak ZIP dan buka folder proyek.
3. Pada Windows, klik dua kali `jalankan_windows.bat`. Atau jalankan melalui terminal:

   ```bash
   python main.py
   ```

4. Hasil akan disimpan di folder `hasil/`:
   - `ringkasan_hasil.txt` — hasil singkat dan akurasi.
   - `hasil_prediksi.csv` — klasifikasi untuk 35 alert buatan.
   - `metrik_evaluasi.json` — akurasi, macro F1, precision/recall/F1 per kelas.
   - `confusion_matrix.csv` — kesalahan dan kebenaran klasifikasi.
   - `dashboard_hasil.html` — buka dengan browser, terdapat filter kategori dan pencarian ID.

**Tidak perlu `pip install`**, karena seluruh kode menggunakan pustaka standar Python.

## Eksperimen sederhana

Coba ubah banyaknya tetangga model KNN, lalu bandingkan hasil:

```bash
python main.py --k 3
python main.py --k 7
```

Coba data buatan baru (tetap deterministik):

```bash
python main.py --buat-ulang-data
```

Untuk membuat ulang datanya saja:

```bash
python buat_dataset.py
```

Untuk menjalankan pengujian otomatis:

```bash
python -m unittest discover -s tests -v
```

## Struktur berkas

```text
webinar_6_studi_kasus_implementasi/
├── README.md
├── STUDI_KASUS.md
├── buat_dataset.py              # membuat dataset latihan dan alert simulasi
├── model_knn.py                 # algoritma KNN dan metrik evaluasi
├── main.py                      # jalankan pipeline dan buat dashboard
├── jalankan_windows.bat
├── data/
│   ├── data_berlabel_sintetis.csv
│   └── alert_baru_sintetis.csv
├── hasil/
│   ├── ringkasan_hasil.txt
│   ├── hasil_prediksi.csv
│   ├── confusion_matrix.csv
│   ├── metrik_evaluasi.json
│   └── dashboard_hasil.html
└── tests/
    └── test_pipeline.py
```

## Kaitannya dengan webinar

Dalam webinar, Dr. Bart menjelaskan bahwa sistem peringatan berbasis citra optik Sentinel-2 dan radar Sentinel-1 dapat menemukan perubahan tutupan hutan, lalu model **Convolutional Neural Network (CNN)** membantu mengenali kemungkinan penyebab langsungnya. Studi kasus ini **menyederhanakan** gagasan tersebut: tidak memproses piksel citra atau membangun CNN, tetapi mencontohkan alur klasifikasi menggunakan **KNN** pada data fitur buatan supaya mudah dipahami mahasiswa pemula.

Untuk sistem sungguhan diperlukan data satelit yang benar, ekstraksi fitur/citra, anotasi terpercaya, evaluasi terpisah menurut wilayah, dan verifikasi lapangan. Hasil klasifikasi cepat juga tidak selalu menjelaskan akar sosial atau ekonomi dari deforestasi.
