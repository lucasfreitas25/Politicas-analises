import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_seguranca_data, load_json
from modules.ui_components import (
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD,
    render_compare_stat,
    fmt_br,
    render_source
)

def render_tab_security():
    st.markdown('<div class="section-title">🛡️ Segurança Pública & Criminalidade</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Mortes Violentas Intencionais (MVI - Fórum Brasileiro de Segurança Pública e Ministério da Justiça), registros de armas (CACs), feminicídios e apreensões.</div>',
        unsafe_allow_html=True
    )

    df_mvi, df_armas, destaques = get_seguranca_data()

    # 1. Cards de Destaque (fim do governo Bolsonaro x dado mais recente)
    if not df_mvi.empty:
        b = df_mvi[df_mvi["governo"] == "Bolsonaro"].iloc[-1]
        l = df_mvi[df_mvi["governo"] == "Lula"].iloc[-1]
        col1, col2, col3 = st.columns(3)
        with col1:
            render_compare_stat("Taxa de mortes violentas (por 100 mil)", fmt_br(b["taxa_mvi_100k"]), fmt_br(l["taxa_mvi_100k"]),
                                f"{b['ano']} ➔ {l['ano']} · menor taxa desde 2012", better="lula")
        with col2:
            render_compare_stat("Mortes violentas intencionais (total)", fmt_br(b["total_mvi"], 0), fmt_br(l["total_mvi"], 0),
                                f"{b['ano']} ➔ {l['ano']} · pico de 2017 passava de 60 mil", better="lula")
        with col3:
            render_compare_stat("Feminicídios registrados", fmt_br(b["feminicidios"], 0), fmt_br(l["feminicidios"], 0),
                                f"{b['ano']} ➔ {l['ano']} · recorde da série em {l['ano']}", better="bolsonaro")
        nota = load_json("seguranca.json").get("nota_metodologica")
        if nota:
            render_source(nota, "https://forumseguranca.org.br/anuario-brasileiro-seguranca-publica/")

    st.markdown("---")

    # 2. Gráfico de Mortes Violentas Intencionais
    st.subheader("1. Taxa de Mortes Violentas Intencionais por 100 mil habitantes (FBSP / MJSP)")
    st.caption("Indicador padronizado internacionalmente que engloba homicídios dolosos, latrocínios, lesões corporais seguidas de morte e mortes decorrentes de intervenção policial.")

    if not df_mvi.empty:
        colors_mvi = [
            COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
            for g in df_mvi["governo"]
        ]
        fig_mvi = go.Figure()
        fig_mvi.add_trace(go.Bar(
            x=df_mvi["ano"].astype(str),
            y=df_mvi["taxa_mvi_100k"],
            marker_color=colors_mvi,
            text=df_mvi["taxa_mvi_100k"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=12),
            hovertemplate="<b>Ano:</b> %{x}<br><b>Taxa MVI:</b> %{y:.1f} por 100k hab<extra></extra>"
        ))
        apply_plotly_theme(fig_mvi, title="Taxa Nacional de Mortes Violentas Intencionais (por 100 mil hab.)")
        st.plotly_chart(fig_mvi, use_container_width=True)

    # 3. Armas de Fogo e Feminicídio em duas colunas
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.subheader("Política de Armas (Acervo CACs)")
        st.caption("Número de registros ativos de Caçadores, Atiradores e Colecionadores (Exército Brasileiro / PF).")
        if not df_armas.empty:
            fig_armas = go.Figure()
            fig_armas.add_trace(go.Bar(
                x=df_armas["governo"],
                y=df_armas["registro_cacs"],
                marker_color=[COLOR_BOLSONARO, COLOR_LULA],
                text=df_armas["registro_cacs"].apply(lambda v: f"{v:,.0f}"),
                textposition="outside",
                textfont=dict(color="#ffffff", size=12)
            ))
            apply_plotly_theme(fig_armas, title="Registros Ativos de Armas CACs")
            st.plotly_chart(fig_armas, use_container_width=True)

    with col_s2:
        st.subheader("Feminicídios Registrados no Brasil")
        st.caption("Assassinatos de mulheres motivados por violência doméstica ou discriminação de gênero.")
        if not df_mvi.empty:
            fig_fem = go.Figure()
            fig_fem.add_trace(go.Scatter(
                x=df_mvi["ano"].astype(str),
                y=df_mvi["feminicidios"],
                mode="lines+markers+text",
                marker=dict(size=8, color="#fb7185"),
                line=dict(color="#f43f5e", width=3),
                text=df_mvi["feminicidios"],
                textposition="top center",
                textfont=dict(color="#ffffff", size=11),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Feminicídios:</b> %{y:,.0f}<extra></extra>"
            ))
            apply_plotly_theme(fig_fem, title="Casos Oficiais de Feminicídio (Anual)")
            st.plotly_chart(fig_fem, use_container_width=True)

    st.markdown("---")

    # 4. Box Analítico de Nuances em Segurança Pública
    b_dest = destaques.get("bolsonaro", {})
    l_dest = destaques.get("lula", {})

    st.subheader("🔍 Análise Imparcial das Diretrizes em Segurança")
    col_b, col_l = st.columns(2)
    with col_b:
        card_b = (
            '<div class="kpi-card">'
            '<h4 style="color: #93c5fd; margin-bottom: 10px;">Governo Bolsonaro (2019-2022):</h4>'
            '<ul style="color: #e2e8f0; line-height: 1.6; font-size: 0.88rem;">'
            '<li><b>Redução Histórica:</b> Consolidação da queda de homicídios após o pico de 2017, impulsionada pelo Sistema Único de Segurança Pública (SUSP) e transferência de líderes do crime organizado para presídios de segurança máxima.</li>'
            '<li><b>Acesso a Armas:</b> Edição de decretos flexibilizando calibres e porte para CACs, sob o argumento de legítima defesa e direito individual.</li>'
            '<li><b>Críticas Documentadas:</b> Aumento da circulação de armas que acabaram desviadas para facções, crescimento da letalidade policial em alguns estados e alta nos feminicídios na pandemia.</li>'
            '</ul>'
            '</div>'
        )
        st.markdown(card_b, unsafe_allow_html=True)
    with col_l:
        card_l = (
            '<div class="kpi-card">'
            '<h4 style="color: #fda4af; margin-bottom: 10px;">Governo Lula (2023-atual):</h4>'
            '<ul style="color: #e2e8f0; line-height: 1.6; font-size: 0.88rem;">'
            '<li><b>Menor taxa desde 2012:</b> 19,1 mortes violentas por 100 mil em 2025 (40.775 mortes, -8,2%); roubos de celular caíram 37,4% entre 2022 e 2025. Lei Antifacção (Lei 15.358/2026) endureceu penas.</li>'
            '<li><b>Desarmamento Controlado:</b> Revogação de decretos armamentistas, transferência do controle de armas para a Polícia Federal e endurecimento de calibres de uso restrito.</li>'
            '<li><b>Críticas Documentadas:</b> Recorde de feminicídios (1.571 em 2025) e de mortes por intervenção policial (6.602); crescimento do poderio financeiro de facções criminosas e milícias no Rio de Janeiro e na Bahia, infiltração do narcotráfico em crimes ambientais na Amazônia e lentidão na criação do Ministério da Segurança Pública autônomo.</li>'
            '</ul>'
            '</div>'
        )
        st.markdown(card_l, unsafe_allow_html=True)
