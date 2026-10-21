import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_ppm_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_livestock():
    st.markdown('<div class="section-title">🐄 Pecuária Municipal: PPM (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Análise dos rebanhos brasileiros e produção de produtos de origem animal da Pesquisa da Pecuária Municipal (PPM - IBGE).</div>',
        unsafe_allow_html=True
    )

    df_efetivos, df_produtos = get_ppm_data()

    if df_efetivos.empty:
        st.warning("Dados da PPM não encontrados.")
        return

    # 1. Efetivo dos Rebanhos
    st.subheader("1. Efetivo dos Rebanhos Brasileiros (Cabeças)")
    st.caption("Evolução dos rebanhos bovino, suíno e galináceo segundo o IBGE.")

    tipos_rebanho = sorted(list(df_efetivos["tipo_rebanho"].unique()))
    rebanho_sel = st.selectbox("Selecione o Tipo de Rebanho:", tipos_rebanho, index=0)

    df_reb_filtered = df_efetivos[df_efetivos["tipo_rebanho"] == rebanho_sel].sort_values("ano")

    if not df_reb_filtered.empty:
        colors_reb = [
            COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else (COLOR_LULA if g == "Lula (2023-atual)" else "#64748b")
            for g in df_reb_filtered["governo"]
        ]
        
        div = 1e6
        unit_str = "Milhões de Cabeças"

        fig_reb = go.Figure()
        fig_reb.add_trace(go.Bar(
            x=df_reb_filtered["ano"].astype(str),
            y=df_reb_filtered["cabecas"] / div,
            marker_color=colors_reb,
            text=(df_reb_filtered["cabecas"] / div).apply(lambda v: f"{v:.1f} mi"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate=f"<b>Ano:</b> %{{x}}<br><b>Efetivo:</b> %{{y:.2f}} {unit_str}<extra></extra>"
        ))
        apply_plotly_theme(fig_reb, title=f"Efetivo de {rebanho_sel} ({unit_str})")
        st.plotly_chart(fig_reb, use_container_width=True)

    st.markdown("---")

    # 2. Produtos de Origem Animal
    st.subheader("2. Produção de Origem Animal (Leite, Ovos, Mel)")
    st.caption("Volumes e valores apurados anualmente pelo IBGE.")

    if not df_produtos.empty:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            prods = sorted(list(df_produtos["produto"].unique()))
            prod_sel = st.selectbox("Selecione o Produto:", prods, index=0)
        with col_p2:
            vars_prod = sorted(list(df_produtos["variavel"].unique()))
            var_prod_sel = st.selectbox("Selecione a Métrica:", vars_prod, index=0)

        df_prod_filt = df_produtos[(df_produtos["produto"] == prod_sel) & (df_produtos["variavel"] == var_prod_sel)].sort_values("ano")

        if not df_prod_filt.empty:
            colors_prod = [
                COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else (COLOR_LULA if g == "Lula (2023-atual)" else "#64748b")
                for g in df_prod_filt["governo"]
            ]
            unit_p = df_prod_filt["unidade"].iloc[0]

            fig_p = go.Figure()
            fig_p.add_trace(go.Bar(
                x=df_prod_filt["ano"].astype(str),
                y=df_prod_filt["valor"],
                marker_color=colors_prod,
                text=df_prod_filt["valor"].apply(lambda v: f"{v:,.0f}"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate=f"<b>Ano:</b> %{{x}}<br><b>Valor:</b> %{{y:,.1f}} {unit_p}<extra></extra>"
            ))
            apply_plotly_theme(fig_p, title=f"{prod_sel} — {var_prod_sel} ({unit_p})")
            st.plotly_chart(fig_p, use_container_width=True)

    # Box Explicativo da Pecuária
    st.markdown("""
    <div class="info-box">
      <b>🐄 Dinâmica da Pecuária Brasileira:</b><br/>
      • <b>Rebanho Bovino Recorde:</b> O rebanho bovino nacional superou 234 milhões de cabeças (mais de 1 boi por habitante), impulsionado pelo ciclo do gado e investimentos em confinamento e genética.<br/>
      • <b>Ciclo da Pecuária:</b> Em 2021/2022, os altos preços da arroba incentivaram a retenção de fêmeas; em 2023/2024, a fase de descarte de fêmeas aumentou a oferta de carne bovina, barateando os cortes ao consumidor no IPCA.<br/>
      • <b>Avicultura e Suinocultura:</b> O Brasil ampliou a liderança global como maior exportador de carne de frango do planeta e 4º maior em carne suína.
    </div>
    """, unsafe_allow_html=True)
