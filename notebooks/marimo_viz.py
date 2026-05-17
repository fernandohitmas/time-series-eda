import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
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
    from altair.datasets import data
    import polars as pl
    import matplotlib.pyplot as plt


    # Statistics
    from statsmodels.tsa.seasonal import seasonal_decompose

    return alt, data, mo, pl


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    alt.renderers.set_embed_options(actions=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Importing Weather dataset
    """)
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
        pl.col('date').dt.year().alias('year'),
        pl.col('date').dt.month().alias('month'),
        pl.concat_str(
            pl.col('date').dt.year(),
            pl.col('date').dt.strftime('%V'),
        ).str.to_integer().alias('weekyear'),
        pl.col('date').dt.weekday().alias('weekday'),
        pl.col('date').dt.week().alias('isoweek'),
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
def _(alt, df2, mo):
    chart1 = alt.Chart(df2).mark_line().encode(
        x=alt.X('date', title='Date'),
        y=alt.Y('wind:Q', title='Wind Velocity (mm)'),
        color='location:N',
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=800
    )


    chart2 = alt.Chart(df2).mark_tick().encode(
        # x=alt.X('precipitation', title='Count'),
        y=alt.Y('wind',
                scale=alt.Scale(domainMin=0),
                axis=alt.Axis(orient='right', labels=False, ticks=False, title=None)),
        color=alt.Color('location:N', legend=alt.Legend(orient="top", title='Location')),
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=20,
    )

    grouped_chart = chart1 | chart2

    mo.ui.altair_chart(grouped_chart)
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


if __name__ == "__main__":
    app.run()
