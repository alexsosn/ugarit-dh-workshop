import unittest

import pandas as pd

from workshop_tools.genre_features import (
    build_word_document_matrix,
    select_genre_features,
)


class GenreFeatureTests(unittest.TestCase):
    def setUp(self):
        self.corpus = pd.DataFrame(
            {
                "tablet": ["A1", "A2", "B1", "B2"],
                "genre": ["A", "A", "B", "B"],
                "tokens": [
                    ["w", "alpha", "1", "xbroken"],
                    ["w", "alpha", "1"],
                    ["w", "beta", "Xgap"],
                    ["w", "beta"],
                ],
            }
        )

    def test_matrix_has_documents_as_columns_and_keeps_numbers(self):
        info, matrix = build_word_document_matrix(self.corpus, min_documents=1)
        self.assertEqual(list(matrix.columns), ["A1", "A2", "B1", "B2"])
        self.assertIn("1", matrix.index)
        self.assertNotIn("xbroken", matrix.index)
        self.assertNotIn("Xgap", matrix.index)
        self.assertEqual(info.loc["A1", "genre"], "A")

    def test_chi_square_selects_associated_not_uniform_forms(self):
        info, matrix = build_word_document_matrix(self.corpus, min_documents=1)
        selected = select_genre_features(
            matrix, info["genre"], top_n=5, min_genre_documents=2
        )
        by_genre = selected.groupby("genre")["form"].apply(set)
        self.assertIn("alpha", by_genre["A"])
        self.assertIn("1", by_genre["A"])
        self.assertIn("beta", by_genre["B"])
        self.assertNotIn("w", set(selected["form"]))


if __name__ == "__main__":
    unittest.main()
