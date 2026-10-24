import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_pnadc_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD,
    COLOR_NEUTRAL,
    render_source,
    fmt_br
)

def render_tab_labor():
    st.markdown('<div class="section-title">Mercado de Trabalho: PNAD Contínua & CAGED</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Evolução detalhada da taxa de desocupação, rendimento médio real, massa salarial e saldo de empregos formais gerados.</div>',
        unsafe_allow_html=True
    )
    from modules.historico_ui import cards_padrao
    cards_padrao("trabalho")

    df_series, df_caged = get_pnadc_data()

    if df_series.empty:
        st.warning("Dados da PNAD Contínua não encontrados.")
        return

    # Filtros de Governo
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        gov_options = ["Todos os Governos", "Bolsonaro (2019-2022)", "Lula (2023-atual)"]
        gov_filter = st.selectbox("Filtrar Período de Governo:", gov_options, key="labor_gov_filter")
    with col_sel2:
        st.caption("ℹ️ A PNAD Contínua do IBGE divulga dados mensais com base em trimestres móveis. O Novo CAGED computa vínculos formais CLT.")

    # Gráfico 1: Taxa de Desocupação
    st.subheader("1. Taxa de Desocupação (%) — PNAD Contínua IBGE")
    
    fig_desoc = go.Figure()
    
    df_bols = df_series[df_series["governo"] == "Bolsonaro (2019-2022)"]
    df_lula = df_series[df_series["governo"] == "Lula (2023-atual)"]
    
    if gov_filter in ("Todos os Governos", "Bolsonaro (2019-2022)"):
        fig_desoc.add_trace(go.Scatter(
            x=df_bols["periodo"],
            y=df_bols["taxa_desocupacao"],
            mode="lines+markers",
            name="Gov. Bolsonaro (2019-2022)",
            line=dict(color=COLOR_BOLSONARO, width=3.5),
            marker=dict(size=5, color=COLOR_BOLSONARO),
            hovertemplate="<b>Período:</b> %{x}<br><b>Desemprego:</b> %{y:.1f}%<extra>Bolsonaro</extra>"
        ))
    
    if gov_filter in ("Todos os Governos", "Lula (2023-atual)"):
        fig_desoc.add_trace(go.Scatter(
            x=df_lula["periodo"],
            y=df_lula["taxa_desocupacao"],
            mode="lines+markers",
            name="Gov. Lula (2023-atual)",
            line=dict(color=COLOR_LULA, width=3.5),
            marker=dict(size=5, color=COLOR_LULA),
            hovertemplate="<b>Período:</b> %{x}<br><b>Desemprego:</b> %{y:.1f}%<extra>Lula</extra>"
        ))

    # Anotações de destaques (Pico Covid e Mínima)
    if gov_filter == "Todos os Governos" and not df_bols.empty:
        pico = df_bols.loc[df_bols["taxa_desocupacao"].idxmax()]
        fig_desoc.add_annotation(
            text=f"Pico na pandemia: {fmt_br(pico['taxa_desocupacao'])}% ({pico['periodo']})",
            x=pico["periodo"],
            y=pico["taxa_desocupacao"],
            showarrow=True,
            arrowhead=2,
            arrowcolor="#f87171",
            font=dict(color="#ffffff", size=11),
            bgcolor="rgba(239, 68, 68, 0.85)",
            bordercolor="#b91c1c",
            borderwidth=1
        )
        if not df_lula.empty:
            minima = df_lula.loc[df_lula["taxa_desocupacao"].idxmin()]
            fig_desoc.add_annotation(
                text=f"Mínima da série: {fmt_br(minima['taxa_desocupacao'])}% ({minima['periodo']})",
                x=minima["periodo"],
                y=minima["taxa_desocupacao"],
                showarrow=True,
                arrowhead=2,
                arrowcolor="#34d399",
                font=dict(color="#ffffff", size=11),
                bgcolor="rgba(16, 185, 129, 0.85)",
                bordercolor="#059669",
                borderwidth=1
            )

    fig_desoc.update_xaxes(nticks=12, tickangle=-25)
    apply_plotly_theme(fig_desoc, title="Taxa de Desocupação no Brasil (%) - Série Mensal PNAD Contínua")
    st.plotly_chart(fig_desoc, width="stretch")

    # Gráficos 2 & 3 em duas colunas: Rendimento Médio Real e Massa Salarial
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("2. Rendimento Médio Real (R$)")
        st.caption("Rendimento habitual médio deflacionado pelo IPCA (preços constantes).")
        
        fig_rend = go.Figure()
        if gov_filter in ("Todos os Governos", "Bolsonaro (2019-2022)"):
            fig_rend.add_trace(go.Scatter(
                x=df_bols["periodo"],
                y=df_bols["rendimento_medio_real"],
                mode="lines",
                name="Bolsonaro",
                line=dict(color=COLOR_BOLSONARO, width=3),
                hovertemplate="<b>Período:</b> %{x}<br><b>Rendimento:</b> R$ %{y:,.2f}<extra>Bolsonaro</extra>"
            ))
        if gov_filter in ("Todos os Governos", "Lula (2023-atual)"):
            fig_rend.add_trace(go.Scatter(
                x=df_lula["periodo"],
                y=df_lula["rendimento_medio_real"],
                mode="lines",
                name="Lula",
                line=dict(color=COLOR_LULA, width=3),
                hovertemplate="<b>Período:</b> %{x}<br><b>Rendimento:</b> R$ %{y:,.2f}<extra>Lula</extra>"
            ))
        fig_rend.update_xaxes(nticks=8, tickangle=-25)
        apply_plotly_theme(fig_rend, title="Rendimento Médio Real Habitual (R$)")
        st.plotly_chart(fig_rend, width="stretch")

    with col_g2:
        st.subheader("3. Massa de Rendimento Real (R$ bi)")
        st.caption("Massa salarial total em circulação na economia nacional.")
        
        fig_massa = go.Figure()
        if gov_filter in ("Todos os Governos", "Bolsonaro (2019-2022)"):
            fig_massa.add_trace(go.Scatter(
                x=df_bols["periodo"],
                y=df_bols["massa_rendimento_real_milhoes"] / 1000.0,
                mode="lines",
                name="Bolsonaro",
                line=dict(color=COLOR_BOLSONARO, width=3),
                hovertemplate="<b>Período:</b> %{x}<br><b>Massa:</b> R$ %{y:,.1f} bi<extra>Bolsonaro</extra>"
            ))
        if gov_filter in ("Todos os Governos", "Lula (2023-atual)"):
            fig_massa.add_trace(go.Scatter(
                x=df_lula["periodo"],
                y=df_lula["massa_rendimento_real_milhoes"] / 1000.0,
                mode="lines",
                name="Lula",
                line=dict(color=COLOR_LULA, width=3),
                hovertemplate="<b>Período:</b> %{x}<br><b>Massa:</b> R$ %{y:,.1f} bi<extra>Lula</extra>"
            ))
        fig_massa.update_xaxes(nticks=8, tickangle=-25)
        apply_plotly_theme(fig_massa, title="Massa de Rendimento Real (R$ Bilhões)")
        st.plotly_chart(fig_massa, width="stretch")

    st.markdown("---")

    # Gráfico 4: Saldo CAGED de Empregos Formais
    st.subheader("4. Saldo Anual de Vagas com Carteira Assinada (Novo CAGED)")
    st.caption("Saldo líquido anual entre admissões e demissões formais CLT registrado pelo Ministério do Trabalho e Emprego.")

    fig_caged = go.Figure()
    caged_colors = [COLOR_BOLSONARO if g == "Bolsonaro" else COLOR_LULA for g in df_caged["governo"]]
    
    fig_caged.add_trace(go.Bar(
        x=[f"{r.ano}* (jan–ago)" if r.parcial else str(r.ano) for r in df_caged.itertuples()],
        y=df_caged["saldo_postos_formais"],
        marker_color=caged_colors,
        text=df_caged["saldo_postos_formais"].apply(lambda x: f"+{x:,.0f}" if x>0 else f"{x:,.0f}"),
        textposition="outside",
        textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif"),
        hovertemplate="<b>Ano:</b> %{x}<br><b>Saldo:</b> %{y:,.0f} vagas<extra></extra>"
    ))

    apply_plotly_theme(fig_caged, title="Saldo Líquido Anual de Empregos Formais (Novo CAGED)")
    st.plotly_chart(fig_caged, width="stretch")

    render_source("MTE — Novo CAGED, série com ajustes (inclui declarações fora do prazo; divulgação de dez/2025). 2019 pelo CAGED antigo, de metodologia diferente. 2026 = acumulado de janeiro a agosto.",
                  "https://static.poder360.com.br/2026/01/Caged-apresentacao-dez-2025-1.pdf")

    # Tabela de Métricas Resumo do Trabalho (calculada a partir das séries)
    st.subheader("Síntese Numérica do Mercado de Trabalho")
    col_t1, col_t2 = st.columns(2)
    for col, df_gov, nome, cor, caged_gov in (
        (col_t1, df_bols, "Governo Bolsonaro (2019-2022)", "#93c5fd", "Bolsonaro"),
        (col_t2, df_lula, "Governo Lula (2023-atual)", "#fca5a5", "Lula"),
    ):
        if df_gov.empty:
            continue
        idx_max = df_gov["taxa_desocupacao"].idxmax()
        idx_min = df_gov["taxa_desocupacao"].idxmin()
        caged_g = df_caged[df_caged["governo"] == caged_gov]
        meses_caged = int(caged_g["meses"].sum())
        saldo = int(caged_g["saldo_postos_formais"].sum())
        with col:
            st.markdown(
                '<div class="kpi-card">'
                f'<h4 style="color: {cor}; margin-bottom: 8px;">{nome}:</h4>'
                '<ul style="color: #e2e8f0; line-height: 1.7; margin-bottom: 0;">'
                f'<li>Desemprego médio (trimestres móveis): <b>{fmt_br(df_gov["taxa_desocupacao"].mean())}%</b></li>'
                f'<li>Primeiro dado ({df_gov["periodo"].iloc[0]}): <b>{fmt_br(df_gov["taxa_desocupacao"].iloc[0])}%</b></li>'
                f'<li>Máxima: <b>{fmt_br(df_gov.loc[idx_max, "taxa_desocupacao"])}%</b> ({df_gov.loc[idx_max, "periodo"]})</li>'
                f'<li>Mínima: <b>{fmt_br(df_gov.loc[idx_min, "taxa_desocupacao"])}%</b> ({df_gov.loc[idx_min, "periodo"]})</li>'
                f'<li>Último dado ({df_gov["periodo"].iloc[-1]}): <b>{fmt_br(df_gov["taxa_desocupacao"].iloc[-1])}%</b></li>'
                f'<li>Rendimento real: <b>R$ {fmt_br(df_gov["rendimento_medio_real"].iloc[0], 0)} ➔ R$ {fmt_br(df_gov["rendimento_medio_real"].iloc[-1], 0)}</b></li>'
                f'<li>Saldo CAGED: <b>+{fmt_br(saldo, 0)} vagas</b> em {meses_caged} meses (~{fmt_br(saldo / meses_caged / 1000, 1)} mil/mês)</li>'
                '</ul></div>',
                unsafe_allow_html=True
            )
    st.caption("Valores de rendimento a preços do último mês disponível (deflacionados pelo IBGE). A série da PNAD na base começa em jul–set/2018.")
