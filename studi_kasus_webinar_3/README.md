# Webinar 3 — Studi Kasus GIS: Menentukan Lokasi Toko Baru

**Topik webinar:** *Career and Competition in Industrial Era with GIS*  
**Narasumber:** Widi Primadeva (alumni Informatika UNIB; profesional GIS di Selandia Baru)  
**Bahasa:** Python 3.9+  
**Kebutuhan:** Tidak perlu menginstal library tambahan, tidak perlu internet.

## Gambaran singkat

Dalam webinar, narasumber membahas penggunaan GIS untuk memilih lokasi toko, memperkirakan cakupan pelanggan, dan membantu efisiensi logistik. Proyek ini menerapkan **analisis spasial sederhana untuk memilih lokasi toko baru** dari 10 kandidat simulasi di area Bengkulu.

Kriteria simulasi:
- Jumlah penduduk dalam radius 1 km (semakin banyak semakin baik).
- Jarak dari toko yang sudah ada (hindari lokasi terlalu dekat).
- Jarak dari gudang (semakin dekat semakin baik untuk logistik).
- Perkiraan biaya sewa bulanan (semakin murah semakin baik).

**PENTING: SEMUA DATA DUMMY/SINTETIS.** Koordinat, populasi, toko, gudang, dan biaya sewa hanya untuk latihan; bukan pengamatan nyata atau usulan lokasi usaha sesungguhnya.

## Menjalankan kode

1. Pastikan sudah menginstal **Python 3.9 atau lebih baru**.
2. Ekstrak ZIP dan buka folder `studi_kasus_webinar_3`.
3. Di terminal folder tersebut, jalankan:

```bash
python main.py
```

Pada Windows, bisa langsung mengklik dua kali `jalankan_windows.bat` apabila perintah `python` tersedia.

Hasil berada di folder `output/`:
- `hasil_analisis.csv` — tabel penilaian semua kandidat; bisa dibuka di Excel.
- `laporan_rekomendasi.txt` — peringkat, rekomendasi utama dan alasan penolakan.
- `peta_lokasi.svg` — peta skematis; **buka di browser** tanpa memerlukan internet.

## Mengubah parameter dan data

```bash
python main.py --min-jarak-toko 1.0 --max-jarak-gudang 8
```

Silakan edit isi `data/kandidat_lokasi.csv`, `data/toko_eksisting.csv`, atau `data/gudang.csv`, lalu jalankan ulang. Satuan jarak = km; sewa = juta rupiah per bulan. Perhatikan bahwa nilai penduduk adalah angka contoh untuk wilayah radius 1 km, bukan data BPS.

## Menjalankan pengujian kode

```bash
python -m unittest discover -s tests -v
```

## Struktur file

```text
studi_kasus_webinar_3/
├── README.md
├── STUDI_KASUS.md
├── main.py
├── jalankan_windows.bat
├── data/
│   ├── kandidat_lokasi.csv
│   ├── toko_eksisting.csv
│   └── gudang.csv
├── output/
│   ├── hasil_analisis.csv
│   ├── laporan_rekomendasi.txt
│   └── peta_lokasi.svg
└── tests/
    └── test_main.py
```

## Catatan batasan

Perhitungan jarak menggunakan **Haversine** (jarak lurus), **bukan rute kendaraan** dan tidak menggunakan peta jalan. SVG hanya memvisualisasikan koordinat data dummy, tanpa peta dasar jalan. Skor dan bobot merupakan asumsi tugas, bukan metode validasi lokasi komersial. Untuk pengembangan nyata, gunakan data geospasial resmi, QGIS/ArcGIS, integrasi API, survei lapangan, kondisi akses jalan, risiko banjir, dan izin usaha.
