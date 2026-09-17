from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.services import get_donation_data
from dashboard.utils import (
    format_brl,
    format_number,
)
from dashboard.charts import (
    donation_monthly_chart,
    donation_dimension_chart,
)


# =========================================================
# HTML HELPER
# =========================================================

def render_html(html: str) -> None:
    """
    Render an HTML block safely.

    Blank lines end Markdown's raw-HTML mode, and lines indented by
    4+ spaces are treated as code blocks. So the block is flattened
    into a single line before being handed to Streamlit.
    """

    cleaned = " ".join(
        line.strip()
        for line in html.strip().splitlines()
        if line.strip()
    )

    st.markdown(
        cleaned,
        unsafe_allow_html=True,
    )


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard de Doações",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# LOAD CSS
# =========================================================

css_path = Path("dashboard/style.css")

with open(
    css_path,
    "r",
    encoding="utf-8",
) as file:

    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html=True,
    )


# =========================================================
# MONTHS
# =========================================================

MONTH_NAMES = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]

MONTH_NUMBERS = {
    month: number
    for number, month in enumerate(
        MONTH_NAMES,
        start=1,
    )
}


# =========================================================
# CURRENT PERIOD
# =========================================================

today = pd.Timestamp(date.today())

current_month_number = today.month

current_month_name = (
    MONTH_NAMES[
        current_month_number - 1
    ]
)


# =========================================================
# HEADER
# =========================================================

render_html(
    f"""
    <div class="dashboard-header">

        <div class="header-title-group">

            <div class="header-title">
                Dashboard de Doações
            </div>

            <div class="header-subtitle">
                Acompanhamento de doações por loja, categoria e produto
            </div>

        </div>

        <div class="header-badge">
            Atualizado até {current_month_name}/{today.year}
        </div>

    </div>
    """
)


# =========================================================
# LOAD DATA
# =========================================================

df = get_donation_data()

df["data_perda"] = pd.to_datetime(
    df["data_perda"],
    errors="coerce",
)

df = df.dropna(
    subset=["data_perda"]
)


# =========================================================
# ONLY SHOW DATA UP TO CURRENT DATE
# =========================================================

df = df[
    df["data_perda"] <= today
]


# =========================================================
# FILTERS
# =========================================================

month_col, store_col, category_col = st.columns(3)


# =========================================================
# MONTH
# =========================================================

with month_col:

    available_months = (
        MONTH_NAMES[
            :current_month_number
        ]
    )

    selected_month = st.selectbox(
        "Mês",
        ["Todos"] + available_months,
    )


# =========================================================
# STORE
# =========================================================

with store_col:

    available_stores = sorted(
        df["sigla_loja"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_store = st.selectbox(
        "Loja",
        ["Todas"] + available_stores,
    )


# =========================================================
# CATEGORY
# =========================================================

with category_col:

    available_categories = sorted(
        df["categoria_modular"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_category = st.selectbox(
        "Categoria",
        ["Todas"] + available_categories,
    )


# =========================================================
# APPLY FILTERS
# =========================================================

df_filter = df.copy()


# =========================================================
# MONTH FILTER
# =========================================================

if selected_month != "Todos":

    month_number = (
        MONTH_NUMBERS[
            selected_month
        ]
    )

    df_filter = df_filter[
        df_filter["data_perda"].dt.month
        == month_number
    ]


# =========================================================
# STORE FILTER
# =========================================================

if selected_store != "Todas":

    df_filter = df_filter[
        df_filter["sigla_loja"].astype(str)
        == selected_store
    ]


# =========================================================
# CATEGORY FILTER
# =========================================================

if selected_category != "Todas":

    df_filter = df_filter[
        df_filter["categoria_modular"].astype(str)
        == selected_category
    ]


# =========================================================
# PREVIOUS MONTH
# =========================================================

def get_previous_month(
    month_number: int,
) -> int:
    """
    Return the previous calendar month.
    """

    return (
        12
        if month_number == 1
        else month_number - 1
    )


def delta_badge(
    current: float,
    previous: float | None,
    previous_label: str | None = None,
    fallback: str = "",
) -> str:
    """
    Month-over-month variation badge.

    previous_label names the baseline month.
    """

    if previous is None or previous == 0:

        if fallback:

            return (
                f'<div class="kpi-description">'
                f'{fallback}'
                f'</div>'
            )

        return ""

    percentage = (
        (current - previous)
        / previous
        * 100
    )

    direction = (
        "up"
        if percentage >= 0
        else "down"
    )

    arrow = (
        "▲"
        if percentage >= 0
        else "▼"
    )

    reference = (
        f"vs. {previous_label}"
        if previous_label
        else "vs. mês anterior"
    )

    return (
        f'<span class="kpi-delta '
        f'kpi-delta-{direction}">'
        f'{arrow} '
        f'{abs(percentage):,.1f}% '
        f'{reference}'
        f'</span>'
    )


previous_value = None
previous_quantity = None
previous_label = None


# =========================================================
# CALCULATE PREVIOUS MONTH
# =========================================================

if selected_month != "Todos":

    month_number = (
        MONTH_NUMBERS[
            selected_month
        ]
    )

    # -----------------------------------------------------
    # Previous calendar month
    # -----------------------------------------------------

    previous_month = get_previous_month(
        month_number
    )

    previous_label = (
        MONTH_NAMES[
            previous_month - 1
        ]
    )

    df_previous = df.copy()

    df_previous = df_previous[
        df_previous["data_perda"].dt.month
        == previous_month
    ]

    # -----------------------------------------------------
    # Apply same store filter
    # -----------------------------------------------------

    if selected_store != "Todas":

        df_previous = df_previous[
            df_previous[
                "sigla_loja"
            ].astype(str)
            == selected_store
        ]

    # -----------------------------------------------------
    # Apply same category filter
    # -----------------------------------------------------

    if selected_category != "Todas":

        df_previous = df_previous[
            df_previous[
                "categoria_modular"
            ].astype(str)
            == selected_category
        ]

    # -----------------------------------------------------
    # Calculate previous values
    # -----------------------------------------------------

    if not df_previous.empty:

        previous_value = (
            df_previous[
                "valor_perda"
            ]
            .abs()
            .sum()
        )

        previous_quantity = (
            df_previous[
                "quantidade"
            ]
            .abs()
            .sum()
        )


# =========================================================
# KPIs
# =========================================================

total_value = (
    df_filter[
        "valor_perda"
    ]
    .abs()
    .sum()
)

total_quantity = (
    df_filter[
        "quantidade"
    ]
    .abs()
    .sum()
)

active_stores = (
    df_filter[
        "sigla_loja"
    ]
    .nunique()
)

average_value = (
    total_value / len(df_filter)
    if len(df_filter)
    else 0
)


# =========================================================
# KPI COLUMNS
# =========================================================

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = (
    st.columns(4)
)


# =========================================================
# KPI 1 - TOTAL VALUE
# =========================================================

with kpi_col1:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                Valor total de doações
            </div>

            <div class="kpi-value">
                {format_brl(total_value)}
            </div>

            {delta_badge(
                total_value,
                previous_value,
                previous_label,
                fallback=(
                    "Todos os meses"
                    if selected_month == "Todos"
                    else "Sem base de comparação"
                ),
            )}

        </div>
        """
    )


# =========================================================
# KPI 2 - TOTAL QUANTITY
# =========================================================

with kpi_col2:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                Quantidade total de doações
            </div>

            <div class="kpi-value">
                {format_number(total_quantity)}
            </div>

            {delta_badge(
                total_quantity,
                previous_quantity,
                previous_label,
                fallback=(
                    "Todos os meses"
                    if selected_month == "Todos"
                    else "Sem base de comparação"
                ),
            )}

        </div>
        """
    )


# =========================================================
# KPI 3 - AVERAGE VALUE
# =========================================================

with kpi_col3:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                Valor médio por doação
            </div>

            <div class="kpi-value">
                {format_brl(average_value)}
            </div>

            <div class="kpi-description">
                Por registro de doação
            </div>

        </div>
        """
    )


# =========================================================
# KPI 4 - STORES
# =========================================================

with kpi_col4:

    render_html(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                Lojas participantes
            </div>

            <div class="kpi-value">
                {format_number(active_stores)}
            </div>

            <div class="kpi-description">
                No período selecionado
            </div>

        </div>
        """
    )


# =========================================================
# EMPTY STATE
# =========================================================

if df_filter.empty:

    render_html(
        """
        <div class="empty-state">
            Não há doações registradas para os filtros selecionados.
        </div>
        """
    )

    render_html(
        """
        <div class="dashboard-footer">
            Dashboard de Doações
        </div>
        """
    )

    st.stop()


# =========================================================
# ANALYSIS SECTION
# =========================================================

render_html(
    """
    <div class="section-heading">

        <div class="section-title">
            Análise das doações
        </div>

        <div class="section-description">
            Selecione uma dimensão e a métrica para visualizar o ranking.
        </div>

    </div>
    """
)


# =========================================================
# ANALYSIS CONTROLS
# =========================================================

control_col1, control_col2 = st.columns(
    [2, 1]
)


# =========================================================
# DIMENSION SELECTOR
# =========================================================

with control_col1:

    dimensions = [
        "Loja",
        "Categoria",
        "Produto",
    ]

    if hasattr(st, "segmented_control"):

        selected_dimension = st.segmented_control(
            "Dimensão",
            options=dimensions,
            default="Loja",
            key="donation_dimension",
        )

    else:

        selected_dimension = st.radio(
            "Dimensão",
            options=dimensions,
            horizontal=True,
            key="donation_dimension",
        )


# =========================================================
# RANKING SELECTOR
# =========================================================

with control_col2:

    ranking_options = [
        "Valor",
        "Quantidade",
    ]

    if hasattr(st, "segmented_control"):

        selected_ranking = st.segmented_control(
            "Exibir por",
            options=ranking_options,
            default="Valor",
            key="donation_ranking",
        )

    else:

        selected_ranking = st.radio(
            "Exibir por",
            options=ranking_options,
            horizontal=True,
            key="donation_ranking",
        )


# =========================================================
# MAP VALUES
# =========================================================

dimension_map = {
    "Loja": "loja",
    "Categoria": "categoria",
    "Produto": "produto",
}

ranking_map = {
    "Valor": "valor",
    "Quantidade": "quantidade",
}

selected_dimension_key = dimension_map[
    selected_dimension
]

selected_ranking_key = ranking_map[
    selected_ranking
]


# =========================================================
# CHART TITLES
# =========================================================

titles = {
    "Loja": "Doações por loja",
    "Categoria": "Doações por categoria",
    "Produto": "Doações por produto",
}

subtitles = {
    "Loja": {
        "Valor": "Top 10 lojas por valor das doações",
        "Quantidade": "Top 10 lojas por quantidade doada",
    },
    "Categoria": {
        "Valor": "Top 10 categorias por valor das doações",
        "Quantidade": "Top 10 categorias por quantidade doada",
    },
    "Produto": {
        "Valor": "Top 10 produtos por valor das doações",
        "Quantidade": "Top 10 produtos por quantidade doada",
    },
}


# =========================================================
# CHART HEADER
# =========================================================

render_html(
    f"""
    <div class="chart-header">

        <div class="chart-title">
            {titles[selected_dimension]}
        </div>

        <div class="chart-subtitle">
            {subtitles[selected_dimension][selected_ranking]}
        </div>

    </div>
    """
)


# =========================================================
# DIMENSION CHART
# =========================================================

fig = donation_dimension_chart(
    df_filter,
    dimension=selected_dimension_key,
    top_n=10,
    ranking=selected_ranking_key,
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


# =========================================================
# MONTHLY SECTION
# =========================================================

render_html(
    """
    <div class="section-heading">

        <div class="section-title">
            Evolução das doações
        </div>

        <div class="section-description">
            Acompanhamento mensal das doações, do ano todo.
        </div>

    </div>
    """
)


# =========================================================
# MONTHLY CHART HEADER
# =========================================================

render_html(
    """
    <div class="chart-header">

        <div class="chart-title">
            Valor e quantidade doados por mês
        </div>

        <div class="chart-subtitle">
            Evolução mensal &middot; não é afetado pelos filtros acima
        </div>

    </div>
    """
)


# =========================================================
# MONTHLY CHART
# =========================================================

fig = donation_monthly_chart(
    df,
    current_month=current_month_number,
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


# =========================================================
# FOOTER
# =========================================================

render_html(
    """
    <div class="dashboard-footer">
        Dashboard de Doações
    </div>
    """
)