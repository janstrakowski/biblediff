#!/usr/bin/env python3
"""Zestawienie Biblii gdańskiej z 1879 roku z King James Version.

Cytaty polskie biorą się z folderu 1879 w klonie
https://github.com/UczenJezusa/biblia-druk-tekst (commit zapisany niżej).
Cytaty angielskie biorą się z publicznego tekstu KJV w rewizji z 1769 roku.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(os.environ.get("BG1879", "/tmp/biblia-src/biblia-druk-tekst/1879"))
KJV_PATH = Path(os.environ.get("KJV_JSON", "/tmp/kjv-src/try.json"))
OUT = Path(__file__).resolve().parent.parent / "BG1879-a-KJV.pdf"
COMMIT = "e5b1d3962179321a7bc9e502e634a2354c49a0a5"
COMMIT_WHEN = "8 listopada 2026, 7:57 (czas środkowoeuropejski)"

FONT = "/usr/share/fonts/truetype/dejavu"

# Kolejność ksiąg w repozytorium i w pliku KJV jest ta sama.
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


def load():
    kjv = json.loads(KJV_PATH.read_text(encoding="utf-8"))
    folders = sorted(p for p in ROOT.iterdir() if p.is_dir())
    if len(folders) != 66 or len(kjv) != 66:
        raise SystemExit("oczekiwano 66 ksiąg w obu tekstach")
    books = []
    for i, (folder, book) in enumerate(zip(folders, kjv)):
        chapters = {}
        for f in folder.glob("*.txt"):
            lines = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
            chapters[int(f.stem)] = lines
        books.append({
            "abbr": book["abbrev"],
            "en": book["name"],
            "pl": PL[i],
            "bg": chapters,
            "kjv": book["chapters"],
        })
    return books


def ps_offset(books):
    ps = next(b for b in books if b["abbr"] == "sl")
    return {i: len(ps["bg"][i]) - len(ch) for i, ch in enumerate(ps["kjv"], 1)}


class Doc(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.add_font("sans", "", f"{FONT}/DejaVuSans.ttf")
        self.add_font("sans", "B", f"{FONT}/DejaVuSans-Bold.ttf")
        self.add_font("serif", "", f"{FONT}/DejaVuSerif.ttf")
        self.add_font("serif", "B", f"{FONT}/DejaVuSerif-Bold.ttf")
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(16, 16, 16)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("sans", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, "Biblia gdańska 1879  ·  King James Version", align="L",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(16, 14, 194, 14)
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def mc(self, text, font="sans", style="", size=10, h=5.1, fill=False):
        self.set_font(font, style, size)
        self.set_x(self.l_margin)
        self.multi_cell(0, h, text, fill=fill, align="L", new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_y(-12)
        self.set_font("sans", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)

    def h1(self, text):
        if self.y > 250:
            self.add_page()
        self.ln(2)
        self.mc(text, style="B", size=15, h=7.5)
        self.ln(1)

    def h2(self, text):
        if self.y > 250:
            self.add_page()
        self.ln(2)
        self.mc(text, style="B", size=12, h=6.2)
        self.ln(0.5)

    def h3(self, text):
        if self.y > 255:
            self.add_page()
        self.ln(1.5)
        self.mc(text, style="B", size=11, h=5.6)
        self.ln(0.3)

    def p(self, text):
        self.mc(text)
        self.ln(1.4)

    def bullet(self, text):
        self.mc("•  " + text)
        self.ln(0.6)

    def pair(self, ref, bg, kj, note=None):
        self.mc(ref, style="B", size=10, h=5.2)
        self.set_fill_color(245, 242, 232)
        self.mc("BG 1879.  " + bg, font="serif", size=10, h=5.0, fill=True)
        self.ln(0.8)
        self.set_fill_color(232, 238, 245)
        self.mc("KJV.  " + kj, font="serif", size=10, h=5.0, fill=True)
        self.ln(1.2)
        if note:
            self.p(note)


def main():
    books = load()
    by = {b["abbr"]: b for b in books}
    off = ps_offset(books)
    pdf = Doc()
    pdf.set_title("Biblia gdańska 1879 a King James Version")
    pdf.set_author("Zestawienie tekstu z repozytorium biblia-druk-tekst")
    pdf.set_lang("pl")
    pdf.add_page()
    cover(pdf)
    intro(pdf)
    versification(pdf, books, off)
    sense(pdf)
    sheol(pdf)
    names(pdf)
    church(pdf, books)
    pascha(pdf, books)
    charity(pdf)
    psalm_titles(pdf)
    agreements(pdf)
    limit(pdf)
    pdf.output(str(OUT))
    print(f"wrote {OUT} pages={pdf.page_no()}")


def cover(pdf: Doc):
    pdf.set_font("sans", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 8, "Zestawienie tekstów", align="L")
    pdf.ln(16)
    pdf.set_text_color(0, 0, 0)
    pdf.mc("Biblia gdańska z 1879 roku\na King James Version", style="B", size=22, h=10)
    pdf.ln(3)
    pdf.mc("Różnice tłumaczenia i skąd się wzięły", size=13, h=7)
    pdf.ln(8)
    pdf.mc((
        "Tekst polski: wydanie z 1879 roku w postaci cyfrowej z repozytorium "
        "UczenJezusa/biblia-druk-tekst, folder 1879, commit "
        f"{COMMIT[:12]} ({COMMIT_WHEN}).\n\n"
        "Tekst angielski: King James Version w brzmieniu utrwalonym rewizją "
        "z 1769 roku, czyli ten tekst, który dziś oznacza skrót KJV. Nie jest to "
        "skład z 1611 roku: tamten różni się pisownią i w kilku miejscach także słowem.\n\n"
        "Opracowanie: 21 listopada 2026 (czas warszawski)."
    ))
    pdf.ln(6)
    pdf.set_text_color(70, 70, 70)
    pdf.mc((
        "Wydanie z 1879 roku nie jest nowym przekładem. Jest to tekst Biblii gdańskiej "
        "z 1632 roku, podany w pisowni XIX wieku. Różnice wobec KJV pochodzą więc "
        "z pracy tłumaczy gdańskich, nie z późniejszej modernizacji ortografii."
    ))
    pdf.set_text_color(0, 0, 0)


def intro(pdf: Doc):
    pdf.add_page()
    pdf.h1("1. Co w tym zestawieniu jest różnicą")
    pdf.p(
        "Polski i angielski nie dadzą się porównać słowo w słowo. „Rzekł” i „said”, "
        "„Pan” i „LORD”, „Mojżesz” i „Moses” to ten sam sens w dwóch językach. "
        "Takich par nie ma na liście. Różnicą jest miejsce, w którym czytelnik "
        "obu wydań dostaje inną treść, inny obraz albo inny numer wersetu."
    )
    pdf.bullet("Inny podział wersetów przy tej samej treści. Tekst jest, numer się nie zgadza.")
    pdf.bullet("Inne słowo, które zmienia obraz: grób albo piekło, rozpostarcie albo firmament, Azazel albo kozioł ofiarny.")
    pdf.bullet("Inna podstawa zdania: inny wariant grecki albo inny rozbiór tego samego zdania hebrajskiego.")
    pdf.bullet("Inne oddanie nazwy własnej: imię Boże przetłumaczone albo przepisane, tytuł psalmu przetłumaczony albo zostawiony po hebrajsku.")
    pdf.p(
        "Cytaty są wzięte z folderu 1879 i z tekstu KJV, nie z pamięci nagłówka. "
        "Zamknięte są cztery listy: każdy rozdział o innej liczbie wersetów, cała lista "
        "szeolu, hadesu i gehenny, miejsca, w których KJV pisze JEHOVAH, firmament, "
        "charity, passover albo zostawia hebrajski nagłówek psalmu, oraz aparat wariantów, "
        "w których Textus Receptus i tradycja luterska zwykle się schodzą albo rozchodzą. "
        "Nie jest to kolacjonowanie wszystkich 31 102 wersetów pod kątem każdego synonimu. "
        "Granicę opisuje ostatni rozdział."
    )

    pdf.h1("2. Dlaczego te dwa przekłady są tak blisko")
    pdf.p(
        "Oba są protestanckie i trzymają się tekstu oryginalnego ściślej niż przekłady "
        "swobodne. Stary Testament idzie za tekstem masoreckim. Nowy Testament idzie "
        "za drukowanym tekstem greckim, który od 1633 roku nazywa się Textus Receptus. "
        "Stąd zgoda w miejscach, w których nowsze przekłady już się rozchodzą: "
        "zakończenie Marka, perykopa o kobiecie pojmanej na cudzołóstwie, Comma Johanneum "
        "w 1 Jana 5,7–8, „przebodli ręce moje” w Psalmie 22, „Syn Boży” w Daniela 3,25, "
        "„panna” w Izajasza 7,14."
    )
    pdf.p(
        "Różnice biorą się z tego, co tłumacze mieli na stole obok oryginału. Biblię gdańską "
        "wydano w 1632 roku. Nad przekładem czuwał zespół duchownych luterańskich i reformowanych; "
        "najważniejszym tłumaczem był Daniel Mikołajewski. Pracowano z hebrajskiego i greckiego, "
        "a obok leżały Biblia brzeska, Biblia Lutra i czeska Biblia kralicka. King James Version "
        "ukończono w 1611 roku. Jej tłumacze mieli pod ręką Biblię Genewską, Bishops’ Bible, "
        "Tyndale’a, Wulgatę oraz łacińskie przekłady Tremelliusza i Bezy. Tam, gdzie Luter "
        "albo tradycja czeska rozchodzi się z tradycją angielską, gdańska idzie zwykle za "
        "Lutrem albo za hebrajskim obrazem słowa, a KJV za Wulgatą, za Tyndalem albo za "
        "utartym terminem łacińskim."
    )
    pdf.p(
        "Osobna sprawa to słowa, które w 1611 i w 1879 roku znaczyły to samo, a dziś "
        "rozjechały się w uszach czytelnika. Angielskie charity w 1611 roku znaczyło miłość "
        "(łacińskie caritas). Polskie „pokutujcie” u protestantów XVII wieku znaczyło "
        "to samo co greckie metanoeite i angielskie repent, a nie sakrament pokuty. "
        "„Zakon” znaczył prawo Mojżeszowe, a nie zgromadzenie zakonne. Te pary opisuję "
        "osobno, żeby ich nie mieszać z miejscami, w których sens już wtedy był inny."
    )


def versification(pdf: Doc, books, off):
    pdf.add_page()
    pdf.h1("3. Inny podział wersetów")
    pdf.p(
        "W tych miejscach zdania są te same. Inny jest tylko numer. Biblia gdańska trzyma "
        "się podziału wersetów hebrajskich, tego, który przejęły też Biblia Lutra i Biblia "
        "kralicka. KJV trzyma się podziału utrwalonego w Biblii Genewskiej i w angielskich "
        "wydaniach XVI wieku. Stephanus ponumerował Nowy Testament w 1551 roku; Stary "
        "Testament w tradycji angielskiej dostał własny, nie wszędzie hebrajski podział."
    )

    pdf.h2("3.1. Księgi poza Psalterzem")
    rows = [
        ("3 Moj. 16", "BG ma 35 wersetów, KJV 34.",
         "KJV 16,34 składa się z dwóch zdań. BG kładzie drugie („I uczynił Mojżesz, jako mu był rozkazał Pan”) jako werset 35."),
        ("3 Moj. 24", "BG 24, KJV 23.",
         "To samo cięcie na końcu rozdziału. BG 24,24 to druga połowa KJV 24,23: „I uczynili synowie Izraelscy według tego, jako przykazał Pan Mojżeszowi”."),
        ("4 Moj. 12–13", "BG 12 ma 15 wersetów, KJV 16. BG 13 ma 34, KJV 33.",
         "KJV 12,16 („I ruszył lud z Haserotu…”) jest w BG pierwszym wersetem rozdziału 13. Dalej cały rozdział 13 jest przesunięty o jeden: BG 13,34 = KJV 13,33. Rozdział 14 znowu się schodzi."),
        ("4 Moj. 29–30", "BG 29 ma 39, KJV 40. BG 30 ma 17, KJV 16.",
         "KJV 29,40 jest w BG wersetem 30,1. Cały rozdział 30 jest więc o jeden wyżej: BG 30,17 = KJV 30,16."),
        ("1 Sam. 20", "BG 43, KJV 42.",
         "KJV 20,42 jest rozcięty. BG 20,42 kończy się na przysiędze, a BG 20,43 to zdanie „A tak wstawszy Dawid odszedł, a Jonatan wszedł do miasta”."),
        ("1 Sam. 23–24", "BG 23 ma 28, KJV 29. BG 24 ma 23, KJV 22.",
         "KJV 23,29 („Dawid wyszedł stamtąd i mieszkał w Engaddy”) otwiera w BG rozdział 24. Dalej 1 Sam. 24 jest o jeden wyżej, aż do BG 24,23 = KJV 24,22."),
        ("1 Król. 22", "BG 54, KJV 53.",
         "Wersety schodzą się do 22,42. KJV 22,43 jest w BG rozcięty na 22,43 (Jozafat chodził drogą Azy) i 22,44 (wyżyny). Od tego miejsca BG jest o jeden wyżej, aż do BG 22,54 = KJV 22,53."),
        ("Ijob 36–37", "BG 36 ma 34, KJV 33. BG 37 ma 23, KJV 24.",
         "Rozdziały schodzą się do 36,33. BG 36,34 („A nad tem zdumiewa się serce moje, i porusza się z miejsca swego”) to KJV 37,1. Dalej cały rozdział 37 jest o jeden niżej: BG 37,1 = KJV 37,2, BG 37,23 = KJV 37,24. Rozdział 38 zaczyna się znowu w tym samym miejscu."),
        ("Ijob 38–41", "Liczby rozjeżdżają się o kilka wersetów.",
         "Tu różnica jest większa niż o jeden werset, bo angielski podział mowy Boga z wichru nie pokrywa się z hebrajskim. Sprawdzone styki: KJV 38,39–41 (lew i kruk) = BG 39,1–3. BG 39,34–38 = KJV 40,1–5. BG 40,1 („odpowiedział Pan Ijobowi z wichru”) = KJV 40,6. Behemot i lewiat zaczynają się w BG pod numerami hebrajskimi, więc KJV 41 zaczyna się wcześniej niż BG 41. Treść opisu zwierząt jest ta sama; inny jest numer."),
        ("Koh. 4–5", "BG 4 ma 17, KJV 16. BG 5 ma 19, KJV 20.",
         "BG 4,17 = KJV 5,1 („Strzeż nogi twojej, gdy idziesz do domu Bożego”). Cały rozdział 5 jest o jeden niżej: BG 5,1 = KJV 5,2, BG 5,19 = KJV 5,20. Rozdział 6 znowu się schodzi."),
        ("Koh. 7–8", "BG 7 ma 30, KJV 29. Rozdział 8 ma w obu po 17.",
         "Jedno zdanie KJV 8,1 jest rozcięte o granicę rozdziału. BG 7,30: „Któż może z mądrym porównać? a kto może wyłożyć każdą rzecz?” BG 8,1: „Mądrość człowieka oświeca oblicze jego, a hardość twarzy jego odmienia.” W KJV oba człony stoją w 8,1."),
        ("Pnp. 5–6", "BG 5 ma 17, KJV 16. BG 6 ma 12, KJV 13.",
         "KJV 6,1 jest w BG wersetem 5,17. Dalej BG 6,n = KJV 6,n+1, aż do BG 6,12 = KJV 6,13. Rozdział 7 znowu się schodzi."),
        ("Jer. 29", "BG 31, KJV 32.",
         "Nic nie wypadło. BG 29,30 łączy KJV 29,30 i 29,31. BG 29,31 = KJV 29,32."),
        ("Jon. 1–2", "BG 1 ma 16, KJV 17. BG 2 ma 11, KJV 10.",
         "Zdanie o rybie, które w KJV jest 1,17, otwiera w BG rozdział 2. Dalej Jon. 2 jest o jeden wyżej: BG 2,3 = KJV 2,2, BG 2,11 = KJV 2,10. To podział hebrajski. Osobno, w tym samym miejscu, jest różnica słowa: patrz Jonasz przy szeolu."),
        ("Agg. 1–2", "BG 1 ma 14, KJV 15. BG 2 ma 24, KJV 23.",
         "Data „dnia dwudziestego i czwartego, miesiąca szóstego” jest w KJV wersetem 1,15, a w BG wersetem 2,1. Dalej Aggeusz 2 jest o jeden wyżej: BG 2,24 = KJV 2,23."),
        ("1 Piotr. 4,7–8", "Oba wydania mają 19 wersetów. Cięcie jest w środku.",
         "BG 4,7 to tylko pierwsze zdanie KJV 4,7: „A wszystkiemuć się koniec przybliża.” Wezwanie „trzeźwymi bądźcie i czułymi ku modlitwom” gdańska dokłada do wersetu 8, przed zdaniem o miłości. KJV trzyma trzeźwość w 4,7, a miłość w 4,8. Od 4,9 numery znowu się schodzą."),
        ("Dz. 19", "BG 40, KJV 41.",
         "BG 19,40 łączy KJV 19,40 i 19,41. Zdanie o rozpuszczeniu zgromadzenia jest w BG w tym samym wersecie co obawa o rozruch."),
        ("2 Kor. 11", "BG 32, KJV 33.",
         "BG 11,32 łączy KJV 11,32 i 11,33: i straż Aretasa, i spuszczenie w koszu."),
        ("2 Kor. 13", "BG 13, KJV 14.",
         "BG 13,11 łączy KJV 13,11 i 13,12 (pozdrowienie pocałowaniem). BG 13,12 = KJV 13,13. BG 13,13 = KJV 13,14, błogosławieństwo."),
        ("Gal. 1", "BG 23, KJV 24.",
         "BG 1,23 kończy się słowami „I chwalili Boga ze mnie”, czyli KJV 1,24 jest doklejony do poprzedniego wersetu."),
        ("3 Jan", "BG 15, KJV 14.",
         "BG 1,14 kończy się na „ustnie mówić będziemy”. BG 1,15 to reszta KJV 1,14: „Pokój tobie. Pozdrawiają cię przyjaciele. Pozdrów i ty przyjaciół z imienia.”"),
        ("Obj. 12–13", "BG 12 ma 18, KJV 17.",
         "BG 12,18: „I stanąłem na piasku morskim.” W KJV to zdanie otwiera 13,1, a dalej dopiero jest bestia. BG 13,1 zaczyna się od bestii. Czytanie jest to samo: pierwsza osoba, „stanąłem”, nie „stanął”. Inny jest tylko numer."),
    ]
    for ref, counts, note in rows:
        pdf.h3(ref)
        pdf.p(counts + " " + note)

    pdf.h2("3.2. Psalmy")
    pdf.p(
        "W KJV nagłówek psalmu stoi nad wersetem 1 i nie ma numeru. W Biblii gdańskiej "
        "nagłówek hebrajski jest policzony. Tam, gdzie nagłówek ma jeden werset hebrajski, "
        "BG ma o jeden werset więcej i wiersz n KJV jest wersetem n+1 BG. Tam, gdzie "
        "nagłówek ma dwa wersety (Psalmy 51, 52, 54 i 60), przesunięcie wynosi dwa."
    )
    pdf.p(
        "Część psalmów ma nagłówek włączony w werset 1, razem z pierwszym wierszem pieśni. "
        "Numery dalszych wersetów wtedy się schodzą. Tak jest między innymi w Psalmach "
        "11, 15, 17, 23–29, 32, 35, 37, 50, 73, 74, 78, 79, 82, 86, 90, 98, 100, 101, "
        "103, 109, 110 i w pieśniach stopni 120–134. KJV drukuje ten sam nagłówek osobno, "
        "a werset 1 zaczyna od pieśni. Treść nagłówka jest w obu wydaniach."
    )
    pdf.p("Psalmy, w których sam numer się rozjeżdża: " + "; ".join(
        f"{i} ({off[i]:+d})" for i in range(1, 151) if off[i]
    ) + ".")
    pdf.p(
        "Trzy psalmy mają nagłówek jako osobny werset, a mimo to tyle samo wersetów co KJV, "
        "bo dwa wiersze pieśni są złączone."
    )
    pdf.bullet(
        "Psalm 13. BG 13,1 to sam nagłówek. BG 13,2 = KJV 13,1. BG 13,6 łączy KJV 13,5 i 13,6 "
        "(ufność i śpiew w jednym wersecie)."
    )
    pdf.bullet(
        "Psalm 16. BG 16,1 to „Złota pieśń Dawidowa”. BG 16,2 łączy KJV 16,1 i 16,2. "
        "Od wersetu 3 numery znowu się schodzą, dlatego BG 16,10 stoi naprzeciw KJV 16,10. "
        "Słowo w tym wersecie jest już inne: grób wobec hell. Patrz rozdział o szeolu."
    )
    pdf.bullet(
        "Psalm 66. BG 66,1 to sam nagłówek, a pieśń zaczyna się w 66,2, naprzeciw KJV 66,1. "
        "Rozdział ma w obu wydaniach 20 wersetów, więc dwa wiersze KJV są gdzieś dalej "
        "złączone. Nie wskazuję numeru tego złączenia: bez osobnego kolacjonowania każdego "
        "wiersza łatwo o pomyłkę, a o treść nagłówka tu nie chodzi."
    )


def sense(pdf: Doc):
    pdf.add_page()
    pdf.h1("4. Różnice sensu, sprawdzone na tekście")
    pdf.p(
        "Każdy cytat poniżej jest wzięty z pliku wydania 1879 i z tekstu KJV. "
        "Tam, gdzie numer psalmu albo Jonasza się rozjeżdża, podaję oba numery."
    )

    pdf.h2("4.1. Izajasza 14,12. Jutrzenka, nie Lucyfer")
    pdf.pair(
        "Iz. 14,12",
        "Jakoż to, żeś spadł z nieba, o jutrzenko! która wschodzisz rano? powalonyś aż na ziemię, któryś wątlił narody!",
        "How art thou fallen from heaven, O Lucifer, son of the morning! how art thou cut down to the ground, which didst weaken the nations!",
    )
    pdf.p(
        "Hebrajskie helel ben-szachar znaczy „jaśniejący, syn zorzy”. Nie jest to imię własne. "
        "Hieronim oddał je w Wulgacie słowem Lucifer, „niosący światło”, i to łacińskie imię "
        "weszło do KJV. Luter w wydaniu z 1545 roku ma „du schöner Morgenstern”, piękną "
        "gwiazdę poranną. Biblia gdańska idzie za tym obrazem: „jutrzenka, która wschodzisz rano”. "
        "Różnica nie wynika z innego hebrajskiego słowa. Wynika z tego, że KJV zatrzymał "
        "łacińskie imię, a gdańska przetłumaczyła hebrajski obraz, tak jak Luter."
    )

    pdf.h2("4.2. Łukasza 2,14. Gdzie leży „dobre upodobanie”")
    pdf.pair(
        "Łuk. 2,14",
        "Chwała na wysokościach Bogu, a na ziemi pokój, w ludziach dobre upodobanie.",
        "Glory to God in the highest, and on earth peace, good will toward men.",
    )
    pdf.p(
        "Grecki Textus Receptus ma tu mianownik εὐδοκία, nie dopełniacz εὐδοκίας. Oba przekłady "
        "zostają przy mianowniku, więc nie jest to spór o wariant krytyczny („w ludziach dobrej woli”). "
        "Rozchodzą się w składni. KJV czyta: pokój na ziemi i dobra wola wobec ludzi. "
        "Gdańska czyta: pokój, a w ludziach dobre upodobanie. To jest składnia Lutra: "
        "„den Menschen ein Wohlgefallen”, upodobanie dane ludziom, a nie dobra wola skierowana ku nim. "
        "To samo greckie słowo, inny kierunek zdania."
    )

    pdf.h2("4.3. Łukasza 2,33. Ojciec, nie Józef. Werset 43 już nie")
    pdf.pair(
        "Łuk. 2,33",
        "A ojciec i matka jego dziwowali się temu, co powiadano o nim.",
        "And Joseph and his mother marvelled at those things which were spoken of him.",
    )
    pdf.pair(
        "Łuk. 2,43. Tu różnicy nie ma. Podaję werset, bo stoi tuż obok i łatwo go pomylić z poprzednim.",
        "I gdy skończyli one dni, a już się wracali nazad, zostało dziecię Jezus w Jeruzalemie, a tego nie wiedział Józef i matka jego.",
        "And when they had fulfilled the days, as they returned, the child Jesus tarried behind in Jerusalem; and Joseph and his mother knew not of it.",
    )
    pdf.p(
        "W wersecie 33 greckie rękopisy się rozchodzą. Starsze mają „jego ojciec i matka”. "
        "Textus Receptus, a za nim KJV, ma „Józef i jego matka”. Ta zmiana osłaniała "
        "dziewicze poczęcie przed wnioskiem, że Józef jest ojcem. Luter zostawił „sein Vater und Mutter”. "
        "Gdańska w 2,33 idzie za tym starszym czytaniem. W 2,43 oba wydania mają już „Józef i matka jego”. "
        "Gdańska nie jest więc konsekwentnie po jednej stronie tego wariantu: werset 33 bierze "
        "z tradycji luterskiej i ze starszej greki, werset 43 z Textus Receptus."
    )

    pdf.h2("4.4. Kapłańska 16. Azazel, nie kozioł ofiarny")
    pdf.pair(
        "3 Moj. 16,8",
        "I rzuci Aaron na oba kozły losy; los jeden Panu, a los drugi Azazelowi.",
        "And Aaron shall cast lots upon the two goats; one lot for the LORD, and the other lot for the scapegoat.",
    )
    pdf.pair(
        "3 Moj. 16,10",
        "Ale kozła, na którego padł los Azazela, postawi żywego przed Panem, aby oczyszczenie uczynił przezeń, a wypuścił go do Azazela na puszczą.",
        "But the goat, on which the lot fell to be the scapegoat, shall be presented alive before the LORD, to make an atonement with him, and to let him go for a scapegoat into the wilderness.",
    )
    pdf.pair(
        "3 Moj. 16,26",
        "A ten, który zawiódł kozła do Azazela, upierze szaty swe; a omywszy ciało swoje wodą, potem wnijdzie do obozu.",
        "And he that let go the goat for the scapegoat shall wash his clothes, and bathe his flesh in water, and afterward come into the camp.",
    )
    pdf.p(
        "Hebrajskie la-azazel można czytać jako nazwę, miejsce albo istotę, do której kozioł jest posyłany, "
        "albo jako opis kozła puszczanego wolno. Wulgata ma caper emissarius, „kozioł wysłany”. "
        "Tyndale zrobił z tego scapegoat, kozła, który uchodzi, i to słowo zostało w KJV. "
        "Luter w 1545 roku też opisuje, nie nazywa: „dem ledigen Bock”, kozioł puszczony luzem. "
        "Gdańska zostawia hebrajską nazwę Azazel. Nie jest to więc ślad Lutra z 1545 roku. "
        "Jest to wybór hebrajskiej nazwy własnej przeciwko łacińsko-angielskiemu opisowi."
    )

    pdf.h2("4.5. Rozpostarcie i firmament")
    pdf.pair(
        "1 Moj. 1,6–8. Podaję werset 6; 7 i 8 powtarzają to samo słowo.",
        "Potem rzekł Bóg: Niech będzie rozpostarcie, w pośrodku wód, a niech dzieli wody od wód.",
        "And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters.",
    )
    pdf.p(
        "Hebrajskie raqia pochodzi od czasownika „rozpłaszczyć, rozciągnąć”. "
        "Septuaginta i Wulgata zrobiły z tego coś twardego: stereoma, firmamentum. "
        "KJV wziął firmament z tej linii. Gdańska oddaje hebrajski obraz słowem „rozpostarcie”. "
        "To samo słowo stoi naprzeciw firmament także w 1 Moj. 1,14.15.17.20, w Psalmie 19 "
        "(BG 19,2 = KJV 19,1), w Psalmie 150,1, w Ezechiela 1,22–26 i 10,1."
    )
    pdf.pair(
        "Dan. 12,3. Tu dochodzi druga różnica, nie tylko firmament.",
        "Ale ci, którzy innych nauczają, świecić się będą jako światłość na niebie, a którzy wielu ku sprawiedliwości przywodzą, jako gwiazdy na wieki wieczne.",
        "And they that be wise shall shine as the brightness of the firmament; and they that turn many to righteousness as the stars for ever and ever.",
    )
    pdf.p(
        "Raqia jest tu „niebem”, nie „rozpostarciem” i nie firmamentem. Osobno: "
        "hammaskilim KJV czyta jako „mądrzy”, a gdańska jako „ci, którzy innych nauczają”. "
        "Czasownik w stronie sprawczej może znaczyć jedno i drugie: być roztropnym albo uczyć innych. "
        "KJV bierze pierwszy sens, gdańska drugi."
    )

    pdf.h2("4.6. Koheleta 3,11. Dodane słowo „żądość”")
    pdf.pair(
        "Koh. 3,11",
        "Wszystko dobrze czyni czasu swego; owszem i żądość świata dał do serca ich, choć człowiek dzieła tego, które Bóg sprawuje, ani początku, ani końca nie dochodzi.",
        "He hath made every thing beautiful in his time: also he hath set the world in their heart, so that no man can find out the work that God maketh from the beginning to the end.",
    )
    pdf.p(
        "Dwa odstępstwa od hebrajskiego zdania, nie jeden. Jafe znaczy „piękne”. KJV ma beautiful. "
        "Gdańska ma „dobrze czyni”, czyli dobrze, a nie pięknie. Drugie: ha-olam KJV oddaje jako world, "
        "świat. Nowsze przekłady czytają tu „wieczność”. Gdańska dokłada rzeczownik, którego w zdaniu "
        "nie ma: „żądość świata”, pragnienie świata. To jest wykładnia, nie tłumaczenie osobnego słowa. "
        "KJV tego dodatku nie ma."
    )

    pdf.h2("4.7. Pieśń nad pieśniami 6,11 i wozy Amminadiba")
    pdf.pair(
        "Pnp. BG 6,11 = KJV 6,12. Numer jest przesunięty, patrz rozdział 3.",
        "Niżem się dowiedziała, dusza moja wsadziła mię na wóz przedniejszych z ludu mego.",
        "Or ever I was aware, my soul made me like the chariots of Amminadib.",
    )
    pdf.p(
        "Hebrajskie ammi nadib da się przeczytać jako imię Amminadib albo jako „mój szlachetny lud”. "
        "KJV przepisuje imię. Gdańska tłumaczy: wóz przedniejszych z ludu. Luter ma tu „die Wagen "
        "meines edlen Volks”. Gdańska idzie za tym tłumaczeniem, nie za imieniem."
    )

    pdf.h2("4.8. 1 Samuela 13,1. Zdanie, którego hebrajski nie dopowiada")
    pdf.pair(
        "1 Sam. 13,1",
        "Saul tedy pierwszego roku królowania swego (bo tylko dwa lata królował nad Izraelem,)",
        "Saul reigned one year; and when he had reigned two years over Israel,",
    )
    pdf.p(
        "Hebrajski werset jest urwany: „Saul miał rok… gdy zaczął królować, a dwa lata królował”. "
        "Brakuje liczby lat życia. Oba przekłady próbują to zdanie uratować. KJV zostawia "
        "szorstką kalkę: królował jeden rok, a gdy królował dwa lata. Gdańska wkłada w nawias "
        "wykładnię: „bo tylko dwa lata królował”. Nawiasu w hebrajskim nie ma. To glosa tłumacza "
        "gdańskiego na tym samym uszkodzonym zdaniu."
    )

    pdf.h2("4.9. Ijoba 19,25. Proch, nie ziemia")
    pdf.pair(
        "Ijob 19,25",
        "Aczci ja wiem, iż Odkupiciel mój żyje, a iż w ostateczny dzień nad prochem stanie.",
        "For I know that my redeemer liveth, and that he shall stand at the latter day upon the earth:",
    )
    pdf.p(
        "Afar to proch, pył. Gdańska tak mówi. KJV rozszerza na earth, ziemię. "
        "„Ostateczny dzień” i „the latter day” to ten sam, tradycyjny odczyt słowa acharon. "
        "Werset 26 w obu wydaniach ma „w ciele” i robaki, których hebrajski wprost nie nazywa. "
        "To wspólny dodatek tradycji, nie różnica między tymi dwoma tekstami."
    )


def sheol(pdf: Doc):
    pdf.add_page()
    pdf.h1("5. Szeol: grób, piekło, dół")
    pdf.p(
        "Hebrajski szeol nie ma jednego polskiego ani jednego angielskiego odpowiednika. "
        "KJV rozdziela go na hell, grave i pit. Gdańska rozdziela go na piekło, grób, dół, "
        "przepaść, a raz na samą ziemię. W większości z około sześćdziesięciu pięciu miejsc "
        "wybór pada na tę samą stronę: hell przy piekle, grave przy grobie. Poniżej są "
        "wszystkie miejsca, w których obraz się rozjeżdża. Sprawdzone na pełnej liście "
        "wystąpień szeolu, nie na próbce."
    )
    pdf.p(
        "Skąd to się bierze. Żadne z tych słów nie jest innym hebrajskim wyrazem. "
        "Komitety wybierały obraz osobno w każdym wersecie. KJV w części psalmów i u proroków "
        "zostawia hell, czyli miejsce, które po angielsku brzmi jak kara. Gdańska w tych "
        "samych wersetach często woli grób. Odwrotnie bywa rzadziej: tam KJV ma pit albo grave, "
        "a gdańska piekło. Luter na ogół ma Hölle albo Grab, i gdańska nie kopiuje go mechanicznie. "
        "Widać to po Psalmie 16 i po Dziejach Apostolskich 2, które ten psalm cytują."
    )

    items = [
        ("4 Moj. 16,30 i 16,33",
         "zstąpią żywo do piekła",
         "went down quick into the pit / went down alive into the pit",
         "KJV ma pit, dół. Gdańska ma piekło. To najmocniejsze zaostrzenie w tę stronę: zstąpienie żywcem w ziemię staje się zstąpieniem do piekła."),
        ("2 Sam. 22,6 i Ps. 18. BG 18,6 = KJV 18,5",
         "Boleści grobu ogarnęły mię",
         "The sorrows of hell compassed me about",
         "Ten sam wiersz jest w 2 Samuela 22 i w Psalmie 18. W obu miejscach KJV ma hell, gdańska grób."),
        ("Ijob 17,16",
         "W głębię grobu zstąpię",
         "They shall go down to the bars of the pit",
         "KJV pit, gdańska grób."),
        ("Ijob 26,6",
         "Odkryte są przepaści przed nim, a nie ma przykrycia zatracenie.",
         "Hell is naked before him, and destruction hath no covering.",
         "Szeol: przepaść wobec hell. Drugi człon, Abaddon, zgadza się: zatracenie i destruction."),
        ("Ps. 16,10",
         "Bo nie zostawisz duszy mojej w grobie",
         "For thou wilt not leave my soul in hell",
         "Najważniejszy przypadek, bo Nowy Testament go cytuje. Patrz niżej, Dzieje 2,27."),
        ("Ps. 30. BG 30,4 = KJV 30,3",
         "wywiodłeś z piekła duszę moję; … abym nie zstąpił do grobu",
         "thou hast brought up my soul from the grave: … that I should not go down to the pit",
         "Tu słowa są zamienione miejscami. Szeol: KJV grave, gdańska piekło. Dół (hebr. bor): KJV pit, gdańska grób."),
        ("Ps. 86,13",
         "wyrwał duszę moję z dołu głębokiego",
         "thou hast delivered my soul from the lowest hell",
         "KJV hell, gdańska dół. „Najgłębsze” i „głębokiego” sobie odpowiadają."),
        ("Ps. 116,3",
         "utrapienia grobu zjęły mię",
         "the pains of hell gat hold upon me",
         "KJV hell, gdańska grób. Śmierć w pierwszym członie zgadza się w obu."),
        ("Ps. 139,8",
         "jeźlibym sobie posłał w grobie, i tameś przytomny",
         "if I make my bed in hell, behold, thou art there",
         "KJV hell, gdańska grób."),
        ("Prz. 9,18",
         "są w głębokościach grobu",
         "her guests are in the depths of hell",
         "KJV hell, gdańska grób."),
        ("Iz. 14,11",
         "Strącona jest do piekła, pycha twoja",
         "Thy pomp is brought down to the grave",
         "W tym samym rozdziale, dwie linijki obok, wybór jest odwrotny. Iz. 14,9 i 14,15 mają w obu piekło i hell. Werset 11: KJV grave, gdańska piekło."),
        ("Iz. 57,9",
         "a poniżasz się aż do grobu",
         "and didst debase thyself even unto hell",
         "KJV hell, gdańska grób."),
        ("Ez. 31,16",
         "gdym go wepchnął do grobu z tymi, co w dół zstępują",
         "when I cast him down to hell with them that descend into the pit",
         "Szeol: hell wobec grób. Dół i pit się zgadzają."),
        ("Ez. 31,17",
         "I ci z nim zstąpili do grobu",
         "They also went down into hell with him",
         "KJV hell, gdańska grób."),
        ("Ez. 32,21",
         "z pośrodku grobu",
         "out of the midst of hell",
         "KJV hell, gdańska grób."),
        ("Ez. 32,27",
         "co zstąpili do grobu z wojennym orężem swoim",
         "which are gone down to hell with their weapons of war",
         "Oprócz grobu wobec hell inaczej idzie czasownik. Hebrajskie szakab znaczy „położyć się”. KJV ma shall not lie. Gdańska ma „nie polegli”, czyli nie padli w boju. To wykładnia wojskowa tego samego czasownika."),
        ("Am. 9,2",
         "Choćby się zakopali w ziemię, i stamtądby ich ręka moja wzięła",
         "Though they dig into hell, thence shall mine hand take them",
         "Tu gdańska nie mówi ani piekło, ani grób. Mówi „w ziemię”. KJV zostawia hell. Szeol znika w ogólnym „zakopać się w ziemię”."),
        ("Jon. BG 2,3 = KJV 2,2",
         "z głębokości grobu wołałem",
         "out of the belly of hell cried I",
         "Numer jest przesunięty, bo zdanie o rybie otwiera w BG rozdział 2. Słowo: KJV hell, gdańska grób. „Belly”, wnętrze, gdańska oddaje przez „głębokość”."),
    ]
    for ref, bg, kj, note in items:
        pdf.h3(ref)
        pdf.p("BG: " + bg)
        pdf.p("KJV: " + kj)
        pdf.p(note)

    pdf.h2("5.1. Ten sam cytat w Dziejach Apostolskich już się zgadza")
    pdf.pair(
        "Dz. 2,27. Cytat z Psalmu 16,10.",
        "Albowiem nie zostawisz duszy mojej w piekle, a nie dasz świętemu twojemu oglądać skażenia.",
        "Because thou wilt not leave my soul in hell, neither wilt thou suffer thine Holy One to see corruption.",
    )
    pdf.p(
        "W Psalmie 16 gdańska ma grób, a KJV hell. W Dziejach 2,27 i 2,31 oba mają piekło i hell. "
        "Greka Dziejów cytuje Septuagintę i mówi hades, nie szeol. Gdańska przy hadesie w tym "
        "cytacie wybiera piekło, tak jak KJV. Stary Testament i jego cytat w Nowym nie są więc "
        "w gdańskiej oddane tym samym polskim słowem. KJV jest tu konsekwentny: hell i w psalmie, i w Dziejach."
    )
    pdf.pair(
        "1 Kor. 15,55",
        "Gdzież jest, o śmierci! bodziec twój? Gdzież jest, piekło! zwycięstwo twoje?",
        "O death, where is thy sting? O grave, where is thy victory?",
    )
    pdf.p(
        "Textus Receptus ma tu ᾅδη, hades. Tekst krytyczny ma θάνατε, śmierci, drugi raz. "
        "Oba przekłady zostają przy hadesie, nie przy drugim „śmierci”. Różnią się słowem: "
        "gdańska piekło, KJV grave. KJV w innych miejscach hades oddaje przez hell "
        "(Mat. 16,18, Łuk. 16,23, Obj. 20,13). Tu, w cytacie z Ozeasza 13,14, wybiera grave, "
        "bo w Ozeaszu sam ma grave. Gdańska w Ozeaszu 13,14 też ma grób, a w 1 Kor. 15,55 "
        "mimo to mówi piekło. Cytat i jego źródło znowu dostają u niej dwa różne słowa."
    )
    pdf.p(
        "Pozostałe miejsca hadesu w Nowym Testamencie (Mat. 11,23; 16,18; Łuk. 10,15; 16,23; "
        "Dz. 2,27.31; Obj. 1,18; 6,8; 20,13.14) mają w obu piekło i hell. 2 Piotra 2,4, "
        "tartar, też jest w obu piekłem. Gehenna jest piekłem w Mat. 5,22.29.30; 10,28; 18,9; "
        "23,33; Mar. 9,43.45.47; Łuk. 12,5 i Jak. 3,6. Zostaje jeden werset, w którym gdańska "
        "gehenny nie nazywa piekłem."
    )
    pdf.pair(
        "Mat. 23,15",
        "iż obchodzicie morze i ziemię, abyście uczynili jednego nowego Żyda; a gdy się stanie, czynicie go synem zatracenia, dwakroć więcej niżeliście sami.",
        "for ye compass sea and land to make one proselyte, and when he is made, ye make him twofold more the child of hell than yourselves.",
    )
    pdf.p(
        "Dwie różnice w jednym zdaniu. Greckie προσήλυτον KJV zostawia jako proselyte. "
        "Gdańska wykłada je jako „nowy Żyd”. Greckie υἱὸν γεέννης, syn gehenny, KJV oddaje "
        "tak jak w pozostałych miejscach: child of hell. Gdańska mówi „syn zatracenia”. "
        "Tego zwrotu używa tam, gdzie greka ma syna zguby: Jan 17,12 i 2 Tes. 2,3, "
        "a KJV son of perdition. W Mateusza 23,15 greka ma syna gehenny, nie syna zguby. "
        "Obraz piekła w tym jednym wersecie ginie, a zostaje zatracenie."
    )


def names(pdf: Doc):
    pdf.h1("6. Imię Boże tam, gdzie KJV je przepisuje")
    pdf.p(
        "Na co dzień różnicy nie ma. Tetragram JHWH gdańska oddaje przez „Pan”, a KJV przez LORD. "
        "To umówiony odpowiednik, nie inna treść. Inaczej jest w kilku miejscach, w których KJV "
        "łamie własny zwyczaj i pisze JEHOVAH albo zlepek Jehovah-jireh, Jehovah-nissi, Jehovah-shalom. "
        "Gdańska te zlepki tłumaczy. Wyjątkiem zgodnym jest 2 Moj. 6,3: oba wydania mają tu imię "
        "Jehowa / JEHOVAH i nigdzie indziej gdańska tego imienia już nie stawia."
    )
    pdf.pair(
        "1 Moj. 22,14",
        "I nazwał Abraham imię miejsca onego: Pan obmyśli; ztądże po dziś dzień mówią: Na górze Pańskiej będzie obmyślono.",
        "And Abraham called the name of that place Jehovah-jireh: as it is said to this day, In the mount of the LORD it shall be seen.",
    )
    pdf.p(
        "Nazwa: gdańska tłumaczy („Pan obmyśli”), KJV przepisuje Jehovah-jireh. "
        "Przysłowie pod spodem rozchodzi się drugi raz. Hebrajski czasownik w stronie biernej "
        "znaczy „będzie zobaczone”. KJV tak ma: it shall be seen. Gdańska powtarza sens z wersetu 8, "
        "„obmyślić, opatrzyć”, i pisze „będzie obmyślono”. Werset 8 jest w obu o opatrzeniu baranka "
        "i różnicy sensu tam nie ma."
    )
    pdf.pair(
        "2 Moj. 17,15",
        "I zbudował Mojżesz ołtarz, a nazwał imię jego: Pan chorągiew moja.",
        "And Moses built an altar, and called the name of it Jehovah-nissi.",
    )
    pdf.pair(
        "Sędz. 6,24",
        "Przetoż zbudował tam Giedeon ołtarz Panu, i nazwał go: Pan pokoju.",
        "Then Gideon built an altar there unto the LORD, and called it Jehovah-shalom.",
    )
    pdf.pair(
        "Iz. 12,2",
        "albowiem Pan, Bóg mój, jest mocą moją, i pieśnią moją, i zbawieniem mojem.",
        "for the LORD JEHOVAH is my strength and my song; he also is become my salvation.",
    )
    pdf.p(
        "Hebrajski ma tu dwa imiona obok siebie, Jah i tetragram. KJV pisze LORD JEHOVAH. "
        "Gdańska ściąga to do „Pan, Bóg mój” i drugiego imienia już nie widać."
    )
    pdf.pair(
        "Iz. 26,4",
        "Miejcie nadzieję w Panu aż na wieki; boć w Panu, w Panu jest skała wieczna.",
        "Trust ye in the LORD for ever: for in the LORD JEHOVAH is everlasting strength.",
    )
    pdf.p(
        "To samo podwójne imię. Gdańska powtarza „w Panu, w Panu”, żeby zostało słychać dwa słowa. "
        "KJV pisze LORD JEHOVAH. „Skała wieczna” i everlasting strength to już wykładnia tego samego "
        "hebrajskiego obrazu skały; tu są blisko."
    )
    pdf.pair(
        "Ps. BG 83,19 = KJV 83,18",
        "A tak niech poznają, żeś ty, którego imię jest Pan, tyś sam Najwyższym nad wszystką ziemią.",
        "That men may know that thou, whose name alone is JEHOVAH, art the most high over all the earth.",
    )
    pdf.p(
        "KJV w tym jednym psalmie pisze JEHOVAH zamiast LORD. Gdańska zostaje przy „Pan”, "
        "tak jak w całej reszcie Psałterza. „Alone”, „sam”, jest w obu."
    )


def church(pdf: Doc, books):
    pdf.h1("7. Kościół, zbór i świątynia")
    pdf.p(
        "Po polsku XVII i XIX wieku „kościół” znaczył budowlę świętą, nie tylko wspólnotę chrześcijańską. "
        "Gdańska kładzie to słowo na hebrajską i grecką świątynię, tam gdzie KJV ma temple albo shrine. "
        "Na zgromadzenie, greckie ekklesia, KJV konsekwentnie mówi church. Gdańska mówi najczęściej zbór, "
        "a w części listów i w Mateusza 16,18 mówi kościół. Czytelnik, który przykłada dzisiejsze "
        "„kościół” do angielskiego church, zobaczy różnicę także tam, gdzie gdańska mówi o murach świątyni."
    )
    pdf.pair(
        "Jan 2,15",
        "A uczyniwszy bicz z powrozków, wszystkie wygnał z kościoła, i owce i woły.",
        "And when he had made a scourge of small cords, he drove them all out of the temple.",
    )
    pdf.pair(
        "1 Kor. 3,16",
        "Azaż nie wiecie, iż kościołem Bożym jesteście, a Duch Boży mieszka w was?",
        "Know ye not that ye are the temple of God, and that the Spirit of God dwelleth in you?",
    )
    pdf.pair(
        "Dz. 19,24",
        "który robił kościoły srebrne Dyjany",
        "which made silver shrines for Diana",
    )
    pdf.p(
        "Greka Jana 2,15 i Dziejów 19 to hieron albo naos, świątynia albo kapliczka, nie ekklesia. "
        "1 Kor. 3,16 też jest naos: jesteście świątynią, nie „jesteście Kościołem” w sensie instytucji. "
        "KJV trzyma temple i shrine. Gdańska ma jedno słowo, kościół, na budowlę i na część wspólnoty. "
        "To ten sam mechanizm co angielskie church, które też znaczy i zbór, i budynek, z tą różnicą, "
        "że KJV na budynek jerozolimski słowa church nie używa."
    )
    pdf.pair(
        "Mat. 16,18. Tu kościół i church stoją naprzeciw siebie i oba znaczą ekklesia.",
        "A Jać też powiadam, żeś ty jest Piotr; a na tej opoce zbuduję kościół mój, a bramy piekielne nie przemogą go.",
        "And I say also unto thee, That thou art Peter, and upon this rock I will build my church; and the gates of hell shall not prevail against it.",
    )
    pdf.pair(
        "Dz. 8,1. Tu na to samo greckie słowo gdańska mówi już zbór.",
        "I wszczęło się onegoż czasu wielkie prześladowanie przeciwko zborowi, który był w Jeruzalemie.",
        "And at that time there was a great persecution against the church which was at Jerusalem.",
    )
    pdf.p(
        "„Bramy piekielne” i the gates of hell to hades w obu, więc tego wersetu nie ma wśród różnic szeolu. "
        "Różnica leksykalna jest gdzie indziej: zbór wobec church w narracji Dziejów i w wielu listach, "
        "kościół wobec temple tam, gdzie chodzi o budowlę."
    )
    pdf.p(
        "Miejsca Nowego Testamentu, w których gdańska mówi „kościół” o świątyni albo o naos, "
        "a KJV mówi temple, shrine albo o budowli nieba: Mat. 21,12.23; 23,35; 24,1; Mar. 11,11.15; 13,1.3; "
        "Łuk. 1,9; 2,27.37; 11,51; 18,10; 19,45; 22,4; Jan 2,15; 7,14; 8,2.59; 10,22; "
        "Dz. 3,1–3.8; 5,21; 7,48; 17,24; 19,24.35; 21,26–30; 25,8; 1 Kor. 3,16; 6,19; 2 Kor. 6,16; "
        "Obj. 11,2; 14,15.17; 15,6.8; 16,1.17; 21,22."
    )
    pdf.p(
        "Miejsca, w których gdańska mówi „kościół” o ekklesia, zgodnie z KJV church co do sensu, "
        "choć obok, w innych wersetach, ma zbór: Mat. 16,18; Ef. 1,22; 5,23.27; Fil. 3,6; "
        "Kol. 1,18; 1 Tym. 3,15."
    )

    # indeks zboru w NT
    nt = False
    refs = []
    for b in books:
        if b["abbr"] == "mt":
            nt = True
        if not nt:
            continue
        for ch, lines in sorted(b["bg"].items()):
            for i, ln in enumerate(lines, 1):
                if re.search(r"\bzb[oó]r", ln, re.I):
                    refs.append(f"{b['pl']} {ch},{i}")
    pdf.p(
        "Wersetów ze słowem „zbór” w Nowym Testamencie, naprzeciw KJV church albo assembly, "
        f"jest {len(refs)}. Pełny indeks: " + "; ".join(refs) + "."
    )


def pascha(pdf: Doc, books):
    pdf.h1("8. Wielkanoc i passover")
    lines_out = []
    counts = {"wielkanoc": 0, "przejście": 0, "baranek": 0, "inne": 0}
    for b in books:
        for ci, ch in enumerate(b["kjv"], 1):
            bgch = b["bg"].get(ci, [])
            for vi, ln in enumerate(ch, 1):
                if re.search(r"passover", ln, re.I):
                    bg = bgch[vi - 1] if vi <= len(bgch) else ""
                    if re.search(r"wielkanoc|wielkonoc|wielkiej nocy|wielk[aą] noc", bg, re.I):
                        mark = "wielkanoc"
                    elif re.search(r"przejś", bg, re.I):
                        mark = "przejście"
                    elif re.search(r"baran", bg, re.I):
                        mark = "baranek"
                    else:
                        mark = "inne"
                    counts[mark] += 1
                    lines_out.append(f"{b['pl']} {ci},{vi} ({mark})")
    if counts["inne"]:
        raise SystemExit(f"nieopisane oddanie passover: {counts}")
    pdf.p(
        "Hebrajskie pesach i greckie pascha to jedna uroczystość. KJV mówi na nią passover, "
        "słowo Tyndale’a, zbudowane od „przejść obok”. Słowo Easter zostawia tylko raz, w Dziejach 12,4, "
        "bo taką nazwę święta miała starsza angielszczyzna. Gdańska nie ma jednego odpowiednika. "
        f"W {counts['przejście']} wersetach stoi „przejście” albo „święto przejścia”. To tłumaczy pesach "
        "i jest bliskie passover. "
        f"W {counts['wielkanoc']} wersetach stoi wielkanoc albo baranek wielkanocny, polska nazwa tego święta. "
        "Dla dzisiejszego czytelnika brzmi jak święto chrześcijańskie położone na święto żydowskie. "
        "W 1632 roku była po prostu nazwą paschy. "
        f"W {counts['baranek']} wersetach Ewangelii, tam gdzie KJV mówi o przygotowaniu passover, "
        "gdańska mówi już tylko o baranku."
    )
    pdf.pair(
        "Dz. 12,4. Tu KJV nie mówi passover. Oba wydania używają nazwy wielkanocnej.",
        "chcąc go po Wielkiej nocy wywieść ludowi.",
        "intending after Easter to bring him forth to the people.",
    )
    pdf.p(
        "W tym jednym wersecie różnicy nie ma. Jest wspólny ślad starej nazwy święta. "
        "Indeks wszystkich wersetów KJV ze słowem passover, z tym, co w tym samym numerze "
        "stoi w wydaniu 1879:"
    )
    pdf.p("; ".join(lines_out) + ".")
    pdf.p(
        "W 2 Kron. 35,1 gdańska kładzie oba swoje słowa obok siebie: „święto przejścia” i „baranek wielkanocny”. "
        "KJV w tym wersecie ma samo passover."
    )


def charity(pdf: Doc):
    pdf.h1("9. Miłość, charity i jeden werset z łaską")
    pdf.p(
        "Greckie agape KJV w Ewangelii Jana oddaje przez love, a w wielu miejscach listów przez charity. "
        "Charity w 1611 roku znaczyło miłość, z łacińskiego caritas, nie jałmużnę. Gdańska w tych "
        "miejscach ma miłość. Dla czytelnika z 1611 i z 1879 roku sens był ten sam. Dla czytelnika "
        "dzisiejszego charity brzmi węziej. Dlatego te pary nie są różnicą treści, ale łatwo je za nią wziąć."
    )
    pdf.p(
        "Wersety, w których KJV ma charity, a gdańska miłość: 1 Kor. 8,1; 13,1–4.8.13; 14,1; 16,14; "
        "Kol. 3,14; 1 Tes. 3,6; 2 Tes. 1,3; 1 Tym. 1,5; 2,15; 4,12; 2 Tym. 2,22; 3,10; Tyt. 2,2; "
        "1 Piotr. 4,8; 5,14; 3 Jan 6; Obj. 2,19. W 1 Piotr. 4,8 słowo miłość stoi w tym samym "
        "wersecie co wezwanie do trzeźwości, które KJV trzyma jeszcze w 4,7. Patrz podział wersetów."
    )
    pdf.p("Dwa miejsca wychodzą z tej pary i są już różnicą sensu.")
    pdf.pair(
        "2 Piotr. 1,7",
        "A do pobożności braterską miłość, a do miłości braterskiej łaskę.",
        "And to godliness brotherly kindness; and to brotherly kindness charity.",
    )
    pdf.p(
        "Grecki łańcuch kończy się na filadelfii, miłości braterskiej, i na agape. "
        "KJV: brotherly kindness, potem charity. Gdańska miłość braterską kładzie na filadelfię, "
        "a agape oddaje przez łaskę. Łaska w tej polszczyźnie to przychylność, życzliwość, nie miłość. "
        "Szczyt łańcucha cnót jest więc inny: u KJV miłość, u gdańskiej łaska. "
        "W 1 Kor. 13 ta sama agape jest u niej miłością. Ten werset jest wyjątkiem wewnątrz samej gdańskiej."
    )
    pdf.pair(
        "Judy 12",
        "Cić są na świętych ucztach waszych zmazami, którzy z wami godując bez wstydu, sami się pasą.",
        "These are spots in your feasts of charity, when they feast with you, feeding themselves without fear.",
    )
    pdf.p(
        "Greckie agapais to uczty agapy, uczty miłości. KJV zostawia ten sens: feasts of charity. "
        "Gdańska mówi „święte uczty” i słowa miłość tu nie ma. Uczta zostaje, jej nazwa się zmienia: "
        "z uczty miłości na ucztę świętą."
    )

    pdf.h2("9.1. Pokutujcie i repent")
    pdf.p(
        "Mat. 3,2 i dalsze wezwania mają w gdańskiej „Pokutujcie”, a w KJV repent. "
        "Greckie metanoeite znaczy zmianę myślenia. Luter tłumaczył „Tut Buße”. "
        "Protestancka polszczyzna XVII wieku wzięła stąd pokutę jako nawrócenie, nie jako "
        "pokutę sakramentalną. W 1879 roku to słowo jeszcze tak stało. Dziś „pokuta” ściąga "
        "ku karze i ku spowiedzi. To przesunięcie języka polskiego, nie inny grecki tekst niż KJV."
    )


def psalm_titles(pdf: Doc):
    pdf.add_page()
    pdf.h1("10. Nagłówki psalmów: tłumaczyć czy przepisać")
    pdf.p(
        "KJV muzyczne i gatunkowe słowa nagłówka zwykle przepisuje: Maschil, Michtam, "
        "Aijeleth Shahar, Al-taschith, Jonath-elem-rechokim. Gdańska część z nich tłumaczy, "
        "a część też przepisuje (Neginot, Gittyt, Seminit, Sosannim, Syggajon). "
        "Tam, gdzie oba przepisują, zostaje tylko pisownia. Różnicą jest tłumaczenie wobec imienia."
    )
    pdf.pair(
        "Ps. 22, nagłówek. W BG jest wersetem 1.",
        "Przedniejszemu śpiewakowi na czas poranny psalm Dawidowy.",
        "To the chief Musician upon Aijeleth Shahar, A Psalm of David.",
    )
    pdf.p(
        "Ajelet ha-szachar to „łania zorzy”, najpewniej nazwa melodii. KJV zostawia Aijeleth Shahar. "
        "Gdańska bierze samą zorzę i pisze „na czas poranny”. Łani w polskim nagłówku nie ma."
    )
    pdf.pair(
        "Ps. 16,1",
        "Złota pieśń Dawidowa.",
        "Michtam of David. Nagłówek KJV stoi nad wersetem, nie w nim.",
    )
    pdf.p(
        "Michtam bywa łączone ze „złotem”. Gdańska tak to tłumaczy: złota pieśń. "
        "To samo w Psalmach 56–60, gdzie KJV zostawia Michtam, a gdańska ma „złoty” albo „złota”."
    )
    pdf.pair(
        "Ps. 45, nagłówek. W BG werset 1.",
        "Przedniejszemu śpiewakowi z synów Korego na Sosannim psalm nauczający, a pieśń weselna.",
        "To the chief Musician upon Shoshannim, Maschil, A Song of loves.",
    )
    pdf.p(
        "Dwa odstępstwa naraz. Maschil KJV przepisuje, gdańska tłumaczy jako „psalm nauczający” "
        "(w innych psalmach także „wyuczająca” albo, w Psalmie 42, „pieśń ćwicząca”). "
        "„Song of loves” to pieśń o miłościach. Gdańska robi z niej „pieśń weselną”. "
        "Wesele jest wnioskiem z treści psalmu, nie tłumaczeniem słowa jedidot."
    )
    pdf.pair(
        "Ps. 56, nagłówek.",
        "Przedniejszemu śpiewakowi o niemej gołębicy, na miejscach odległych, złoty psalm Dawidowy.",
        "To the chief Musician upon Jonath-elem-rechokim, Michtam of David.",
    )
    pdf.p(
        "Jonath-elem-rechokim znaczy „gołębica milcząca na dalekich miejscach”. "
        "Gdańska to tłumaczy. KJV zostawia jako nazwę melodii. „Złoty” znowu stoi za Michtam."
    )
    pdf.p(
        "„Nie zatracaj” w nagłówkach Psalmów 57, 58, 59 i 75 to tłumaczenie Al-taschith, "
        "„nie gub”. KJV zostawia Al-taschith. „Nauczający”, „wyuczający” i „ćwicząca” "
        "w Psalmach 32, 42, 44, 45, 52–55, 74, 78, 88, 89 i 142 stoją za Maschil, "
        "które KJV przepisuje."
    )


def agreements(pdf: Doc):
    pdf.h1("11. Miejsca, które wyglądają na różnicę, a nią nie są")
    pdf.p(
        "Kilka znanych osobliwości KJV jest w wydaniu 1879 tak samo. Podaję je, bo przy "
        "zestawieniu z KJV szuka się ich pierwsze, a ich brak na liście różnic byłby mylący."
    )
    pdf.bullet(
        "Obj. 22,19. Oba mają „księgę żywota”, book of life, nie „drzewo żywota”. "
        "Greckie rękopisy mają ξύλου, drzewa. Erazm, nie mając greki ostatnich wersetów, "
        "przetłumaczył Wulgatę z powrotem na grekę i napisał księgę. Textus Receptus to przejął, "
        "a za nim i KJV, i gdańska."
    )
    pdf.bullet(
        "1 Jana 5,7–8. Oba mają świadków w niebie: Ojca, Słowo i Ducha. To Comma Johanneum, "
        "dopisek łaciński, który przez Textus Receptus wszedł do obu przekładów."
    )
    pdf.bullet(
        "Ps. 22. BG 22,17 = KJV 22,16: „przebodli ręce moje i nogi moje”, they pierced my hands and my feet. "
        "Tekst masorecki w brzmieniu „jak lew” jest w obu odrzucony na rzecz czytania „przebodli”."
    )
    pdf.bullet(
        "Iz. 7,14. Oba mają pannę i virgin, za Septuagintą i tradycją chrześcijańską, nie samo „młodą kobietę”.")
    pdf.bullet(
        "Dan. 3,25. Oba mają „Syna Bożego”, the Son of God, nie „syna bogów”.")
    pdf.bullet(
        "Zach. 12,10. Oba mają „patrzyć będą na mię, którego przebodli”, they shall look upon me whom they have pierced.")
    pdf.bullet(
        "1 Tym. 3,16. Oba mają „Bóg objawiony jest w ciele”, God was manifest in the flesh.")
    pdf.bullet(
        "Dz. 8,37; Mat. 17,21; 18,11; Łuk. 17,36; Jan 5,4; Rzym. 8,1 z dodatkiem o chodzeniu według Ducha; "
        "Kol. 1,14 „przez krew jego”. Te dopiski Textus Receptus są w obu.")
    pdf.bullet(
        "Jednorożec. 4 Moj. 23,22 i dalsze miejsca re’em: gdańska „jednorożec”, KJV unicorn. "
        "To ten sam ślad Septuaginty i Wulgaty (monokeros, unicornis), nie różnica między tymi wydaniami.")
    pdf.bullet(
        "Biskup. Dz. 20,28, Fil. 1,1, 1 Tym. 3, 1 Piotr. 2,25: gdańska „biskup”, KJV bishop. "
        "Oba zostawiają kościelne słowo na episkopos, zamiast tłumaczyć je jako „nadzorca”.")
    pdf.bullet(
        "Dz. 12,4, jak wyżej: Wielka noc i Easter. Zgoda w tym jednym wersecie, różnica we wszystkich pozostałych miejscach paschy.")


def limit(pdf: Doc):
    pdf.h1("12. Granica tego zestawienia")
    pdf.p(
        "Sprawdzone zostało całe ustawienie ksiąg i każdy rozdział, w którym liczba wersetów "
        "się nie zgadza. Sprawdzona została pełna lista szeolu, hadesu i gehenny. Sprawdzone "
        "zostały miejsca, w których KJV pisze JEHOVAH, firmament, charity, passover, Easter, "
        "scapegoat, Lucifer i nazwy nagłówków psalmów. Sprawdzony został aparat miejsc, "
        "w których Textus Receptus i tradycja luterska zwykle się rozchodzą albo schodzą: "
        "zakończenia Ewangelii, dopiski Dziejów, 1 Jana 5, Obj. 22, Łuk. 2,33 i 2,43, "
        "Iz. 7,14, Iz. 9, Ps. 22, Dan. 3,25, Zach. 12,10, 5 Moj. 32,8, 1 Sam. 6,19, "
        "2 Sam. 21,19."
    )
    pdf.p(
        "Nie sprawdzono każdego wersetu narracji pod kątem drobnego synonimu. W 1 Moj. 1, "
        "przeczytanym w całości, jedyną różnicą sensu jest rozpostarcie wobec firmamentu. "
        "Reszta rozdziału idzie krok w krok. Tak wygląda większa część obu Biblii. "
        "Rozdziały o tej samej liczbie wersetów nie były przeglądane werset po wersecie "
        "pod kątem wewnętrznego cięcia. Jedno takie cięcie wyszło przy czytaniu 1 Piotra 4 "
        "i jest w rozdziale o numeracji. Inne mogło zostać. "
        "Gdyby w jakimś wersecie historycznym zostało inne imię własne albo inne zdanie "
        "nieujęte w klasach powyżej, tej listy ono nie zamyka. Zamyka ją to, co zmienia "
        "obraz, wariant albo numer, i co dało się pokazać cytatem z obu plików."
    )
    pdf.p(
        "Tekst polski może jeszcze dostać korektę w repozytorium. Zestawienie dotyczy "
        f"commitu {COMMIT}. Data wydania cyfrowego tego commitu: {COMMIT_WHEN}."
    )


if __name__ == "__main__":
    main()
