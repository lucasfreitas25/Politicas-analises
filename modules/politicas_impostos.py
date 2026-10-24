"""Aba Impostos da página de Políticas: tributos criados, aumentados, reduzidos e extintos em cada governo."""
import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.ui_components import apply_plotly_theme, COR_MANDATO, PARTIDO, PERIODO
from modules.ux import gl

CAT_COR = {"Em vigor": "#10B981", "Contestado ou em transição": "#38BDF8", "Extinto ou revogado": "#EF4444", "Barrado ou revertido": "#F59E0B"}
ACAO_COR = {"Criação": "#A78BFA", "Aumento": "#F87171", "Redução": "#34D399", "Extinção": "#94A3B8"}


def _chip(texto, cor):
    return f'<span class="verdict-pill" style="background:{cor};">{html.escape(texto)}</span>'


def _cartao(r):
    cor = COR_MANDATO.get(r["governo"], "#94A3B8")
    n = r["norma"]
    norma = f'<a href="{html.escape(n["url"], quote=True)}" target="_blank">{html.escape(n["nome"])} ↗</a>' if n.get("url") else html.escape(n["nome"])
    fontes = "".join(f'<li>{html.escape(x["texto"])} <a href="{html.escape(x["url"], quote=True)}" target="_blank">{html.escape(x["fonte"])} ↗</a></li>' for x in r["fontes"])
    qtd = f' · {r["qtd"]} novo{"s" if r["qtd"] != 1 else ""}' if r["acao"] == "Criação" and r["qtd"] else ""
    st.markdown(gl(
        f'<div class="prog-card" style="border-top:3px solid {cor};">'
        f'<div class="prog-meta"><span class="prog-gov" style="background:{cor};">{html.escape(r["governo"])}</span><span>{html.escape(str(r["ano"]))}</span>'
        f'<span class="prog-sit">{html.escape(r["tipo"])}</span>{_chip(r["acao"] + qtd, ACAO_COR[r["acao"]])}{_chip(r["categoria"], CAT_COR[r["categoria"]])}</div>'
        f'<div class="prog-titulo">{html.escape(r["tributo"])}</div>'
        f'<div class="prog-frase"><b>O que é:</b> {html.escape(r["resumo"])}</div>'
        f'<div class="prog-frase"><b>Situação hoje:</b> {html.escape(r["situacao"])}</div>'
        f'{"<div class=prog-bom><b>Fontes</b><ul>" + fontes + "</ul></div>" if fontes else ""}'
        f'<div class="prog-foot">Norma: {norma}</div></div>'), unsafe_allow_html=True)


def render_impostos(govs, chave="imp"):
    """govs: nomes no padrão FHC 1 … Lula 3. 'Lula' (base antiga) é tratado como 'Lula 3'."""
    govs = ["Lula 3" if g == "Lula" else g for g in govs]
    d = load_json("tributos.json")
    df = pd.DataFrame(d["tributos"])
    df = df[df["governo"].isin(govs)]
    st.markdown(
        '<div class="info-box"><b>Impostos e outros tributos por governo.</b> Mostra o que cada governo <b>criou</b>, <b>aumentou</b>, <b>reduziu</b> ou <b>extinguiu</b>, '
        'o que <b>continua em vigor</b>, o que foi <b>extinto ou revogado</b> e quais <b>reduções de imposto foram barradas, limitadas ou revertidas</b>. '
        f'{html.escape(d["metadados"]["aviso"])}</div>', unsafe_allow_html=True)
    if df.empty:
        st.info("Nenhum tributo mapeado para estes governos.")
        return

    # resumo por governo
    linhas = []
    for g in govs:
        s = df[df["governo"] == g]
        linhas.append({
            "Governo": g, "Criados": int(s["qtd"].sum()), "Aumentos": int((s["acao"] == "Aumento").sum()), "Reduções": int((s["acao"] == "Redução").sum()),
            "Extinções": int((s["acao"] == "Extinção").sum()), "Em vigor": int((s["categoria"] == "Em vigor").sum()),
            "Extintos ou revogados": int((s["categoria"] == "Extinto ou revogado").sum()),
            "Barrados ou revertidos": int((s["categoria"] == "Barrado ou revertido").sum()),
            "Contestados ou em transição": int((s["categoria"] == "Contestado ou em transição").sum()),
            "Reduções impedidas": int(s["reducao_impedida"].sum()),
        })
    resumo = pd.DataFrame(linhas)

    fig = go.Figure(go.Bar(x=resumo["Governo"], y=resumo["Criados"], marker_color=[COR_MANDATO[g] for g in resumo["Governo"]],
                           text=resumo["Criados"], textposition="outside", textfont=dict(color="#ffffff"),
                           customdata=[PARTIDO[g] + " · " + PERIODO[g] for g in resumo["Governo"]], hovertemplate="<b>%{x}</b> (%{customdata})<br>%{y} tributos ou regimes criados<extra></extra>"))
    apply_plotly_theme(fig, title="Tributos e regimes de tributação criados em cada governo", height=340)
    fig.update_layout(hovermode="closest", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.caption("Conta tributos e regimes de tributação novos. Mudança de alíquota de tributo que já existia (aumento ou redução por decreto ou lei) aparece em outra coluna e não entra aqui.")

    cat = go.Figure()
    for c, cor in CAT_COR.items():
        cat.add_trace(go.Bar(x=resumo["Governo"], y=resumo[{"Em vigor": "Em vigor", "Contestado ou em transição": "Contestados ou em transição",
                                                              "Extinto ou revogado": "Extintos ou revogados", "Barrado ou revertido": "Barrados ou revertidos"}[c]],
                             name=c, marker_color=cor))
    cat.update_layout(barmode="stack")
    apply_plotly_theme(cat, title="Situação das medidas de cada governo (criações, aumentos, reduções e extinções)", height=360)
    cat.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top"))
    st.plotly_chart(cat, width="stretch")
    from modules.ui_components import mostrar_tabela
    mostrar_tabela(resumo, titulo_col="Governo", width="stretch", hide_index=True)

    # reduções impedidas
    barradas = df[df["reducao_impedida"]]
    st.subheader("Reduções de imposto que foram barradas, limitadas ou revertidas")
    st.markdown(
        '<div class="info-box">São cortes de imposto que o governo fez ou tentou e que foram suspensos pela Justiça, derrubados, limitados em acordo ou desfeitos pelo governo seguinte. '
        'Inclui combustíveis, produtos industrializados e a folha de pagamento. Cada item diz quem barrou e quando.</div>', unsafe_allow_html=True)
    if barradas.empty:
        st.caption("Nenhuma redução barrada nos governos escolhidos.")
    for _, r in barradas.iterrows():
        _cartao(r)

    st.subheader("Todas as medidas")
    c1, c2 = st.columns(2)
    with c1:
        acoes = st.pills("Tipo de medida", list(ACAO_COR), selection_mode="multi", default=list(ACAO_COR), key=f"{chave}_acoes_{'_'.join(govs)}") or []
    with c2:
        cats = st.pills("Situação hoje", list(CAT_COR), selection_mode="multi", default=list(CAT_COR), key=f"{chave}_cats_{'_'.join(govs)}") or []
    f = df[df["acao"].isin(acoes) & df["categoria"].isin(cats)]
    if f.empty:
        st.info("Nenhuma medida com esses filtros.")
        return
    if len(govs) <= 2:
        cols = st.columns(len(govs))
        for col, g in zip(cols, govs):
            with col:
                st.markdown(f"**{g}** · {PARTIDO[g]} · {PERIODO[g]}")
                parte = f[f["governo"] == g]
                if parte.empty:
                    st.caption("Nenhuma medida com esses filtros.")
                for _, r in parte.iterrows():
                    _cartao(r)
    else:
        abas = st.tabs([f"{g} ({int((f['governo'] == g).sum())})" for g in govs])
        for aba, g in zip(abas, govs):
            with aba:
                parte = f[f["governo"] == g]
                if parte.empty:
                    st.caption("Nenhuma medida com esses filtros.")
                for _, r in parte.iterrows():
                    _cartao(r)
    tabela = f[["governo", "ano", "tributo", "tipo", "acao", "categoria", "resumo", "situacao"]]
    st.download_button("Baixar medidas (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"), file_name="tributos_por_governo.csv", mime="text/csv")
