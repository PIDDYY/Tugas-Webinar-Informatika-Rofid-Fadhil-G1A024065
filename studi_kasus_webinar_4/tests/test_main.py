import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import NaiveBayesTeks, bagi_data, hitung_metrik, muat_data, tokenisasi


class UjiWebinar4(unittest.TestCase):
    def test_tokenisasi(self):
        self.assertEqual(tokenisasi("PROMO, Gratis!"), ["promo", "gratis"])

    def test_dataset_seimbang(self):
        data = muat_data()
        self.assertEqual(len(data), 80)
        self.assertEqual(sum(label == "spam" for _, label in data), 40)

    def test_split_stratified(self):
        latih, uji = bagi_data(muat_data())
        self.assertEqual((len(latih), len(uji)), (64, 16))
        self.assertEqual(sum(label == "spam" for _, label in uji), 8)
        self.assertEqual(set(latih).intersection(set(uji)), set())

    def test_prediksi_sederhana(self):
        model = NaiveBayesTeks().latih([
            ("voucher promo diskon gratis", "spam"),
            ("promo hadiah voucher", "spam"),
            ("rapat tugas kuliah kelompok", "normal"),
            ("jadwal dosen kelas", "normal")
        ])
        self.assertEqual(model.prediksi("voucher hadiah gratis"), "spam")
        self.assertEqual(model.prediksi("rapat jadwal dosen"), "normal")

    def test_metrik(self):
        m = hitung_metrik(["spam", "spam", "normal", "normal"],
                          ["spam", "normal", "spam", "normal"])
        self.assertEqual(m["accuracy"], 0.5)
        self.assertEqual(m["precision"], 0.5)
        self.assertEqual(m["recall"], 0.5)
        self.assertEqual(m["f1"], 0.5)


if __name__ == "__main__":
    unittest.main()
