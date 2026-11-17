"""Модуль попереднього оброблення тексту за допомогою NLTK."""
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def ensure_nltk_resources():
    """Завантажує потрібні ресурси NLTK, якщо їх ще немає."""
    needed = {"punkt": "tokenizers/punkt", "punkt_tab": "tokenizers/punkt_tab",
              "stopwords": "corpora/stopwords", "wordnet": "corpora/wordnet",
              "vader_lexicon": "sentiment/vader_lexicon.zip"}
    for name, path in needed.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


class TextPreprocessor:
    """Очищення, токенізація, видалення стоп-слів і лематизація."""

    URL_RE = re.compile(r"https?://\S+|www\.\S+")
    NON_LETTER_RE = re.compile(r"[^a-z\s]")

    def __init__(self, remove_stopwords=True):
        ensure_nltk_resources()
        self._remove_stop = remove_stopwords
        self._stop = set(stopwords.words("english"))
        self._lemmatizer = WordNetLemmatizer()

    def tokenize(self, text):
        """Повертає список очищених лем із тексту."""
        text = self.URL_RE.sub(" ", str(text).lower())
        text = self.NON_LETTER_RE.sub(" ", text)
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if len(t) > 2]
        if self._remove_stop:
            tokens = [t for t in tokens if t not in self._stop]
        return [self._lemmatizer.lemmatize(t) for t in tokens]
