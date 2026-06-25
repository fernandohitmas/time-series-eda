import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    from polars import selectors as cs
    import numpy as np
    import altair as alt
    from datetime import timedelta, datetime

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Relatório básico de Série Temporal

    O objetivo deste notebook é a análise de características básicas de séries temporais e assim entender a possibilidade de se utilizar métodos de predição. As etapas que são destrinchadas ao longo do notebook são:

    - Estatísticas básicas da série escolhida
    - Exploração visual da série com os seguintes gráficos:
     - Visualização total do período disponível
     - Gráfico de **sazonalidade**
     - Gráfico de **tedência**
     - Gráfico de **lag**
     - Gráfico de **média móvel**
     - Gráfico de **diferenciação**
     - Gráfico de **decomposição**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Como funciona este relatório?

    Através do input dos dados da série que se tem interesse de analisar este notebook irá trazer automaticamente informações relevantes para para avaliar a hipótese de estacionariedade a série estudada.
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
