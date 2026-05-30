import marimo

__generated_with = "0.19.11"
app = marimo.App(width="columns")


@app.cell(column=0, hide_code=True)
def _(mo):
    mo.md(r"""
    # Marimo interactive visualization
    """)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import altair as alt

    import polars as pl
    import matplotlib.pyplot as plt

    # Altair datasets 
    from altair.datasets import data

    return alt, data, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Enabling vegafusion for bigger datasets
    """)
    return


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    alt.renderers.set_embed_options(actions=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Choosing Dataset
    """)
    return


@app.cell
def _(mo):
    dropdown = mo.ui.dropdown(options=["Apples", "Oranges", "Pears"], label="choose fruit")
    dropdown_dict = mo.ui.dropdown(options={"Apples":1, "Oranges":2, "Pears":3},
                            value="Apples", # initial value
                            label="choose fruit with dict options")
    return dropdown, dropdown_dict


@app.cell(hide_code=True)
def _(dropdown, dropdown_dict, mo):
    mo.vstack([mo.hstack([dropdown, mo.md(f"Has value: {dropdown.value}")]),
    mo.hstack([dropdown_dict, mo.md(f"Has value: {dropdown_dict.value} and selected_key {dropdown_dict.selected_key}")]),
                ])
    return


@app.cell
def _(data, mo):
    datasets_dropdown = mo.ui.dropdown(options=data.list_datasets(), label="Choose the dataset")
    datasets_dropdown
    return


@app.cell
def _(data, pl):
    pl.from_dataframe(getattr(data, 'weather')())
    return


@app.cell
def _(data, pl):
    df = pl.from_dataframe(data.weather()) 
    return (df,)


@app.cell
def _(df):
    df.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## New time columns
    """)
    return


@app.cell
def _(df, pl):
    df2 = df.with_columns(
        pl.col("date").dt.year().alias("year"),
        pl.col("date").dt.month().alias("month"),
        pl.concat_str(
            pl.col("date").dt.year(),
            pl.col("date").dt.strftime("%V"),
        )
        .str.to_integer()
        .alias("weekyear"),
        pl.col("date").dt.weekday().alias("weekday"),
        pl.col("date").dt.week().alias("isoweek"),
    )
    return (df2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Visual Exploration - Split by city
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Wind velocity
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Total interval visualization
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell(column=1)
def _():
    return


@app.cell(hide_code=True)
def _(alt, df2, mo):
    chart1 = (
        alt.Chart(df2)
        .mark_line()
        .encode(
            x=alt.X("date", title="Date"),
            y=alt.Y("wind:Q", title="Wind Velocity (mm)"),
            color="location:N",
            row=alt.Row("location", header=None),
        )
        .properties(height=200, width=800)
    )


    chart2 = (
        alt.Chart(df2)
        .mark_tick()
        .encode(
            # x=alt.X('precipitation', title='Count'),
            y=alt.Y(
                "wind",
                scale=alt.Scale(domainMin=0),
                axis=alt.Axis(
                    orient="right", labels=False, ticks=False, title=None
                ),
            ),
            color=alt.Color(
                "location:N", legend=alt.Legend(orient="top", title="Location")
            ),
            row=alt.Row("location", header=None),
        )
        .properties(
            height=200,
            width=20,
        )
    )

    grouped_chart = chart1 | chart2

    mo.ui.altair_chart(grouped_chart)
    return


if __name__ == "__main__":
    app.run()
