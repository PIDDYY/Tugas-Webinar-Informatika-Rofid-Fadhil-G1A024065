"""Webinar 2: versi mini High Performance Computing dengan simulasi paralel.

Jalankan: python main.py
Contoh:   python main.py --skenario 6000 --workers 4 --mode bandingkan
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from grafik_svg import buat_grafik
from simulasi import baca_wilayah, tugas_wilayah

AKAR = Path(__file__).resolve().parent
DATA_BAWAAN = AKAR / "data" / "wilayah_bengkulu_dummy.csv"
KOLOM_HASIL = [
    "kode", "nama_wilayah", "jumlah_skenario", "jumlah_melebihi_ambang",
    "persentase_skenario_genangan", "rata_rata_puncak_genangan_mm",
    "puncak_tertinggi_mm", "kategori_simulasi",
]


def jalankan_simulasi(daftar_wilayah, jumlah: int, seed: int, pekerja: int):
    """Pekerja=1 diproses berurutan; >1 memakai banyak proses CPU."""
    pekerjaan = [(w, jumlah, seed) for w in daftar_wilayah]
    mulai = time.perf_counter()
    if pekerja == 1:
        hasil = [tugas_wilayah(p) for p in pekerjaan]
    else:
        with ProcessPoolExecutor(max_workers=pekerja) as executor:
            hasil = list(executor.map(tugas_wilayah, pekerjaan))
    lama = time.perf_counter() - mulai
    return hasil, lama


def simpan_csv(lokasi: Path, data: list[dict], kolom: list[str]) -> None:
    with lokasi.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=kolom)
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulasi HPC sederhana untuk risiko genangan (data fiktif).")
    parser.add_argument("--data", type=Path, default=DATA_BAWAAN, help="Lokasi file data CSV")
    parser.add_argument("--skenario", type=int, default=2000, help="Simulasi hujan per wilayah (default: 2000)")
    parser.add_argument("--workers", type=int, default=2, help="Jumlah proses CPU untuk mode paralel (default: 2)")
    parser.add_argument("--seed", type=int, default=2026, help="Nilai acak awal, agar eksperimen berulang")
    parser.add_argument("--mode", choices=("serial", "paralel", "bandingkan"), default="bandingkan")
    opsi = parser.parse_args()
    if opsi.skenario < 1 or opsi.skenario > 1_000_000:
        parser.error("--skenario harus antara 1 dan 1.000.000.")
    if opsi.workers < 1 or opsi.workers > 32:
        parser.error("--workers harus antara 1 dan 32.")
    if opsi.mode != "serial" and opsi.workers < 2:
        parser.error("Mode paralel/bandingkan membutuhkan --workers minimal 2.")

    wilayah = baca_wilayah(opsi.data)
    if opsi.mode == "serial":
        hasil, waktu_utama = jalankan_simulasi(wilayah, opsi.skenario, opsi.seed, 1)
        waktu_serial, waktu_paralel = waktu_utama, None
    elif opsi.mode == "paralel":
        hasil, waktu_utama = jalankan_simulasi(wilayah, opsi.skenario, opsi.seed, opsi.workers)
        waktu_serial, waktu_paralel = None, waktu_utama
    else:
        serial, waktu_serial = jalankan_simulasi(wilayah, opsi.skenario, opsi.seed, 1)
        hasil, waktu_paralel = jalankan_simulasi(wilayah, opsi.skenario, opsi.seed, opsi.workers)
        if serial != hasil:
            raise RuntimeError("Pemeriksaan gagal: hasil serial dan paralel tidak sama!")

    tujuan = AKAR / "hasil"
    tujuan.mkdir(parents=True, exist_ok=True)
    simpan_csv(tujuan / "ringkasan_per_wilayah.csv", hasil, KOLOM_HASIL)
    buat_grafik(hasil, tujuan / "grafik_risiko.svg")

    perbandingan = []
    if waktu_serial is not None:
        perbandingan.append({"mode": "Serial (1 proses)", "jumlah_proses": 1, "waktu_detik": f"{waktu_serial:.4f}"})
    if waktu_paralel is not None:
        perbandingan.append({"mode": "Paralel", "jumlah_proses": opsi.workers, "waktu_detik": f"{waktu_paralel:.4f}"})
    simpan_csv(tujuan / "perbandingan_waktu.csv", perbandingan, ["mode", "jumlah_proses", "waktu_detik"])

    catatan = [
        "HASIL STUDI KASUS WEBINAR 2 — MINI HPC",
        "Judul webinar: Bridging Global Infrastructure to Address Local Challenges in HPC",
        "Studi kasus: simulasi peluang genangan menggunakan Monte Carlo + multiprocessing.",
        "CATATAN: Seluruh angka merupakan asumsi/sintetis, bukan pengukuran atau prakiraan banjir.",
        "",
        f"Jumlah wilayah: {len(wilayah)}",
        f"Jumlah simulasi per wilayah: {opsi.skenario}",
        f"Total simulasi: {len(wilayah) * opsi.skenario}",
        f"Mode: {opsi.mode}",
        f"Seed: {opsi.seed}",
        "",
        "PERSENTASE SKENARIO DENGAN GENANGAN DI ATAS AMBANG (BUKAN RISIKO RESMI):",
    ]
    for h in sorted(hasil, key=lambda x: -x["persentase_skenario_genangan"]):
        catatan.append(f"- {h['nama_wilayah']}: {h['persentase_skenario_genangan']:.2f}% ({h['kategori_simulasi']})")
    catatan += ["", "KECEPATAN PENGOLAHAN:"]
    if waktu_serial is not None:
        catatan.append(f"- Serial: {waktu_serial:.4f} detik")
    if waktu_paralel is not None:
        catatan.append(f"- Paralel ({opsi.workers} proses): {waktu_paralel:.4f} detik")
    if waktu_serial is not None and waktu_paralel is not None:
        catatan.append(f"- Faktor percepatan (serial / paralel): {waktu_serial / waktu_paralel:.2f}x")
        catatan.append("- Cek hasil serial == paralel: LULUS (identik)")
    catatan += [
        "", "INTERPRETASI:",
        "Angka merupakan frekuensi kejadian yang melewati ambang dalam kumpulan hujan sintetis.",
        "Nilai lebih tinggi hanya berarti lebih sering tergenang MENURUT ASUMSI MODEL INI.",
        "Paralel dapat lebih lambat pada tugas kecil karena ada biaya memulai proses.",
        "Tidak memperhitungkan topografi, aliran antarkawasan, tanah nyata, sungai, pasang laut, atau data BMKG.",
    ]
    (tujuan / "laporan_hasil.txt").write_text("\n".join(catatan) + "\n", encoding="utf-8")

    print("\n".join(catatan))
    print("\nFile hasil tersedia dalam folder 'hasil/'. Buka grafik_risiko.svg di browser.")


if __name__ == "__main__":
    # Wajib untuk membuat proses paralel di Windows (tidak berjalan rekursif).
    import multiprocessing
    multiprocessing.freeze_support()
    main()
