import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_sociais_ambientais_data, get_politicas_data
from modules.tabs_policy_balance import render_policy_card
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
)


def _media(serie, gov, campo):
    vals = [p[campo] for p in serie if p["governo"] == gov and p.get(campo) is not None and not p.get("estimativa")]
    return sum(vals) / len(vals) if vals else None


def _card_evolucao(titulo, antes, depois, nota):
    """Cartão de evolução dentro de um mesmo governo (sem colunas Bolsonaro x Lula)."""
    st.markdown(
        f'<div class="kpi-card compare-stat" style="border-top:3px solid #EF2B2D;"><div class="compare-title">{titulo}</div>'
        f'<div class="compare-values"><span class="compare-val" style="color:#fca5a5 !important;">{antes}</span>'
        f'<span style="color:#64748b;"> ➔ </span><span class="compare-val" style="color:#fca5a5 !important;">{depois}</span></div>'
        f'<div class="compare-foot">{nota}</div></div>', unsafe_allow_html=True)


def render_tab_environment():
    render_section_header(
        "Meio Ambiente & Clima",
        "Desmatamento na Amazônia e no Cerrado (Inpe/PRODES), queimadas (Inpe), emissões de gases de efeito estufa (SEEG), "
        "terras indígenas e as principais políticas ambientais de cada governo.",
    )

    extras = get_sociais_ambientais_data()
    amz = extras.get("desmatamento_prodes", {})
    cer = extras.get("desmatamento_cerrado", {})
    fogo = extras.get("queimadas", {})
    emis = extras.get("emissoes", {})

    # ---------------- Cartões
    c1, c2, c3 = st.columns(3)
    if amz:
        with c1:
            render_compare_stat("Desmatamento Amazônia (média anual, km²)", fmt_br(_media(amz["serie"], "Bolsonaro", "km2"), 0),
                                fmt_br(_media(amz["serie"], "Lula", "km2"), 0), "PRODES 2019–22 x 2023–25", better="lula")
    if cer:
        with c2:
            render_compare_stat("Desmatamento Cerrado (média anual, km²)", fmt_br(_media(cer["serie"], "Bolsonaro", "km2"), 0),
                                fmt_br(_media(cer["serie"], "Lula", "km2"), 0), "PRODES Cerrado 2019–22 x 2023–25 · pico em 2023",
                                better="bolsonaro")
    if emis:
        s = emis["serie"]
        with c3:
            _card_evolucao("Emissões brutas, dentro do governo Lula (GtCO2e)", f"{fmt_br(s[0]['brutas'], 2)} ({s[0]['ano']})", f"{fmt_br(s[-1]['brutas'], 2)} ({s[-1]['ano']})",
                           "Queda de 16,7% (SEEG 13). A edição atual da base não traz anos do governo Bolsonaro, então não há comparação entre governos.")
    if fogo:
        f = {p["ano"]: p["focos"] for p in fogo["serie"]}
        c4, c5, _ = st.columns(3)
        with c4:
            render_compare_stat("Focos de queimada (pior ano de cada governo)", fmt_br(f[2020], 0), fmt_br(f[2024], 0),
                                "2020 (Bolsonaro) x 2024 (Lula, seca recorde)", better="bolsonaro")
        with c5:
            _card_evolucao("Focos de queimada, dentro do governo Lula", f"{fmt_br(f[2024], 0)} (2024)", f"{fmt_br(f[2025], 0)} (2025)",
                           f"{100 * (f[2025] / f[2024] - 1):+.0f}% de 2024 para 2025 (ano completo, Inpe). 2024 foi o ano da seca recorde.".replace(".", ","))

    st.markdown("---")

    # ---------------- Desmatamento
    st.subheader("1. Desmatamento por bioma (PRODES, km² por ano)")
    st.caption("O ano PRODES vai de agosto a julho — o dado de 2023 inclui cinco meses do governo Bolsonaro. 2026 é estimativa do Inpe (out/2026) e não entra nas médias.")
    if amz and cer:
        da, dc = pd.DataFrame(amz["serie"]), pd.DataFrame(cer["serie"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=da["ano"].astype(str), y=da["km2"], name="Amazônia", marker_color="#10B981",
                             text=da["km2"].apply(lambda v: fmt_br(v, 0)), textposition="outside"))
        fig.add_trace(go.Bar(x=dc["ano"].astype(str), y=dc["km2"], name="Cerrado", marker_color="#F59E0B",
                             text=dc["km2"].apply(lambda v: fmt_br(v, 0)), textposition="outside"))
        fig.add_vrect(x0=0.5, x1=4.5, fillcolor="#3B82F6", opacity=0.06, line_width=0, annotation_text="Bolsonaro", annotation_position="top left")
        fig.add_vrect(x0=4.5, x1=8.5, fillcolor="#EF2B2D", opacity=0.06, line_width=0, annotation_text="Lula", annotation_position="top left")
        fig.update_layout(barmode="group")
        apply_plotly_theme(fig, title="Área desmatada (km²)", height=440)
        st.plotly_chart(fig, width="stretch")
        render_source(amz["fonte"] + " e " + cer["fonte"] + ". " + cer["nota"], cer["url"])

    col_q, col_e = st.columns(2)
    with col_q:
        st.subheader("2. Focos de queimada no Brasil")
        if fogo:
            dq = pd.DataFrame(fogo["serie"])
            fig = go.Figure(go.Bar(x=dq["ano"].astype(str), y=dq["focos"], marker_color=[gov_color(g) for g in dq["governo"]],
                                   text=dq["focos"].apply(lambda v: "s/ dado" if pd.isna(v) else fmt_br(v, 0)), textposition="outside"))
            apply_plotly_theme(fig, title="Focos de calor detectados por satélite", height=400)
            st.plotly_chart(fig, width="stretch")
            render_source(fogo["fonte"] + ". " + fogo["nota"], fogo["url"])
    with col_e:
        st.subheader("3. Emissões de gases de efeito estufa")
        if emis:
            de = pd.DataFrame(emis["serie"])
            fig = go.Figure()
            fig.add_trace(go.Bar(x=de["ano"].astype(str), y=de["brutas"], name="Brutas", marker_color="#94A3B8",
                                 text=de["brutas"].apply(lambda v: fmt_br(v, 2)), textposition="outside"))
            fig.add_trace(go.Bar(x=de["ano"].astype(str), y=de["liquidas"], name="Líquidas (descontando remoções)", marker_color="#10B981",
                                 text=de["liquidas"].apply(lambda v: fmt_br(v, 2)), textposition="outside"))
            fig.update_layout(barmode="group")
            apply_plotly_theme(fig, title="Emissões do Brasil (GtCO2e)", height=400)
            st.plotly_chart(fig, width="stretch")
            render_source(emis["fonte"] + ". " + emis["nota"], emis["url"])

    ti = extras.get("terras_indigenas", {})
    if ti:
        st.markdown(f'<div class="info-box"><b>Terras indígenas:</b> {ti["nota"]}</div>', unsafe_allow_html=True)

    # ---------------- Políticas ambientais
    st.markdown("---")
    st.subheader("4. Políticas ambientais de cada governo")
    pol = get_politicas_data()
    pol = pol[pol["area"] == "Meio Ambiente & Clima"] if not pol.empty else pol
    col_b, col_l = st.columns(2)
    for col, gov in ((col_b, "Bolsonaro"), (col_l, "Lula")):
        with col:
            for _, row in pol[pol["governo"] == gov].iterrows():
                render_policy_card(row)
