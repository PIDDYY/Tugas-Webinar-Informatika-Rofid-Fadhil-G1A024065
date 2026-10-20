"""Mesin simulasi mini: Monte Carlo hujan-genangan, mandiri tanpa pustaka eksternal.

Data dan rumus di proyek ini sengaja disederhanakan untuk pembelajaran.
Bukan model hidrologi yang telah dikalibrasi, dan bukan prakiraan banjir resmi.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

# Bentuk hujan harian sintetis: biasanya lebih kuat di sekitar jam ke-14.
# Deret ini sengaja dibuat tetap agar hasil serial dan paralel identik.
POLA_JAM = tuple(0.55 + 1.7 * math.exp(-((jam - 14) / 4.0) ** 2) for jam in range(24))


@dataclass(frozen=True)
class Wilayah:
    kode: int
    nama: str
    hujan_acuan: float        # mm per hari; angka ilustrasi, bukan hasil ukur
    resapan: float            # kapasitas resapan mm/jam
    drainase: float           # kapasitas drainase mm/jam
    koefisien_limpasan: float # porsi air hujan yang menjadi limpasan (0..1)
    ambang: float             # ambang genangan maksimum dalam mm


def baca_wilayah(lokasi: str | Path) -> list[Wilayah]:
    """Memuat dan memvalidasi parameter 9 wilayah fiktif/ilustratif."""
    with open(lokasi, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        wajib = {
            "kode", "nama_wilayah", "hujan_acuan_mm_hari", "resapan_mm_jam",
            "drainase_mm_jam", "koefisien_limpasan", "ambang_genangan_mm",
        }
        if not wajib.issubset(reader.fieldnames or []):
            raise ValueError("Kolom CSV tidak lengkap. Periksa header file data.")
        wilayah = []
        for row in reader:
            try:
                w = Wilayah(
                    kode=int(row["kode"]),
                    nama=row["nama_wilayah"].strip(),
                    hujan_acuan=float(row["hujan_acuan_mm_hari"]),
                    resapan=float(row["resapan_mm_jam"]),
                    drainase=float(row["drainase_mm_jam"]),
                    koefisien_limpasan=float(row["koefisien_limpasan"]),
                    ambang=float(row["ambang_genangan_mm"]),
                )
            except (KeyError, ValueError, TypeError) as exc:
                raise ValueError(f"Data wilayah tidak valid: {row}") from exc
            if (not w.nama or w.kode <= 0 or w.hujan_acuan <= 0 or w.resapan < 0 or
                w.drainase < 0 or not 0 <= w.koefisien_limpasan <= 1 or w.ambang <= 0 or
                not all(math.isfinite(x) for x in (
                    w.hujan_acuan, w.resapan, w.drainase, w.koefisien_limpasan, w.ambang
                ))):
                raise ValueError(f"Parameter tidak valid untuk wilayah {w.nama!r}.")
            wilayah.append(w)
    if not wilayah:
        raise ValueError("CSV wilayah kosong.")
    if len({w.kode for w in wilayah}) != len(wilayah):
        raise ValueError("Kolom kode harus unik untuk setiap wilayah.")
    return wilayah


def simulasi_hujan(wilayah: Wilayah, indeks_skenario: int, seed: int) -> float:
    """Kembalikan kedalaman genangan puncak (mm) dalam simulasi hujan 24 jam.

    Setiap skenario memakai seed sendiri, sehingga distribusi tugas ke proses
    tidak mengubah angka akhir. Ini penting untuk pemeriksaan hasil HPC.
    """
    angka_seed = seed + wilayah.kode * 1_000_003 + indeks_skenario * 9_176
    acak = random.Random(angka_seed)
    hujan_harian = wilayah.hujan_acuan * acak.uniform(0.35, 1.85)
    bobot = [pola * acak.uniform(0.75, 1.25) for pola in POLA_JAM]
    total_bobot = sum(bobot)
    genangan, puncak = 0.0, 0.0
    kemampuan_kuras = wilayah.resapan + wilayah.drainase

    for b in bobot:
        hujan_jam = hujan_harian * b / total_bobot
        limpasan = hujan_jam * wilayah.koefisien_limpasan
        genangan = max(0.0, genangan + limpasan - kemampuan_kuras)
        puncak = max(puncak, genangan)
    return puncak


def tugas_wilayah(argumen: tuple[Wilayah, int, int]) -> dict:
    """Fungsi pekerja untuk satu wilayah: aman dipakai multiprocessing Windows."""
    wilayah, jumlah_skenario, seed = argumen
    kejadian_melampaui_ambang = 0
    jumlah_genangan = 0.0
    maksimum_genangan = 0.0

    for indeks in range(jumlah_skenario):
        puncak = simulasi_hujan(wilayah, indeks, seed)
        kejadian_melampaui_ambang += (puncak >= wilayah.ambang)
        jumlah_genangan += puncak
        maksimum_genangan = max(maksimum_genangan, puncak)

    peluang = kejadian_melampaui_ambang / jumlah_skenario
    kategori = "Tinggi" if peluang >= 0.65 else "Sedang" if peluang >= 0.35 else "Rendah"
    return {
        "kode": wilayah.kode,
        "nama_wilayah": wilayah.nama,
        "jumlah_skenario": jumlah_skenario,
        "jumlah_melebihi_ambang": kejadian_melampaui_ambang,
        "persentase_skenario_genangan": round(peluang * 100, 2),
        "rata_rata_puncak_genangan_mm": round(jumlah_genangan / jumlah_skenario, 2),
        "puncak_tertinggi_mm": round(maksimum_genangan, 2),
        "kategori_simulasi": kategori,
    }
