"""Jalankan: python main.py

Studi kasus WEBINAR 6: contoh sederhana mendeteksi penyebab langsung
gangguan hutan memakai fitur buatan, bukan citra Sentinel yang asli.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from html import escape
from pathlib import Path

from buat_dataset import FITUR, generate
from model_knn import KNN, bagi_stratifikasi, baca_csv, metrik

ROOT = Path(__file__).resolve().parent
COLORS = {
    "Pertanian skala kecil": "#7ccf91",
    "Pertanian skala besar": "#2f9960",
    "Penebangan selektif": "#daa25b",
    "Pertambangan": "#9879dc",
    "Pembangunan jalan": "#57a1df",
    "Kebakaran hutan": "#ea7368",
    "Banjir / gangguan alami": "#60bacb",
}


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, columns)
        writer.writeheader()
        writer.writerows(rows)


def buat_html(hasil: list[dict], evaluasi: dict, dest: Path, n_train: int, k: int):
    by_class = Counter(item["prediksi"] for item in hasil)
    cols = []
    for label, color in COLORS.items():
        count = by_class[label]
        panjang = (count / max(1, len(hasil))) * 100
        cols.append(
            f'<div class="barrow"><span>{escape(label)}</span>'
            f'<div class="barbg"><div style="width:{panjang:.2f}%;background:{color}"></div></div>'
            f'<strong>{count}</strong></div>'
        )
    warna = COLORS
    dots = []
    for row in hasil:
        x = float(row.get("grid_x", 50))
        y = float(row.get("grid_y", 50))
        title = escape(f"{row['id']}: {row['prediksi']}")
        # Koordinat sintetis: ini visualisasi GRID, bukan koordinat asli.
        dots.append(
            f'<circle data-category="{escape(row["prediksi"], quote=True)}" '
            f'cx="{x:.2f}" cy="{y:.2f}" r="2.2" fill="{warna[row["prediksi"]]}" '
            f'stroke="#102336" stroke-width="0.28"><title>{title}</title></circle>'
        )
    trs = []
    for row in hasil:
        lab = escape(row["prediksi"])
        trs.append(
            f'<tr data-category="{escape(row["prediksi"], quote=True)}">'
            f'<td>{escape(row["id"])}</td><td><span class="dot" '
            f'style="background:{warna[row["prediksi"]]}"></span>{lab}</td>'
            f'<td>{int(round(row["skor_tetangga"] * 100))}%</td>'
            f'<td>{row["luas_ha"]:.2f}</td></tr>'
        )
    options = ''.join(f'<option value="{escape(l, quote=True)}">{escape(l)}</option>' for l in COLORS)
    page = '''<!doctype html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simulasi Pemantauan Gangguan Hutan - Webinar 6</title>
<style>
:root{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;color:#e9eff7;background:#0b1522;line-height:1.5}
*{box-sizing:border-box}body{margin:0}main{max-width:1100px;margin:auto;padding:32px 20px 64px}
h1{margin:10px 0 6px;font-size:clamp(26px,4vw,38px);line-height:1.18}h2{margin:0 0 16px;font-size:19px}
p{color:#b5c6d8;margin:8px 0}small{color:#adc4d7}.tag{display:inline-flex;background:#173e37;color:#93f0c3;padding:5px 12px;border-radius:30px;font-weight:700;font-size:12px;letter-spacing:.04em}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:22px 0}
.card,.panel{background:#132337;border:1px solid #284158;border-radius:16px;padding:20px}
.value{font-size:30px;font-weight:800;color:#f6fafd}.label{font-size:13px;color:#a9bfd0}
.layout{display:grid;grid-template-columns:1.15fr 1fr;gap:15px}.barrow{display:grid;grid-template-columns:155px 1fr 32px;gap:10px;align-items:center;margin:12px 0;font-size:12px}
.barbg{background:#263b4e;height:12px;overflow:hidden;border-radius:30px}.barbg>div{height:100%;border-radius:30px}
svg{width:100%;height:auto;background:#0c1c2d;border:1px solid #395168;border-radius:12px}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:22px 0 12px}
select,input{background:#172d42;color:#fff;border:1px solid #466178;border-radius:9px;padding:10px;max-width:100%}
.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:610px}th,td{text-align:left;padding:11px;border-bottom:1px solid #30475d;font-size:13px}th{color:#b6d7dc}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:9px}
.note{margin-top:18px;padding:14px 16px;border-left:3px solid #e5af60;background:#292b35;border-radius:6px;color:#f0d5a8;font-size:13px}
footer{margin-top:30px;color:#93a7bb;font-size:12px}
@media(max-width:800px){.layout{grid-template-columns:1fr}.cards{grid-template-columns:1fr}.barrow{grid-template-columns:142px 1fr 28px}}
</style></head><body><main>
<div class="tag">STUDI KASUS WEBINAR 6 · DATA SIMULASI</div>
<h1>Memahami penyebab perubahan hutan dengan AI sederhana</h1>
<p>Klasifikasi penyebab langsung gangguan hutan dari fitur sintetis yang terinspirasi citra radar dan optik.</p>
<div class="cards">
<div class="card"><div class="label">Akurasi data uji</div><div class="value">__ACCURACY__%</div><small>Data uji terpisah dari data latih</small></div>
<div class="card"><div class="label">Macro F1</div><div class="value">__F1__</div><small>Rata-rata F1 antar kelas</small></div>
<div class="card"><div class="label">Alert simulasi</div><div class="value" id="jumlah-alert">__COUNT__</div><small>Diprediksi menggunakan KNN (k=__K__)</small></div>
</div>
<div class="layout"><section class="panel"><h2>Persebaran hasil klasifikasi</h2>__BARS__
<p><small>Jumlah alert baru per kelas hasil prediksi.</small></p></section>
<section class="panel"><h2>Lokasi pada grid simulasi</h2>
<svg viewBox="0 0 100 100" aria-label="Persebaran alert di grid sintetis" role="img">
<g stroke="#21394e" stroke-width=".25"><path d="M20 0V100 M40 0V100 M60 0V100 M80 0V100 M0 20H100 M0 40H100 M0 60H100 M0 80H100"/></g>
__DOTS__</svg><p><small>Posisi titik adalah koordinat grid acak, BUKAN lokasi geografis atau peta yang sebenarnya.</small></p>
</section></div>
<section class="panel" style="margin-top:16px"><h2>Daftar alert baru</h2>
<div class="toolbar"><label for="kategori">Kategori</label><select id="kategori"><option value="">Semua kategori</option>__OPTIONS__</select>
<label for="cari">Cari ID</label><input id="cari" placeholder="Contoh: ALT-01" type="search"></div>
<div class="tablewrap"><table><thead><tr><th>ID alert</th><th>Prediksi penyebab</th><th>Suara tetangga</th><th>Luas (ha)</th></tr></thead>
<tbody>__ROWS__</tbody></table></div>
<div class="note"><strong>Catatan penting:</strong> Semua data dan grid adalah buatan untuk belajar, bukan pemantauan hutan sungguhan. "Suara tetangga" menggambarkan persentase voting model KNN, bukan probabilitas maupun tingkat kepercayaan ilmiah. Model ini TIDAK dapat digunakan untuk penegakan hukum atau keputusan lingkungan nyata.</div>
</section><footer>__TRAIN__ data latih · __TEST__ data uji · Python standar tanpa library eksternal</footer>
</main><script>
const sel=document.getElementById('kategori'),cari=document.getElementById('cari');
function filter(){
  const kategori=sel.value,query=cari.value.trim().toLowerCase();let count=0;
  document.querySelectorAll('tbody tr').forEach(tr=>{
    const ok=(!kategori||tr.dataset.category===kategori)&&tr.cells[0].textContent.toLowerCase().includes(query);
    tr.hidden=!ok;if(ok)count++;
  });
  document.querySelectorAll('svg circle[data-category]').forEach(c=>{c.style.opacity=(!kategori||c.dataset.category===kategori)?1:.08});
  document.getElementById('jumlah-alert').textContent=count;
}
sel.addEventListener('change',filter);cari.addEventListener('input',filter);
</script></body></html>'''
    replace = {
        "__ACCURACY__": f"{evaluasi['akurasi'] * 100:.1f}",
        "__F1__": f"{evaluasi['macro_f1']:.3f}",
        "__COUNT__": str(len(hasil)),
        "__K__": str(k),
        "__BARS__": ''.join(cols),
        "__DOTS__": '\n'.join(dots),
        "__ROWS__": '\n'.join(trs),
        "__OPTIONS__": options,
        "__TRAIN__": str(n_train),
        "__TEST__": str(evaluasi['jumlah_data_tes']),
    }
    for tag, val in replace.items():
        page = page.replace(tag, val)
    dest.write_text(page, encoding="utf-8")


def jalankan(path_data: Path, path_alert: Path, folder_hasil: Path, k: int, seed: int):
    latih_berlabel = baca_csv(path_data, berlabel=True)
    alert_baru = baca_csv(path_alert, berlabel=False)
    train_rows, test_rows = bagi_stratifikasi(latih_berlabel, seed)
    model = KNN(k=k).fit(train_rows)
    pred_tes = [model.prediksi(r)[0] for r in test_rows]
    evaluasi = metrik([r["label"] for r in test_rows], pred_tes)
    evaluasi.update({"k": k, "seed": seed, "jumlah_data_latih": len(train_rows)})

    hasil = []
    for row in alert_baru:
        kelas, suara = model.prediksi(row)
        hasil.append({**row, "prediksi": kelas, "skor_tetangga": suara})
    folder_hasil.mkdir(parents=True, exist_ok=True)
    write_csv(folder_hasil / "hasil_prediksi.csv", hasil,
              ["id", *FITUR, "grid_x", "grid_y", "prediksi", "skor_tetangga"])
    (folder_hasil / "metrik_evaluasi.json").write_text(
        json.dumps(evaluasi, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    labels = sorted(evaluasi["confusion_matrix"])
    write_csv(folder_hasil / "confusion_matrix.csv",
              [{"aktual": a, **evaluasi["confusion_matrix"][a]} for a in labels],
              ["aktual", *labels])
    buat_html(hasil, evaluasi, folder_hasil / "dashboard_hasil.html", len(train_rows), k)
    lines = [
        "WEBINAR 6 - HASIL STUDI KASUS (DATA SINTETIS)",
        "=" * 50,
        "Studi kasus: Klasifikasi penyebab LANGSUNG gangguan hutan",
        "Fitur Sentinel-1/2: PROKSI SIMULASI; bukan ekstraksi data satelit asli.",
        f"Data latih: {len(train_rows)} | Data uji: {len(test_rows)} | Alert baru: {len(hasil)}",
        f"KNN: k={k}; split per kelas, seed={seed}; standardisasi hanya dari latih",
        f"Akurasi pada data uji sintetis: {evaluasi['akurasi']:.2%}",
        f"Macro F1 pada data uji sintetis: {evaluasi['macro_f1']:.3f}",
        "", "Distribusi prediksi pada alert baru:",
    ]
    for label, jumlah in sorted(Counter(r["prediksi"] for r in hasil).items()):
        lines.append(f"- {label}: {jumlah}")
    lines += ["", "PENTING: Ini bukan sistem pemantauan operasional.",
              "Hasil tidak cocok dijadikan dasar keputusan kebijakan/penegakan hukum."]
    (folder_hasil / "ringkasan_hasil.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nLihat dashboard: {folder_hasil / 'dashboard_hasil.html'}")
    return evaluasi, hasil


def main():
    parser = argparse.ArgumentParser(description="Demo pemantauan gangguan hutan, dataset sintetis")
    parser.add_argument("--k", type=int, default=5, help="Jumlah tetangga ganjil, default 5")
    parser.add_argument("--seed", type=int, default=42, help="Seed pembagian train/test")
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "data_berlabel_sintetis.csv")
    parser.add_argument("--alert", type=Path, default=ROOT / "data" / "alert_baru_sintetis.csv")
    parser.add_argument("--hasil", type=Path, default=ROOT / "hasil")
    parser.add_argument("--buat-ulang-data", action="store_true", help="Bangkitkan dataset sintetis baru")
    args = parser.parse_args()
    if args.buat_ulang_data or not args.data.exists() or not args.alert.exists():
        generate()
    jalankan(args.data, args.alert, args.hasil, args.k, args.seed)


if __name__ == "__main__":
    main()
