import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Como funciona este relatório?

    Este notebook se utiliza da funcionalidade de **automação** do Marimo para realizar cálculos e construir gráficos que tem como intuito a avaliação da hipótese de **estacionariedade** dos dados inputados e, dessa forma, entender a possibilidade de se utilizar métodos preditivos básicos como o ARIMA. Além da automação já mencionada, este notebook propõe ao usuário que o **utilize de forma interativa** para enriquecer ainda mais a investigação sobre a série de interesse, através do uso do Vega Altair, ferramenta de visualização de dados.
    """)
    return


@app.cell(hide_code=True)
def _():
    import polars as pl
    from polars import selectors as cs
    import numpy as np
    from datetime import timedelta, datetime

    import marimo as mo
    import altair as alt

    return alt, mo, pl


@app.cell(hide_code=True)
def _(alt):
    alt.data_transformers.enable("vegafusion")
    _ = alt.renderers.set_embed_options(actions=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Análise de estacionariedade de série temporal

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
     - Testes de **hipótese**
     - Gráficos de Autocorrelação e Autocorrelação Parcial
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Carregamento dos dados

    Os dados podem ter mais de uma coluna, porém, é importante notar que a análise será feita para uma métrica específica de cada vez.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    file_ui = mo.ui.file(
                        filetypes=['.csv'],
                        multiple=False,
                        kind='area'
                    )
    file_ui
    return (file_ui,)


@app.cell(hide_code=True)
def _(file_ui, mo, pl):
    if file_ui.value:
        df = pl.read_csv(file_ui.contents())
        # mo.style.text(mo.md("Your text here"), size="xl")
        output = mo.md(
                    """ 
        <span style="font-size: 24px;">Carregamento completo!</span>
                    """
                ).center()
    else:
        output = mo.md(
                    """ 
        <span style="font-size: 24px;">Nenhum arquivo carregado!</span>
                    """
                ).center()
    
    output
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.1 Colunas de data e períodos
    """)
    return


@app.cell(hide_code=True)
def _(df, mo):
    date_col_drop = mo.ui.dropdown(
        label="##Selecione a coluna de data",
        options=df.columns, 
        full_width=True
    )
    # amplificar(date_col_drop)
    date_col_drop

    return (date_col_drop,)


@app.cell
def _(date_col_drop, df, pl):
    df_new = df.with_columns(
        pl.col(date_col_drop.value).str.to_datetime()
    ).clone()
    return (df_new,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Novas colunas derivadas da coluna data

    - **year**: extrai o ano;
    - **month**: extrai o mês;
    - **weekyear**: concatena a semana ISO e o ano;
    - **weekday**: extrai o dia da semana;
    - **isoweek**: extrai o semana ISO;
    """)
    return


@app.cell
def _(date_col_drop, df_new, pl):
    df2 = df_new.with_columns(
        pl.col(date_col_drop.value).dt.year().alias("year"),
        pl.col(date_col_drop.value).dt.month().alias("month"),
        pl.concat_str(
            pl.col(date_col_drop.value).dt.year(),
            pl.col(date_col_drop.value).dt.strftime("%V"),
        ).str.to_integer().alias("weekyear"),
        pl.col(date_col_drop.value).dt.weekday().alias("weekday"),
        pl.col(date_col_drop.value).dt.week().alias("isoweek"),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Explorando os dados
    """)
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(df, pl):
    df.select(pl.col('date', 'location', 'temp_min')).write_csv('teste.csv')
    return


@app.cell
def _():
    import os

    return (os,)


@app.cell
def _(os):
    os.getcwd()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
