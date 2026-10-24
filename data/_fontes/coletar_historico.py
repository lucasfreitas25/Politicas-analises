"""
Coleta séries longas (1995 em diante) para comparar todos os governos desde FHC e grava data/historico.json.

Fontes: Banco Central (SGS), Ipeadata (séries do IBGE harmonizadas pelo Ipea, Atlas da Violência) e Inpe (TerraBrasilis).
Cada indicador traz o método de agregação por mandato e as adaptações feitas quando a metodologia muda no meio da série.

Execute:  python data/_fontes/coletar_historico.py
"""
import json
import os
import time
import urllib.request

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "historico.json")

# Mandatos. Dilma foi afastada em 12/05/2016; nos dados mensais Temer começa em maio/2016.
# Nos dados anuais, 2016 vai para Temer (8 dos 12 meses), então Dilma 2 fica só com 2015.
GOVERNOS = [
    ("FHC 1", "1995-01", "1998-12"), ("FHC 2", "1999-01", "2002-12"),
    ("Lula 1", "2003-01", "2006-12"), ("Lula 2", "2007-01", "2010-12"),
    ("Dilma 1", "2011-01", "2014-12"), ("Dilma 2", "2015-01", "2016-04"),
    ("Temer", "2016-05", "2018-12"), ("Bolsonaro", "2019-01", "2022-12"),
    ("Lula 3", "2023-01", "2099-12"),
]
ANO_GOV = {}
for nome, ini, fim in GOVERNOS:
    for ano in range(int(ini[:4]), min(int(fim[:4]), 2030) + 1):
        ANO_GOV.setdefault(ano, nome)
ANO_GOV[2016] = "Temer"


def gov_mes(ym):
    for nome, ini, fim in GOVERNOS:
        if ini <= ym <= fim:
            return nome
    return None


def _get(url, tentativas=4):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=180) as r:
                return json.load(r)
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(5)


def sgs(codigo, inicio="01/01/1994"):
    v = _get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={inicio}&dataFinal=31/12/2026")
    return [(f"{x['data'][6:10]}-{x['data'][3:5]}", float(x["valor"])) for x in v]


def ipea(codigo, nivel=("", "Brasil", None)):
    v = _get(f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{codigo}')")["value"]
    return [(x["VALDATA"][:7], float(x["VALVALOR"])) for x in v if x["VALVALOR"] is not None and x.get("NIVNOME") in nivel]


def anual(pares):
    return {int(ym[:4]): v for ym, v in pares}


# ---------------------------------------------------------------- agregações por mandato
def por_mandato_anual(serie, func):
    out = {}
    for nome, *_ in GOVERNOS:
        vals = [(a, v) for a, v in sorted(serie.items()) if ANO_GOV.get(a) == nome and a >= 1995]
        if vals:
            out[nome] = func(vals)
    return out


def media(vals):
    return round(sum(v for _, v in vals) / len(vals), 2)


def media_geom(vals):
    p = 1.0
    for _, v in vals:
        p *= 1 + v / 100
    return round((p ** (1 / len(vals)) - 1) * 100, 2)


def variacao_pp(serie):
    """Diferença em pontos entre o último ano do mandato e o último ano do mandato anterior (ou o 1º ano disponível)."""
    def f(vals):
        primeiro = vals[0][0]
        base = serie.get(primeiro - 1)
        while base is None and primeiro - 1 >= min(serie) and primeiro - 1 not in serie:
            primeiro -= 1
            base = serie.get(primeiro - 1)
        base = base if base is not None else vals[0][1]
        return round(vals[-1][1] - base, 2)
    return f


def variacao_real_anualizada(serie):
    def f(vals):
        ano_ini = vals[0][0] - 1
        base = serie.get(ano_ini)
        while base is None and ano_ini >= min(serie):
            ano_ini -= 1
            base = serie.get(ano_ini)
        if base is None:
            ano_ini, base = vals[0]
        anos = vals[-1][0] - ano_ini
        if anos <= 0:
            return None
        return round(((vals[-1][1] / base) ** (1 / anos) - 1) * 100, 2)
    return f


def mensal_por_mandato(pares, func):
    out = {}
    for nome, ini, fim in GOVERNOS:
        vals = [(ym, v) for ym, v in pares if ini <= ym <= fim]
        if vals:
            r = func(vals, ini)
            if r is not None:
                out[nome] = r
    return out


def ipca_anualizado(vals, _ini):
    p = 1.0
    for _, v in vals:
        p *= 1 + v / 100
    return round((p ** (12 / len(vals)) - 1) * 100, 2)


def media_mensal(vals, _ini):
    return round(sum(v for _, v in vals) / len(vals), 2)


def var_real_mensal(pares):
    idx = dict(pares)
    def f(vals, ini):
        a, m = int(ini[:4]), int(ini[5:])
        anterior = f"{a - 1}-12" if m == 1 else f"{a}-{m - 1:02d}"
        base = idx.get(anterior, vals[0][1])
        meses = len(vals) + (1 if anterior in idx else 0) - 1
        if meses <= 0:
            return None
        return round(((vals[-1][1] / base) ** (12 / meses) - 1) * 100, 2)
    return f


def var_pp_mensal(pares):
    idx = dict(pares)
    def f(vals, ini):
        a, m = int(ini[:4]), int(ini[5:])
        anterior = f"{a - 1}-12" if m == 1 else f"{a}-{m - 1:02d}"
        if anterior not in idx:
            return None  # sem o ponto de partida o mandato não é comparável
        return round(vals[-1][1] - idx[anterior], 2)
    return f


def sgs_url(codigo):
    """Link direto para os dados exatos usados (CSV do SGS)."""
    return f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv"


def ipea_url(codigo):
    """Link para os dados exatos usados (API do Ipeadata). Parênteses e aspas vão codificados para o link não quebrar."""
    return f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie%28SERCODIGO=%27{codigo}%27%29"


SIDRA_TAB = "https://sidra.ibge.gov.br/tabela/"


def ultimo_por_mandato(serie):
    """Valor da última edição/ano disponível dentro de cada mandato (para indicadores bienais ou trienais)."""
    out = {}
    for nome, *_ in GOVERNOS:
        vals = [(a, v) for a, v in sorted(serie.items()) if ANO_GOV.get(a) == nome]
        if vals:
            out[nome] = vals[-1][1]
    return out


def deflacionar_mensal(pares, ipca_m):
    """Leva uma série mensal em R$ correntes para reais do último mês do IPCA."""
    idx, v = {}, 1.0
    for ym, x in ipca_m:
        v *= 1 + x / 100
        idx[ym] = v
    ultimo = idx[max(idx)]
    return [(ym, x * ultimo / idx[ym]) for ym, x in pares if ym in idx]


# Em quais abas cada indicador aparece
ABAS = {
    "pib": ["visao-geral", "macroeconomia"], "ipca": ["visao-geral", "inflacao"], "selic": ["visao-geral", "macroeconomia"],
    "desemprego": ["visao-geral", "trabalho"], "salario_minimo": ["visao-geral", "trabalho", "cesta-basica"],
    "renda": ["visao-geral", "trabalho", "fiscal-social-ambiental"], "gini": ["visao-geral", "fiscal-social-ambiental", "inclusao"],
    "pobreza": ["visao-geral", "fiscal-social-ambiental", "inclusao"], "extrema_pobreza": ["visao-geral", "fiscal-social-ambiental", "inclusao"],
    "homicidios": ["visao-geral", "seguranca"], "divida_liquida": ["visao-geral", "macroeconomia"],
    "divida_bruta": ["visao-geral", "macroeconomia"], "primario": ["visao-geral", "macroeconomia", "fiscal-social-ambiental"],
    "saldo_comercial": ["visao-geral", "comercio-exterior"], "desmatamento": ["visao-geral", "meio-ambiente"],
    "caged": ["trabalho"], "ipca_alimentos": ["inflacao", "cesta-basica"], "dolar": ["macroeconomia"],
    "exportacoes": ["comercio-exterior"], "importacoes": ["comercio-exterior"], "safra": ["agro"],
    "industria": ["industria"], "abate_bovinos": ["pecuaria"], "tarifa_energia": ["energia-agua-esgoto"],
    "inadimplencia_pf": ["inadimplencia"], "ideb_iniciais": ["educacao"], "ideb_finais": ["educacao"], "ideb_medio": ["educacao"],
    "pisa_leitura": ["educacao"], "pisa_matematica": ["educacao"], "pisa_ciencias": ["educacao"], "analfabetismo": ["educacao"],
    "mortalidade_infantil": ["saude"], "esperanca_vida": ["saude"], "desemprego_negros": ["inclusao"],
}


def main():
    ind = {}

    # PIB
    pib = anual(sgs(7326))
    ind["pib"] = {
        "nome": "Crescimento do PIB (média anual)", "unidade": "% ao ano", "maior_melhor": True, "eixo": "Economia",
        "anual": pib, "mandato": por_mandato_anual(pib, media_geom),
        "metodo": "Média geométrica das taxas anuais de cada mandato.", "comparabilidade": "ok",
        "fonte": "IBGE — Contas Nacionais, via Banco Central (SGS 7326)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "Lula 3 com 2023–2025 (2026 ainda não fechado).",
    }

    # IPCA
    ipca_m = [p for p in sgs(433) if p[0] >= "1995-01"]
    ipca_ano = {}
    for ym, v in ipca_m:
        ipca_ano.setdefault(int(ym[:4]), 1.0)
        ipca_ano[int(ym[:4])] *= 1 + v / 100
    ipca_ano = {a: round((p - 1) * 100, 2) for a, p in ipca_ano.items()}
    ind["ipca"] = {
        "nome": "Inflação (IPCA anualizado)", "unidade": "% ao ano", "maior_melhor": False, "eixo": "Economia",
        "anual": ipca_ano, "mandato": mensal_por_mandato(ipca_m, ipca_anualizado),
        "metodo": "Variações mensais encadeadas em cada mandato e convertidas em taxa anual (corrige mandatos de tamanhos diferentes).", "comparabilidade": "ok",
        "fonte": "IBGE — IPCA, via Banco Central (SGS 433)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "2026 é parcial no gráfico anual (até o último mês divulgado).",
    }

    # Selic
    selic_m = [p for p in sgs(4189) if p[0] >= "1995-01"]
    selic_ano = {}
    for ym, v in selic_m:
        selic_ano.setdefault(int(ym[:4]), []).append(v)
    ind["selic"] = {
        "nome": "Selic média", "unidade": "% ao ano", "maior_melhor": False, "eixo": "Economia",
        "anual": {a: round(sum(v) / len(v), 2) for a, v in selic_ano.items()}, "mandato": mensal_por_mandato(selic_m, media_mensal),
        "metodo": "Média da Selic mensal anualizada em cada mandato.", "comparabilidade": "ajustado",
        "fonte": "Banco Central (SGS 4189)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "Juro nominal: em 1995–1999 a inflação e o regime de câmbio eram outros, e o Banco Central só ganhou autonomia formal em 2021.",
    }

    # Desemprego: PNAD Contínua (2013+) e PNAD anual retropolada (1995–2012)
    pnadc = anual(ipea("PAN_TDESOC"))
    pnad = anual([p for p in ipea("Dese_Pnad", nivel=("Brasil",))])
    fator = sum(pnadc[a] / pnad[a] for a in (2013, 2014) if a in pnad and a in pnadc) / 2
    desemp = {a: round(v * fator, 2) for a, v in pnad.items() if a < 2013}
    desemp.update(pnadc)
    ind["desemprego"] = {
        "nome": "Desemprego médio", "unidade": "%", "maior_melhor": False, "eixo": "Emprego e renda",
        "anual": desemp, "anual_pnad_original": pnad, "anual_pnadc": pnadc, "fator_retropolacao": round(fator, 3),
        "mandato": por_mandato_anual(desemp, media),
        "metodo": f"PNAD Contínua a partir de 2013. Antes disso, PNAD anual multiplicada por {fator:.3f} (razão média PNADC/PNAD em 2013–2014), para ficar na escala da pesquisa atual.",
        "comparabilidade": "ressalva",
        "fonte": "IBGE — PNAD (1992–2014) e PNAD Contínua, via Ipeadata (Dese_Pnad e PAN_TDESOC)", "url": "http://www.ipeadata.gov.br/",
        "nota": "Retropolação feita pelo painel: as duas pesquisas medem desemprego de formas diferentes. Não há PNAD em 2000 e 2010 (anos de Censo).",
    }

    # Salário mínimo real
    sm = [p for p in ipea("GAC12_SALMINRE12") if p[0] >= "1994-01"]
    sm_ano = {}
    for ym, v in sm:
        if ym.endswith("-12") or ym == sm[-1][0]:
            sm_ano[int(ym[:4])] = round(v, 2)
    ind["salario_minimo"] = {
        "nome": "Salário mínimo real (ganho ao ano)", "unidade": "% ao ano", "maior_melhor": True, "eixo": "Emprego e renda",
        "anual": sm_ano, "mandato": mensal_por_mandato(sm, var_real_mensal(sm)),
        "metodo": "Variação real do mês anterior à posse até o último mês do mandato, convertida em taxa anual.", "comparabilidade": "ok",
        "fonte": "Ipea — salário mínimo real (deflacionado pelo INPC)", "url": "http://www.ipeadata.gov.br/",
        "nota": "O gráfico anual mostra o valor de dezembro de cada ano, em reais do último mês da série.",
    }

    # Renda, Gini e pobreza (PNAD/PNADC harmonizadas pelo Ipea)
    renda = anual(ipea("PNADS_RENDAMEDIA"))
    gini = anual(ipea("PNADS_GINI"))
    pob = anual(ipea("PNADS_PERCPOBRE830"))
    ext = anual(ipea("PNADS_PERCPOBRE300"))
    base_pnads = {"fonte": "Ipea — PNAD (até 2015) e PNAD Contínua (desde 2016), harmonizadas pelo Ipea", "url": "http://www.ipeadata.gov.br/",
                  "comparabilidade": "ajustado"}
    nota_pnads = "Série compatibilizada pelo Ipea entre a PNAD antiga e a PNAD Contínua; não há dados em 2000 e 2010 (anos de Censo). Mandato comparado com o último ano do governo anterior."
    ind["renda"] = {**base_pnads, "nome": "Renda domiciliar per capita real (ganho ao ano)", "unidade": "% ao ano", "maior_melhor": True, "eixo": "Emprego e renda",
                    "anual": renda, "mandato": por_mandato_anual(renda, variacao_real_anualizada(renda)),
                    "metodo": "Variação real anualizada da renda média per capita (todas as fontes).", "nota": nota_pnads}
    ind["gini"] = {**base_pnads, "nome": "Desigualdade (Gini, variação no mandato)", "unidade": "pontos (0–100)", "maior_melhor": False, "eixo": "Sociedade",
                   "anual": gini, "mandato": por_mandato_anual(gini, variacao_pp(gini)),
                   "metodo": "Diferença do Gini (escala 0–100) entre o fim do mandato e o fim do governo anterior. Negativo = desigualdade caiu.", "nota": nota_pnads}
    ind["pobreza"] = {**base_pnads, "nome": "Pobreza (US$ 8,30 PPC, variação no mandato)", "unidade": "pontos percentuais", "maior_melhor": False, "eixo": "Sociedade",
                      "anual": pob, "mandato": por_mandato_anual(pob, variacao_pp(pob)),
                      "metodo": "Diferença da % de pessoas abaixo da linha de US$ 8,30 por dia (PPC 2021) entre o fim do mandato e o fim do governo anterior.", "nota": nota_pnads}
    ind["extrema_pobreza"] = {**base_pnads, "nome": "Extrema pobreza (US$ 3,00 PPC, variação no mandato)", "unidade": "pontos percentuais", "maior_melhor": False, "eixo": "Sociedade",
                              "anual": ext, "mandato": por_mandato_anual(ext, variacao_pp(ext)),
                              "metodo": "Diferença da % de pessoas abaixo da linha de US$ 3,00 por dia (PPC 2021) entre o fim do mandato e o fim do governo anterior.", "nota": nota_pnads}

    # Homicídios
    hom = anual(ipea("AVIOL12_THOMIC", nivel=("Brasil",)))
    ind["homicidios"] = {
        "nome": "Taxa de homicídios (média)", "unidade": "por 100 mil", "maior_melhor": False, "eixo": "Sociedade",
        "anual": hom, "mandato": por_mandato_anual(hom, media),
        "metodo": "Média da taxa anual de homicídios de cada mandato.", "comparabilidade": "ajustado",
        "fonte": "Ipea/FBSP — Atlas da Violência, com dados do SIM/Ministério da Saúde", "url": "https://www.ipea.gov.br/atlasviolencia/",
        "nota": "Segurança é sobretudo responsabilidade dos estados; o dado mais recente sai com cerca de dois anos de atraso.",
    }

    # Fiscal: dívida líquida (dez/2001+), dívida bruta (dez/2006+), primário (2002+)
    dlsp = [p for p in sgs(4513, "01/12/2001")]
    dbgg = [p for p in sgs(13762, "01/12/2006")]
    nfsp = [p for p in ipea("BM12_NFSPPYS12")]
    prim_ano = {int(ym[:4]): round(-v, 2) for ym, v in nfsp if ym.endswith("-12")}
    ind["divida_liquida"] = {
        "nome": "Dívida líquida do setor público (variação no mandato)", "unidade": "pontos do PIB", "maior_melhor": False, "eixo": "Fiscal",
        "anual": {int(ym[:4]): v for ym, v in dlsp if ym.endswith("-12")}, "mandato": mensal_por_mandato(dlsp, var_pp_mensal(dlsp)),
        "metodo": "Diferença em pontos do PIB entre o mês anterior à posse e o último mês do mandato.", "comparabilidade": "ressalva",
        "fonte": "Banco Central (SGS 4513)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "A série atual começa em dez/2001: FHC 1 e FHC 2 ficam sem dado de mandato (só o ano de 2002 aparece no gráfico). A dívida líquida desconta reservas internacionais, então a alta do dólar a reduz.",
    }
    ind["divida_bruta"] = {
        "nome": "Dívida bruta do governo geral (variação no mandato)", "unidade": "pontos do PIB", "maior_melhor": False, "eixo": "Fiscal",
        "anual": {int(ym[:4]): v for ym, v in dbgg if ym.endswith("-12")}, "mandato": mensal_por_mandato(dbgg, var_pp_mensal(dbgg)),
        "metodo": "Diferença em pontos do PIB entre o mês anterior à posse e o último mês do mandato.", "comparabilidade": "ressalva",
        "fonte": "Banco Central (SGS 13762, metodologia a partir de 2008)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "A série começa em dez/2006: governos anteriores a Lula 2 ficam sem dado. A desvalorização do real e a inflação mexem no denominador (PIB nominal).",
    }
    ind["primario"] = {
        "nome": "Resultado primário (média anual)", "unidade": "% do PIB", "maior_melhor": True, "eixo": "Fiscal",
        "anual": prim_ano, "mandato": por_mandato_anual(prim_ano, media),
        "metodo": "Média do resultado primário do setor público consolidado em 12 meses até dezembro de cada ano (positivo = superávit).", "comparabilidade": "ressalva",
        "fonte": "Banco Central — NFSP sem desvalorização cambial, via Ipeadata (BM12_NFSPPYS12)", "url": "http://www.ipeadata.gov.br/",
        "nota": "A série começa em 2002 (FHC 1 sem dado; FHC 2 só com 2002). 2020 inclui os gastos da pandemia.",
    }

    # Comércio exterior
    bal = sgs(22707, "01/01/1995")
    bal_ano = {}
    for ym, v in bal:
        bal_ano[int(ym[:4])] = bal_ano.get(int(ym[:4]), 0) + v / 1000
    ultimo_mes = bal[-1][0]
    bal_ano = {a: round(v, 1) for a, v in bal_ano.items() if a < int(ultimo_mes[:4]) or ultimo_mes.endswith("-12")}
    ind["saldo_comercial"] = {
        "nome": "Saldo comercial (média anual)", "unidade": "US$ bilhões", "maior_melhor": True, "eixo": "Economia",
        "anual": bal_ano, "mandato": por_mandato_anual(bal_ano, media),
        "metodo": "Média dos saldos anuais da balança comercial (anos fechados).", "comparabilidade": "ajustado",
        "fonte": "Banco Central — balança comercial do balanço de pagamentos (SGS 22707)", "url": "https://www3.bcb.gov.br/sgspub/",
        "nota": "Dólares correntes, sem correção pela inflação americana; o saldo depende muito do câmbio e do preço das commodities.",
    }

    # Desmatamento (PRODES)
    rates = _get("https://terrabrasilis.dpi.inpe.br/app/prodes/dashboard/deforestation/files/rates2026.json")
    prodes = {}
    for p in rates["periods"]:
        prodes[p["endDate"]["year"]] = round(sum(a["area"] for f in p["features"] for a in f["areas"] if a["type"] == 1))
    ultimo = max(prodes)
    consolidados = {a: v for a, v in prodes.items() if a < ultimo}
    ind["desmatamento"] = {
        "nome": "Desmatamento na Amazônia (média anual)", "unidade": "km²", "maior_melhor": False, "eixo": "Meio ambiente",
        "anual": prodes, "estimativa": [ultimo], "mandato": por_mandato_anual(consolidados, media),
        "metodo": "Média das taxas anuais PRODES de cada mandato. O ano PRODES vai de agosto a julho e é atribuído ao governo em exercício de janeiro a julho.",
        "comparabilidade": "ajustado",
        "fonte": "Inpe — PRODES Amazônia Legal (TerraBrasilis)", "url": "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates",
        "nota": f"{ultimo} é estimativa e fica fora das médias. O ano de posse de cada governo inclui 5 meses do governo anterior.",
    }

    # ---------------- indicadores por aba
    # CAGED: antigo (mai/1999–2019) e Novo CAGED com ajustes (2020+)
    cag_old = ipea("CAGED12_SALDO12")
    cag_new = ipea("CAGED12_SALDONAJU12")
    cag = cag_old + [p for p in cag_new if p[0] >= "2020-01"]
    cag_ano = {}
    for ym, v in cag:
        cag_ano[int(ym[:4])] = cag_ano.get(int(ym[:4]), 0) + v / 1000
    ind["caged"] = {
        "nome": "Empregos formais criados (média por mês)", "unidade": "mil vagas/mês", "maior_melhor": True, "eixo": "Emprego e renda",
        "anual": {a: round(v, 0) for a, v in cag_ano.items()}, "mandato": mensal_por_mandato(cag, lambda vals, _i: round(sum(v for _, v in vals) / len(vals) / 1000, 1)),
        "metodo": "Saldo mensal médio (admissões menos desligamentos) em cada mandato, em mil vagas por mês.", "comparabilidade": "ressalva",
        "outra_metodologia": [a for a in cag_ano if a <= 2019], "parcial": [1999] + ([int(cag[-1][0][:4])] if not cag[-1][0].endswith("-12") else []),
        "fonte": "MTE — CAGED antigo (1999–2019) e Novo CAGED com ajustes (2020+), via Ipeadata", "url": ipea_url("CAGED12_SALDONAJU12"), "url_extra": ipea_url("CAGED12_SALDO12"),
        "nota": "A série pública começa em maio/1999: FHC 1 fica sem dado e FHC 2 começa no meio. Em 2020 o CAGED mudou (eSocial), e os níveis antes e depois não são totalmente comparáveis.",
    }

    # IPCA alimentação e bebidas
    ali_m = [p for p in sgs(1635) if p[0] >= "1995-01"]
    ali_ano = {}
    for ym, v in ali_m:
        ali_ano.setdefault(int(ym[:4]), 1.0)
        ali_ano[int(ym[:4])] *= 1 + v / 100
    ind["ipca_alimentos"] = {
        "nome": "Inflação de alimentos e bebidas (anualizada)", "unidade": "% ao ano", "maior_melhor": False, "eixo": "Economia",
        "anual": {a: round((p - 1) * 100, 2) for a, p in ali_ano.items()}, "mandato": mensal_por_mandato(ali_m, ipca_anualizado),
        "metodo": "Variação mensal do grupo Alimentação e bebidas do IPCA, encadeada e convertida em taxa anual.", "comparabilidade": "ok",
        "fonte": "IBGE — IPCA, grupo Alimentação e bebidas, via Banco Central (SGS 1635)", "url": sgs_url(1635),
        "nota": "Na aba Cesta Básica serve como aproximação: a série do DIEESE não está disponível em formato aberto desde 1995.",
    }

    # Dólar
    usd = [p for p in sgs(3698) if p[0] >= "1995-01"]
    usd_ano = {}
    for ym, v in usd:
        usd_ano.setdefault(int(ym[:4]), []).append(v)
    ind["dolar"] = {
        "nome": "Dólar médio (PTAX)", "unidade": "R$ por US$", "maior_melhor": False, "eixo": "Economia",
        "anual": {a: round(sum(v) / len(v), 2) for a, v in usd_ano.items()}, "mandato": mensal_por_mandato(usd, media_mensal),
        "metodo": "Média da cotação de venda mensal em cada mandato (valor nominal).", "comparabilidade": "ajustado",
        "fonte": "Banco Central — PTAX venda, média mensal (SGS 3698)", "url": sgs_url(3698),
        "nota": "Valor nominal: não desconta a inflação brasileira nem a americana. Dólar alto encarece importados, mas favorece exportadores; não há lado 'melhor' absoluto.",
    }

    # Exportações e importações
    for chave, cod, nome in (("exportacoes", 22708, "Exportações (média anual)"), ("importacoes", 22709, "Importações (média anual)")):
        serie = sgs(cod, "01/01/1995")
        anos = {}
        for ym, v in serie:
            anos[int(ym[:4])] = anos.get(int(ym[:4]), 0) + v / 1000
        ult = serie[-1][0]
        anos = {a: round(v, 1) for a, v in anos.items() if a < int(ult[:4]) or ult.endswith("-12")}
        ind[chave] = {
            "nome": nome, "unidade": "US$ bilhões", "maior_melhor": chave == "exportacoes", "eixo": "Economia",
            "anual": anos, "mandato": por_mandato_anual(anos, media),
            "metodo": "Média dos valores anuais (anos fechados), em dólares correntes.", "comparabilidade": "ajustado",
            "fonte": f"Banco Central — balanço de pagamentos (SGS {cod})", "url": sgs_url(cod),
            "nota": "Dólares correntes; o valor depende de preços internacionais. Importação maior não é necessariamente ruim (reflete consumo e investimento).",
        }

    # Safra de grãos (CONAB)
    saf = {a: round(v / 1000, 1) for a, v in anual(ipea("DEPAE_SAFRA")).items()}
    ind["safra"] = {
        "nome": "Safra de grãos (média anual)", "unidade": "milhões de t", "maior_melhor": True, "eixo": "Economia",
        "anual": saf, "mandato": por_mandato_anual(saf, media),
        "metodo": "Média da produção de grãos de cada mandato; cada safra é atribuída ao ano em que termina (2024/25 = 2025).", "comparabilidade": "ajustado",
        "fonte": "CONAB — série histórica de grãos, via Ipeadata (DEPAE_SAFRA)", "url": ipea_url("DEPAE_SAFRA"),
        "nota": "Produção cresce com área e tecnologia ao longo de décadas, então mandatos mais recentes tendem a ter safras maiores. Clima pesa mais que política no curto prazo.",
    }

    # Produção industrial
    pim = ipea("PIMPFN12_QIIGNN12")
    pim_ano = {}
    for ym, v in pim:
        pim_ano.setdefault(int(ym[:4]), []).append(v)
    pim_ano = {a: round(sum(v) / len(v), 2) for a, v in pim_ano.items() if len(v) == 12}
    ind["industria"] = {
        "nome": "Produção industrial (crescimento ao ano)", "unidade": "% ao ano", "maior_melhor": True, "eixo": "Economia",
        "anual": pim_ano, "mandato": por_mandato_anual(pim_ano, variacao_real_anualizada(pim_ano)),
        "metodo": "Variação anualizada da média anual do índice de produção física (2022 = 100) entre o fim do mandato anterior e o fim do mandato.", "comparabilidade": "ressalva",
        "fonte": "IBGE — PIM-PF, indústria geral, via Ipeadata (PIMPFN12_QIIGNN12)", "url": ipea_url("PIMPFN12_QIIGNN12"),
        "nota": "A série atual começa em 2002: FHC 1 e FHC 2 ficam sem dado de mandato. O gráfico anual mostra o índice médio de cada ano.",
    }

    # Abate de bovinos
    bov = {a: round(v / 1000, 2) for a, v in anual(ipea("ABATE_ABQUBV")).items() if a >= 1994}
    ind["abate_bovinos"] = {
        "nome": "Abate de bovinos (crescimento ao ano)", "unidade": "% ao ano", "maior_melhor": True, "eixo": "Economia",
        "anual": bov, "mandato": por_mandato_anual(bov, variacao_real_anualizada(bov)),
        "metodo": "Variação anualizada do número de cabeças abatidas (milhões) entre o fim do mandato anterior e o fim do mandato.", "comparabilidade": "ajustado",
        "fonte": "IBGE — Pesquisa Trimestral do Abate, via Ipeadata (ABATE_ABQUBV)", "url": ipea_url("ABATE_ABQUBV"),
        "nota": "O abate segue o ciclo do gado (retenção e descarte de fêmeas) e a demanda externa; o gráfico anual mostra milhões de cabeças.",
    }

    # Tarifa residencial de energia (real)
    tar = [p for p in ipea("ELETRO12_CEETRES12") if p[0] >= "1995-01"]
    tar_real = deflacionar_mensal(tar, ipca_m)
    tar_ano = {}
    for ym, v in tar_real:
        tar_ano.setdefault(int(ym[:4]), []).append(v)
    ind["tarifa_energia"] = {
        "nome": "Tarifa residencial de energia (variação real ao ano)", "unidade": "% ao ano", "maior_melhor": False, "eixo": "Economia",
        "anual": {a: round(sum(v) / len(v), 1) for a, v in tar_ano.items()}, "mandato": mensal_por_mandato(tar_real, var_real_mensal(tar_real)),
        "metodo": "Tarifa média residencial (R$/MWh) deflacionada pelo IPCA; variação real do mês anterior à posse ao último mês do mandato, ao ano.", "comparabilidade": "ajustado",
        "fonte": "Tarifa média residencial por MWh (Eletrobras/Aneel), via Ipeadata (ELETRO12_CEETRES12), deflacionada pelo painel", "url": ipea_url("ELETRO12_CEETRES12"),
        "nota": "Gráfico anual em R$/MWh a preços do último mês. Inclui efeitos de bandeiras, subsídios (CDE) e da MP 579/2013, que reduziu tarifas por um período.",
    }

    # Inadimplência PF
    inad = ipea("BM12_CINPF12")
    inad_ano = {}
    for ym, v in inad:
        inad_ano.setdefault(int(ym[:4]), []).append(v)
    ind["inadimplencia_pf"] = {
        "nome": "Inadimplência de pessoas físicas (média)", "unidade": "% da carteira", "maior_melhor": False, "eixo": "Economia",
        "anual": {a: round(sum(v) / len(v), 2) for a, v in inad_ano.items()}, "mandato": mensal_por_mandato(inad, media_mensal),
        "metodo": "Média mensal da inadimplência (atraso acima de 90 dias) da carteira de crédito a pessoas físicas.", "comparabilidade": "ressalva",
        "fonte": "Banco Central — notas de crédito, via Ipeadata (BM12_CINPF12)", "url": ipea_url("BM12_CINPF12"),
        "nota": "A série atual começa em março/2011: de FHC a Lula 2 não há dado comparável (o BC mudou a metodologia das estatísticas de crédito).",
    }

    # IDEB (Inep, planilha oficial até 2023 + divulgação de 2025)
    ideb = {
        "ideb_iniciais": ("Anos iniciais (1º ao 5º)", {2005: 3.8, 2007: 4.2, 2009: 4.6, 2011: 5.0, 2013: 5.2, 2015: 5.5, 2017: 5.8, 2019: 5.9, 2021: 5.8, 2023: 6.0, 2025: 6.3}),
        "ideb_finais": ("Anos finais (6º ao 9º)", {2005: 3.5, 2007: 3.8, 2009: 4.0, 2011: 4.1, 2013: 4.2, 2015: 4.5, 2017: 4.7, 2019: 4.9, 2021: 5.1, 2023: 5.0, 2025: 5.3}),
        "ideb_medio": ("Ensino médio", {2005: 3.4, 2007: 3.5, 2009: 3.6, 2011: 3.7, 2013: 3.7, 2015: 3.7, 2017: 3.8, 2019: 4.2, 2021: 4.2, 2023: 4.3, 2025: 4.5}),
    }
    for chave, (etapa, serie) in ideb.items():
        ind[chave] = {
            "nome": f"IDEB — {etapa} (última edição do mandato)", "unidade": "nota 0–10", "maior_melhor": True, "eixo": "Sociedade",
            "anual": serie, "mandato": ultimo_por_mandato(serie),
            "metodo": "Nota da última edição do IDEB (bienal) realizada em cada mandato.", "comparabilidade": "ajustado",
            "fonte": "Inep — planilha oficial do Ideb (2005–2023) e divulgação de 05/08/2026 (2025)", "url": "https://download.inep.gov.br/ideb/resultados/divulgacao_brasil_ideb_2023.xlsx",
            "nota": "O IDEB começou em 2005: FHC 1 e FHC 2 não têm dado. Edições nos anos ímpares; 2015 (Dilma 2) e 2017 (Temer) ficam cada uma com o seu governo. 2021 foi afetado pela pandemia.",
        }

    # PISA (tabela do Inep no relatório de 2025)
    pisa = {
        "pisa_leitura": ("Leitura", {2000: 396, 2003: 403, 2006: 393, 2009: 412, 2012: 407, 2015: 407, 2018: 413, 2022: 410, 2025: 408}, []),
        "pisa_matematica": ("Matemática", {2003: 356, 2006: 370, 2009: 386, 2012: 389, 2015: 377, 2018: 384, 2022: 379, 2025: 377}, []),
        "pisa_ciencias": ("Ciências", {2006: 390, 2009: 405, 2012: 402, 2015: 401, 2018: 404, 2022: 403, 2025: 409}, []),
    }
    for chave, (area, serie, _x) in pisa.items():
        ind[chave] = {
            "nome": f"PISA — {area} (última prova do mandato)", "unidade": "pontos", "maior_melhor": True, "eixo": "Sociedade",
            "anual": serie, "mandato": ultimo_por_mandato(serie),
            "metodo": "Nota média do Brasil na última aplicação do PISA (trienal) feita em cada mandato. O ano é o da aplicação da prova.", "comparabilidade": "ajustado",
            "fonte": "OCDE/Inep — tabela de médias do Brasil no relatório PISA 2025 (Inep, set/2026)", "url": "https://static.poder360.com.br/uploads/2026/09/Resultados_Pisa_2025_Final.pdf",
            "nota": "Matemática só é comparável desde 2003 e Ciências desde 2006 (a OCDE mudou as escalas). Dilma 2 fica com 2015 e Temer com 2018. Mandatos sem prova ficam com —.",
        }

    # Analfabetismo: Censo (1991, 2000, 2010, 2022) e PNAD Contínua (2016+)
    cen = anual(ipea("ADH_T_ANALF15M"))
    pnc = anual(ipea("PNADCA_TXA15MUF"))
    anf = {**{a: round(v, 1) for a, v in cen.items() if a >= 1991 and a not in pnc}, **{a: round(v, 1) for a, v in pnc.items()}}
    ind["analfabetismo"] = {
        "nome": "Analfabetismo, 15 anos ou mais (último dado do mandato)", "unidade": "%", "maior_melhor": False, "eixo": "Sociedade",
        "anual": anf, "mandato": ultimo_por_mandato({a: v for a, v in anf.items() if a >= 1995}), "outra_metodologia": [a for a in cen if a not in pnc],
        "metodo": "Último dado disponível em cada mandato. Censo em 2000, 2010 e 2022; PNAD Contínua de 2016 em diante.", "comparabilidade": "ressalva",
        "fonte": "IBGE — Censos (via Atlas do Desenvolvimento Humano/Ipea) e PNAD Contínua", "url": ipea_url("PNADCA_TXA15MUF"), "url_extra": ipea_url("ADH_T_ANALF15M"),
        "nota": "Censo e PNAD Contínua têm métodos diferentes (marcados com *). Sem dado nos mandatos sem Censo nem PNAD Contínua (FHC 1, Lula 1, Dilma 1). A queda é estrutural, pela troca de gerações.",
    }

    # Saúde: projeções do IBGE (revisão 2018) — outra metodologia
    # Valores medidos (Tábuas de Mortalidade do IBGE) substituem a projeção onde existem
    medido_tmi = {2022: 12.9, 2023: 12.5, 2024: 12.3}
    medido_esv = {2019: 76.2, 2020: 74.8, 2021: 72.8, 2022: 75.5, 2023: 76.4, 2024: 76.6}
    proj_tmi = {a: round(v, 1) for a, v in anual(ipea("DEPIS_TMI")).items() if a not in medido_tmi}
    proj_esv = {a: round(v, 1) for a, v in anual(ipea("DEPIS_ESVIDA")).items() if a not in medido_esv}
    tmi = {**proj_tmi, **medido_tmi}
    esv = {**proj_esv, **medido_esv}
    for chave, serie, nome, unid, maior in (("mortalidade_infantil", tmi, "Mortalidade infantil (último ano do mandato)", "por mil nascidos", False),
                                            ("esperanca_vida", esv, "Esperança de vida ao nascer (último ano do mandato)", "anos", True)):
        ind[chave] = {
            "nome": nome, "unidade": unid, "maior_melhor": maior, "eixo": "Sociedade",
            "anual": serie, "mandato": ultimo_por_mandato(serie),
            "outra_metodologia": list(proj_tmi if chave == "mortalidade_infantil" else proj_esv),
            "metodo": "Valor do último ano de cada mandato. Anos marcados com * vêm da projeção da população do IBGE (revisão 2018); os demais são medidos nas Tábuas de Mortalidade.", "comparabilidade": "ressalva",
            "fonte": f"IBGE — Projeção da População (revisão 2018), via Ipeadata ({'DEPIS_TMI' if chave == 'mortalidade_infantil' else 'DEPIS_ESVIDA'})",
            "url": ipea_url("DEPIS_TMI" if chave == "mortalidade_infantil" else "DEPIS_ESVIDA"),
            "nota": "A projeção (anos com *) foi feita antes da pandemia e do Censo 2022, então tende a ficar acima do medido; serve para ver a tendência longa. "
                    "Valores medidos: esperança de vida de 2019 a 2024 e mortalidade infantil de 2022 a 2024 (Tábuas de Mortalidade 2022 e 2024).",
        }

    # Desemprego de pretos e pardos (PNAD Contínua, 2012+)
    neg = ipea("PNADCT_TXDSCUPUF_NEG", nivel=("Brasil",))
    neg_ano = {}
    for ym, v in neg:
        neg_ano.setdefault(int(ym[:4]), []).append(v)
    neg_ano = {a: round(sum(v) / len(v), 1) for a, v in neg_ano.items()}
    ind["desemprego_negros"] = {
        "nome": "Desemprego de pretos e pardos (média)", "unidade": "%", "maior_melhor": False, "eixo": "Emprego e renda",
        "anual": neg_ano, "mandato": por_mandato_anual(neg_ano, media),
        "metodo": "Média anual da taxa trimestral de desocupação de pretos e pardos, por mandato.", "comparabilidade": "ressalva",
        "fonte": "IBGE — PNAD Contínua trimestral, via Ipeadata (PNADCT_TXDSCUPUF_NEG)", "url": ipea_url("PNADCT_TXDSCUPUF_NEG"),
        "nota": "A PNAD Contínua começa em 2012: de FHC a Lula 2 não há dado nesta série, e Dilma 1 tem só 2012–2014.",
    }

    # Pobreza, extrema pobreza e Gini: o que importa é QUANTO CAIU. Mostrar "queda" com número positivo evita a leitura
    # confusa de "-11 contra -8" (aqui, maior queda = melhor).
    ind["pobreza"].update(nome="Queda da pobreza no mandato (US$ 8,30 PPC)", unidade="p.p. de queda", maior_melhor=True,
                          metodo="Quantos pontos percentuais a parcela de pessoas abaixo da linha de US$ 8,30 por dia (PPC 2021) caiu entre o fim do governo anterior e o fim do mandato. "
                                 "Número positivo = a pobreza caiu; negativo = subiu. Quanto maior a queda, melhor.")
    ind["extrema_pobreza"].update(nome="Queda da extrema pobreza no mandato (US$ 3,00 PPC)", unidade="p.p. de queda", maior_melhor=True,
                                  metodo="Quantos pontos percentuais a parcela de pessoas abaixo da linha de US$ 3,00 por dia (PPC 2021) caiu entre o fim do governo anterior e o fim do mandato. "
                                         "Número positivo = caiu; negativo = subiu. Quanto maior a queda, melhor.")
    ind["gini"].update(nome="Queda da desigualdade (Gini) no mandato", unidade="pontos de queda", maior_melhor=True,
                       metodo="Quantos pontos o Gini (escala 0–100) caiu entre o fim do governo anterior e o fim do mandato. "
                              "Número positivo = a desigualdade caiu; negativo = subiu. Quanto maior a queda, melhor.")
    for k in ("pobreza", "extrema_pobreza", "gini"):
        ind[k]["mandato"] = {g: round(-v, 2) for g, v in ind[k]["mandato"].items()}
    ind["divida_liquida"]["nome"] = "Variação da dívida líquida no mandato"
    ind["divida_bruta"]["nome"] = "Variação da dívida bruta no mandato"
    for k in ("divida_liquida", "divida_bruta"):
        ind[k]["metodo"] += " Número negativo = a dívida caiu (isso é bom); positivo = subiu."

    # Séries mensais (para os gráficos "mês a mês desde a posse", no mesmo formato das abas originais)
    pnadc_m = ipea("PNADC12_TDESOC12")
    mensais = {
        "ipca": ({ym: v for ym, v in ipca_m}, "acumulado", "% acumulado desde a posse"),
        "ipca_alimentos": ({ym: v for ym, v in ali_m}, "acumulado", "% acumulado desde a posse"),
        "selic": (dict(selic_m), "nivel", "% ao ano"),
        "dolar": (dict(usd), "nivel", "R$ por US$"),
        "salario_minimo": ({ym: round(v, 2) for ym, v in sm}, "nivel", "R$ (do último mês)"),
        "inadimplencia_pf": (dict(inad), "nivel", "% da carteira"),
        "tarifa_energia": ({ym: round(v, 1) for ym, v in tar_real}, "nivel", "R$/MWh (do último mês)"),
        "caged": ({ym: round(v / 1000, 1) for ym, v in cag}, "nivel", "mil vagas no mês"),
        "desemprego": ({ym: v for ym, v in pnadc_m}, "nivel", "% (PNAD Contínua, trimestre móvel)"),
        "divida_liquida": (dict(dlsp), "nivel", "% do PIB"),
        "divida_bruta": (dict(dbgg), "nivel", "% do PIB"),
        "primario": ({ym: round(-v, 2) for ym, v in nfsp}, "nivel", "% do PIB em 12 meses"),
    }
    for k, (serie, tipo, unidade) in mensais.items():
        ind[k]["mensal"] = serie
        ind[k]["mensal_tipo"] = tipo
        ind[k]["mensal_unidade"] = unidade

    # Indicadores de saúde que dependem de saude_series.json (rode coletar_saude.py antes)
    caminho_saude = os.path.join(os.path.dirname(OUT), "saude_series.json")
    if os.path.exists(caminho_saude):
        ss = json.load(open(caminho_saude, encoding="utf-8"))

        def serie_int(d):
            return {int(a): v for a, v in d.items()}

        def add(chave, nome, unidade, maior_melhor, serie, fonte, url, nota, parcial, sem_lado=False, metodo=None):
            ind[chave] = {
                "nome": nome, "unidade": unidade, "maior_melhor": maior_melhor, "eixo": "Sociedade", "anual": serie,
                "mandato": por_mandato_anual(serie, media), "parcial": parcial, "comparabilidade": "ajustado",
                "metodo": metodo or "Média dos valores anuais de cada mandato.", "fonte": fonte, "url": url, "nota": nota, "abas": ["saude"],
                **({"sem_lado_melhor": True} if sem_lado else {}),
            }

        add("medicos", "Médicos por 10 mil habitantes (média)", "por 10 mil hab.", True, serie_int(ss["medicos_por_10mil"]["serie"]),
            ss["medicos_por_10mil"]["fonte"], ss["medicos_por_10mil"]["url"],
            "A série do CNES começa em 2010: Lula 2 aparece só com 2010 (†) e os governos anteriores ficam sem dado. " + ss["medicos_por_10mil"]["nota"], [2010])
        add("leitos_sus", "Leitos de internação do SUS por 10 mil habitantes (média)", "por 10 mil hab.", True, serie_int(ss["leitos"]["sus_por_10mil"]),
            ss["leitos"]["fonte"], ss["leitos"]["url"], "A série começa em 2010: Lula 2 aparece só com 2010 (†). " + ss["leitos"]["nota"], [2010])
        gasto = {int(a): v["pago_real_2025_bi"] for a, v in ss["gasto_federal_saude"]["serie"].items()}
        add("gasto_saude", "Despesa federal em saúde (R$ bi de 2025, média anual)", "R$ bi de 2025", True, gasto,
            ss["gasto_federal_saude"]["fonte"], ss["gasto_federal_saude"]["url"],
            "A série pública começa em 2014: Dilma 1 aparece só com 2014 (†). Gastar mais não significa, por si só, atender melhor, por isso o painel não aponta um lado melhor. "
            + ss["gasto_federal_saude"]["nota"], [2014], sem_lado=True)
        add("vacina_polio", "Cobertura da vacina contra a pólio (média)", "% das crianças", True, serie_int(ss["vacinacao_oms"]["poliomielite_3_doses"]),
            ss["vacinacao_oms"]["fonte"], ss["vacinacao_oms"]["url"], "A série da OMS começa em 2000: FHC 2 aparece só com 2000–2002 (†). " + ss["vacinacao_oms"]["nota"], [2000])
        add("vacina_sarampo", "Cobertura da vacina tríplice viral, 1ª dose (média)", "% das crianças", True, serie_int(ss["vacinacao_oms"]["sarampo_1_dose"]),
            ss["vacinacao_oms"]["fonte"], ss["vacinacao_oms"]["url"], "A série da OMS começa em 2000: FHC 2 aparece só com 2000–2002 (†). " + ss["vacinacao_oms"]["nota"], [2000])

    # Links diretos para as séries já existentes
    links = {"pib": sgs_url(7326), "ipca": sgs_url(433), "selic": sgs_url(4189), "salario_minimo": ipea_url("GAC12_SALMINRE12"),
             "renda": ipea_url("PNADS_RENDAMEDIA"), "gini": ipea_url("PNADS_GINI"), "pobreza": ipea_url("PNADS_PERCPOBRE830"),
             "extrema_pobreza": ipea_url("PNADS_PERCPOBRE300"), "homicidios": ipea_url("AVIOL12_THOMIC"),
             "divida_liquida": sgs_url(4513), "divida_bruta": sgs_url(13762), "primario": ipea_url("BM12_NFSPPYS12"),
             "saldo_comercial": sgs_url(22707), "desemprego": ipea_url("PAN_TDESOC")}
    for k, u in links.items():
        ind[k]["url"] = u

    # Página oficial e legível de cada série como link principal; o dado bruto do Ipeadata fica como link complementar
    paginas = {
        "desemprego": (SIDRA_TAB + "4099", ipea_url("Dese_Pnad")),
        "salario_minimo": ("http://www.ipeadata.gov.br/ExibeSerie.aspx?oper=view&module=M&serid=37667", None),
        "homicidios": ("https://www.ipea.gov.br/atlasviolencia/", None),  # a série bruta tem todos os municípios e é pesada demais para abrir
        "primario": (sgs_url(5793), None),
        "inadimplencia_pf": (sgs_url(21084), None),
        "safra": ("https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/series-historicas", ipea_url("DEPAE_SAFRA")),
        "industria": (SIDRA_TAB + "8888", ipea_url("PIMPFN12_QIIGNN12")),
        "abate_bovinos": (SIDRA_TAB + "1092", ipea_url("ABATE_ABQUBV")),
        "analfabetismo": (SIDRA_TAB + "7113", "https://www.atlasbrasil.org.br/consulta/planilha"),
        "desemprego_negros": (SIDRA_TAB + "6402", ipea_url("PNADCT_TXDSCUPUF_NEG")),
        "mortalidade_infantil": ("https://www.ibge.gov.br/estatisticas/sociais/populacao/9126-tabuas-completas-de-mortalidade.html", ipea_url("DEPIS_TMI")),
        "esperanca_vida": ("https://www.ibge.gov.br/estatisticas/sociais/populacao/9126-tabuas-completas-de-mortalidade.html", ipea_url("DEPIS_ESVIDA")),
    }
    for k, (principal, extra) in paginas.items():
        ind[k]["url"] = principal
        if extra:
            ind[k]["url_extra"] = extra
    ind["primario"]["fonte"] = "Banco Central — NFSP do setor público consolidado, resultado primário em 12 meses (SGS 5793, sinal invertido)"
    ind["inadimplencia_pf"]["fonte"] = "Banco Central — inadimplência das operações de crédito a pessoas físicas (SGS 21084)"
    ind["desemprego"]["fonte"] = "IBGE — PNAD Contínua (SIDRA 4099; média anual via Ipeadata PAN_TDESOC) e PNAD anual de 1992–2014 (Ipeadata Dese_Pnad)"
    ind["industria"]["fonte"] = "IBGE — PIM-PF, indústria geral (SIDRA 8888)"
    ind["abate_bovinos"]["fonte"] = "IBGE — Pesquisa Trimestral do Abate de Animais (SIDRA 1092)"
    ind["analfabetismo"]["fonte"] = "IBGE — PNAD Contínua (SIDRA 7113) e Censos 2000, 2010 e 2022 (Atlas do Desenvolvimento Humano)"
    ind["desemprego_negros"]["fonte"] = "IBGE — PNAD Contínua trimestral por cor ou raça (SIDRA 6402)"
    ind["safra"]["fonte"] = "CONAB — séries históricas de grãos"
    ind["homicidios"]["fonte"] = "Ipea/FBSP — Atlas da Violência, com dados do SIM/Ministério da Saúde"
    ind["desemprego"]["url_extra"] = ipea_url("Dese_Pnad")
    ind["desemprego"]["outra_metodologia"] = [a for a in ind["desemprego"]["anual"] if a < 2013]
    for k in ind:
        ind[k]["abas"] = ABAS.get(k, ind[k].get("abas", []))


    payload = {
        "atualizado_em": time.strftime("%Y-%m-%d"),
        "governos": [{"nome": n, "inicio": i, "fim": (f if f != "2099-12" else None)} for n, i, f in GOVERNOS],
        "nota_governos": "Dilma foi afastada em 12/05/2016. Nos dados mensais, Temer começa em maio/2016; nos anuais, 2016 conta para Temer (8 de 12 meses), "
                         "então Dilma 2 fica só com 2015. Lula 3 está em curso e usa os dados disponíveis.",
        "indicadores": {k: {**v, "mandato": {g: x for g, x in v["mandato"].items() if x is not None}, "anual": {str(a): x for a, x in v["anual"].items()},
                            **({"anual_pnad_original": {str(a): x for a, x in v["anual_pnad_original"].items()},
                                "anual_pnadc": {str(a): x for a, x in v["anual_pnadc"].items()}} if "anual_pnadc" in v else {})}
                        for k, v in ind.items()},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("gravado:", OUT)
    import alinhar_com_versao_padrao  # iguala Bolsonaro e Lula 3 aos números da versão padrão de cada aba
    alinhar_com_versao_padrao.main()
    for k, v in ind.items():
        print(k, v["mandato"])


if __name__ == "__main__":
    main()
