"""
Séries longas extras para comparar todos os governos (FHC 1 a Lula 3) nas abas temáticas.
Grava data/historico_extra.json, que o painel junta a historico.json.

Dois tipos de dado:
- "indicadores": mesmo formato de historico.json (anual + valor por mandato), um gráfico por indicador;
- "categorias": um valor por categoria e por governo (ex.: quanto o arroz subiu em cada mandato), mostrado em barras agrupadas.

Fontes: IBGE/SIDRA (IPCA por item e grupo, PAM, PPM, PEVS), Ipeadata (Dieese, Conab, PIM-PF), ComexStat (MDIC) e Our World in Data.
Execute:  python data/_fontes/coletar_historico_extra.py
"""
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coletar_historico import (GOVERNOS, ANO_GOV, por_mandato_anual, media, variacao_real_anualizada, ipea, sgs, ipea_url,  # noqa: E402
                               sgs_url, deflacionar_mensal, SIDRA_TAB)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "historico_extra.json")
NOMES = [g[0] for g in GOVERNOS]


def baixar(url, tentativas=4):
    for i in range(tentativas):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}), timeout=240).read()
            return gzip.decompress(r) if r[:2] == b"\x1f\x8b" else r
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(6)


def jget(url):
    return json.loads(baixar(url))


def categorias_sidra(tabela, classif):
    m = jget(f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/metadados")
    return {c["nome"]: c["id"] for c in next(x for x in m["classificacoes"] if x["id"] == classif)["categorias"]}


def sidra(tabela, variavel, classif, codigos, periodo="all"):
    """Devolve {codigo_categoria: {periodo: valor}}; períodos 'AAAA' (anual) ou 'AAAAMM' (mensal)."""
    url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/n1/all/v/{variavel}/p/{periodo}/c{classif}/{','.join(str(c) for c in codigos)}"
    linhas = jget(url)
    cab = linhas[0]
    dims = {k: v for k, v in cab.items() if k.startswith("D") and k.endswith("C")}
    k_per = next(k for k, v in dims.items() if v.startswith(("Ano", "Mês")))
    k_cat = next(k for k, v in dims.items() if k != k_per and not v.startswith(("Brasil", "Variável")))
    out = {}
    for ln in linhas[1:]:
        try:
            v = float(ln["V"])
        except ValueError:
            continue
        out.setdefault(int(ln[k_cat]), {})[ln[k_per]] = v
    return out


# ---------------------------------------------------------------- deflator anual (IPCA médio do ano, R$ de 2025)
IPCA_M = sgs(433, "01/01/1994")


def deflator_anual():
    idx, v, por_ano = {}, 1.0, {}
    for ym, x in IPCA_M:
        v *= 1 + x / 100
        por_ano.setdefault(int(ym[:4]), []).append(v)
    medio = {a: sum(l) / len(l) for a, l in por_ano.items()}
    return {a: medio[2025] / m for a, m in medio.items()}


DEF = deflator_anual()


def ind(nome, unidade, maior_melhor, anual, mandato, metodo, fonte, url, nota, abas, comparabilidade="ok", **extra):
    return {"nome": nome, "unidade": unidade, "maior_melhor": maior_melhor, "eixo": "Economia", "anual": {str(a): v for a, v in sorted(anual.items())},
            "mandato": {g: x for g, x in mandato.items() if x is not None}, "metodo": metodo, "comparabilidade": comparabilidade,
            "fonte": fonte, "url": url, "nota": nota, "abas": abas, **extra}


def media_mandato(serie, desde=1995):
    return por_mandato_anual({a: v for a, v in serie.items() if a >= desde}, media)


# ---------------------------------------------------------------- IPCA por item e por grupo, acumulado em cada mandato
# (nome, código na tabela 58 [1991–jul/1999], códigos nas tabelas 655, 2938, 1419 e 7060 [ago/1999 em diante])
TAB_IPCA = [(58, 72, "199101", "199907"), (655, 315, "199908", "200606"), (2938, 315, "200607", "201112"), (1419, 315, "201201", "201912"), (7060, 315, "202001", "209912")]
ITENS = [
    ("Alimentação no domicílio", {58: 1327, "novo": 7171}),
    ("Arroz", {58: 1457, "novo": 7173}),
    ("Feijão-carioca", {2938: 7180, 1419: 12222, 7060: 12222}),
    ("Carnes", {58: 1375, "novo": 7283}),
    ("Leite (pasteurizado; longa vida desde 2012)", {58: 1795, 655: 7357, 2938: 7357, 1419: 12393, 7060: 12393}),
    ("Café moído", {58: 1853, "novo": 7392}),
    ("Óleo de soja", {58: 1843, "novo": 7385}),
    ("Pão francês", {58: 1827, "novo": 7375}),
    ("Ovo de galinha", {58: 1791, "novo": 7355}),
    ("Tomate", {58: 1529, "novo": 7212}),
    ("Batata-inglesa", {58: 1509, "novo": 7202}),
    ("Açúcar refinado", {58: 1545, "novo": 7220}),
    ("Energia elétrica residencial", {"novo": 7485}),
    ("Gás de botijão", {"novo": 7482}),
    ("Gasolina", {58: 2247, "novo": 7657}),
    ("Aluguel residencial", {58: 1935, "novo": 7448}),
    ("Ônibus urbano", {58: 2199, "novo": 7628}),
    ("Remédios (produtos farmacêuticos)", {58: 1437, "novo": 7662}),
    ("Plano de saúde", {"novo": 7696}),
]
GRUPOS = [
    ("Índice geral", {58: 2640, "novo": 7169}), ("Alimentação e bebidas", {58: 1313, "novo": 7170}), ("Habitação", {58: 1397, "novo": 7445}),
    ("Artigos de residência", {58: 1317, "novo": 7486}), ("Vestuário", {58: 1319, "novo": 7558}), ("Transportes", {"novo": 7625}),
    ("Saúde e cuidados pessoais", {58: 1323, "novo": 7660}), ("Despesas pessoais", {58: 1325, "novo": 7712}),
    ("Educação", {"novo": 7766}), ("Comunicação", {"novo": 7786}),
]
ALIMENTOS = {"Alimentação no domicílio", "Arroz", "Feijão-carioca", "Carnes", "Leite (pasteurizado; longa vida desde 2012)", "Café moído", "Óleo de soja",
             "Pão francês", "Ovo de galinha", "Tomate", "Batata-inglesa", "Açúcar refinado"}


def codigo(mapa, tabela):
    if tabela in mapa:
        return mapa[tabela]
    return mapa.get("novo") if tabela != 58 else None


def serie_ipca(lista):
    """{nome: {AAAA-MM: variação mensal}} juntando as cinco tabelas."""
    out = {n: {} for n, _ in lista}
    for tab, cl, *_ in TAB_IPCA:
        cods = {n: codigo(m, tab) for n, m in lista}
        validos = sorted({c for c in cods.values() if c})
        dados = sidra(tab, 63, cl, validos)
        for n, c in cods.items():
            for per, v in dados.get(c, {}).items():
                out[n][f"{per[:4]}-{per[4:]}"] = v
        time.sleep(1)
    return out


def acumulado_por_mandato(serie, ultimo):
    acum, ano, parcial = {}, {}, {}
    for nome, ini, fim in GOVERNOS:
        fim = min(fim, ultimo)
        meses, a, m = [], int(ini[:4]), int(ini[5:])
        while f"{a}-{m:02d}" <= fim:
            meses.append(f"{a}-{m:02d}")
            a, m = (a + 1, 1) if m == 12 else (a, m + 1)
        com = [serie[x] for x in meses if x in serie]
        if not meses or len(com) < 0.85 * len(meses):
            continue
        p = 1.0
        for v in com:
            p *= 1 + v / 100
        acum[nome] = round((p - 1) * 100, 1)
        ano[nome] = round((p ** (12 / len(com)) - 1) * 100, 1)
        if len(com) < len(meses):
            parcial[nome] = f"{len(com)} de {len(meses)} meses"
    return acum, ano, parcial


def bloco_ipca(lista, nome, nota):
    s = serie_ipca(lista)
    ultimo = max(max(v) for v in s.values() if v)
    cats, cats_ano, parc = {}, {}, {}
    for n, serie in s.items():
        a, b, p = acumulado_por_mandato(serie, ultimo)
        cats[n], cats_ano[n] = a, b
        if p:
            parc[n] = p
    return {"nome": nome, "unidade": "%", "maior_melhor": False, "categorias": cats, "categorias_ao_ano": cats_ano, "parcial": parc,
            "metodo": f"Variação acumulada no mandato, encadeando as variações mensais do IPCA (último mês: {ultimo}). Também dá para ver a média ao ano, que corrige mandatos de tamanhos diferentes.",
            "fonte": "IBGE — IPCA por grupos, itens e subitens (SIDRA 58, 655, 2938, 1419 e 7060)", "url": SIDRA_TAB + "7060", "nota": nota}


# ---------------------------------------------------------------- PAM, PPM e PEVS (IBGE)
def anual_sidra(tabela, variavel, classif, nomes):
    cats = categorias_sidra(tabela, classif)
    ids = {n: next((i for k, i in cats.items() if k.lower().startswith(n.lower())), None) for n in nomes}
    dados = sidra(tabela, variavel, classif, [i for i in ids.values() if i is not None])
    return {n: {int(p): v for p, v in dados.get(i, {}).items()} for n, i in ids.items() if i is not None}


def categorias_media(series, escala, desde=1995):
    out = {}
    for n, s in series.items():
        out[n] = {g: round(v / escala, 2) for g, v in media_mandato(s, desde).items()}
    return out


def main():
    I, C = {}, {}

    # IPCA: itens e grupos
    C["ipca_itens"] = bloco_ipca(ITENS, "Quanto cada item subiu em cada mandato (IPCA oficial)",
                                  "Energia elétrica, gás de botijão e plano de saúde só aparecem no IPCA a partir de ago/1999, e o feijão-carioca a partir de jul/2006: "
                                  "antes disso o painel mostra Sem dado. O leite era o pasteurizado até 2011 e passou a ser o longa vida em 2012 (mesmo subitem).")
    C["ipca_itens"]["abas"] = ["cesta-basica", "inflacao"]
    C["ipca_itens"]["grupos_de_itens"] = {"Alimentos": sorted(ALIMENTOS), "Energia, moradia e transporte": ["Energia elétrica residencial", "Gás de botijão", "Gasolina", "Aluguel residencial", "Ônibus urbano"],
                                          "Saúde": ["Remédios (produtos farmacêuticos)", "Plano de saúde"]}
    print("ipca_itens ok")
    C["ipca_grupos"] = bloco_ipca(GRUPOS, "Decomposição Setorial do IPCA (Grupos de Consumo)",
                                   "Até jul/1999 o IPCA tinha 7 grupos (transportes e comunicação juntos, educação dentro de despesas pessoais): por isso Transportes, Educação e Comunicação "
                                   "ficam Sem dado no FHC 1, e Despesas pessoais no FHC 1 inclui educação.")
    C["ipca_grupos"]["abas"] = ["inflacao"]
    print("ipca_grupos ok")

    # Cesta básica (Dieese, São Paulo): custo real e horas de trabalho
    cesta = [p for p in ipea("DIEESE12_CBSP12") if p[0] >= "1994-07"]
    cesta_real = deflacionar_mensal(cesta, IPCA_M)
    ano_real = {}
    for ym, v in cesta_real:
        ano_real.setdefault(int(ym[:4]), []).append(v)
    ano_real = {a: round(sum(l) / len(l), 0) for a, l in ano_real.items() if a >= 1995}
    I["cesta_real"] = ind("Custo da cesta básica em São Paulo (R$ de hoje, média)", "R$ de hoje", False, ano_real, media_mandato(ano_real),
                          "Média do custo mensal da cesta básica do Dieese em São Paulo, corrigido pelo IPCA até o último mês disponível.",
                          "Dieese — Pesquisa Nacional da Cesta Básica, São Paulo (via Ipeadata DIEESE12_CBSP12)", ipea_url("DIEESE12_CBSP12"),
                          "A cesta do Dieese segue a lista de 1938 (Decreto-Lei 399) e mudou de metodologia em jan/2016. É a cidade de São Paulo, não o país inteiro.",
                          ["cesta-basica"], "ajustado")
    salmin = dict(ipea("MTE12_SALMIN12"))
    horas = {}
    for ym, v in cesta:
        if ym in salmin and salmin[ym]:
            horas.setdefault(int(ym[:4]), []).append(v / (salmin[ym] / 220))
    horas = {a: round(sum(l) / len(l), 0) for a, l in horas.items() if a >= 1995}
    I["cesta_horas"] = ind("Horas de trabalho para comprar a cesta (salário mínimo, média)", "horas", False, horas, media_mandato(horas),
                           "Custo da cesta em São Paulo dividido pelo valor da hora de quem ganha um salário mínimo (jornada de 220 horas por mês), como faz o Dieese.",
                           "Dieese (cesta, via Ipeadata DIEESE12_CBSP12) e salário mínimo nominal (Ipeadata MTE12_SALMIN12)", ipea_url("DIEESE12_CBSP12"),
                           "Quanto menos horas, maior o poder de compra do salário mínimo para alimentos básicos. Conta do painel com a mesma regra do Dieese.",
                           ["cesta-basica"], "ajustado", url_extra=ipea_url("MTE12_SALMIN12"))
    print("cesta ok")

    # Conab: área plantada e produtividade de grãos
    area = {a: v / 1000 for a, v in {int(ym[:4]): v for ym, v in ipea("DEPAE_SAFRAAREA")}.items()}
    saf = {int(ym[:4]): v / 1000 for ym, v in ipea("DEPAE_SAFRA")}
    I["area_graos"] = ind("Área plantada de grãos (média anual)", "milhões de ha", True, {a: round(v, 1) for a, v in area.items()},
                          media_mandato({a: round(v, 1) for a, v in area.items()}),
                          "Média da área plantada de grãos em cada mandato (safra atribuída ao ano em que termina).",
                          "Conab — séries históricas de grãos (via Ipeadata DEPAE_SAFRAAREA)", ipea_url("DEPAE_SAFRAAREA"),
                          "Área maior significa mais produção, mas também pode significar abertura de novas terras; por isso o painel não aponta um lado melhor.",
                          ["agro"], sem_lado_melhor=True)
    prod = {a: round(saf[a] / area[a], 2) for a in area if a in saf and area[a]}
    I["produtividade_graos"] = ind("Produtividade dos grãos (média)", "t por hectare", True, prod, media_mandato(prod),
                                   "Produção de grãos dividida pela área plantada, média de cada mandato.",
                                   "Conab — séries históricas de grãos (via Ipeadata DEPAE_SAFRA e DEPAE_SAFRAAREA)", ipea_url("DEPAE_SAFRA"),
                                   "A produtividade sobe com tecnologia ao longo de décadas, então mandatos recentes tendem a ter números maiores. O clima pesa muito em cada safra.",
                                   ["agro"], "ajustado")
    print("conab ok")

    # PAM: produção por lavoura (IBGE)
    lavouras = ["Soja (em grão)", "Milho (em grão)", "Cana-de-açúcar", "Arroz (em casca)", "Feijão (em grão)", "Trigo (em grão)", "Café (em grão) Total",
                "Algodão herbáceo (em caroço)", "Mandioca", "Laranja"]
    pam_q = anual_sidra(5457, 214, 782, lavouras)
    C["pam_lavouras"] = {"nome": "PAM: produção das principais lavouras (média anual)", "unidade": "milhões de t", "maior_melhor": True,
                         "categorias": categorias_media(pam_q, 1e6), "parcial": {},
                         "metodo": "Média anual da quantidade produzida de cada lavoura em cada mandato (toneladas convertidas em milhões).",
                         "fonte": "IBGE — Produção Agrícola Municipal (SIDRA 5457)", "url": SIDRA_TAB + "5457",
                         "nota": "A PAM sai com cerca de um ano de atraso: o ano mais recente pode ainda não estar publicado. Produção depende muito do clima e do preço internacional.",
                         "abas": ["agro"]}
    pam_tot = anual_sidra(5457, 8331, 782, ["Total"]).get("Total", {})
    pam_area = {a: round(v / 1e6, 1) for a, v in pam_tot.items() if a >= 1994}
    I["pam_area"] = ind("PAM: área plantada de todas as lavouras (média anual)", "milhões de ha", True, pam_area, media_mandato(pam_area),
                        "Média da área plantada ou destinada à colheita, lavouras temporárias e permanentes.", "IBGE — Produção Agrícola Municipal (SIDRA 5457)",
                        SIDRA_TAB + "5457", "Área maior não é, por si só, melhor ou pior: pode vir de produtividade ou de abertura de terras.", ["agro"], sem_lado_melhor=True)
    pam_val = anual_sidra(5457, 215, 782, ["Total"]).get("Total", {})
    pam_val = {a: round(v * DEF.get(a, 1) / 1e6, 1) for a, v in pam_val.items() if a >= 1995 and a in DEF}
    I["pam_valor"] = ind("PAM: valor da produção agrícola (R$ bi de 2025, média anual)", "R$ bi de 2025", True, pam_val, media_mandato(pam_val),
                         "Valor da produção das lavouras, corrigido pelo IPCA médio de cada ano para reais de 2025.", "IBGE — Produção Agrícola Municipal (SIDRA 5457)",
                         SIDRA_TAB + "5457", "O valor sobe e desce com o preço das commodities em dólar, não só com a quantidade produzida.", ["agro"], "ajustado")
    print("pam ok")

    # PPM: rebanhos e produção de origem animal
    reb = anual_sidra(3939, 105, 79, ["Bovino", "Suíno - total", "Galináceos - total", "Ovino", "Caprino", "Bubalino"])
    C["ppm_rebanhos"] = {"nome": "Efetivo dos Rebanhos Brasileiros (média anual)", "unidade": "milhões de cabeças", "maior_melhor": None,
                         "categorias": categorias_media(reb, 1e6), "parcial": {},
                         "metodo": "Média anual do número de animais em 31/12 de cada ano, por tipo de rebanho.", "fonte": "IBGE — Pesquisa da Pecuária Municipal (SIDRA 3939)",
                         "url": SIDRA_TAB + "3939", "nota": "Rebanho maior não é necessariamente melhor: depende de preço, exportação e ciclo do gado.", "abas": ["pecuaria"]}
    bov = {a: round(v / 1e6, 1) for a, v in reb.get("Bovino", {}).items() if a >= 1994}
    I["rebanho_bovino"] = ind("Rebanho bovino (média anual)", "milhões de cabeças", True, bov, media_mandato(bov),
                              "Média do efetivo bovino em 31/12 de cada ano.", "IBGE — Pesquisa da Pecuária Municipal (SIDRA 3939)", SIDRA_TAB + "3939",
                              "O tamanho do rebanho segue o ciclo do gado e o preço da arroba; não há lado melhor absoluto.", ["pecuaria"], sem_lado_melhor=True)
    oa = anual_sidra(74, 106, 80, ["Leite", "Ovos de galinha", "Mel de abelha"])
    leite = {a: round(v / 1e6, 1) for a, v in oa.get("Leite", {}).items() if a >= 1994}
    ovos = {a: round(v / 1e6, 2) for a, v in oa.get("Ovos de galinha", {}).items() if a >= 1994}
    mel = {a: round(v / 1e6, 1) for a, v in oa.get("Mel de abelha", {}).items() if a >= 1994}  # kg -> mil toneladas
    I["leite"] = ind("Produção de leite (média anual)", "bilhões de litros", True, leite, media_mandato(leite), "Média anual da produção de leite.",
                     "IBGE — Pesquisa da Pecuária Municipal (SIDRA 74)", SIDRA_TAB + "74", "Produção de leite inspecionado e não inspecionado declarada na PPM.", ["pecuaria"])
    I["ovos"] = ind("Produção de ovos de galinha (média anual)", "bilhões de dúzias", True, ovos, media_mandato(ovos), "Média anual da produção de ovos de galinha.",
                    "IBGE — Pesquisa da Pecuária Municipal (SIDRA 74)", SIDRA_TAB + "74", "Inclui granjas e criação em pequenas propriedades.", ["pecuaria"])
    I["mel"] = ind("Produção de mel (média anual)", "mil toneladas", True, mel, media_mandato(mel), "Média anual da produção de mel de abelha.",
                   "IBGE — Pesquisa da Pecuária Municipal (SIDRA 74)", SIDRA_TAB + "74", "Produção sensível a clima e a uso de agrotóxicos.", ["pecuaria"])
    print("ppm ok")

    # PEVS: silvicultura e extração vegetal (valor real)
    for chave, tab, var, cl, nome, aba_nota in (
        ("silvicultura_valor", 291, 143, 194, "Valor da Produção da Silvicultura (R$ milhões de 2025, média anual)", "Florestas plantadas: madeira em tora, carvão, lenha, celulose."),
        ("extracao_valor", 289, 145, 193, "Valor da Produção na Extração Vegetal Nativa (R$ milhões de 2025, média anual)", "Produtos de florestas nativas: açaí, erva-mate, castanha, madeira nativa, babaçu."),
    ):
        tot = anual_sidra(tab, var, cl, ["Total"]).get("Total", {})
        serie = {a: round(v * DEF[a] / 1e3, 0) for a, v in tot.items() if a >= 1995 and a in DEF}
        I[chave] = ind(nome, "R$ milhões de 2025", True, serie, media_mandato(serie),
                       "Valor da produção (mil reais) corrigido pelo IPCA médio de cada ano para reais de 2025, média de cada mandato.",
                       f"IBGE — Produção da Extração Vegetal e da Silvicultura (SIDRA {tab})", SIDRA_TAB + str(tab), aba_nota + " O valor acompanha preços de mercado.",
                       ["silvicultura"], "ajustado")
    print("pevs ok")

    # PIM-PF: extrativa x transformação (a série atual começa em 2002)
    for chave, cod, nome in (("pim_extrativa", "PIMPFN12_QIEMNN12", "Indústria extrativa (crescimento ao ano)"),
                             ("pim_transformacao", "PIMPFN12_QIITNN12", "Indústria de transformação (crescimento ao ano)")):
        s = {}
        for ym, v in ipea(cod):
            s.setdefault(int(ym[:4]), []).append(v)
        s = {a: round(sum(l) / len(l), 2) for a, l in s.items() if len(l) == 12}
        I[chave] = ind(nome, "% ao ano", True, s, por_mandato_anual(s, variacao_real_anualizada(s)),
                       "Variação anualizada da média anual do índice de produção física (2022 = 100) entre o fim do mandato anterior e o fim do mandato.",
                       "IBGE — PIM-PF por seções (SIDRA 8888, via Ipeadata " + cod + ")", SIDRA_TAB + "8888",
                       "A série atual começa em 2002: FHC 1 e FHC 2 ficam sem dado de mandato. A extrativa depende muito de petróleo e minério.",
                       ["industria"], "ressalva", url_extra=ipea_url(cod))
    print("pim ok")

    # Emissões de gases de efeito estufa (inclui mudança no uso da terra)
    linhas = list(csv.DictReader(io.StringIO(baixar("https://ourworldindata.org/grapher/total-ghg-emissions.csv?useColumnShortNames=true").decode("utf-8"))))
    col = [k for k in linhas[0] if k not in ("entity", "code", "year", "Entity", "Code", "Year")][0]
    em = {int(r.get("year") or r.get("Year")): round(float(r[col]) / 1e6, 0) for r in linhas if (r.get("code") or r.get("Code")) == "BRA" and r[col]}
    em = {a: v for a, v in em.items() if a >= 1994}
    I["emissoes"] = ind("Emissões de gases de efeito estufa (média anual)", "milhões de t de CO₂e", False, em, media_mandato(em),
                        "Média anual das emissões totais (gás carbônico, metano e óxido nitroso), incluindo desmatamento e mudança no uso da terra.",
                        "Jones et al. (2025), via Our World in Data", "https://ourworldindata.org/grapher/total-ghg-emissions?country=~BRA",
                        "Estimativa científica internacional, não o inventário oficial do governo. O desmatamento é a maior parte das emissões do Brasil e varia muito de um ano para outro.",
                        ["meio-ambiente"], "ajustado")
    print("emissoes ok")

    # ComexStat: destinos e pauta por mandato (dados desde 1997)
    try:
        import coletar_comexstat as cx
        destinos, pauta, cob = {}, {}, {}
        for nome, ini, fim in GOVERNOS:
            de, ate = max(ini, "1997-01"), min(fim, "2025-12")
            if de > ate:
                continue
            if de != ini:
                cob[nome] = f"só {de[:4]}–{ate[:4]} (ComexStat começa em 1997)"
            for alvo, det, rot in ((destinos, "country", "country"), (pauta, "section", "section")):
                lista = cx.consulta("export", de, ate, [det])
                tot = sum(float(x["metricFOB"]) for x in lista)
                for x in lista:
                    rotulo = x[rot].split(";")[0].strip()
                    rotulo = rotulo if len(rotulo) <= 55 else rotulo[:52].rsplit(" ", 1)[0] + "…"
                    alvo.setdefault(rotulo, {})[nome] = round(alvo.get(rotulo, {}).get(nome, 0) + 100 * float(x["metricFOB"]) / tot, 1)
        def top(d, n):
            ordem = sorted(d, key=lambda k: -max(d[k].values()))[:n]
            return {k: d[k] for k in ordem}
        base = {"unidade": "% das exportações", "maior_melhor": None, "parcial": {k: {g: v for g, v in cob.items()} for k in []},
                "fonte": "MDIC/Secex — ComexStat (valores FOB em US$, API pública)", "url": "https://comexstat.mdic.gov.br/pt/home", "abas": ["comercio-exterior"]}
        C["comex_destinos"] = {**base, "nome": "Para onde o Brasil exporta (participação em cada mandato)", "categorias": top(destinos, 10),
                               "metodo": "Participação de cada país no valor exportado no período do mandato (soma dos anos).",
                               "nota": "Lula 3 usa 2023–2025 (anos fechados). " + " ".join(f"{g}: {t}." for g, t in cob.items())}
        C["comex_pauta"] = {**base, "nome": "O que o Brasil exporta (seções do Sistema Harmonizado)", "categorias": top(pauta, 9),
                            "metodo": "Participação de cada seção do Sistema Harmonizado no valor exportado no período do mandato.",
                            "nota": "Lula 3 usa 2023–2025 (anos fechados). " + " ".join(f"{g}: {t}." for g, t in cob.items())}
        print("comex ok")
    except Exception as e:  # a API do ComexStat tem limite de acessos; sem ela as seções mostram Sem dado
        print("comex falhou:", e)

    payload = {"atualizado_em": time.strftime("%Y-%m-%d"), "indicadores": I, "categorias": C}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("gravado:", OUT)
    for k, v in I.items():
        print(k, v["mandato"])
    for k, v in C.items():
        print(k, {c: len(g) for c, g in list(v["categorias"].items())[:4]})


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
