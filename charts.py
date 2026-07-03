import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from cleaning import explode_genres, REGION_COLUMNS

# Shared console palette used across all charts.
CONSOLE_COLORS = {"PS3": "#2E6DB4", "PS4": "#00439C", "PS5": "#0072CE"}

TEMPLATE = "plotly_white"


def releases_over_time(df: pd.DataFrame) -> go.Figure:
    """Line chart: number of released games per year and console."""
    data = (
        df.dropna(subset=["release_year"])
        .groupby(["release_year", "Console"])
        .size()
        .reset_index(name="Liczba gier")
    )
    fig = px.line(
        data,
        x="release_year",
        y="Liczba gier",
        color="Console",
        markers=True,
        color_discrete_map=CONSOLE_COLORS,
        title="Liczba wydanych gier w czasie wg konsoli",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Rok wydania",
        yaxis_title="Liczba gier",
        legend_title="Konsola",
    )
    return fig


def top_genres_by_sales(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """Bar chart: genres with the highest total sales."""
    long_df = explode_genres(df)
    data = (
        long_df.groupby("genre")["sales_millions"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig = px.bar(
        data,
        x="sales_millions",
        y="genre",
        orientation="h",
        color="sales_millions",
        color_continuous_scale="Blues",
        title=f"Top {top_n} gatunków wg łącznej sprzedaży",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Łączna sprzedaż (mln sztuk)",
        yaxis_title="Gatunek",
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    return fig


def score_vs_sales(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: Metacritic score versus sales."""
    data = df.dropna(subset=["metacritic", "sales_millions"])
    fig = px.scatter(
        data,
        x="metacritic",
        y="sales_millions",
        color="Console",
        color_discrete_map=CONSOLE_COLORS,
        hover_name="Name",
        opacity=0.7,
        title="Ocena Metacritic a sprzedaż gry",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Ocena Metacritic (0-100)",
        yaxis_title="Sprzedaż (mln sztuk)",
        legend_title="Konsola",
    )
    return fig


def metacritic_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram: distribution of Metacritic scores per console."""
    data = df.dropna(subset=["metacritic"])
    fig = px.histogram(
        data,
        x="metacritic",
        color="Console",
        nbins=30,
        color_discrete_map=CONSOLE_COLORS,
        barmode="overlay",
        opacity=0.7,
        title="Rozkład ocen Metacritic",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Ocena Metacritic (0-100)",
        yaxis_title="Liczba gier",
        legend_title="Konsola",
    )
    return fig


def genre_year_heatmap(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Heatmap: release counts in a genre by year layout."""
    long_df = explode_genres(df).dropna(subset=["release_year"])

    # Limit to the most frequent genres to keep the heatmap readable.
    top = long_df["genre"].value_counts().head(top_n).index
    long_df = long_df[long_df["genre"].isin(top)]

    pivot = (
        long_df.groupby(["genre", "release_year"])
        .size()
        .reset_index(name="count")
        .pivot(index="genre", columns="release_year", values="count")
        .fillna(0)
    )
    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        title=f"Liczba wydań: {top_n} najczęstszych gatunków w czasie",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Rok wydania",
        yaxis_title="Gatunek",
        coloraxis_colorbar_title="Liczba gier",
    )
    return fig


def publishers_treemap(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Treemap: publisher share of total sales."""
    data = (
        df[df["Publisher"] != "Unknown"]
        .groupby("Publisher")["sales_millions"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig = px.treemap(
        data,
        path=["Publisher"],
        values="sales_millions",
        color="sales_millions",
        color_continuous_scale="Blues",
        title=f"Top {top_n} wydawców wg łącznej sprzedaży",
    )
    fig.update_layout(template=TEMPLATE, coloraxis_colorbar_title="Sprzedaż (mln)")
    fig.update_traces(
        texttemplate="%{label}<br>%{value:.1f} mln",
        hovertemplate="%{label}<br>Sprzedaż: %{value:.2f} mln<extra></extra>",
    )
    return fig


def regional_sales(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart: sales by geographic region and console."""
    records = []
    for col, label in REGION_COLUMNS.items():
        grouped = df.groupby("Console")[col].sum() / 1_000_000
        for console, value in grouped.items():
            records.append({"Region": label, "Console": console, "Sprzedaż": value})
    data = pd.DataFrame(records)

    fig = px.bar(
        data,
        x="Region",
        y="Sprzedaż",
        color="Console",
        barmode="group",
        color_discrete_map=CONSOLE_COLORS,
        title="Sprzedaż wg regionu i konsoli",
    )
    fig.update_layout(
        template=TEMPLATE,
        xaxis_title="Region",
        yaxis_title="Sprzedaż (mln sztuk)",
        legend_title="Konsola",
    )
    return fig
