"""
Componentes da série histórica (FHC a Lula 3): quadro por mandato, gráfico anual, comparação entre dois governos
e a seção "Todos os governos" usada no fim de cada aba.
"""
import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.ui_components import apply_plotly_theme, render_source, fmt_br, COR_MANDATO, classe_gov

CMP = {"ok": ("✔", "mesma metodologia em toda a série"), "ajustado": ("≈", "ajustada (períodos ou bases diferentes)"),
       "ressalva": ("⚠", "a metodologia muda ou falta parte da série")}
ORDEM_EIXO = ["Economia", "Emprego e renda", "Sociedade", "Fiscal", "Meio ambiente"]
VARIACAO = ("pontos percentuais", "pontos do PIB", "pontos (0–100)")


def base():
    return load_json("historico.json")


def nomes_governos(d=None):
    d = d or base()
    return [g["nome"] for g in d.get("governos", [])]


def ano_gov(ano):
    """Mesma regra do coletor: cada ano vai para o governo em exercício; 2016 conta para Temer."""
    if ano == 2016:
        return "Temer"
    for nome, ini, fim in (("FHC 1", 1995, 1998), ("FHC 2", 1999, 2002), ("Lula 1", 2003, 2006), ("Lula 2", 2007, 2010),
                           ("Dilma 1", 2011, 2014), ("Dilma 2", 2015, 2015), ("Temer", 2016, 2018), ("Bolsonaro", 2019, 2022),
                           ("Lula 3", 2023, 2030)):
        if ini <= ano <= fim:
            return nome
    return None


def fmt(v, unidade):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    casas = 0 if unidade in ("km²", "pontos") else (1 if abs(v) >= 10 else 2)
    sinal = "+" if unidade in VARIACAO and v > 0 else ""
    return sinal + fmt_br(v, casas)


def seta_txt(ind):
    """Direção do indicador em palavras; onde o número pode ser negativo e isso é bom, avisa."""
    if ind["maior_melhor"]:
        return "↑ maior é melhor"
    if any(t in ind["nome"].lower() for t in ("dívida", "tarifa")):
        return "↓ menor é melhor (negativo = caiu)"
    return "↓ menor é melhor"


def _marcados(ind):
    """Mandatos cujo valor usa ano de outra metodologia (*) ou ano parcial (†)."""
    outra = {ano_gov(int(a)) for a in ind.get("outra_metodologia", [])}
    parcial = {ano_gov(int(a)) for a in ind.get("parcial", [])}
    return outra, parcial


def _classe(rank, n):
    if n <= 1:
        return "hist-c0"
    return f"hist-c{1 + round(4 * rank / (n - 1))}"


def quadro_html(indicadores, governos, destaque=None):
    """Tabela indicador x mandato com cores relativas (verde = melhor posição na linha, vermelho = pior)."""
    linhas, eixo_atual = [], None
    for ind in sorted(indicadores, key=lambda i: ORDEM_EIXO.index(i["eixo"]) if i["eixo"] in ORDEM_EIXO else 9):
        if ind["eixo"] != eixo_atual:
            eixo_atual = ind["eixo"]
            linhas.append(f'<tr><td colspan="{len(governos) + 1}" class="hist-eixo">{html.escape(eixo_atual)}</td></tr>')
        vals = {g: ind["mandato"].get(g) for g in governos}
        com = sorted([g for g in governos if vals[g] is not None], key=lambda g: vals[g], reverse=ind["maior_melhor"])
        pos = {g: i for i, g in enumerate(com)}
        sem_lado = bool(ind.get("sem_lado_melhor"))
        outra, parcial = _marcados(ind)
        cel = []
        for g in governos:
            if g not in pos:
                cel.append('<td class="hist-val hist-vazio" title="sem dado comparável">*</td>')
                continue
            marca = ("*" if g in outra else "") + ("†" if g in parcial else "")
            top = '<span class="hist-top">1º</span>' if pos[g] == 0 and not sem_lado else ""
            cel.append(f'<td class="hist-val {'hist-c0' if sem_lado else _classe(pos[g], len(com))}" title="{html.escape(g)}: {pos[g] + 1}º de {len(com)}">'
                       f'{fmt(vals[g], ind["unidade"])}{marca}{top}</td>')
        simbolo = CMP[ind["comparabilidade"]][0]
        seta = seta_txt(ind)
        linhas.append(f'<tr><td class="hist-ind"><b>{html.escape(ind["nome"])}</b><div class="hist-sub">{html.escape(ind["unidade"])} · {seta} · '
                      f'<span title="{html.escape(CMP[ind["comparabilidade"]][1])}">{simbolo}</span> · '
                      f'<a href="{html.escape(ind["url"], quote=True)}" target="_blank">dados ↗</a></div></td>{"".join(cel)}</tr>')
    cab = "".join(f'<th class="{"hist-sel" if destaque and g in destaque else ""}" style="border-bottom:3px solid {COR_MANDATO.get(g, "#64748b")};">{html.escape(g)}</th>'
                  for g in governos)
    return (f'<div class="hist-wrap"><table class="custom-table hist-table"><thead><tr><th>Indicador</th>{cab}</tr></thead>'
            f'<tbody>{"".join(linhas)}</tbody></table></div>')


LEGENDA = ("Cores comparam os mandatos dentro de cada linha (verde = melhor posição, vermelho = pior). "
           "✔ mesma metodologia · ≈ ajustada · ⚠ metodologia muda ou falta parte da série · "
           "**\\*** sem dado comparável, ou valor que usa dado de outra metodologia · **†** ano parcial · \"dados ↗\" abre a série exata usada.")


# ======================================================================= comparação na aba inteira
PADRAO = ("Bolsonaro", "Lula 3")
TODOS = "Todos os governos"

# Mesmo título e subtítulo das abas originais (Bolsonaro x Lula), para a aba não mudar de cara ao trocar os governos
TITULOS = {
    "visao-geral": ("Painel Executivo & Scorecard Geral", "Principais indicadores de cada governo, com o mesmo critério para todos."),
    "trabalho": ("Mercado de Trabalho: PNAD Contínua & CAGED", "Evolução da taxa de desocupação, do salário mínimo real, da renda e do saldo de empregos formais gerados."),
    "inflacao": ("Inflação e Preços: IPCA (IBGE)", "Trajetória acumulada da inflação oficial nos mandatos e inflação dos alimentos."),
    "cesta-basica": ("Cesta Básica & Preços Específicos", "Preço dos alimentos (IPCA) e poder de compra do salário mínimo em cada mandato."),
    "inadimplencia": ("Inadimplência: carteiras em atraso e contas não pagas", "Taxa de inadimplência das carteiras de crédito de pessoas físicas (Banco Central: parcelas com mais de 90 dias de atraso)."),
    "energia-agua-esgoto": ("Energia, Água & Esgoto: custos e cobertura", "Quanto a tarifa residencial de energia subiu ou caiu acima da inflação em cada mandato."),
    "macroeconomia": ("Macroeconomia & Finanças Públicas", "Produto Interno Bruto (IBGE), Taxa Selic, Câmbio PTAX, dívida e resultado primário (Banco Central)."),
    "fiscal-social-ambiental": ("Contas Públicas, Pobreza & Desigualdade", "Resultado primário (Banco Central), renda, pobreza e desigualdade (IBGE/Ipea)."),
    "agro": ("Agropecuária & Grãos: CONAB & PAM (IBGE)", "Produção nacional de grãos pela Companhia Nacional de Abastecimento (CONAB)."),
    "industria": ("Indústria: PIM-PF (IBGE)", "Desempenho da Produção Física Industrial brasileira segundo a Pesquisa Industrial Mensal (PIM-PF - IBGE)."),
    "pecuaria": ("Pecuária Municipal: PPM (IBGE)", "Abate de bovinos (IBGE), indicador da atividade pecuária ao longo dos mandatos."),
    "comercio-exterior": ("Comércio Exterior (ComexStat)", "Exportações, importações e saldo da balança comercial brasileira."),
    "educacao": ("Educação & Capital Humano", "Avaliação do IDEB (Inep), PISA (OCDE) e taxa de analfabetismo (IBGE)."),
    "saude": ("Saúde", "Mortalidade infantil e esperança de vida ao nascer (IBGE)."),
    "seguranca": ("Segurança Pública & Criminalidade", "Taxa de homicídios (Atlas da Violência, com dados do Ministério da Saúde)."),
    "inclusao": ("Mulheres, Raça & Minorias", "Desemprego de pretos e pardos, pobreza e desigualdade de renda."),
    "meio-ambiente": ("Meio Ambiente & Clima", "Desmatamento na Amazônia (Inpe/PRODES)."),
    "silvicultura": ("Silvicultura & Extrativismo: PEVS (IBGE)", "Valor da produção da silvicultura e da extração vegetal nativa (IBGE)."),
}
ABAS_COMPARAVEIS = set(TITULOS)

# Molde fixo de cada aba: as mesmas seções numeradas da versão padrão (Bolsonaro x Lula 3).
# Cada seção: (título, [chaves de historico.json], área de programas ou None). Lista vazia = não há série longa: a seção aparece com "Sem dado".
PROG = "programas"
MOLDE = {
    "trabalho": [
        ("Taxa de Desocupação (%) — PNAD Contínua IBGE", ["desemprego"], None),
        ("Rendimento Médio Real (R$)", ["renda"], None),
        ("Massa de Rendimento Real (R$ bi)", [], None),
        ("Saldo Anual de Vagas com Carteira Assinada (Novo CAGED)", ["caged"], None),
        ("Salário mínimo real", ["salario_minimo"], None),
    ],
    "inflacao": [
        ("Inflação Acumulada no Mandato (Mês a Mês) e Série Anual do IPCA", ["ipca"], None),
        ("Inflação dos Alimentos (IPCA)", ["ipca_alimentos"], None),
        ("Decomposição Setorial do IPCA (Grupos de Consumo)", [], None),
    ],
    "cesta-basica": [
        ("Quanto cada item subiu em cada mandato (IPCA oficial)", ["ipca_alimentos"], None),
        ("Poder de compra do salário mínimo", ["salario_minimo"], None),
        ("Custo da cesta básica (R$ nominais, SP)", [], None),
        ("Horas de trabalho para comprar a cesta", [], None),
    ],
    "inadimplencia": [
        ("Inadimplência da carteira de crédito (% com atraso superior a 90 dias)", ["inadimplencia_pf"], None),
        ("Onde está o atraso: modalidades de crédito de pessoas físicas", [], None),
        ("Pessoas e famílias com contas em atraso", [], None),
        ("Renegociação de dívidas: Desenrola", [], None),
    ],
    "energia-agua-esgoto": [
        ("Quanto a tarifa de energia subiu acima da inflação", ["tarifa_energia"], None),
        ("Por que a conta de luz subiu", [], None),
        ("Água e esgoto nos domicílios (IBGE)", [], None),
        ("Políticas relacionadas", [], "Infraestrutura & Energia"),
    ],
    "macroeconomia": [
        ("Crescimento Anual do PIB (%) — IBGE Contas Nacionais", ["pib"], None),
        ("Saldo da Balança Comercial Brasileira (US$ Bilhões)", ["saldo_comercial"], None),
        ("Taxa Selic Média (% a.a.)", ["selic"], None),
        ("Dólar PTAX Médio (R$/US$)", ["dolar"], None),
        ("Dívida do Governo Geral (% do PIB)", ["divida_bruta", "divida_liquida"], None),
        ("Resultado primário (% do PIB)", ["primario"], None),
    ],
    "fiscal-social-ambiental": [
        ("Resultado primário do setor público consolidado (% do PIB)", ["primario"], None),
        ("Dívida bruta x dívida líquida (% PIB)", ["divida_bruta", "divida_liquida"], None),
        ("Custo dos juros da dívida (% PIB)", [], None),
        ("Pobreza e extrema pobreza (% da população)", ["pobreza", "extrema_pobreza"], None),
        ("Desigualdade de renda (Gini)", ["gini"], None),
        ("Rendimento médio real", ["renda"], None),
    ],
    "agro": [
        ("Safras Brasileiras de Grãos (CONAB)", ["safra"], None),
        ("Área plantada e produtividade média", [], None),
        ("PAM: Produção Agrícola Municipal (IBGE)", [], None),
    ],
    "comercio-exterior": [
        ("Exportações, importações e saldo por ano", ["exportacoes", "importacoes", "saldo_comercial"], None),
        ("Para onde o Brasil exporta", [], None),
        ("O que o Brasil exporta", [], None),
    ],
    "industria": [
        ("Evolução Temporal da Produção Física Industrial", ["industria"], None),
        ("Indústrias Extrativas vs. Indústrias de Transformação", [], None),
    ],
    "pecuaria": [
        ("Efetivo dos Rebanhos Brasileiros (Cabeças)", [], None),
        ("Abate de bovinos", ["abate_bovinos"], None),
        ("Produção de Origem Animal (Leite, Ovos, Mel)", [], None),
    ],
    "silvicultura": [
        ("Valor da Produção da Silvicultura (R$ Milhões)", [], None),
        ("Valor da Produção na Extração Vegetal Nativa (R$ Milhões)", [], None),
    ],
    "educacao": [
        ("Evolução do IDEB por Etapa de Ensino (Inep / MEC)", ["ideb_iniciais", "ideb_finais", "ideb_medio"], None),
        ("Taxa de Analfabetismo (%) — IBGE", ["analfabetismo"], None),
        ("Orçamento Executado do MEC (R$ bi)", [], None),
        ("Aprendizado: PISA (OCDE)", ["pisa_leitura", "pisa_matematica", "pisa_ciencias"], None),
        ("Alfabetização na idade certa e escola em tempo integral", [], None),
        ("Principais Políticas Educacionais de Cada Mandato", [], "Educação"),
    ],
    "saude": [
        ("Médicos", ["medicos"], None),
        ("Hospitais e leitos do SUS", ["leitos_sus"], None),
        ("Quanto o governo federal gasta com saúde", ["gasto_saude"], None),
        ("Vacinação", ["vacina_polio", "vacina_sarampo"], None),
        ("Quanto o brasileiro vive e quantos bebês morrem", ["esperanca_vida", "mortalidade_infantil"], None),
        ("Dengue: mortes por ano", [], None),
        ("Covid-19: óbitos acumulados", [], None),
        ("Programas de cada governo: o que foi feito, o que se diz de bom e as críticas", [], "Saúde"),
    ],
    "seguranca": [
        ("Taxa de Mortes Violentas Intencionais por 100 mil habitantes", ["homicidios"], None),
        ("Armas de fogo apreendidas pela PF", [], None),
        ("Feminicídios Registrados no Brasil", [], None),
        ("Políticas de segurança de cada governo", [], "Segurança Pública"),
    ],
    "inclusao": [
        ("Taxa de desemprego por sexo e cor/raça (%)", ["desemprego_negros"], None),
        ("Desigualdade de renda e pobreza", ["gini", "pobreza", "extrema_pobreza"], None),
        ("Violência contra grupos vulneráveis", [], None),
        ("Políticas para mulheres, negros, indígenas e LGBTQIA+", [], "Direitos & Minorias"),
    ],
    "meio-ambiente": [
        ("Desmatamento (PRODES, Amazônia)", ["desmatamento"], None),
        ("Focos de queimada no Brasil", [], None),
        ("Emissões de gases de efeito estufa", [], None),
        ("Políticas ambientais de cada governo", [], "Meio Ambiente & Clima"),
    ],
}


def render_seletor():
    """Seletor no topo das abas: Governo A x Governo B (padrão Bolsonaro x Lula 3) ou todos os governos."""
    governos = nomes_governos()
    if not governos:
        return PADRAO[0], PADRAO[1], False
    if st.session_state.pop("gov_reset_pedido", False):
        st.session_state["gov_a"], st.session_state["gov_b"], st.session_state["gov_todos"] = PADRAO[0], PADRAO[1], False
    st.session_state.setdefault("gov_a", PADRAO[0])
    st.session_state.setdefault("gov_b", PADRAO[1])
    with st.container(border=True):
        st.caption("Escolha os governos que quer comparar, de FHC a Lula 3. O padrão é Bolsonaro x Lula 3.")
        c1, c2, c3, c4 = st.columns([2.2, 0.35, 2.2, 1.9], vertical_alignment="bottom")
        a = c1.selectbox("Governo A", governos, key="gov_a")
        c2.markdown("<div style='text-align:center;font-weight:800;color:#94a3b8;padding-bottom:8px;'>x</div>", unsafe_allow_html=True)
        b = c3.selectbox("Governo B", governos, key="gov_b")
        todos = c4.toggle(TODOS, key="gov_todos", help="Mostra os 9 mandatos de FHC a Lula 3 lado a lado.")
        if (a, b) != PADRAO or todos:
            if c4.button("↺ Voltar para Bolsonaro x Lula 3", key="gov_reset", width="stretch"):
                st.session_state["gov_reset_pedido"] = True
                st.rerun()
    return a, b, todos


def _valor_txt(ind, gov):
    v = ind["mandato"].get(gov)
    if v is None:
        return "Sem dado*"
    outra, parcial = _marcados(ind)
    return fmt(v, ind["unidade"]) + ("*" if gov in outra else "") + ("†" if gov in parcial else "")


def _stat_par(ind, a, b):
    """Mesmo cartão 'antes ➔ depois' das abas originais, com as cores do partido de cada governo."""
    va, vb = ind["mandato"].get(a), ind["mandato"].get(b)
    melhor = None
    if va is not None and vb is not None and va != vb and ind["chave"] not in ("dolar", "importacoes") and not ind.get("sem_lado_melhor"):
        melhor = b if (vb > va) == ind["maior_melhor"] else a
    ca, cb = classe_gov(a), classe_gov(b)
    st.markdown(
        '<div class="kpi-card compare-stat">'
        f'<div class="compare-title">{html.escape(ind["nome"])}</div>'
        '<div class="compare-values">'
        f'<span class="compare-val {ca}{" is-better" if melhor == a else ""}">{_valor_txt(ind, a)}</span>'
        '<span class="compare-arrow">➔</span>'
        f'<span class="compare-val {cb}{" is-better" if melhor == b else ""}">{_valor_txt(ind, b)}</span>'
        '</div>'
        f'<div class="compare-foot">{html.escape(a)} ➔ {html.escape(b)} · {html.escape(ind["unidade"])} · '
        f'{seta_txt(ind)}</div>'
        '</div>', unsafe_allow_html=True)


def _janela(d, gov):
    g = next(x for x in d["governos"] if x["nome"] == gov)
    return g["inicio"], g["fim"] or "2099-12"


def _grafico_mensal(d, ind, chave, governos_sel):
    """Linhas mês a mês desde a posse, como os gráficos de Bolsonaro x Lula (ex.: inflação acumulada no mandato)."""
    fig = go.Figure()
    acumulado = ind.get("mensal_tipo") == "acumulado"
    for g in governos_sel:
        ini, fim = _janela(d, g)
        pontos = sorted((ym, v) for ym, v in ind["mensal"].items() if ini <= ym <= fim)
        if not pontos:
            continue
        ys, acc = [], 1.0
        for _, v in pontos:
            if acumulado:
                acc *= 1 + v / 100
                ys.append(round((acc - 1) * 100, 2))
            else:
                ys.append(v)
        fig.add_trace(go.Scatter(
            x=list(range(1, len(pontos) + 1)), y=ys, name=g, mode="lines", line=dict(color=COR_MANDATO.get(g), width=3),
            customdata=[ym for ym, _ in pontos], hovertemplate="Mês %{x} (%{customdata}): %{y:.2f}<extra>" + g + "</extra>"))
    titulo = ind["nome"].split(" (")[0]
    apply_plotly_theme(fig, title=f"{titulo} — mês a mês desde a posse ({ind.get('mensal_unidade', '')})", height=420)
    fig.update_xaxes(title="Meses de mandato")
    st.plotly_chart(fig, width="stretch", key=f"par_mensal_{chave}")


def _cobertura_mensal(d, ind, governos_sel):
    if "mensal" not in ind:
        return False
    for g in governos_sel:
        ini, fim = _janela(d, g)
        if sum(1 for ym in ind["mensal"] if ini <= ym <= fim) < 6:
            return False
    return True


def _grafico_anual_par(ind, chave, governos_sel):
    """Barras por ano com a cor do partido de cada governo, como os gráficos anuais das abas originais."""
    anual = pd.Series({int(a): v for a, v in ind["anual"].items()}).sort_index()
    anual = anual[[ano_gov(a) in governos_sel for a in anual.index]]
    if anual.empty:
        st.info("Sem dado anual para os governos escolhidos.")
        return
    outra = {int(a) for a in ind.get("outra_metodologia", [])} | {int(a) for a in ind.get("estimativa", [])}
    parcial = {int(a) for a in ind.get("parcial", [])}
    fig = go.Figure()
    for g in governos_sel:
        sub = anual[[ano_gov(a) == g for a in anual.index]]
        if sub.empty:
            continue
        rot = [fmt(v, ind["unidade"] if ind["unidade"] not in VARIACAO else "") + ("*" if x in outra else "") + ("†" if x in parcial else "")
               for x, v in sub.items()]
        fig.add_trace(go.Bar(
            x=[str(x) for x in sub.index], y=sub.values, name=g,
            marker=dict(color=COR_MANDATO.get(g), pattern=dict(shape=["/" if x in outra or x in parcial else "" for x in sub.index], fgcolor="rgba(15,23,42,0.55)")),
            text=rot if len(anual) <= 16 else None, textposition="outside", hovertemplate="%{x}: %{y}<extra>" + g + "</extra>"))
    apply_plotly_theme(fig, title=f"{ind['nome'].split(' (')[0]} — por ano", height=420)
    fig.update_layout(hovermode="closest", bargap=0.25)
    fig.update_xaxes(type="category", categoryorder="category ascending")
    st.plotly_chart(fig, width="stretch", key=f"par_anual_{chave}")


def _fonte(ind):
    simbolo, desc = CMP[ind["comparabilidade"]]
    extra = f' · <a href="{html.escape(ind["url_extra"], quote=True)}" target="_blank">série complementar ↗</a>' if ind.get("url_extra") else ""
    render_source(html.escape(ind["fonte"]) + f". Comparabilidade: {simbolo} {html.escape(desc)}" + extra, ind["url"])


def _sem_dado(titulo_secao, sel, motivo=None):
    """Seção sem série longa: mesmo lugar e mesmo título da versão padrão, com 'Sem dado' para cada governo escolhido."""
    chips = "".join(f'<span style="display:inline-block;margin:2px 6px 2px 0;padding:1px 9px;border-radius:999px;border:1px solid #64748b;font-size:0.78rem;">{html.escape(g)}: <b>Sem dado</b></span>' for g in sel)
    st.markdown(
        f'<div class="info-box"><b>Sem dado para comparar estes governos.</b> {chips}<br/>'
        f'{html.escape(motivo or "Esta medida não tem série longa e comparável nas fontes abertas consultadas, então não dá para colocar os governos escolhidos lado a lado. ")}'
        'Para Bolsonaro e Lula 3, quando existe, ela aparece na versão padrão da aba (botão "Voltar para Bolsonaro x Lula 3").</div>',
        unsafe_allow_html=True)


def render_aba_comparada(aba, a, b, todos):
    """Refaz a aba para outro par de governos (ou todos) no mesmo molde da aba Bolsonaro x Lula:
    cabeçalho, cartões 'A ➔ B', as mesmas seções numeradas (com gráfico, 'Sem dado' ou programas) e caixa de contexto no fim.
    Sempre devolve True: seção sem série mostra 'Sem dado' em vez de voltar ao padrão."""
    from modules.ui_components import render_section_header, css_governos, PARTIDO, PERIODO
    d = base()
    if a == b and not todos:
        st.info("Escolha dois governos diferentes.")
        return True
    st.markdown(css_governos(), unsafe_allow_html=True)
    governos = nomes_governos(d)
    sel = governos if todos else [a, b]
    titulo, sub = TITULOS.get(aba, (aba, ""))
    render_section_header(titulo, sub + (" Todos os governos, de FHC a Lula 3." if todos else f" {a} x {b}."))
    molde = MOLDE.get(aba, [])
    chaves = [k for k, v in d.get("indicadores", {}).items() if aba in v.get("abas", [])]
    usados = [k for _, ks, _ in molde for k in ks]
    # indicadores da aba que o molde não citou entram no fim, para nada sumir
    extras = [k for k in chaves if k not in usados]
    if extras:
        molde = molde + [("Outros indicadores desta aba", extras, None)]
    todas_chaves = list(dict.fromkeys(k for _, ks, _ in molde for k in ks if k in d["indicadores"]))
    inds = [{**d["indicadores"][k], "chave": k} for k in todas_chaves]

    # 1. Cartões (ou o quadro com todos os mandatos)
    if inds:
        if todos:
            st.markdown(quadro_html(inds, governos), unsafe_allow_html=True)
            st.caption(LEGENDA)
        else:
            cols = st.columns(3)
            for i, ind in enumerate(inds):
                with cols[i % 3]:
                    _stat_par(ind, a, b)

    # 2. Seções numeradas, na mesma ordem da versão padrão
    from modules.programas_ui import render_programas
    for n, (titulo_secao, ks, area_prog) in enumerate(molde, start=1):
        st.markdown("---")
        st.subheader(f"{n}. {titulo_secao}")
        if area_prog:
            render_programas(area_prog, sel, titulo=None, chave=f"cmp_{aba}_{n}")
            continue
        series = [{**d["indicadores"][k], "chave": k} for k in ks if k in d["indicadores"]]
        if not series:
            _sem_dado(titulo_secao, sel)
            continue
        for ind in series:
            if len(series) > 1:
                st.markdown(f"**{ind['nome'].split(' (')[0]}**")
            st.caption(ind["metodo"] + (" " + ind["nota"] if ind.get("nota") else ""))
            if _cobertura_mensal(d, ind, sel):
                _grafico_mensal(d, ind, ind["chave"], sel)
                if ind.get("mensal_tipo") == "acumulado":
                    _grafico_anual_par(ind, ind["chave"], sel)
            else:
                _grafico_anual_par(ind, ind["chave"], sel)
            faltam = [g for g in sel if ind["mandato"].get(g) is None]
            if faltam:
                st.caption("Sem dado para: " + ", ".join(faltam) + ". Nas barras e cartões aparece como \"Sem dado*\".")
            _fonte(ind)

    # 3. Contexto de cada período
    from modules.tabs_overview import CONTEXTO
    linhas = "".join(f'• <b>Governo {html.escape(g)} ({PARTIDO[g]}, {PERIODO[g]}):</b> {html.escape(CONTEXTO[g])}<br/>' for g in sel)
    st.markdown(
        f'<div class="info-box"><b>Contexto de cada período:</b><br/>{linhas}'
        '<span style="color:#94a3b8;font-size:0.8rem;">Séries longas e oficiais agregadas do mesmo jeito para todos os mandatos (acumulados viram taxa por ano; '
        'estoques viram variação no mandato). "Sem dado" = não há série comparável para o governo; número com * = dado de outra metodologia; † = ano parcial. '
        'Detalhes que só existem para Bolsonaro x Lula 3 (notícias, recortes por bioma ou modalidade) aparecem ao voltar ao padrão.</span></div>',
        unsafe_allow_html=True)
    return True
    st.markdown(css_governos(), unsafe_allow_html=True)
    governos = nomes_governos(d)
    sel = governos if todos else [a, b]
    titulo, sub = TITULOS.get(aba, (aba, ""))
    render_section_header(titulo, sub + (" Todos os governos, de FHC a Lula 3." if todos else f" {a} x {b}."))
    inds = [{**d["indicadores"][k], "chave": k} for k in chaves]

    # 1. Cartões (ou o quadro com todos os mandatos)
    if todos:
        st.markdown(quadro_html(inds, governos), unsafe_allow_html=True)
        st.caption(LEGENDA)
    else:
        cols = st.columns(3)
        for i, ind in enumerate(inds):
            with cols[i % 3]:
                _stat_par(ind, a, b)
    if aba == "visao-geral":
        nomes = {i["nome"]: i["chave"] for i in inds}
        k = nomes[st.selectbox("Ver ano a ano:", list(nomes), key="vg_hist_sel")]
        inds = [{**d["indicadores"][k], "chave": k}]

    # 2. Um gráfico por indicador, numerado como nas abas originais
    for n, ind in enumerate(inds, start=1):
        st.markdown("---")
        st.subheader(f"{n}. {ind['nome'].split(' (')[0]}")
        st.caption(ind["metodo"] + (" " + ind["nota"] if ind.get("nota") else ""))
        if _cobertura_mensal(d, ind, sel):
            _grafico_mensal(d, ind, ind["chave"], sel)
            if ind.get("mensal_tipo") == "acumulado":
                _grafico_anual_par(ind, ind["chave"], sel)
        else:
            _grafico_anual_par(ind, ind["chave"], sel)
        _fonte(ind)

    # 3. Programas de cada governo (benefícios e críticas), quando a área já foi mapeada
    if aba == "saude":
        from modules.programas_ui import render_programas
        st.markdown("---")
        render_programas("Saúde", sel, chave="cmp")

    # 4. Contexto de cada período
    from modules.tabs_overview import CONTEXTO
    linhas = "".join(f'• <b>Governo {html.escape(g)} ({PARTIDO[g]}, {PERIODO[g]}):</b> {html.escape(CONTEXTO[g])}<br/>' for g in sel)
    st.markdown(
        f'<div class="info-box"><b>Contexto de cada período:</b><br/>{linhas}'
        '<span style="color:#94a3b8;font-size:0.8rem;">Séries longas e oficiais agregadas do mesmo jeito para todos os mandatos (acumulados viram taxa por ano; '
        'estoques viram variação no mandato). "Sem dado*" = não há série comparável; número com * = dado de outra metodologia; † = ano parcial. '
        'Partes da aba que só existem para Bolsonaro x Lula 3 (políticas, notícias, detalhamentos) aparecem ao voltar ao padrão.</span></div>',
        unsafe_allow_html=True)
    return True
