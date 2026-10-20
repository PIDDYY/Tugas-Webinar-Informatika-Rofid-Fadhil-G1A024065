"""Webinar 4 - contoh supervised machine learning: klasifikasi spam.

Python standard library saja; tidak memerlukan paket pihak ketiga.
Jalankan: python main.py
          python main.py --pesan "Diskon spesial untuk Anda"
"""

import argparse
import csv
import math
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "email_dummy.csv"
OUTPUT_DIR = ROOT / "output"


def tokenisasi(kalimat):
    """Normalisasi sederhana dan ubah pesan menjadi kata-kata."""
    return re.findall(r"[a-z0-9]+", kalimat.lower())


def muat_data(path=DATA_PATH):
    """Baca dataset dan validasi label."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        baris = list(csv.DictReader(f))
    data = []
    for nomor, item in enumerate(baris, start=2):
        label = (item.get("label") or "").strip().lower()
        pesan = (item.get("pesan") or "").strip()
        if label not in {"spam", "normal"} or not pesan:
            raise ValueError(f"Dataset tidak valid di baris {nomor}")
        data.append((pesan, label))
    if not data:
        raise ValueError("Dataset kosong")
    return data


def bagi_data(data, rasio_latih=0.8, seed=42):
    """80% latih, 20% uji secara stratified agar kedua label seimbang."""
    if not 0 < rasio_latih < 1:
        raise ValueError("rasio_latih harus di antara 0 dan 1")
    acak = random.Random(seed)
    kelompok = {"spam": [], "normal": []}
    for item in data:
        kelompok[item[1]].append(item)
    latih, uji = [], []
    for label, item_kelas in kelompok.items():
        if len(item_kelas) < 2:
            raise ValueError(f"Perlu minimal 2 contoh untuk label {label}")
        acak.shuffle(item_kelas)
        batas = max(1, min(len(item_kelas) - 1, round(len(item_kelas) * rasio_latih)))
        latih.extend(item_kelas[:batas])
        uji.extend(item_kelas[batas:])
    acak.shuffle(latih)
    acak.shuffle(uji)
    return latih, uji


class NaiveBayesTeks:
    """Multinomial Naive Bayes dari nol dengan Laplace smoothing."""

    def __init__(self):
        self.label = ("spam", "normal")
        self.jumlah_dokumen = Counter()
        self.frekuensi_kata = {kelas: Counter() for kelas in self.label}
        self.total_kata = Counter()
        self.kosakata = set()

    def latih(self, data):
        if not data:
            raise ValueError("Data latih kosong")
        for pesan, kelas in data:
            self.jumlah_dokumen[kelas] += 1
            kata_kata = tokenisasi(pesan)
            self.frekuensi_kata[kelas].update(kata_kata)
            self.total_kata[kelas] += len(kata_kata)
            self.kosakata.update(kata_kata)
        if any(self.jumlah_dokumen[kelas] == 0 for kelas in self.label):
            raise ValueError("Data latih harus memiliki spam dan normal")
        return self

    def skor_log(self, pesan):
        kata_kata = tokenisasi(pesan)
        total_dokumen = sum(self.jumlah_dokumen.values())
        ukuran_kamus = len(self.kosakata)
        skor = {}
        for kelas in self.label:
            prior = self.jumlah_dokumen[kelas] / total_dokumen
            log_skor = math.log(prior)
            penyebut = self.total_kata[kelas] + ukuran_kamus
            for kata in kata_kata:
                # Kata yang tidak pernah muncul pada pelatihan diabaikan.
                if kata in self.kosakata:
                    jumlah = self.frekuensi_kata[kelas][kata]
                    log_skor += math.log((jumlah + 1) / penyebut)
            skor[kelas] = log_skor
        return skor

    def prediksi(self, pesan):
        skor = self.skor_log(pesan)
        return max(self.label, key=lambda k: skor[k])


def hitung_metrik(y_sebenarnya, y_prediksi):
    """Positive class = spam. Semua metrik dalam skala 0..1."""
    if len(y_sebenarnya) != len(y_prediksi) or not y_sebenarnya:
        raise ValueError("Label uji tidak valid")
    tp = sum(a == "spam" and p == "spam" for a, p in zip(y_sebenarnya, y_prediksi))
    tn = sum(a == "normal" and p == "normal" for a, p in zip(y_sebenarnya, y_prediksi))
    fp = sum(a == "normal" and p == "spam" for a, p in zip(y_sebenarnya, y_prediksi))
    fn = sum(a == "spam" and p == "normal" for a, p in zip(y_sebenarnya, y_prediksi))
    akurasi = (tp + tn) / len(y_sebenarnya)
    presisi = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * presisi * recall / (presisi + recall) if presisi + recall else 0.0
    return {"TP": tp, "TN": tn, "FP": fp, "FN": fn,
            "accuracy": akurasi, "precision": presisi, "recall": recall, "f1": f1}


def format_laporan(total, ukuran_latih, ukuran_uji, metrik):
    return (
        "STUDI KASUS WEBINAR 4 - MACHINE LEARNING\n"
        "Klasifikasi Pesan Spam (Supervised Learning / Naive Bayes)\n"
        f"{'=' * 60}\n"
        f"Total data     : {total}\n"
        f"Data latih     : {ukuran_latih} (80%)\n"
        f"Data uji       : {ukuran_uji} (20%)\n"
        "\nEVALUASI (kelas positif: spam)\n"
        f"Accuracy       : {metrik['accuracy']:.2%}\n"
        f"Precision      : {metrik['precision']:.2%}\n"
        f"Recall         : {metrik['recall']:.2%}\n"
        f"F1 Score       : {metrik['f1']:.2%}\n"
        "\nConfusion matrix:\n"
        "                      Diprediksi Spam   Diprediksi Normal\n"
        f"  Sebenarnya Spam     {metrik['TP']:>5}             {metrik['FN']:>5}\n"
        f"  Sebenarnya Normal   {metrik['FP']:>5}             {metrik['TN']:>5}\n"
        "\nCatatan: hasil berasal dari DATA SINTETIS untuk pembelajaran.\n"
    )


def jalankan(pesan_baru=None):
    data = muat_data()
    latih, uji = bagi_data(data)
    model = NaiveBayesTeks().latih(latih)
    hasil = [(pesan, label, model.prediksi(pesan)) for pesan, label in uji]
    metrik = hitung_metrik([a for _, a, _ in hasil], [p for _, _, p in hasil])
    laporan = format_laporan(len(data), len(latih), len(uji), metrik)
    print(laporan)

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_DIR / "hasil_pengujian.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pesan", "label_asli", "label_prediksi", "benar"])
        for pesan, asli, prediksi in hasil:
            writer.writerow([pesan, asli, prediksi, asli == prediksi])
    (OUTPUT_DIR / "laporan_evaluasi.txt").write_text(laporan, encoding="utf-8")

    print("CONTOH PREDIKSI PESAN BARU")
    contoh = ["Dapatkan voucher promo dan hadiah gratis sekarang",
              "Jadwal rapat kelompok dipindah ke hari Jumat"]
    for pesan in contoh:
        print(f"- {pesan}\n  -> {model.prediksi(pesan).upper()}")
    if pesan_baru:
        print(f"\nPesan yang Anda masukkan: {pesan_baru}")
        print(f"Hasil prediksi: {model.prediksi(pesan_baru).upper()}")
    print(f"\nFile hasil tersimpan di: {OUTPUT_DIR}")
    return metrik


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Klasifikasi teks dengan Naive Bayes")
    parser.add_argument("--pesan", type=str, help="Coba prediksi pesan Anda sendiri")
    argumen = parser.parse_args()
    jalankan(argumen.pesan)
