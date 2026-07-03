import numpy as np
import pandas as pd
import streamlit as st

# Regional sales columns treated as a quasi-geographic dimension.
REGION_COLUMNS = {
    "NA Sales": "Ameryka Płn.",
    "PAL Sales": "Europa (PAL)",
    "Japan Sales": "Japonia",
    "Other Sales": "Pozostałe",
}


def _split_genres(value) -> list[str]:
    """Split a comma separated genre string into a list of genres."""
    if pd.isna(value):
        return []
    return [g.strip() for g in str(value).split(",") if g.strip()]


@st.cache_data(show_spinner="Przygotowanie danych...")
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned data frame ready for analysis."""
    df = df.copy()

    # Parse dates and derive the release year.
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    df["release_year"] = df["Release Date"].dt.year

    # Coerce numeric columns to avoid text values breaking aggregations.
    numeric_cols = [
        "Total Shipped", "Total Sales", "NA Sales", "PAL Sales",
        "Japan Sales", "Other Sales", "rating", "ratings_count", "metacritic",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Zero sales here means "not reported", not an actual zero. Flag such rows
    # and replace zeros with NaN so they do not deflate sales aggregates.
    df["has_sales_data"] = df["Total Sales"] > 0
    df["Total Sales"] = df["Total Sales"].replace(0, np.nan)
    df["sales_millions"] = df["Total Sales"] / 1_000_000

    # Normalise missing publisher and developer labels.
    df["Publisher"] = df["Publisher"].fillna("Unknown").replace("", "Unknown")
    df["Developer"] = df["Developer"].fillna("Unknown").replace("", "Unknown")

    # Genre list plus the primary (first) genre for simple grouping.
    df["genre_list"] = df["genres"].apply(_split_genres)
    df["primary_genre"] = df["genre_list"].apply(
        lambda lst: lst[0] if lst else "Nieznany"
    )

    # Sales per Metacritic point, computed only where both values exist.
    df["sales_per_metascore"] = np.where(
        (df["metacritic"].notna()) & (df["metacritic"] > 0),
        df["sales_millions"] / df["metacritic"],
        np.nan,
    )

    return df


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Return a long frame with one row per game-genre pair."""
    long_df = df.explode("genre_list").rename(columns={"genre_list": "genre"})
    return long_df[long_df["genre"].notna() & (long_df["genre"] != "")]


def all_genres(df: pd.DataFrame) -> list[str]:
    """Return the sorted list of unique genres in the dataset."""
    genres: set[str] = set()
    for lst in df["genre_list"]:
        genres.update(lst)
    return sorted(genres)
