"""Studi kasus Webinar 3: analisis lokasi toko berbasis GIS (data SIMULASI).

Seluruh fungsi menggunakan pustaka bawaan Python 3.9+; tidak perlu internet.
Contoh: python main.py --min-jarak-toko 0.7 --max-jarak-gudang 10
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from html import escape
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

EARTH_RADIUS_KM = 6371.0088
BOBOT = {"penduduk": 0.40, "jarak_toko": 0.25, "logistik": 0.20, "sewa": 0.15}


@dataclass(frozen=True)
class Lokasi:
    kode: str
    nama: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Kandidat(Lokasi):
    penduduk_1km: int
    sewa_juta_bulan: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Perkiraan jarak garis lurus di permukaan Bumi (kilometer)."""
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(min(1.0, sqrt(a)))


def skor_skala(nilai: float, minimum: float, maksimum: float) -> float:
    """Normalisasi ke skor 0–100: semakin besar nilainya, semakin tinggi skor."""
    if maksimum <= minimum:
        raise ValueError("Batas maksimum harus lebih besar dari minimum.")
    return 100 * max(0.0, min(1.0, (nilai - minimum) / (maksimum - minimum)))


def baca_csv(jalur: Path, kolom: set[str]) -> list[dict[str, str]]:
    if not jalur.is_file():
        raise FileNotFoundError(f"File data tidak ditemukan: {jalur}")
    with jalur.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not kolom.issubset(reader.fieldnames):
            raise ValueError(f"Kolom pada {jalur.name} tidak lengkap. Wajib: {', '.join(sorted(kolom))}")
        hasil = list(reader)
    if not hasil:
        raise ValueError(f"File data kosong: {jalur}")
    return hasil


def lokasi_dari_baris(baris: dict[str, str]) -> Lokasi:
    obj = Lokasi(baris["kode"].strip(), baris["nama"].strip(), float(baris["lat"]), float(baris["lon"]))
    if not obj.kode or not obj.nama or not (-90 <= obj.lat <= 90 and -180 <= obj.lon <= 180):
        raise ValueError(f"Data lokasi tidak valid: {baris}")
    return obj


def muat_data(folder: Path) -> tuple[list[Kandidat], list[Lokasi], Lokasi]:
    dasar = {"kode", "nama", "lat", "lon"}
    kandidat_baris = baca_csv(folder / "kandidat_lokasi.csv", dasar | {"penduduk_1km", "sewa_juta_bulan"})
    toko_baris = baca_csv(folder / "toko_eksisting.csv", dasar)
    gudang_baris = baca_csv(folder / "gudang.csv", dasar)
    if len(gudang_baris) != 1:
        raise ValueError("File gudang.csv harus memiliki tepat satu baris.")
    kandidat = []
    for baris in kandidat_baris:
        lokasi = lokasi_dari_baris(baris)
        p = int(baris["penduduk_1km"])
        sewa = float(baris["sewa_juta_bulan"])
        if p < 0 or sewa < 0:
            raise ValueError(f"Penduduk atau biaya sewa negatif: {lokasi.kode}")
        kandidat.append(Kandidat(lokasi.kode, lokasi.nama, lokasi.lat, lokasi.lon, p, sewa))
    toko = [lokasi_dari_baris(b) for b in toko_baris]
    gudang = lokasi_dari_baris(gudang_baris[0])
    if len({k.kode for k in kandidat}) != len(kandidat):
        raise ValueError("Kode kandidat tidak boleh duplikat.")
    return kandidat, toko, gudang


def evaluasi(kandidat: list[Kandidat], toko: list[Lokasi], gudang: Lokasi,
            min_jarak_toko: float = 0.7, max_jarak_gudang: float = 10.0) -> list[dict]:
    if not toko:
        raise ValueError("Minimal harus ada satu toko eksisting.")
    if min_jarak_toko < 0 or max_jarak_gudang <= 0:
        raise ValueError("Batas jarak tidak valid.")
    hasil = []
    for k in kandidat:
        jarak_toko = min(haversine_km(k.lat, k.lon, t.lat, t.lon) for t in toko)
        jarak_gudang = haversine_km(k.lat, k.lon, gudang.lat, gudang.lon)
        alasan = []
        if jarak_toko < min_jarak_toko:
            alasan.append("Terlalu dekat toko lain")
        if jarak_gudang > max_jarak_gudang:
            alasan.append("Terlalu jauh dari gudang")
        s_penduduk = skor_skala(k.penduduk_1km, 3000, 10000)
        s_toko = skor_skala(jarak_toko, 0.7, 3.0)
        s_logistik = 100 - skor_skala(jarak_gudang, 0, 8)
        s_sewa = 100 - skor_skala(k.sewa_juta_bulan, 3, 12)
        skor = (BOBOT["penduduk"] * s_penduduk + BOBOT["jarak_toko"] * s_toko
                + BOBOT["logistik"] * s_logistik + BOBOT["sewa"] * s_sewa)
        hasil.append({
            "kode": k.kode, "nama": k.nama, "lat": k.lat, "lon": k.lon,
            "penduduk_1km": k.penduduk_1km, "sewa_juta_bulan": k.sewa_juta_bulan,
            "jarak_toko_km": round(jarak_toko, 3), "jarak_gudang_km": round(jarak_gudang, 3),
            "skor_penduduk": round(s_penduduk, 2), "skor_jarak_toko": round(s_toko, 2),
            "skor_logistik": round(s_logistik, 2), "skor_sewa": round(s_sewa, 2),
            "skor_total": round(skor, 2), "status": "LAYAK" if not alasan else "TIDAK LAYAK",
            "alasan": "; ".join(alasan) if alasan else "Memenuhi syarat awal",
            "peringkat": "",
        })
    # Peringkat khusus kandidat layak; yang tidak layak tetap ditampilkan untuk transparansi.
    hasil.sort(key=lambda r: (r["status"] != "LAYAK", -r["skor_total"], r["kode"]))
    for nomor, r in enumerate((r for r in hasil if r["status"] == "LAYAK"), 1):
        r["peringkat"] = nomor
    return hasil


def simpan_csv(hasil: list[dict], jalur: Path) -> None:
    with jalur.open("w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=list(hasil[0].keys()))
        penulis.writeheader()
        penulis.writerows(hasil)


def simpan_laporan(hasil: list[dict], jalur: Path, min_jarak_toko: float, max_jarak_gudang: float) -> None:
    terpilih = next((r for r in hasil if r["status"] == "LAYAK"), None)
    layak = sum(r["status"] == "LAYAK" for r in hasil)
    lines = [
        "STUDI KASUS GIS: PEMILIHAN LOKASI TOKO (SIMULASI)",
        "=" * 55, "Semua data dan lokasi pada proyek ini adalah DUMMY, bukan hasil survei lapangan.",
        "Jarak dihitung secara garis lurus (Haversine), bukan jarak berkendara.",
        f"Syarat awal: jarak toko >= {min_jarak_toko:.2f} km, jarak gudang <= {max_jarak_gudang:.2f} km.",
        "Bobot: penduduk 40%, jarak ke toko 25%, logistik 20%, biaya sewa 15%.",
        f"Jumlah kandidat: {len(hasil)} | Layak: {layak} | Tidak layak: {len(hasil) - layak}",
        "", "PERINGKAT KANDIDAT LAYAK:",
    ]
    for r in hasil:
        if r["status"] == "LAYAK":
            lines.append(f"{r['peringkat']}. {r['kode']} - {r['nama']} | Skor {r['skor_total']:.2f}/100 | "
                         f"Toko terdekat {r['jarak_toko_km']:.2f} km | Gudang {r['jarak_gudang_km']:.2f} km")
    lines.append("")
    if terpilih:
        lines.append(f"REKOMENDASI: {terpilih['kode']} - {terpilih['nama']} ({terpilih['skor_total']:.2f}/100).")
    else:
        lines.append("Tidak ada kandidat yang memenuhi syarat; ubah parameter secara bertanggung jawab.")
    lines += ["", "KANDIDAT TIDAK LAYAK:"]
    for r in hasil:
        if r["status"] != "LAYAK":
            lines.append(f"- {r['kode']} ({r['nama']}): {r['alasan']}")
    lines += ["", "CATATAN: Hasil hanyalah latihan analisis spasial, bukan rekomendasi bisnis nyata.",
              "Evaluasi dunia nyata membutuhkan data aktual, rute jalan, izin, banjir, pesaing, dan survei lapangan."]
    jalur.write_text("\n".join(lines) + "\n", encoding="utf-8")


def simpan_peta_svg(hasil: list[dict], toko: list[Lokasi], gudang: Lokasi, jalur: Path) -> None:
    """Membuat peta skematis offline tanpa basemap. Arah utara di atas."""
    w, h = 1120, 740
    margin = 82
    semua = [(r["lat"], r["lon"]) for r in hasil] + [(t.lat, t.lon) for t in toko] + [(gudang.lat, gudang.lon)]
    ref_lat = sum(x[0] for x in semua) / len(semua)
    lon_ke_km = 111.32 * cos(radians(ref_lat))
    posisi = [(lon * lon_ke_km, lat * 111.32) for lat, lon in semua]
    xs, ys = [p[0] for p in posisi], [p[1] for p in posisi]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    pad_x, pad_y = max(0.5, (max_x - min_x) * 0.13), max(0.5, (max_y - min_y) * 0.13)
    min_x, max_x, min_y, max_y = min_x - pad_x, max_x + pad_x, min_y - pad_y, max_y + pad_y
    scale = min((w - 2 * margin) / (max_x - min_x), (h - 2 * margin) / (max_y - min_y))
    ox = (w - (max_x - min_x) * scale) / 2
    oy = (h - (max_y - min_y) * scale) / 2

    def xy(lat: float, lon: float) -> tuple[float, float]:
        return ox + (lon * lon_ke_km - min_x) * scale, h - (oy + (lat * 111.32 - min_y) * scale)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<rect width="100%" height="100%" fill="#f7f9fc"/>',
           '<text x="52" y="43" font-family="Arial" font-size="22" font-weight="bold" fill="#1c334a">Peta Sebaran Kandidat Lokasi (Data Simulasi)</text>',
           '<text x="52" y="66" font-family="Arial" font-size="13" fill="#536a81">Koordinat ilustratif area Bengkulu • bukan peta jalan • arah utara di atas</text>']
    for i in range(6):
        xx = ox + ((max_x - min_x) * scale) * i / 5
        yy = oy + ((max_y - min_y) * scale) * i / 5
        svg.extend([f'<line x1="{xx:.1f}" y1="{oy:.1f}" x2="{xx:.1f}" y2="{h-oy:.1f}" stroke="#dfe6ed"/>',
                    f'<line x1="{ox:.1f}" y1="{yy:.1f}" x2="{w-ox:.1f}" y2="{yy:.1f}" stroke="#dfe6ed"/>'])
    # Gudang (berlian) dan toko eksisting (kotak).
    gx, gy = xy(gudang.lat, gudang.lon)
    svg.append(f'<polygon points="{gx:.1f},{gy-13:.1f} {gx+13:.1f},{gy:.1f} {gx:.1f},{gy+13:.1f} {gx-13:.1f},{gy:.1f}" fill="#7250ad" stroke="white" stroke-width="2"/>')
    svg.append(f'<text x="{gx+16:.1f}" y="{gy-13:.1f}" font-family="Arial" font-size="13" font-weight="bold" fill="#593b8c">Gudang</text>')
    for t in toko:
        x, y = xy(t.lat, t.lon)
        svg.append(f'<rect x="{x-8:.1f}" y="{y-8:.1f}" width="16" height="16" fill="#ec9741" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{x+11:.1f}" y="{y+4:.1f}" font-family="Arial" font-size="12" fill="#7a4f21">{escape(t.kode)}</text>')
    terbaik = next((r for r in hasil if r["status"] == "LAYAK"), None)
    for r in reversed(hasil):
        x, y = xy(r["lat"], r["lon"])
        bagus = r["status"] == "LAYAK"
        color = "#267d68" if bagus else "#c9575c"
        if r is terbaik:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="none" stroke="#2479a9" stroke-width="3" stroke-dasharray="5 3"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{x+13:.1f}" y="{y-9:.1f}" font-family="Arial" font-size="13" font-weight="bold" fill="#243e50">{escape(r["kode"])}</text>')
    svg.append('<text x="994" y="105" font-family="Arial" font-weight="bold" font-size="16" fill="#34495e">N ↑</text>')
    # Bilah skala 1 kilometer garis lurus.
    bar_px = scale
    bx, by = 70, h - 70
    svg += [f'<line x1="{bx}" y1="{by}" x2="{bx+bar_px:.1f}" y2="{by}" stroke="#34495e" stroke-width="4"/>',
            f'<line x1="{bx}" y1="{by-7}" x2="{bx}" y2="{by+7}" stroke="#34495e" stroke-width="2"/>',
            f'<line x1="{bx+bar_px:.1f}" y1="{by-7}" x2="{bx+bar_px:.1f}" y2="{by+7}" stroke="#34495e" stroke-width="2"/>',
            f'<text x="{bx}" y="{by-12}" font-family="Arial" font-size="12" fill="#34495e">1 km (garis lurus)</text>']
    svg += ['<rect x="741" y="615" rx="9" width="336" height="100" fill="white" stroke="#dee5ed"/>',
            '<circle cx="760" cy="634" r="7" fill="#267d68"/><text x="777" y="638" font-family="Arial" font-size="12">Layak</text>',
            '<circle cx="874" cy="634" r="7" fill="#c9575c"/><text x="891" y="638" font-family="Arial" font-size="12">Tidak layak</text>',
            '<rect x="753" y="653" width="14" height="14" fill="#ec9741"/><text x="777" y="665" font-family="Arial" font-size="12">Toko eksisting</text>',
            '<polygon points="883,651 893,661 883,671 873,661" fill="#7250ad"/><text x="902" y="665" font-family="Arial" font-size="12">Gudang</text>',
            '<text x="755" y="695" font-family="Arial" font-size="12" fill="#2479a9">Lingkaran biru: rekomendasi teratas</text>',
            '</svg>']
    jalur.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis lokasi toko berbasis GIS (DATA DUMMY)")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    parser.add_argument("--min-jarak-toko", type=float, default=0.7, metavar="KM")
    parser.add_argument("--max-jarak-gudang", type=float, default=10.0, metavar="KM")
    args = parser.parse_args()
    try:
        kandidat, toko, gudang = muat_data(args.data_dir)
        hasil = evaluasi(kandidat, toko, gudang, args.min_jarak_toko, args.max_jarak_gudang)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        simpan_csv(hasil, args.output_dir / "hasil_analisis.csv")
        simpan_laporan(hasil, args.output_dir / "laporan_rekomendasi.txt", args.min_jarak_toko, args.max_jarak_gudang)
        simpan_peta_svg(hasil, toko, gudang, args.output_dir / "peta_lokasi.svg")
        print((args.output_dir / "laporan_rekomendasi.txt").read_text(encoding="utf-8"))
        print("Buka output/peta_lokasi.svg di browser untuk melihat peta skematis.")
    except (ValueError, FileNotFoundError) as e:
        parser.exit(2, f"Kesalahan: {e}\n")


if __name__ == "__main__":
    main()
