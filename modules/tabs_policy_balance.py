import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_politicas_data, get_leis_data
from modules.ui_components import apply_plotly_theme, render_section_header, COLOR_LULA, COR_MANDATO, PARTIDO, PERIODO
from modules.ux import gl

# Na base de Bolsonaro x Lula o governo atual se chama "Lula"; nas demais bases, "Lula 3"
GOV_LABEL = {"Bolsonaro": "Governo Bolsonaro (2019–2022)", "Lula": "Governo Lula (2023–2026)"}
STATUS_COR = {
    "Em vigor": "#10B981", "Em vigor em parte": "#F59E0B", "Deixou de valer": "#EF4444",
    "Concluída": "#94A3B8", "Em tramitação ou disputa": "#38BDF8",
}
REPERC_COR = {"Boa": "#10B981", "Dividida": "#F59E0B", "Baixa": "#EF4444", "Sem dado": "#64748B"}
REPERC_ROTULO = {"Boa": "Boa repercussão", "Dividida": "Repercussão dividida", "Baixa": "Baixa repercussão", "Sem dado": "Sem pesquisa encontrada"}


def _cor(g):
    return COLOR_LULA if g == "Lula" else COR_MANDATO.get(g, "#94A3B8")


def _label(g):
    return GOV_LABEL.get(g) or f"{g} · {PARTIDO.get(g, '')} ({PERIODO.get(g, '')})"


def _k(base, govs):
    """Chave de widget que muda com o par de governos, para o estado não vazar de um par para outro."""
    return f"{base}_{'_'.join(govs)}"


def _por_governo(govs, desenhar):
    """Até dois governos lado a lado; mais que isso em abas. desenhar(gov) renderiza o conteúdo de um governo."""
    if len(govs) <= 2:
        for col, g in zip(st.columns(len(govs)), govs):
            with col:
                st.markdown(f"**{_label(g)}**")
                desenhar(g)
    else:
        for aba, g in zip(st.tabs(list(govs)), govs):
            with aba:
                st.markdown(f"**{_label(g)}**")
                desenhar(g)


def _chip(texto, cor, escuro=True):
    return f'<span class="verdict-pill" style="background:{cor};{"" if escuro else "color:#fff !important;"}">{html.escape(texto)}</span>'


def _lista_fontes(itens):
    saida = []
    for i in itens:
        txt = html.escape(i["texto"])
        if i.get("url"):
            txt += f' <a href="{html.escape(i["url"], quote=True)}" target="_blank">{html.escape(i["fonte"])} ↗</a>'
        elif i.get("fonte"):
            txt += f' <span class="src">({html.escape(i["fonte"])})</span>'
        saida.append(f"<li>{txt}</li>")
    return "<ul>" + "".join(saida) + "</ul>"


def render_policy_card(row):
    gov = row["governo"]
    cor = _cor(gov)
    rep = row.get("repercussao") if hasattr(row, "get") else None
    rep = rep if isinstance(rep, dict) else {"nivel": "Sem dado", "evidencia": "", "fonte": "", "url": ""}
    cat = row.get("status_categoria", "Em vigor") if hasattr(row, "get") else "Em vigor"
    if rep["nivel"] != "Sem dado":
        link = f' <a href="{rep["url"]}" target="_blank">{html.escape(rep["fonte"])} ↗</a>' if rep.get("url") else ""
        bloco_rep = (f'<div class="policy-rep" style="border-left-color:{REPERC_COR[rep["nivel"]]};"><b>{REPERC_ROTULO[rep["nivel"]]}:</b> '
                     f'{html.escape(rep["evidencia"])}{link}</div>')
    else:
        bloco_rep = '<div class="policy-rep" style="border-left-color:#64748B;"><b>Repercussão:</b> sem pesquisa de opinião encontrada.</div>'
    pos_itens, neg_itens = row.get("pos_itens"), row.get("neg_itens")
    pos = _lista_fontes(pos_itens) if isinstance(pos_itens, list) and pos_itens else html.escape(row["impactos_positivos"])
    neg = _lista_fontes(neg_itens) if isinstance(neg_itens, list) and neg_itens else html.escape(row["impactos_negativos"])
    st.markdown(gl(
        f'<div class="policy-card" style="border-top:3px solid {cor};">'
        f'<div class="check-meta"><span class="prog-gov" style="background:{cor};">{html.escape(gov)}</span>'
        f'<span>· {html.escape(str(row["ano"]))}</span><span>· {html.escape(row["area"])}</span>'
        f'{_chip(cat, STATUS_COR.get(cat, "#94A3B8"))}</div>'
        f'<div class="policy-title">{html.escape(row["politica"])}</div>'
        f'<div class="policy-desc">{html.escape(row["descricao"])}</div>'
        f'<div class="policy-pos">✔ <b>Impactos positivos:</b> {pos}</div>'
        f'<div class="policy-neg">⚠ <b>Impactos negativos e críticas:</b> {neg}</div>'
        f'{bloco_rep}'
        f'<div class="policy-foot">Situação: {html.escape(row["status"])} · Fonte: {html.escape(row["fonte"])}</div>'
        '</div>'),
        unsafe_allow_html=True,
    )


def _filtrar(df, gov_sel, areas_sel, status_sel, busca):
    f = df[df["area"].isin(areas_sel) & df["governo"].isin(gov_sel)]
    if status_sel:
        f = f[f["status_categoria"].isin(status_sel)]
    if busca:
        texto = f[["politica", "descricao", "impactos_positivos", "impactos_negativos"]].agg(" ".join, axis=1)
        f = f[texto.str.contains(busca, case=False, regex=False)]
    return f


def _aba_por_area(f, areas, layout, area_sel, busca, govs):
    contagem = f.groupby(["area", "governo"]).size().unstack(fill_value=0).reindex([a for a in areas if a in set(f["area"])])
    fig = go.Figure()
    for gov in govs:
        if gov in contagem.columns:
            fig.add_trace(go.Bar(y=contagem.index, x=contagem[gov], name=_label(gov), orientation="h", marker_color=_cor(gov),
                                 hovertemplate="%{y}: %{x} políticas<extra>" + gov + "</extra>"))
    fig.update_layout(barmode="group")
    apply_plotly_theme(fig, title=f"Políticas mapeadas por área (nº de políticas; {len(f)} no filtro atual)", height=max(320, (30 if len(govs) <= 2 else 14 * len(govs)) * len(contagem) + 140))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")

    if layout == "Lista":
        for _, row in f.iterrows():
            render_policy_card(row)
        return
    for area in [a for a in areas if a in set(f["area"])]:
        sub = f[f["area"] == area]
        with st.expander(f"**{area}** — {len(sub)} {'política' if len(sub) == 1 else 'políticas'}", expanded=len(area_sel) <= 2 or bool(busca)):
            def desenhar(gov, sub=sub):
                parte = sub[sub["governo"] == gov]
                if parte.empty:
                    st.caption("Nenhuma política nesta área com os filtros atuais.")
                for _, row in parte.iterrows():
                    render_policy_card(row)
            _por_governo(govs, desenhar)


def _aba_deixou_de_valer(df, leis, govs, todas):
    st.markdown(
        '<div class="info-box"><b>O que de fato deixou de estar em vigor:</b> políticas revogadas, substituídas, encerradas ou derrubadas pela Justiça '
        'ou pelo Congresso. "Em vigor em parte" indica que só uma parte foi revertida. A coluna de situação reproduz o que ocorreu com cada uma.</div>',
        unsafe_allow_html=True,
    )
    f = df[df["status_categoria"].isin(["Deixou de valer", "Em vigor em parte"])].copy()
    cols = st.columns(3)
    cols[0].metric("Deixaram de valer", int((f["status_categoria"] == "Deixou de valer").sum()))
    cols[1].metric("Em vigor em parte", int((f["status_categoria"] == "Em vigor em parte").sum()))
    cols[2].metric("Ainda em vigor (todas as políticas)", int((todas["status_categoria"] == "Em vigor").sum()))
    tabela = f[["governo", "ano", "area", "politica", "status_categoria", "status"]].rename(columns={
        "governo": "Governo", "ano": "Período", "area": "Área", "politica": "Política", "status_categoria": "Faixa", "status": "O que aconteceu"})
    from modules.ui_components import mostrar_tabela
    mostrar_tabela(tabela, titulo_col="Política", width="stretch", hide_index=True, height=min(80 + 36 * len(tabela), 640),
                 column_config={"Política": st.column_config.TextColumn(width="large"), "O que aconteceu": st.column_config.TextColumn(width="medium")})

    if not leis.empty:
        fim = leis[leis["governo"].isin(govs) & ~leis["situacao"].str.startswith("Em vigor") & ~leis["situacao"].str.startswith("Em implantação")]
        if not fim.empty:
            st.subheader("Normas sancionadas que perderam efeito ou foram alteradas")
            t = fim[["data", "governo", "norma", "resumo", "situacao"]].rename(columns={"data": "Data", "governo": "Governo", "norma": "Norma", "resumo": "O que fazia", "situacao": "Situação"})
            mostrar_tabela(t, titulo_col="Norma", width="stretch", hide_index=True,
                         column_config={"Data": st.column_config.DateColumn(format="DD/MM/YYYY"), "O que fazia": st.column_config.TextColumn(width="large")})
    st.subheader("Detalhe das políticas que deixaram de valer")

    def desenhar(gov):
        parte = f[f["governo"] == gov]
        if parte.empty:
            st.caption("Nenhuma com os filtros atuais.")
        for _, row in parte.iterrows():
            render_policy_card(row)
    _por_governo(govs, desenhar)


def _aba_repercussao(f, govs):
    st.markdown(
        '<div class="info-box"><b>Repercussão:</b> o que pesquisas de opinião (Datafolha, Quaest, AtlasIntel e outras) e a imprensa registraram sobre cada política. '
        'Só aparece quando encontramos pesquisa ou cobertura confiável, nunca por suposição. Algumas pesquisas medem a popularidade do governo ou de um reajuste, '
        'não da política inteira (isso está dito em cada caso). Pesquisas encomendadas por governos ou campanhas estão sinalizadas.</div>',
        unsafe_allow_html=True,
    )
    f = f.copy()
    f["nivel"] = f["repercussao"].apply(lambda r: r["nivel"])
    medidas = f[f["nivel"] != "Sem dado"]
    sem_cobertura = [g for g in govs if g not in set(medidas["governo"])]
    if sem_cobertura and len(sem_cobertura) < len(govs):
        st.caption("Sem repercussão medida em pesquisa para: " + ", ".join(sem_cobertura) + ". Só Bolsonaro e Lula 3 têm esse dado mapeado.")
    if medidas.empty:
        st.info("Nenhuma política com repercussão medida nos governos escolhidos. A repercussão em pesquisas só foi mapeada para Bolsonaro e Lula 3.")
    else:
        tab = medidas.groupby(["governo", "nivel"]).size().unstack(fill_value=0)
        fig = go.Figure()
        for nivel in ("Boa", "Dividida", "Baixa"):
            if nivel in tab.columns:
                fig.add_trace(go.Bar(x=[_label(g) for g in tab.index], y=tab[nivel], name=REPERC_ROTULO[nivel], marker_color=REPERC_COR[nivel],
                                     text=tab[nivel], textposition="inside"))
        fig.update_layout(barmode="stack")
        apply_plotly_theme(fig, title="Políticas com repercussão medida em pesquisa (nº de políticas)", height=340)
        fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top"))
        st.plotly_chart(fig, width="stretch")
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
            for gov in govs:
                nomes = sem[sem["governo"] == gov]["politica"].tolist()
                if nomes:
                    st.markdown(f"**{_label(gov)}**: " + "; ".join(nomes))


def _aba_leis(leis, govs):
    st.markdown(
        '<div class="info-box"><b>Leis, leis complementares e emendas sancionadas ou promulgadas:</b> cada número e data foi conferido no texto oficial do Planalto '
        '(link na coluna "Texto oficial"). Quando há matéria de imprensa relevante sobre a norma, ela aparece em "Na imprensa". '
        'A lista traz as principais normas de cada governo, não todas as milhares sancionadas.</div>',
        unsafe_allow_html=True,
    )
    leis = leis[leis["governo"].isin(govs)].copy()
    leis["data"] = pd.to_datetime(leis["data"])
    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        if len(govs) == 2:
            esc = st.segmented_control("Governo", ["Ambos"] + list(govs), default="Ambos", key=_k("leis_gov", govs)) or "Ambos"
            sel = list(govs) if esc == "Ambos" else [esc]
        else:
            sel = st.pills("Governos", list(govs), selection_mode="multi", default=list(govs), key=_k("leis_gov", govs)) or []
    with c2:
        tipos = st.pills("Tipo", sorted(leis["tipo"].unique()), selection_mode="multi", default=sorted(leis["tipo"].unique()), key=_k("leis_tipo", govs)) or []
    with c3:
        areas = sorted(leis["area"].unique())
        areas_sel = st.multiselect("Área", areas, default=areas, key=_k("leis_area", govs))
    faixas = ["Em vigor ou em implantação", "Perdeu efeito, foi substituída ou alterada", "Aguardando sanção ou promulgação"]
    sit = st.pills("Situação", faixas, selection_mode="multi", default=faixas, key=_k("leis_sit", govs)) or []

    def faixa(s):
        if s.startswith("Aguardando"):
            return faixas[2]
        if s.startswith("Em vigor") or s.startswith("Em implantação"):
            return faixas[0]
        return faixas[1]

    leis["faixa"] = leis["situacao"].map(faixa)
    f = leis[leis["tipo"].isin(tipos) & leis["area"].isin(areas_sel) & leis["faixa"].isin(sit) & leis["governo"].isin(sel)]
    if f.empty:
        st.info("Nenhuma norma com esses filtros.")
        return
    contagem = f.groupby("governo").size().reindex([g for g in govs if g in sel]).fillna(0).astype(int)
    st.caption("Normas por governo: " + " · ".join(f"{g}: {n}" for g, n in contagem.items()))

    fig = go.Figure()
    for g in govs:
        sub = f[f["governo"] == g]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(x=sub["data"], y=sub["area"], mode="markers", name=g, marker=dict(size=12, color=_cor(g), line=dict(width=1, color="#0b0f19")),
                                 text=sub["norma"], customdata=sub["resumo"],
                                 hovertemplate="<b>%{text}</b><br>%{x|%d/%m/%Y}<br>%{customdata}<extra></extra>"))
    apply_plotly_theme(fig, title=f"Linha do tempo das normas ({len(f)})", height=max(360, 26 * f["area"].nunique() + 150))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top"))
    st.plotly_chart(fig, width="stretch")

    tabela = f.sort_values("data")[["data", "governo", "norma", "area", "resumo", "situacao", "texto_oficial", "manchete", "url_imprensa"]]
    st.dataframe(
        tabela, width="stretch", hide_index=True, height=560,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"), "governo": "Governo", "norma": "Norma", "area": "Área",
            "resumo": st.column_config.TextColumn("O que faz", width="large"), "situacao": st.column_config.TextColumn("Situação", width="medium"),
            "texto_oficial": st.column_config.LinkColumn("Texto oficial", display_text="Planalto ↗"),
            "manchete": st.column_config.TextColumn("Na imprensa", width="large"),
            "url_imprensa": st.column_config.LinkColumn("Link", display_text="ler ↗"),
        },
    )
    st.download_button("Baixar normas (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"), file_name="normas_sancionadas_governos.csv", mime="text/csv")


def render_tab_policy_balance():
    from modules.historico_ui import render_seletor, PADRAO, nomes_governos
    from modules.politicas_comparadas import politicas_unificadas, leis_unificadas
    from modules.politicas_impostos import render_impostos

    a, b, todos = render_seletor()
    padrao = (a, b) == PADRAO and not todos
    if a == b and not todos:
        st.info("Escolha dois governos diferentes.")
        return
    if padrao:
        govs = ["Bolsonaro", "Lula"]
        df, leis = get_politicas_data(), get_leis_data()
        subtitulo = ("As principais políticas dos governos Bolsonaro e Lula em todas as áreas: o que cada uma trouxe de bom e de ruim, o que ainda está em vigor, "
                     "como foi recebida pela população, quais leis foram sancionadas e quais impostos cada governo criou, reduziu ou extinguiu.")
    else:
        from modules.historico_ui import governos_ativos
        govs = governos_ativos(todos, a, b)
        df, leis = politicas_unificadas(govs), leis_unificadas()
        subtitulo = ("As principais políticas, leis e impostos de " + ("todos os governos, de FHC a Lula 3" if todos else f"{a} e {b}") +
                     ": o que cada uma trouxe de bom e de ruim, o que ainda está em vigor e quais leis foram sancionadas. "
                     "Os governos anteriores a 2019 têm menos políticas mapeadas, e a repercussão em pesquisas só existe para Bolsonaro e Lula 3.")
    render_section_header("Políticas de Governo: Impactos Positivos e Negativos", subtitulo)
    if df.empty:
        st.warning("Base de políticas não encontrada.")
        return

    if not padrao:
        n_prog = {g: int((df["governo"] == g).sum()) for g in govs}
        n_leis = {g: int((leis["governo"] == g).sum()) for g in govs}
        linhas = "".join(f"<li><b>{g}</b> ({PARTIDO[g]}, {PERIODO[g]}): {n_prog[g]} políticas e {n_leis[g]} leis</li>" for g in govs)
        st.markdown(f'<div class="info-box"><b>O que o painel tem de cada governo selecionado:</b><ul style="margin-bottom:0;">{linhas}</ul>'
                    'As políticas são uma seleção das mais conhecidas e vão sendo ampliadas; as leis cobrem todas as áreas.</div>', unsafe_allow_html=True)

    areas = list(dict.fromkeys(df["area"]))
    status_opts = list(STATUS_COR)
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            if padrao:
                esc = st.segmented_control("Governo", ["Ambos", "Bolsonaro", "Lula"], default="Ambos", key="pol_gov") or "Ambos"
                gov_sel = govs if esc == "Ambos" else [esc]
            else:
                gov_sel = st.pills("Governos", govs, selection_mode="multi", default=govs, key=_k("pol_gov", govs)) or []
            layout = st.segmented_control("Exibição (aba Por área)", ["Lado a lado por área", "Lista"], default="Lado a lado por área", key=_k("pol_layout", govs)) or "Lado a lado por área"
        with c2:
            area_sel = st.pills("Áreas", areas, selection_mode="multi", default=areas, key=_k("pol_areas", govs)) or []
        status_sel = st.pills("Situação atual", status_opts, selection_mode="multi", default=status_opts, key=_k("pol_status", govs)) or []
        busca = st.text_input("Buscar", "", placeholder="Ex.: Previdência, armas, desmatamento, Bolsa Família, INSS...", key=_k("pol_busca", govs))

    f = _filtrar(df, gov_sel, area_sel, status_sel, busca)
    govs_ver = [g for g in govs if g in gov_sel] or govs

    n_rep = int((df["repercussao"].apply(lambda r: r["nivel"]) != "Sem dado").sum())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Políticas mapeadas", len(df))
    k2.metric("Ainda em vigor", int((df["status_categoria"] == "Em vigor").sum()))
    k3.metric("Deixaram de valer", int((df["status_categoria"] == "Deixou de valer").sum()))
    k4.metric("Com repercussão medida", n_rep)

    abas = st.tabs(["Por área", "O que deixou de valer", "Repercussão", "Leis sancionadas", "Impostos"])
    with abas[0]:
        if f.empty:
            st.info("Nenhuma política com esses filtros.")
        else:
            _aba_por_area(f, areas, layout, area_sel, busca, govs_ver)
            st.download_button("Baixar políticas (CSV)", f.drop(columns=[c for c in ("repercussao", "pos_itens", "neg_itens") if c in f.columns]).to_csv(index=False).encode("utf-8-sig"),
                               file_name="politicas_governos.csv", mime="text/csv")
    with abas[1]:
        _aba_deixou_de_valer(f if not f.empty else df.iloc[0:0], leis, govs_ver, df)
    with abas[2]:
        _aba_repercussao(f if not f.empty else df.iloc[0:0], govs_ver)
    with abas[3]:
        if leis.empty:
            st.info("Base de leis não encontrada.")
        else:
            _aba_leis(leis, govs)
    with abas[4]:
        render_impostos(govs)
