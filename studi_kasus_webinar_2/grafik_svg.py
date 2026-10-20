"""Grafik batang SVG sederhana tanpa matplotlib: buka di browser."""

from html import escape
from pathlib import Path


def buat_grafik(hasil: list[dict], tujuan: str | Path) -> None:
    ukuran_per_baris = 42
    tinggi = 130 + len(hasil) * ukuran_per_baris
    elemen = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{tinggi}" viewBox="0 0 960 {tinggi}">',
        '<rect width="960" height="100%" fill="#fafbff"/>',
        '<text x="40" y="46" font-family="Arial" font-size="24" font-weight="bold" fill="#212b45">Simulasi Risiko Genangan — Wilayah Bengkulu</text>',
        '<text x="40" y="72" font-family="Arial" font-size="13" fill="#586174">Data sintetis • Persentase skenario yang melewati ambang • Bukan prakiraan resmi</text>',
        '<line x1="320" y1="92" x2="880" y2="92" stroke="#cfd5e2"/>',
    ]
    for persen in (0, 25, 50, 75, 100):
        x = 320 + 5.6 * persen
        elemen += [
            f'<line x1="{x}" y1="93" x2="{x}" y2="{tinggi-23}" stroke="#e4e7ef"/>',
            f'<text x="{x}" y="{tinggi-8}" fill="#6b7280" font-family="Arial" text-anchor="middle" font-size="12">{persen}%</text>',
        ]
    for urut, baris in enumerate(sorted(hasil, key=lambda r: -r["persentase_skenario_genangan"])):
        y = 116 + urut * ukuran_per_baris
        persen = baris["persentase_skenario_genangan"]
        kategori = baris["kategori_simulasi"]
        warna = {"Tinggi": "#d94b53", "Sedang": "#e3a73d", "Rendah": "#389d82"}[kategori]
        elemen += [
            f'<text x="40" y="{y+17}" font-family="Arial" font-size="15" fill="#273449">{escape(str(baris["nama_wilayah"]))}</text>',
            f'<rect x="320" y="{y}" width="{max(0.0,5.6 * persen):.2f}" height="23" rx="4" fill="{warna}"/>',
            f'<text x="{min(885,330+5.6 * persen):.2f}" y="{y+17}" font-family="Arial" font-size="13" fill="#273449">{persen:.1f}%</text>',
        ]
    elemen.append("</svg>")
    Path(tujuan).write_text("\n".join(elemen), encoding="utf-8")
