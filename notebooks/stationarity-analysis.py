import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    from datetime import datetime, timedelta

    import marimo as mo
    import anywidget
    import polars as pl
    from polars import selectors as cs
    import altair as alt
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    from statsmodels.tsa.stattools import adfuller, kpss, acf
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.tsa.seasonal import seasonal_decompose, STL, MSTL
    from statsmodels.tsa.x13 import x13_arima_select_order, x13_arima_analysis

    from scipy.stats import boxcox

    return MSTL, acf, alt, cs, mo, np, pl, seasonal_decompose


@app.cell(hide_code=True)
def _(alt):
    # alt.data_transformers.enable("vegafusion")
    _ = alt.renderers.set_embed_options(actions=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 📊 Análise de Estacionariedade de Séries Temporais

    Este notebook guia você por uma análise completa de **estacionariedade** de uma série temporal,
    cobrindo desde a exploração visual dos dados até testes estatísticos formais (**ADF** e **KPSS**).
    O objetivo é fornecer um diagnóstico claro e orientar a escolha de métodos preditivos adequados.

    | # | Etapa | O que será feito |
    |---|---|---|
    | **1** | Carregamento dos dados | Upload do arquivo CSV e prévia |
    | **2** | Configuração da série | Seleção da métrica, data e frequência |
    | **3** | Visão Geral Descritiva | Estatísticas básicas da série configurada |
    | **4** | Exploração Visual | Sazonalidade, tendência, lag, média móvel, decomposição |
    | **5** | Testes de Estacionariedade | Testes ADF e KPSS com interpretação |
    | **6** | ACF e PACF | Autocorrelações para parâmetros ARIMA |
    | **7** | Conclusões | Síntese da análise e próximos passos |

    /// admonition | 💡 **Como usar**
    O notebook é **reativo** — carregue o arquivo na Seção 1, configure a série na Seção 2 e todas as seções seguintes se atualizam automaticamente.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 1. Carregamento dos Dados

    Faça o upload de um arquivo `.csv` contendo pelo menos uma **coluna de data** e uma
    **coluna numérica** (a métrica a ser analisada). O arquivo pode conter múltiplas métricas
    e colunas categóricas para agrupamento — a seleção será feita na Seção 2.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    file_ui = mo.ui.file(
        filetypes=[".csv"],
        multiple=False,
        kind="area",
        label="Arraste o arquivo CSV aqui ou clique para selecionar",
    )
    file_ui
    return (file_ui,)


@app.cell(hide_code=True)
def _(file_ui, mo, pl):
    mo.stop(
        not file_ui.value,
        mo.callout(
            mo.md("⬆️ **Aguardando arquivo.** Faça o upload de um arquivo CSV acima para iniciar a análise."),
            kind="warn",
        ),
    )
    df = pl.read_csv(file_ui.contents(), try_parse_dates=True)
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"✅ **Arquivo carregado com sucesso!** "
                    f"**{len(df):,}** linhas · **{len(df.columns)}** colunas"
                ),
                kind="success",
            ),
            mo.md("### Prévia dos dados"),
            df.head(5),
        ]
    )
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 2. Configuração da Série

    Selecione a **coluna de data** e, se necessário, filtre a série por um **grupo** específico
    (útil quando o arquivo contém múltiplas entidades como cidades, produtos ou canais).
    A escolha da **métrica** será feita na Seção 3, próxima aos gráficos.

    > ⚠️ Se houver múltiplos registros por dia, será calculada a **média diária** da métrica.
    """)
    return


@app.cell(hide_code=True)
def _(cs, df, mo, pl):
    # Detecta colunas temporais e categóricas
    _temporal_types = (pl.Date, pl.Datetime)
    _date_cols = [c for c in df.columns if isinstance(df.schema[c], _temporal_types)]
    _date_options = _date_cols if _date_cols else df.columns
    _cat_cols = df.select(cs.string()).columns

    date_col_drop = mo.ui.dropdown(
        options=list(_date_options),
        value=_date_options[0] if _date_options else None,
        label="Coluna de data",
        full_width=True,
    )
    group_col_drop = mo.ui.dropdown(
        options={"Nenhum (série completa)": None} | {c: c for c in _cat_cols},
        value="Nenhum (série completa)",
        label="Agrupamento (opcional)",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("### 2.1 Coluna de data"),
            date_col_drop,
        ]
    )
    return date_col_drop, group_col_drop


@app.cell(hide_code=True)
def _(df, group_col_drop, mo):
    # Dropdown de valor do grupo — reativo ao group_col_drop
    if group_col_drop.value is None:
        group_val_drop = mo.ui.dropdown(
            options=["Série completa"],
            value="Série completa",
            label="Valor do grupo",
            full_width=True,
        )
        _group_row = group_col_drop
    else:
        _vals = df[group_col_drop.value].drop_nulls().unique().sort().to_list()
        group_val_drop = mo.ui.dropdown(
            options=_vals,
            value=_vals[0] if _vals else None,
            label=f"Filtrar por: {group_col_drop.value}",
            full_width=True,
        )
        _group_row = mo.hstack([group_col_drop, group_val_drop], gap=1, justify="start")

    mo.vstack([
        mo.md("### 2.2 Filtragem por grupo (opcional)"),
        mo.md(
            "> Útil quando o arquivo contém múltiplas entidades (ex: cidade, produto, canal). "
            "Selecione uma coluna categórica e o valor que deseja analisar."
        ),
        _group_row,
    ])
    return (group_val_drop,)


@app.cell(hide_code=True)
def _(date_col_drop, df, group_col_drop, group_val_drop, mo, pl):
    mo.stop(
        not date_col_drop.value,
        mo.callout(
            mo.md("⚙️ Selecione a coluna de data acima para continuar."),
            kind="warn",
        ),
    )

    _date_col = date_col_drop.value

    # Converte a coluna de data para Datetime se ainda for string
    _temporal_types = (pl.Date, pl.Datetime)
    if isinstance(df.schema[_date_col], _temporal_types):
        _df_parsed = df.with_columns(pl.col(_date_col).cast(pl.Datetime))
    else:
        _df_parsed = df.with_columns(pl.col(_date_col).str.to_datetime(strict=False))

    # Aplica filtro de grupo se selecionado
    if group_col_drop.value is not None:
        df_prepared = _df_parsed.filter(
            pl.col(group_col_drop.value) == group_val_drop.value
        )
    else:
        df_prepared = _df_parsed

    _d_min = df_prepared[_date_col].min()
    _d_max = df_prepared[_date_col].max()
    _d_min_str = _d_min.strftime("%d/%m/%Y") if _d_min else "—"
    _d_max_str = _d_max.strftime("%d/%m/%Y") if _d_max else "—"
    _group_info = (
        f" · Grupo: **{group_col_drop.value} = {group_val_drop.value}**"
        if group_col_drop.value
        else ""
    )

    mo.vstack(
        [
            mo.md("### 2.3 Série preparada"),
            mo.callout(
                mo.md(
                    f"📅 **{len(df_prepared):,}** registros · "
                    f"de **{_d_min_str}** a **{_d_max_str}**"
                    f"{_group_info}"
                ),
                kind="info",
            ),
        ]
    )
    return (df_prepared,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 3. Visão Geral Descritiva

    Selecione a **métrica** que deseja analisar e confira as estatísticas básicas da série.
    A escolha aqui reflete diretamente em todos os gráficos e testes abaixo.
    """)
    return


@app.cell(hide_code=True)
def _(cs, df_prepared, mo):
    _numeric_cols = df_prepared.select(cs.numeric()).columns
    metric_col_drop = mo.ui.dropdown(
        options=list(_numeric_cols),
        value=_numeric_cols[0] if _numeric_cols else None,
        label="Métrica a analisar",
        full_width=True,
    )
    mo.vstack([mo.md("### 3.1 Selecione a métrica"), metric_col_drop])
    return (metric_col_drop,)


@app.cell(hide_code=True)
def _(date_col_drop, df_prepared, metric_col_drop, mo, pl):
    mo.stop(
        not metric_col_drop.value,
        mo.callout(mo.md("⚙️ Selecione uma métrica acima para continuar."), kind="warn"),
    )

    _date_col = date_col_drop.value
    _metric_col = metric_col_drop.value

    # Agrega diariamente (média por dia)
    df_series = (
        df_prepared
        .with_columns(pl.col(_date_col).dt.truncate("1d").alias("date"))
        .group_by("date")
        .agg(pl.col(_metric_col).mean().alias("value"))
        .sort("date")
        .drop_nulls()
    )

    _s = df_series["value"]
    _n = len(_s)
    _nulls = _s.null_count()
    _d_min = df_series["date"].min()
    _d_max = df_series["date"].max()
    _span = (_d_max - _d_min).days if _d_min and _d_max else 0

    _stats = pl.DataFrame({
        "Estatística": ["Contagem", "Nulos", "Mínimo", "Máximo", "Média", "Mediana", "Desvio padrão"],
        "Valor": [
            f"{_n:,}",
            f"{_nulls} ({100*_nulls/_n:.1f}%)" if _n > 0 else "—",
            f"{_s.min():.4f}",
            f"{_s.max():.4f}",
            f"{_s.mean():.4f}",
            f"{_s.median():.4f}",
            f"{_s.std():.4f}",
        ],
    })

    _callout_kind = "warn" if _nulls > 0 else "success"
    _callout_msg = (
        f"⚠️ A série possui **{_nulls} valores nulos** ({100*_nulls/_n:.1f}%). "
        "Eles serão ignorados nos cálculos estatísticos e gráficos."
        if _nulls > 0
        else f"✅ Nenhum valor nulo. Série **{_metric_col}** com **{_n}** dias, "
             f"abrangendo **{_span}** dias no total."
    )

    mo.vstack([
        mo.callout(mo.md(_callout_msg), kind=_callout_kind),
        mo.md("### 3.2 Estatísticas descritivas"),
        df_prepared[metric_col_drop.value].describe(),
    ])
    return (df_series,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # 4. Exploração Visual

    Navegue pelas abas abaixo para explorar diferentes aspectos da série temporal.
    Os gráficos são interativos: passe o mouse para ver tooltips, clique na legenda
    para filtrar e use o seletor de intervalo para zoom.
    """)
    return


@app.cell(hide_code=True)
def _(df_series, mo, pl):
    mov_avg_slider = mo.ui.slider(
        start=2, stop=52, value=7, step=1,
        label="Janela da média móvel (períodos)",
        full_width=True,
    )
    decomp_radio = mo.ui.radio(
        options={"Aditivo": "additive", "Multiplicativo": "multiplicative"},
        value="Aditivo",
        label="Modelo de decomposição",
    )

    _anos_selecionaveis = ['Todos']
    _anos_selecionaveis.extend(list(df_series['date'].dt.year().cast(pl.String).unique().sort()))

    heatmap_dropdown = mo.ui.dropdown(
        options=_anos_selecionaveis,
        label='Anos disponíveis',
        value=df_series['date'].dt.year().max()
    )
    sazonal_radio = mo.ui.radio(
        options=['Todos', 'Mês do ano', 'Semana do ano', 'Dia da semana'],
        inline=True,
        value='Mês do ano'
    )
    return decomp_radio, heatmap_dropdown, mov_avg_slider, sazonal_radio


@app.cell(hide_code=True)
def _(date_col_drop, df_series, mo):
    _date_range = mo.ui.date_range.from_series(df_series[date_col_drop.selected_key],label=None,full_width=True)
    date_selector = mo.md(
        r"""
        ## 4.1 Gráfico da série temporal completa
        Selecionador de intervalo: {date_selector}    
        """
    ).batch(date_selector=_date_range)
    # date_selector
    return (date_selector,)


@app.cell(hide_code=True)
def _(alt, date_selector, df_series, mo):
    # ── Tab 1: Série completa ────────────────────────────────────────────────────

    # Define intervalo inicial
    _date_range = ((date_selector.value["date_selector"][0], date_selector.value["date_selector"][1]))

    _brush = alt.selection_interval(encodings=["x"], value={"x":_date_range})

    _line = (
        alt.Chart(df_series)
        .mark_line(color="#4f8ef7")
        .encode(
            x=alt.X("date:T", title="Data").scale(domain=_brush),
            y=alt.Y("value:Q", title="Valor"),
            tooltip=[
                alt.Tooltip("date:T", title="Data", format="%d/%m/%Y"),
                alt.Tooltip("value:Q", title="Valor", format=",.1f"),
            ],
        )
        .properties(
            height=280, width=900,
            title=alt.Title("Série temporal completa", fontSize=20, color="#2d3a4a"),
        )
    )

    _area = (
        alt.Chart(df_series)
        .mark_area(color="#4f8ef7", opacity=0.1)
        .encode(
            x=alt.X("date:T", title="Data").scale(domain=_brush),
            y="value:Q"
        )
        .properties(height=280, width=900)
    )
    _selector = (
        alt.Chart(df_series)
        .mark_line(color="gray")
        .encode(x=alt.X("date:T", title=None), y=alt.Y("value:Q", title=None))
        .properties(height=50, width=900, title=alt.Title("Seletor de intervalo", fontSize=11))
        .add_params(_brush)
    )

    # teste = mo.hstack([_line & _selector, _line.value])
    # teste
    _chart_serie = mo.ui.altair_chart((_line + _area) & _selector)

    _final_chart = mo.vstack([date_selector, _chart_serie])
    _final_chart
    return


@app.cell
def _(date_selector, df_series, pl):
    df_series.filter(
        (pl.col('date') >= date_selector.value["date_selector"][0]) &
        (pl.col('date') <= date_selector.value["date_selector"][1])
    ).describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.2 Gráficos diversos para análise da série
    """)
    return


@app.cell(hide_code=True)
def _(
    alt,
    decomp_radio,
    df_series,
    heatmap_dropdown,
    mo,
    mov_avg_slider,
    pl,
    sazonal_radio,
    seasonal_decompose,
):
    # ── Definindo novas colunas de tempo ──────────────────────────────────────────────────────
    _df_s = df_series.with_columns([
        pl.col("date").dt.year().alias("ano"),
        pl.col("date").dt.month().alias("mes"),
        pl.col("date").dt.week().alias("semana_iso"),
        pl.col("date").dt.weekday().alias("dia_semana"),
    ])

    # ── Tab 2: Hetmap ──────────────────────────────────────────────────────
    if heatmap_dropdown.value == 'Todos':
        _df_heatmap = _df_s
    else:
        _df_heatmap = _df_s.filter(pl.col('ano')==int(heatmap_dropdown.value))

    _heatmap = (
        alt.Chart(_df_heatmap)
        .mark_rect()
        .encode(
            x=alt.X(field='date', type='temporal', sort='ascending', timeUnit='date'),
            y=alt.Y(field='mes',sort='ascending'),
            color=alt.Color(field='value', type='quantitative', scale={'scheme': 'blueorange'}),
            row=alt.Row(field='ano', sort='ascending', spacing=50),
            tooltip=alt.Tooltip(['date','value'])
        )
        .properties(height=250, width=820, title=alt.Title("Heatmap ano a ano", fontSize=14, color="#2d3a4a"))
    )

    _chart_heatmap = mo.vstack([
        heatmap_dropdown,
        mo.ui.altair_chart(_heatmap)
    ])



    # ── Tab 2: Sazonalidade ──────────────────────────────────────────────────────
    _legend_select = alt.selection_point(fields=['ano'], bind='legend')

    _sazo_mensal = (
        alt.Chart(_df_s)
        .mark_line(point=alt.OverlayMarkDef(filled=False, fill="white"))
        .encode(
            x=alt.X("month(date):T", title="Mês"),
            y=alt.Y("mean(value):Q", title="Valor médio"),
            color=alt.Color("ano:N", title="Ano"),
            opacity=alt.when(_legend_select).then(alt.value(1)).otherwise(alt.value(0.2)),
            tooltip=[
                alt.Tooltip("month(date):T", title="Mês"),
                alt.Tooltip("ano:N", title="Ano"),
                alt.Tooltip("mean(value):Q", title="Média", format=",.4f"),
            ],
        )
        .properties(height=220, width=820, title=alt.Title("Sazonalidade mensal — comparação ano a ano", fontSize=14, color="#2d3a4a"))
        .add_params(_legend_select)
    )

    _sazo_semanal = (
        alt.Chart(_df_s)
        .mark_line(point=alt.OverlayMarkDef(filled=False, fill="white"))
        .encode(
            x=alt.X("semana_iso:Q", title="Semana ISO"),
            y=alt.Y("mean(value):Q", title="Valor médio"),
            color=alt.Color("ano:N", title="Ano"),
            opacity=alt.when(_legend_select).then(alt.value(1)).otherwise(alt.value(0.2)),
            tooltip=[
                alt.Tooltip("semana_iso:Q", title="Semana"),
                alt.Tooltip("ano:N", title="Ano"),
                alt.Tooltip("mean(value):Q", title="Média", format=",.4f"),
            ],
        )
        .properties(height=220, width=820, title=alt.Title("Sazonalidade semanal — comparação ano a ano", fontSize=14, color="#2d3a4a"))
        .add_params(_legend_select)
    )

    # YoY por dia da semana (facetado por ano)
    _sazo_diasemana = (
        alt.Chart(_df_s)
        .mark_line()
        .encode(
            x=alt.X("dia_semana:Q", title="Dia da semana (0=Seg, 6=Dom)",
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5, 6])),
            y=alt.Y("mean(value):Q", title="Valor médio"),
            color=alt.Color("semana_iso:Q", title="Semana ISO",
                            scale=alt.Scale(scheme="blues")),
            row=alt.Row("ano:N", title="Ano"),
            tooltip=[
                alt.Tooltip("dia_semana:Q", title="Dia da semana"),
                alt.Tooltip("semana_iso:Q", title="Semana ISO"),
                alt.Tooltip("ano:N", title="Ano"),
                alt.Tooltip("mean(value):Q", title="Média", format=",.4f"),
            ],
        )
        .properties(height=220, width=820,
                    title=alt.Title("Sazonalidade semanal — por dia da semana e ano", fontSize=14, color="#2d3a4a"))
    )

    if sazonal_radio.value == 'Mês do ano':
        _chart_sazo = mo.vstack([sazonal_radio,_sazo_mensal])
    elif sazonal_radio.value == 'Semana do ano':
        _chart_sazo = mo.vstack([sazonal_radio,_sazo_semanal])
    elif sazonal_radio.value == 'Dia da semana':
        _chart_sazo = mo.vstack([sazonal_radio,_sazo_diasemana])
    else:
        _chart_sazo = mo.vstack([
            sazonal_radio,
            mo.ui.altair_chart(
                alt.vconcat(_sazo_mensal, _sazo_semanal)
                .resolve_scale(color="shared")
            ),
            mo.ui.altair_chart(_sazo_diasemana),
        ])


    # _chart_sazo = mo.vstack([
    #     mo.ui.altair_chart(
    #         alt.vconcat(_sazo_mensal, _sazo_semanal)
    #         .resolve_scale(color="shared")
    #     ),
    #     mo.ui.altair_chart(_sazo_diasemana),
    # ])

    # ── Tab 3: Tendência ─────────────────────────────────────────────────────────
    # Média anual facetada por mês (inspirado em data-visualization.py)
    _df_trend = df_series.with_columns([
        pl.col("date").dt.year().alias("ano"),
        pl.col("date").dt.month().alias("mes"),
    ])
    _years_list = sorted(_df_trend["ano"].unique().to_list())

    _trend_line = (
        alt.Chart(_df_trend)
        .mark_line(point=alt.OverlayMarkDef(filled=False, fill="white"), color="#4f8ef7")
        .encode(
            x=alt.X("ano:Q", title="Ano",
                    axis=alt.Axis(values=_years_list, format="d", labelAngle=-90)),
            y=alt.Y("mean(value):Q", title="Média"),
        )
        .properties(height=300, width=55)
    )
    _trend_rule = (
        alt.Chart(_df_trend)
        .transform_aggregate(avg_val="mean(value)", groupby=["ano", "mes"])
        .mark_rule(color="#e05a5a", strokeDash=[4, 3], size=1.5)
        .encode(y=alt.Y("mean(avg_val):Q"))
    )
    _chart_trend = mo.ui.altair_chart(
        (_trend_line + _trend_rule)
        .facet(column=alt.Column("mes:Q", title="Mês", sort="ascending"))
        .properties(
            title=alt.Title(
                "Tendência — média anual por mês (linha vermelha = média histórica do mês)",
                fontSize=14, color="#2d3a4a",
            )
        )
    )

    # ── Tab 4: Lag plots ─────────────────────────────────────────────────────────
    def _make_lag_chart(lag, w=200, h=200):
        return (
            alt.Chart(df_series)
            .transform_window(window=[alt.WindowFieldDef(op="lag", field="value", param=lag, **{"as": f"lag{lag}"})])
            .mark_point(opacity=0.5, size=20, color="#4f8ef7")
            .encode(
                x=alt.X("value:Q", title="y(t)"),
                y=alt.Y(f"lag{lag}:Q", title=f"y(t-{lag})"),
                tooltip=[
                    alt.Tooltip("date:T", title="Data", format="%d/%m/%Y"),
                    alt.Tooltip("value:Q", title="y(t)", format=",.4f"),
                    alt.Tooltip(f"lag{lag}:Q", title=f"y(t-{lag})", format=",.4f"),
                ],
            )
            .properties(width=w, height=h, title=f"Lag {lag}")
        )
    _chart_lag = mo.ui.altair_chart(
        alt.hconcat(_make_lag_chart(1), _make_lag_chart(2), _make_lag_chart(7), _make_lag_chart(14))
        .resolve_scale(x="shared", y="shared")
    )

    # ── Tab 5: Média móvel ───────────────────────────────────────────────────────
    _window = mov_avg_slider.value
    _df_ma = df_series.with_columns(
        pl.col("value").rolling_mean(window_size=_window, center=True).alias("media_movel")
    )
    _ma_raw = (
        alt.Chart(_df_ma)
        .mark_line(color="#b0b8c9", opacity=0.6)
        .encode(
            x=alt.X("date:T", title="Data"),
            y=alt.Y("value:Q", title="Valor"),
            tooltip=[alt.Tooltip("date:T", format="%d/%m/%Y"), alt.Tooltip("value:Q", format=",.4f")],
        )
    )
    _ma_line = (
        alt.Chart(_df_ma)
        .mark_line(color="#f7934f", size=2.5)
        .encode(
            x="date:T",
            y=alt.Y("media_movel:Q", title="Média móvel"),
            tooltip=[alt.Tooltip("date:T", format="%d/%m/%Y"), alt.Tooltip("media_movel:Q", title=f"MM({_window})", format=",.4f")],
        )
    )
    _chart_ma = mo.vstack([
        mov_avg_slider,
        mo.ui.altair_chart(
            (_ma_raw + _ma_line)
            .properties(height=280, width=900, title=f"Série original + Média Móvel (janela = {_window} períodos)")
        ),
    ])

    # ── Tab 6: Diferenciação ─────────────────────────────────────────────────────
    _chart_diff = mo.ui.altair_chart(
        alt.Chart(df_series)
        .transform_window(window=[alt.WindowFieldDef(op="lag", field="value", param=1, **{"as": "lag1"})])
        .transform_calculate(diff1="datum.value - datum.lag1")
        .mark_line(color="#a055f7")
        .encode(
            x=alt.X("date:T", title="Data"),
            y=alt.Y("diff1:Q", title="Δ Valor (1ª diferença)"),
            tooltip=[
                alt.Tooltip("date:T", title="Data", format="%d/%m/%Y"),
                alt.Tooltip("diff1:Q", title="Diferença", format=",.4f"),
            ],
        )
        .properties(height=280, width=900, title="1ª Diferença da série (y(t) − y(t−1))")
    )

    # ── Tab 7: Decomposição ──────────────────────────────────────────────────────
    _model = decomp_radio.value
    try:
        _arr = df_series["value"].drop_nulls().to_numpy()
        _n_periods = max(2, len(_arr) // 4)
        _decomp = seasonal_decompose(_arr, model=_model, period=_n_periods, extrapolate_trend="freq")
        _dates = df_series["date"].drop_nulls().to_list()[:len(_arr)]

        _df_decomp = pl.DataFrame({
            "date": _dates,
            "Observado": _arr.tolist(),
            "Tendência": _decomp.trend.tolist(),
            "Sazonalidade": _decomp.seasonal.tolist(),
            "Resíduos": _decomp.resid.tolist(),
        })

        def _decomp_chart(y_col, color):
            return (
                alt.Chart(_df_decomp)
                .mark_line(color=color)
                .encode(
                    x=alt.X("date:T", title=None),
                    y=alt.Y(f"{y_col}:Q", title=y_col),
                    tooltip=[alt.Tooltip("date:T", format="%d/%m/%Y"), alt.Tooltip(f"{y_col}:Q", format=",.4f")],
                )
                .properties(height=120, width=860, title=y_col)
            )
        _decomp_full = alt.vconcat(
            _decomp_chart("Observado", "#4f8ef7"),
            _decomp_chart("Tendência", "#f7934f"),
            _decomp_chart("Sazonalidade", "#55c97a"),
            _decomp_chart("Resíduos", "#e05a5a"),
        ).resolve_scale(x="shared")

        _chart_decomp = mo.vstack([
            decomp_radio,
            mo.ui.altair_chart(_decomp_full),
        ])
    except Exception as _e:
        _chart_decomp = mo.callout(
            mo.md(f"⚠️ Não foi possível decompor a série: `{_e}`. "
                  "Tente aumentar o número de períodos ou usar frequência mensal."),
            kind="warn",
        )

    # ── Montagem das abas ────────────────────────────────────────────────────────
    mo.ui.tabs({
        "📅 Sazonalidade": _chart_sazo,
        "📊 Heatmap": _chart_heatmap,
        "📈 Tendência": _chart_trend,
        "🔁 Lag": _chart_lag,
        "〰️ Média Móvel": _chart_ma,
        # "➕ Diferenciação": _chart_diff,
        # "🧩 Decomposição": _chart_decomp,
    })
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. Decomposição
    """)
    return


@app.cell
def _(df_series, seasonal_decompose):
    _decompos = seasonal_decompose(df_series['value'], period=365, extrapolate_trend="freq")

    _decompos.plot()
    return


@app.cell
def _(df_series):
    max(2, len(df_series['value']) // 4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. Tranformações

    As transformações disponíveis para os dados são:

     - Diferenciação: calcular a diferença entre dois dias sucessivos;
     - Transformação de Box Cox: o objetivo é normalizar a variação da amplitudade dos dados para que sua variância esteja mais uniforme;
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.1 Diferenciação
    """)
    return


@app.cell
def _(df_series, np, pl):
    _df_diff = df_series.with_columns(
        diff1 = pl.col(name='value') - pl.col(name='value').shift()
    ).drop_nulls()

    _n_bins = 20
    _bin_size = (np.ceil(_df_diff['diff1'].max()) - np.floor(_df_diff['diff1'].min()))/_n_bins

    _df_diff = _df_diff.with_columns(
        bin = (pl.col('diff1')/_bin_size).round(0)
    )
    # _df_diff
    _df_diff = _df_diff.group_by('bin').agg(
        pl.col('bin').count().alias('count')
    ).with_columns(
        bin_value=pl.col('bin')*_bin_size
    )
    return


@app.cell
def _(alt, df_series, np, pl):
    _ts_size = df_series['value'].len()
    _acf_limit = 2/np.sqrt(_ts_size)

    _df_diff = df_series.with_columns(
        diff1 = pl.col(name='value') - pl.col(name='value').shift()
    )

    _chart_diff = alt.Chart(_df_diff).encode(
        x='date',
        y='diff1'
    ).mark_rule().properties(width=900)

    _chart_density = alt.Chart(_df_diff).transform_density('diff1', as_=['diff1', 'density']).encode(
        x=alt.X('diff1:Q'),
        y=alt.Y('density:Q')
    ).mark_area(opacity=0.5).properties(width=900)

    _chart_diff_hist = alt.Chart(_df_diff).transform_calculate(
        freq='count()/'
    ).encode(
        y='count()',
        x=alt.X('diff1', bin=True).bin(step=.5)
    ).mark_bar(opacity=0.5).properties(width=900)

    # _chart_diff &  (_chart_diff_hist + 
    _chart_density
    # _chart_diff_hist
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Autocorrelação
    """)
    return


@app.cell
def _(MSTL, acf, alt, df_series, np, pl):
    _decompos = MSTL(df_series['value'], periods=365).fit()

    _df_diff = df_series.with_columns(
        diff1 = pl.col(name='value') - pl.col(name='value').shift()
    )

    _ts_size = df_series['value'].len()
    _acf_limit = 2/np.sqrt(_ts_size)


    _data_acf = acf(_df_diff.filter(pl.col('diff1').is_not_null())['diff1'])


    _data_acf = acf(_decompos.resid)

    _df_acf = pl.DataFrame(data=_data_acf, schema=['valores'])

    _df_acf = _df_acf.with_row_index(offset=1).filter(pl.col('index') > 1)

    _base_chart = alt.Chart(_df_acf)

    _chart_acf = _base_chart.encode(
        x='index:Q',
        y='valores:Q'
    ).mark_bar().properties(width=900)

    _chart_acf_limit_pos = _base_chart.mark_rule(strokeDash=[8,4], color='red').encode(
        x=alt.value(0),
        y=alt.datum(_acf_limit),
        x2=alt.value('width'),
        y2=alt.datum(_acf_limit)
    )

    _chart_acf_limit_neg = _base_chart.mark_rule(strokeDash=[8,4], color='red').encode(
        x=alt.value(0),
        y=alt.datum(-_acf_limit),
        x2=alt.value('width'),
        y2=alt.datum(-_acf_limit)
    )

    _chart_acf + _chart_acf_limit_pos + _chart_acf_limit_neg

    # _data_acf
    # _chart_diff
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
