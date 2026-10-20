"""K-nearest neighbors berbasis pustaka bawaan Python saja.

PENTING: Pengukuran pada data simulasi hanyalah fitur proksi,
bukan ekstraksi numerik Sentinel-1/2 yang sesungguhnya.
"""
from __future__ import annotations

import csv
import math
import random
from collections import Counter
from pathlib import Path

from buat_dataset import FITUR


def baca_csv(path: Path, berlabel: bool) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"CSV kosong: {path}")
    diperlukan = {"id", *FITUR} | ({"label"} if berlabel else set())
    kurang = diperlukan - rows[0].keys()
    if kurang:
        raise ValueError(f"Kolom CSV tidak ditemukan: {', '.join(sorted(kurang))}")
    for row in rows:
        for fitur in FITUR:
            try:
                row[fitur] = float(row[fitur])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Data {row['id']} pada kolom {fitur} harus angka") from exc
    return rows


def bagi_stratifikasi(rows: list[dict], seed: int, rasio_tes: float = 0.20):
    """Mencegah kelas langka hilang dari bagian pengujian."""
    kelompok: dict[str, list] = {}
    for row in rows:
        kelompok.setdefault(row["label"], []).append(row)
    rng = random.Random(seed)
    latih, tes = [], []
    for label in sorted(kelompok):
        isi = kelompok[label][:]
        if len(isi) < 2:
            raise ValueError(f"Kelas {label} butuh setidaknya 2 baris")
        rng.shuffle(isi)
        n_tes = max(1, min(len(isi) - 1, round(len(isi) * rasio_tes)))
        tes.extend(isi[:n_tes])
        latih.extend(isi[n_tes:])
    rng.shuffle(latih)
    rng.shuffle(tes)
    return latih, tes


class KNN:
    def __init__(self, k: int = 5):
        if k < 1 or k % 2 == 0:
            raise ValueError("k harus bilangan positif ganjil, contoh 3 atau 5")
        self.k = k
        self.latih = []
        self.mean = {}
        self.std = {}

    def fit(self, latih: list[dict]):
        if len(latih) < self.k:
            raise ValueError("Data latih kurang dari nilai k")
        self.latih = latih
        # Normalisasi hanya dengan data LATIH (mencegah data leakage).
        for fitur in FITUR:
            values = [row[fitur] for row in latih]
            mean = sum(values) / len(values)
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
            self.mean[fitur], self.std[fitur] = mean, (std if std > 1e-12 else 1.0)
        return self

    def _jarak(self, a: dict, b: dict) -> float:
        return math.sqrt(sum(
            ((a[f] - b[f]) / self.std[f]) ** 2 for f in FITUR
        ))

    def prediksi(self, row: dict) -> tuple[str, float]:
        """Keluaran kedua ialah porsi suara tetangga, BUKAN probabilitas terkalibrasi."""
        tetangga = sorted(
            ((self._jarak(row, r), r["label"]) for r in self.latih),
            key=lambda d: (d[0], d[1]),
        )[: self.k]
        voting = Counter(label for _, label in tetangga)
        # Jika seri, pakai total jarak terkecil lalu nama label untuk deterministik.
        candidates = sorted(voting, key=lambda c: (
            -voting[c], sum(j for j, label in tetangga if label == c), c
        ))
        label = candidates[0]
        return label, round(voting[label] / self.k, 3)


def metrik(y_true: list[str], y_pred: list[str]) -> dict:
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Label aktual dan prediksi harus sama panjang dan tidak kosong")
    labels = sorted(set(y_true) | set(y_pred))
    confusion = {a: {p: 0 for p in labels} for a in labels}
    for actual, pred in zip(y_true, y_pred):
        confusion[actual][pred] += 1
    benar = sum(a == b for a, b in zip(y_true, y_pred))
    per_kelas = {}
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[a][label] for a in labels if a != label)
        fn = sum(confusion[label][p] for p in labels if p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        per_kelas[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "jumlah_tes": sum(confusion[label].values()),
        }
    return {
        "akurasi": round(benar / len(y_true), 4),
        "macro_f1": round(sum(x["f1"] for x in per_kelas.values()) / len(per_kelas), 4),
        "per_kelas": per_kelas,
        "confusion_matrix": confusion,
        "jumlah_data_tes": len(y_true),
    }
