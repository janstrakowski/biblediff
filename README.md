# Biblia gdańska 1879 a King James Version

Zestawienie różnic między wydaniem Biblii gdańskiej z 1879 roku a tekstem King James Version w brzmieniu z 1769 roku. PDF nie jest częścią repozytorium. Nazywa się `BG1879-a-KJV.pdf`.

Pierwsze wydanie to tag `v1`: obecny generator i obecne teksty. Przy wydaniu GitHub Actions buduje ten PDF i dokłada go do wydania.

Porównanie dotyczy folderu `1879` w repozytorium [UczenJezusa/biblia-druk-tekst](https://github.com/UczenJezusa/biblia-druk-tekst), commit `e5b1d3962179321a7bc9e502e634a2354c49a0a5`. Wydania z 1632 i z 2023 roku nie wchodzą do zestawienia. Rok 1879 jest unowocześnioną pisownią przekładu z 1632 roku, nie nowym tłumaczeniem.

Różnicą jest tu inny numer wersetu, inne słowo zmieniające obraz, inny wariant tekstu albo inne oddanie nazwy własnej. Zwykłe odpowiedniki dwóch języków, takie jak Mojżesz i Moses, na liście nie stoją.

## Źródła

Teksty są submodułami, przypiętymi do commitów, na których powstało to zestawienie.

| Ścieżka | Repozytorium | Commit | Co jest czytane |
| --- | --- | --- | --- |
| `zrodla/biblia-druk-tekst` | [UczenJezusa/biblia-druk-tekst](https://github.com/UczenJezusa/biblia-druk-tekst) | `e5b1d3962179321a7bc9e502e634a2354c49a0a5` | folder `1879` |
| `zrodla/bible` | [thiagobodruk/bible](https://github.com/thiagobodruk/bible) | `df0860fe0921b5b899d1b554041900ab072cd4c4` | `json/en_kjv.json` |

Drugie repozytorium jest duże, około 500 MB, bo trzyma wiele przekładów. Z niego używany jest jeden plik.

## Wydania

Tag postaci `v1`, `v2`, `v3` uruchamia akcję [PDF wydania](.github/workflows/pdf-wydania.yml). To samo dzieje się, gdy na GitHubie powstaje opublikowane wydanie z takiego tagu.

Akcja bierze kod z tego tagu i teksty z commitów, które tag przypina w submodułach. Z repozytorium `bible` ściąga tylko `json/en_kjv.json`. Gotowy plik dokłada jako `BG1879-a-KJV.pdf`. Jeśli wydania jeszcze nie ma, tworzy je. Jeśli jest, dopisuje tylko plik i nie rusza tytułu ani opisu.

Kolejne wydanie:

```bash
git tag v2
git push origin v2
```

Lokalne zbudowanie PDF, bez wydania, jest opisane niżej. Plik wynikowy dalej nie wchodzi do gita.

## Jak odtworzyć PDF

```bash
git clone --recurse-submodules git@github.com:janstrakowski/biblediff.git
cd biblediff
conda env create -f environment.yml
conda activate biblediff
python zestawienie/buduj_pdf.py
```

Jeśli katalog jest już sklonowany bez submodułów:

```bash
git submodule update --init
conda env update -f environment.yml --prune
conda activate biblediff
python zestawienie/buduj_pdf.py
```

`environment.yml` stawia osobne środowisko Condy: Python, `fpdf2` i czcionki DejaVu z pakietu `open-fonts`. Nic nie instaluje się globalnie. Przy kolejnym uruchomieniu wystarczy `conda activate biblediff`.

Wynik zapisuje się jako `BG1879-a-KJV.pdf` w katalogu głównym. Tego pliku nie commituje się. Ścieżki tekstów można nadpisać zmiennymi `BG1879` i `KJV_JSON`, a katalog czcionek zmienną `FONT_DIR`.
