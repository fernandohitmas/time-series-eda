import marimo

__generated_with = "0.23.9"
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

    import pandas as pd

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
def _():
    # uploaded_file = mo.ui.file(
    #     filetypes=['.csv'],
    #     multiple=False,
    #     kind='area'
    # )
    # uploaded_file
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading uploaded file
    """)
    return


@app.cell(hide_code=True)
def _():
    # if uploaded_file.value:
    #     df_file = pl.read_csv(uploaded_file.contents())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Selecting a dataset from Altair's database
    """)
    return


@app.cell(hide_code=True)
def _(data, mo):
    datasets_dropdown = mo.ui.dropdown(
        options=data.list_datasets(),
        label="###Choose one dataset",
        full_width=True,
        value="weather"
    )
    datasets_dropdown
    return (datasets_dropdown,)


@app.cell
def _(data, datasets_dropdown, pl):
    dataset_name = datasets_dropdown.selected_key
    df = pl.from_dataframe(getattr(data, dataset_name)())
    return (df,)


@app.cell(hide_code=True)
def _(df, mo):
    text_cols = "<br>".join(df.columns)
    mo.md(f'''
    # Dataset columns:
    {text_cols}

    ''')
    return


@app.cell
def _(df, mo):
    date_col_drop = mo.ui.dropdown(
        label="##Select the date column",
        options=df.columns, 
        full_width=True
    )
    date_col_drop
    return (date_col_drop,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## New columns derived from Date

    - year: extract year from selected date column
    - month: extract month from selected date column
    - weekyear: concatenates the ISO week and year from selected date column
    - weekday: extract which day of the week from selected date
    - isoweek: extract ISO wekk from selected date columns
    """)
    return


@app.cell(hide_code=True)
def _(date_col_drop, df, pl):
    df2 = df.with_columns(
        pl.col(date_col_drop.value).dt.year().alias("year"),
        pl.col(date_col_drop.value).dt.month().alias("month"),
        pl.concat_str(
            pl.col(date_col_drop.value).dt.year(),
            pl.col(date_col_drop.value).dt.strftime("%V"),
        ).str.to_integer().alias("weekyear"),
        pl.col(date_col_drop.value).dt.weekday().alias("weekday"),
        pl.col(date_col_drop.value).dt.week().alias("isoweek"),
    )
    return (df2,)


@app.cell
def _(df2, pl):
    df2.select(pl.nth(range(-5,0,1))).head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Visual Exploration
    """)
    return


@app.cell(hide_code=True)
def _(date_col_drop, df, mo):
    not_date_cols = df.columns
    not_date_cols.remove(date_col_drop.selected_key)

    metri_col_drop = mo.ui.dropdown(
        label="##Select a metric",
        options=not_date_cols, 
        full_width=True
    )
    metri_col_drop
    return (metri_col_drop,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complete time series interval
    """)
    return


@app.cell(hide_code=True)
def _(alt, date_col_drop, df2, metri_col_drop):
    brush = alt.selection_interval(encodings=['x'])

    year_rule = (
        alt.Chart(df2)
        .mark_rule(color="gray",strokeDash=[8,4], strokeWidth=1)
        .encode(
            x=alt.X(f"year({date_col_drop.selected_key})", axis=None).scale(domain=brush)
        )
    )

    line_chart = (
        alt.Chart(df2)
        .mark_line()
        .encode(
            x=alt.X(f"{date_col_drop.selected_key}:T", title="Date").scale(domain=brush),
            y=alt.Y(f"mean({metri_col_drop.selected_key}):Q", title="Avg. Wind Velocity"),
            color=alt.Color("location:N").legend(orient='top'),
        )
        .properties(height=300, width=1000)
    )

    selector = (
        alt.Chart(df2)
        .mark_line(color='black')
        .encode(
            x=alt.X(f"{date_col_drop.selected_key}", title=None),
            y=alt.Y(f"mean({metri_col_drop.selected_key}):Q", title=None)
        )
        .properties(height=50, width=1000)
        .add_params(brush)
    )

    composed_chart =  (line_chart + year_rule).resolve_axis(x="independent") 
    composed_chart & selector
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Seasonality charts
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


if __name__ == "__main__":
    app.run()
