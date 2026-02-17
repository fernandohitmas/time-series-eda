import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Imports

    - **marimo** for future UI and interactive elements
    - **altair** for the visual representations
     - **altair datasets** for easy access for example datasets without the need for local storage.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import altair as alt
    from altair.datasets import data
    import polars as pl
    import os

    return alt, data, mo, pl


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    return


@app.cell
def _(data):
    data.list_datasets()[:10]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Example dataset: **WEATHER**

    **Description**: daily measurements of precipitation, maximum temperature, minimum temperature, wind velocity and weather category from January 1st, 2012 to December 31st, 2015 for the cities of Seattle and New York.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting the data to dataframe
    """)
    return


@app.cell
def _(data, pl):
    df = pl.from_pandas(data.weather())
    return (df,)


@app.cell
def _(df):
    df.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Different cities in the dataset: Seattle and New York
    """)
    return


@app.cell
def _(df):
    df['location'].unique()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Data description per city
    """)
    return


@app.cell
def _(df, pl):
    df.group_by(
        pl.col('location').alias('city')
    ).agg(
        pl.len().alias('Number of records'),
        pl.min('precipitation').alias('min_prec'),
        pl.max('precipitation').alias('max_prec'),
        pl.col('date').min().dt.strftime('%d/%m/%Y').alias('min_date'),
        pl.col('date').max().dt.strftime('%d/%m/%Y').alias('max_date'),
        pl.min('temp_max').alias('min_temp_max'),
        pl.max('temp_max').alias('max_temp_max'),
        pl.min('temp_min').alias('min_temp_min'),
        pl.max('temp_min').alias('max_temp_min'),
        pl.min('wind').alias('min_wind_vel'),
        pl.max('wind').alias('max_wind_vel'),
        pl.col('weather').value_counts().sort().first().alias('least_common_weather'),
        pl.max('weather').alias('most_common_weather'),

    ).unpivot(
        index='city', variable_name='Metrics'
    ).pivot('city', index='Metrics')
    return


@app.cell
def _(df, pl):
    df.group_by(
        pl.col('location'),
        pl.col('weather')
    ).agg(
        pl.len()
    ).sort(by='len')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
