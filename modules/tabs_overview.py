import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_scorecard, load_json
from modules.alinhado import render_comparacao_alinhada
from modules.ux import gl
from modules.ui_components import (
    render_kpi_card,
    apply_plotly_theme,
    render_section_header,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COR_MANDATO,
    COR_CLARA,
    PARTIDO,
    PERIODO,
    classe_gov,
    hex_rgba,
    css_governos,
    fmt_br,
)

PADRAO = ("Bolsonaro", "Lula 3")

RADAR = [
    # (rótulo, indicador do scorecard, quanto maior melhor?)
    ("Crescimento do PIB", "Crescimento médio anual do PIB", True),
    ("Desemprego", "Taxa de desocupação média", False),
    ("Renda real", "Rendimento médio real habitual (fim do período)", True),
    ("Inflação", "IPCA médio anualizado", False),
    ("Juros (Selic)", "Taxa Selic média", False),
    ("Dívida bruta", "Dívida bruta do governo geral (% PIB)", False),
    ("Violência (MVI)", "Mortes violentas intencionais (total anual)", False),
    ("Pobreza", "Pobreza (linha do Banco Mundial)", False),
    ("Desmatamento", "Desmatamento na Amazônia (PRODES, média anual)", False),
]


def _ctx_padrao():
    """Rótulos e cores do par padrão (Bolsonaro x Lula), iguais ao painel original."""
    return {
        "a": "Bolsonaro", "b": "Lula", "a_full": "Bolsonaro (2019-22)", "b_full": "Lula (2023-atual)",
        "a_tab": "Bolsonaro (2019–22)", "b_tab": "Lula (2023–26)", "a_head": "Governo Bolsonaro (2019-2022)", "b_head": "Governo Lula (2023-atual)",
        "cor_a": COLOR_BOLSONARO, "cor_b": COLOR_LULA, "claro_a": "#93c5fd", "claro_b": "#fca5a5",
        "cls_a": "bolsonaro", "cls_b": "lula", "badge_a": "mb-bols", "badge_b": "mb-lula", "win_a": "win-b", "win_b": "win-l",
        "padrao": True,
    }


def _ctx_par(a, b):
    def nome(g):
        return f"{g} · {PARTIDO[g]} ({PERIODO[g]})"
    return {
        "a": a, "b": b, "a_full": nome(a), "b_full": nome(b), "a_tab": f"{a} ({PERIODO[a]})", "b_tab": f"{b} ({PERIODO[b]})",
        "a_head": f"Governo {a} · {PARTIDO[a]} ({PERIODO[a]})", "b_head": f"Governo {b} · {PARTIDO[b]} ({PERIODO[b]})",
        "cor_a": COR_MANDATO[a], "cor_b": COR_MANDATO[b], "claro_a": COR_CLARA[a], "claro_b": COR_CLARA[b],
        "cls_a": classe_gov(a), "cls_b": classe_gov(b), "badge_a": classe_gov(a), "badge_b": classe_gov(b),
        "win_a": "win-" + classe_gov(a), "win_b": "win-" + classe_gov(b), "padrao": False,
    }


def _radar_scores(indicadores):
    """Índice relativo: o melhor resultado recebe 100 e o outro recebe a razão entre os dois valores."""
    por_nome = {i["indicador"]: i for i in indicadores}
    labels, sb, sl, vb, vl = [], [], [], [], []
    for rotulo, nome, maior_melhor in RADAR:
        item = por_nome.get(nome)
        if not item:
            continue
        b, l = abs(item["bolsonaro_num"]), abs(item["lula_num"])
        if maior_melhor:
            sb.append(100 * b / max(b, l))
            sl.append(100 * l / max(b, l))
        else:
            sb.append(100 * min(b, l) / b)
            sl.append(100 * min(b, l) / l)
        labels.append(f"{rotulo} {'↑' if maior_melhor else '↓'}")
        vb.append(str(item["bolsonaro"]))
        vl.append(str(item["lula"]))
    return labels, sb, sl, vb, vl


EIXOS = {
    "Economia e finanças": ["Crescimento Econômico", "Monetário & Juros", "Câmbio", "Fiscal", "Setor Externo", "Indústria", "Agropecuária"],
    "Emprego e renda": ["Mercado de Trabalho", "Poder de Compra"],
    "Preços e custo de vida": ["Inflação", "Custo de Vida", "Inadimplência"],
    "Sociedade": ["Social", "Educação", "Saúde", "Segurança Pública", "Saneamento"],
    "Meio ambiente": ["Meio Ambiente"],
}
EIXO_DE = {c: e for e, cs in EIXOS.items() for c in cs}
ORDEM_CAT = [c for cs in EIXOS.values() for c in cs]
CMP = {"ok": ("✔ Mesma metodologia", "cmp-ok"), "ajustado": ("≈ Ajustado", "cmp-aj"), "ressalva": ("⚠ Ressalva", "cmp-res")}

DIRECAO_TXT = {True: "↑ maior é melhor", False: "↓ menor é melhor"}


def _classificar(indicadores, ctx):
    """Quem está melhor em cada indicador, olhando só para a direção (maior ou menor é melhor) — sem medir o tamanho da diferença."""
    linhas = []
    for i in indicadores:
        if i.get("no_grafico"):
            continue
        b = i.get("grafico_b", i["bolsonaro_num"])
        l = i.get("grafico_l", i["lula_num"])
        if b is None or l is None:
            continue
        maior_melhor = i.get("maior_melhor", True)
        if b == l:
            continue
        lula_melhor = (l > b) if maior_melhor else (l < b)
        if i["melhor"] == "empate":
            grupo = "Depende de contexto"
        else:
            grupo = ctx["b"] if lula_melhor else ctx["a"]
        linhas.append({
            "indicador": i["indicador"], "categoria": i["categoria"], "grupo": grupo, "direcao": DIRECAO_TXT[maior_melhor],
            "valor_b": i["bolsonaro"], "valor_l": i["lula"],
        })
    return linhas


def _grafico_placar(indicadores, ctx, nota_periodos):
    """Contagem simples: em quantos indicadores cada governo está melhor (cada indicador vale 1)."""
    linhas = _classificar(indicadores, ctx)
    if not linhas:
        return
    A, B = ctx["a"], ctx["b"]
    df = pd.DataFrame(linhas)
    df["eixo"] = df["categoria"].map(EIXO_DE).fillna("Outros")
    eixos = [e for e in EIXOS if e in set(df["eixo"])]
    escolha = st.pills("Eixos incluídos no placar:", eixos, selection_mode="multi", default=eixos, key="placar_eixos",
                       help="Tire eixos para ver como o placar muda. Cada indicador continua valendo 1 ponto.")
    if escolha:
        df = df[df["eixo"].isin(escolha)]
    else:
        st.info("Selecione ao menos um eixo.")
        return
    total = len(df)
    n = {g: int((df["grupo"] == g).sum()) for g in (A, "Depende de contexto", B)}
    cor = {A: ctx["cor_a"], "Depende de contexto": "#64748B", B: ctx["cor_b"]}
    rotulo = {A: f"{A} está melhor", "Depende de contexto": "Depende de contexto", B: f"{B} está melhor"}

    # (a) Placar geral: uma barra com os três grupos
    fig = go.Figure()
    for g in (A, "Depende de contexto", B):
        fig.add_trace(go.Bar(
            y=["Todos os indicadores"], x=[n[g]], name=rotulo[g], orientation="h", marker_color=cor[g],
            text=[(f"{n[g]} de {total}" if n[g] >= 3 else str(n[g])) if n[g] else ""], textposition="inside", insidetextanchor="middle", textangle=0,
            textfont=dict(color="#ffffff", size=15), hovertemplate=f"{rotulo[g]}: %{{x}} indicadores<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    apply_plotly_theme(fig, title="Placar geral: em quantos indicadores cada governo está melhor", height=200)
    fig.update_layout(hovermode="closest", margin=dict(l=20, r=20, t=75, b=30), legend=dict(orientation="h", y=1.18, x=0.5, xanchor="center"))
    fig.update_xaxes(range=[0, total], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig, width="stretch")

    # (b) Por categoria
    cats = [c for c in ORDEM_CAT if c in set(df["categoria"])]
    fig = go.Figure()
    for g in (A, "Depende de contexto", B):
        xs, textos, hovers = [], [], []
        for c in cats:
            sub = df[(df["categoria"] == c) & (df["grupo"] == g)]
            xs.append(len(sub))
            textos.append(str(len(sub)) if len(sub) else "")
            hovers.append("<br>".join(f"• {t} ({d})" for t, d in zip(sub["indicador"], sub["direcao"])) or "—")
        fig.add_trace(go.Bar(
            y=cats, x=xs, name=rotulo[g], orientation="h", marker_color=cor[g], text=textos, textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=13), customdata=hovers, showlegend=False,
            hovertemplate="<b>%{y}</b><br>" + rotulo[g] + ": %{x}<br>%{customdata}<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    apply_plotly_theme(fig, title="Por categoria: quantos indicadores cada governo leva", height=max(380, 30 * len(cats) + 130))
    fig.update_layout(hovermode="closest", margin=dict(l=20, r=20, t=70, b=40))
    fig.update_xaxes(dtick=1, title="Número de indicadores", zeroline=False)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Cada indicador vale 1 ponto, e o gráfico só conta quem está melhor em cada um — já considerando que em alguns indicadores menor é melhor "
        "(desemprego, inflação, juros, dívida, mortes) e em outros maior é melhor (PIB, renda, safra, empregos). "
        "Não mede o tamanho da diferença nem o peso de cada tema, então o placar não diz quem governa melhor. "
        "\"Depende de contexto\" marca o indicador em que os números favorecem um lado, mas o contexto relativiza (ou em que não há lado melhor, como o câmbio). "
        + nota_periodos
    )

    # (c) Quais são: lista por grupo, com a direção de cada indicador
    abas = st.tabs([f"{B} está melhor ({n[B]})", f"{A} está melhor ({n[A]})", f"Depende de contexto ({n['Depende de contexto']})"])
    for aba, g in zip(abas, (B, A, "Depende de contexto")):
        with aba:
            sub = df[df["grupo"] == g][["categoria", "indicador", "direcao", "valor_b", "valor_l"]].rename(columns={
                "categoria": "Categoria", "indicador": "Indicador", "direcao": "Como ler", "valor_b": ctx["a_tab"], "valor_l": ctx["b_tab"]})
            st.dataframe(sub, width="stretch", hide_index=True, height=min(80 + 36 * len(sub), 620),
                         column_config={"Indicador": st.column_config.TextColumn(width="large")})


RESUMO = [
    ("Crescimento médio do PIB", "Crescimento médio anual do PIB"),
    ("Desemprego médio", "Taxa de desocupação média"),
    ("Renda real (fim do período)", "Rendimento médio real habitual (fim do período)"),
    ("Inflação (IPCA médio ao ano)", "IPCA médio anualizado"),
    ("Selic média", "Taxa Selic média"),
    ("Dívida bruta (% PIB)", "Dívida bruta do governo geral (% PIB)"),
    ("Empregos formais (CAGED)", "Saldo de empregos formais (CAGED)"),
    ("Mortes violentas (por ano)", "Mortes violentas intencionais (total anual)"),
    ("Pobreza (Banco Mundial)", "Pobreza (linha do Banco Mundial)"),
    ("Desmatamento na Amazônia", "Desmatamento na Amazônia (PRODES, média anual)"),
]


def _resumo_10(por_nome, ctx, resumo=RESUMO):
    itens = [(t, por_nome[n]) for t, n in resumo if n in por_nome]
    if not itens:
        return
    A, B = ctx["a"], ctx["b"]
    st.subheader("Resumo em 10 números")
    st.caption("Para quem tem pouco tempo: os dez indicadores mais citados no debate, com a direção de cada um. O quadro completo está logo abaixo.")
    linhas_html = []
    for i in range(0, len(itens), 2):
        cols = st.columns(2)
        for col, (titulo, it) in zip(cols, itens[i:i + 2]):
            dir_txt = DIRECAO_TXT[bool(it.get("maior_melhor", True))]
            melhor = {"lula": B, "bolsonaro": A}.get(it["melhor"], "Depende de contexto")
            fonte_txt = html.escape(it.get("fonte", ""))
            fonte_html = (f'Fonte: <a href="{html.escape(it["fonte_url"], quote=True)}" target="_blank" style="color:#38bdf8;">{fonte_txt} ↗</a>'
                          if it.get("fonte_url") else (f"Fonte: {fonte_txt}" if fonte_txt else ""))
            if ctx["padrao"]:
                borda_attr = f' style="border-top:3px solid {({"lula": "#ef2b2d", "bolsonaro": "#3b82f6"}.get(it["melhor"], "#64748b"))};"'
                borda_cls = ""
            else:
                borda_attr = ""
                borda_cls = " borda-" + {"lula": ctx["cls_b"], "bolsonaro": ctx["cls_a"]}.get(it["melhor"], "")
            selo = {"lula": (B, ctx["badge_b"]), "bolsonaro": (A, ctx["badge_a"])}.get(it["melhor"], ("Depende de contexto", "mb-tie"))

            def lado(nome, valor, cor, cls, vence):
                if ctx["padrao"]:
                    fundo = f"background:{cor}22;border:1px solid {cor};" if vence else "border:1px solid transparent;opacity:0.75;"
                    return (f'<div style="flex:1;border-radius:8px;padding:6px 8px;{fundo}">'
                            f'<div style="font-size:0.68rem;font-weight:800;color:{cor};letter-spacing:0.04em;text-transform:uppercase;">{html.escape(nome)}</div>'
                            f'<div class="compare-val" style="color:{cor} !important;">{html.escape(str(valor))}</div></div>')
                estilo = "border:1px solid transparent;" if vence else "border:1px solid transparent;opacity:0.75;"
                return (f'<div class="resumo-lado {cls}{" vence" if vence else ""}" style="flex:1;border-radius:8px;padding:6px 8px;{estilo}">'
                        f'<div style="font-size:0.68rem;font-weight:800;letter-spacing:0.04em;text-transform:uppercase;">{html.escape(nome)}</div>'
                        f'<div class="compare-val">{html.escape(str(valor))}</div></div>')
            with col:
                st.markdown(
                    f'<div class="kpi-card compare-stat{borda_cls}"{borda_attr}>'
                    f'<div class="compare-title">{html.escape(titulo)}</div>'
                    f'<div style="display:flex;gap:8px;margin:6px 0;">'
                    f'{lado(A, it["bolsonaro"], ctx["claro_a"], ctx["cls_a"], it["melhor"] == "bolsonaro")}'
                    f'{lado(B, it["lula"], ctx["claro_b"], ctx["cls_b"], it["melhor"] == "lula")}</div>'
                    f'<div class="compare-foot">{dir_txt} · melhor: <span class="mini-badge {selo[1]}">{html.escape(selo[0])}</span></div>'
                    f'<div class="compare-foot" style="margin-top:4px;">{fonte_html}</div></div>',
                    unsafe_allow_html=True)
            linhas_html.append(f"<tr><td>{html.escape(titulo)}</td><td>{html.escape(str(it['bolsonaro']))}</td><td>{html.escape(str(it['lula']))}</td><td>{dir_txt}</td><td>{html.escape(melhor)}</td><td>{html.escape(it.get('fonte', ''))} {html.escape(it.get('fonte_url', ''))}</td></tr>")
    doc = ("<!doctype html><meta charset='utf-8'><title>Resumo em 10 números</title>"
           "<style>body{font-family:sans-serif;max-width:760px;margin:24px auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #999;padding:6px 8px;text-align:left}</style>"
           f"<h2>{html.escape(ctx['a_tab'])} vs {html.escape(ctx['b_tab'])}: resumo em 10 números</h2>"
           f"<table><tr><th>Indicador</th><th>{html.escape(A)}</th><th>{html.escape(B)}</th><th>Como ler</th><th>Melhor</th><th>Fonte</th></tr>" + "".join(linhas_html) +
           "</table><p>Fontes e critérios: página Metodologia do painel. \"Melhor\" considera só a direção do indicador, sem medir o tamanho da diferença.</p>")
    st.download_button("Baixar este resumo (HTML)", data=doc, file_name="resumo_10_numeros.html", mime="text/html")


def _celula_valor(valor, vence, lado, neutro, ctx):
    """Valor principal em destaque, detalhe entre parênteses em linha menor e selo próprio (sem quebrar ao lado do número)."""
    texto = html.escape(str(valor))
    principal, detalhe = (texto.split(" (", 1) + [""])[:2] if " (" in texto else (texto, "")
    detalhe = f"({detalhe}" if detalhe else ""
    selo = ""
    eh_b = lado == "lula"
    if neutro:
        selo = '<span class="mini-badge mb-tie">≈ DEPENDE</span>'
    elif vence:
        selo = f'<span class="mini-badge {ctx["badge_b"] if eh_b else ctx["badge_a"]}">✓ MELHOR</span>'
    win = ctx["win_b"] if eh_b else ctx["win_a"]
    classe = f"val-cell {win if vence and not neutro else ''}"
    if ctx["padrao"]:
        cor = "#93c5fd" if lado == "bolsonaro" else "#fca5a5"
        principal_html = f'<div class="val-main" style="color:{cor};">{principal}</div>'
    else:
        principal_html = f'<div class="val-main {ctx["cls_b"] if eh_b else ctx["cls_a"]}">{principal}</div>'
    return (f'<td class="{classe}"><div class="val-top">{selo}</div>'
            f'{principal_html}'
            f'<div class="val-detail">{detalhe}</div></td>')


# ======================================================================= dados de outros pares (base histórica)
CATEGORIA_HIST = {
    "pib": "Crescimento Econômico", "ipca": "Inflação", "ipca_alimentos": "Inflação", "selic": "Monetário & Juros", "dolar": "Câmbio",
    "desemprego": "Mercado de Trabalho", "caged": "Mercado de Trabalho", "desemprego_negros": "Mercado de Trabalho",
    "salario_minimo": "Poder de Compra", "renda": "Poder de Compra", "gini": "Social", "pobreza": "Social", "extrema_pobreza": "Social",
    "homicidios": "Segurança Pública", "divida_liquida": "Fiscal", "divida_bruta": "Fiscal", "primario": "Fiscal",
    "saldo_comercial": "Setor Externo", "exportacoes": "Setor Externo", "importacoes": "Setor Externo", "desmatamento": "Meio Ambiente",
    "safra": "Agropecuária", "abate_bovinos": "Agropecuária", "industria": "Indústria", "tarifa_energia": "Custo de Vida",
    "inadimplencia_pf": "Inadimplência", "ideb_iniciais": "Educação", "ideb_finais": "Educação", "ideb_medio": "Educação",
    "pisa_leitura": "Educação", "pisa_matematica": "Educação", "pisa_ciencias": "Educação", "analfabetismo": "Educação",
    "mortalidade_infantil": "Saúde", "esperanca_vida": "Saúde",
}
SEM_LADO_MELHOR = {"dolar", "importacoes"}  # câmbio e importações não têm direção "melhor"
UNIDADE_CURTA = {"% ao ano": "% a.a.", "%": "%", "por 100 mil": " por 100 mil", "km²": " km²", "pontos do PIB": " p.p. do PIB",
                 "pontos percentuais": " p.p.", "pontos (0–100)": " pts", "p.p. de queda": " p.p. de queda", "pontos de queda": " pts de queda", "mil vagas/mês": " mil/mês", "milhões de t": " Mt",
                 "% da carteira": "%", "% do PIB": "% do PIB", "nota 0–10": "", "pontos": " pts", "anos": " anos", "por mil nascidos": " por mil"}
GOV_ANUAL = {"Dilma 2": "2015", "Temer": "2016–18"}


def _ano_gov(ano):
    if ano == 2016:
        return "Temer"
    for nome, ini, fim in (("FHC 1", 1995, 1998), ("FHC 2", 1999, 2002), ("Lula 1", 2003, 2006), ("Lula 2", 2007, 2010),
                           ("Dilma 1", 2011, 2014), ("Dilma 2", 2015, 2015), ("Temer", 2016, 2018), ("Bolsonaro", 2019, 2022),
                           ("Lula 3", 2023, 2030)):
        if ini <= ano <= fim:
            return nome
    return None


def _texto(ind, gov, v):
    if v is None:
        return "Sem dado*"
    u = ind["unidade"]
    casas = 0 if u in ("km²", "pontos") else (1 if abs(v) >= 10 else 2)
    num = fmt_br(v, casas)
    if u in ("pontos do PIB", "pontos percentuais", "pontos (0–100)") and v > 0:
        num = "+" + num
    if u == "US$ bilhões":
        txt = f"US$ {num} bi"
    elif u == "R$ por US$":
        txt = f"R$ {num}"
    else:
        txt = num + UNIDADE_CURTA.get(u, " " + u)
    outra = {_ano_gov(int(a)) for a in ind.get("outra_metodologia", [])}
    parcial = {_ano_gov(int(a)) for a in ind.get("parcial", [])}
    return txt + ("*" if gov in outra else "") + ("†" if gov in parcial else "")


def _indicadores_par(a, b):
    """Converte a base histórica no mesmo formato do scorecard (lado A no lugar de 'bolsonaro', lado B no de 'lula')."""
    d = load_json("historico.json")
    lista = []
    for k, ind in d.get("indicadores", {}).items():
        va, vb = ind["mandato"].get(a), ind["mandato"].get(b)
        if va is None and vb is None:
            continue
        if va is None or vb is None or k in SEM_LADO_MELHOR or ind.get("sem_lado_melhor") or va == vb:
            melhor = "empate"
        else:
            melhor = "lula" if (vb > va) == ind["maior_melhor"] else "bolsonaro"
        lista.append({
            "chave": k, "categoria": CATEGORIA_HIST.get(k, "Social"), "indicador": ind["nome"],
            "bolsonaro": _texto(ind, a, va), "lula": _texto(ind, b, vb), "bolsonaro_num": va, "lula_num": vb,
            "unidade": ind["unidade"], "melhor": melhor, "maior_melhor": ind["maior_melhor"],
            "observacao": (ind["metodo"] + " " + ind.get("nota", "")).strip(), "fonte": ind["fonte"], "fonte_url": ind["url"],
            "comparabilidade": ind["comparabilidade"], "no_grafico": va is None or vb is None,
        })
    return lista, d


DESTAQUES_HIST = [("Crescimento médio do PIB", "pib"), ("Desemprego médio", "desemprego"), ("Inflação (IPCA ao ano)", "ipca"),
                  ("Empregos formais (CAGED)", "caged"), ("Variação da dívida líquida", "divida_liquida"), ("Selic média", "selic")]
RESUMO_HIST = [("Crescimento médio do PIB", "pib"), ("Desemprego médio", "desemprego"), ("Renda real (ganho ao ano)", "renda"),
               ("Inflação (IPCA ao ano)", "ipca"), ("Selic média", "selic"), ("Salário mínimo real (ganho ao ano)", "salario_minimo"),
               ("Empregos formais (CAGED)", "caged"), ("Homicídios (taxa média)", "homicidios"), ("Queda da pobreza", "pobreza"),
               ("Desmatamento na Amazônia", "desmatamento")]
RADAR_HIST = [("Crescimento do PIB", "pib"), ("Desemprego", "desemprego"), ("Renda real", "renda"), ("Inflação", "ipca"),
              ("Juros (Selic)", "selic"), ("Salário mínimo", "salario_minimo"), ("Violência", "homicidios"),
              ("Pobreza", "pobreza"), ("Desmatamento", "desmatamento")]
CONTEXTO = {
    "FHC 1": "Consolidação do Plano Real (inflação caindo de dois dígitos), câmbio controlado, privatizações e crises do México (1995), da Ásia (1997) e da Rússia (1998), com juros muito altos.",
    "FHC 2": "Desvalorização do real e adoção do tripé (metas de inflação, câmbio flutuante, superávit) em 1999, Lei de Responsabilidade Fiscal (2000), apagão (2001) e crise de confiança em 2002.",
    "Lula 1": "Manutenção do tripé, juros altos no início, alta das commodities e da demanda chinesa, Bolsa Família (2003) e valorização do salário mínimo.",
    "Lula 2": "Crise financeira global de 2008–09 com estímulos (PAC, crédito público, Minha Casa Minha Vida) e crescimento de 7,5% em 2010.",
    "Dilma 1": "Desaceleração, 'nova matriz econômica' (juros e energia mais baratos por decisão de governo, desonerações), desemprego na mínima da época e início da deterioração fiscal.",
    "Dilma 2": "Recessão de 2015–16, ajuste fiscal, inflação acima de 10% em 2015, Lava Jato e impeachment (afastamento em maio de 2016).",
    "Temer": "Saída da recessão, teto de gastos (EC 95), reforma trabalhista (2017), inflação e juros em queda, greve dos caminhoneiros (2018).",
    "Bolsonaro": "Reforma da Previdência (2019), pandemia de 2020 com auxílio emergencial, inflação alta em 2021–22 e corte de impostos sobre combustíveis e energia em 2022.",
    "Lula 3": "Arcabouço fiscal (2023), reforma tributária do consumo, supersafra de 2023, juros altos (Selic até 15% em 2025) e desemprego na mínima da série.",
}


def _radar_hist(lista_por_chave, d, ctx):
    """Posição de cada governo entre todos os mandatos desde 1995 (0 = pior, 100 = melhor), para não depender do sinal dos valores."""
    labels, sa, sb, ta, tb = [], [], [], [], []
    for rotulo, k in RADAR_HIST:
        ind, item = d["indicadores"].get(k), lista_por_chave.get(k)
        if not ind or not item or item["bolsonaro_num"] is None or item["lula_num"] is None:
            continue
        vals = list(ind["mandato"].values())
        melhor, pior = (max(vals), min(vals)) if ind["maior_melhor"] else (min(vals), max(vals))
        if melhor == pior:
            continue
        sa.append(100 * (item["bolsonaro_num"] - pior) / (melhor - pior))
        sb.append(100 * (item["lula_num"] - pior) / (melhor - pior))
        labels.append(f"{rotulo} {'↑' if ind['maior_melhor'] else '↓'}")
        ta.append(item["bolsonaro"])
        tb.append(item["lula"])
    return labels, sa, sb, ta, tb


def _cabecalho_e_cartoes(ctx, indicators, por_nome, destaques):
    cols = st.columns(3)
    for i, (titulo, nome) in enumerate(destaques):
        item = por_nome.get(nome)
        if not item:
            continue
        with cols[i % 3]:
            if ctx["padrao"]:
                render_kpi_card(title=titulo, val_bols=item["bolsonaro"], val_lula=item["lula"],
                                unit=item.get("fonte", "").split(" — ")[0], note=item["observacao"])
            else:
                render_kpi_card(title=titulo, val_bols=item["bolsonaro"], val_lula=item["lula"],
                                unit=item.get("fonte", "").split(" — ")[0], note=item["observacao"],
                                nome_a=ctx["a_full"], nome_b=ctx["b_full"], cls_a=ctx["cls_a"], cls_b=ctx["cls_b"])


def _radar(ctx, categories, values_a, values_b, txt_a, txt_b, legenda):
    def traco(nome, valores, textos, cor, fundo, simbolo):
        return go.Scatterpolar(
            r=valores + [valores[0]], theta=categories + [categories[0]], fill="toself", name=nome,
            line=dict(color=cor, width=3), fillcolor=fundo, marker=dict(size=8, color=cor, symbol=simbolo),
            customdata=textos + [textos[0]],
            hovertemplate="<b>%{theta}</b><br>" + nome.split(" (")[0] + ": %{customdata}<br>Índice: %{r:.0f}/100<extra></extra>",
        )

    fig_radar = go.Figure()
    nome_a = "Bolsonaro (2019–2022)" if ctx["padrao"] else ctx["a_full"]
    nome_b = "Lula (2023–atual)" if ctx["padrao"] else ctx["b_full"]
    fig_radar.add_trace(traco(nome_a, values_a, txt_a, ctx["cor_a"], hex_rgba(ctx["cor_a"], 0.18), "circle"))
    fig_radar.add_trace(traco(nome_b, values_b, txt_b, ctx["cor_b"], hex_rgba(ctx["cor_b"], 0.18), "diamond"))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0e1526",
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100], gridcolor="#334155", linecolor="#334155",
                            tickfont=dict(color="#94a3b8", size=10), angle=90),
            angularaxis=dict(gridcolor="#334155", linecolor="#334155", tickfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif")),
        ),
        showlegend=True, template="plotly_dark", paper_bgcolor="#111827", height=560, hovermode="closest",
        margin=dict(l=90, r=90, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5, font=dict(color="#ffffff", size=13)),
    )
    st.plotly_chart(fig_radar, width="stretch")
    st.caption(legenda)


def _tabela(ctx, indicators):
    df_score = pd.DataFrame(indicators)
    df_score["eixo"] = df_score["categoria"].map(EIXO_DE).fillna("Outros")
    eixo_sel = st.pills("Eixo:", ["Todos"] + [e for e in EIXOS if e in set(df_score["eixo"])], default="Todos", key="score_eixo") or "Todos"
    col_f1, col_f2, col_f3 = st.columns([1.2, 1, 1.4])
    with col_f1:
        cats_eixo = [c for c in ORDEM_CAT if c in set(df_score["categoria"]) and (eixo_sel == "Todos" or EIXO_DE.get(c) == eixo_sel)]
        cat_sel = (st.pills("Categoria:", cats_eixo, selection_mode="multi", key=f"score_cat_{eixo_sel}") or []) if eixo_sel != "Todos" else []
        if eixo_sel == "Todos":
            st.caption("Escolha um eixo para filtrar por categoria.")
    with col_f2:
        cmp_sel = st.pills("Comparabilidade:", [v[0] for v in CMP.values()], selection_mode="multi", key="score_cmp",
                           help="Mostra se os dois períodos usam a mesma metodologia ou se há ajuste/ressalva.") or []
    with col_f3:
        busca = st.text_input("Buscar indicador:", "", placeholder="Ex: PIB, Selic, Desocupação, Safra...", key="score_search")

    df_filtered = df_score.copy()
    if eixo_sel != "Todos":
        df_filtered = df_filtered[df_filtered["eixo"] == eixo_sel]
    if cat_sel:
        df_filtered = df_filtered[df_filtered["categoria"].isin(cat_sel)]
    if cmp_sel:
        nomes_cmp = {v[0]: k for k, v in CMP.items()}
        df_filtered = df_filtered[df_filtered["comparabilidade"].isin([nomes_cmp[c] for c in cmp_sel])]
    if busca:
        df_filtered = df_filtered[
            df_filtered["indicador"].str.contains(busca, case=False) |
            df_filtered["observacao"].str.contains(busca, case=False)
        ]
    df_filtered = df_filtered.assign(_o=df_filtered["categoria"].map({c: i for i, c in enumerate(ORDEM_CAT)}).fillna(99)).sort_values("_o", kind="stable")
    st.caption(f"{len(df_filtered)} de {len(df_score)} indicadores. **Comparabilidade:** ✔ mesma série e metodologia · ≈ períodos de tamanhos ou datas diferentes, com ajuste · "
               "⚠ metodologia, cobertura ou natureza do número diferem entre os dois lados (leia a ressalva na tabela)."
               + ("" if ctx["padrao"] else " **Sem dado*** = não há série comparável para esse governo; número com * = dado de outra metodologia; † = ano parcial."))

    table_rows = []
    for _, row in df_filtered.iterrows():
        neutro = row["melhor"] == "empate"
        fonte = ""
        if row.get("fonte_url"):
            fonte = f'<br/><a href="{html.escape(row["fonte_url"], quote=True)}" target="_blank" style="color:#38bdf8; font-size:0.75rem;">{html.escape(row["fonte"])}</a>'
        maior_melhor = bool(row.get("maior_melhor", True))
        direcao = f'<div class="dir-tag {"dir-up" if maior_melhor else "dir-down"}">{DIRECAO_TXT[maior_melhor]}</div>'
        table_rows.append(
            "<tr>"
            f"<td><b style='color: #ffffff;'>{html.escape(row['categoria'])}</b></td>"
            f"<td><b style='color: #38bdf8;'>{html.escape(row['indicador'])}</b>{direcao}</td>"
            + _celula_valor(row["bolsonaro"], row["melhor"] == "bolsonaro", "bolsonaro", neutro, ctx)
            + _celula_valor(row["lula"], row["melhor"] == "lula", "lula", neutro, ctx)
            + f"<td style='color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;'>{gl(html.escape(row['observacao']))}{fonte}</td>"
            "</tr>"
        )

    html_table = (
        '<table class="custom-table score-table">'
        '<thead><tr>'
        '<th>Categoria</th>'
        '<th>Indicador</th>'
        f'<th>{html.escape(ctx["a_head"])}</th>'
        f'<th>{html.escape(ctx["b_head"])}</th>'
        '<th>Contexto & Fonte Oficial</th>'
        '</tr></thead>'
        f"<tbody>{''.join(table_rows)}</tbody>"
        '</table>'
    )
    st.markdown(html_table, unsafe_allow_html=True)


def render_tab_overview():
    a = st.session_state.get("gov_a", PADRAO[0])
    b = st.session_state.get("gov_b", PADRAO[1])
    if (a, b) != PADRAO and a != b and a in COR_MANDATO and b in COR_MANDATO:
        return _render_par(a, b)

    ctx = _ctx_padrao()
    render_section_header(
        "Painel Executivo & Scorecard Geral",
        "Síntese dos principais indicadores dos governos escolhidos no seletor acima. Por padrão aparecem Bolsonaro (2019–2022) e Lula 3 (2023–2026), "
        "com dados conferidos contra as fontes em 21/10/2026; troque os governos para comparar qualquer mandato desde FHC.",
    )
    st.markdown('<div class="info-box"><b>Qual página usar?</b> Esta página é o <b>panorama</b>: todos os indicadores de uma vez, com placar e tabela. '
                'Para olhar <b>um indicador em detalhe</b> (valores, método e fonte), use o <b>Comparador Direto</b>.</div>', unsafe_allow_html=True)

    scorecard_data = get_scorecard()
    indicators = scorecard_data.get("indicadores", [])
    meta = scorecard_data.get("metadados", {})
    por_nome = {i["indicador"]: i for i in indicators}

    # 1. KPI Cards Grid (valores lidos do scorecard)
    destaques = [
        ("Crescimento médio do PIB", "Crescimento médio anual do PIB"),
        ("Desemprego médio", "Taxa de desocupação média"),
        ("Inflação acumulada (IPCA)", "IPCA acumulado no mandato"),
        ("Empregos formais (CAGED)", "Saldo de empregos formais (CAGED)"),
        ("Dívida bruta (% PIB)", "Dívida bruta do governo geral (% PIB)"),
        ("Selic média", "Taxa Selic média"),
    ]
    _cabecalho_e_cartoes(ctx, indicators, por_nome, destaques)

    vant_b = sum(1 for i in indicators if i["melhor"] == "bolsonaro")
    vant_l = sum(1 for i in indicators if i["melhor"] == "lula")
    empates = sum(1 for i in indicators if i["melhor"] == "empate")
    st.caption(
        f"Nos {len(indicators)} indicadores do scorecard: resultado mais favorável com Lula em {vant_l}, com Bolsonaro em {vant_b} "
        f"e empate/depende de contexto em {empates}. {meta.get('criterio_melhor', '')}"
    )

    st.markdown("---")
    _resumo_10(por_nome, ctx)
    st.markdown("---")
    render_comparacao_alinhada()
    st.markdown("---")

    # 2. Radar calculado a partir do scorecard
    st.subheader("Radar Comparativo (índice relativo, 0–100)")
    st.caption("Em cada eixo, o período com melhor resultado recebe 100 e o outro recebe a proporção entre os dois valores. "
               "Calculado a partir do scorecard abaixo — não há notas atribuídas à mão.")
    categories, values_bolsonaro, values_lula, txt_b, txt_l = _radar_scores(indicators)
    _radar(ctx, categories, values_bolsonaro, values_lula, txt_b, txt_l,
           "Quanto mais perto da borda (100), melhor o resultado naquele eixo. A seta mostra a direção: ↑ maior é melhor, ↓ menor é melhor "
           "(já invertida no índice, então vale sempre \"mais longe do centro = melhor\"). Passe o mouse para ver os valores reais.")

    st.markdown("---")

    # 3. Placar quantitativo + tabela comparativa
    st.subheader("Tabela Comparativa Consolidada dos Indicadores")
    _grafico_placar(indicators, ctx, "Para comparar períodos de 48 e 44–45 meses, acumulados viram taxa ao ano e o CAGED vira média mensal; "
                                     "o IPCA acumulado fica de fora para não contar duas vezes.")
    st.markdown("---")
    _tabela(ctx, indicators)

    # 4. Box de Contexto Macroeconômico
    info_html = (
        '<div class="info-box">'
        '<b>Contextualização Macroeconômica Crucial:</b><br/>'
        '• <b>Governo Bolsonaro (2019–2022):</b> Marcado pelo impacto da pandemia de COVID-19 em 2020 (PIB de -3,3%), '
        'seguida por choque inflacionário e desorganização de cadeias globais em 2021/2022 e pela deflação pontual do '
        'segundo semestre de 2022 via corte de impostos (ICMS sobre combustíveis e energia). Encerrou o mandato com mercado de trabalho em recuperação '
        '(desemprego em 7,9%), superávit primário e dívida bruta em 71,7% do PIB.<br/>'
        '• <b>Governo Lula (2023–2026):</b> Herdou Selic de 13,75% e foi impulsionado pela supersafra de 2023 e pela resiliência do emprego. '
        'Beneficiou-se de reformas prévias (Trabalhista, Previdência, Marco do Saneamento, Autonomia do BC) e recuperou o poder de compra via '
        'valorização do salário mínimo, mas enfrenta déficits primários, Selic de até 15% (2025), dívida bruta em alta '
        '(82,9% do PIB em ago/2026) e endividamento recorde das famílias.'
        '</div>'
    )
    st.markdown(info_html, unsafe_allow_html=True)


def _render_par(a, b):
    """Mesma Visão Geral do par padrão, alimentada pela base histórica, com as cores do partido de cada presidente."""
    ctx = _ctx_par(a, b)
    st.markdown(css_governos(), unsafe_allow_html=True)
    render_section_header(
        "Painel Executivo & Scorecard Geral",
        f"Síntese dos principais indicadores de {ctx['a_full']} e {ctx['b_full']}, a partir de séries longas e oficiais "
        "agregadas do mesmo jeito para todos os mandatos desde 1995. Use o seletor acima para trocar os governos.",
    )
    indicators, d = _indicadores_par(a, b)
    por_chave = {i["chave"]: i for i in indicators}
    por_nome = {i["indicador"]: i for i in indicators}

    # 1. Cartões
    _cabecalho_e_cartoes(ctx, indicators, {t: por_chave[k] for t, k in DESTAQUES_HIST if k in por_chave},
                         [(t, t) for t, k in DESTAQUES_HIST if k in por_chave])
    validos = [i for i in indicators if i["melhor"] != "empate"]
    va = sum(1 for i in validos if i["melhor"] == "bolsonaro")
    vb = sum(1 for i in validos if i["melhor"] == "lula")
    st.caption(f"Nos {len(indicators)} indicadores da base histórica: resultado mais favorável com {b} em {vb}, com {a} em {va} "
               f"e empate, sem dado para um dos lados ou sem lado melhor em {len(indicators) - va - vb}. "
               "\"Melhor\" considera só a direção do indicador, sem medir o tamanho da diferença.")

    st.markdown("---")
    _resumo_10({t: por_chave[k] for t, k in RESUMO_HIST if k in por_chave}, ctx, [(t, t) for t, k in RESUMO_HIST if k in por_chave])
    st.markdown("---")

    # 2. Radar
    st.subheader("Radar Comparativo (posição entre todos os governos, 0–100)")
    st.caption("Em cada eixo, 100 é o melhor resultado entre os nove mandatos desde 1995 e 0 é o pior; os dois governos escolhidos aparecem nessa régua. "
               "Calculado a partir da tabela abaixo — não há notas atribuídas à mão.")
    labels, sa, sb, ta, tb = _radar_hist(por_chave, d, ctx)
    if labels:
        _radar(ctx, labels, sa, sb, ta, tb,
               "Quanto mais perto da borda (100), melhor a posição do governo naquele eixo entre todos os mandatos desde FHC. A seta mostra a direção do indicador. "
               "Passe o mouse para ver os valores reais. Eixos sem dado para um dos governos ficam de fora.")
    else:
        st.info("Os dois governos não têm dados suficientes em comum para o radar.")

    st.markdown("---")

    # 3. Placar + tabela
    st.subheader("Tabela Comparativa Consolidada dos Indicadores")
    _grafico_placar(indicators, ctx, "Mandatos de tamanhos diferentes: acumulados viram taxa ao ano, níveis viram médias e estoques (pobreza, Gini, dívida) "
                                     "viram variação no mandato. Indicadores sem dado para um dos governos ficam fora do placar.")
    st.markdown("---")
    _tabela(ctx, indicators)

    # 4. Contexto
    st.markdown(
        '<div class="info-box"><b>Contextualização de cada período:</b><br/>'
        f'• <b>Governo {html.escape(a)} ({PARTIDO[a]}, {PERIODO[a]}):</b> {html.escape(CONTEXTO[a])}<br/>'
        f'• <b>Governo {html.escape(b)} ({PARTIDO[b]}, {PERIODO[b]}):</b> {html.escape(CONTEXTO[b])}<br/>'
        '<span style="color:#94a3b8;font-size:0.8rem;">Cores pelo partido do presidente na época: PSDB (FHC), PT (Lula e Dilma), MDB (Temer), '
        'PSL/PL (Bolsonaro, eleito pelo PSL e filiado ao PL desde 2021). Mandatos do mesmo partido usam tons diferentes.</span></div>',
        unsafe_allow_html=True)
