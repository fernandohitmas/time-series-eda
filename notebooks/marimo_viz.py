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
    # Upload .csv data file
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    dropdown = mo.ui.file(
        filetypes=['.csv'],
        multiple=False,
        kind='area'
    )
    dropdown
    return (dropdown,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading uploaded file
    """)
    return


@app.cell
def _(dropdown, pl):
    if dropdown.value:
        df_file = pl.read_csv(dropdown.contents())
        df_file
    return


@app.cell(hide_code=True)
def _(data, mo):
    datasets_dropdown = mo.ui.dropdown(options=data.list_datasets(), label="Choose the dataset")
    datasets_dropdown
    return (datasets_dropdown,)


@app.cell
def _(data, datasets_dropdown, pl):
    dataset_name = datasets_dropdown.selected_key
    pl.from_dataframe(getattr(data, dataset_name)())
    return


@app.cell
def _(data, pl):
    df = pl.from_dataframe(data.weather()) 
    return (df,)


@app.cell
def _(df):
    df.write_csv(file='teste.csv')
    return


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
