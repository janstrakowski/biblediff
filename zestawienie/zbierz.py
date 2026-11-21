#!/usr/bin/env python3
"""Zbiera pary, które przeszły filtr. PDF-a nie zapisuje.

Wynik wchodzi do zestawienia jako ostatni rozdział. Plik PDF powstaje
w buduj_pdf.py i nie jest częścią repozytorium.
"""

from __future__ import annotations

import json
from pathlib import Path

import filtr
from filtr import align_book, build_lexicon, judge, load

OUT_DIR = Path(__file__).resolve().parent / "kandydaci"


def _key(hit: dict, order: dict[str, int]) -> tuple:
    ref = hit["bg_ref"].split("+")[0]
    chapter, verses = ref.split(",")
    verse = int(verses.split("-")[0])
    return (order[hit["book_pl"]], int(chapter), verse, hit["kjv_ref"])


def load_sense(order: dict[str, int]) -> list[dict]:
    rows = []
    for path in sorted(OUT_DIR.glob("sens-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    rows.sort(key=lambda hit: _key(hit, order))
    return rows


def merge(structural: list[dict], sense: list[dict], order: dict[str, int]) -> list[dict]:
    seen = {(hit["book_pl"], hit["bg_ref"], hit["kjv_ref"]) for hit in structural}
    extra = [hit for hit in sense if (hit["book_pl"], hit["bg_ref"], hit["kjv_ref"]) not in seen]
    return sorted(structural + extra, key=lambda hit: _key(hit, order))


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


def all_hits() -> tuple[int, list[dict]]:
    seen, structural = collect()
    order = {name: i for i, name in enumerate(filtr.PL)}
    sense = load_sense(order)
    return seen, merge(structural, sense, order)


def main():
    seen, hits = all_hits()
    ezek = next(h for h in hits if h["book_pl"] == "Ez." and h["bg_ref"] == "40,30")
    print(f"widziane={seen} pary={len(hits)}")
    print(f"Ez. 40,30 {ezek['powody']} {ezek['szczegoly']}")


if __name__ == "__main__":
    main()
