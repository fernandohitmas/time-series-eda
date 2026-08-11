import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import anywidget
    import polars as pl
    from polars import selectors as cs
    import altair as alt
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    from statsmodels.tsa.stattools import adfuller, kpss
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.tsa.seasonal import seasonal_decompose

    return alt, cs, mo, pl, seasonal_decompose


@app.cell(hide_code=True)
def _(alt):
    alt.data_transformers.enable("vegafusion")
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
        _stats,
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
def _(mo):
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
    return decomp_radio, mov_avg_slider


@app.cell(hide_code=True)
def _(date_col_drop, df_series, mo):
    _date_range = mo.ui.date_range.from_series(df_series[date_col_drop.selected_key],label=None)
    date_selector = mo.md(
        r"""
        ## 4.1 Gráfico da série temporal completa
        Selecionador de data:
    
        {date_selector}    
        """
    ).batch(date_selector=_date_range)
    date_selector
    return (date_selector,)


@app.cell(hide_code=True)
def _(alt, date_selector, df_series):
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
    _chart_serie = (_line + _area) & _selector 
    _chart_serie
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
    mo,
    mov_avg_slider,
    pl,
    seasonal_decompose,
):
    # ── Tab 2: Sazonalidade ──────────────────────────────────────────────────────
    _legend_select = alt.selection_point(fields=['ano'], bind='legend')

    _df_s = df_series.with_columns([
        pl.col("date").dt.year().alias("ano"),
        pl.col("date").dt.month().alias("mes"),
        pl.col("date").dt.week().alias("semana_iso"),
        pl.col("date").dt.weekday().alias("dia_semana"),
    ])

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
        .properties(height=220, width=700,
                    title=alt.Title("Sazonalidade semanal — por dia da semana e ano", fontSize=14, color="#2d3a4a"))
    )
    _chart_sazo = mo.vstack([
        mo.ui.altair_chart(
            alt.vconcat(_sazo_mensal, _sazo_semanal)
            .resolve_scale(color="shared")
        ),
        mo.ui.altair_chart(_sazo_diasemana),
    ])

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
            # tooltip=[
            #     alt.Tooltip("ano:Q", title="Ano"),
            #     alt.Tooltip("mes:Q", title="Mês"),
            #     alt.Tooltip("mean(value):Q", title="Média", format=",.4f"),
            # ],
        )
        .properties(height=300, width=55)
    )
    _trend_rule = (
        alt.Chart(_df_trend)
        .mark_rule(color="#e05a5a", strokeDash=[4, 3], size=1.5)
        .encode(y=alt.Y("mean(avg_val):Q"))
        .transform_aggregate(avg_val="mean(value)", groupby=["ano", "mes"])
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
        # "🗓 Série completa": _chart_serie,
        "📅 Sazonalidade": _chart_sazo,
        "📈 Tendência": _chart_trend,
        "🔁 Lag": _chart_lag,
        "〰️ Média Móvel": _chart_ma,
        "➕ Diferenciação": _chart_diff,
        "🧩 Decomposição": _chart_decomp,
    })
    return


if __name__ == "__main__":
    app.run()
