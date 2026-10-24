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

    from modules.historico_ui import filtro_tipo_padrao
    st.subheader("1. Silvicultura (florestas plantadas)")
    st.caption("Florestas cultivadas (eucalipto e pinus) para papel, celulose, carvão vegetal e madeira industrial. Escolha o produto e a medida.")
    filtro_tipo_padrao("pevs_silvicultura")

    st.markdown("---")
    st.subheader("2. Extração vegetal nativa")
    st.caption("Produtos da floresta nativa, como açaí, castanha, babaçu, erva-mate e madeira em tora.")
    filtro_tipo_padrao("pevs_extracao")

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
