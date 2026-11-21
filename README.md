# Biblia gdańska 1879 a King James Version

Zestawienie różnic między wydaniem Biblii gdańskiej z 1879 roku a tekstem King James Version w brzmieniu z 1769 roku. PDF nie jest częścią repozytorium. Powstaje lokalnie po uruchomieniu generatora i nazywa się `BG1879-a-KJV.pdf`.

Porównanie dotyczy folderu `1879` w repozytorium [UczenJezusa/biblia-druk-tekst](https://github.com/UczenJezusa/biblia-druk-tekst), commit `e5b1d3962179321a7bc9e502e634a2354c49a0a5`. Wydania z 1632 i z 2023 roku nie wchodzą do zestawienia. Rok 1879 jest unowocześnioną pisownią przekładu z 1632 roku, nie nowym tłumaczeniem.

Różnicą jest tu inny numer wersetu, inne słowo zmieniające obraz, inny wariant tekstu albo inne oddanie nazwy własnej. Zwykłe odpowiedniki dwóch języków, takie jak Mojżesz i Moses, na liście nie stoją.

## Jak odtworzyć PDF

Potrzebny jest Python 3 i pakiet `fpdf2`. Skrypt czyta dwa lokalne źródła. Domyślne ścieżki można nadpisać zmiennymi `BG1879` (folder `1879` z klonu `biblia-druk-tekst`) i `KJV_JSON` (plik JSON z tekstem KJV z 1769 roku).

```bash
pip install fpdf2
python3 zestawienie/buduj_pdf.py
```

Wynik zapisuje się jako `BG1879-a-KJV.pdf` w katalogu głównym. Tego pliku nie commituje się.
