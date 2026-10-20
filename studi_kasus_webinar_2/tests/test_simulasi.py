"""Uji sederhana dengan unittest (tanpa instalasi paket tambahan)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import jalankan_simulasi  # noqa: E402
from simulasi import baca_wilayah, simulasi_hujan  # noqa: E402


class TestSimulasi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wilayah = baca_wilayah(ROOT / "data" / "wilayah_bengkulu_dummy.csv")

    def test_data_wilayah(self):
        self.assertEqual(len(self.wilayah), 9)
        self.assertEqual(len({w.kode for w in self.wilayah}), 9)

    def test_hasil_tetap_dengan_seed_yang_sama(self):
        w = self.wilayah[0]
        self.assertEqual(simulasi_hujan(w, 123, 2026), simulasi_hujan(w, 123, 2026))

    def test_genangan_nonnegatif(self):
        self.assertGreaterEqual(simulasi_hujan(self.wilayah[0], 10, 2026), 0)

    def test_serial_dan_paralel_identik(self):
        sample = self.wilayah[:3]
        serial, _ = jalankan_simulasi(sample, 20, 2026, 1)
        paralel, _ = jalankan_simulasi(sample, 20, 2026, 2)
        self.assertEqual(serial, paralel)
        for hasil in serial:
            self.assertTrue(0 <= hasil["persentase_skenario_genangan"] <= 100)


if __name__ == "__main__":
    unittest.main()
