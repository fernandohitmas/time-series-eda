import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import polars as pl
    import os

    return alt, mo, pl


@app.cell
def _(alt):
    alt.data_transformers.enable("vegafusion")
    return


@app.cell
def _():
    data_path = '../../data/raw/Online Retail.xlsx'
    return (data_path,)


@app.cell
def _(data_path, pl):
    df = pl.read_excel(source=data_path)
    return (df,)


@app.cell
def _(df):
    df.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data description

    ## Variables

    - **InvoiceNoID**:	Categorical	a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation.
    - **StockCodeID**:	Categorical	a 5-digit integral number uniquely assigned to each distinct product.
    - **Description**:	Categorical	product name.
    - **Quantity**:	Integer	the quantities of each product (item) per transaction.
    - **InvoiceDate**:	Date	the day and time when each transaction was generated.
    - **UnitPrice**:	Continuous	product price per unit	sterling.
    - **CustomerID**:	Categorical	a 5-digit integral number uniquely assigned to each customer.
    - **Country**:	Categorical	the name of the country where each customer resides.
    """)
    return


@app.cell
def _(df):
    df.describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Investigating InvoiceNo
    """)
    return


@app.cell
def _(df, pl):
    df.group_by('InvoiceNo').agg(pl.len()).sort(by='len', descending=True).head(n=5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There is InvoiceNo that has a lot products related to a possible transaction.
    """)
    return


@app.cell
def _(df, pl):
    df.filter(pl.col('InvoiceNo') == 573585)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Checking the invoiceNo that has the most number of transactions that is no NULL show that the customer ID is NULL so the next step is checking the count of null values for each column
    """)
    return


@app.cell
def _(df):
    df.null_count()
    return


@app.cell
def _(df):
    df_no_nulls = df.drop_nulls()
    return (df_no_nulls,)


@app.cell
def _(df_no_nulls):
    df_no_nulls.null_count()
    return


@app.cell
def _(df_no_nulls, pl):
    df_no_nulls.group_by('InvoiceNo').agg(pl.len()).sort(by='len', descending=True).head(n=5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plotting Number of items for each transaction descending
    """)
    return


@app.cell
def _(alt, df_no_nulls, pl):
    # Definig the chart object from altair
    chart = alt.Chart(data=df_no_nulls.group_by('InvoiceNo').agg(pl.len()).sort(by='len', descending=True).head(10))
    return (chart,)


@app.cell
def _(alt, chart):
    chart.mark_bar().encode(
        x = alt.X('InvoiceNo:N').sort('-y'),
        y = alt.Y('len:Q')
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
