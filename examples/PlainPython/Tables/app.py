from trame.layouts import SinglePage
from trame.html import vuetify, vega
from itertools import cycle
import json

import altair as alt
import pandas as pd
import numpy as np
import trame as tr


# --------------------------------------------------------------------------------
# Making dataframe
# --------------------------------------------------------------------------------
np.random.seed(4)
DATA_FRAME = None


def fetch_data(samples=15):
    global DATA_FRAME
    deltas = cycle(
        [
            pd.Timedelta(weeks=-2),
            pd.Timedelta(days=-1),
            pd.Timedelta(hours=-1),
            pd.Timedelta(0),
            pd.Timedelta(minutes=5),
            pd.Timedelta(seconds=10),
            pd.Timedelta(microseconds=50),
            pd.Timedelta(microseconds=10),
        ]
    )
    dummy_data = {
        "date_time_naive": pd.date_range("2021-01-01", periods=samples),
        "apple": np.random.randint(0, 100, samples) / 3.0,
        "banana": np.random.randint(0, 100, samples) / 5.0,
        "chocolate": np.random.randint(0, 100, samples),
        "group": np.random.choice(["A", "B"], size=samples),
        "season": np.random.choice(
            ["Spring", "Summer", "Fall", "Winter"], size=samples
        ),
        "date_only": pd.date_range("2020-01-01", periods=samples).date,
        "timedelta": [next(deltas) for i in range(samples)],
        "date_tz_aware": pd.date_range(
            "2022-01-01", periods=samples, tz="Asia/Katmandu"
        ),
    }
    DATA_FRAME = pd.DataFrame(dummy_data)
    return DATA_FRAME


fetch_data()

# --------------------------------------------------------------------------------
# Preparing table
# --------------------------------------------------------------------------------
header_options = {"apple": {"sortable": False}}
headers, rows = vuetify.dataframe_to_grid(DATA_FRAME, header_options)

table = {
    "headers": ("headers", headers),
    "items": ("rows", rows),
    "v_model": ("selection", None),
    "search": ("query", ""),
    "classes": "elevation-1 ma-4",
    "multi_sort": True,
    "dense": True,
    "show_select": True,
    "single_select": True,
}

# --------------------------------------------------------------------------------
# Describing chart
# --------------------------------------------------------------------------------


@tr.change("selection")
def selection_change(selection=[], **kwargs):
    from pprint import pprint

    pprint(kwargs)
    global DATA_FRAME
    selected_df = pd.DataFrame(selection)

    # Chart
    chart_data = DATA_FRAME.loc[
        :, ["date_time_naive", "apple", "banana", "chocolate"]
    ].assign(source="total")

    if not selected_df.empty:
        selected_data = selected_df.loc[
            :, ["date_time_naive", "apple", "banana", "chocolate"]
        ].assign(source="selection")
        chart_data = pd.concat([chart_data, selected_data])

    chart_data = pd.melt(
        chart_data,
        id_vars=["date_time_naive", "source"],
        var_name="item",
        value_name="quantity",
    )
    chart = (
        alt.Chart(data=chart_data)
        .mark_bar()
        .encode(
            x=alt.X("item:O"),
            y=alt.Y("sum(quantity):Q", stack=False),
            color=alt.Color("source:N", scale=alt.Scale(domain=["total", "selection"])),
        )
        .properties(
            width="container",
            height=175,
        )
    )

    chart_component.update(chart)


# --------------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------------

layout = SinglePage("Vuetify table example", on_ready=selection_change)
layout.title.set_text("Vuetify table example")
with layout.toolbar:
    vuetify.VSpacer()
    vuetify.VTextField(
        v_model=("query",),
        placeholder="Search",
        dense=True,
        hide_details=True,
    )

with layout.content:
    vuetify.VDataTable(**table)
    chart_component = vega.VegaEmbed(name="myChart", classes="ma-2")

if __name__ == "__main__":
    layout.start()
