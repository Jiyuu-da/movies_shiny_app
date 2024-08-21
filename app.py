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


ui.tags.style(
    """
    .donut_card{
        max-height: 360px;
    }
"""
)
ui.page_opts(
    title="Movies Analytics",  
    window_title="Movie Dashboard",
)

@reactive.calc
def data():
    infile = Path(__file__).parent / "dataset" / "clean_movies.csv"
    df = pl.read_csv(infile)
    df.drop("Movie Info")

    return df

@reactive.calc
def unique_distributors():
    df = data()
    unique_dist = df["Distributor"].drop_nulls().unique()
    return unique_dist



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

            df_by_year = df.filter(
                pl.col("Year") == int(selected_year)
            )

            df_by_year = df_by_year.sort(by = "World Wide Sales (in $)", descending=True).head(int(input.top_n()))

            fig = px.bar(df_by_year, x = "Title", y = "World Wide Sales (in $)")

            return fig
        

    with ui.card():
        with ui.layout_columns(col_widths=(6, 6, 12)):
            with ui.card(class_="donut_card"):

                ui.card_header("Top Distributors by year")
                @render_plotly
                def top_dist_by_year():
                    df = data()
                    selected_year = int(input.donut_top_dist_year())

                    dist_by_year = df.filter(
                        pl.col("Year") == selected_year
                    )

                    pie = dist_by_year.group_by(pl.col("Distributor"), maintain_order=True).agg(pl.col("World Wide Sales (in $)").sum()).sort(by="World Wide Sales (in $)", descending=True)[:10]

                    print(pie)
                    pie_df = pie.to_pandas()
                    fig = px.pie(pie_df,
                                  values = pie_df["World Wide Sales (in $)"], names=pie_df["Distributor"],
                                  hole=0.65
                                  )

                    fig.update_traces(
                    hoverinfo='label+percent'
                )
                    fig.update_layout(
                        showlegend=False,
                        autosize=True,
                        height = 200,
                    )
                    return fig
                

                ui.input_select(
                    "donut_top_dist_year",
                    "Year",
                    {year : year for year in range(2020, 1977, -1)}
                )


            with ui.card(class_ = "donut_card"):
                ui.card_header("Top Profitable Distributors by year")
                @render_plotly
                def top_proft_dist_by_year():
                    df = data()
                    df = df.drop_nulls(subset=["Budget (in $)"])
                    df = df.with_columns(
                        (pl.col("World Wide Sales (in $)") - pl.col("Budget (in $)")).alias("Profit (in $)")
                    )                
    
                    selected_year = int(input.donut_top_profit_dist_year())

                    dist_by_year = df.filter(
                        pl.col("Year") == selected_year
                    )

                    pie = dist_by_year.group_by(pl.col("Distributor"), maintain_order=True).agg(pl.col("Profit (in $)").sum()).sort(by="Profit (in $)", descending=True)[:10]

                    print(pie)

                    pie_df = pie.to_pandas()
                    fig = px.pie(pie_df,
                                values = pie_df["Profit (in $)"], names=pie_df["Distributor"],
                                hole=0.65
                                )

                    fig.update_traces(
                    hoverinfo='label+percent'
                )
                    fig.update_layout(
                        showlegend=False,
                        autosize=True,
                        height = 200,
                    )
                    return fig
                    

                ui.input_select(
                    "donut_top_profit_dist_year",
                    "Year",
                    {year : year for year in range(2020, 1977, -1)}
                )

            with ui.card(class_ = "donut_card"):
                ui.card_header("Percentage of total movies by Distributor")
                @render_plotly
                def top_providing_dist_by_year():
                    df = data()
    
                    selected_year = int(input.donut_top_providing_dist_year())

                    dist_by_year = df.filter(
                        pl.col("Year") == selected_year
                    )

                    pie = dist_by_year.group_by(pl.col("Distributor"), maintain_order=True).agg(pl.col("Title").count()).sort(by="Title", descending=True)[:10]

                    print(pie)

                    pie_df = pie.to_pandas()
                    fig = px.pie(pie_df,
                                values = pie_df["Title"], names=pie_df["Distributor"],
                                hole=0.65
                                )

                    fig.update_traces(
                    hoverinfo='label+percent'
                )
                    fig.update_layout(
                        autosize=True,
                        height = 200,
                    )
                    return fig
                    

                ui.input_select(
                    "donut_top_providing_dist_year",
                    "Year",
                    {year : year for year in range(2020, 1977, -1)}
                )    



        
with ui.layout_columns(col_widths=(6, 6)):
    with ui.card():
        ui.card_header("Movies with Most budget")

        ui.input_select(
            "top_budget_select_year",
            "Year",
            {year : year for year in range(2020, 1977, -1)}
        )

        @render_plotly
        def top_budget_office():
            df = data()
            df = df.drop_nulls(subset=["Budget (in $)"])
            selected_year = input.top_budget_select_year()

            df_budget_year = df.filter(
                pl.col("Year") == int(selected_year)
            )

            df_budget_year = df_budget_year.sort(by = "Budget (in $)", descending=True).head()

            fig = px.bar(df_budget_year, x = "Title", y = "Budget (in $)")

            return fig


















def format_numbers(x):
    if isinstance(x, (int, float)):
        return "{:,}".format(x)
    return x

def format_genre(x):
    x = x.strip("[]")
    x = x.replace("'", "")
    return x

@render.data_frame
def sample_df():
    infile = Path(__file__).parent / "dataset" / "clean_movies.csv"
    df2 = pd.read_csv(infile)
    df2.drop(columns=["Movie Info", "idx"], inplace=True)

    cols_with_comma = df2.columns.difference(["Year"])
    df2[cols_with_comma] = df2[cols_with_comma].map(format_numbers)


    df2["Genre"] = df2["Genre"].apply(format_genre)

    return df2.head()
