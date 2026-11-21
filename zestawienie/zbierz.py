#!/usr/bin/env python3
"""Zbiera wszystko, co przeszło filtr, do JSONL i do PDF.

Człowiek później odrzuca fałszywe trafienia. Ten plik nie zastępuje
cytowanego BG1879-a-KJV.pdf.
"""

from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF

import filtr
from filtr import align_book, build_lexicon, judge, load

OUT_DIR = Path(__file__).resolve().parent / "kandydaci"
JSONL = OUT_DIR / "strukturalne.jsonl"
PDF = Path(__file__).resolve().parent.parent / "BG1879-a-KJV-filtr.pdf"


def font(name: str) -> str:
    root = Path("/usr/share/fonts/truetype/dejavu")
    path = root / name
    if not path.is_file():
        raise SystemExit(f"brak czcionki {path}")
    return str(path)


class Doc(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.add_font("sans", "", font("DejaVuSans.ttf"))
        self.add_font("sans", "B", font("DejaVuSans-Bold.ttf"))
        self.add_font("serif", "", font("DejaVuSerif.ttf"))
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(16, 16, 16)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("sans", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, "Filtr całości  ·  BG 1879 i KJV  ·  do odrzucenia ręcznego",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-12)
        self.set_font("sans", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)

    def mc(self, text, style="", size=9, h=4.6):
        self.set_font("sans" if style or size != 9 else "serif", style, size)
        self.set_x(self.l_margin)
        self.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def collect():
    books = load()
    lexicon = build_lexicon(books)
    hits = []
    seen = 0
    for book in books:
        for para in align_book(book["i"], book["pl"], book["en"], book["bg"], book["kjv"]):
            seen += 1
            if para.kind != "werset":
                continue
            judge(para, lexicon)
            if not para.reasons:
                continue
            hits.append({
                "book_pl": para.book_pl,
                "book_en": para.book_en,
                "bg_ref": para.bg_ref,
                "kjv_ref": para.kjv_ref,
                "bg": para.bg,
                "kjv": para.kjv,
                "powody": para.reasons,
                "szczegoly": para.detail,
            })
    return seen, hits


def write_pdf(hits: list[dict]) -> None:
    pdf = Doc()
    pdf.set_title("Filtr całości BG 1879 i KJV")
    pdf.set_lang("pl")
    pdf.add_page()
    pdf.set_font("sans", "B", 16)
    pdf.multi_cell(0, 8, "Wszystko, co przeszło przez filtr")
    pdf.ln(2)
    pdf.set_font("sans", "", 10)
    pdf.multi_cell(0, 5, (
        "To nie jest zestawienie cytowane. Są tu wszystkie pary, które filtr "
        "zatrzymał: liczba, nawias, przeczenie, imię zostawione tylko po jednej "
        "stronie, oraz kilka par obrazu. Fałszywe trafienia odrzuca się później. "
        f"Par: {len(hits)}."
    ))
    pdf.ln(2)
    for i, hit in enumerate(hits, 1):
        if pdf.y > 250:
            pdf.add_page()
        ref = f"{hit['book_pl']} {hit['bg_ref']}"
        if hit["kjv_ref"] and hit["kjv_ref"] != hit["bg_ref"]:
            ref += f"  =  {hit['book_en']} {hit['kjv_ref']}"
        pdf.mc(f"{i}.  {ref}   [{', '.join(hit['powody'])}]", style="B", size=9, h=5)
        if hit["szczegoly"]:
            pdf.set_text_color(80, 80, 80)
            pdf.mc(hit["szczegoly"], size=8, h=4)
            pdf.set_text_color(0, 0, 0)
        pdf.set_font("serif", "", 9)
        pdf.mc("BG  " + hit["bg"])
        pdf.mc("KJV  " + hit["kjv"])
        pdf.ln(1.2)
    pdf.output(str(PDF))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen, hits = collect()
    with JSONL.open("w", encoding="utf-8") as fh:
        for hit in hits:
            fh.write(json.dumps(hit, ensure_ascii=False) + "\n")
    write_pdf(hits)
    print(f"widziane={seen} trafienia={len(hits)}")
    print(f"jsonl={JSONL}")
    print(f"pdf={PDF}")


if __name__ == "__main__":
    main()
