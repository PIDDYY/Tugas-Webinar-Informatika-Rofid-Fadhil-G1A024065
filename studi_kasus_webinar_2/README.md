# Studi Kasus Webinar 2 — HPC untuk Permasalahan Lokal

**Webinar:** *Bridging Global Infrastructure to Address Local Challenges in HPC* — Informatics Practitioner Lecture Series.

**Studi kasus:** Simulasi peluang genangan hujan pada 9 kecamatan di Kota Bengkulu dengan **Monte Carlo** dan **pemrosesan paralel (multiprocessing)** menggunakan Python. Ini contoh kecil cara memecah pekerjaan komputasi menjadi banyak tugas independen, seperti prinsip HPC. **Tidak memerlukan superkomputer.**

> **PENTING:** Nama kecamatan adalah nama wilayah nyata, tetapi **semua angka curah hujan, drainase, resapan, dan hasil adalah DATA DUMMY**. Hasil tidak boleh dipakai sebagai prakiraan cuaca, peta rawan banjir resmi, atau rujukan keputusan keselamatan.

## Menjalankan di Windows (VS Code / terminal)

1. Ekstrak ZIP, buka folder `studi_kasus_webinar_2` di VS Code.
2. Pastikan Python 3.9+ terpasang.
3. Buka terminal, kemudian jalankan:

```bash
python main.py
```

Apabila Windows menggunakan perintah `py`, gunakan `py main.py`. **Tidak perlu instal paket** karena hanya menggunakan pustaka bawaan Python.

### Coba membandingkan 1 CPU dan beberapa CPU

```bash
python main.py --skenario 6000 --workers 4 --mode bandingkan
```

Perintah ini menjalankan simulasi dua kali: pertama **serial (1 proses)**, lalu **paralel (4 proses)**. Hasil prediksi keduanya diperiksa agar **identik**, dan waktu eksekusi dibandingkan. Jika hanya ingin mode tertentu:

```bash
python main.py --mode serial --skenario 2000
python main.py --mode paralel --skenario 2000 --workers 2
```

Hasil tersimpan di folder `hasil/`. Buka `hasil/grafik_risiko.svg` dengan Chrome/Edge untuk melihat grafik; buka file CSV di Excel. Pada data kecil, proses paralel **bisa lebih lambat** akibat biaya membuat proses—ini normal, bukan kegagalan.

Untuk menjalankan pengujian kode:

```bash
python -m unittest discover -s tests -v
```

## Isi paket

- `STUDI_KASUS.md` — latar belakang, masalah, tujuan, rumus model sederhana, alur, pembahasan, keterkaitan HPC, dan keterbatasan.
- `main.py` — program utama dan pembanding waktu serial-versus-paralel.
- `simulasi.py` — fungsi Monte Carlo 24 jam dan validasi data.
- `grafik_svg.py` — membuat grafik batang SVG tanpa instalasi library tambahan.
- `data/wilayah_bengkulu_dummy.csv` — **parameter simulasi fiktif**, bukan data dari BMKG/BPBD.
- `hasil/ringkasan_per_wilayah.csv` — frekuensi skenario yang melampaui ambang per kecamatan.
- `hasil/perbandingan_waktu.csv` — waktu eksekusi serial dan paralel.
- `hasil/grafik_risiko.svg` — grafik batang hasil simulasi.
- `hasil/laporan_hasil.txt` — interpretasi hasil yang bisa dibacakan saat presentasi.
- `tests/test_simulasi.py` — tes reproducibility dan kesamaan hasil serial dan paralel.

## Garis besar presentasi singkat

Kasusnya adalah simulasi kejadian hujan yang mungkin menimbulkan genangan. Komputer menjalankan ribuan skenario acak untuk setiap wilayah dan menghitung seberapa sering ambang genangan terlewati. Karena satu wilayah bisa dihitung independen dari wilayah lain, kita dapat membagi pekerjaan ke beberapa proses CPU. Inilah prinsip dasar *parallel computing* yang digunakan dalam HPC. **Berbeda dari aplikasi prakiraan resmi**, model ini sengaja sangat sederhana dan dipakai hanya untuk latihan teknik komputasi.
