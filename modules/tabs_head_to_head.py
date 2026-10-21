import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_scorecard
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_head_to_head():
    st.markdown('<div class="section-title">⚖️ Comparador Direto Frente a Frente (Head-to-Head)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Escolha qualquer indicador oficial para confrontar diretamente os mandatos em valores absolutos, taxas de variação e contexto histórico.</div>',
        unsafe_allow_html=True
    )

    scorecard_data = get_scorecard()
    indicators = scorecard_data.get("indicadores", [])

    if not indicators:
        st.warning("Indicadores não encontrados.")
        return

    ind_names = [ind["indicador"] for ind in indicators]
    ind_sel_name = st.selectbox("Selecione o Indicador para Confronto Direto:", ind_names, index=0)

    selected_ind = next(item for item in indicators if item["indicador"] == ind_sel_name)
    if selected_ind["melhor"] == "empate":
        st.info("≈ Neste indicador a diferença é pequena ou depende de contexto — nenhum dos períodos foi marcado como melhor.")

    # Layout do confronto direto
    col_b, col_vs, col_l = st.columns([5, 2, 5])
    
    with col_b:
        badge_b = '<span class="badge-winner-bols" style="font-size: 0.85rem; padding: 5px 14px;">🏆 Vantagem Estatística</span>' if selected_ind['melhor'] == 'bolsonaro' else '<span style="color: #94a3b8; font-size: 0.8rem;">Resultado do Período</span>'
        card_b = (
            f'<div style="background: rgba(37, 99, 235, 0.16); border: 2px solid #3b82f6; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
            f'<h3 style="color: #93c5fd; margin-bottom: 4px; font-weight: 800;">Governo Bolsonaro</h3>'
            f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 12px;">(2019 — 2022)</p>'
            f'<div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; font-family: monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{selected_ind["bolsonaro"]}</div>'
            f'<div style="margin-top: 14px;">{badge_b}</div>'
            f'</div>'
        )
        st.markdown(card_b, unsafe_allow_html=True)

    with col_vs:
        card_vs = (
            '<div style="display: flex; align-items: center; justify-content: center; height: 100%; min-height: 140px; font-size: 2rem; font-weight: 900; color: #94a3b8; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">'
            'VS'
            '</div>'
        )
        st.markdown(card_vs, unsafe_allow_html=True)

    with col_l:
        badge_l = '<span class="badge-winner-lula" style="font-size: 0.85rem; padding: 5px 14px;">🏆 Vantagem Estatística</span>' if selected_ind['melhor'] == 'lula' else '<span style="color: #94a3b8; font-size: 0.8rem;">Resultado do Período</span>'
        card_l = (
            f'<div style="background: rgba(225, 29, 72, 0.16); border: 2px solid #f43f5e; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
            f'<h3 style="color: #fda4af; margin-bottom: 4px; font-weight: 800;">Governo Lula</h3>'
            f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 12px;">(2023 — atual)</p>'
            f'<div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; font-family: monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{selected_ind["lula"]}</div>'
            f'<div style="margin-top: 14px;">{badge_l}</div>'
            f'</div>'
        )
        st.markdown(card_l, unsafe_allow_html=True)

    st.markdown("---")

    # Gráfico de barras comparativo do indicador selecionado
    b_num = selected_ind.get("bolsonaro_num")
    l_num = selected_ind.get("lula_num")
    unidade = selected_ind.get("unidade", "")

    if b_num is not None and l_num is not None:
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=["Bolsonaro (2019-2022)", "Lula (2023-atual)"],
            y=[b_num, l_num],
            marker_color=[COLOR_BOLSONARO, COLOR_LULA],
            text=[selected_ind["bolsonaro"], selected_ind["lula"]],
            textposition="outside",
            textfont=dict(color="#ffffff", size=13, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate="<b>Governo:</b> %{x}<br><b>Valor:</b> %{y} " + unidade + "<extra></extra>"
        ))
        apply_plotly_theme(fig_comp, title=f"Confronto Numérico: {selected_ind['indicador']} ({unidade})")
        st.plotly_chart(fig_comp, use_container_width=True)

    # Detalhamento e Nota Explicativa
    st.markdown(f"""
    <div class="info-box">
      <b>📌 Análise Oficial e Contexto Histórico:</b><br/>
      {selected_ind['observacao']}<br/>
      <span style="font-size: 0.8rem;">📎 Fonte: <a href="{selected_ind.get('fonte_url', '#')}" target="_blank" style="color:#38bdf8;">{selected_ind.get('fonte', '—')}</a></span>
    </div>
    """, unsafe_allow_html=True)
