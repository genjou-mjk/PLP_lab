"""Модуль збереження результатів: CSV, JSON, XLSX та підсумковий PDF-звіт."""
import json
from datetime import datetime
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

UA = {"positive": "Позитивні", "neutral": "Нейтральні", "negative": "Негативні"}


class ResultSaver:
    """Експорт таблиці результатів у кілька форматів."""

    def __init__(self, out_dir="output"):
        self._dir = Path(out_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def save_all(self, result, stats):
        export = result.drop(columns=["tokens"], errors="ignore")
        paths = {"csv": self._dir / "results.csv",
                 "json": self._dir / "results.json",
                 "xlsx": self._dir / "results.xlsx",
                 "txt": self._dir / "summary.txt"}
        export.to_csv(paths["csv"], index=False, encoding="utf-8-sig")
        export.to_json(paths["json"], orient="records", force_ascii=False, indent=2)
        export.to_excel(paths["xlsx"], index=False, sheet_name="Results")
        with open(paths["txt"], "w", encoding="utf-8") as fh:
            fh.write(self.summary_text(stats))
        return {k: str(v) for k, v in paths.items()}

    @staticmethod
    def summary_text(stats):
        c = stats["counts"]
        return (f"Усього повідомлень: {stats['total']}\n"
                f"Позитивних: {c['positive']}\nНейтральних: {c['neutral']}\n"
                f"Негативних: {c['negative']}\n"
                f"Середня оцінка: {stats['mean_score']:.3f}\n"
                f"Медіана: {stats['median_score']:.3f}\n"
                f"Стд. відхилення: {stats['std_score']:.3f}\n"
                f"Середня суб'єктивність: {stats['mean_subjectivity']:.3f}\n"
                f"Узгодженість VADER/TextBlob: {stats['agreement']*100:.1f}%\n")


class ReportGenerator:
    """Формує підсумковий PDF-звіт із таблицями та графіками."""

    def __init__(self, out_dir="output"):
        self._dir = Path(out_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        # шрифт із підтримкою кирилиці (входить до складу matplotlib)
        font = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
        bold = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans-Bold.ttf"
        pdfmetrics.registerFont(TTFont("DejaVu", str(font)))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(bold)))
        base = getSampleStyleSheet()
        self._h1 = ParagraphStyle("h1", parent=base["Heading1"], fontName="DejaVu-Bold")
        self._h2 = ParagraphStyle("h2", parent=base["Heading2"], fontName="DejaVu-Bold")
        self._p = ParagraphStyle("p", parent=base["BodyText"], fontName="DejaVu", fontSize=9.5)
        self._cell = ParagraphStyle("c", parent=self._p, fontSize=8, leading=10)

    def build(self, result, stats, charts, settings):
        path = self._dir / "report.pdf"
        doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2*cm,
                                rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
                                title="Звіт з аналізу тональності")
        s = [Paragraph("Звіт з аналізу тональності текстів", self._h1),
             Paragraph(f"Дата: {datetime.now():%d.%m.%Y %H:%M}. "
                       f"Файл: {settings['input_file']}. "
                       f"Пороги: +{settings['pos_threshold']} / {settings['neg_threshold']}.",
                       self._p), Spacer(1, 10),
             Paragraph("1. Зведена статистика", self._h2)]
        c = stats["counts"]
        rows = [["Показник", "Значення"],
                ["Усього повідомлень", stats["total"]],
                ["Позитивні / нейтральні / негативні",
                 f"{c['positive']} / {c['neutral']} / {c['negative']}"],
                ["Середня оцінка", f"{stats['mean_score']:.3f}"],
                ["Медіана", f"{stats['median_score']:.3f}"],
                ["Стандартне відхилення", f"{stats['std_score']:.3f}"],
                ["Середня суб'єктивність", f"{stats['mean_subjectivity']:.3f}"],
                ["Узгодженість VADER/TextBlob", f"{stats['agreement']*100:.1f}%"]]
        s += [self._table(rows, [9*cm, 6*cm]), Spacer(1, 10),
              Paragraph("2. Графіки", self._h2)]
        for img in charts:
            s += [Image(img, width=13*cm, height=13*cm * self._ratio(img)), Spacer(1, 6)]
        s += [PageBreak(), Paragraph("3. Результати по повідомленнях", self._h2)]
        data = [["ID", "Текст", "VADER", "TextBlob", "Оцінка", "Клас"]]
        for _, r in result.iterrows():
            data.append([r["id"], Paragraph(str(r["text"]), self._cell),
                         f"{r['vader_compound']:.2f}", f"{r['tb_polarity']:.2f}",
                         f"{r['score']:.2f}", r["label"]])
        s.append(self._table(data, [1*cm, 8.2*cm, 1.7*cm, 1.9*cm, 1.7*cm, 1.9*cm], 8))
        doc.build(s)
        return str(path)

    @staticmethod
    def _ratio(img_path):
        from PIL import Image as PILImage
        w, h = PILImage.open(img_path).size
        return h / w

    @staticmethod
    def _table(rows, widths, font=9.5):
        t = Table(rows, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
            ("FONTSIZE", (0, 0), (-1, -1), font),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f3")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        return t
