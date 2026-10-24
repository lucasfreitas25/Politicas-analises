"""
Componentes da série histórica (FHC a Lula 3): quadro por mandato, gráfico anual, comparação entre dois governos
e a seção "Todos os governos" usada no fim de cada aba.
"""
import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.ui_components import apply_plotly_theme, render_source, fmt_br, COR_MANDATO, classe_gov, eh_celular

CMP = {"ok": ("✔", "mesma metodologia em toda a série"), "ajustado": ("≈", "ajustada (períodos ou bases diferentes)"),
       "ressalva": ("⚠", "a metodologia muda ou falta parte da série")}
ORDEM_EIXO = ["Economia", "Emprego e renda", "Sociedade", "Fiscal", "Meio ambiente"]
VARIACAO = ("pontos percentuais", "pontos do PIB", "pontos (0–100)")


def base():
    """historico.json com as séries extras (historico_extra.json) já juntas."""
    d = load_json("historico.json")
    extra = load_json("historico_extra.json").get("indicadores", {})
    if extra:
        d = {**d, "indicadores": {**d.get("indicadores", {}), **extra}}
    return d


def categorias():
    """Blocos 'um valor por categoria e por governo' (ex.: quanto cada item do IPCA subiu em cada mandato)."""
    return load_json("historico_extra.json").get("categorias", {})


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


def quadro_cartoes_html(indicadores, governos):
    """Versão para celular do quadro: um cartão por indicador, com um 'selo' por governo (cor = posição entre os mostrados)."""
    saida, eixo_atual = [], None
    for ind in sorted(indicadores, key=lambda i: ORDEM_EIXO.index(i["eixo"]) if i["eixo"] in ORDEM_EIXO else 9):
        if ind["eixo"] != eixo_atual:
            eixo_atual = ind["eixo"]
            saida.append(f'<div class="hist-eixo-m">{html.escape(eixo_atual)}</div>')
        vals = {g: ind["mandato"].get(g) for g in governos}
        com = sorted([g for g in governos if vals[g] is not None], key=lambda g: vals[g], reverse=ind["maior_melhor"])
        pos = {g: i for i, g in enumerate(com)}
        sem_lado = bool(ind.get("sem_lado_melhor"))
        outra, parcial = _marcados(ind)
        chips = []
        for g in governos:
            cor = COR_MANDATO.get(g, "#64748b")
            if g not in pos:
                chips.append(f'<div class="chip-gov hist-vazio" style="border-left-color:{cor};"><span>{html.escape(g)}</span><b>Sem dado</b></div>')
                continue
            marca = ("*" if g in outra else "") + ("†" if g in parcial else "")
            classe = "hist-c0" if sem_lado else _classe(pos[g], len(com))
            top = " 🥇" if pos[g] == 0 and not sem_lado and len(com) > 1 else ""
            chips.append(f'<div class="chip-gov {classe}" style="border-left-color:{cor};"><span>{html.escape(g)}</span>'
                         f'<b>{fmt(vals[g], ind["unidade"])}{marca}{top}</b></div>')
        simbolo = CMP[ind["comparabilidade"]][0]
        saida.append(
            f'<div class="ind-card"><div class="ind-card-t"><b>{html.escape(ind["nome"])}</b>'
            f'<div class="hist-sub">{html.escape(ind["unidade"])} · {seta_txt(ind)} · {simbolo} · '
            f'<a href="{html.escape(ind["url"], quote=True)}" target="_blank">dados ↗</a></div></div>'
            f'<div class="chip-grid">{"".join(chips)}</div></div>')
    return "".join(saida)


def quadro_html(indicadores, governos, destaque=None):
    """Tabela indicador x mandato com cores relativas (verde = melhor posição na linha, vermelho = pior).
    No celular vira uma lista de cartões, para não obrigar a rolar para o lado."""
    from modules.ui_components import eh_celular
    if eh_celular():
        return quadro_cartoes_html(indicadores, governos)
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
        ("Decomposição Setorial do IPCA (Grupos de Consumo)", ["@ipca_grupos"], None),
        ("Quanto cada item subiu em cada mandato", ["@ipca_itens"], None),
    ],
    "cesta-basica": [
        ("Quanto cada item subiu em cada mandato (IPCA oficial)", ["@ipca_itens"], None),
        ("Custo da cesta básica (São Paulo, R$ de hoje)", ["cesta_real"], None),
        ("Horas de trabalho para comprar a cesta", ["cesta_horas"], None),
        ("Poder de compra do salário mínimo", ["salario_minimo"], None),
        ("Inflação dos alimentos (IPCA)", ["ipca_alimentos"], None),
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
        ("Área plantada e produtividade média dos grãos", ["area_graos", "produtividade_graos"], None),
        ("PAM: Produção Agrícola Municipal (IBGE)", ["@pam_lavouras", "pam_area", "pam_valor"], None),
    ],
    "comercio-exterior": [
        ("Exportações, importações e saldo por ano", ["exportacoes", "importacoes", "saldo_comercial"], None),
        ("Para onde o Brasil exporta", ["@comex_destinos"], None),
        ("O que o Brasil exporta", ["@comex_pauta"], None),
    ],
    "industria": [
        ("Evolução Temporal da Produção Física Industrial", ["industria"], None),
        ("Indústrias Extrativas vs. Indústrias de Transformação", ["pim_extrativa", "pim_transformacao"], None),
    ],
    "pecuaria": [
        ("Efetivo dos Rebanhos Brasileiros", ["@ppm_rebanhos", "rebanho_bovino"], None),
        ("Abate de bovinos", ["abate_bovinos"], None),
        ("Produção de Origem Animal (Leite, Ovos, Mel)", ["leite", "ovos", "mel"], None),
    ],
    "silvicultura": [
        ("Valor da Produção da Silvicultura", ["silvicultura_valor"], None),
        ("Valor da Produção na Extração Vegetal Nativa", ["extracao_valor"], None),
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
        ("Emissões de gases de efeito estufa", ["emissoes"], None),
        ("Políticas ambientais de cada governo", [], "Meio Ambiente & Clima"),
    ],
}


def render_seletor():
    """Seletor no topo das abas: Governo A x Governo B (padrão Bolsonaro x Lula 3) ou todos os governos."""
    governos = nomes_governos()
    if not governos:
        return PADRAO[0], PADRAO[1], False
    # A escolha fica em chaves próprias (gov_a, gov_b, gov_todos), separadas das chaves dos campos (_w_...).
    # O Streamlit apaga o estado de um campo quando a página seguinte não o desenha; sem essa separação,
    # ao trocar de página o seletor caía no primeiro item da lista (FHC 1 x FHC 1).
    if st.session_state.pop("gov_reset_pedido", False):
        st.session_state["gov_a"], st.session_state["gov_b"], st.session_state["gov_todos"] = PADRAO[0], PADRAO[1], False
        for k in ("_w_gov_a", "_w_gov_b", "_w_gov_todos"):
            st.session_state.pop(k, None)
    for k, v in (("gov_a", PADRAO[0]), ("gov_b", PADRAO[1]), ("gov_todos", False)):
        st.session_state.setdefault(k, v)
    if st.session_state["gov_a"] not in governos:
        st.session_state["gov_a"] = PADRAO[0]
    if st.session_state["gov_b"] not in governos:
        st.session_state["gov_b"] = PADRAO[1]

    def _guardar(campo, chave):
        st.session_state[chave] = st.session_state[campo]

    with st.container(border=True, key="seletor_gov"):
        st.caption("Escolha os governos que quer comparar, de FHC a Lula 3. O padrão é Bolsonaro x Lula 3.")
        c1, c2, c3, c4 = st.columns([2.2, 0.35, 2.2, 1.9], vertical_alignment="bottom")
        for campo, chave in (("_w_gov_a", "gov_a"), ("_w_gov_b", "gov_b"), ("_w_gov_todos", "gov_todos")):
            st.session_state[campo] = st.session_state[chave]
        a = c1.selectbox("Governo A", governos, key="_w_gov_a", on_change=_guardar, args=("_w_gov_a", "gov_a"))
        c2.markdown("<div class='sel-x'>x</div>", unsafe_allow_html=True)
        b = c3.selectbox("Governo B", governos, key="_w_gov_b", on_change=_guardar, args=("_w_gov_b", "gov_b"))
        todos = c4.toggle(TODOS, key="_w_gov_todos", on_change=_guardar, args=("_w_gov_todos", "gov_todos"),
                          help="Mostra os 9 mandatos de FHC a Lula 3 lado a lado.")
        if (a, b) != PADRAO or todos:
            if c4.button("↺ Voltar para Bolsonaro x Lula 3", key="gov_reset", width="stretch"):
                st.session_state["gov_reset_pedido"] = True
                st.rerun()
        if todos:
            # no modo "Todos" dá para tirar ou pôr cada governo, o que evita tabelas e gráficos com 9 colunas no celular
            st.session_state.setdefault("gov_lista", list(governos))
            st.session_state["gov_lista"] = [g for g in st.session_state["gov_lista"] if g in governos] or list(governos)
            st.session_state["_w_gov_lista"] = st.session_state["gov_lista"]
            st.pills("Governos mostrados (toque para tirar ou pôr)", governos, selection_mode="multi", key="_w_gov_lista",
                     on_change=lambda: st.session_state.__setitem__("gov_lista", st.session_state["_w_gov_lista"] or list(governos)))
    st.session_state["gov_a"], st.session_state["gov_b"], st.session_state["gov_todos"] = a, b, todos
    return a, b, todos


def governos_ativos(todos, a, b):
    """Governos que a página deve mostrar: A e B, ou, no modo Todos, os que estão marcados no filtro (ao menos um)."""
    governos = nomes_governos()
    if not todos:
        return [a, b]
    marcados = [g for g in st.session_state.get("gov_lista", governos) if g in governos]
    return [g for g in governos if g in marcados] or list(governos)


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
            text=rot if len(anual) <= (8 if eh_celular() else 16) else None, textposition="outside", hovertemplate="%{x}: %{y}<extra>" + g + "</extra>"))
    apply_plotly_theme(fig, title=f"{ind['nome'].split(' (')[0]} — por ano", height=420)
    fig.update_layout(hovermode="closest", bargap=0.25)
    fig.update_xaxes(type="category", categoryorder="category ascending")
    st.plotly_chart(fig, width="stretch", key=f"par_anual_{chave}")


def _fonte(ind):
    simbolo, desc = CMP[ind["comparabilidade"]]
    extra = f' · <a href="{html.escape(ind["url_extra"], quote=True)}" target="_blank">série complementar ↗</a>' if ind.get("url_extra") else ""
    render_source(html.escape(ind["fonte"]) + f". Comparabilidade: {simbolo} {html.escape(desc)}" + extra, ind["url"])


def _grafico_categorias(bloco, sel, chave):
    """Barras agrupadas (até 3 governos) ou mapa de calor (mais governos): um valor por categoria e por governo."""
    cats = bloco["categorias"]
    unidade = bloco.get("unidade", "")
    c1, c2 = st.columns([1, 1.6])
    if bloco.get("categorias_ao_ano"):
        with c1:
            modo = st.segmented_control("Mostrar", ["Acumulado no mandato", "Média ao ano"], default="Acumulado no mandato", key=f"cat_modo_{chave}") or "Acumulado no mandato"
        if modo == "Média ao ano":
            cats, unidade = bloco["categorias_ao_ano"], "% ao ano"
    nomes = list(cats)
    grupos = bloco.get("grupos_de_itens")
    if grupos:
        with c2:
            g = st.segmented_control("Itens", list(grupos) + ["Todos"], default=list(grupos)[0], key=f"cat_grp_{chave}") or list(grupos)[0]
        if g != "Todos":
            nomes = [n for n in nomes if n in grupos[g]]
    from modules.ui_components import eh_celular, quebrar
    celular = eh_celular()
    if celular and len(sel) > 3:
        # muitos governos no celular: um item por vez, com uma barra por governo (o mapa de cores não cabe na tela)
        item = st.selectbox("Escolha o item", nomes, key=f"cat_item_{chave}")
        vals = [cats[item].get(g) for g in sel]
        fig = go.Figure(go.Bar(y=sel, x=[v if v is not None else 0 for v in vals], orientation="h", marker_color=[COR_MANDATO.get(g) for g in sel],
                               text=[fmt_br(v) if v is not None else "Sem dado" for v in vals], textposition="outside", cliponaxis=False,
                               textfont=dict(size=12, color="#ffffff"), hovertemplate="%{y}: %{text}<extra></extra>"))
        apply_plotly_theme(fig, title=f"{item} ({unidade})", height=44 * len(sel) + 130)
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#f8fafc"))
        fig.update_layout(showlegend=False, hovermode="closest", margin=dict(l=8, r=40, t=70, b=20))
        st.plotly_chart(fig, width="stretch", key=f"cat_{chave}")
        faltam = [g for g in sel if cats[item].get(g) is None]
        if faltam:
            st.caption("Sem dado: " + ", ".join(faltam) + ".")
        st.caption(bloco.get("metodo", "") + " " + bloco.get("nota", ""))
        render_source(html.escape(bloco["fonte"]), bloco["url"])
        return
    ref = next((x for x in reversed(sel) if any(cats[n].get(x) is not None for n in nomes)), sel[-1])
    nomes = sorted(nomes, key=lambda n: -(cats[n].get(ref) if cats[n].get(ref) is not None else -1e9))
    rotulo = (lambda n: quebrar(n, 22)) if celular else (lambda n: n)
    if len(sel) <= 3:
        fig = go.Figure()
        for gov in sel:
            vals = [cats[n].get(gov) for n in nomes]
            fig.add_trace(go.Bar(
                y=[rotulo(n) for n in nomes], x=[v if v is not None else 0 for v in vals], orientation="h", name=gov, marker_color=COR_MANDATO.get(gov),
                text=[fmt_br(v) if v is not None else "Sem dado" for v in vals], textposition="outside", cliponaxis=False,
                textfont=dict(size=11 if celular else 12),
                hovertemplate="%{y}: %{text}<extra>" + gov + "</extra>"))
        fig.update_layout(barmode="group", bargap=0.25)
        altura = len(nomes) * ((30 if celular else 16) * len(sel) + (22 if celular else 16)) + 140
        apply_plotly_theme(fig, title=f"{bloco['nome'].split(' (')[0]} ({unidade})", height=max(380, altura))
        fig.update_yaxes(autorange="reversed")
        if celular:
            fig.update_layout(margin=dict(l=8, r=48, t=90, b=70))
        fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", yanchor="top"))
    else:
        z = [[cats[n].get(gov) for gov in sel] for n in nomes]
        fig = go.Figure(go.Heatmap(z=z, x=sel, y=nomes, colorscale="RdYlGn" + ("_r" if bloco.get("maior_melhor") is False else ""),
                                   text=[[fmt_br(v) if v is not None else "Sem dado" for v in linha] for linha in z], texttemplate="%{text}",
                                   hovertemplate="%{y} · %{x}: %{text}<extra></extra>", showscale=False, xgap=2, ygap=2))
        apply_plotly_theme(fig, title=f"{bloco['nome'].split(' (')[0]} ({unidade})", height=max(380, 30 * len(nomes) + 140))
        fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch", key=f"cat_{chave}")
    faltas = {gov: [n for n in nomes if cats[n].get(gov) is None] for gov in sel}
    faltas = {gov: l for gov, l in faltas.items() if l}
    if faltas:
        st.caption("Sem dado: " + "; ".join(f"{gov} ({', '.join(l) if len(l) <= 4 else f'{len(l)} itens'})" for gov, l in faltas.items()) + ".")
    parcial = {n: p for n, p in bloco.get("parcial", {}).items() if n in nomes}
    if parcial:
        trechos = sorted({f"{gov}: {t}" for p in parcial.values() for gov, t in p.items() if gov in sel})
        if trechos:
            st.caption("Período parcial: " + "; ".join(trechos) + ".")
    st.caption(bloco.get("metodo", "") + " " + bloco.get("nota", ""))
    render_source(html.escape(bloco["fonte"]), bloco["url"])


def cards_padrao(aba, a=PADRAO[0], b=PADRAO[1]):
    """Cartões 'A ➔ B' no topo da versão padrão de uma aba, com o mesmo visual dos outros pares."""
    from modules.ui_components import css_governos
    d = base()
    ks = list(dict.fromkeys(k for _, lista, _ in MOLDE.get(aba, []) for k in lista if not k.startswith("@") and k in d["indicadores"]))
    if not ks:
        return
    st.markdown(css_governos(), unsafe_allow_html=True)
    cols = st.columns(3)
    for i, k in enumerate(ks[:6]):
        with cols[i % 3]:
            _stat_par({**d["indicadores"][k], "chave": k}, a, b)


def _sem_dado(titulo_secao, sel, motivo=None):
    """Seção sem série longa: mesmo lugar e mesmo título da versão padrão, com 'Sem dado' para cada governo escolhido."""
    chips = "".join(f'<span style="display:inline-block;margin:2px 6px 2px 0;padding:1px 9px;border-radius:999px;border:1px solid #64748b;font-size:0.78rem;">{html.escape(g)}: <b>Sem dado</b></span>' for g in sel)
    st.markdown(
        f'<div class="info-box"><b>Sem dado para comparar estes governos.</b> {chips}<br/>'
        f'{html.escape(motivo or "Esta medida não tem série longa e comparável nas fontes abertas consultadas, então não dá para colocar os governos escolhidos lado a lado. ")}'
        'Para Bolsonaro e Lula 3, quando existe, ela aparece na versão padrão da aba (botão "Voltar para Bolsonaro x Lula 3").</div>',
        unsafe_allow_html=True)


def _visao_geral_todos(d, sel, titulo):
    """Visão Geral para vários governos: quadro (ou cartões, no celular) com todos os indicadores e um gráfico ano a ano à escolha."""
    from modules.tabs_overview import CONTEXTO
    from modules.ui_components import PARTIDO, PERIODO
    inds = [{**v, "chave": k} for k, v in d["indicadores"].items() if "visao-geral" in v.get("abas", [])]
    st.markdown(quadro_html(inds, sel), unsafe_allow_html=True)
    st.caption(LEGENDA)
    st.markdown("---")
    nomes = {i["nome"]: i["chave"] for i in inds}
    k = nomes[st.selectbox("Ver ano a ano:", list(nomes), key="vg_hist_sel")]
    ind = {**d["indicadores"][k], "chave": k}
    st.subheader(ind["nome"].split(" (")[0])
    st.caption(ind["metodo"] + (" " + ind["nota"] if ind.get("nota") else ""))
    if _cobertura_mensal(d, ind, sel):
        _grafico_mensal(d, ind, k, sel)
        if ind.get("mensal_tipo") == "acumulado":
            _grafico_anual_par(ind, k, sel)
    else:
        _grafico_anual_par(ind, k, sel)
    faltam = [g for g in sel if ind["mandato"].get(g) is None]
    if faltam:
        st.caption("Sem dado para: " + ", ".join(faltam) + ".")
    _fonte(ind)
    linhas = "".join(f'• <b>Governo {html.escape(g)} ({PARTIDO[g]}, {PERIODO[g]}):</b> {html.escape(CONTEXTO[g])}<br/>' for g in sel)
    st.markdown(f'<div class="info-box"><b>Contexto de cada período:</b><br/>{linhas}</div>', unsafe_allow_html=True)


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
    governos = governos_ativos(todos, a, b)
    sel = governos
    titulo, sub = TITULOS.get(aba, (aba, ""))
    render_section_header(titulo, sub + (" Todos os governos, de FHC a Lula 3." if todos else f" {a} x {b}."))
    if aba == "visao-geral":
        _visao_geral_todos(d, sel, titulo)
        return True
    molde = MOLDE.get(aba, [])
    chaves = [k for k, v in d.get("indicadores", {}).items() if aba in v.get("abas", [])]
    usados = [k for _, ks, _ in molde for k in ks]
    # indicadores da aba que o molde não citou entram no fim, para nada sumir
    extras = [k for k in chaves if k not in usados]
    if extras:
        molde = molde + [("Outros indicadores desta aba", extras, None)]
    todas_chaves = list(dict.fromkeys(k for _, ks, _ in molde for k in ks if not k.startswith("@") and k in d["indicadores"]))
    blocos = categorias()
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
        itens = [("cat", blocos[k[1:]]) if k.startswith("@") and k[1:] in blocos else ("ind", {**d["indicadores"][k], "chave": k})
                 for k in ks if (k.startswith("@") and k[1:] in blocos) or k in d["indicadores"]]
        if not itens:
            _sem_dado(titulo_secao, sel)
            continue
        series = [x for t, x in itens if t == "ind"]
        for tipo, x in itens:
            if tipo == "cat":
                if len(itens) > 1:
                    st.markdown(f"**{x['nome'].split(' (')[0]}**")
                _grafico_categorias(x, sel, f"{aba}_{n}_{x['nome'][:20]}")
                continue
            ind = x
            if len(itens) > 1:
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
