import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_pim_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_industry():
    st.markdown('<div class="section-title">🏭 Indústria: PIM-PF (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Desempenho da Produção Física Industrial brasileira segundo a Pesquisa Industrial Mensal (PIM-PF - IBGE).</div>',
        unsafe_allow_html=True
    )

    df_pim = get_pim_data()

    if df_pim.empty:
        st.warning("Dados da PIM-PF não encontrados.")
        return

    vars_disponiveis = df_pim["variavel"].unique()
    var_sel = st.selectbox("Selecione o Indicador Industrial:", vars_disponiveis, index=0)

    df_filtered = df_pim[df_pim["variavel"] == var_sel].copy()

    # 1. Gráfico da Indústria Geral ao Longo do Tempo
    st.subheader("1. Evolução Temporal da Produção Física Industrial")
    st.caption("Acompanhamento mensal com quebra por governo.")

    df_geral = df_filtered[df_filtered["atividade"].str.contains("geral", case=False, na=False)].copy()

    if not df_geral.empty:
        df_bols = df_geral[df_geral["governo"] == "Bolsonaro (2019-2022)"]
        df_lula = df_geral[df_geral["governo"] == "Lula (2023-atual)"]

        fig_pim = go.Figure()
        fig_pim.add_trace(go.Scatter(
            x=df_bols["periodo"],
            y=df_bols["valor"],
            mode="lines+markers",
            name="Bolsonaro (2019-2022)",
            line=dict(color=COLOR_BOLSONARO, width=3),
            marker=dict(size=4, color=COLOR_BOLSONARO),
            hovertemplate="<b>Período:</b> %{x}<br><b>Índice:</b> %{y:.2f}<extra>Bolsonaro</extra>"
        ))
        fig_pim.add_trace(go.Scatter(
            x=df_lula["periodo"],
            y=df_lula["valor"],
            mode="lines+markers",
            name="Lula (2023-atual)",
            line=dict(color=COLOR_LULA, width=3),
            marker=dict(size=4, color=COLOR_LULA),
            hovertemplate="<b>Período:</b> %{x}<br><b>Índice:</b> %{y:.2f}<extra>Lula</extra>"
        ))

        # Anotação de choque da pandemia
        if "abril 2020" in df_bols["periodo"].values:
            y_val = df_bols[df_bols["periodo"] == "abril 2020"]["valor"].values[0]
            fig_pim.add_annotation(
                text="Choque Covid-19 (Abr/20)",
                x="abril 2020",
                y=y_val,
                showarrow=True,
                arrowhead=2,
                arrowcolor="#f87171",
                font=dict(color="#ffffff", size=11),
                bgcolor="rgba(239, 68, 68, 0.85)",
                bordercolor="#b91c1c",
                borderwidth=1
            )

        fig_pim.update_xaxes(nticks=12, tickangle=-25)
        apply_plotly_theme(fig_pim, title=f"Produção da Indústria Geral — {var_sel}")
        st.plotly_chart(fig_pim, use_container_width=True)

    # 2. Comparativo Setorial: Transformação vs Extrativa
    st.subheader("2. Indústrias Extrativas vs. Indústrias de Transformação")
    st.caption("Comparação entre o setor de extração mineral/petrolífera e o parque manufatureiro fabril.")

    col_i1, col_i2 = st.columns(2)
    
    with col_i1:
        df_ext = df_filtered[df_filtered["atividade"].str.contains("extrativa", case=False, na=False)]
        if not df_ext.empty:
            media_b_ext = df_ext[df_ext["governo"] == "Bolsonaro (2019-2022)"]["valor"].mean()
            media_l_ext = df_ext[df_ext["governo"] == "Lula (2023-atual)"]["valor"].mean()
            
            fig_ext = go.Figure()
            fig_ext.add_trace(go.Bar(
                x=["Bolsonaro (2019-2022)", "Lula (2023-atual)"],
                y=[media_b_ext, media_l_ext],
                marker_color=[COLOR_BOLSONARO, COLOR_LULA],
                text=[f"{media_b_ext:.1f}", f"{media_l_ext:.1f}"],
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif")
            ))
            apply_plotly_theme(fig_ext, title="Média: Indústrias Extrativas (Petróleo/Minério)")
            st.plotly_chart(fig_ext, use_container_width=True)

    with col_i2:
        df_transf = df_filtered[df_filtered["atividade"].str.contains("transforma", case=False, na=False)]
        if not df_transf.empty:
            media_b_transf = df_transf[df_transf["governo"] == "Bolsonaro (2019-2022)"]["valor"].mean()
            media_l_transf = df_transf[df_transf["governo"] == "Lula (2023-atual)"]["valor"].mean()
            
            fig_transf = go.Figure()
            fig_transf.add_trace(go.Bar(
                x=["Bolsonaro (2019-2022)", "Lula (2023-atual)"],
                y=[media_b_transf, media_l_transf],
                marker_color=[COLOR_BOLSONARO, COLOR_LULA],
                text=[f"{media_b_transf:.1f}", f"{media_l_transf:.1f}"],
                textposition="outside",
                textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif")
            ))
            apply_plotly_theme(fig_transf, title="Média: Indústrias de Transformação (Manufatura)")
            st.plotly_chart(fig_transf, use_container_width=True)

    # Box Explicativo da Indústria
    st.markdown("""
    <div class="info-box">
      <b>🏭 Análise Estrutural da Indústria Nacional:</b><br/>
      • <b>Indústria Extrativa (Destaque Positivo):</b> Ambos os governos contaram com forte expansão da produção de petróleo na camada pré-sal (liderada pela Petrobras) e da produção de minério de ferro pela Vale, garantindo números robustos e superávit de divisas.<br/>
      • <b>Indústria de Transformação:</b> O setor manufatureiro enfrentou maiores desafios de produtividade e custo Brasil. Durante o governo Bolsonaro sofreu com paralisações em cadeias automotivas e escassez de componentes; no governo Lula vem ensaiando recuperação puxada por bens de consumo e incentivos setoriais (Nova Indústria Brasil - NIB).
    </div>
    """, unsafe_allow_html=True)
