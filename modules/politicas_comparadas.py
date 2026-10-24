"""Página de Políticas, Leis & Repercussão para qualquer par de governos (ou todos), sobre a base histórica."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.historico_ui import nomes_governos
from modules.programas_ui import render_programas, programas_unificados
from modules.ui_components import apply_plotly_theme, COR_MANDATO, PARTIDO, PERIODO, render_source


def leis_unificadas():
    """Leis de FHC a Temer (base histórica) somadas às de Bolsonaro e Lula 3 já existentes no painel."""
    hist = pd.DataFrame(load_json("leis_historicas.json"))
    atual = pd.DataFrame(load_json("leis_sancionadas.json"))
    if not atual.empty:
        atual["governo"] = atual["governo"].replace({"Lula": "Lula 3"})
    cols = ["data", "governo", "norma", "tipo", "area", "resumo", "situacao", "texto_oficial", "manchete", "url_imprensa"]
    tudo = pd.concat([hist[cols] if not hist.empty else pd.DataFrame(columns=cols), atual[cols] if not atual.empty else pd.DataFrame(columns=cols)], ignore_index=True)
    tudo["data"] = pd.to_datetime(tudo["data"])
    return tudo.sort_values("data")


def _aba_leis(leis, sel):
    f = leis[leis["governo"].isin(sel)]
    st.markdown(
        '<div class="info-box"><b>Leis, leis complementares e emendas constitucionais:</b> cada número e data foi conferido no texto oficial do Planalto '
        '(link na coluna "Texto oficial"). O resumo é do painel, em linguagem simples. A lista traz as principais normas de cada governo, não todas as milhares sancionadas. '
        'Para FHC a Temer, a situação ("em vigor", "com alterações", "revogada") foi lida do texto do Planalto; para Bolsonaro e Lula 3, foi conferida norma por norma.</div>',
        unsafe_allow_html=True)
    areas = sorted(f["area"].unique())
    c1, c2 = st.columns([1.4, 1])
    with c1:
        areas_sel = st.multiselect("Área", areas, default=areas, key="leis_cmp_area")
    with c2:
        tipos = sorted(f["tipo"].unique())
        tipos_sel = st.pills("Tipo", tipos, selection_mode="multi", default=tipos, key="leis_cmp_tipo") or []
    f = f[f["area"].isin(areas_sel) & f["tipo"].isin(tipos_sel)]
    if f.empty:
        st.info("Nenhuma norma com esses filtros.")
        return
    contagem = f.groupby("governo").size().reindex(sel).fillna(0).astype(int)
    st.caption("Normas por governo: " + " · ".join(f"{g}: {n}" for g, n in contagem.items()))
    fig = go.Figure()
    for g in sel:
        sub = f[f["governo"] == g]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(x=sub["data"], y=sub["area"], mode="markers", name=g, marker=dict(size=12, color=COR_MANDATO.get(g), line=dict(width=1, color="#0b0f19")),
                                 text=sub["norma"], customdata=sub["resumo"], hovertemplate="<b>%{text}</b><br>%{x|%d/%m/%Y}<br>%{customdata}<extra></extra>"))
    apply_plotly_theme(fig, title=f"Linha do tempo das normas ({len(f)})", height=max(380, 26 * f["area"].nunique() + 160))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top"))
    st.plotly_chart(fig, width="stretch")
    tabela = f[["data", "governo", "norma", "area", "resumo", "situacao", "texto_oficial", "manchete", "url_imprensa"]]
    st.dataframe(
        tabela, width="stretch", hide_index=True, height=560,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"), "governo": "Governo", "norma": "Norma", "area": "Área",
            "resumo": st.column_config.TextColumn("O que faz", width="large"), "situacao": st.column_config.TextColumn("Situação", width="medium"),
            "texto_oficial": st.column_config.LinkColumn("Texto oficial", display_text="Planalto ↗"),
            "manchete": st.column_config.TextColumn("Na imprensa", width="large"), "url_imprensa": st.column_config.LinkColumn("Link", display_text="ler ↗"),
        })
    st.download_button("Baixar normas (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"), file_name="normas_governos_selecionados.csv", mime="text/csv")


def render_politicas_comparadas(a, b, todos):
    from modules.ui_components import render_section_header
    governos = nomes_governos()
    sel = governos if todos else [a, b]
    render_section_header(
        "Políticas de Governo: Impactos Positivos e Negativos",
        "As principais políticas e leis de cada governo, com o que cada uma trouxe de bom e de ruim. "
        + ("Todos os governos, de FHC a Lula 3." if todos else f"{a} x {b}."))
    if a == b and not todos:
        st.info("Escolha dois governos diferentes.")
        return
    itens, meta = programas_unificados()
    leis = leis_unificadas()
    n_prog = {g: sum(1 for p in itens if p["governo"] == g) for g in sel}
    n_leis = {g: int((leis["governo"] == g).sum()) for g in sel}
    linhas = "".join(f"<li><b>{g}</b> ({PARTIDO[g]}, {PERIODO[g]}): {n_prog[g]} programas e {n_leis[g]} leis</li>" for g in sel)
    st.markdown(
        '<div class="info-box"><b>O que o painel tem de cada governo selecionado:</b>'
        f'<ul style="margin-bottom:0;">{linhas}</ul>'
        'A repercussão em pesquisas de opinião só existe para as políticas de Bolsonaro e Lula 3; os programas dos demais governos ainda não têm esse dado. '
        'Os programas de cada governo são uma seleção das mais conhecidas e vão sendo ampliados por área; as leis cobrem todas as áreas.</div>', unsafe_allow_html=True)
    areas = sorted({p["area"] for p in itens})
    area_sel = st.pills("Áreas dos programas", areas, selection_mode="multi", default=areas, key="pol_cmp_areas") or areas
    abas = st.tabs(["Programas e políticas", "Leis sancionadas"])
    with abas[0]:
        if not render_programas(area_sel, sel, titulo=None, dados=(itens, meta)):
            st.info("Nenhum programa nas áreas escolhidas.")
    with abas[1]:
        _aba_leis(leis, sel)
