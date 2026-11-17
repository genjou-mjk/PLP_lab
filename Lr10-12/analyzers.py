"""Модуль аналізу тональності: NLTK VADER + TextBlob."""
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

from preprocessing import ensure_nltk_resources


class SentimentAnalyzer:
    """Визначає тональність тексту двома методами та об'єднує результат."""

    LABELS = ("positive", "neutral", "negative")

    def __init__(self, pos_threshold=0.05, neg_threshold=-0.05):
        if not (-1 <= neg_threshold < pos_threshold <= 1):
            raise ValueError("Потрібно: -1 <= neg_threshold < pos_threshold <= 1.")
        ensure_nltk_resources()
        self._pos = pos_threshold
        self._neg = neg_threshold
        self._vader = SentimentIntensityAnalyzer()

    def _label(self, score):
        """Перетворює числову оцінку на мітку класу."""
        if score >= self._pos:
            return "positive"
        if score <= self._neg:
            return "negative"
        return "neutral"

    def analyze_text(self, text):
        """Повертає словник оцінок для одного повідомлення."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Порожній текст неможливо проаналізувати.")
        vader = self._vader.polarity_scores(text)["compound"]
        blob = TextBlob(text).sentiment
        combined = round((vader + blob.polarity) / 2, 4)
        return {"vader_compound": round(vader, 4),
                "tb_polarity": round(blob.polarity, 4),
                "tb_subjectivity": round(blob.subjectivity, 4),
                "score": combined,
                "label": self._label(combined)}

    def analyze_dataframe(self, df, preprocessor=None):
        """Додає до таблиці стовпці з оцінками (та токени, якщо є препроцесор)."""
        rows = []
        for text in df["text"]:
            try:
                rows.append(self.analyze_text(text))
            except Exception as exc:  # окремий збій не зупиняє весь аналіз
                print(f"  [!] Пропущено повідомлення через помилку: {exc}")
                rows.append({"vader_compound": None, "tb_polarity": None,
                             "tb_subjectivity": None, "score": None, "label": None})
        result = pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
        result = result.dropna(subset=["label"]).reset_index(drop=True)
        if preprocessor is not None:
            result["tokens"] = result["text"].apply(preprocessor.tokenize)
        return result

    @staticmethod
    def statistics(result):
        """Зведена статистика: розподіл класів та числові характеристики."""
        counts = result["label"].value_counts().reindex(
            SentimentAnalyzer.LABELS, fill_value=0)
        return {"total": int(len(result)),
                "counts": counts.to_dict(),
                "mean_score": float(result["score"].mean()),
                "median_score": float(result["score"].median()),
                "std_score": float(result["score"].std(ddof=0)),
                "mean_subjectivity": float(result["tb_subjectivity"].mean()),
                "agreement": float(((result["vader_compound"] > 0) ==
                                    (result["tb_polarity"] > 0)).mean())}
