"""Membuat dataset SINTETIS untuk pembelajaran klasifikasi gangguan hutan.

Semua angka adalah simulasi, bukan pengukuran satelit yang nyata.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FITUR = [
    "indeks_kehilangan_vegetasi", "perubahan_radar", "ketidakteraturan_bentuk",
    "bentuk_memanjang", "indikasi_api", "indikasi_air", "indikasi_galian",
    "kedekatan_jalan", "luas_ha",
]

# Rata-rata contoh buatan yang sengaja cukup mudah dibedakan.
POLA = {
    "Pertanian skala kecil":     (.72, .58, .57, .24, .22, .16, .07, .60, 3.2),
    "Pertanian skala besar":     (.85, .73, .22, .12, .35, .13, .06, .55, 85.0),
    "Penebangan selektif":      (.33, .40, .54, .65, .05, .15, .08, .80, 9.0),
    "Pertambangan":            (.90, .86, .28, .20, .16, .10, .92, .74, 38.0),
    "Pembangunan jalan":       (.77, .65, .15, .95, .07, .12, .10, .81, 5.0),
    "Kebakaran hutan":        (.63, .67, .78, .15, .92, .21, .10, .32, 60.0),
    "Banjir / gangguan alami": (.40, .55, .89, .11, .09, .95, .02, .30, 26.0),
}


def batas_01(x: float) -> float:
    return round(max(0, min(1, x)), 3)


def buat_contoh(rng: random.Random, kategori: str, campur: bool = False) -> dict[str, float]:
    pusat = list(POLA[kategori])
    if campur:
        kategori_lain = rng.choice([k for k in POLA if k != kategori])
        p2 = POLA[kategori_lain]
        campuran = rng.uniform(0.15, 0.34)
        pusat = [(1-campuran)*a + campuran*b for a, b in zip(pusat, p2)]
    hasil = {}
    for i, fitur in enumerate(FITUR):
        if fitur == "luas_ha":
            hasil[fitur] = round(max(0.2, pusat[i] * rng.uniform(0.70, 1.45)), 2)
        else:
            hasil[fitur] = batas_01(pusat[i] + rng.gauss(0, 0.10))
    return hasil


def tulis_csv(path: Path, baris: list[dict], kolom: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolom)
        w.writeheader()
        w.writerows(baris)


def generate(seed: int = 2026) -> tuple[Path, Path]:
    DATA.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    latih = []
    alert = []
    for kelas_idx, kategori in enumerate(POLA):
        for i in range(60):
            row = {"id": f"LAT-{kelas_idx+1:02d}-{i+1:03d}", "label": kategori}
            row.update(buat_contoh(rng, kategori, campur=(i % 11 == 0)))
            latih.append(row)
        for i in range(5):
            # Koordinat grid ini BUKAN lintang/bujur atau peta lokasi sesungguhnya.
            row = {"id": f"ALT-{kelas_idx+1:02d}-{i+1:02d}"}
            row.update(buat_contoh(rng, kategori, campur=(i == 4)))
            row.update({"grid_x": rng.randint(6, 94), "grid_y": rng.randint(7, 92)})
            alert.append(row)
    rng.shuffle(latih)
    rng.shuffle(alert)
    path1 = DATA / "data_berlabel_sintetis.csv"
    path2 = DATA / "alert_baru_sintetis.csv"
    tulis_csv(path1, latih, ["id", "label", *FITUR])
    tulis_csv(path2, alert, ["id", *FITUR, "grid_x", "grid_y"])
    return path1, path2


if __name__ == "__main__":
    a, b = generate()
    print(f"Dataset latihan: {a}")
    print(f"Alert baru:      {b}")
