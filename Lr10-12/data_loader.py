"""Модуль введення даних: завантаження текстів із TXT та JSON у директорії data."""
import json
from pathlib import Path

import pandas as pd


class DataFormatError(Exception):
    """Власний виняток: некоректний формат або структура вхідних даних."""


class DataLoader:
    """Читає текстові повідомлення з файлу в директорії data та повертає очищений DataFrame."""

    SUPPORTED = (".txt", ".json", ".csv")
    DATA_DIR = Path("data")

    def __init__(self, path=None, text_column="text"):
        # Якщо шлях не задано або вказано директорію — шукаємо файл у data/
        target = Path(path) if path else self.DATA_DIR
        self._path = self._resolve_file(target) if target.is_dir() or str(target) in (".", "data", "data/") else target
        self._text_column = text_column
        self.removed = 0

    def _resolve_file(self, directory: Path) -> Path:
        """Знаходить файл підтримки (.txt або .json) у вказаній директорії."""
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"Директорію з даними не знайдено: {directory}")

        candidates = sorted(
            p for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() in self.SUPPORTED
        )

        if not candidates:
            raise FileNotFoundError(
                f"У директорії '{directory}' немає жодного файлу підтримуваного формату "
                f"({', '.join(self.SUPPORTED)})."
            )

        if len(candidates) > 1:
            names = ", ".join(p.name for p in candidates)
            raise DataFormatError(
                f"У директорії '{directory}' знайдено декілька файлів ({names}). "
                f"Залиште один файл для однозначного зчитування або вкажіть конкретний шлях."
            )

        return candidates[0]

    def load(self):
        """Завантажує файл за розширенням і виконує первинне очищення."""
        if not self._path.exists():
            raise FileNotFoundError(f"Файл не знайдено: {self._path}")

        ext = self._path.suffix.lower()
        if ext not in self.SUPPORTED:
            raise DataFormatError(
                f"Непідтримуваний формат '{ext}'. Підтримуються лише: {', '.join(self.SUPPORTED)}"
            )

        try:
            if ext == ".json":
                df = self._read_json()
            else:
                df = self._read_txt()
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise DataFormatError(f"Файл пошкоджено або має хибне кодування/формат: {exc}") from exc

        return self._clean(df)

    def _read_json(self):
        """JSON: список рядків ['...'] або список словників [{'text': '...'}]."""
        with open(self._path, encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list) or len(data) == 0:
            raise DataFormatError("JSON має містити непорожній список записів.")

        if all(isinstance(item, str) for item in data):
            return pd.DataFrame({self._text_column: data})

        if all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
            if self._text_column not in df.columns:
                raise DataFormatError(
                    f"У JSON-об'єктах відсутнє поле '{self._text_column}'."
                )
            # Перевіряємо, що значення в текстовому полі є рядками (а не списками/словниками/числами)
            invalid_items = [
                val for val in df[self._text_column]
                if val is not None and not isinstance(val, str)
            ]
            if invalid_items:
                raise DataFormatError(
                    f"Поле '{self._text_column}' містить некоректний тип даних замість тексту."
                )
            return df

        raise DataFormatError(
            "Некоректна структура JSON: очікується список рядків або список об'єктів."
        )

    def _read_txt(self):
        """TXT: кожен непорожній рядок — окреме текстове повідомлення."""
        with open(self._path, encoding="utf-8") as fh:
            raw_lines = fh.readlines()

        if not raw_lines or all(not line.strip() for line in raw_lines):
            raise DataFormatError("TXT-файл порожній або містить лише пробільні символи.")

        lines = [ln.strip() for ln in raw_lines]
        return pd.DataFrame({self._text_column: lines})

    def _clean(self, df):
        """Перевіряє наявність стовпця, видаляє порожні та дублікати, валідує текст."""
        if self._text_column not in df.columns:
            raise DataFormatError(
                f"У файлі немає поля/стовпця '{self._text_column}'. Наявні: {list(df.columns)}"
            )

        before = len(df)
        df = df.rename(columns={self._text_column: "text"})

        # Перевіряємо, чи є хоча б один коректний текстовий запис
        non_str = df["text"].dropna().apply(lambda x: not isinstance(x, str))
        if non_str.any():
            raise DataFormatError("Текстові дані сформовано неправильно: виявлено нерядкові значення.")

        df["text"] = df["text"].astype("string").str.strip()
        df = df.dropna(subset=["text"])
        df = df[df["text"] != ""].drop_duplicates(subset="text").reset_index(drop=True)

        if df.empty:
            raise DataFormatError(
                "Після очищення не залишилось жодного коректного текстового повідомлення."
            )

        # Додаткова перевірка: чи є хоча б якісь літери/символи, придатні для текстового аналізу
        has_letters = df["text"].str.contains(r"[A-Za-zА-Яа-яІіЇїЄєҐґ]", regex=True, na=False)
        if not has_letters.any():
            raise DataFormatError(
                "Текстова інформація сформована некоректно: повідомлення не містять літер для аналізу."
            )

        if "id" not in df.columns:
            df.insert(0, "id", range(1, len(df) + 1))

        self.removed = before - len(df)
        return df