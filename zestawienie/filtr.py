#!/usr/bin/env python3
"""Filtr całości: Biblia gdańska 1879 wobec KJV.

Każdy werset jest zestawiany ze swoim odpowiednikiem, a potem przechodzi
przez filtr. PDF z tego pliku zbiera wszystko, co filtr zatrzymał.
Człowiek później odrzuca fałszywe trafienia. Opis: zestawienie/calosc.md.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BG_ROOT = Path(os.environ["BG1879"]) if os.environ.get("BG1879") else Path("/tmp/bg-one/1879")
if not BG_ROOT.is_dir():
    BG_ROOT = REPO / "zrodla" / "biblia-druk-tekst" / "1879"
KJV_PATH = Path(os.environ["KJV_JSON"]) if os.environ.get("KJV_JSON") else Path("/tmp/bible-one/json/en_kjv.json")
if not KJV_PATH.is_file():
    KJV_PATH = REPO / "zrodla" / "bible" / "json" / "en_kjv.json"

PL = [
    "1 Moj.", "2 Moj.", "3 Moj.", "4 Moj.", "5 Moj.",
    "Joz.", "Sędz.", "Rut", "1 Sam.", "2 Sam.",
    "1 Król.", "2 Król.", "1 Kron.", "2 Kron.", "Ezdr.",
    "Neh.", "Est.", "Ijob", "Ps.", "Prz.",
    "Koh.", "Pnp.", "Iz.", "Jer.", "Lam.",
    "Ez.", "Dan.", "Oz.", "Joel", "Am.",
    "Abd.", "Jon.", "Mich.", "Nah.", "Hab.",
    "Sof.", "Agg.", "Zach.", "Mal.", "Mat.",
    "Mar.", "Łuk.", "Jan", "Dz.", "Rzym.",
    "1 Kor.", "2 Kor.", "Gal.", "Ef.", "Fil.",
    "Kol.", "1 Tes.", "2 Tes.", "1 Tym.", "2 Tym.",
    "Tyt.", "Filem.", "Hebr.", "Jak.", "1 Piotr.",
    "2 Piotr.", "1 Jan", "2 Jan", "3 Jan", "Judy", "Obj.",
]

# Imiona, które są tym samym imieniem mimo innej pisowni. Reszta klas
# powstaje ze rdzenia. Pan, LORD, Bóg i God nie są imionami na tej liście.
ALIASES = {
    "mojzesz": "moses", "mojzesza": "moses", "mojzeszowi": "moses",
    "jezus": "jesus", "jezusa": "jesus", "jezusowi": "jesus", "jezusa": "jesus",
    "dawid": "david", "dawida": "david", "dawidowi": "david",
    "jeruzalem": "jerusalem", "jeruzalemie": "jerusalem", "jeruzalemu": "jerusalem",
    "jeruzalemem": "jerusalem",
    "izrael": "israel", "izraela": "israel", "izraelu": "israel",
    "izraelczyk": "israel", "izraelski": "israel", "izraelskich": "israel",
    "izraelscy": "israel", "izraelskiego": "israel",
    "egipt": "egypt", "egiptu": "egypt", "egipskiej": "egypt", "egipski": "egypt",
    "chrystus": "christ", "chrystusa": "christ", "chrystusowi": "christ",
    "jakob": "jacob", "jakuba": "jacob", "jakubowi": "jacob",
    "jozef": "joseph", "jozefa": "joseph", "jozefowi": "joseph",
    "aaron": "aaron", "aarona": "aaron",
    "abraham": "abraham", "abrahama": "abraham",
    "salomon": "solomon", "salomona": "solomon",
    "jozue": "joshua", "jozu": "joshua",
    "faraon": "pharaoh", "faraona": "pharaoh",
    "noe": "noah", "noego": "noah",
    "saul": "saul", "saula": "saul",
    "piotr": "peter", "piotra": "peter",
    "pawel": "paul", "pawla": "paul",
    "jan": "john", "jana": "john",
    "judzki": "judah", "juda": "judah", "judzie": "judah",
    "babilon": "babylon", "babilonu": "babylon",
    "syjon": "zion", "syjonie": "zion",
    "jordan": "jordan", "jordanu": "jordan",
    "efraim": "ephraim", "benjamin": "benjamin", "moab": "moab",
    "filistyn": "philistine", "filistyni": "philistine", "filistynow": "philistine",
    "lewita": "levite", "lewitow": "levite", "lewici": "levite",
    "azazel": "azazel", "lucyfer": "lucifer", "jehowa": "jehovah",
    "lewi": "levi", "lewiego": "levi", "alfuesz": "alphaeus", "alfeusz": "alphaeus",
}

STOP_EN = {
    "and", "the", "behold", "what", "thou", "thus", "let", "go", "this", "if",
    "o", "i", "a", "but", "then", "now", "he", "his", "when", "where", "who",
    "how", "why", "lord", "god", "father", "son", "spirit", "jews", "ye", "thee",
    "thy", "that", "there", "these", "those", "him", "her", "them", "they",
    "unto", "upon", "into", "from", "with", "for", "not", "nor", "neither",
    "in", "it", "of", "be", "so", "to", "as", "at", "by", "which", "one", "all",
    "shall", "will", "have", "hast", "hath", "said", "came", "went", "come",
    "after", "before", "over", "under", "out", "up", "down", "their", "your",
    "was", "were", "are", "is", "am", "my", "me", "we", "our", "us", "do", "did",
    "no", "yes", "yea", "lo", "also", "even", "every", "any", "such", "than",
    "because", "therefore", "moreover", "again", "yet", "still", "only", "own",
    "man", "men", "people", "house", "land", "king", "day", "night", "hand",
}
STOP_PL = {
    "pan", "pana", "panu", "panie", "panem", "pański", "pańskiego", "pańskie",
    "pańskim", "pańskich", "bóg", "boga", "bogu", "boże", "bożego", "bogiem",
    "boży", "boża", "ja", "i", "a", "nie", "oto", "tak", "izali", "cóż", "ale",
    "więc", "tedy", "przetoż", "przeto", "on", "ona", "ono", "jego", "jej", "ich",
    "ten", "ta", "to", "w", "z", "do", "na", "od", "po", "za", "ku", "rzekł",
    "rzekl", "odpowiedział", "odpowiedzial", "widział", "widzial", "niech",
    "potem", "który", "ktory", "która", "ktora", "które", "ktore", "gdy", "gdyż",
    "gdysz", "albowiem", "abowiem", "bo", "że", "ze", "się", "sie", "jest",
    "był", "byl", "była", "byla", "będzie", "bedzie", "mi", "ci", "go", "mu",
    "ją", "je", "my", "wy", "nas", "was", "tego", "tej", "tym", "tejże", "ów",
    "owa", "owo", "lecz", "ani", "czy", "aż", "az", "już", "juz", "też", "tez",
    "tylko", "sam", "sama", "samo", "wszystek", "wszystka", "wszystko",
}


def strip_diacritics(text: str) -> str:
    text = text.replace("ł", "l").replace("Ł", "L")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def clazz(word: str) -> str:
    w = strip_diacritics(word.lower())
    if w in ALIASES:
        return ALIASES[w]
    for suf in ("owego", "owej", "emu", "ach", "ami", "owi", "ego", "owie", "em", "ie", "om", "ow", "a", "u", "y", "i", "e"):
        if len(w) - len(suf) >= 4 and w.endswith(suf):
            stem = w[: -len(suf)]
            return ALIASES.get(stem, stem)
    return ALIASES.get(w, w)


# --- liczby ---------------------------------------------------------------

_PL_UNIT = {
    "jeden": 1, "jedna": 1, "jedno": 1, "jednego": 1, "jednym": 1, "jednemu": 1,
    "jednej": 1, "jednem": 1,
    "pierwszy": 1, "pierwsza": 1, "pierwszego": 1, "pierwszym": 1, "pierwsze": 1,
    "oba": 2, "obie": 2, "obydwa": 2, "obydwie": 2, "obojga": 2,
    "dwa": 2, "dwie": 2, "dwu": 2, "dwoch": 2, "dwaj": 2,
    "trzy": 3, "trzech": 3,
    "cztery": 4, "czterech": 4,
    "piec": 5, "pieciu": 5,
    "szesc": 6, "szesciu": 6,
    "siedem": 7, "siedm": 7, "siedmiu": 7,
    "osiem": 8, "osm": 8,
    "dziewiec": 9, "dziewieciu": 9,
}
_PL_TEEN = {
    "jedenascie": 11, "dwanascie": 12, "trzynascie": 13, "czternascie": 14,
    "pietnascie": 15, "szesnascie": 16, "siedemnascie": 17, "osiemnascie": 18,
    "osmnascie": 18, "dziewietnascie": 19, "dziesiec": 10,
}
_PL_TEN = {
    "dwadziescia": 20, "trzydziesci": 30, "czterdziesci": 40, "piecdziesiat": 50,
    "szescdziesiat": 60, "siedemdziesiat": 70, "siedmdziesiat": 70,
    "osiemdziesiat": 80, "osmdziesiat": 80, "dziewiecdziesiat": 90,
}
_PL_HUND = {
    "sto": 100, "dwiescie": 200, "trzysta": 300, "czterysta": 400, "piecset": 500,
    "szescset": 600, "siedemset": 700, "siedmset": 700, "osiemset": 800, "osmset": 800,
    "dziewiecset": 900,
}
_KROC = {
    "siedmkroc": 7, "dwarazy": 2, "dwakroc": 2, "trzykroc": 3, "czterokroc": 4,
    "pieciokroc": 5, "szesciokroc": 6, "siedmiokroc": 7, "osmiokroc": 8,
    "dwoje": 2, "dwojgu": 2, "dwojga": 2, "siedmioro": 7, "siedmiorako": 7,
}
# „siedmioraką”, „siedmiorakie” — siedem razy.
_KROC_PREFIX = (("siedmiorak", 7), ("sevens", 7))

_EN_UNIT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "first": 1,
}
_EN_TEEN = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_EN_TEN = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "threescore": 60, "fourscore": 80,
}


def _tokens(text: str) -> list[str]:
    raw = strip_diacritics(text.lower())
    raw = raw.replace("siedmkroc", " siedmkroc ")
    return re.findall(r"[a-z]+|\d+", raw)


def numbers_pl(text: str) -> list[int]:
    toks = _tokens(text)
    out: list[int] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.isdigit():
            out.append(int(t))
            i += 1
            continue
        for pref, valp in (
            ("jedenasc", 11), ("dwanasc", 12), ("trzynasc", 13), ("czternasc", 14),
            ("pietnasc", 15), ("szesnasc", 16), ("siedemnasc", 17),
            ("osiemnasc", 18), ("osmnasc", 18), ("dziewietnasc", 19),
        ):
            if t.startswith(pref):
                out.append(valp)
                i += 1
                break
        else:
            pref = None
        if pref:
            continue
        if t in _KROC or any(t.startswith(p) for p, _ in _KROC_PREFIX):
            out.append(_KROC[t] if t in _KROC else next(v for p, v in _KROC_PREFIX if t.startswith(p)))
            i += 1
            continue
        val = None
        used = 0
        if t in _PL_HUND:
            val = _PL_HUND[t]
            used = 1
        elif t in _PL_UNIT and i + 1 < len(toks) and toks[i + 1] in ("set", "sta"):
            val = _PL_UNIT[t] * 100
            used = 2
        elif t in _PL_TEN:
            val = _PL_TEN[t]
            used = 1
        elif t in _PL_TEEN:
            val = _PL_TEEN[t]
            used = 1
        elif t in _PL_UNIT:
            val = _PL_UNIT[t]
            used = 1
        else:
            i += 1
            continue
        j = i + used
        # „i” łączące dziesiątki albo jedności, oraz dalszy człon tej samej liczby
        while j < len(toks):
            n = toks[j]
            if n == "i" and j + 1 < len(toks):
                n2 = toks[j + 1]
                if n2 in _PL_TEN and val is not None and val % 100 == 0:
                    val += _PL_TEN[n2]
                    j += 2
                    continue
                if n2 in _PL_UNIT and val is not None and val >= 20:
                    val += _PL_UNIT[n2]
                    j += 2
                    continue
                if n2 in _KROC and val is not None and val >= 20:
                    val += _KROC[n2]
                    j += 2
                    continue
            if n in _PL_TEN and val is not None and val % 100 == 0:
                val += _PL_TEN[n]
                j += 1
                continue
            if n in _PL_UNIT and val is not None and val >= 20 and val % 10 == 0:
                val += _PL_UNIT[n]
                j += 1
                continue
            break
        if val is not None:
            out.append(val)
        i = j
    return _collapse_pair(out)


def _collapse_pair(nums: list[int]) -> list[int]:
    """„siedmioro a siedmioro” i „two and two” to jedno powtórzenie, nie dwie liczby."""
    out: list[int] = []
    for n in nums:
        if out and out[-1] == n:
            continue
        out.append(n)
    return out


def numbers_en(text: str) -> list[int]:
    toks = _tokens(text)
    out: list[int] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.isdigit():
            out.append(int(t))
            i += 1
            continue
        if t == "an" and i + 1 < len(toks) and toks[i + 1] in ("hundred", "thousand"):
            t = "one"
        if t in ("score",):
            i += 1
            continue
        if t == "sevens":
            out.append(7)
            i += 1
            continue
        if t.endswith("fold") and t[:-4] in _EN_UNIT:
            # sevenfold bywa osobno; „seventy and sevenfold” skleja się niżej
            bare = _EN_UNIT[t[:-4]]
            if out and out[-1] >= 20 and out[-1] % 10 == 0:
                out[-1] += bare
            else:
                out.append(bare)
            i += 1
            continue
        if t not in _EN_UNIT and t not in _EN_TEEN and t not in _EN_TEN and t not in ("hundred", "thousand"):
            i += 1
            continue
        val = 0
        j = i
        # „five and twenty”
        if t in _EN_UNIT and j + 2 < len(toks) and toks[j + 1] == "and" and toks[j + 2] in _EN_TEN:
            val = _EN_TEN[toks[j + 2]] + _EN_UNIT[t]
            j += 3
        else:
            hundred_done = False
            while j < len(toks):
                n = toks[j]
                if n == "and":
                    j += 1
                    continue
                if n in _EN_UNIT and j + 1 < len(toks) and toks[j + 1] == "hundred":
                    val += _EN_UNIT[n] * 100
                    j += 2
                    hundred_done = True
                    continue
                if n == "hundred":
                    val += 100
                    j += 1
                    hundred_done = True
                    continue
                if n in _EN_UNIT and j + 1 < len(toks) and toks[j + 1] == "thousand":
                    val += _EN_UNIT[n] * 1000
                    j += 2
                    continue
                if n == "thousand":
                    val = (val or 1) * 1000
                    j += 1
                    continue
                if n in _EN_TEN:
                    val += _EN_TEN[n]
                    j += 1
                    if j < len(toks) and toks[j] in _EN_UNIT:
                        val += _EN_UNIT[toks[j]]
                        j += 1
                    elif j + 1 < len(toks) and toks[j] == "and" and toks[j + 1].endswith("fold") and toks[j + 1][:-4] in _EN_UNIT:
                        val += _EN_UNIT[toks[j + 1][:-4]]
                        j += 2
                    continue
                if n in _EN_TEEN:
                    val += _EN_TEEN[n]
                    j += 1
                    continue
                if n in _EN_UNIT and (hundred_done or val >= 20):
                    val += _EN_UNIT[n]
                    j += 1
                    continue
                if n in _EN_UNIT and val == 0 and not hundred_done:
                    val = _EN_UNIT[n]
                    j += 1
                    break
                break
        if j == i:
            i += 1
            continue
        if val:
            out.append(val)
        i = j
    return _collapse_pair(out)


def numbers(text: str, lang: str) -> list[int]:
    return numbers_pl(text) if lang == "pl" else numbers_en(text)


def _numbers_differ(nb: list[int], nk: list[int]) -> bool:
    """Ta sama liczba zapisana w częściach (dziewięć set i trzydzieści = 930) nie jest różnicą."""
    if sorted(nb) == sorted(nk):
        return False
    if sum(nb) != sum(nk):
        return True
    if len(nb) == 1 or len(nk) == 1:
        return False
    return True


# --- imiona, nawias, przeczenie ------------------------------------------

_NAME_RE = re.compile(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+")


def _lexicon(books_token_counts: dict[str, int], stop: set[str], minimum: int) -> set[str]:
    lex = set()
    for word, n in books_token_counts.items():
        if n < minimum:
            continue
        low = word.lower()
        if low in stop or strip_diacritics(low) in stop:
            continue
        if word[:1].isupper():
            c = clazz(word)
            if len(c) >= 4 and c not in stop:
                lex.add(c)
    return lex


def name_classes(text: str, lexicon: set[str]) -> set[str]:
    """Imię własne: wielka litera w środku zdania, nie zwykłe słowo po kropce."""
    found = set()
    for part in re.split(r"[.!?]\s+", text):
        words = _NAME_RE.findall(part)
        for i, word in enumerate(words):
            if i == 0 or not word[:1].isupper():
                continue
            if strip_diacritics(word.lower()) in STOP_PL or word.lower() in STOP_EN:
                continue
            c = clazz(word)
            if len(c) < 4:
                continue
            if c in lexicon or c in ("azazel", "lucifer", "jehovah"):
                found.add(c)
    return found


# „nie” w „na nie” to zaimek, nie przeczenie. „niewiasta” i „niebo” też nie.
_NIE_RZECZ = re.compile(
    r"nie(bo|bios|wiast|przyjac|wol|win|praw|poboz|sprawied)",
    re.I,
)
_PREP_NIE = re.compile(
    r"\b(na|w|z|do|od|przez|za|przed|nad|pod|miedzy|ku|o|po|dla|bez|we|ze)\s+nie\b",
    re.I,
)
_NEG_EN = re.compile(r"\b(not|neither|nor|never|none|nothing|nobody)\b", re.I)
_NEG_PL_WORD = re.compile(r"\b(nie|ani|ni|nigdy|zaden|zadna|zadne|nikt|nikogo|nic)\b", re.I)
# Inny obraz przy tym samym miejscu. Obie strony muszą mieć swój wyraz.
_OBRAZ = (
    ("rozpostarcie", "firmament"),
    ("upodobanie", "good will"),
    ("ojciec", "joseph"),
    ("azazel", "scapegoat"),
    ("zadosc", "world"),
    ("jutrzenk", "lucifer"),
)

_EXPLICIT_NAMES = (
    ("azazel", "azazel"),
    ("lucyfer", "lucifer"),
    ("jehowa", "jehovah"),
)
_PAREN = re.compile(r"\([^)]{0,200}\)")


def has_neg(text: str, lang: str) -> bool:
    t = strip_diacritics(text)
    if lang == "en":
        return bool(_NEG_EN.search(t))
    if _NEG_PL_WORD.search(t) and not _PREP_NIE.search(t):
        # samo „nie” po przyimku to zaimek; inne „nie” w tym wersecie mogą zostać
        words = re.findall(r"[a-z]+", t.lower())
        for i, w in enumerate(words):
            if w in ("ani", "ni", "nigdy", "zaden", "zadna", "zadne", "nikt", "nikogo", "nic"):
                return True
            if w == "nie" and (i == 0 or words[i - 1] not in (
                "na", "w", "z", "do", "od", "przez", "za", "przed", "nad", "pod",
                "miedzy", "ku", "o", "po", "dla", "bez", "we", "ze",
            )):
                return True
    for w in re.findall(r"[a-z]+", t.lower()):
        if w.startswith((
            "niewiem", "niewiesz", "niewie", "niemasz", "niemam", "niebede",
            "niebedzie", "niebyl", "niebyla", "niebylo", "niemogl", "niemogla",
            "niemogli", "niechce", "niechca", "niewypelni",
        )):
            return True
    return False


def explicit_name_sides(text: str) -> set[str]:
    t = strip_diacritics(text.lower())
    found = set()
    for pl, en in _EXPLICIT_NAMES:
        if re.search(r"\b" + pl, t) or re.search(r"\b" + en, t):
            found.add(en)
    return found


# --- zestawienie wersetów ------------------------------------------------

@dataclass
class Para:
    book_pl: str
    book_en: str
    bg_ref: str
    kjv_ref: str
    bg: str
    kjv: str
    kind: str = "werset"  # werset | naglowek
    reasons: list[str] = field(default_factory=list)
    detail: str = ""


def _ref(ch: int, a: int, b: int | None = None) -> str:
    if b is None or a == b:
        return f"{ch},{a}"
    return f"{ch},{a}-{b}"


def _join(lines: list[str], start: int, end: int) -> str:
    return " ".join(lines[start - 1 : end])


def _add(pairs: list[Para], book_pl: str, book_en: str, bg_ch, bg_lines, bg_a, bg_b, kj_ch, kj_lines, kj_a, kj_b, kind="werset"):
    bg = _join(bg_lines, bg_a, bg_b) if bg_ch else ""
    kj = _join(kj_lines, kj_a, kj_b) if kj_ch else ""
    pairs.append(Para(
        book_pl, book_en,
        _ref(bg_ch, bg_a, bg_b) if bg_ch else "",
        _ref(kj_ch, kj_a, kj_b) if kj_ch else "",
        bg, kj, kind,
    ))


def _one_to_one(pairs, book_pl, book_en, ch, bg, kj):
    n = min(len(bg), len(kj))
    for i in range(1, n + 1):
        _add(pairs, book_pl, book_en, ch, bg, i, i, ch, kj, i, i)
    for i in range(n + 1, len(bg) + 1):
        _add(pairs, book_pl, book_en, ch, bg, i, i, None, kj, 1, 0)
    for i in range(n + 1, len(kj) + 1):
        _add(pairs, book_pl, book_en, None, bg, 1, 0, ch, kj, i, i)


def align_psalm(book_pl, book_en, n, bg, kj) -> list[Para]:
    pairs: list[Para] = []
    off = len(bg) - len(kj)
    if n == 13 and off == 0:
        _add(pairs, book_pl, book_en, n, bg, 1, 1, None, kj, 1, 0, "naglowek")
        for i in range(1, 5):
            _add(pairs, book_pl, book_en, n, bg, i + 1, i + 1, n, kj, i, i)
        _add(pairs, book_pl, book_en, n, bg, 6, 6, n, kj, 5, 6)
        return pairs
    if n == 16 and off == 0:
        _add(pairs, book_pl, book_en, n, bg, 1, 1, None, kj, 1, 0, "naglowek")
        _add(pairs, book_pl, book_en, n, bg, 2, 2, n, kj, 1, 2)
        for i in range(3, 12):
            _add(pairs, book_pl, book_en, n, bg, i, i, n, kj, i, i)
        return pairs
    if n == 66 and off == 0:
        _add(pairs, book_pl, book_en, n, bg, 1, 1, None, kj, 1, 0, "naglowek")
        _add(pairs, book_pl, book_en, n, bg, 2, 2, n, kj, 1, 2)
        for i in range(3, 21):
            _add(pairs, book_pl, book_en, n, bg, i, i, n, kj, i, i)
        return pairs
    if off > 0:
        for i in range(1, off + 1):
            _add(pairs, book_pl, book_en, n, bg, i, i, None, kj, 1, 0, "naglowek")
        for i in range(1, len(kj) + 1):
            _add(pairs, book_pl, book_en, n, bg, i + off, i + off, n, kj, i, i)
        return pairs
    line = bg[0]
    m = re.match(r"^((?:Psalm|Pieśń|Przedniejszemu|Złota pieśń)[^.]{0,80})\.\s+(\S.*)$", line)
    if m:
        _add(pairs, book_pl, book_en, n, [m.group(1) + "."], 1, 1, None, kj, 1, 0, "naglowek")
        rest = [m.group(2)] + bg[1:]
        for i in range(1, len(kj) + 1):
            _add(pairs, book_pl, book_en, n, rest, i, i, n, kj, i, i)
        return pairs
    _one_to_one(pairs, book_pl, book_en, n, bg, kj)
    return pairs


def align_book(book_i: int, book_pl: str, book_en: str, bg: dict[int, list[str]], kjv: list[list[str]]) -> list[Para]:
    if book_i == 18:
        pairs: list[Para] = []
        for n, k in enumerate(kjv, 1):
            pairs.extend(align_psalm(book_pl, book_en, n, bg[n], k))
        return pairs
    pairs = []
    # Rozdziały objęte ręcznym szwem. Reszta idzie jeden do jednego.
    handled: set[int] = set()

    def take(ch: int) -> tuple[list[str], list[str]]:
        handled.add(ch)
        return bg[ch], kjv[ch - 1]

    def oo(ch: int, b: list[str], k: list[str]):
        _one_to_one(pairs, book_pl, book_en, ch, b, k)

    if book_i == 2:  # Kapłańska
        b, k = take(16)
        for i in range(1, 34):
            _add(pairs, book_pl, book_en, 16, b, i, i, 16, k, i, i)
        _add(pairs, book_pl, book_en, 16, b, 34, 35, 16, k, 34, 34)
        b, k = take(24)
        for i in range(1, 23):
            _add(pairs, book_pl, book_en, 24, b, i, i, 24, k, i, i)
        _add(pairs, book_pl, book_en, 24, b, 23, 24, 24, k, 23, 23)
    elif book_i == 3:  # Liczb
        b12, k12 = take(12)
        b13, k13 = take(13)
        for i in range(1, 16):
            _add(pairs, book_pl, book_en, 12, b12, i, i, 12, k12, i, i)
        _add(pairs, book_pl, book_en, 13, b13, 1, 1, 12, k12, 16, 16)
        for i in range(1, 34):
            _add(pairs, book_pl, book_en, 13, b13, i + 1, i + 1, 13, k13, i, i)
        b29, k29 = take(29)
        b30, k30 = take(30)
        for i in range(1, 40):
            _add(pairs, book_pl, book_en, 29, b29, i, i, 29, k29, i, i)
        _add(pairs, book_pl, book_en, 30, b30, 1, 1, 29, k29, 40, 40)
        for i in range(1, 17):
            _add(pairs, book_pl, book_en, 30, b30, i + 1, i + 1, 30, k30, i, i)
    elif book_i == 8:  # 1 Samuela
        b, k = take(20)
        for i in range(1, 42):
            _add(pairs, book_pl, book_en, 20, b, i, i, 20, k, i, i)
        _add(pairs, book_pl, book_en, 20, b, 42, 43, 20, k, 42, 42)
        b23, k23 = take(23)
        b24, k24 = take(24)
        for i in range(1, 29):
            _add(pairs, book_pl, book_en, 23, b23, i, i, 23, k23, i, i)
        _add(pairs, book_pl, book_en, 24, b24, 1, 1, 23, k23, 29, 29)
        for i in range(1, 23):
            _add(pairs, book_pl, book_en, 24, b24, i + 1, i + 1, 24, k24, i, i)
    elif book_i == 10:  # 1 Królewska
        b, k = take(22)
        for i in range(1, 43):
            _add(pairs, book_pl, book_en, 22, b, i, i, 22, k, i, i)
        _add(pairs, book_pl, book_en, 22, b, 43, 44, 22, k, 43, 43)
        for i in range(44, 54):
            _add(pairs, book_pl, book_en, 22, b, i + 1, i + 1, 22, k, i, i)
    elif book_i == 17:  # Ijob
        b36, k36 = take(36)
        b37, k37 = take(37)
        for i in range(1, 34):
            _add(pairs, book_pl, book_en, 36, b36, i, i, 36, k36, i, i)
        _add(pairs, book_pl, book_en, 36, b36, 34, 34, 37, k37, 1, 1)
        for i in range(2, 25):
            _add(pairs, book_pl, book_en, 37, b37, i - 1, i - 1, 37, k37, i, i)
        b38, k38 = take(38)
        b39, k39 = take(39)
        b40, k40 = take(40)
        b41, k41 = take(41)
        for i in range(1, 39):
            _add(pairs, book_pl, book_en, 38, b38, i, i, 38, k38, i, i)
        for i in range(39, 42):
            _add(pairs, book_pl, book_en, 39, b39, i - 38, i - 38, 38, k38, i, i)
        for i in range(1, 31):
            _add(pairs, book_pl, book_en, 39, b39, i + 3, i + 3, 39, k39, i, i)
        for i in range(1, 6):
            _add(pairs, book_pl, book_en, 39, b39, i + 33, i + 33, 40, k40, i, i)
        for i in range(6, 25):
            _add(pairs, book_pl, book_en, 40, b40, i - 5, i - 5, 40, k40, i, i)
        for i in range(1, 10):
            _add(pairs, book_pl, book_en, 40, b40, i + 19, i + 19, 41, k41, i, i)
        for i in range(10, 35):
            _add(pairs, book_pl, book_en, 41, b41, i - 9, i - 9, 41, k41, i, i)
    elif book_i == 20:  # Kohelet
        b4, k4 = take(4)
        b5, k5 = take(5)
        for i in range(1, 17):
            _add(pairs, book_pl, book_en, 4, b4, i, i, 4, k4, i, i)
        _add(pairs, book_pl, book_en, 4, b4, 17, 17, 5, k5, 1, 1)
        for i in range(2, 21):
            _add(pairs, book_pl, book_en, 5, b5, i - 1, i - 1, 5, k5, i, i)
        b7, k7 = take(7)
        b8, k8 = take(8)
        for i in range(1, 30):
            _add(pairs, book_pl, book_en, 7, b7, i, i, 7, k7, i, i)
        _add(pairs, book_pl, book_en, 7, b7, 30, 30, 8, k8, 1, 1)
        # BG 8,1 jest drugą połową KJV 8,1. Doklejamy ją do tej pary niżej, po złożeniu.
        pairs[-1].bg = pairs[-1].bg + " " + b8[0]
        pairs[-1].bg_ref = "7,30+8,1"
        for i in range(2, 18):
            _add(pairs, book_pl, book_en, 8, b8, i, i, 8, k8, i, i)
    elif book_i == 21:  # Pieśń
        b5, k5 = take(5)
        b6, k6 = take(6)
        for i in range(1, 17):
            _add(pairs, book_pl, book_en, 5, b5, i, i, 5, k5, i, i)
        _add(pairs, book_pl, book_en, 5, b5, 17, 17, 6, k6, 1, 1)
        for i in range(2, 14):
            _add(pairs, book_pl, book_en, 6, b6, i - 1, i - 1, 6, k6, i, i)
    elif book_i == 23:  # Jeremiasz
        b, k = take(29)
        for i in range(1, 30):
            _add(pairs, book_pl, book_en, 29, b, i, i, 29, k, i, i)
        _add(pairs, book_pl, book_en, 29, b, 30, 30, 29, k, 30, 31)
        _add(pairs, book_pl, book_en, 29, b, 31, 31, 29, k, 32, 32)
    elif book_i == 31:  # Jonasz
        b1, k1 = take(1)
        b2, k2 = take(2)
        for i in range(1, 17):
            _add(pairs, book_pl, book_en, 1, b1, i, i, 1, k1, i, i)
        _add(pairs, book_pl, book_en, 2, b2, 1, 1, 1, k1, 17, 17)
        for i in range(1, 11):
            _add(pairs, book_pl, book_en, 2, b2, i + 1, i + 1, 2, k2, i, i)
    elif book_i == 36:  # Aggeusz
        b1, k1 = take(1)
        b2, k2 = take(2)
        for i in range(1, 15):
            _add(pairs, book_pl, book_en, 1, b1, i, i, 1, k1, i, i)
        _add(pairs, book_pl, book_en, 2, b2, 1, 1, 1, k1, 15, 15)
        for i in range(1, 24):
            _add(pairs, book_pl, book_en, 2, b2, i + 1, i + 1, 2, k2, i, i)
    elif book_i == 43:  # Dzieje
        b, k = take(19)
        for i in range(1, 40):
            _add(pairs, book_pl, book_en, 19, b, i, i, 19, k, i, i)
        _add(pairs, book_pl, book_en, 19, b, 40, 40, 19, k, 40, 41)
    elif book_i == 46:  # 2 Koryntian
        b, k = take(11)
        for i in range(1, 32):
            _add(pairs, book_pl, book_en, 11, b, i, i, 11, k, i, i)
        _add(pairs, book_pl, book_en, 11, b, 32, 32, 11, k, 32, 33)
        b, k = take(13)
        for i in range(1, 11):
            _add(pairs, book_pl, book_en, 13, b, i, i, 13, k, i, i)
        _add(pairs, book_pl, book_en, 13, b, 11, 11, 13, k, 11, 12)
        _add(pairs, book_pl, book_en, 13, b, 12, 12, 13, k, 13, 13)
        _add(pairs, book_pl, book_en, 13, b, 13, 13, 13, k, 14, 14)
    elif book_i == 47:  # Galacjan
        b, k = take(1)
        for i in range(1, 23):
            _add(pairs, book_pl, book_en, 1, b, i, i, 1, k, i, i)
        _add(pairs, book_pl, book_en, 1, b, 23, 23, 1, k, 23, 24)
    elif book_i == 59:  # 1 Piotra
        b, k = take(4)
        for i in range(1, 7):
            _add(pairs, book_pl, book_en, 4, b, i, i, 4, k, i, i)
        _add(pairs, book_pl, book_en, 4, b, 7, 8, 4, k, 7, 8)
        for i in range(9, 20):
            _add(pairs, book_pl, book_en, 4, b, i, i, 4, k, i, i)
    elif book_i == 63:  # 3 Jana
        b, k = take(1)
        for i in range(1, 14):
            _add(pairs, book_pl, book_en, 1, b, i, i, 1, k, i, i)
        _add(pairs, book_pl, book_en, 1, b, 14, 15, 1, k, 14, 14)
    elif book_i == 65:  # Objawienie
        b12, k12 = take(12)
        b13, k13 = take(13)
        for i in range(1, 18):
            _add(pairs, book_pl, book_en, 12, b12, i, i, 12, k12, i, i)
        _add(pairs, book_pl, book_en, 12, b12, 18, 18, 13, k13, 1, 1)
        pairs[-1].bg = pairs[-1].bg + " " + b13[0]
        pairs[-1].bg_ref = "12,18+13,1"
        for i in range(2, 19):
            _add(pairs, book_pl, book_en, 13, b13, i, i, 13, k13, i, i)

    for ch in range(1, len(kjv) + 1):
        if ch in handled:
            continue
        oo(ch, bg[ch], kjv[ch - 1])
    return pairs


def load():
    kjv = json.loads(KJV_PATH.read_text(encoding="utf-8"))
    folders = sorted(p for p in BG_ROOT.iterdir() if p.is_dir())
    if len(folders) != 66 or len(kjv) != 66:
        raise SystemExit(f"oczekiwano 66 ksiąg, jest BG {len(folders)} KJV {len(kjv)}")
    books = []
    for i, (folder, book) in enumerate(zip(folders, kjv)):
        chapters = {}
        for f in folder.glob("*.txt"):
            lines = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
            chapters[int(f.stem)] = lines
        books.append({
            "i": i,
            "pl": PL[i],
            "en": book["name"],
            "abbr": book["abbrev"],
            "bg": chapters,
            "kjv": book["chapters"],
        })
    return books


def build_lexicon(books) -> set[str]:
    en: dict[str, int] = {}
    pl: dict[str, int] = {}
    for b in books:
        for ch in b["kjv"]:
            for v in ch:
                words = _NAME_RE.findall(v)
                for i, w in enumerate(words):
                    if i == 0 or not w[:1].isupper():
                        continue
                    en[w] = en.get(w, 0) + 1
        for lines in b["bg"].values():
            for v in lines:
                words = _NAME_RE.findall(v)
                for i, w in enumerate(words):
                    if i == 0 or not w[:1].isupper():
                        continue
                    pl[w] = pl.get(w, 0) + 1
    return _lexicon(en, STOP_EN, 8) | _lexicon(pl, STOP_PL, 8) | {"azazel", "lucifer", "jehovah"}


def judge(para: Para, lexicon: set[str]) -> None:
    if para.kind == "naglowek":
        return
    if not para.bg or not para.kjv:
        para.reasons.append("brak pary")
        para.detail = "Werset nie ma odpowiednika po drugiej stronie."
        return
    nb, nk = numbers(para.bg, "pl"), numbers(para.kjv, "en")
    if _numbers_differ(nb, nk):
        para.reasons.append("liczba")
        para.detail = f"BG {nb} / KJV {nk}"
    pb, pk = _PAREN.findall(para.bg), _PAREN.findall(para.kjv)
    if bool(pb) != bool(pk):
        para.reasons.append("nawias")
        if para.detail:
            para.detail += "; "
        para.detail += "nawias tylko po jednej stronie"
    neg_b, neg_k = has_neg(para.bg, "pl"), has_neg(para.kjv, "en")
    if neg_b != neg_k:
        para.reasons.append("przeczenie")
        if para.detail:
            para.detail += "; "
        para.detail += "przeczenie tylko po jednej stronie"
    # Otwarte porównanie imion zasypuje listę odmianą (Mojżesz / Moses).
    # Tu zostają imiona, które jedna strona zostawia, a druga tłumaczy.
    bgl, kjl = strip_diacritics(para.bg.lower()), para.kjv.lower()
    for pl_bit, en_bit in _OBRAZ:
        if pl_bit in bgl and en_bit in kjl:
            para.reasons.append("obraz")
            if para.detail:
                para.detail += "; "
            para.detail += f"{pl_bit} / {en_bit}"
            break
    cb, ck = explicit_name_sides(para.bg), explicit_name_sides(para.kjv)
    if cb != ck:
        para.reasons.append("imie")
        if para.detail:
            para.detail += "; "
        para.detail += f"BG {sorted(cb) or '—'} / KJV {sorted(ck) or '—'}"


def self_check(books) -> None:
    gen = books[0]
    b = gen["bg"][5]
    k = gen["kjv"][4]
    # 1 Moj. 5,4: ośm set = eight hundred. Nie jest różnicą.
    assert not _numbers_differ(numbers(b[3], "pl"), numbers(k[3], "en")), (numbers(b[3], "pl"), numbers(k[3], "en"), b[3], k[3])
    assert not _numbers_differ(numbers(b[4], "pl"), numbers(k[4], "en")), (numbers(b[4], "pl"), numbers(k[4], "en"), b[4], k[4])
    assert not _numbers_differ(numbers(b[14], "pl"), numbers(k[14], "en")), (numbers(b[14], "pl"), numbers(k[14], "en"))
    for i in range(len(b)):
        if _numbers_differ(numbers(b[i], "pl"), numbers(k[i], "en")):
            raise SystemExit(f"1 Moj. 5,{i+1} fałszywa liczba {numbers(b[i],'pl')} / {numbers(k[i],'en')}\n{b[i]}\n{k[i]}")
    ez = books[25]
    eb, ek = ez["bg"][40][29], ez["kjv"][39][29]
    assert numbers(eb, "pl") != numbers(ek, "en"), (numbers(eb, "pl"), numbers(ek, "en"))
    # Każdy werset KJV i BG jest użyty dokładnie raz.
    for b in books:
        pairs = align_book(b["i"], b["pl"], b["en"], b["bg"], b["kjv"])
        seen_bg: set[tuple[int, int]] = set()
        seen_kj: set[tuple[int, int]] = set()

        def mark(ref: str, into: set, chapter_fallback: int | None):
            if not ref:
                return
            # „7,30+8,1” albo „12,18+13,1” albo „40,30-31” albo „13,5-6”
            for part in ref.split("+"):
                ch_s, verses = part.split(",")
                ch = int(ch_s)
                if "-" in verses:
                    a, c = verses.split("-")
                    for n in range(int(a), int(c) + 1):
                        into.add((ch, n))
                else:
                    into.add((ch, int(verses)))

        for p in pairs:
            mark(p.bg_ref, seen_bg, None)
            mark(p.kjv_ref, seen_kj, None)
        for ch, lines in b["bg"].items():
            for i in range(1, len(lines) + 1):
                if (ch, i) not in seen_bg:
                    raise SystemExit(f"BG opuszczony {b['pl']} {ch},{i}")
        for ch, lines in enumerate(b["kjv"], 1):
            for i in range(1, len(lines) + 1):
                if (ch, i) not in seen_kj:
                    raise SystemExit(f"KJV opuszczony {b['en']} {ch},{i}")
    print("self_check ok")


if __name__ == "__main__":
    bs = load()
    self_check(bs)
