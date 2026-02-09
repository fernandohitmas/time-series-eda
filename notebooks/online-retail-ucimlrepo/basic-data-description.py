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

    return alt, data, mo


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    return


@app.cell
def _(data):
    data.weather()
    return


if __name__ == "__main__":
    app.run()
