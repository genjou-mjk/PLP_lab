"""Модуль візуалізації: чотири типи графіків (matplotlib), автозбереження у PNG."""
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # без графічного вікна - лише збереження у файли
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

COLORS = {"positive": "#2e9e5b", "neutral": "#9aa0a6", "negative": "#d64545"}
UA = {"positive": "Позитивні", "neutral": "Нейтральні", "negative": "Негативні"}


class Visualizer:
    """Будує та зберігає графіки результатів аналізу."""

    def __init__(self, out_dir="output"):
        self._dir = Path(out_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _save(self, fig, name):
        path = self._dir / name
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return str(path)

    def pie(self, stats):
        """Кругова діаграма розподілу класів."""
        labels = [k for k, v in stats["counts"].items() if v > 0]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie([stats["counts"][k] for k in labels], labels=[UA[k] for k in labels],
               colors=[COLORS[k] for k in labels], autopct="%1.1f%%", startangle=90)
        ax.legend(title="Клас", loc="lower right")
        ax.set_title("Розподіл тональності повідомлень")
        return self._save(fig, "pie_distribution.png")

    def histogram(self, result, pos, neg):
        """Гістограма інтегральної оцінки з порогами."""
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.hist(result["score"], bins=15, color="#4c78a8", edgecolor="white",
                label="Кількість повідомлень")
        ax.axvline(pos, color=COLORS["positive"], ls="--", label=f"Поріг + ({pos})")
        ax.axvline(neg, color=COLORS["negative"], ls="--", label=f"Поріг - ({neg})")
        ax.set_title("Гістограма інтегральної оцінки тональності")
        ax.set_xlabel("Оцінка (від -1 до +1)")
        ax.set_ylabel("Кількість повідомлень")
        ax.grid(alpha=0.3)
        ax.legend()
        return self._save(fig, "histogram_scores.png")

    def top_words(self, result, top_n=10):
        """Стовпчикова діаграма найчастіших слів у позитивних і негативних текстах."""
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        for ax, label in zip(axes, ("positive", "negative")):
            counter = Counter(w for toks in result.loc[result["label"] == label, "tokens"]
                              for w in toks)
            common = counter.most_common(top_n)
            if common:
                words, freq = zip(*common)
                ax.barh(words[::-1], freq[::-1], color=COLORS[label], label=UA[label])
                ax.legend()
            ax.set_title(f"Топ-{top_n} слів: {UA[label].lower()}")
            ax.set_xlabel("Частота")
            ax.set_ylabel("Слово")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.grid(axis="x", alpha=0.3)
        return self._save(fig, "top_words.png")

    def scatter(self, result):
        """Діаграма розсіювання: VADER проти TextBlob."""
        fig, ax = plt.subplots(figsize=(6.5, 5.5))
        for label in ("positive", "neutral", "negative"):
            sub = result[result["label"] == label]
            ax.scatter(sub["vader_compound"], sub["tb_polarity"], s=60, alpha=0.8,
                       color=COLORS[label], label=UA[label])
        ax.axhline(0, color="black", lw=0.6)
        ax.axvline(0, color="black", lw=0.6)
        ax.set_title("Порівняння методів: VADER та TextBlob")
        ax.set_xlabel("VADER compound")
        ax.set_ylabel("TextBlob polarity")
        ax.grid(alpha=0.3)
        ax.legend()
        return self._save(fig, "scatter_methods.png")

    def build_all(self, result, stats, pos, neg, top_n=10):
        """Будує всі графіки та повертає список шляхів до файлів."""
        return [self.pie(stats), self.histogram(result, pos, neg),
                self.top_words(result, top_n), self.scatter(result)]
