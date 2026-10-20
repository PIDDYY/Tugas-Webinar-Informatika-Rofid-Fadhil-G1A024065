"""Jalankan: python -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path

from buat_dataset import generate
from main import jalankan
from model_knn import KNN, bagi_stratifikasi, baca_csv, metrik


class UjiModel(unittest.TestCase):
    def test_stratifikasi_tidak_bocor(self):
        data_file, alert_file = generate()
        rows = baca_csv(data_file, True)
        train, test = bagi_stratifikasi(rows, seed=42)
        self.assertEqual(len(rows), len(train) + len(test))
        self.assertFalse({r['id'] for r in train} & {r['id'] for r in test})
        self.assertEqual(len({r['label'] for r in train}), 7)
        self.assertEqual(len({r['label'] for r in test}), 7)
        self.assertEqual(len(baca_csv(alert_file, False)), 35)

    def test_metrik_ada_akurasinya(self):
        result = metrik(['A', 'A', 'B', 'B'], ['A', 'B', 'B', 'B'])
        self.assertAlmostEqual(result['akurasi'], 0.75)
        self.assertGreater(result['macro_f1'], 0)

    def test_pipeline_membuat_berkas(self):
        data, alert = generate()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            met, rows = jalankan(data, alert, out, k=5, seed=42)
            self.assertEqual(len(rows), 35)
            self.assertGreater(met['akurasi'], 0.6)
            for file in ['hasil_prediksi.csv', 'metrik_evaluasi.json', 'confusion_matrix.csv', 'dashboard_hasil.html', 'ringkasan_hasil.txt']:
                self.assertTrue((out / file).is_file(), file)

    def test_k_genap_tidak_diperbolehkan(self):
        with self.assertRaises(ValueError):
            KNN(2)


if __name__ == '__main__':
    unittest.main()
