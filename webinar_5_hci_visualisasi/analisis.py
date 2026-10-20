"""Analisis dataset penjualan menggunakan pustaka standar Python saja."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

DEFAULT_FILE = Path(__file__).resolve().parent / 'data' / 'penjualan.csv'


def baca_data(lokasi=DEFAULT_FILE):
    hasil = []
    with open(lokasi, encoding='utf-8-sig', newline='') as file:
        pembaca = csv.DictReader(file)
        kolom_wajib = {'tanggal', 'wilayah', 'kategori', 'transaksi', 'omzet', 'keluhan'}
        if not kolom_wajib.issubset(set(pembaca.fieldnames or [])):
            raise ValueError('Kolom CSV tidak lengkap: tanggal, wilayah, kategori, transaksi, omzet, keluhan wajib ada.')
        for n, baris in enumerate(pembaca, start=2):
            try:
                d = {key: baris[key].strip() for key in ('tanggal', 'wilayah', 'kategori')}
                d.update({key: int(baris[key]) for key in ('transaksi', 'omzet', 'keluhan')})
                if any(d[k] < 0 for k in ('transaksi', 'omzet', 'keluhan')) or d['keluhan'] > d['transaksi']:
                    raise ValueError('nilai tidak valid')
            except (ValueError, TypeError) as e:
                raise ValueError(f'Data tidak valid pada baris CSV {n}: {e}') from e
            hasil.append(d)
    return hasil


def ringkas(data, bulan='Semua', wilayah='Semua', kategori='Semua'):
    terpilih = [d for d in data if (bulan == 'Semua' or d['tanggal'][:7] == bulan)
                and (wilayah == 'Semua' or d['wilayah'] == wilayah)
                and (kategori == 'Semua' or d['kategori'] == kategori)]
    total_transaksi = sum(d['transaksi'] for d in terpilih)
    total_keluhan = sum(d['keluhan'] for d in terpilih)
    omzet = sum(d['omzet'] for d in terpilih)
    kategori_omzet = defaultdict(int)
    for d in terpilih:
        kategori_omzet[d['kategori']] += d['omzet']
    urutan = sorted(kategori_omzet.items(), key=lambda pair: (-pair[1], pair[0]))
    return {
        'jumlah_baris': len(terpilih),
        'omzet_rp': omzet,
        'transaksi': total_transaksi,
        'keluhan': total_keluhan,
        'rasio_keluhan_persen': round(100 * total_keluhan / total_transaksi, 2) if total_transaksi else 0.0,
        'kategori_tertinggi': urutan[0][0] if urutan else None,
        'omzet_per_kategori': dict(urutan),
    }


def main():
    parser = argparse.ArgumentParser(description='Analisis sederhana data penjualan webinar 5')
    parser.add_argument('--file', type=Path, default=DEFAULT_FILE, help='Lokasi CSV')
    parser.add_argument('--bulan', default='Semua', help='Contoh: 2026-09 atau Semua')
    parser.add_argument('--wilayah', default='Semua', help='Bengkulu, Curup, Mukomuko, atau Semua')
    parser.add_argument('--kategori', default='Semua', help='Makanan, Minuman, ATK, Perlengkapan, atau Semua')
    parser.add_argument('--json', action='store_true', help='Tampilkan dalam format JSON')
    args = parser.parse_args()
    hasil = ringkas(baca_data(args.file), args.bulan, args.wilayah, args.kategori)
    if args.json:
        print(json.dumps(hasil, indent=2, ensure_ascii=False))
    else:
        print('RINGKASAN PENJUALAN (DATA SIMULASI)')
        print(f"Jumlah baris       : {hasil['jumlah_baris']}")
        print(f"Omzet              : Rp{hasil['omzet_rp']:,}".replace(',', '.'))
        print(f"Total transaksi    : {hasil['transaksi']}")
        print(f"Total keluhan      : {hasil['keluhan']}")
        print(f"Rasio keluhan      : {hasil['rasio_keluhan_persen']}%")
        print(f"Kategori terlaris  : {hasil['kategori_tertinggi'] or '-'}")


if __name__ == '__main__':
    main()
