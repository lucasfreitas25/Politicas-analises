import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_pevs_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_forestry():
    st.markdown('<div class="section-title">Silvicultura & Extrativismo: PEVS (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Dados oficiais da Produção da Extração Vegetal e da Silvicultura (PEVS - IBGE), destacando celulose, papel, carvão e produtos nativos.</div>',
        unsafe_allow_html=True
    )
    from modules.historico_ui import cards_padrao
    cards_padrao("silvicultura")

    df_silv, df_extr = get_pevs_data()

    if df_silv.empty and df_extr.empty:
        st.warning("Dados da PEVS não encontrados.")
        return

    # 1. Silvicultura (Florestas Plantadas)
    st.subheader("1. Valor da Produção da Silvicultura (R$ Milhões)")
    st.caption("Florestas cultivadas (eucalipto e pinus) para papel, celulose, carvão vegetal e madeira industrial.")

    if not df_silv.empty:
        produtos_silv = sorted(list(df_silv["produto"].unique()))
        silv_sel = st.selectbox("Selecione o Produto da Silvicultura:", produtos_silv, index=0)

        df_s_filt = df_silv[df_silv["produto"] == silv_sel].sort_values("ano")

        if not df_s_filt.empty:
            colors_s = [
                COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else (COLOR_LULA if g == "Lula (2023-atual)" else "#64748b")
                for g in df_s_filt["governo"]
            ]

            fig_s = go.Figure()
            fig_s.add_trace(go.Bar(
                x=df_s_filt["ano"].astype(str),
                y=df_s_filt["valor_producao_mil_reais"] / 1000.0,
                marker_color=colors_s,
                text=(df_s_filt["valor_producao_mil_reais"] / 1000.0).apply(lambda v: f"R$ {v:,.0f} mi"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Valor:</b> R$ %{y:,.1f} milhões<extra></extra>"
            ))
            apply_plotly_theme(fig_s, title=f"Silvicultura: {silv_sel} (R$ Milhões)")
            st.plotly_chart(fig_s, width="stretch")

    st.markdown("---")

    # 2. Extração Vegetal (Produtos Florestais Nativos)
    st.subheader("2. Valor da Produção na Extração Vegetal Nativa (R$ Milhões)")
    st.caption("Coleta extrativista sustentável e nativa (Açaí, Castanha-do-Pará, Erva-Mate e outros).")

    if not df_extr.empty:
        produtos_extr = sorted(list(df_extr["produto"].unique()))
        extr_sel = st.selectbox("Selecione o Produto Extrativo:", produtos_extr, index=0)

        df_e_filt = df_extr[df_extr["produto"] == extr_sel].sort_values("ano")

        if not df_e_filt.empty:
            colors_e = [
                COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else (COLOR_LULA if g == "Lula (2023-atual)" else "#64748b")
                for g in df_e_filt["governo"]
            ]

            fig_e = go.Figure()
            fig_e.add_trace(go.Bar(
                x=df_e_filt["ano"].astype(str),
                y=df_e_filt["valor_producao_mil_reais"] / 1000.0,
                marker_color=colors_e,
                text=(df_e_filt["valor_producao_mil_reais"] / 1000.0).apply(lambda v: f"R$ {v:,.0f} mi"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Valor:</b> R$ %{y:,.1f} milhões<extra></extra>"
            ))
            apply_plotly_theme(fig_e, title=f"Extração Vegetal: {extr_sel} (R$ Milhões)")
            st.plotly_chart(fig_e, width="stretch")

    # Box Explicativo da PEVS
    def _total(df, ano):
        return float(df[(df["ano"] == ano) & (df["produto"] == "Total")]["valor_producao_mil_reais"].sum())
    ult = int(max(df_silv["ano"].max(), df_extr["ano"].max()))
    s24, e24, s18, e18 = _total(df_silv, ult), _total(df_extr, ult), _total(df_silv, 2019), _total(df_extr, 2019)
    share_silv = f"{100 * s24 / (s24 + e24):.0f}".replace(".", ",") if s24 + e24 else "—"
    share_silv_18 = f"{100 * s18 / (s18 + e18):.0f}".replace(".", ",") if s18 + e18 else "—"
    silv_bi = f"{s24 / 1e6:.1f}".replace(".", ",")
    extr_bi = f"{e24 / 1e6:.1f}".replace(".", ",")
    st.markdown(f"""
    <div class="info-box">
      <b>Silvicultura e extrativismo:</b><br/>
      • <b>Silvicultura em alta:</b> as florestas plantadas responderam por {share_silv}% do valor da produção florestal em {ult} (R$ {silv_bi} bi), contra {share_silv_18}% em 2019 (PEVS/IBGE).<br/>
      • <b>Extrativismo:</b> a extração vegetal nativa somou R$ {extr_bi} bi em {ult} (PEVS/IBGE).
    </div>
    """, unsafe_allow_html=True)
