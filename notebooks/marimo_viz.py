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
    # Visual Exploration - Split by city
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    # chart1 = (
    #     alt.Chart(df2)
    #     .mark_line()
    #     .encode(
    #         x=alt.X("date", title="Date"),
    #         y=alt.Y("wind:Q", title="Wind Velocity (mm)"),
    #         color="location:N",
    #         row=alt.Row("location", header=None),
    #     )
    #     .properties(height=200, width=800)
    # )


    # chart2 = (
    #     alt.Chart(df2)
    #     .mark_tick()
    #     .encode(
    #         # x=alt.X('precipitation', title='Count'),
    #         y=alt.Y(
    #             "wind",
    #             scale=alt.Scale(domainMin=0),
    #             axis=alt.Axis(
    #                 orient="right", labels=False, ticks=False, title=None
    #             ),
    #         ),
    #         color=alt.Color(
    #             "location:N", legend=alt.Legend(orient="top", title="Location")
    #         ),
    #         row=alt.Row("location", header=None),
    #     )
    #     .properties(
    #         height=200,
    #         width=20,
    #     )
    # )

    # grouped_chart = chart1 | chart2

    # mo.ui.altair_chart(grouped_chart)
    return


@app.cell
def _():

    # import datetime as dt
    # source = data.sp500.url

    # date_range = (dt.date(2007, 6, 30), dt.date(2009, 6, 30))

    # brush = alt.selection_interval(encodings=['x'],
    #                                value={'x': date_range})

    # base = alt.Chart(source, width=600, height=200).mark_area().encode(
    #     x = 'date:T',
    #     y = 'price:Q'
    # )

    # upper = base.encode(
    #     alt.X('date:T').scale(domain=brush)
    # )

    # lower = base.properties(
    #     height=60
    # ).add_params(brush)

    # upper & lower
    return


@app.cell
def _(alt, df2):
    brush = alt.selection_interval(encodings=['x'])

    base = (
        alt.Chart(df2)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("mean(wind):Q", title=" Avg Wind Velocity (mm)"),
        )
        .properties(height=200, width=800)
    )

    chart = (
        base
        .encode(
            x=alt.X("date:T", title="Date").scale(domain=brush),
        
            color="location:N",
            # row=alt.Row("location", header=None),
        )
        .properties(height=200, width=900)
    )

    selector = (
        base
        .properties(height=50, width=900)
        .add_params(brush)
    )

    chart & selector
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
