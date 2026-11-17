"""Модуль введення даних: завантаження текстів із CSV, JSON та TXT."""
import json
from pathlib import Path

import pandas as pd


class DataFormatError(Exception):
    """Власний виняток: некоректний формат або структура вхідних даних."""


class DataLoader:
    """Читає текстові повідомлення з файлу та повертає очищений DataFrame."""

    SUPPORTED = (".csv", ".json", ".txt")

    def __init__(self, path, text_column="text"):
        self._path = Path(path)          # інкапсульований шлях до файлу
        self._text_column = text_column  # назва стовпця з текстом

    def load(self):
        """Завантажує файл за розширенням і виконує первинне очищення."""
        if not self._path.exists():
            raise FileNotFoundError(f"Файл не знайдено: {self._path}")
        ext = self._path.suffix.lower()
        if ext not in self.SUPPORTED:
            raise DataFormatError(
                f"Непідтримуваний формат '{ext}'. Дозволено: {', '.join(self.SUPPORTED)}")
        try:
            if ext == ".csv":
                df = pd.read_csv(self._path, encoding="utf-8")
            elif ext == ".json":
                df = self._read_json()
            else:
                df = self._read_txt()
        except (pd.errors.ParserError, pd.errors.EmptyDataError,
                json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise DataFormatError(f"Файл пошкоджено або має хибний формат: {exc}") from exc
        return self._clean(df)

    def _read_json(self):
        """JSON: список об'єктів [{'text': ...}] або список рядків."""
        with open(self._path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise DataFormatError("JSON має містити список записів.")
        if data and isinstance(data[0], str):
            return pd.DataFrame({self._text_column: data})
        return pd.DataFrame(data)

    def _read_txt(self):
        """TXT: кожен непорожній рядок - окреме повідомлення."""
        with open(self._path, encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh]
        return pd.DataFrame({self._text_column: lines})

    def _clean(self, df):
        """Перевіряє наявність стовпця, видаляє порожні та дублікати."""
        if self._text_column not in df.columns:
            raise DataFormatError(
                f"У файлі немає стовпця '{self._text_column}'. Наявні: {list(df.columns)}")
        before = len(df)
        df = df.rename(columns={self._text_column: "text"})
        df["text"] = df["text"].astype("string").str.strip()
        df = df.dropna(subset=["text"])
        df = df[df["text"] != ""].drop_duplicates(subset="text").reset_index(drop=True)
        if df.empty:
            raise DataFormatError("Після очищення не залишилось жодного повідомлення.")
        if "id" not in df.columns:
            df.insert(0, "id", range(1, len(df) + 1))
        self.removed = before - len(df)  # скільки записів відкинуто
        return df
