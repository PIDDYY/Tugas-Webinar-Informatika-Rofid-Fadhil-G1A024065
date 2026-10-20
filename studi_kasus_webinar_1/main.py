"""Studi kasus Webinar 1: prediksi keterlambatan pembayaran tagihan.

Jalankan:
    python main.py

Alur mengikuti CRISP-DM: memahami masalah -> memahami data -> pembersihan
-> pemodelan -> evaluasi -> contoh prediksi tagihan baru.
"""

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")  # Grafik disimpan sebagai PNG, tidak perlu jendela GUI.
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

DIREKTORI = Path(__file__).resolve().parent
FILE_DATA = DIREKTORI / "data" / "tagihan_dummy.csv"
HASIL = DIREKTORI / "hasil"

# Hanya informasi yang SUDAH DIKETAHUI saat tagihan diterbitkan.
FITUR_ANGKA = ["nilai_tagihan", "termin_hari", "riwayat_telat_6bln", "lama_pelanggan_bulan"]
FITUR_KATEGORI = ["segmen_pelanggan"]
FITUR = FITUR_ANGKA + FITUR_KATEGORI
TARGET = "terlambat"


def baca_dan_bersihkan():
    if not FILE_DATA.exists():
        raise FileNotFoundError("Data tidak ada. Jalankan 'python buat_data.py' terlebih dahulu.")

    df = pd.read_csv(FILE_DATA)
    baris_awal = len(df)
    df = df.drop_duplicates(subset="id_invoice").copy()
    duplikat = baris_awal - len(df)

    # Angka salah format menjadi NaN, lalu ditangani oleh SimpleImputer di pipeline.
    for kolom in FITUR_ANGKA:
        df[kolom] = pd.to_numeric(df[kolom], errors="coerce")
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df[TARGET] = df[TARGET].astype(int)
    df["segmen_pelanggan"] = df["segmen_pelanggan"].replace(r"^\s*$", pd.NA, regex=True)

    # Periksa target historis; kolom ini sengaja tidak digunakan sebagai FITUR.
    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Kolom target 'terlambat' harus berisi 0 atau 1.")
    return df, duplikat


def siapkan_pemrosesan():
    angka = Pipeline([
        ("isi_kosong", SimpleImputer(strategy="median")),
        ("normalisasi", StandardScaler()),
    ])
    kategori = Pipeline([
        ("isi_kosong", SimpleImputer(strategy="most_frequent")),
        ("ubah_ke_angka", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("angka", angka, FITUR_ANGKA),
        ("kategori", kategori, FITUR_KATEGORI),
    ])


def hitung_metrik(nama, asli, prediksi):
    return {
        "model": nama,
        "accuracy": accuracy_score(asli, prediksi),
        "precision": precision_score(asli, prediksi, zero_division=0),
        "recall": recall_score(asli, prediksi, zero_division=0),
        "f1_score": f1_score(asli, prediksi, zero_division=0),
    }


def simpan_grafik(data, nilai_metrik):
    jumlah = data[TARGET].value_counts().reindex([0, 1], fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Tepat waktu", "Terlambat"], jumlah.values)
    ax.set_ylabel("Jumlah tagihan")
    ax.set_title("Distribusi status pembayaran (data dummy)")
    fig.tight_layout()
    fig.savefig(HASIL / "grafik_status_tagihan.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    posisi = range(len(nilai_metrik))
    lebar = 0.35
    ax.bar([x - lebar / 2 for x in posisi], nilai_metrik["accuracy"], width=lebar, label="Akurasi")
    ax.bar([x + lebar / 2 for x in posisi], nilai_metrik["recall"], width=lebar, label="Recall terlambat")
    ax.set_xticks(list(posisi), nilai_metrik["model"], rotation=12, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title("Mengapa akurasi saja tidak cukup?")
    ax.legend()
    fig.tight_layout()
    fig.savefig(HASIL / "grafik_perbandingan_model.png", dpi=140)
    plt.close(fig)


def jalankan():
    HASIL.mkdir(exist_ok=True, parents=True)
    df, jumlah_duplikat = baca_dan_bersihkan()
    X = df[FITUR]
    y = df[TARGET]

    # Pembagian 80:20; stratify menjaga proporsi kelas terlambat.
    X_latih, X_uji, y_latih, y_uji, idx_latih, idx_uji = train_test_split(
        X, y, df.index, test_size=0.20, random_state=42, stratify=y
    )

    algoritma = {
        "Baseline mayoritas": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_leaf=10, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, min_samples_leaf=5, class_weight="balanced", random_state=42),
    }

    daftar_hasil = []
    model_terlatih = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        for nama, algoritma_pilih in algoritma.items():
            model = Pipeline([
                ("persiapan", siapkan_pemrosesan()),
                ("algoritma", algoritma_pilih),
            ])
            model.fit(X_latih, y_latih)
            prediksi = model.predict(X_uji)
            daftar_hasil.append(hitung_metrik(nama, y_uji, prediksi))
            model_terlatih[nama] = model

    metrik = pd.DataFrame(daftar_hasil)
    metrik.to_csv(HASIL / "perbandingan_model.csv", index=False, float_format="%.4f")

    # Model terpilih hanya dari tiga algoritma utama (bukan baseline).
    pilihan = metrik[metrik["model"] != "Baseline mayoritas"].sort_values(
        by=["f1_score", "recall"], ascending=False
    ).iloc[0]["model"]
    terbaik = model_terlatih[pilihan]
    prediksi_uji = terbaik.predict(X_uji)
    hasil_uji = df.loc[idx_uji, ["id_invoice", "id_pelanggan", TARGET]].copy()
    hasil_uji["prediksi_terlambat"] = prediksi_uji
    hasil_uji["prediksi_benar"] = (hasil_uji[TARGET] == hasil_uji["prediksi_terlambat"])
    hasil_uji.to_csv(HASIL / "hasil_prediksi_data_uji.csv", index=False)

    # Contoh penggunaan model ketika baru menerbitkan tagihan:
    tagihan_baru = pd.DataFrame([
        {"nilai_tagihan": 8_000_000, "termin_hari": 30, "riwayat_telat_6bln": 0, "lama_pelanggan_bulan": 60, "segmen_pelanggan": "Korporat"},
        {"nilai_tagihan": 65_000_000, "termin_hari": 14, "riwayat_telat_6bln": 4, "lama_pelanggan_bulan": 5, "segmen_pelanggan": "UMKM"},
        {"nilai_tagihan": 22_000_000, "termin_hari": 30, "riwayat_telat_6bln": 2, "lama_pelanggan_bulan": 19, "segmen_pelanggan": "Ritel"},
    ])
    tagihan_baru["prediksi_terlambat"] = terbaik.predict(tagihan_baru)
    tagihan_baru["hasil_prediksi"] = tagihan_baru["prediksi_terlambat"].map({0: "Tepat waktu", 1: "Berisiko terlambat"})
    tagihan_baru.to_csv(HASIL / "contoh_prediksi_tagihan_baru.csv", index=False)

    simpan_grafik(df, metrik)
    tn, fp, fn, tp = confusion_matrix(y_uji, prediksi_uji, labels=[0, 1]).ravel()
    proporsi = 100 * df[TARGET].mean()
    summary = f"""HASIL STUDI KASUS: MAKE SENSE OF DATA WITH ANALYSIS AND AI
=======================================================
Perusahaan                 : PT Maju Bersama (fiktif)
Jumlah tagihan mentah      : {len(df) + jumlah_duplikat}
Duplikat yang dibuang      : {jumlah_duplikat}
Jumlah tagihan bersih      : {len(df)}
Tagihan terlambat          : {df[TARGET].sum()} ({proporsi:.1f}%)
Pembagian data             : {len(X_latih)} latih, {len(X_uji)} uji

Model dengan F1 terbaik    : {pilihan}
Hasil confusion matrix:
- True Positive (TP)       : {tp}  -> terlambat dan diprediksi terlambat
- False Negative (FN)      : {fn}  -> terlambat tetapi lolos dari deteksi
- False Positive (FP)      : {fp}  -> tepat waktu tetapi dianggap terlambat
- True Negative (TN)       : {tn}  -> tepat waktu dan diprediksi tepat waktu

INTERPRETASI
- Akurasi tinggi belum tentu berarti model bagus mendeteksi keterlambatan.
- Recall memperlihatkan berapa banyak tagihan benar-benar terlambat yang terdeteksi.
- Gunakan hasil prediksi sebagai prioritas pengingat pembayaran, bukan hukuman otomatis.
- Ini DATA BUATAN, bukan data asli perusahaan atau hasil penelitian webinar.
- Kolom 'hari_bayar_aktual' dilarang menjadi fitur: baru diketahui setelah tagihan dibayar.
- Model diuji pada pemisahan acak tagihan; untuk produksi perlu validasi lebih kuat.

Lihat: perbandingan_model.csv, grafik_perbandingan_model.png, dan contoh_prediksi_tagihan_baru.csv
"""
    (HASIL / "ringkasan_hasil.txt").write_text(summary, encoding="utf-8")
    print(summary)
    print(metrik.to_string(index=False, float_format=lambda n: f"{n:.3f}"))
    print("\nBerkas hasil tersimpan di folder 'hasil/'.")


if __name__ == "__main__":
    jalankan()
