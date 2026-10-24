import html
import streamlit as st
import pandas as pd
from modules.data_loader import get_propostas_data
from modules.ui_components import render_section_header


def _ausente(item):
    t = item["texto"].lower()
    return "não consta" in t or "não trata" in t or "não há proposta" in t


def _situacao(itens):
    """'✔ Propõe' (todos os itens são propostas), '◐ Parcial' (mistura de proposta e lacuna) ou '— Não consta'."""
    aus = sum(_ausente(i) for i in itens)
    if aus == 0:
        return "✔ Propõe"
    return "— Não consta" if aus == len(itens) else "◐ Parcial"


def _item_html(item, fontes):
    f = fontes.get(item["fonte"], {})
    ausente = _ausente(item)
    classe = "prop-gap" if ausente else ""
    link = f'<a href="{f["url"]}" target="_blank">{html.escape(f["nome"])} ↗</a>' if f else ""
    return f'<div class="prop-item"><span class="{classe}">{html.escape(item["texto"])}</span> <span class="src">· {link}</span></div>'


def _plano_html(itens, url):
    if not itens:
        return ""
    linhas = "".join(
        f'<div class="prop-item"><span>{html.escape(i["texto"])}</span> <span class="src">· <a href="{url}#page={i["pagina"]}" target="_blank">p. {i["pagina"]} ↗</a></span></div>'
        for i in itens)
    return f'<div class="prop-card plano"><div class="src">No plano oficial (conferido no PDF)</div>{linhas}</div>'


def render_tab_campaign():
    render_section_header(
        "Propostas de Campanha",
        "O que os candidatos de 2026 prometem e o que cada presidente eleito desde 1994 propôs no plano com que venceu a eleição, "
        "lado a lado, com a fonte e a página de cada ponto.",
    )
    aba_2026, aba_planos = st.tabs(["Eleição 2026: Lula x Flávio", "Planos dos presidentes eleitos (1994–2022)"])
    with aba_2026:
        _render_2026()
    with aba_planos:
        _render_planos()


def _item_plano(item, url):
    return (f'<div class="prop-item"><span class="mini-badge mb-tie">{html.escape(item["tema"])}</span> {html.escape(item["texto"])} '
            f'<span class="src">· <a href="{html.escape(url, quote=True)}#page={item["pagina"]}" target="_blank">p. {item["pagina"]} ↗</a></span></div>')


def _cartao_plano(plano, temas_sel):
    from modules.ui_components import classe_gov, PERIODO
    c = classe_gov(plano["governo"])
    itens = [i for i in plano["propostas"] if not temas_sel or i["tema"] in temas_sel]
    corpo = "".join(_item_plano(i, plano["url"]) for i in itens) or '<div class="prop-item prop-gap">Nenhuma proposta destes temas no resumo do plano.</div>'
    st.markdown(
        f'<div class="prop-card borda-{c}">'
        f'<div class="gov-name {c}" style="font-weight:800;font-size:1rem;">{html.escape(plano["governo"])} · {html.escape(PERIODO.get(plano["governo"], ""))}</div>'
        f'<div style="color:#f8fafc;font-weight:700;margin:2px 0 2px;">{html.escape(plano["titulo"])} ({plano["ano"]})</div>'
        f'<div class="src" style="color:#94a3b8;font-size:0.78rem;margin-bottom:6px;">{html.escape(plano["partido"])} · '
        f'<a href="{html.escape(plano["url"], quote=True)}" target="_blank">íntegra em PDF ↗</a></div>'
        f'{corpo}<div class="src" style="color:#64748b;font-size:0.72rem;margin-top:6px;">{html.escape(plano["nota"])}</div></div>',
        unsafe_allow_html=True)


def _render_planos():
    from modules.data_loader import load_json
    from modules.ui_components import css_governos
    dados = load_json("planos_governo.json")
    if not dados:
        st.warning("Base de planos não encontrada (data/planos_governo.json).")
        return
    st.markdown(css_governos(), unsafe_allow_html=True)
    planos = {p["governo"]: p for p in dados["planos"]}
    nomes = list(planos)
    st.markdown(f'<div class="info-box">{html.escape(dados["metadados"]["aviso"])} '
                'Temer não foi eleito como cabeça de chapa; aparece o programa "Uma Ponte para o Futuro" (PMDB, 2015), que o governo adotou como base.</div>',
                unsafe_allow_html=True)
    padrao_a = st.session_state.get("gov_a", "Bolsonaro")
    padrao_b = st.session_state.get("gov_b", "Lula 3")
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1.6], vertical_alignment="bottom")
        a = c1.selectbox("Governo A", nomes, index=nomes.index(padrao_a) if padrao_a in nomes else nomes.index("Bolsonaro"), key="plano_a")
        b = c2.selectbox("Governo B", nomes, index=nomes.index(padrao_b) if padrao_b in nomes else nomes.index("Lula 3"), key="plano_b")
        todos = c3.toggle("Todos os governos", key="plano_todos")
        temas = sorted({i["tema"] for p in dados["planos"] for i in p["propostas"]})
        temas_sel = st.pills("Temas", temas, selection_mode="multi", key="plano_temas") or []
    if todos:
        for i in range(0, len(nomes), 2):
            cols = st.columns(2)
            for col, g in zip(cols, nomes[i:i + 2]):
                with col:
                    _cartao_plano(planos[g], temas_sel)
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            _cartao_plano(planos[a], temas_sel)
        with col_b:
            _cartao_plano(planos[b], temas_sel)
    st.caption("Cada item é um resumo do painel; o número da página abre o PDF no trecho citado. As páginas são as do arquivo PDF, que podem diferir da numeração impressa.")


def _render_2026():
    dados = get_propostas_data()
    if not dados:
        st.warning("Base de propostas não encontrada (data/propostas_campanha.json).")
        return
    meta, fontes, temas = dados["metadados"], dados["fontes"], dados["temas"]

    st.markdown(
        f'<div class="info-box"><b>⚠ São promessas, não fatos.</b> {html.escape(meta["aviso"])}<br/>'
        f'<b>Planos:</b> Lula — {html.escape(meta["planos"]["Lula"])}; Flávio Bolsonaro — {html.escape(meta["planos"]["Flávio Bolsonaro"])}. '
        f'Íntegras em PDF: <a href="{fontes["plula"]["url"]}" target="_blank">Lula ↗</a> · <a href="{fontes["pflavio"]["url"]}" target="_blank">Flávio ↗</a> '
        '(cópias de Congresso em Foco e Poder360; o arquivo oficial está no portal do TSE).</div>',
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
    st.dataframe(quadro, width="stretch", hide_index=True, height=38 * (len(quadro) + 1))
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
                st.markdown(_plano_html(t.get("plano", {}).get("lula"), fontes["plula"]["url"]), unsafe_allow_html=True)
            with col_f:
                st.markdown("**Flávio Bolsonaro (PL)**")
                st.markdown('<div class="prop-card flavio">' + "".join(_item_html(i, fontes) for i in t["flavio"]) + "</div>", unsafe_allow_html=True)
                st.markdown(_plano_html(t.get("plano", {}).get("flavio"), fontes["pflavio"]["url"]), unsafe_allow_html=True)
            if ctx and t["contexto"]:
                st.markdown(f'<div class="info-box"><b>Contexto hoje:</b> {html.escape(t["contexto"])}</div>', unsafe_allow_html=True)
            if ver and t["verificacao"]:
                st.markdown(f'<div class="info-box"><b>Checagem relacionada:</b> {html.escape(t["verificacao"])} '
                            'Veja todas na página \"Checagem: Lula x Flávio\".</div>', unsafe_allow_html=True)
    if mostrados == 0:
        st.info("Nenhum tema com esses filtros.")

    st.caption("Nomes e prazos conforme as reportagens citadas em cada item. Se o plano registrado no TSE trouxer redação diferente, ela prevalece.")
