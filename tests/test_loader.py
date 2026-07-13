import unittest

from workshop_tools.loader import (
    corpus_as_documents,
    token_counts,
    without_broken_tokens,
)


class LoaderTests(unittest.TestCase):
    def test_broken_tokens_are_excluded_from_clustering_documents(self):
        tokens = ["bˤl", "xx", "abx", "X", "ym"]
        self.assertEqual(without_broken_tokens(tokens), ["bˤl", "ym"])

        texts = [{"ktu": "1.1", "tokens": tokens}]
        labels, documents = corpus_as_documents(texts)
        self.assertEqual(labels, ["1.1"])
        self.assertEqual(documents, ["bˤl ym"])
        self.assertEqual(
            token_counts(texts, exclude_broken=True),
            {"bˤl": 1, "ym": 1},
        )


if __name__ == "__main__":
    unittest.main()
