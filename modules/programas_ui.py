"""
Programas e leis de cada governo, em linguagem simples, com pontos positivos, críticas e a fonte de cada um.
Usado na aba Saúde, na página de Políticas e na versão comparada das abas (outros pares de governos).
"""
import html
import streamlit as st
from modules.data_loader import load_json
from modules.ui_components import COR_MANDATO, PARTIDO, PERIODO

REP_COR = {"Boa": "#10B981", "Dividida": "#F59E0B", "Baixa": "#EF4444"}
REP_ROT = {"Boa": "Boa repercussão", "Dividida": "Repercussão dividida", "Baixa": "Baixa repercussão"}


def _link(item):
    texto = html.escape(item["texto"])
    if item.get("url"):
        return f'{texto} <a href="{html.escape(item["url"], quote=True)}" target="_blank">{html.escape(item["fonte"])} ↗</a>'
    return f'{texto} <span class="src">({html.escape(item["fonte"])})</span>' if item.get("fonte") else texto


def programas_unificados():
    """Programas do arquivo novo (Saúde e demais áreas já mapeadas) somados às políticas de Bolsonaro e Lula 3 já existentes no painel."""
    d = load_json("programas_governo.json")
    itens = list(d.get("programas", []))
    cobertos = {(p["area"], p["governo"]) for p in itens}
    for p in load_json("politicas.json"):
        gov = "Lula 3" if p["governo"] == "Lula" else p["governo"]
        area = p["area"]
        if (area, gov) in cobertos:
            continue
        itens.append({
            "id": f"pol-{p['id']}", "area": area, "governo": gov, "ano": p["ano"], "programa": p["politica"], "em_uma_frase": p["descricao"],
            "base_legal": {"nome": p.get("fonte", ""), "url": ""}, "situacao": p["status"],
            "beneficios": [{"texto": p["impactos_positivos"], "fonte": p.get("fonte", ""), "url": ""}] if p.get("impactos_positivos") else [],
            "criticas": [{"texto": p["impactos_negativos"], "fonte": p.get("fonte", ""), "url": ""}] if p.get("impactos_negativos") else [],
            "repercussao": p.get("repercussao"),
        })
    return itens, d.get("metadados", {})


def _cartao(p, mostrar_area=False):
    cor = COR_MANDATO.get(p["governo"], "#94A3B8")
    bons = "".join(f"<li>{_link(i)}</li>" for i in p["beneficios"]) or "<li>Não encontramos ponto positivo medido nas fontes consultadas.</li>"
    ruins = "".join(f"<li>{_link(i)}</li>" for i in p["criticas"]) or "<li>Não encontramos crítica relevante nas fontes consultadas.</li>"
    base = p["base_legal"]
    base_html = (f'<a href="{html.escape(base["url"], quote=True)}" target="_blank">{html.escape(base["nome"])} ↗</a>' if base.get("url") else html.escape(base["nome"]))
    area = f'<span class="prog-sit">{html.escape(p["area"])}</span>' if mostrar_area else ""
    rep = p.get("repercussao")
    rep_html = ""
    if isinstance(rep, dict) and rep.get("nivel") in REP_COR:
        link = f' <a href="{html.escape(rep["url"], quote=True)}" target="_blank">{html.escape(rep["fonte"])} ↗</a>' if rep.get("url") else ""
        rep_html = (f'<div class="prog-rep" style="border-left:3px solid {REP_COR[rep["nivel"]]};"><b>{REP_ROT[rep["nivel"]]}:</b> '
                    f'{html.escape(rep["evidencia"])}{link}</div>')
    st.markdown(
        f'<div class="prog-card" style="border-top:3px solid {cor};">'
        f'<div class="prog-meta"><span class="prog-gov" style="background:{cor};">{html.escape(p["governo"])}</span>'
        f'<span>{html.escape(str(p["ano"]))}</span>{area}<span class="prog-sit">{html.escape(p["situacao"])}</span></div>'
        f'<div class="prog-titulo">{html.escape(p["programa"])}</div>'
        f'<div class="prog-frase"><b>Em uma frase:</b> {html.escape(p["em_uma_frase"])}</div>'
        f'<div class="prog-bom"><b>O que se diz de bom</b><ul>{bons}</ul></div>'
        f'<div class="prog-ruim"><b>As críticas</b><ul>{ruins}</ul></div>'
        f'{rep_html}'
        f'<div class="prog-foot">Base: {base_html}</div>'
        '</div>', unsafe_allow_html=True)


def _cabecalho_gov(g, n):
    cor = COR_MANDATO.get(g, "#94A3B8")
    return (f'<div class="prog-gov-cab" style="border-left:5px solid {cor};"><b>{html.escape(g)}</b> · {PARTIDO.get(g, "")} · {PERIODO.get(g, "")} · '
            f'{n} {"programa" if n == 1 else "programas"} mapeado{"" if n == 1 else "s"}</div>')


def render_programas(area, governos, titulo="Programas de cada governo: o que foi feito, o que se diz de bom e as críticas", chave="prog", dados=None, aviso=None):
    """area: nome, lista de nomes ou None (todas as áreas). Mostra um cartão por programa, em colunas (até 2 governos) ou em abas."""
    itens, meta = dados if dados is not None else programas_unificados()
    areas = None if area is None else ([area] if isinstance(area, str) else list(area))
    itens = [p for p in itens if areas is None or p["area"] in areas]
    if not itens:
        return False
    if titulo:
        st.subheader(titulo)
    st.markdown(
        '<div class="info-box"><b>Como ler:</b> cada cartão traz uma frase simples sobre o programa, o que se diz de bom e as críticas, sempre com o link da fonte. '
        'Quando o número vem de quem fez a política (governo ou setor interessado), o próprio texto avisa. '
        f'{html.escape(aviso or meta.get("aviso", ""))}</div>', unsafe_allow_html=True)
    multiplas = areas is None or len(areas) > 1
    por_gov = {g: sorted([p for p in itens if p["governo"] == g], key=lambda x: (x["area"], str(x["ano"]))) for g in governos}
    vazio = ('<div class="prog-vazio">Nenhum programa deste governo foi mapeado {onde} ainda. A lista é uma seleção, não o conjunto completo.</div>')
    onde = "nesta área" if not multiplas else "com estes filtros"
    if len(governos) <= 2:
        cols = st.columns(len(governos))
        for col, g in zip(cols, governos):
            with col:
                st.markdown(_cabecalho_gov(g, len(por_gov[g])), unsafe_allow_html=True)
                if not por_gov[g]:
                    st.markdown(vazio.format(onde=onde), unsafe_allow_html=True)
                for p in por_gov[g]:
                    _cartao(p, multiplas)
    else:
        abas = st.tabs([f"{g} ({len(por_gov[g])})" for g in governos])
        for aba, g in zip(abas, governos):
            with aba:
                st.markdown(_cabecalho_gov(g, len(por_gov[g])), unsafe_allow_html=True)
                if not por_gov[g]:
                    st.markdown(vazio.format(onde=onde), unsafe_allow_html=True)
                for p in por_gov[g]:
                    _cartao(p, multiplas)
    return True
