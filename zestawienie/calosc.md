# Zestawienie całości

Obecny PDF zamyka klasy miejsc. Nie jest przeglądem każdego wersetu. Ezechiela 40,30 nie ma na liście, bo rozdział ma w obu tekstach po 49 wersetów i nie wpada w żadne hasło, które generator przegląda. Werset jest w obu. Szerokość przysionków jest inna: gdańska ma pięćdziesiąt łokci, KJV pięć.

W Biblii gdańskiej jest 31 171 wersetów, w KJV 31 102. Rozdziałów o tej samej liczbie wersetów jest 1 094, a w nich 29 284 wersetów. Tych generator nie czyta werset po wersecie. Rozdziałów o różnej liczbie jest 95, w nich 1 887 wersetów polskich. Tam opisany jest szew numeracji, nie każdy fakt w zdaniu.

Dokładanie kolejnego hasła tego nie domyka. Każdy werset ma być zestawiony ze swoim odpowiednikiem angielskim, a potem oceniony tą samą regułą co teraz.

## Reguła

Na listę wchodzi inne zdanie, inny obraz, inne imię albo inna liczba. Zwykłe odpowiedniki dwóch języków zostają poza listą. „Mojżesz” i „Moses”, „Pan” i „LORD” to ten sam sens. To samo dotyczy par, które w 1611 i w 1879 roku znaczyły to samo, a dziś brzmią węziej, jak charity i miłość albo pokutujcie i repent. Te pary są opisane osobno w obecnym zestawieniu i filtra całości nie powinny zatykać.

## 1. Mapa wersetów

Porównanie treści zaczyna się od pary, nie od numeru. Przy równej liczbie wersetów rozdział startuje jako para jeden do jednego, a potem szuka się wewnętrznego cięcia. Takie cięcie jest w 1 Piotra 4,7–8: oba wydania mają 19 wersetów, a granica zdań i tak się rozjeżdża.

Przy różnej liczbie szew wyznacza się raz na rozdział, tak jak jest to zrobione ręcznie dla tych 95 rozdziałów.

Sam przesuw nagłówka nie załatwia Psalmów. W Psalmach 13, 16 i 66 nagłówek jest osobnym wersetem, a dwa wiersze pieśni są gdzie indziej złączone.

## 2. Filtr

Każdy zestawiony werset przechodzi przez filtr. Filtr zostawia ślad, że werset był widziany.

Pisownia z 1879 roku musi być wcześniej sprowadzona do jednej postaci. W 1 Mojżeszowej 5,4 stoi „ośm set lat”, nie „osiemset”. Bez tego filtr liczb kłamie. Na surowej pisowni, w samych rozdziałach o równej liczbie, rozjeżdża się 1 753 zestawy liczb, w większości fałszywie. Po normalizacji zostają prawdziwe rozjazdy. Ezechiela 40,30 jest wśród nich.

Same liczby nie domykają całości. Łukasza 2,14 nie ma w sobie żadnej liczby, a sens jest inny. Obok liczb filtr bierze:

- nawias i dopisek, którego w drugim tekście nie ma;
- imię tylko po jednej stronie;
- przeczenie albo człon zdania tylko po jednej stronie;
- pary, w których zdania nie wynikają z siebie nawzajem.

## 3. Najpierw PDF, potem odrzucenie

Przebieg jest w `zestawienie/filtr.py` i `zestawienie/zbierz.py`. Składa go `python zestawienie/buduj_pdf.py` jako ostatni rozdział jednego pliku, `BG1879-a-KJV.pdf`. Tego pliku nie ma w repozytorium. Powstaje przy tagu wydania.

Filtr, który przebieg domyka sam, to liczba (po sprowadzeniu pisowni z 1879 roku), nawias, przeczenie, imię zostawione tylko po jednej stronie (Azazel, Lucyfer, Jehowa) i kilka par obrazu, w których obie strony mają swój wyraz. Zwykłe „jeden” i „one” oraz „dziewięć set i trzydzieści” wobec „nine hundred and thirty” nie wchodzą. Otwarte porównanie wszystkich imion nie wchodzi, bo odmiana (Mojżesz i Moses) zasypuje listę.

Pary o podobnej długości, w których zdania nie wynikają z siebie, a nie łapie ich żaden z tych warunków, są w `zestawienie/kandydaci/sens-*.jsonl` i wchodzą do tego samego rozdziału. Człowiek odrzuca fałszywe trafienia dopiero z gotowego PDF-a.

Drugie wydanie nie czeka na werdykt. Rejestr odrzuceń powstaje przy czytaniu. Zostaje w nim albo różnica, albo „ten sam sens”. Kompletność jest w rejestrze: każdy werset ma werdykt. Ostatni rozdział mówi, że przejrzany został każdy werset pod tę regułę, a nie tylko szeol, firmament, passover i reszta zamkniętych list.
