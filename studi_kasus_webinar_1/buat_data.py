"""Membuat contoh data tagihan pelanggan fiktif PT Maju Bersama.

Jalankan hanya jika ingin membuat ulang data:
    python buat_data.py
"""

from pathlib import Path
import random
from datetime import date, timedelta
import csv
import math

LOKASI = Path(__file__).resolve().parent
OUTPUT = LOKASI / "data" / "tagihan_dummy.csv"
SEED = 2026


def sigmoid(angka):
    return 1 / (1 + math.exp(-angka))


def buat_data():
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    awal = date(2024, 7, 1)
    data = []
    pelanggan = {}

    # Karakteristik pelanggan dibuat stabil agar datanya terasa masuk akal.
    for nomor in range(1, 101):
        pelanggan[nomor] = {
            "segmen": rng.choices(["Ritel", "UMKM", "Korporat"], weights=[40, 43, 17])[0],
            "lama": rng.randint(2, 90),
            "risiko": rng.uniform(-0.45, 0.45),
        }

    for nomor in range(1, 601):
        id_pelanggan = rng.randint(1, 100)
        profil = pelanggan[id_pelanggan]
        segmen = profil["segmen"]
        nilai = rng.randint(9, 900) * 100_000  # Rp900.000 s.d. Rp90.000.000
        termin = rng.choice([14, 30, 45])
        riwayat = rng.choices([0, 1, 2, 3, 4], weights=[31, 29, 20, 13, 7])[0]
        lama = profil["lama"]

        peluang = sigmoid(
            -2.35
            + 0.55 * riwayat
            + (0.45 if segmen == "UMKM" else 0.12 if segmen == "Ritel" else -0.3)
            + (0.35 if termin == 14 else -0.15 if termin == 45 else 0)
            + 0.010 * (nilai / 1_000_000)
            - 0.011 * lama
            + profil["risiko"]
        )
        terlambat = int(rng.random() < peluang)
        hari_bayar = termin + rng.randint(1, 30) if terlambat else max(1, termin - rng.randint(0, 12))
        tanggal = awal + timedelta(days=rng.randint(0, 729))

        # Beberapa nilai sengaja dikosongkan agar ada contoh pembersihan data.
        segmen_tampil = "" if rng.random() < 0.025 else segmen
        lama_tampil = "" if rng.random() < 0.03 else lama
        data.append({
            "id_invoice": f"INV{nomor:04d}",
            "id_pelanggan": f"PLG{id_pelanggan:03d}",
            "tanggal_invoice": tanggal.isoformat(),
            "segmen_pelanggan": segmen_tampil,
            "nilai_tagihan": nilai,
            "termin_hari": termin,
            "riwayat_telat_6bln": riwayat,
            "lama_pelanggan_bulan": lama_tampil,
            # Kolom berikut diketahui SETELAH pembayaran, tidak boleh jadi input model.
            "hari_bayar_aktual": hari_bayar,
            "terlambat": terlambat,
        })

    # Duplikat sengaja dibuat untuk simulasi data mentah yang belum bersih.
    for indeks in rng.sample(range(len(data)), 9):
        data.append(data[indeks].copy())
    rng.shuffle(data)

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        penulis.writeheader()
        penulis.writerows(data)
    print(f"Data dummy dibuat: {OUTPUT} ({len(data)} baris termasuk duplikat)")


if __name__ == "__main__":
    buat_data()
