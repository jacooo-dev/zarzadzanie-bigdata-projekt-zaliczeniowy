import pandas as pd
import streamlit as st

import charts
from cleaning import all_genres, clean, explode_genres
from data_loader import load_raw

st.set_page_config(
    page_title="PlayStation Market Explorer",
    page_icon="🎮",
    layout="wide",
)

# Both steps are cached, so changing filters does not reload or reclean data.
raw = load_raw()
df = clean(raw)

st.sidebar.title("Filtry")
st.sidebar.caption(
    "Ustawienia poniżej wpływają na wszystkie wskaźniki i wykresy w aplikacji."
)

consoles = sorted(df["Console"].unique())
selected_consoles = st.sidebar.multiselect(
    "Konsola", options=consoles, default=consoles,
)

year_series = df["release_year"].dropna()
min_year, max_year = int(year_series.min()), int(year_series.max())
selected_years = st.sidebar.slider(
    "Rok wydania",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

genres = all_genres(df)
selected_genres = st.sidebar.multiselect(
    "Gatunki (puste oznacza wszystkie)", options=genres, default=[],
)

selected_meta = st.sidebar.slider(
    "Ocena Metacritic",
    min_value=0,
    max_value=100,
    value=(0, 100),
)

only_with_sales = st.sidebar.checkbox(
    "Tylko gry z danymi o sprzedaży", value=False,
)


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Return the frame narrowed to the sidebar selection."""
    mask = data["Console"].isin(selected_consoles)

    # Apply the year filter only once the range is actually narrowed, so the
    # default view keeps games without a release date.
    if selected_years != (min_year, max_year):
        year_mask = data["release_year"].between(*selected_years)
        mask &= year_mask.fillna(False)

    # At the default 0-100 range let unrated games through as well.
    if selected_meta != (0, 100):
        meta_mask = data["metacritic"].between(*selected_meta)
        mask &= meta_mask.fillna(False)

    if only_with_sales:
        mask &= data["has_sales_data"]

    filtered = data[mask]

    # Genre filter runs last because it operates on the genre list.
    if selected_genres:
        chosen = set(selected_genres)
        keep = filtered["genre_list"].apply(lambda lst: bool(chosen & set(lst)))
        filtered = filtered[keep]

    return filtered


fdf = apply_filters(df)

st.title("PlayStation Market Explorer")
st.markdown(
    "Analiza rynku gier na konsole PlayStation trzech generacji (PS3, PS4, "
    "PS5). Aplikacja prowadzi przez kolejne pytania: jak zmieniała się liczba "
    "premier, które gatunki dominują, jak ocena krytyków przekłada się na "
    "sprzedaż oraz którzy wydawcy odpowiadają za największy wolumen. Dane "
    "pochodzą z serwisu VGChartz oraz RAWG API (zbiór Kaggle, stan na "
    "październik 2025)."
)

st.info(
    "Uwaga metodologiczna: dane o sprzedaży pochodzą z VGChartz i obejmują "
    "praktycznie wyłącznie tytuły PS3 oraz PS4. Gry PS5 są obecne w katalogu "
    "wraz z ocenami i metadanymi, natomiast nie mają jeszcze przypisanej "
    "sprzedaży w źródle. Analizy wolumenu sprzedaży należy więc czytać jako "
    "obraz generacji PS3 i PS4, a analizy ocen i liczby premier jako pełne "
    "dla wszystkich trzech konsol.",
    icon="ℹ️",
)

# Guard against an overly narrow filter selection.
if fdf.empty:
    st.warning(
        "Dla wybranych filtrów brak gier. Rozszerz zakres w panelu bocznym."
    )
    st.stop()

kpi_games = len(fdf)
kpi_sales = fdf["sales_millions"].sum()
kpi_meta = fdf["metacritic"].median()
top_genre_series = explode_genres(fdf)["genre"].value_counts()
kpi_top_genre = top_genre_series.index[0] if not top_genre_series.empty else "brak"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Liczba gier", f"{kpi_games:,}".replace(",", " "))
c2.metric("Łączna sprzedaż", f"{kpi_sales:,.1f} mln".replace(",", " "))
c3.metric(
    "Mediana Metacritic",
    f"{kpi_meta:.0f}" if pd.notna(kpi_meta) else "brak danych",
)
c4.metric("Dominujący gatunek", kpi_top_genre)

st.divider()

st.subheader("1. Jak zmieniała się liczba premier")
st.plotly_chart(charts.releases_over_time(fdf), width="stretch")
st.caption(
    "Interpretacja: każda generacja ma własny cykl życia. Widać moment "
    "przejmowania rynku przez nowszą konsolę oraz stopniowe wygaszanie "
    "premier na starszym sprzęcie. Spadek liczby tytułów PS5 w ostatnich "
    "latach wynika częściowo z niepełnego pokrycia najnowszych premier w "
    "zbiorze, a nie wyłącznie z realnego trendu."
)

st.divider()

st.subheader("2. Które gatunki sprzedają się najlepiej")
col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(charts.top_genres_by_sales(fdf), width="stretch")
with col_b:
    st.plotly_chart(charts.genre_year_heatmap(fdf), width="stretch")
st.caption(
    "Interpretacja: wolumen sprzedaży koncentruje się w kilku gatunkach o "
    "masowym zasięgu, podczas gdy heatmapa pokazuje, że liczba premier "
    "rozkłada się szerzej. Duża liczba tytułów w danym gatunku nie oznacza "
    "więc automatycznie największej sprzedaży."
)

st.divider()

st.subheader("3. Czy wysokie oceny idą w parze ze sprzedażą")
col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(charts.score_vs_sales(fdf), width="stretch")
with col_d:
    st.plotly_chart(charts.metacritic_distribution(fdf), width="stretch")
st.caption(
    "Interpretacja: zależność między oceną a sprzedażą jest dodatnia, lecz "
    "daleka od liniowej. Najwyższą sprzedaż osiągają pojedyncze tytuły o "
    "bardzo dobrych ocenach, jednak wiele wysoko ocenionych gier sprzedaje "
    "się umiarkowanie. Rozkład ocen koncentruje się wokół wartości 70-80."
)

st.divider()

st.subheader("4. Wydawcy i rozkład geograficzny sprzedaży")
col_e, col_f = st.columns(2)
with col_e:
    st.plotly_chart(charts.publishers_treemap(fdf), width="stretch")
with col_f:
    st.plotly_chart(charts.regional_sales(fdf), width="stretch")
st.caption(
    "Interpretacja: rynek jest silnie skoncentrowany po stronie kilku dużych "
    "wydawców. W ujęciu regionalnym dominują Ameryka Północna oraz Europa, "
    "natomiast rynek japoński pozostaje wyraźnie mniejszy, co odpowiada "
    "strukturze globalnej sprzedaży konsol."
)

st.divider()

with st.expander("Podgląd przefiltrowanych danych"):
    preview_cols = [
        "Name", "Console", "Publisher", "release_year",
        "primary_genre", "metacritic", "sales_millions",
    ]
    st.dataframe(
        fdf[preview_cols].sort_values("sales_millions", ascending=False),
        width="stretch",
        hide_index=True,
    )

st.caption(
    "Projekt zaliczeniowy, przedmiot Zarządzanie Big Data. Źródło danych: "
    "Kaggle (VGChartz, RAWG API)."
)
