import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_macro_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD,
    COLOR_NEUTRAL,
    render_source
)

def render_tab_macro():
    st.markdown('<div class="section-title">Macroeconomia & Finanças Públicas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Produto Interno Bruto (IBGE Contas Nacionais), Balança Comercial (MDIC), Taxa Selic, Câmbio PTAX e Dívida Bruta (Banco Central).</div>',
        unsafe_allow_html=True
    )

    df_trim, df_anual, df_ind = get_macro_data()

    # 1. PIB Anual (% Crescimento Real)
    st.subheader("1. Crescimento Anual do PIB (%) — IBGE Contas Nacionais")
    st.caption("Variação percentual do volume do PIB a preços de mercado.")

    if not df_anual.empty:
        colors_pib = [
            COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
            for g in df_anual["governo"]
        ]

        fig_pib = go.Figure()
        fig_pib.add_trace(go.Bar(
            x=[f"{r.ano}*" if getattr(r, "parcial", False) else str(r.ano) for r in df_anual.itertuples()],
            y=df_anual["crescimento_pib_pct"],
            marker_color=colors_pib,
            text=df_anual["crescimento_pib_pct"].apply(lambda v: f"{v:+.1f}%"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate="<b>Ano:</b> %{x}<br><b>Crescimento:</b> %{y:+.1f}%<br><b>Governo:</b> %{customdata}<extra></extra>",
            customdata=df_anual["governo"]
        ))
        apply_plotly_theme(fig_pib, title="Crescimento Real do PIB Anual (%)")
        st.plotly_chart(fig_pib, width="stretch")
        render_source("IBGE — Contas Nacionais (SIDRA 6784; * = acumulado em 4 trimestres, ano em curso)", "https://sidra.ibge.gov.br/tabela/5932")

    # 2. Balança Comercial & Superávit
    st.subheader("2. Saldo da Balança Comercial Brasileira (US$ Bilhões)")
    st.caption("Superávit comercial anual registrado pelo Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC / ComexStat).")

    df_bal = df_ind.dropna(subset=["balanca_comercial_saldo_bi_usd"]) if not df_ind.empty else df_ind
    if not df_bal.empty:
        colors_bal = [
            COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
            for g in df_bal["governo"]
        ]

        fig_bal = go.Figure()
        fig_bal.add_trace(go.Bar(
            x=df_bal["ano"].astype(str),
            y=df_bal["balanca_comercial_saldo_bi_usd"],
            marker_color=colors_bal,
            text=df_bal["balanca_comercial_saldo_bi_usd"].apply(lambda v: f"US$ {v:.1f} bi"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate="<b>Ano:</b> %{x}<br><b>Saldo Comercial:</b> US$ %{y:.1f} bilhões<extra></extra>"
        ))
        apply_plotly_theme(fig_bal, title="Saldo Anual da Balança Comercial (US$ Bilhões)")
        st.plotly_chart(fig_bal, width="stretch")
        render_source("MDIC/Secex — ComexStat (2026 omitido: ano em curso)", "https://comexstat.mdic.gov.br/pt/geral")

    # 3. Selic e Câmbio Dólar em duas colunas
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.subheader("Taxa Selic Média (% a.a.)")
        if not df_ind.empty:
            fig_selic = go.Figure()
            fig_selic.add_trace(go.Scatter(
                x=df_ind["ano"].astype(str),
                y=df_ind["selic_media"],
                mode="lines+markers+text",
                marker=dict(size=8, color="#fbbf24"),
                line=dict(color="#f59e0b", width=3),
                text=df_ind["selic_media"].apply(lambda v: f"{v:.1f}%"),
                textposition="top center",
                textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Selic Média:</b> %{y:.2f}%<extra></extra>"
            ))
            apply_plotly_theme(fig_selic, title="Taxa Selic Média Anual (% a.a.)")
            st.plotly_chart(fig_selic, width="stretch")

    with col_m2:
        st.subheader("Dólar PTAX Médio (R$/US$)")
        if not df_ind.empty:
            fig_dol = go.Figure()
            fig_dol.add_trace(go.Scatter(
                x=df_ind["ano"].astype(str),
                y=df_ind["dolar_medio"],
                mode="lines+markers+text",
                marker=dict(size=8, color="#38bdf8"),
                line=dict(color="#0284c7", width=3),
                text=df_ind["dolar_medio"].apply(lambda v: f"R$ {v:.2f}"),
                textposition="top center",
                textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Câmbio Médio:</b> R$ %{y:.2f}<extra></extra>"
            ))
            apply_plotly_theme(fig_dol, title="Taxa de Câmbio Média (R$ por US$)")
            st.plotly_chart(fig_dol, width="stretch")

    # 4. Dívida Pública Bruta / PIB
    st.subheader("3. Dívida Bruta do Governo Geral (% do PIB)")
    st.caption("Endividamento público apurado pelo Banco Central do Brasil segundo metodologia oficial.")

    if not df_ind.empty:
        colors_div = [
            COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
            for g in df_ind["governo"]
        ]

        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            x=df_ind["ano"].astype(str),
            y=df_ind["divida_bruta_pib_pct"],
            marker_color=colors_div,
            text=df_ind["divida_bruta_pib_pct"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate="<b>Ano:</b> %{x}<br><b>Dívida/PIB:</b> %{y:.1f}%<extra></extra>"
        ))
        apply_plotly_theme(fig_div, title="Dívida Bruta do Governo Geral (% PIB)")
        fig_div.update_xaxes(ticktext=[f"{r.ano}*" if getattr(r, "parcial", False) else str(r.ano) for r in df_ind.itertuples()],
                             tickvals=df_ind["ano"].astype(str))
        st.plotly_chart(fig_div, width="stretch")
        render_source("Banco Central — SGS 13762, posição de dezembro (* = último mês disponível). Selic: SGS 432; câmbio: SGS 1.", "https://www3.bcb.gov.br/sgspub/")

    # Box Explicativo Macroeconômico
    st.markdown("""
    <div class="info-box">
      <b>Equilíbrio Macroeconômico e Fiscal:</b><br/>
      • <b>Desempenho do PIB:</b> Bolsonaro teve média de 1,5% ao ano, puxada para baixo pela pandemia (2020: -3,3%) e compensada pela reabertura (2021: +4,8%). Lula teve média de 3,0% em 2023–2025 (3,2%, 3,4% e 2,3%), com desaceleração em 2025–26 sob juros altos.<br/>
      • <b>Juros:</b> a Selic foi da mínima histórica de 2,00% (2020–21) a 13,75% (fim de 2022). Com Lula, subiu até 15,00% em junho de 2025 — maior nível desde 2006 — e voltou a 13,75% em 2026.<br/>
      • <b>Setor Externo:</b> em 2023 o superávit comercial bateu o recorde de US$ 98,9 bilhões; em 2025, US$ 68,3 bilhões, com exportações recordes apesar do tarifaço dos EUA.<br/>
      • <b>Trajetória Fiscal:</b> a dívida bruta caiu ao fim de 2022 pelo efeito da inflação alta sobre o PIB nominal e por receitas extraordinárias; voltou a subir a partir de 2023 com déficits primários e juros elevados, chegando a 82,9% do PIB em agosto de 2026.
    </div>
    """, unsafe_allow_html=True)
