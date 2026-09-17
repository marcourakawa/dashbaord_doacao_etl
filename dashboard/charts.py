import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =========================================================
# COLORS
# =========================================================

VALUE_COLOR = "#0EA6A0"
QUANTITY_COLOR = "#F5A623"
GRID_COLOR = "#E7ECF3"
AXIS_TEXT_COLOR = "#334155"


MONTHS = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}


# =========================================================
# COMMON STYLE
# =========================================================

def apply_chart_style(
    fig,
    height=430,
):
    fig.update_layout(
        height=height,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Arial, sans-serif",
            color=AXIS_TEXT_COLOR,
        ),
        hoverlabel=dict(
            bgcolor="#1A2744",
            bordercolor="#1A2744",
            font_size=13,
            font_family="Inter, Arial, sans-serif",
            font_color="#FFFFFF",
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(
            size=11,
            color=AXIS_TEXT_COLOR,
        ),
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            size=12,
            color=AXIS_TEXT_COLOR,
        ),
    )

    return fig


# =========================================================
# EMPTY CHART
# =========================================================

def empty_figure(
    height=430,
    message="Sem dados no período selecionado",
):
    fig = go.Figure()

    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            size=13,
            color=AXIS_TEXT_COLOR,
        ),
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return apply_chart_style(
        fig,
        height=height,
    )


# =========================================================
# DIMENSION CHART
# =========================================================

def donation_dimension_chart(
    df,
    dimension="loja",
    top_n=10,
    ranking="valor",
):
    """
    Create a donation ranking chart.

    Ranking can be based on total value or total quantity.
    """

    if df.empty:
        return empty_figure()

    data = df.copy()

    # =====================================================
    # ABS VALUES
    # =====================================================

    data["valor_perda"] = (
        data["valor_perda"]
        .abs()
    )

    data["quantidade"] = (
        data["quantidade"]
        .abs()
    )

    # =====================================================
    # STORE
    # =====================================================

    if dimension == "loja":

        grouped = (
            data
            .groupby(
                "sigla_loja",
                dropna=False,
            )
            .agg(
                valor=(
                    "valor_perda",
                    "sum",
                ),
                quantidade=(
                    "quantidade",
                    "sum",
                ),
                registros=(
                    "valor_perda",
                    "size",
                ),
            )
            .reset_index()
        )

        grouped["label"] = (
            grouped["sigla_loja"]
            .fillna("Não informado")
            .astype(str)
        )

    # =====================================================
    # CATEGORY
    # =====================================================

    elif dimension == "categoria":

        grouped = (
            data
            .groupby(
                "categoria_modular",
                dropna=False,
            )
            .agg(
                valor=(
                    "valor_perda",
                    "sum",
                ),
                quantidade=(
                    "quantidade",
                    "sum",
                ),
                registros=(
                    "valor_perda",
                    "size",
                ),
            )
            .reset_index()
        )

        grouped["label"] = (
            grouped["categoria_modular"]
            .fillna("Não informado")
            .astype(str)
        )

    # =====================================================
    # PRODUCT
    # =====================================================

    elif dimension == "produto":

        grouped = (
            data
            .groupby(
                [
                    "codbar",
                    "produto",
                ],
                dropna=False,
            )
            .agg(
                valor=(
                    "valor_perda",
                    "sum",
                ),
                quantidade=(
                    "quantidade",
                    "sum",
                ),
                registros=(
                    "valor_perda",
                    "size",
                ),
            )
            .reset_index()
        )

        grouped["label"] = (
            grouped["produto"]
            .fillna("Produto não informado")
            .astype(str)
        )

    # =====================================================
    # INVALID DIMENSION
    # =====================================================

    else:

        raise ValueError(
            f"Dimensão inválida: {dimension}"
        )

    # =====================================================
    # EMPTY AFTER GROUPING
    # =====================================================

    if grouped.empty:
        return empty_figure()

    # =====================================================
    # RANKING
    # =====================================================

    if ranking == "valor":

        grouped = (
            grouped
            .sort_values(
                "valor",
                ascending=False,
            )
            .head(top_n)
            .sort_values(
                "valor",
                ascending=True,
            )
        )

    elif ranking == "quantidade":

        grouped = (
            grouped
            .sort_values(
                "quantidade",
                ascending=False,
            )
            .head(top_n)
            .sort_values(
                "quantidade",
                ascending=True,
            )
        )

    else:

        raise ValueError(
            f"Ranking inválido: {ranking}"
        )

    # =====================================================
    # CREATE FIGURE
    # =====================================================

    fig = go.Figure()

    # =====================================================
    # VALUE RANKING
    # =====================================================

    if ranking == "valor":

        fig.add_trace(
            go.Bar(
                x=grouped["valor"],
                y=grouped["label"],
                orientation="h",
                name="Valor",

                marker=dict(
                    color=VALUE_COLOR,
                    cornerradius=4,
                ),

                customdata=grouped[
                    [
                        "quantidade",
                        "registros",
                    ]
                ].values,

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Valor: R$ %{x:,.2f}<br>"
                    "Quantidade: %{customdata[0]:,.0f}<br>"
                    "Registros: %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    # =====================================================
    # QUANTITY RANKING
    # =====================================================

    else:

        fig.add_trace(
            go.Bar(
                x=grouped["quantidade"],
                y=grouped["label"],
                orientation="h",
                name="Quantidade",

                marker=dict(
                    color=QUANTITY_COLOR,
                    cornerradius=4,
                ),

                customdata=grouped[
                    [
                        "valor",
                        "registros",
                    ]
                ].values,

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Quantidade: %{x:,.0f}<br>"
                    "Valor: R$ %{customdata[0]:,.2f}<br>"
                    "Registros: %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        height=500,

        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20,
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color=AXIS_TEXT_COLOR,
        ),

        showlegend=False,

        hoverlabel=dict(
            bgcolor="#1A2744",
            bordercolor="#1A2744",
            font_size=13,
            font_family="Inter, Arial, sans-serif",
            font_color="#FFFFFF",
        ),
    )

    # =====================================================
    # X AXIS
    # =====================================================

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        tickfont=dict(
            size=11,
            color=AXIS_TEXT_COLOR,
        ),
    )

    # =====================================================
    # Y AXIS
    # =====================================================

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(
            size=12,
            color=AXIS_TEXT_COLOR,
        ),
    )

    # =====================================================
    # VALUE FORMAT
    # =====================================================

    if ranking == "valor":

        fig.update_xaxes(
            tickprefix="R$ ",
            tickformat=",.0f",
        )

    # =====================================================
    # QUANTITY FORMAT
    # =====================================================

    else:

        fig.update_xaxes(
            tickformat=",.0f",
        )

    return fig


# =========================================================
# MONTHLY CHART
# =========================================================

def donation_monthly_chart(
    df,
    current_month=None,
):
    """
    Monthly evolution chart.

    This chart is intentionally built from the UNFILTERED dataset
    (only capped at current_month), so it always reflects the
    full-year trend regardless of the Mês / Loja / Categoria
    filters applied elsewhere on the page.
    """

    if df.empty:

        return empty_figure(
            height=380,
            message="Sem dados no período selecionado",
        )

    # =====================================================
    # CURRENT MONTH
    # =====================================================

    if current_month is None:
        current_month = 12

    current_month = max(
        1,
        min(
            12,
            current_month,
        ),
    )

    data = df.copy()

    # =====================================================
    # ABS VALUES
    # =====================================================

    data["valor_perda"] = (
        data["valor_perda"]
        .abs()
    )

    data["quantidade"] = (
        data["quantidade"]
        .abs()
    )

    # =====================================================
    # GROUP BY MONTH
    # =====================================================

    grouped = (
        data
        .groupby(
            data["data_perda"].dt.month
        )
        .agg(
            valor=(
                "valor_perda",
                "sum",
            ),
            quantidade=(
                "quantidade",
                "sum",
            ),
        )
    )

    # =====================================================
    # REINDEX ONLY UP TO CURRENT MONTH
    # =====================================================

    grouped = grouped.reindex(
        range(
            1,
            current_month + 1,
        ),
        fill_value=0,
    )

    labels = [
        MONTHS[month]
        for month in range(
            1,
            current_month + 1,
        )
    ]

    # =====================================================
    # FIGURE
    # =====================================================

    fig = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True
                }
            ]
        ]
    )

    # =====================================================
    # QUANTITY BAR
    # =====================================================

    fig.add_trace(
        go.Bar(
            x=labels,
            y=grouped["quantidade"],
            name="Quantidade",

            marker=dict(
                color=QUANTITY_COLOR,
                cornerradius=4,
            ),

            opacity=0.88,

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Quantidade doada: %{y:,.0f}"
                "<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    # =====================================================
    # VALUE LINE
    # =====================================================

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=grouped["valor"],
            name="Valor",
            mode="lines+markers",

            line=dict(
                color=VALUE_COLOR,
                width=3,
                shape="spline",
                smoothing=0.3,
            ),

            marker=dict(
                size=8,
                color="#FFFFFF",

                line=dict(
                    width=2,
                    color=VALUE_COLOR,
                ),
            ),

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Valor doado: R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        height=380,

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color=AXIS_TEXT_COLOR,
        ),

        bargap=0.35,

        showlegend=True,

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                size=12
            ),
        ),

        hoverlabel=dict(
            bgcolor="#1A2744",
            bordercolor="#1A2744",
            font_size=13,
            font_family="Inter, Arial, sans-serif",
            font_color="#FFFFFF",
        ),

        hovermode="x unified",
    )

    # =====================================================
    # X AXIS
    # =====================================================

    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID_COLOR,

        tickfont=dict(
            size=12,
            color=AXIS_TEXT_COLOR,
        ),
    )

    # =====================================================
    # QUANTITY AXIS
    # =====================================================

    fig.update_yaxes(
        title_text=None,

        showgrid=True,
        gridcolor=GRID_COLOR,

        zeroline=False,

        tickfont=dict(
            size=12,
            color=AXIS_TEXT_COLOR,
        ),

        secondary_y=False,
    )

    # =====================================================
    # VALUE AXIS
    # =====================================================

    fig.update_yaxes(
        title_text=None,

        showgrid=False,
        zeroline=False,

        tickfont=dict(
            size=12,
            color=AXIS_TEXT_COLOR,
        ),

        secondary_y=True,
    )

    return fig