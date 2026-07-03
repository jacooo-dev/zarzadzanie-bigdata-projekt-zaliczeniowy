from pathlib import Path
import glob

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"


def _find_main_file() -> Path:
    """Return the path to the main CSV file or raise a readable error."""
    matches = sorted(glob.glob(str(DATA_DIR / f"playstation_sales_and_metadata.csv")))
    if not matches:
        raise FileNotFoundError(
            f"Nie znaleziono pliku pasującego do wzorca 'playstation_sales_and_metadata.csv' "
            f"w katalogu {DATA_DIR}. Umieść zbiór z Kaggle w folderze data/."
        )
    return Path(matches[0])


@st.cache_data(show_spinner="Wczytywanie zbioru danych...")
def load_raw() -> pd.DataFrame:
    """Read the raw dataset into a data frame (cached by Streamlit)."""
    return pd.read_csv(_find_main_file())
