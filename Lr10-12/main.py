"""Головний модуль: меню, налаштування (config.json + аргументи CLI), обробка помилок."""
import argparse
import json
import sys
from pathlib import Path

from analyzers import SentimentAnalyzer
from data_loader import DataFormatError, DataLoader
from preprocessing import TextPreprocessor
from reporter import ReportGenerator, ResultSaver
from visualizer import Visualizer

DEFAULTS = {"input_file": "data/sample_reviews.csv", "text_column": "text",
            "pos_threshold": 0.05, "neg_threshold": -0.05, "top_n_words": 10,
            "remove_stopwords": True, "output_dir": "output"}


def load_config(path):
    """Читає конфігурацію; за відсутності/помилки використовує значення за замовчуванням."""
    cfg = dict(DEFAULTS)
    try:
        with open(path, encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    except FileNotFoundError:
        print(f"[!] Конфігурацію '{path}' не знайдено, використано типові значення.")
    except json.JSONDecodeError as exc:
        print(f"[!] Помилка у файлі конфігурації ({exc}); використано типові значення.")
    return cfg


class SentimentApp:
    """Керує послідовністю етапів: завантаження -> аналіз -> графіки -> збереження."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.df = None        # завантажені дані
        self.result = None    # результати аналізу
        self.stats = None
        self.charts = []

    # ---------- етапи ----------
    def load(self):
        print(f"\n[1/5] Завантаження файлу '{self.cfg['input_file']}'...")
        loader = DataLoader(self.cfg["input_file"], self.cfg["text_column"])
        self.df = loader.load()
        print(f"      Завантажено повідомлень: {len(self.df)} "
              f"(відкинуто порожніх/дублікатів: {loader.removed})")

    def analyze(self):
        if self.df is None:
            raise RuntimeError("Спочатку завантажте дані (пункт 1).")
        print("\n[2/5] Попереднє оброблення (NLTK) та аналіз тональності...")
        prep = TextPreprocessor(self.cfg["remove_stopwords"])
        analyzer = SentimentAnalyzer(self.cfg["pos_threshold"], self.cfg["neg_threshold"])
        self.result = analyzer.analyze_dataframe(self.df, prep)
        self.stats = analyzer.statistics(self.result)
        print("      Аналіз завершено.")

    def show_stats(self):
        self._need_result()
        print("\n[3/5] Результати:")
        print(ResultSaver.summary_text(self.stats))
        print(self.result[["id", "text", "score", "label"]]
              .assign(text=lambda d: d["text"].str.slice(0, 45) + "...")
              .head(10).to_string(index=False))

    def plot(self):
        self._need_result()
        print("\n[4/5] Побудова графіків...")
        self.charts = Visualizer(self.cfg["output_dir"]).build_all(
            self.result, self.stats, self.cfg["pos_threshold"],
            self.cfg["neg_threshold"], self.cfg["top_n_words"])
        for p in self.charts:
            print(f"      збережено: {p}")

    def save(self):
        self._need_result()
        print("\n[5/5] Збереження результатів...")
        for k, p in ResultSaver(self.cfg["output_dir"]).save_all(self.result, self.stats).items():
            print(f"      {k.upper()}: {p}")

    def report(self):
        self._need_result()
        if not self.charts:
            self.plot()
        print("\n      Формування PDF-звіту...")
        print(f"      PDF: {ReportGenerator(self.cfg['output_dir']).build(self.result, self.stats, self.charts, self.cfg)}")

    def analyze_custom(self):
        text = input("Введіть англомовне речення: ").strip()
        analyzer = SentimentAnalyzer(self.cfg["pos_threshold"], self.cfg["neg_threshold"])
        r = analyzer.analyze_text(text)
        print(f"      VADER={r['vader_compound']}, TextBlob={r['tb_polarity']}, "
              f"суб'єктивність={r['tb_subjectivity']} -> {r['label'].upper()}")

    def run_all(self):
        for step in (self.load, self.analyze, self.show_stats, self.plot, self.save, self.report):
            step()

    # налаштування
    def change_settings(self):
        print("\nПоточні налаштування:")
        for k, v in self.cfg.items():
            print(f"   {k} = {v}")
        key = input("Який параметр змінити? (Enter - нічого): ").strip()
        if not key:
            return
        if key not in self.cfg:
            raise KeyError(f"Невідомий параметр '{key}'.")
        raw = input(f"Нове значення для '{key}': ").strip()
        old = self.cfg[key]
        if isinstance(old, bool):
            self.cfg[key] = raw.lower() in ("1", "true", "yes", "так", "y")
        elif isinstance(old, (int, float)):
            try:
                self.cfg[key] = type(old)(raw)
            except ValueError:
                raise ValueError(f"Для '{key}' потрібно ввести число, а не '{raw}'.")
        else:
            self.cfg[key] = raw
        print(f"      '{key}' = {self.cfg[key]}")
        if key in ("input_file", "text_column"):
            self.df = self.result = None    # потрібно перезавантажити

    def _need_result(self):
        if self.result is None:
            raise RuntimeError("Спочатку виконайте аналіз (пункт 2).")


MENU = """
                АНАЛІЗ ТОНАЛЬНОСТІ ТЕКСТУ 
 1 - Завантажити дані        5 - Зберегти CSV/JSON/XLSX/TXT
 2 - Виконати аналіз         6 - Сформувати PDF-звіт
 3 - Показати статистику     7 - Змінити налаштування
 4 - Побудувати графіки      8 - Перевірити власне речення
 9 - Виконати все автоматично      0 - Вихід
                                                            """


def main(argv=None):
    ap = argparse.ArgumentParser(description="Аналіз тональності текстових повідомлень")
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--input", help="вхідний файл (перевизначає config.json)")
    ap.add_argument("--auto", action="store_true", help="виконати всі етапи без меню")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    if args.input:
        cfg["input_file"] = args.input
    app = SentimentApp(cfg)
    actions = {"1": app.load, "2": app.analyze, "3": app.show_stats, "4": app.plot,
               "5": app.save, "6": app.report, "7": app.change_settings,
               "8": app.analyze_custom, "9": app.run_all}

    if args.auto:
        safe_call(app.run_all)
        return
    while True:
        print(MENU)
        try:
            choice = input("Ваш вибір: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПрограму завершено.")
            break
        if choice == "0":
            print("До побачення!")
            break
        if choice in actions:
            safe_call(actions[choice])
        else:
            print("[!] Некоректний вибір. Введіть число від 0 до 9.")


def safe_call(func):
    """Виконує етап і перехоплює типові виняткові ситуації."""
    try:
        func()
    except FileNotFoundError as exc:
        print(f"[ПОМИЛКА] {exc}")
    except DataFormatError as exc:
        print(f"[ПОМИЛКА ДАНИХ] {exc}")
    except (ValueError, KeyError) as exc:
        print(f"[НЕКОРЕКТНЕ ЗНАЧЕННЯ] {exc}")
    except RuntimeError as exc:
        print(f"[ПІДКАЗКА] {exc}")
    except PermissionError:
        print("[ПОМИЛКА] Немає доступу до файлу (можливо, він відкритий в іншій програмі).")
    except Exception as exc:  # остання лінія захисту
        print(f"[НЕОЧІКУВАНА ПОМИЛКА] {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
