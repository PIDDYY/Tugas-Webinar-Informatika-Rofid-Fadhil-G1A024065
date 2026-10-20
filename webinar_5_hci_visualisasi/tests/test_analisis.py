"""Unit test ringan untuk logika yang dipakai pada contoh webinar."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analisis import baca_data, ringkas  # noqa: E402


class TestAnalisis(unittest.TestCase):
    def setUp(self):
        self.data = [
            {'tanggal': '2026-09-01', 'wilayah': 'Bengkulu', 'kategori': 'Makanan', 'transaksi': 10, 'omzet': 100000, 'keluhan': 1},
            {'tanggal': '2026-09-02', 'wilayah': 'Curup', 'kategori': 'Makanan', 'transaksi': 5, 'omzet': 50000, 'keluhan': 0},
            {'tanggal': '2026-10-01', 'wilayah': 'Bengkulu', 'kategori': 'ATK', 'transaksi': 20, 'omzet': 200000, 'keluhan': 2},
        ]

    def test_total_semua(self):
        hasil = ringkas(self.data)
        self.assertEqual(hasil['omzet_rp'], 350000)
        self.assertEqual(hasil['transaksi'], 35)
        self.assertEqual(hasil['keluhan'], 3)
        self.assertEqual(hasil['kategori_tertinggi'], 'ATK')

    def test_filter_kombinasi(self):
        hasil = ringkas(self.data, bulan='2026-09', wilayah='Bengkulu', kategori='Makanan')
        self.assertEqual(hasil['jumlah_baris'], 1)
        self.assertEqual(hasil['omzet_rp'], 100000)
        self.assertEqual(hasil['rasio_keluhan_persen'], 10)

    def test_tanpa_data(self):
        hasil = ringkas(self.data, bulan='2026-08')
        self.assertEqual(hasil['jumlah_baris'], 0)
        self.assertEqual(hasil['rasio_keluhan_persen'], 0)
        self.assertIsNone(hasil['kategori_tertinggi'])

    def test_file_contoh(self):
        hasil = baca_data()
        self.assertEqual(len(hasil), 600)
        self.assertTrue(all(x['keluhan'] <= x['transaksi'] for x in hasil))


if __name__ == '__main__':
    unittest.main()
