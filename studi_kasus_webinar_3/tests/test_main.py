"""Unit test untuk rumus jarak dan logika seleksi."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import Kandidat, Lokasi, evaluasi, haversine_km, muat_data, skor_skala


class TestGIS(unittest.TestCase):
    def test_jarak_titik_sama_nol(self):
        self.assertAlmostEqual(haversine_km(-3.8, 102.2, -3.8, 102.2), 0)

    def test_jarak_simetris(self):
        ab = haversine_km(-3.8, 102.2, -3.9, 102.25)
        ba = haversine_km(-3.9, 102.25, -3.8, 102.2)
        self.assertAlmostEqual(ab, ba)
        self.assertGreater(ab, 0)

    def test_skor_batas(self):
        self.assertEqual(skor_skala(2, 3, 10), 0)
        self.assertEqual(skor_skala(20, 3, 10), 100)
        self.assertEqual(skor_skala(6.5, 3, 10), 50)

    def test_dekat_toko_eksisting_tidak_layak(self):
        k = Kandidat("X", "Percobaan", -3.8, 102.2, 5000, 5)
        toko = [Lokasi("T", "Toko", -3.8, 102.2)]
        gudang = Lokasi("G", "Gudang", -3.81, 102.2)
        result = evaluasi([k], toko, gudang)
        self.assertEqual(result[0]["status"], "TIDAK LAYAK")
        self.assertIn("Terlalu dekat", result[0]["alasan"])

    def test_dataset_dan_peringkat(self):
        data = Path(__file__).resolve().parents[1] / "data"
        k, t, g = muat_data(data)
        hasil = evaluasi(k, t, g)
        layak = [x for x in hasil if x["status"] == "LAYAK"]
        self.assertEqual(len(k), 10)
        self.assertGreater(len(layak), 0)
        self.assertEqual([x["peringkat"] for x in layak], list(range(1, len(layak)+1)))
        self.assertTrue(all(layak[i]["skor_total"] >= layak[i+1]["skor_total"] for i in range(len(layak)-1)))


if __name__ == "__main__":
    unittest.main()
