import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import polars as pl 

from shiny import reactive
from shiny.express import render, ui, input
from shinywidgets import render_widget, render_plotly
from pathlib import Path

from functools import partial

from shiny.express import ui
from shiny.ui import page_navbar

ui.page_opts(
    title="Movies Analytics",  
    window_title="Movie Dashboard",
)

def format_numbers(x):
    if isinstance(x, (int, float)):
        return "{:,}".format(x)
    return x


with ui.layout_columns(col_widths=(6, 6)):
    with ui.card():
        ui.card_header("Top Box Office over the Years")
        ui.input_select(
            "top_box_select_year",
            "Year",
            {year : year for year in range(2023, 1930, -1)}
        )
        ui.input_select(
            "top_n",
            "Top",
            [i for i in range(5, 11)],
            selected=5
        )
        @render_plotly
        def top_box_office():
            df = data()
            selected_year = input.top_box_select_year()
            df_by_year = df[df["Year"] == int(selected_year)]

            print(selected_year)

            df_by_year = df_by_year.sort_values(by = "World Wide Sales (in $)", ascending=False).head(int(input.top_n()))

            fig = px.bar(df_by_year, x = "Title", y = "World Wide Sales (in $)")

            return fig
        
with ui.layout_columns(col_widths=(6, 6)):
    with ui.card():
        ui.card_header("Movies with Most budget")

        ui.input_select(
            "top_budget_select_year",
            "Year",
            {year : year for year in range(2020, 1930, -1)}
        )

        @render_plotly
        def top_budget_office():
            df = data()
            df = df.dropna(subset=["Budget (in $)"])
            selected_year = input.top_budget_select_year()
            df_budget_year = df[df["Year"] == int(selected_year)]

            df_budget_year = df_budget_year.sort_values(by = "Budget (in $)", ascending=False).head()

            fig = px.bar(df_budget_year, x = "Title", y = "Budget (in $)")

            print(df_budget_year)

            return fig



















@reactive.calc
def data():
    infile = Path(__file__).parent / "dataset" / "clean_movies.csv"

    df = pd.read_csv(infile)
    df.drop("Movie Info", axis = 1, inplace = True)

    return df


@render.data_frame
def sample_df():
    return data().head()
