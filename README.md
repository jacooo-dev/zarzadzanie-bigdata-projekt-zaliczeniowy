# PlayStation Market Explorer

Aplikacja analityczna zbudowana w Streamlit, przygotowana jako projekt
zaliczeniowy z przedmiotu Zarządzanie Big Data (studia informatyczne II
stopnia). Aplikacja realizuje pełny przepływ pracy z danymi: pozyskanie,
czyszczenie, analizę eksploracyjną, wizualizację oraz komunikację wniosków.

Wdrożona aplikacja:
https://zarzadzanie-bigdata-projekt-zaliczeniowy-jakub-nowosad.streamlit.app/

## Cel i zakres

Celem projektu jest analiza rynku gier na konsole PlayStation trzech generacji
(PS3, PS4, PS5). Aplikacja odpowiada na cztery pytania badawcze:

1. Jak zmieniała się liczba premier w kolejnych latach i generacjach.
2. Które gatunki odpowiadają za największy wolumen sprzedaży.
3. Czy wysokie oceny krytyków przekładają się na sprzedaż.
4. Którzy wydawcy dominują rynek i jak rozkłada się sprzedaż geograficznie.

Interfejs prowadzi użytkownika przez te pytania w formie spójnej narracji,
a każdy blok wykresów opatrzony jest interpretacją wyników.

## Źródło danych

Dane pochodzą z serwisu Kaggle i zostały zebrane z dwóch źródeł: sprzedaż z
VGChartz oraz metadane (oceny, gatunki, daty) z RAWG API. Stan zbioru to
październik 2025.

- Zbiór: PlayStation Sales and Metadata (PS3, PS4, PS5)
- Adres: https://www.kaggle.com/datasets/gvidalguiresse/playstation-sales-and-metadata-ps3ps4ps5
- Liczba rekordów: 4963 gry (PS3: 1892, PS4: 1991, PS5: 1080)

Plik CSV należy umieścić w katalogu `data/` pod nazwą
`playstation_sales_and_metadata.csv`, ponieważ aplikacja wczytuje go dokładnie
z tej ścieżki.

### Ograniczenia danych

Dane o sprzedaży z VGChartz obejmują w praktyce wyłącznie tytuły PS3 oraz PS4.
Gry PS5 występują w katalogu wraz z ocenami i metadanymi, natomiast nie mają
jeszcze przypisanej sprzedaży w źródle. Z tego powodu analizy wolumenu
sprzedaży dotyczą przede wszystkim generacji PS3 i PS4, natomiast analizy
ocen i liczby premier są pełne dla wszystkich trzech konsol. Ograniczenie to
jest sygnalizowane bezpośrednio w aplikacji.

## Przetwarzanie danych

Krok czyszczenia (moduł `cleaning.py`) obejmuje:

- konwersję daty wydania na typ daty oraz wyprowadzenie roku wydania,
- wymuszenie typów liczbowych na kolumnach sprzedaży i ocen,
- świadomą obsługę sprzedaży zerowej, która w tym zbiorze oznacza brak danych,
  a nie faktyczną sprzedaż równą zeru (rekordy oznaczane są osobną flagą,
  a zera zamieniane na wartość pustą na potrzeby analiz sprzedażowych),
- ujednolicenie zapisu braków w kolumnach wydawcy i dewelopera,
- utworzenie kolumn pochodnych: sprzedaż w milionach sztuk, lista gatunków,
  gatunek główny oraz sprzedaż w przeliczeniu na punkt oceny Metacritic.

## Wizualizacje

Aplikacja zawiera siedem wykresów w sześciu różnych typach:

- liniowy: liczba premier w czasie wg konsoli,
- słupkowy poziomy: gatunki o najwyższej sprzedaży,
- heatmapa: liczba premier w układzie gatunek na rok,
- punktowy: ocena Metacritic względem sprzedaży,
- histogram: rozkład ocen Metacritic,
- treemapa: udział wydawców w sprzedaży,
- słupkowy grupowany: sprzedaż wg regionu geograficznego i konsoli.

## Filtry

Panel boczny udostępnia pięć widgetów filtrujących, które wpływają na wszystkie
wskaźniki i wykresy jednocześnie:

- wybór konsoli (multiselect),
- zakres lat wydania (slider),
- wybór gatunków (multiselect),
- zakres oceny Metacritic (slider),
- ograniczenie do gier z dostępnymi danymi o sprzedaży (checkbox).

## Struktura projektu

```
ProjektZaliczeniowy/
  app.py            orkiestrator, layout i obsługa filtrów
  data_loader.py    wczytanie pliku CSV z katalogu data/
  cleaning.py       czyszczenie i kolumny pochodne
  charts.py         funkcje budujące wykresy
  pyproject.toml    zależności i konfiguracja Poetry
  poetry.lock       zablokowane wersje zależności
  .python-version   docelowa wersja Pythona (3.12)
  .streamlit/       konfiguracja motywu
  data/             playstation_sales_and_metadata.csv (zbiór z Kaggle)
```

Kod jest modularny: `app.py` pełni rolę orkiestratora, a logika przetwarzania
i rysowania znajduje się w osobnych modułach. Operacje wczytania i czyszczenia
danych są cache'owane przez `@st.cache_data`, dzięki czemu zmiana filtrów nie
uruchamia ponownego przetwarzania całego zbioru.

## Wersja Pythona

Docelowa wersja to Python 3.12, zapisana w pliku `.python-version` na potrzeby
narzędzi lokalnych (pyenv, Poetry). Streamlit Community Cloud nie odczytuje tego
pliku, dlatego przy tworzeniu aplikacji w panelu chmury należy wybrać tę samą
wersję w ustawieniach zaawansowanych. Zakres akceptowanych wersji określa
`pyproject.toml` (`>=3.11,<3.15`).

## Uruchomienie lokalne

Zależnościami zarządza Poetry (plik `pyproject.toml` wraz z `poetry.lock`).

```bash
cd ProjektZaliczeniowy
poetry install
poetry run streamlit run app.py
```

Przed uruchomieniem należy pobrać zbiór z Kaggle i umieścić plik w katalogu
`data/` pod nazwą `playstation_sales_and_metadata.csv`.

## Wdrożenie

Aplikacja jest przystosowana do wdrożenia na Streamlit Community Cloud.
Wystarczy wskazać repozytorium oraz plik `app.py` jako punkt wejścia. Streamlit
Community Cloud wykrywa `poetry.lock` i instaluje zależności przez Poetry, więc
oba pliki (`pyproject.toml`, `poetry.lock`) muszą znaleźć się w repozytorium.
Zbiór ma niewielki rozmiar (poniżej 1 MB), dlatego plik CSV również należy
dołączyć do repozytorium, aby był dostępny w środowisku chmurowym.

Link do wdrożonej aplikacji:
https://zarzadzanie-bigdata-projekt-zaliczeniowy-jakub-nowosad.streamlit.app/
