import html
import streamlit as st
import pandas as pd
from modules.data_loader import get_propostas_data
from modules.ui_components import render_section_header


def _ausente(item):
    t = item["texto"].lower()
    return "não consta" in t or "não trata" in t or "não há proposta" in t


def _situacao(itens):
    """'✅ Propõe' (todos os itens são propostas), '◐ Parcial' (mistura de proposta e lacuna) ou '— Não consta'."""
    aus = sum(_ausente(i) for i in itens)
    if aus == 0:
        return "✅ Propõe"
    return "— Não consta" if aus == len(itens) else "◐ Parcial"


def _item_html(item, fontes):
    f = fontes.get(item["fonte"], {})
    ausente = _ausente(item)
    classe = "prop-gap" if ausente else ""
    link = f'<a href="{f["url"]}" target="_blank">{html.escape(f["nome"])} ↗</a>' if f else ""
    return f'<div class="prop-item"><span class="{classe}">{html.escape(item["texto"])}</span> <span class="src">· {link}</span></div>'


def render_tab_campaign():
    render_section_header(
        "🗳️ Propostas de Campanha: Lula x Flávio Bolsonaro",
        "O que cada candidato promete nos principais temas do 2º turno de 2026, lado a lado, com a fonte de cada ponto e o contexto de dados e checagens.",
    )

    dados = get_propostas_data()
    if not dados:
        st.warning("Base de propostas não encontrada (data/propostas_campanha.json).")
        return
    meta, fontes, temas = dados["metadados"], dados["fontes"], dados["temas"]

    st.markdown(
        f'<div class="info-box"><b>⚠️ São promessas, não fatos.</b> {html.escape(meta["aviso"])}<br/>'
        f'<b>Planos:</b> Lula — {html.escape(meta["planos"]["Lula"])}; Flávio Bolsonaro — {html.escape(meta["planos"]["Flávio Bolsonaro"])}. '
        f'Íntegra do plano de Flávio: <a href="{fontes["p360"]["url"]}" target="_blank">Poder360 ↗</a>.</div>',
        unsafe_allow_html=True,
    )

    # ---------------- Visão geral: quem tem proposta em cada tema
    st.subheader("Visão geral: onde cada plano apresenta proposta")
    quadro = pd.DataFrame({
        "Tema": [t["tema"] for t in temas],
        "Lula": [_situacao(t["lula"]) for t in temas],
        "Flávio Bolsonaro": [_situacao(t["flavio"]) for t in temas],
        "Itens (Lula)": [len(t["lula"]) for t in temas],
        "Itens (Flávio)": [len(t["flavio"]) for t in temas],
    })
    st.dataframe(quadro, use_container_width=True, hide_index=True, height=38 * (len(quadro) + 1))
    st.caption("\"Parcial\" = o plano cobre parte do tema, e as fontes consultadas não citam o resto. \"Não consta\" significa que as fontes não citam o tema — não prova que o plano completo seja omisso.")

    # ---------------- Filtros
    nomes = [t["tema"] for t in temas]
    with st.container(border=True):
        sel = st.pills("Temas", nomes, selection_mode="multi", default=nomes, key="camp_temas") or []
        c1, c2 = st.columns([1, 1])
        with c1:
            ctx = st.toggle("Mostrar contexto (dados atuais)", value=True, key="camp_ctx")
        with c2:
            ver = st.toggle("Mostrar o que as agências de checagem disseram", value=True, key="camp_ver")
        busca = st.text_input("Buscar nas propostas", "", placeholder="Ex.: privatização, 6x1, armas, IVA, desmatamento...", key="camp_busca")

    # ---------------- Temas
    mostrados = 0
    for t in temas:
        if t["tema"] not in sel:
            continue
        texto_total = " ".join(i["texto"] for i in t["lula"] + t["flavio"]).lower()
        if busca and busca.lower() not in texto_total and busca.lower() not in t["tema"].lower():
            continue
        mostrados += 1
        with st.expander(f"**{t['tema']}**", expanded=bool(busca) or len(sel) <= 3):
            col_l, col_f = st.columns(2)
            with col_l:
                st.markdown("**Lula (PT)**")
                st.markdown('<div class="prop-card lula">' + "".join(_item_html(i, fontes) for i in t["lula"]) + "</div>", unsafe_allow_html=True)
            with col_f:
                st.markdown("**Flávio Bolsonaro (PL)**")
                st.markdown('<div class="prop-card flavio">' + "".join(_item_html(i, fontes) for i in t["flavio"]) + "</div>", unsafe_allow_html=True)
            if ctx and t["contexto"]:
                st.markdown(f'<div class="info-box"><b>📊 Contexto hoje:</b> {html.escape(t["contexto"])}</div>', unsafe_allow_html=True)
            if ver and t["verificacao"]:
                st.markdown(f'<div class="info-box"><b>🔎 Checagem relacionada:</b> {html.escape(t["verificacao"])} '
                            'Veja todas na página \"Checagem: Lula x Flávio\".</div>', unsafe_allow_html=True)
    if mostrados == 0:
        st.info("Nenhum tema com esses filtros.")

    st.caption("Nomes e prazos conforme as reportagens citadas em cada item. Se o plano registrado no TSE trouxer redação diferente, ela prevalece.")
