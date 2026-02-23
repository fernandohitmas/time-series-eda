import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import altair as alt
    from altair.datasets import data
    import polars as pl

    return alt, data, mo, pl


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Importing Weather Data
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


@app.cell
def _(df2):
    df2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Visual Exploration - Split by city
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Precipitation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Total interval visualization
    """)
    return


@app.cell
def _(alt, df2):
    chart1 = alt.Chart(df2).mark_line().encode(
        x=alt.X('date', title='Date'),
        y=alt.Y('precipitation:Q', title='Precipitation (mm)'),
        color='location:N',
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=800
    )


    chart2 = alt.Chart(df2).mark_tick().encode(
        # x=alt.X('precipitation', title='Count'),
        y=alt.Y('precipitation',
                scale=alt.Scale(domainMin=0),
                axis=alt.Axis(orient='right', labels=False, ticks=False, title=None)),
        color=alt.Color('location:N', legend=alt.Legend(orient="top", title='Location')),
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=20,
    )

    chart1 | chart2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sazonality visualization
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Year over year comparison - monthly
    """)
    return


@app.cell
def _(alt, df2):
    chart3 = alt.Chart(df2).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill="white")
    ).encode(
        x=alt.X('month(date):T', title='Date'),
        y=alt.Y('sum(precipitation):Q', title='Precipitation (mm)'),
        color=alt.Color('year:N'),
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=800
    )

    chart3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Year over year comparison - weekly
    """)
    return


@app.cell
def _(alt, df2):
    chart5 = alt.Chart(df2).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill="white")
    ).encode(
        x=alt.X('isoweek', title='Week'),
        y=alt.Y('sum(precipitation):Q', title='Precipitation (mm)'),
        color=alt.Color('year:N'),
        row=alt.Row('location', header=None)
    ).properties(
        height=200,
        width=800
    )

    chart5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Year over year comparison - day of the week
    """)
    return


@app.cell
def _(alt, df2):
    chart6 = alt.Chart(df2).mark_line().encode(
        x=alt.X('weekday:Q', title='Week', axis=alt.Axis(values=[1,2,3,4,5,6,7])),
        y=alt.Y('sum(precipitation):Q', title='Precipitation (mm)'),
        color=alt.Color('isoweek:Q'),
        row=alt.Row('location', header=None),
        column=alt.Column('year')
    ).properties(
        height=200,
        width=400
    )

    chart6

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Basic trend visualization
    """)
    return


@app.cell
def _(alt, df2):
    chart7 = alt.Chart(df2).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill="white")
    ).encode(
        x=alt.X('year:Q', axis=alt.Axis(values=[2012, 2013, 2014, 2015])),
        y=alt.Y('sum(precipitation):Q'),
        column=alt.Column('month:N'),
        row=alt.Row('location:N'),
        color=alt.Color('location')
    ).properties(
        height=150,
        width=40
    )

    chart8 = alt.Chart(df2).mark_rule().encode(
        y=alt.Y('sum(precipitation):Q'),
        #x=alt.X('year:N'),
        column=alt.Column('month:N'),
        row=alt.Row('location:N')
    )

    chart7 #+ chart8
    return


@app.cell
def _(alt, df2):
    chart9 = alt.Chart(df2).mark_rule().encode(
        y=alt.Y('average(precipitation):Q'),
        #x=alt.X('year:N'),
        column=alt.Column('month:N'),
        row=alt.Row('location:N')
    )

    chart9
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
