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
    st.markdown('<div class="section-title">Pecuária Municipal: PPM (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Análise dos rebanhos brasileiros e produção de produtos de origem animal da Pesquisa da Pecuária Municipal (PPM - IBGE).</div>',
        unsafe_allow_html=True
    )
    from modules.historico_ui import cards_padrao
    cards_padrao("pecuaria")

    from modules.historico_ui import filtro_tipo_padrao
    st.subheader("1. Efetivo dos Rebanhos Brasileiros (Cabeças)")
    st.caption("Escolha o tipo de rebanho (bovino, suíno, galináceos, ovinos, caprinos, equinos, bubalinos e outros); o período pode ser recortado no deslizante.")
    if not filtro_tipo_padrao("ppm_rebanhos"):
        st.warning("Dados da PPM não encontrados.")
        return

    st.markdown("---")
    st.subheader("2. Produção de Origem Animal (Leite, Ovos, Mel e outros)")
    st.caption("Quantidade e valor da produção, apurados anualmente pelo IBGE.")
    filtro_tipo_padrao("ppm_origem")

    # Box Explicativo da Pecuária
    st.markdown("""
    <div class="info-box">
      <b>Dinâmica da Pecuária Brasileira:</b><br/>
      • <b>Rebanho Bovino Recorde:</b> O rebanho bovino nacional superou 234 milhões de cabeças (mais de 1 boi por habitante), impulsionado pelo ciclo do gado e investimentos em confinamento e genética.<br/>
      • <b>Ciclo da Pecuária:</b> Em 2021/2022, os altos preços da arroba incentivaram a retenção de fêmeas; em 2023/2024, a fase de descarte de fêmeas aumentou a oferta de carne bovina, barateando os cortes ao consumidor no IPCA.<br/>
      • <b>Avicultura e Suinocultura:</b> O Brasil ampliou a liderança global como maior exportador de carne de frango do planeta e 4º maior em carne suína.
    </div>
    """, unsafe_allow_html=True)
