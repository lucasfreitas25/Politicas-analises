import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_pam_data, get_conab_data
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_agro_conab():
    st.markdown('<div class="section-title">Agropecuária & Grãos: CONAB & PAM (IBGE)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Comparativo oficial da produção nacional de grãos pela Companhia Nacional de Abastecimento (CONAB) e da Produção Agrícola Municipal (PAM - IBGE).</div>',
        unsafe_allow_html=True
    )
    from modules.historico_ui import cards_padrao
    cards_padrao("agro")

    df_conab = get_conab_data()
    df_pam = get_pam_data()

    if df_conab.empty:
        st.warning("Dados da CONAB não encontrados.")
        return

    # 1. CONAB - Safras de Grãos
    st.subheader("1. Safras Brasileiras de Grãos (CONAB)")
    st.caption("Volume físico total colhido por ciclo agrícola (milhões de toneladas).")

    colors_conab = [COLOR_BOLSONARO if g == "Bolsonaro" else COLOR_LULA for g in df_conab["governo"]]

    fig_conab = go.Figure()
    fig_conab.add_trace(go.Bar(
        x=df_conab["safra"],
        y=df_conab["producao_total_milhoes_t"],
        marker_color=colors_conab,
        text=df_conab["producao_total_milhoes_t"].apply(lambda x: f"{x:.1f} Mt"),
        textposition="outside",
        textfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"),
        hovertemplate="<b>Safra:</b> %{x}<br><b>Produção Total:</b> %{y:.1f} milhões de toneladas<br><b>Governo:</b> %{customdata}<extra></extra>",
        customdata=df_conab["governo"]
    ))
    apply_plotly_theme(fig_conab, title="Evolução da Safra Brasileira de Grãos (Milhões de Toneladas - CONAB)")
    st.plotly_chart(fig_conab, width="stretch")

    # Detalhamento CONAB: Área e Produtividade
    col_cnb1, col_cnb2 = st.columns(2)
    with col_cnb1:
        st.subheader("Área Plantada (Milhões de ha)")
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=df_conab["safra"],
            y=df_conab["area_plantada_milhoes_ha"],
            mode="lines+markers",
            marker=dict(size=8, color="#34d399"),
            line=dict(color="#10b981", width=3),
            hovertemplate="<b>Safra:</b> %{x}<br><b>Área:</b> %{y:.1f} Mha<extra></extra>"
        ))
        apply_plotly_theme(fig_area, title="Área Plantada Total (Mha)")
        st.plotly_chart(fig_area, width="stretch")

    with col_cnb2:
        st.subheader("Produtividade Média (kg/ha)")
        fig_prod = go.Figure()
        fig_prod.add_trace(go.Scatter(
            x=df_conab["safra"],
            y=df_conab["produtividade_kg_ha"],
            mode="lines+markers",
            marker=dict(size=8, color="#fbbf24"),
            line=dict(color="#f59e0b", width=3),
            hovertemplate="<b>Safra:</b> %{x}<br><b>Produtividade:</b> %{y:,.0f} kg/ha<extra></extra>"
        ))
        apply_plotly_theme(fig_prod, title="Produtividade Média de Grãos (kg/ha)")
        st.plotly_chart(fig_prod, width="stretch")

    st.markdown("---")

    # 2. PAM - Produção Agrícola Municipal (IBGE)
    st.subheader("2. PAM: Produção Agrícola Municipal (IBGE)")
    st.caption("Evolução das principais culturas agrícolas temporárias e permanentes do Brasil.")

    if not df_pam.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            culturas = sorted(list(df_pam["cultura"].unique()))
            default_idx = 0
            for i, c in enumerate(culturas):
                if "soja" in c.lower():
                    default_idx = i
                    break
            cultura_sel = st.selectbox("Selecione a Cultura Agrícola:", culturas, index=default_idx)
        with col_f2:
            variaveis = sorted(list(df_pam["variavel"].unique()))
            var_sel = st.selectbox("Selecione a Variável:", variaveis, index=0)

        df_pam_filtered = df_pam[(df_pam["cultura"] == cultura_sel) & (df_pam["variavel"] == var_sel)].sort_values("ano")

        if not df_pam_filtered.empty:
            colors_pam = [
                COLOR_BOLSONARO if g == "Bolsonaro (2019-2022)" else (COLOR_LULA if g == "Lula (2023-atual)" else "#64748b")
                for g in df_pam_filtered["governo"]
            ]
            unit = df_pam_filtered["unidade"].iloc[0] if "unidade" in df_pam_filtered.columns else ""

            fig_pam = go.Figure()
            fig_pam.add_trace(go.Bar(
                x=df_pam_filtered["ano"].astype(str),
                y=df_pam_filtered["valor"],
                marker_color=colors_pam,
                text=df_pam_filtered["valor"].apply(lambda v: f"{v:,.0f}"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans, sans-serif"),
                hovertemplate=f"<b>Ano:</b> %{{x}}<br><b>{var_sel}:</b> %{{y:,.1f}} {unit}<extra></extra>"
            ))
            apply_plotly_theme(fig_pam, title=f"{cultura_sel} — {var_sel} ({unit})")
            st.plotly_chart(fig_pam, width="stretch")

    # Box Explicativo do Agro
    st.markdown("""
    <div class="info-box">
      <b>Destaques do Agronegócio Brasileiro:</b><br/>
      • <b>Marco das 300 Milhões de Toneladas:</b> O Brasil superou a barreira inédita de 300 milhões de toneladas de grãos na safra 2022/2023 (324,4 Mt, valor revisado), consolidando o país como o maior produtor e exportador mundial de soja, além de grande líder em milho e carnes.<br/>
      • <b>Choques Climáticos (El Niño 2023/24):</b> Na safra 2023/24, adversidades climáticas severas (estiagem prolongada no Centro-Oeste e excesso de chuvas/enchentes históricas no Rio Grande do Sul) provocaram uma quebra conjuntural pontual para 298,4 Mt.<br/>
      • <b>Novos recordes (2024/25 e 2025/26):</b> a CONAB fechou a safra 2024/25 em 350,2 Mt (12º levantamento, set/2025) e a 2025/26 em 361,7 Mt (set/2026), com recordes de soja e milho. Clima, tecnologia e preços internacionais explicam a maior parte do resultado.
    </div>
    """, unsafe_allow_html=True)
