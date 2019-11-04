"""Utilities for natural language processing"""

from collections import Counter


class TFIDF:
    """
    TFIDF, term frequency–inverse document frequency

    References:
        https://en.wikipedia.org/wiki/Tf-idf
    """

    def __init__(self, tf_weight: str, idf_weight: str):
        """

        Parameters
        ----------
        tf_weight: str, weighting scheme of term frequency
        idf_weight: str, weighting scheme of inverse document frequency
        """
        self._tf_weight = tf_weight
        self._idf_weight = idf_weight
        self._n = 0     # total number of documents in the corpus
        self._term_counter = Counter()
        self._document_counter = Counter()

    def _tf(self, word: str) -> float:
        pass

    def _idf(self, word: str) -> float:
        pass

    def tfidf(self, word: str) -> float:
        return self._tf(word) * self._idf(word)