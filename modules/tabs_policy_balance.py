import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_politicas_data, get_leis_data
from modules.ui_components import apply_plotly_theme, render_section_header, render_source, COLOR_BOLSONARO, COLOR_LULA

GOV_LABEL = {"Bolsonaro": "Governo Bolsonaro (2019–2022)", "Lula": "Governo Lula (2023–2026)"}
STATUS_COR = {
    "Em vigor": "#10B981", "Em vigor em parte": "#F59E0B", "Deixou de valer": "#EF4444",
    "Concluída": "#94A3B8", "Em tramitação ou disputa": "#38BDF8",
}
REPERC_COR = {"Boa": "#10B981", "Dividida": "#F59E0B", "Baixa": "#EF4444", "Sem dado": "#64748B"}
REPERC_ROTULO = {"Boa": "Boa repercussão", "Dividida": "Repercussão dividida", "Baixa": "Baixa repercussão", "Sem dado": "Sem pesquisa encontrada"}


def _chip(texto, cor, escuro=True):
    return f'<span class="verdict-pill" style="background:{cor};{"" if escuro else "color:#fff !important;"}">{html.escape(texto)}</span>'


def render_policy_card(row):
    gov = row["governo"]
    rep = row.get("repercussao") if hasattr(row, "get") else None
    rep = rep if isinstance(rep, dict) else {"nivel": "Sem dado", "evidencia": "", "fonte": "", "url": ""}
    cat = row.get("status_categoria", "Em vigor") if hasattr(row, "get") else "Em vigor"
    bloco_rep = ""
    if rep["nivel"] != "Sem dado":
        link = f' <a href="{rep["url"]}" target="_blank">{html.escape(rep["fonte"])} ↗</a>' if rep.get("url") else ""
        bloco_rep = (f'<div class="policy-rep" style="border-left-color:{REPERC_COR[rep["nivel"]]};">📣 <b>{REPERC_ROTULO[rep["nivel"]]}:</b> '
                     f'{html.escape(rep["evidencia"])}{link}</div>')
    else:
        bloco_rep = '<div class="policy-rep" style="border-left-color:#64748B;">📣 <b>Repercussão:</b> sem pesquisa de opinião encontrada.</div>'
    st.markdown(
        f'<div class="policy-card {gov.lower()}">'
        f'<div class="check-meta"><span class="cand-tag {"flavio" if gov == "Bolsonaro" else "lula"}">{gov}</span>'
        f'<span>· {html.escape(str(row["ano"]))}</span><span>· {html.escape(row["area"])}</span>'
        f'{_chip(cat, STATUS_COR.get(cat, "#94A3B8"))}</div>'
        f'<div class="policy-title">{html.escape(row["politica"])}</div>'
        f'<div class="policy-desc">{html.escape(row["descricao"])}</div>'
        f'<div class="policy-pos">✅ <b>Impactos positivos:</b> {html.escape(row["impactos_positivos"])}</div>'
        f'<div class="policy-neg">⚠️ <b>Impactos negativos e críticas:</b> {html.escape(row["impactos_negativos"])}</div>'
        f'{bloco_rep}'
        f'<div class="policy-foot">Situação: {html.escape(row["status"])} · 📎 Fonte: {html.escape(row["fonte"])}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _filtrar(df, gov_sel, areas_sel, status_sel, busca):
    f = df[df["area"].isin(areas_sel)]
    if gov_sel != "Ambos":
        f = f[f["governo"] == gov_sel]
    if status_sel:
        f = f[f["status_categoria"].isin(status_sel)]
    if busca:
        texto = f[["politica", "descricao", "impactos_positivos", "impactos_negativos"]].agg(" ".join, axis=1)
        f = f[texto.str.contains(busca, case=False, regex=False)]
    return f


def _aba_por_area(f, areas, layout, area_sel, busca):
    contagem = f.groupby(["area", "governo"]).size().unstack(fill_value=0).reindex([a for a in areas if a in set(f["area"])])
    fig = go.Figure()
    for gov, cor in (("Bolsonaro", COLOR_BOLSONARO), ("Lula", COLOR_LULA)):
        if gov in contagem.columns:
            fig.add_trace(go.Bar(y=contagem.index, x=contagem[gov], name=GOV_LABEL[gov], orientation="h", marker_color=cor,
                                 hovertemplate="%{y}: %{x} políticas<extra>" + gov + "</extra>"))
    fig.update_layout(barmode="group")
    apply_plotly_theme(fig, title=f"Políticas mapeadas por área ({len(f)} no filtro atual)", height=max(320, 30 * len(contagem) + 140))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    if layout == "Lista":
        for _, row in f.iterrows():
            render_policy_card(row)
        return
    for area in [a for a in areas if a in set(f["area"])]:
        sub = f[f["area"] == area]
        with st.expander(f"**{area}** — {len(sub)} políticas", expanded=len(area_sel) <= 2 or bool(busca)):
            col_b, col_l = st.columns(2)
            for col, gov in ((col_b, "Bolsonaro"), (col_l, "Lula")):
                with col:
                    parte = sub[sub["governo"] == gov]
                    st.markdown(f"**{GOV_LABEL[gov]}**")
                    if parte.empty:
                        st.caption("Nenhuma política nesta área com os filtros atuais.")
                    for _, row in parte.iterrows():
                        render_policy_card(row)


def _aba_deixou_de_valer(df, leis):
    st.markdown(
        '<div class="info-box"><b>O que de fato deixou de estar em vigor:</b> políticas revogadas, substituídas, encerradas ou derrubadas pela Justiça '
        'ou pelo Congresso. \"Em vigor em parte\" indica que só uma parte foi revertida. A coluna de situação reproduz o que ocorreu com cada uma.</div>',
        unsafe_allow_html=True,
    )
    f = df[df["status_categoria"].isin(["Deixou de valer", "Em vigor em parte"])].copy()
    cols = st.columns(3)
    cols[0].metric("Deixaram de valer", int((f["status_categoria"] == "Deixou de valer").sum()))
    cols[1].metric("Em vigor em parte", int((f["status_categoria"] == "Em vigor em parte").sum()))
    cols[2].metric("Ainda em vigor (todas as políticas)", int((df["status_categoria"] == "Em vigor").sum()))
    tabela = f[["governo", "ano", "area", "politica", "status_categoria", "status"]].rename(columns={
        "governo": "Governo", "ano": "Período", "area": "Área", "politica": "Política", "status_categoria": "Faixa", "status": "O que aconteceu"})
    st.dataframe(tabela, use_container_width=True, hide_index=True, height=min(80 + 36 * len(tabela), 640),
                 column_config={"Política": st.column_config.TextColumn(width="large"), "O que aconteceu": st.column_config.TextColumn(width="medium")})

    if not leis.empty:
        fim = leis[~leis["situacao"].str.startswith("Em vigor") & ~leis["situacao"].str.startswith("Em implantação")]
        if not fim.empty:
            st.subheader("Normas sancionadas que perderam efeito ou foram alteradas")
            t = fim[["data", "governo", "norma", "resumo", "situacao"]].rename(columns={"data": "Data", "governo": "Governo", "norma": "Norma", "resumo": "O que fazia", "situacao": "Situação"})
            st.dataframe(t, use_container_width=True, hide_index=True,
                         column_config={"Data": st.column_config.DateColumn(format="DD/MM/YYYY"), "O que fazia": st.column_config.TextColumn(width="large")})
    st.subheader("Detalhe das políticas que deixaram de valer")
    col_b, col_l = st.columns(2)
    for col, gov in ((col_b, "Bolsonaro"), (col_l, "Lula")):
        with col:
            st.markdown(f"**{GOV_LABEL[gov]}**")
            parte = f[f["governo"] == gov]
            if parte.empty:
                st.caption("Nenhuma com os filtros atuais.")
            for _, row in parte.iterrows():
                render_policy_card(row)


def _aba_repercussao(f):
    st.markdown(
        '<div class="info-box"><b>Repercussão:</b> o que pesquisas de opinião e a imprensa registraram sobre cada política. '
        'Só aparece quando encontramos pesquisa ou cobertura confiável — nunca por suposição. Algumas pesquisas medem a popularidade do governo ou de um reajuste, '
        'não da política inteira (isso está dito em cada caso). Pesquisas encomendadas por governos ou campanhas estão sinalizadas.</div>',
        unsafe_allow_html=True,
    )
    f = f.copy()
    f["nivel"] = f["repercussao"].apply(lambda r: r["nivel"])
    medidas = f[f["nivel"] != "Sem dado"]
    if medidas.empty:
        st.info("Nenhuma política com repercussão medida nos filtros atuais.")
    else:
        tab = medidas.groupby(["governo", "nivel"]).size().unstack(fill_value=0)
        fig = go.Figure()
        for nivel in ("Boa", "Dividida", "Baixa"):
            if nivel in tab.columns:
                fig.add_trace(go.Bar(x=[GOV_LABEL[g] for g in tab.index], y=tab[nivel], name=REPERC_ROTULO[nivel], marker_color=REPERC_COR[nivel],
                                     text=tab[nivel], textposition="inside"))
        fig.update_layout(barmode="stack")
        apply_plotly_theme(fig, title="Políticas com repercussão medida em pesquisa", height=340)
        fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top"))
        st.plotly_chart(fig, use_container_width=True)
        for nivel in ("Boa", "Dividida", "Baixa"):
            sub = medidas[medidas["nivel"] == nivel]
            if sub.empty:
                continue
            with st.expander(f"**{REPERC_ROTULO[nivel]}** — {len(sub)} políticas", expanded=nivel != "Baixa" or len(sub) < 4):
                for _, row in sub.iterrows():
                    render_policy_card(row)
    sem = f[f["nivel"] == "Sem dado"]
    if not sem.empty:
        with st.expander(f"Sem pesquisa encontrada — {len(sem)} políticas"):
            st.caption("Estas políticas não têm medição de opinião pública que consigamos confirmar em fonte aberta.")
            for gov in ("Bolsonaro", "Lula"):
                nomes = sem[sem["governo"] == gov]["politica"].tolist()
                if nomes:
                    st.markdown(f"**{GOV_LABEL[gov]}**: " + "; ".join(nomes))


def _aba_leis(leis):
    st.markdown(
        '<div class="info-box"><b>Leis, leis complementares e emendas sancionadas ou promulgadas:</b> cada número e data foi conferido no texto oficial do Planalto '
        '(link na coluna \"Texto oficial\"). Quando há matéria de imprensa relevante sobre a norma, ela aparece em \"Na imprensa\". '
        'A lista traz as principais normas de cada governo, não todas as milhares sancionadas.</div>',
        unsafe_allow_html=True,
    )
    leis = leis.copy()
    leis["data"] = pd.to_datetime(leis["data"])
    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        gov = st.segmented_control("Governo", ["Ambos", "Bolsonaro", "Lula"], default="Ambos", key="leis_gov") or "Ambos"
    with c2:
        tipos = st.pills("Tipo", sorted(leis["tipo"].unique()), selection_mode="multi", default=sorted(leis["tipo"].unique()), key="leis_tipo") or []
    with c3:
        areas = sorted(leis["area"].unique())
        areas_sel = st.multiselect("Área", areas, default=areas, key="leis_area")
    sit = st.pills("Situação", ["Em vigor ou em implantação", "Perdeu efeito, foi substituída ou alterada", "Aguardando sanção ou promulgação"],
                   selection_mode="multi", default=["Em vigor ou em implantação", "Perdeu efeito, foi substituída ou alterada", "Aguardando sanção ou promulgação"], key="leis_sit") or []

    def faixa(s):
        if s.startswith("Aguardando"):
            return "Aguardando sanção ou promulgação"
        if s.startswith("Em vigor") or s.startswith("Em implantação"):
            return "Em vigor ou em implantação"
        return "Perdeu efeito, foi substituída ou alterada"

    leis["faixa"] = leis["situacao"].map(faixa)
    f = leis[leis["tipo"].isin(tipos) & leis["area"].isin(areas_sel) & leis["faixa"].isin(sit)]
    if gov != "Ambos":
        f = f[f["governo"] == gov]
    if f.empty:
        st.info("Nenhuma norma com esses filtros.")
        return

    cores = {"Bolsonaro": COLOR_BOLSONARO, "Lula": COLOR_LULA}
    fig = go.Figure()
    for g in ("Bolsonaro", "Lula"):
        sub = f[f["governo"] == g]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(x=sub["data"], y=sub["area"], mode="markers", name=g, marker=dict(size=12, color=cores[g], line=dict(width=1, color="#0b0f19")),
                                 text=sub["norma"], customdata=sub["resumo"],
                                 hovertemplate="<b>%{text}</b><br>%{x|%d/%m/%Y}<br>%{customdata}<extra></extra>"))
    apply_plotly_theme(fig, title=f"Linha do tempo das normas ({len(f)})", height=max(360, 26 * f["area"].nunique() + 150))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top"))
    st.plotly_chart(fig, use_container_width=True)

    tabela = f.sort_values("data")[["data", "governo", "norma", "area", "resumo", "situacao", "texto_oficial", "manchete", "url_imprensa"]]
    st.dataframe(
        tabela, use_container_width=True, hide_index=True, height=560,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"), "governo": "Governo", "norma": "Norma", "area": "Área",
            "resumo": st.column_config.TextColumn("O que faz", width="large"), "situacao": st.column_config.TextColumn("Situação", width="medium"),
            "texto_oficial": st.column_config.LinkColumn("Texto oficial", display_text="Planalto ↗"),
            "manchete": st.column_config.TextColumn("Na imprensa", width="large"),
            "url_imprensa": st.column_config.LinkColumn("Link", display_text="ler ↗"),
        },
    )
    st.download_button("📥 Baixar normas (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"), file_name="normas_sancionadas_bolsonaro_lula.csv", mime="text/csv")


def render_tab_policy_balance():
    render_section_header(
        "📜 Políticas de Governo: Impactos Positivos e Negativos",
        "As principais políticas dos governos Bolsonaro e Lula em todas as áreas — o que cada uma trouxe de bom e de ruim, o que ainda está em vigor, "
        "como foi recebida pela população e quais leis foram sancionadas.",
    )

    df = get_politicas_data()
    leis = get_leis_data()
    if df.empty:
        st.warning("Base de políticas não encontrada (data/politicas.json).")
        return

    areas = list(dict.fromkeys(df["area"]))
    status_opts = list(STATUS_COR)
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            gov_sel = st.segmented_control("Governo", ["Ambos", "Bolsonaro", "Lula"], default="Ambos", key="pol_gov") or "Ambos"
            layout = st.segmented_control("Exibição (aba Por área)", ["Lado a lado por área", "Lista"], default="Lado a lado por área", key="pol_layout") or "Lado a lado por área"
        with c2:
            area_sel = st.pills("Áreas", areas, selection_mode="multi", default=areas, key="pol_areas") or []
        status_sel = st.pills("Situação atual", status_opts, selection_mode="multi", default=status_opts, key="pol_status") or []
        busca = st.text_input("Buscar", "", placeholder="Ex.: Previdência, armas, desmatamento, Bolsa Família, INSS...", key="pol_busca")

    f = _filtrar(df, gov_sel, area_sel, status_sel, busca)

    n_rep = int((df["repercussao"].apply(lambda r: r["nivel"]) != "Sem dado").sum())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Políticas mapeadas", len(df))
    k2.metric("Ainda em vigor", int((df["status_categoria"] == "Em vigor").sum()))
    k3.metric("Deixaram de valer", int((df["status_categoria"] == "Deixou de valer").sum()))
    k4.metric("Com repercussão medida", n_rep)

    abas = st.tabs(["🗂️ Por área", "🚫 O que deixou de valer", "📣 Repercussão", "🏛️ Leis sancionadas"])
    with abas[0]:
        if f.empty:
            st.info("Nenhuma política com esses filtros.")
        else:
            _aba_por_area(f, areas, layout, area_sel, busca)
            st.download_button("📥 Baixar políticas (CSV)", f.drop(columns=["repercussao"]).to_csv(index=False).encode("utf-8-sig"),
                               file_name="politicas_bolsonaro_lula.csv", mime="text/csv")
    with abas[1]:
        _aba_deixou_de_valer(f if not f.empty else df.iloc[0:0], leis)
    with abas[2]:
        _aba_repercussao(f if not f.empty else df.iloc[0:0])
    with abas[3]:
        if leis.empty:
            st.info("Base de leis não encontrada (data/leis_sancionadas.json).")
        else:
            _aba_leis(leis)
