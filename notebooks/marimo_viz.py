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
    from datetime import datetime, timedelta

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


@app.cell
def _(mo):
    # 1. Defina a função de escala
    def amplificar(componente, escala=1.3):
        return mo.style(
            componente, 
            style={
                "transform": f"scale({escala})",
                "transform-origin": "left center",
                "margin-bottom": f"{20 * escala}px", # Evita que elementos se sobreponham verticalmente
                "display": "inline-block"
            }
        )

    return (amplificar,)


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
def _(amplificar, data, mo):
    datasets_dropdown = mo.ui.dropdown(
        options=data.list_datasets(),
        label="###Choose one dataset",
        full_width=True,
        value="weather"
    )
    amplificar(datasets_dropdown)
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


@app.cell(hide_code=True)
def _(amplificar, df, mo):
    date_col_drop = mo.ui.dropdown(
        label="##Select the date column",
        options=df.columns, 
        full_width=True
    )
    amplificar(date_col_drop)
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


@app.cell
def _(df2, mo):
    mo.ui.dataframe(df2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Visual Exploration
    """)
    return


@app.cell(hide_code=True)
def _(amplificar, date_col_drop, df, mo):
    not_date_cols = df.columns
    not_date_cols.remove(date_col_drop.selected_key)

    metri_col_drop = mo.ui.dropdown(
        label='''###Select a metric''',
        options=not_date_cols, 
    )

    amplificar(metri_col_drop)
    return (metri_col_drop,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exact date selector
    """)
    return


@app.cell(hide_code=True)
def _(date_col_drop, df2, metri_col_drop, mo):
    date_selector = mo.ui.date_range.from_series(df2[date_col_drop.selected_key],label="###Date Interval")
    # date_selector.center()

    mo.hstack([metri_col_drop, date_selector], gap=1, justify='start')
    return (date_selector,)


@app.cell(hide_code=True)
def _(alt, date_col_drop, date_selector, df2, metri_col_drop):
    date_range = (date_selector.value[0], date_selector.value[1])
    brush = alt.selection_interval(encodings=['x'], value={'x': date_range})

    legend_select = alt.selection_point(fields=['location'], bind='legend')

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
            tooltip=[date_col_drop.selected_key,metri_col_drop.selected_key, 'location'],
            color=alt.Color("location:N").legend(orient='left'),
            opacity=alt.when(legend_select).then(alt.value(1)).otherwise(alt.value(0.2)),
        )
        .properties(
            height=300, 
            width=900, 
            title=alt.Title(
                "Interactive Time Series",
                color='darkslateblue',
                fontSize=30
            )
        )
        .add_params(
            legend_select
        )
    )

    selector = (
        alt.Chart(df2)
        .mark_line(color='gray')
        .encode(
            x=alt.X(f"{date_col_drop.selected_key}", title=None),
            y=alt.Y(f"mean({metri_col_drop.selected_key}):Q", title=None)
        )
        .properties(
            height=50, 
            width=900, 
            title=alt.Title(
                "Selector", 
                fontSize=15, 
                color='black'
            ) 
        )
        .add_params(brush)
    )

    composed_chart =  (line_chart + year_rule).resolve_axis(x="independent") 
    final_chart = (composed_chart & selector)

    final_chart
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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
