import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_ipca_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD,
    COLOR_NEUTRAL
)

def render_tab_inflation():
    st.markdown('<div class="section-title">Inflação e Preços: IPCA (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Acompanhamento oficial do Índice Nacional de Preços ao Consumidor Amplo (IPCA), metas do CMN, trajetória acumulada nos mandatos e decomposição setorial por grupos de consumo.</div>',
        unsafe_allow_html=True
    )

    df_hist, df_grupos, resumo = get_ipca_data()

    if df_hist.empty:
        st.warning("Dados do IPCA não encontrados.")
        return

    # 1. Cartões "antes ➔ depois", no mesmo visual das outras abas
    b_res = resumo.get("Bolsonaro", {})
    l_res = resumo.get("Lula", {})
    from modules.ui_components import render_compare_stat, fmt_br
    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    c1, c2, c3 = st.columns(3)
    pares = (
        (c1, "IPCA acumulado no mandato", "acumulado_total_pct", f"Bolsonaro: 48 meses · Lula: {l_res.get('meses', '')} meses"),
        (c2, "Média anualizada do IPCA", "media_anual_pct", "Inflação média por ano de mandato · menor é melhor"),
        (c3, "Pico da inflação em 12 meses", "maior_12m_pct", f"Bolsonaro: {b_res.get('maior_12m_mes', '')} · Lula: {l_res.get('maior_12m_mes', '')}"),
    )
    for col, titulo, campo, nota in pares:
        vb, vl = _num(b_res.get(campo)), _num(l_res.get(campo))
        melhor = None if vb is None or vl is None or vb == vl else ("bolsonaro" if vb < vl else "lula")
        with col:
            render_compare_stat(titulo, f"{fmt_br(vb, 2)}%" if vb is not None else "Sem dado", f"{fmt_br(vl, 2)}%" if vl is not None else "Sem dado", nota, better=melhor)

    st.markdown("---")

    # 2. Curva Comparativa da Inflação Acumulada no Mandato (Mês 1 ao Mês 48)
    st.subheader("1. Inflação Acumulada no Mandato (Mês a Mês)")
    st.caption("Evolução do percentual acumulado de inflação a partir do 1º mês de cada governo (Base 0%).")

    df_bols = df_hist[df_hist["governo"] == "Bolsonaro (2019-2022)"].copy().reset_index(drop=True)
    df_lula = df_hist[df_hist["governo"] == "Lula (2023-atual)"].copy().reset_index(drop=True)
    
    df_bols["mes_mandato"] = df_bols.index + 1
    df_lula["mes_mandato"] = df_lula.index + 1

    fig_acum = go.Figure()
    fig_acum.add_trace(go.Scatter(
        x=df_bols["mes_mandato"],
        y=df_bols["indice_acumulado_mandato"],
        mode="lines+markers",
        name="Governo Bolsonaro (2019-2022)",
        line=dict(color=COLOR_BOLSONARO, width=3.5),
        marker=dict(size=5, color=COLOR_BOLSONARO),
        hovertemplate="<b>Mês:</b> %{x} de mandato<br><b>Acumulado:</b> %{y:.2f}%<extra>Bolsonaro</extra>"
    ))
    fig_acum.add_trace(go.Scatter(
        x=df_lula["mes_mandato"],
        y=df_lula["indice_acumulado_mandato"],
        mode="lines+markers",
        name="Governo Lula (2023-atual)",
        line=dict(color=COLOR_LULA, width=3.5),
        marker=dict(size=5, color=COLOR_LULA),
        hovertemplate="<b>Mês:</b> %{x} de mandato<br><b>Acumulado:</b> %{y:.2f}%<extra>Lula</extra>"
    ))

    fig_acum.update_xaxes(title_text="Mês de Mandato (1 = Janeiro do 1º ano)", dtick=5)
    fig_acum.update_yaxes(title_text="Inflação Acumulada (%)")
    apply_plotly_theme(fig_acum, title="Trajetória da Inflação Acumulada no Mandato (%)")
    st.plotly_chart(fig_acum, width="stretch")

    # 3. IPCA Mensal e Histórico Completo
    st.subheader("2. Série Histórica Mensal do IPCA (%)")
    st.caption("Taxa de variação percentual mensal do IPCA oficial.")

    df_plot_hist = df_hist[df_hist["ano"] >= 2019].copy()
    
    colors_bars = [
        COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else COLOR_LULA
        for g in df_plot_hist["governo"]
    ]

    fig_bars = go.Figure()
    fig_bars.add_trace(go.Bar(
        x=df_plot_hist["mes_ano"],
        y=df_plot_hist["ipca_mensal"],
        marker_color=colors_bars,
        hovertemplate="<b>Mês/Ano:</b> %{x}<br><b>IPCA:</b> %{y:.2f}%<extra></extra>"
    ))
    fig_bars.update_xaxes(nticks=14, tickangle=-45)
    apply_plotly_theme(fig_bars, title="Variação Mensal do IPCA (%) — Cores por Governo")
    st.plotly_chart(fig_bars, width="stretch")

    # 4. Decomposição pelos 9 Grupos do IBGE
    st.subheader("3. Decomposição Setorial do IPCA (Grupos de Consumo)")
    st.caption("Comportamento dos 9 grandes grupos da cesta de consumo das famílias do IBGE.")

    if not df_grupos.empty:
        df_12m = df_grupos[df_grupos["variavel"] == "Acumulado 12M"]
        if not df_12m.empty:
            ult_periodo = df_12m["periodo"].iloc[-1]
            df_ult_grupos = df_12m[df_12m["periodo"] == ult_periodo].sort_values("valor", ascending=True)
            
            fig_grp = go.Figure()
            fig_grp.add_trace(go.Bar(
                y=df_ult_grupos["grupo"],
                x=df_ult_grupos["valor"],
                orientation="h",
                marker_color="#38bdf8",
                text=df_ult_grupos["valor"].apply(lambda v: f"{v:.2f}%"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate="<b>Grupo:</b> %{y}<br><b>Variação 12M:</b> %{x:.2f}%<extra></extra>"
            ))
            apply_plotly_theme(fig_grp, title=f"Inflação em 12 Meses por Grupo de Consumo ({ult_periodo})")
            st.plotly_chart(fig_grp, width="stretch")

    # Box Explicativo da Inflação
    st.markdown("""
    <div class="info-box">
      <b>Fatores Inflacionários Chave:</b><br/>
      • <b>Choques Globais (2020-2022):</b> A pandemia desarticulou cadeias logísticas de frete marítimo, microchips e insumos agrícolas (fertilizantes), somada ao início da Guerra na Ucrânia em 2022 que explodiu os preços de combustíveis e commodities alimentares (soja, trigo).<br/>
      • <b>Deflação do ICMS (2022):</b> Em meados de 2022, a aprovação do teto de ICMS sobre combustíveis e energia pelo Congresso Nacional provocou três meses de deflação artificial (-0,68% em jul, -0,36% em ago e -0,29% em set), desacelerando o IPCA anual daquele ano.<br/>
      • <b>2023 em diante:</b> o IPCA fechou 2023 em 4,62%, 2024 em 4,83% e 2025 em 4,26%, e acumulava 3,95% até setembro de 2026 (IBGE).
    </div>
    """, unsafe_allow_html=True)
