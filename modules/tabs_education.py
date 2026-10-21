import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_educacao_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_education():
    st.markdown('<div class="section-title">🎓 Educação & Capital Humano</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Avaliação do IDEB (Inep), taxa de analfabetismo (IBGE PNAD Contínua), orçamento federal executado pelo MEC e programas estruturais (Novo Fundeb, Pé-de-Meia).</div>',
        unsafe_allow_html=True
    )

    df_ideb, df_analf, df_orc, programas = get_educacao_data()

    # 1. Cards de Destaque
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="kpi-card" style="text-align: center;">
          <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">IDEB Ensino Médio (Inep)</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff; font-family: monospace; margin: 8px 0;">4,2 ➔ 4,3</div>
          <div style="font-size: 0.75rem; color: #38bdf8;">Bolsonaro (2021): 4,2 | Lula (2023): 4,3</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card" style="text-align: center;">
          <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Taxa de Analfabetismo (15+ anos)</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: #34d399; font-family: monospace; margin: 8px 0;">5,6% ➔ 4,9%</div>
          <div style="font-size: 0.75rem; color: #94a3b8;">2022 ➔ 2025 · IBGE PNAD Contínua (SIDRA 7113)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card" style="text-align: center;">
          <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Orçamento Pago MEC (Executado)</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: #93c5fd; font-family: monospace; margin: 8px 0;">R$ 121 bi ➔ R$ 158 bi</div>
          <div style="font-size: 0.75rem; color: #94a3b8;">Bolsonaro (2022) vs Lula (2024)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Gráfico do IDEB
    st.subheader("1. Evolução do IDEB por Etapa de Ensino (Inep / MEC)")
    st.caption("Índice de Desenvolvimento da Educação Básica (escala de 0 a 10).")

    if not df_ideb.empty:
        fig_ideb = go.Figure()
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["anos_iniciais"],
            name="Anos Iniciais (1º ao 5º ano)",
            marker_color="#38bdf8",
            text=df_ideb["anos_iniciais"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["anos_finais"],
            name="Anos Finais (6º ao 9º ano)",
            marker_color="#10b981",
            text=df_ideb["anos_finais"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["ensino_medio"],
            name="Ensino Médio",
            marker_color="#f59e0b",
            text=df_ideb["ensino_medio"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.update_layout(barmode="group")
        apply_plotly_theme(fig_ideb, title="IDEB Nacional por Ciclo de Ensino")
        st.plotly_chart(fig_ideb, use_container_width=True)

    # 3. Analfabetismo e Orçamento em duas colunas
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("Taxa de Analfabetismo (%) — IBGE")
        st.caption("Pessoas de 15 anos ou mais de idade que não sabem ler e escrever.")
        if not df_analf.empty:
            colors_analf = [
                COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
                for g in df_analf["governo"]
            ]
            fig_analf = go.Figure()
            fig_analf.add_trace(go.Scatter(
                x=df_analf["ano"].astype(str),
                y=df_analf["taxa_analfabetismo_15mais"],
                mode="lines+markers+text",
                marker=dict(size=8, color="#34d399"),
                line=dict(color="#10b981", width=3),
                text=df_analf["taxa_analfabetismo_15mais"].apply(lambda v: f"{v:.1f}%"),
                textposition="top center",
                textfont=dict(color="#ffffff", size=11),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Analfabetismo:</b> %{y:.1f}%<extra></extra>"
            ))
            apply_plotly_theme(fig_analf, title="Taxa de Analfabetismo Nacional (%)")
            st.plotly_chart(fig_analf, use_container_width=True)

    with col_e2:
        st.subheader("Orçamento Executado do MEC (R$ bi)")
        st.caption("Volume financeiro total pago pelo Ministério da Educação.")
        if not df_orc.empty:
            colors_orc = [
                COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
                for g in df_orc["governo"]
            ]
            fig_orc = go.Figure()
            fig_orc.add_trace(go.Bar(
                x=df_orc["ano"].astype(str),
                y=df_orc["orcamento_pago"],
                marker_color=colors_orc,
                text=df_orc["orcamento_pago"].apply(lambda v: f"R$ {v:.1f} bi"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=11),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Orçamento Pago:</b> R$ %{y:.1f} bilhões<extra></extra>"
            ))
            apply_plotly_theme(fig_orc, title="Orçamento Anual Pago do MEC (R$ Bilhões)")
            st.plotly_chart(fig_orc, use_container_width=True)

    st.markdown("---")

    # 4. Programas Estruturantes de Impacto
    st.subheader("📋 Principais Políticas Educacionais de Cada Mandato")
    for prog in programas:
        tag_color = "#3b82f6" if prog["governo"] == "Bolsonaro" else "#f43f5e"
        card_prog = (
            f'<div class="kpi-card" style="margin-bottom: 16px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
            f'<h4 style="color: #ffffff; margin: 0;">{prog["programa"]}</h4>'
            f'<span style="background: {tag_color}; color: #ffffff; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">'
            f'Governo {prog["governo"]}'
            f'</span>'
            f'</div>'
            f'<p style="color: #cbd5e1; font-size: 0.88rem; margin-bottom: 10px;">{prog["descricao"]}</p>'
            f'<div style="background: rgba(16, 185, 129, 0.12); border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">'
            f'<b style="color: #34d399;">Impacto Positivo:</b> <span style="color: #e2e8f0; font-size: 0.85rem;">{prog["pontos_positivos"]}</span>'
            f'</div>'
            f'<div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px;">'
            f'<b style="color: #f87171;">Desafios / Críticas Oficiais:</b> <span style="color: #e2e8f0; font-size: 0.85rem;">{prog["criticas"]}</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_prog, unsafe_allow_html=True)
