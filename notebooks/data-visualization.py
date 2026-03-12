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
    import matplotlib.pyplot as plt


    # Statistics
    from statsmodels.tsa.seasonal import seasonal_decompose

    return alt, data, mo, pl, seasonal_decompose


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
def _(data):
    data.list_datasets()
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
def _(alt, df2):
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
        y=alt.Y('average(wind):Q', title='Wind'),
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
        y=alt.Y('average(wind):Q', title='Wind'),
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
        y=alt.Y('average(wind):Q', title='Wind'),
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
        x=alt.X('year(date):Q', axis=alt.Axis(values=[2012, 2013, 2014, 2015])),
        y=alt.Y('average(wind):Q'),
        # column=alt.Column('month'),
        # row=alt.Row('location'),
        color=alt.Color('location')
    ).properties(
        height=200,
        width=45
    )
    chart8 = alt.Chart(df2).mark_rule().encode(
        y=alt.Y('average(avg_wind):Q'),
        color=alt.Color('location')
    ).transform_aggregate(
        avg_wind='average(wind)',
        groupby=['location','year','month']
    ).properties(
        height=200,
        width=45
    )


    layered_chart = chart7 + chart8
    layered_chart.facet(
        column=alt.Column('month'),
        row=alt.Row('location')
    )
    return


@app.cell
def _(alt, df2):
    width_lag_chart = 150
    height_lag_chart = 150

    chart9 = alt.Chart(df2).transform_window(
        window=[alt.WindowFieldDef(op='lag', field='wind', param=1, **{'as': 'lag1_wind'})],
        # frame=[None, None]
    ).mark_point().encode(
        x=alt.X('wind:Q'),
        y=alt.Y('lag1_wind:Q'),
        row='location',
        color='location'
    ).properties(
        width=width_lag_chart,
        height=height_lag_chart
    )

    chart10 = alt.Chart(df2).transform_window(
        window=[alt.WindowFieldDef(op='lag', field='wind', param=2, **{'as': 'lag2_wind'})],
        # frame=[None, None]
    ).mark_point().encode(
        x=alt.X('wind:Q'),
        y=alt.Y('lag2_wind:Q'),
        row='location',
        color='location'
    ).properties(
        width=width_lag_chart,
        height=height_lag_chart
    )

    chart11 = alt.Chart(df2).transform_window(
        window=[alt.WindowFieldDef(op='lag', field='wind', param=7, **{'as': 'lag7_wind'})],
    ).mark_point().encode(
        x=alt.X('wind:Q'),
        y=alt.Y('lag7_wind:Q'),
        row=alt.Column('location'),
        color='location'
    ).properties(
        width=width_lag_chart,
        height=height_lag_chart
    )

    chart12 = alt.Chart(df2).transform_window(
        window=[alt.WindowFieldDef(op='lag', field='wind', param=14, **{'as': 'lag14_wind'})],
    ).mark_point().encode(
        x=alt.X('wind:Q'),
        y=alt.Y('lag14_wind:Q'),
        row=alt.Column('location'),
        color='location'
    ).properties(
        width=width_lag_chart,
        height=height_lag_chart
    )

    alt.hconcat(chart9, chart10, chart11, chart12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Moving Average (7 days)
    """)
    return


@app.cell
def _(df2, pl):
    df3 = df2.with_columns(
        mov_avg = pl.col('wind').rolling_mean(window_size=7, center=True)
    )
    return (df3,)


@app.cell
def _(alt, df3):


    chart14 = alt.Chart(df3).mark_line(color='lightgreen').encode(
        x=alt.X('date:T'),
        y=alt.Y('mov_avg:Q')
    ).properties(
        width=800,
        height=200
    )

    chart13 = alt.Chart(df3).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('wind:Q', title='Wind Velocity'),
        color='location:N',
        #row=alt.Row('location', header=None)
    ).properties(
        width=800,
        height=200
    )


    # chart13 + chart14
    layered_chart2 = chart13 + chart14

    layered_chart2.facet(
        row=alt.Row('location'),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Diferentiation
    """)
    return


@app.cell
def _(alt, df2):
    chart15 = alt.Chart(df2).transform_window(
        precip_lag1 = 'lag(wind)'
    ).transform_calculate(
        wind_diff1 = alt.datum.precipitation - alt.datum.precip_lag1
    ).mark_line().encode(
        x=alt.X('date'),
        y=alt.Y('wind_diff1:Q')
    )

    chart15
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Decomposition
    """)
    return


@app.cell
def _(df2, pl, seasonal_decompose):
    decompose = seasonal_decompose(df2.select(pl.col('wind').sort_by('date')), period=365)
    return (decompose,)


@app.cell
def _(decompose):
    decompose.plot()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
