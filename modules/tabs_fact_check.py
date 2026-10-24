import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_checagens_data, load_json
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    VERDICT_COLORS,
    VERDICT_ORDER,
)

CANDIDATOS = ["Lula", "Flávio Bolsonaro"]
CAND_CLASS = {"Lula": "lula", "Flávio Bolsonaro": "flavio"}
CAND_LABEL = {"Lula": "Lula (PT)", "Flávio Bolsonaro": "Flávio Bolsonaro (PL)"}
CAT_ICON = {"Verdade": "✔", "Meia-verdade": "≈", "Mentira": "✖", "Sem comprovação": "?"}
PLURAL = {"Verdade": "Verdades", "Meia-verdade": "Meias-verdades", "Mentira": "Mentiras", "Sem comprovação": "Sem comprovação"}
SEVERIDADE = {"Verdade": 0, "Meia-verdade": 1, "Sem comprovação": 2, "Mentira": 3}
MODO_UNICO = "Falas únicas (sem repetição)"
MODO_TODAS = "Todas as checagens (por agência)"
VER_TUDO, VER_EMISSORA, VER_TURNO, VER_CANDIDATO = "Tudo", "Por emissora", "Por turno", "Por candidato"


def _curto(evento):
    return evento.replace("Entrevista TV Globo — ", "Globo ").replace("Debate Band — ", "Band ").replace("Debate TV Globo — ", "Debate Globo ")


def _quote(texto):
    """Coloca aspas só quando a fala já não vem citada literalmente."""
    texto = texto.strip()
    if texto.startswith('"'):
        return html.escape(texto)
    return f"“{html.escape(texto)}”"


def _consolidar(f, contrapontos):
    """Agrupa as checagens filtradas por fala (mesma fala em várias agências ou eventos).
    A faixa final é a mais frequente; em empate com Meia-verdade, vira Meia-verdade, senão a menos grave."""
    linhas = []
    for chave, g in f.groupby("chave", sort=False):
        cats = g["categoria"].value_counts()
        empatadas = cats[cats == cats.max()].index.tolist()
        categoria = "Meia-verdade" if "Meia-verdade" in empatadas else min(empatadas, key=SEVERIDADE.get)
        g = g.sort_values(["data", "agencia"])
        primeiro = g.iloc[0]
        linhas.append({
            "chave": chave, "candidato": primeiro["candidato"], "fala": primeiro["titulo_fala"], "tema": primeiro["tema"],
            "categoria": categoria, "divergencia": g["categoria"].nunique() > 1, "n_checagens": len(g),
            "n_eventos": g["data"].nunique(), "data": primeiro["data"],
            "eventos": sorted(set(g["rotulo_evento"])), "vereditos": g.to_dict("records"),
            "contrapontos": contrapontos.get(chave, []),
        })
    return pd.DataFrame(linhas)


def _score_tile(cats, candidato, unidade):
    total = len(cats)
    counts = cats.value_counts()
    segs, legend = [], []
    for cat in VERDICT_ORDER:
        n = int(counts.get(cat, 0))
        pct = 100 * n / total if total else 0
        if n:
            segs.append(f'<div style="width:{pct:.2f}%; background:{VERDICT_COLORS[cat]};" title="{cat}: {n}"></div>')
        legend.append(f'<div><span class="dot" style="background:{VERDICT_COLORS[cat]}"></span>{cat}: <b>{n}</b> ({pct:.0f}%)</div>')
    cor = "#fca5a5" if candidato == "Lula" else "#93c5fd"
    st.markdown(
        '<div class="score-tile">'
        f'<h4 style="color:{cor};">{CAND_LABEL[candidato]} <span style="color:#94a3b8; font-size:0.8rem; font-weight:600;">· {total} {unidade}</span></h4>'
        f'<div class="score-bar">{"".join(segs)}</div>'
        f'<div class="score-legend">{"".join(legend)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _pill(texto, categoria):
    return f'<span class="verdict-pill" style="background:{VERDICT_COLORS[categoria]};">{html.escape(texto)}</span>'


def _check_card(row):
    """Cartão de uma checagem individual (modo 'todas as checagens')."""
    cor = VERDICT_COLORS[row["categoria"]]
    data_fmt = pd.to_datetime(row["data"]).strftime("%d/%m/%Y")
    st.markdown(
        f'<div class="check-card" style="border-left-color:{cor};">'
        '<div class="check-meta">'
        f'{_pill(row["veredito_original"], row["categoria"])}'
        f'<span class="cand-tag {CAND_CLASS[row["candidato"]]}">{html.escape(row["candidato"])}</span>'
        f'<span>· {html.escape(row["evento"])} ({data_fmt})</span>'
        f'<span>· {html.escape(row["tema"])}</span>'
        '</div>'
        f'<div class="check-quote">{_quote(row["afirmacao"])}</div>'
        f'<div class="check-expl">{html.escape(row["explicacao"])} '
        f'<a href="{row["fonte_url"]}" target="_blank">{html.escape(row["agencia"])} ↗</a></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _fala_card(row):
    """Cartão de uma fala única: vereditos de todas as agências + contrapontos."""
    cor = VERDICT_COLORS[row["categoria"]]
    selos = []
    if row["n_checagens"] > 1:
        selos.append(f'<span class="tag-soft">checada {row["n_checagens"]}x</span>')
    if row["n_eventos"] > 1:
        selos.append(f'<span class="tag-soft">repetida em {row["n_eventos"]} eventos</span>')
    if row["divergencia"]:
        selos.append('<span class="tag-warn">⚠ agências divergem</span>')
    if row["contrapontos"]:
        selos.append('<span class="tag-soft">com contraponto</span>')

    vereditos = "".join(
        '<div class="verdict-line">'
        f'{_pill(v["veredito_original"], v["categoria"])} '
        f'<b>{html.escape(v["agencia"])}</b> · {html.escape(v["rotulo_evento"])} — '
        f'{html.escape(v["explicacao"])} <a href="{v["fonte_url"]}" target="_blank">abrir ↗</a>'
        '</div>'
        for v in row["vereditos"]
    )
    st.markdown(
        f'<div class="check-card" style="border-left-color:{cor};">'
        '<div class="check-meta">'
        f'{_pill(row["categoria"], row["categoria"])}'
        f'<span class="cand-tag {CAND_CLASS[row["candidato"]]}">{html.escape(row["candidato"])}</span>'
        f'<span>· {html.escape(row["tema"])}</span>{"".join(selos)}'
        '</div>'
        f'<div class="check-quote">{_quote(row["fala"])}</div>'
        f'<div class="check-expl">{vereditos}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if row["contrapontos"]:
        with st.expander("Contrapontos — o outro lado e outros veículos"):
            for cp in row["contrapontos"]:
                classe = "cp-favor" if cp["lado"].startswith("A favor") else "cp-contra"
                st.markdown(
                    f'<div class="cp-box {classe}"><b>{html.escape(cp["lado"])}</b> · <i>{html.escape(cp["fonte"])}</i><br/>'
                    f'{html.escape(cp["texto"])} <a href="{cp["url"]}" target="_blank">fonte ↗</a></div>',
                    unsafe_allow_html=True,
                )


def _chart_by_event(f):
    """Barras empilhadas (%) por evento e candidato, sobre as checagens filtradas."""
    df = f.copy()
    curto = df["evento"].map(_curto)
    df["grupo"] = "<b>" + df["candidato"].str.replace(" Bolsonaro", "", regex=False) + "</b><br>" + curto + "<br>" + pd.to_datetime(df["data"]).dt.strftime("%d/%m")
    ordem = df[["data", "candidato", "grupo"]].drop_duplicates().sort_values(["data", "candidato"])["grupo"].tolist()
    tab = df.groupby(["grupo", "categoria"]).size().unstack(fill_value=0).reindex(ordem)
    pct = tab.div(tab.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for cat in VERDICT_ORDER:
        if cat not in tab.columns:
            continue
        fig.add_trace(go.Bar(
            x=pct.index, y=pct[cat], name=cat, marker_color=VERDICT_COLORS[cat],
            customdata=tab[cat], text=[f"{v:.0f}%" if v >= 7 else "" for v in pct[cat]],
            textposition="inside", insidetextfont=dict(color="#0b0f19", size=11),
            hovertemplate="%{x}<br>" + cat + ": %{customdata} (%{y:.0f}%)<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    apply_plotly_theme(fig, title="Vereditos por evento (% das checagens)", height=430)
    fig.update_layout(hovermode="closest", yaxis=dict(range=[0, 100], ticksuffix="%"), margin=dict(t=60, b=40),
                      legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", yanchor="top"))
    fig.update_xaxes(tickangle=0, tickfont=dict(size=10))
    return fig


def _chart_by_theme(u):
    """Falas únicas falsas ou sem comprovação, por tema."""
    ruins = u[u["categoria"].isin(["Mentira", "Sem comprovação"])]
    tab = ruins.groupby(["tema", "candidato"]).size().unstack(fill_value=0)
    for c in CANDIDATOS:
        if c not in tab.columns:
            tab[c] = 0
    tab = tab.loc[tab.sum(axis=1).sort_values().index]
    fig = go.Figure()
    for cand, cor in (("Lula", "#EF2B2D"), ("Flávio Bolsonaro", "#3B82F6")):
        fig.add_trace(go.Bar(y=tab.index, x=tab[cand], name=cand, orientation="h", marker_color=cor,
                             hovertemplate="%{y}<br>" + cand + ": %{x}<extra></extra>"))
    fig.update_layout(barmode="group")
    apply_plotly_theme(fig, title="Falas falsas ou sem comprovação, por tema (falas únicas)", height=max(360, 34 * len(tab) + 150))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", yanchor="top"))
    return fig


def _conteudo(f, contrapontos, unico, cands, chave):
    """Placar, gráficos, listas por veredito e tabela para um recorte das checagens (todo o conjunto ou um grupo)."""
    u = _consolidar(f, contrapontos)
    base, unidade = (u, "falas únicas") if unico else (f, "checagens")

    st.subheader("Placar por candidato")
    st.caption(f"{len(f)} checagens filtradas correspondem a {len(u)} falas diferentes "
               f"({len(f) - len(u)} repetições removidas na visão de falas únicas).")
    for col, cand in zip(st.columns(len(cands)), cands):
        with col:
            _score_tile(base[base["candidato"] == cand]["categoria"], cand, unidade)

    g1, g2 = st.columns([1.25, 1])
    with g1:
        st.plotly_chart(_chart_by_event(f), width="stretch", key=f"{chave}_ev")
    with g2:
        st.plotly_chart(_chart_by_theme(u), width="stretch", key=f"{chave}_tema")
    render_source("Agência Lupa, Aos Fatos, Ranking dos Políticos e Estadão Verifica; contrapontos de Poder360, Metrópoles, Revista Oeste, "
                  "Gazeta do Povo, Instituto Mises, Agência Câmara e Datafolha/FBSP — compilação de 24/10/2026")

    st.subheader("Todas as falas checadas")
    abas = st.tabs([f"{CAT_ICON[c]} {PLURAL[c]} ({int((base['categoria'] == c).sum())})" for c in VERDICT_ORDER] + ["Tabela completa"])
    for aba, cat in zip(abas[:4], VERDICT_ORDER):
        with aba:
            sub = base[base["categoria"] == cat].sort_values("data")
            for col, cand in zip(st.columns(len(cands)), cands):
                with col:
                    parte = sub[sub["candidato"] == cand]
                    st.markdown(f"**{CAND_LABEL[cand]}** — {len(parte)} {unidade}")
                    if parte.empty:
                        st.caption("Nada nesta faixa com os filtros atuais.")
                    for _, row in parte.iterrows():
                        _fala_card(row) if unico else _check_card(row)
    with abas[4]:
        colunas = ["candidato", "data", "evento", "agencia", "tema", "titulo_fala", "afirmacao", "veredito_original", "categoria", "explicacao", "fonte_url"]
        tabela = f[colunas].sort_values(["data", "candidato"])
        st.dataframe(
            tabela, width="stretch", hide_index=True, height=520,
            column_config={
                "candidato": "Candidato", "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "evento": "Evento", "agencia": "Agência", "tema": "Tema",
                "titulo_fala": st.column_config.TextColumn("Fala (agrupada)", width="medium"),
                "afirmacao": st.column_config.TextColumn("Fala (como a agência citou)", width="large"),
                "veredito_original": "Veredito da agência", "categoria": "Faixa",
                "explicacao": st.column_config.TextColumn("Explicação", width="large"),
                "fonte_url": st.column_config.LinkColumn("Fonte", display_text="abrir ↗"),
            },
        )
        st.download_button("Baixar checagens filtradas (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"),
                           file_name="checagens_lula_flavio_2026.csv", mime="text/csv", key=f"{chave}_csv")


def render_tab_fact_check():
    render_section_header(
        "Checagem de Fatos — Eleição Presidencial 2026",
        "O que as agências verificaram nas falas de <b>Lula (PT)</b> e <b>Flávio Bolsonaro (PL)</b> nas entrevistas da TV Globo "
        "e nos debates da Band e da Globo — sem repetições, com o veredito de cada agência e contrapontos de outros veículos.",
    )

    df, meta = get_checagens_data()
    if df.empty:
        st.warning("Base de checagens não encontrada (data/checagens_2026.json).")
        return
    contrapontos = {f["chave"]: f["contrapontos"] for f in load_json("checagens_2026.json").get("falas_unicas", [])}

    st.markdown(
        '<div class="info-box"><b>Como ler esta página:</b> uma mesma fala costuma ser checada por várias agências e repetida pelo candidato '
        'em mais de um evento. Na visão padrão, <b>cada fala aparece uma única vez</b>, com os vereditos de todas as agências; a faixa final é a '
        'mais frequente entre elas, e as falas em que as agências discordam ficam marcadas. Faixas: <b>Verdade</b> (verdadeiro), '
        '<b>Meia-verdade</b> (impreciso, exagerado, subestimado, enganoso, falta contexto), <b>Mentira</b> (falso) e <b>Sem comprovação</b> '
        '(insustentável). Nas falas mais disputadas há <b>contrapontos</b>: o argumento do próprio candidato e de veículos com linhas editoriais '
        f'diferentes, porque o enquadramento também depende do ponto de vista. {html.escape(meta.get("cobertura", ""))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="info-box"><b>Debate da Globo (23/10):</b> '
        f'{html.escape(meta.get("debate_globo", ""))} '
        '<a href="https://www.agencialupa.org/checagem/2026/10/23/ao-vivo-checagem-do-ultimo-debate-entre-lula-e-flavio-bolsonaro-no-segundo-turno/" target="_blank">Lupa ao vivo ↗</a> · '
        '<a href="https://www.aosfatos.org/noticias/checamos-flavio-bolsonaro-lula-debate-globo/" target="_blank">Aos Fatos ao vivo ↗</a>. '
        'As agências incluídas são Lupa, Aos Fatos, Ranking dos Políticos e Estadão Verifica. UOL Confere e Projeto Comprova não trouxeram veredito '
        'explícito sobre falas dos dois candidatos, então não entram na contagem, em vez de classificar por conta própria.</div>',
        unsafe_allow_html=True,
    )
    if meta.get("metodo_aos_fatos"):
        st.markdown('<div class="info-box"><b>Como o painel registra cada agência:</b> ' + html.escape(meta["metodo_aos_fatos"]) + '</div>', unsafe_allow_html=True)

    # ---------------- Filtros
    df["rotulo_evento"] = (df["evento"] + " (" + pd.to_datetime(df["data"]).dt.strftime("%d/%m") + ")").map(_curto)
    with st.container(border=True):
        c0, c00 = st.columns([1, 1.2])
        with c0:
            ver = st.segmented_control("Ver", [VER_TUDO, VER_EMISSORA, VER_TURNO, VER_CANDIDATO], default=VER_TUDO, key="fc_ver",
                                       help="Tudo mostra um placar só. Por emissora, por turno ou por candidato separa o resultado em abas.") or VER_TUDO
        with c00:
            modo = st.segmented_control("Visualização", [MODO_UNICO, MODO_TODAS], default=MODO_UNICO, key="fc_modo") or MODO_UNICO
        c1, c2, c3 = st.columns([1.3, 1.3, 1])
        with c1:
            agencias = sorted(df["agencia"].unique())
            ag_sel = st.pills("Agências", agencias, selection_mode="multi", default=agencias, key="fc_ag") or []
        with c2:
            ev_opts = df[["data", "rotulo_evento"]].drop_duplicates().sort_values("data")["rotulo_evento"].tolist()
            ev_sel = st.pills("Eventos", ev_opts, selection_mode="multi", default=ev_opts, key="fc_ev") or []
        with c3:
            temas = ["Todos os temas"] + sorted(df["tema"].unique())
            tema_sel = st.selectbox("Tema", temas, key="fc_tema")
            so_cp = st.toggle("Só falas com contraponto", key="fc_cp")
        busca = st.text_input("Buscar nas falas e explicações", "", placeholder="Ex.: PIB, déficit, Vorcaro, armas, Bolsa Família...", key="fc_busca")

    f = df[df["agencia"].isin(ag_sel) & df["rotulo_evento"].isin(ev_sel)]
    if tema_sel != "Todos os temas":
        f = f[f["tema"] == tema_sel]
    if so_cp:
        f = f[f["chave"].isin([k for k, v in contrapontos.items() if v])]
    if busca:
        mask = (f["afirmacao"].str.contains(busca, case=False, regex=False)
                | f["explicacao"].str.contains(busca, case=False, regex=False)
                | f["titulo_fala"].str.contains(busca, case=False, regex=False))
        f = f[mask]

    if f.empty:
        st.info("Nenhuma checagem com esses filtros.")
        return

    unico = modo == MODO_UNICO
    if ver == VER_TUDO:
        _conteudo(f, contrapontos, unico, CANDIDATOS, "fc_tudo")
    else:
        coluna = {VER_EMISSORA: "emissora", VER_TURNO: "turno", VER_CANDIDATO: "candidato"}[ver]
        grupos = [g for g in sorted(f[coluna].unique())]
        rotulos = [f"{g} ({len(f[f[coluna] == g])} checagens)" for g in grupos]
        if ver == VER_EMISSORA:
            st.caption("Globo reúne as entrevistas do Jornal Nacional e o debate da TV Globo; Band é o debate de 18/10.")
        for aba, g, rot in zip(st.tabs(rotulos), grupos, rotulos):
            with aba:
                sub = f[f[coluna] == g]
                cands = [g] if ver == VER_CANDIDATO else CANDIDATOS
                _conteudo(sub, contrapontos, unico, cands, f"fc_{coluna}_{g}")

    # ---------------- Placar oficial publicado pelas agências
    placares = meta.get("placares_oficiais", [])
    if placares:
        st.subheader("Placar oficial publicado pelo Ranking dos Políticos")
        st.caption("O Ranking checa a transcrição inteira, o que reduz o viés de seleção das falas. Para o debate da Globo (23/10) ainda não havia placar do Ranking.")
        dp = pd.DataFrame(placares)
        dp["total"] = dp[["verdadeiro", "impreciso", "falso"]].sum(axis=1)
        dp["% falso"] = (100 * dp["falso"] / dp["total"]).round(1)
        dp["% verdadeiro"] = (100 * dp["verdadeiro"] / dp["total"]).round(1)
        st.dataframe(
            dp[["evento", "candidato", "total", "verdadeiro", "impreciso", "falso", "% verdadeiro", "% falso", "url"]],
            width="stretch", hide_index=True,
            column_config={"url": st.column_config.LinkColumn("Fonte", display_text="abrir ↗"),
                           "evento": "Evento", "candidato": "Candidato", "total": "Total"},
        )

    st.markdown(
        '<div class="info-box"><b>⚠ Limites desta comparação:</b> agências escolhem o que checar e usam escalas diferentes; '
        'contagens não medem de forma absoluta "quem mente mais". No debate da Band, Lula fez mais afirmações verificáveis '
        '(47 contra 29 no Ranking dos Políticos), por isso o placar mostra percentuais. Os contrapontos reproduzem argumentos publicados '
        'por campanhas e veículos — não são endossados por este painel. As checagens do debate da Globo vêm de páginas ao vivo que as agências '
        'ainda podem atualizar, e a Lupa pode rever selos depois.</div>',
        unsafe_allow_html=True,
    )
