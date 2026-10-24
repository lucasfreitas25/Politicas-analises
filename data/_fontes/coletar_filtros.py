"""
Séries por ano de cada tipo de rebanho, produto de origem animal, lavoura e produto da silvicultura e do extrativismo (IBGE/SIDRA),
para o filtro "escolha o tipo" das abas comparadas (qualquer par de governos desde FHC).
Grava em data/historico_extra.json, na chave "filtros", sem refazer o resto. Execute:  python data/_fontes/coletar_filtros.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coletar_historico_extra as ex  # noqa: E402
from coletar_historico import por_mandato_anual, media  # noqa: E402

ARQ = ex.OUT
SIDRA = ex.SIDRA_TAB


def sidra_u(tabela, variavel, classif, codigos):
    """{codigo: {ano: valor}} e {codigo: unidade}, para anos de 1995 em diante."""
    url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/n1/all/v/{variavel}/p/all/c{classif}/{','.join(str(c) for c in codigos)}"
    linhas = ex.jget(url)
    cab = linhas[0]
    dims = {k: v for k, v in cab.items() if k.startswith("D") and k.endswith("C")}
    k_per = next(k for k, v in dims.items() if v.startswith(("Ano", "Mês")))
    k_cat = next(k for k, v in dims.items() if k != k_per and not v.startswith(("Brasil", "Variável")))
    dados, unidade = {}, {}
    for ln in linhas[1:]:
        try:
            v = float(ln["V"])
        except ValueError:
            continue
        c = int(ln[k_cat])
        ano = int(ln[k_per])
        if ano >= 1995:
            dados.setdefault(c, {})[ano] = v
            unidade[c] = ln["MN"]
    return dados, unidade


def escalona(anual, unidade):
    """Números muito grandes (237.028.554 cabeças) viram 'milhões de cabeças' etc. para ler melhor; unidades compostas e valores em R$ ficam como estão."""
    if not anual or unidade.startswith("R$") or " por " in unidade:
        return anual, unidade
    m = max(abs(v) for v in anual.values())
    for div, rot in ((1e9, "bilhões de"), (1e6, "milhões de"), (1e4, "mil")):
        if m >= div:
            return {a: v / div for a, v in anual.items()}, f"{rot} {unidade}"
    return anual, unidade


def bloco(nome, rotulo_item, itens, variaveis, fonte, url, metodo, nota, abas):
    """itens: {nome: {variavel: {"unidade":..., "anual": {ano: v}}}}; calcula a média de cada mandato para saber o que dá para comparar."""
    saida = {}
    for item, vars_ in itens.items():
        saida[item] = {}
        for var, d in vars_.items():
            anual, unidade = escalona({a: v for a, v in sorted(d["anual"].items())}, d["unidade"])
            anual = {a: round(v, 3) for a, v in anual.items()}
            if len(anual) < 3:
                continue
            saida[item][var] = {"unidade": unidade, "anual": {str(a): v for a, v in anual.items()},
                                "mandato": {g: x for g, x in por_mandato_anual(anual, media).items() if x is not None}}
        if not saida[item]:
            del saida[item]
    return {"nome": nome, "rotulo_item": rotulo_item, "variaveis": variaveis, "itens": saida, "fonte": fonte, "url": url,
            "metodo": metodo, "nota": nota, "abas": abas}


def deflaciona(serie, escala):
    """Valor nominal (mil R$) para R$ milhões de 2025 pelo IPCA médio de cada ano."""
    return {a: v * ex.DEF[a] / escala for a, v in serie.items() if a in ex.DEF}


def coletar():
    F = {}

    # ---------------------------------------------------------------- PPM: tipos de rebanho
    cats = ex.categorias_sidra(3939, 79)
    ids = {n: i for n, i in cats.items()}
    dados, un = sidra_u(3939, 105, 79, list(ids.values()))
    itens = {n.replace(" - ", ": "): {"Efetivo (cabeças)": {"unidade": "cabeças", "anual": dados.get(i, {})}} for n, i in ids.items()}
    F["ppm_rebanhos"] = bloco(
        "Efetivo dos rebanhos por tipo", "Tipo de rebanho", itens, ["Efetivo (cabeças)"], "IBGE — Pesquisa da Pecuária Municipal (SIDRA 3939)", SIDRA + "3939",
        "Número de animais em 31/12 de cada ano; o painel mostra o ano a ano colorido pelo partido do governo e a média de cada mandato.",
        "Rebanho maior não é, por si só, melhor ou pior: depende de preço, exportação e ciclo do gado. Os anos de 1995 e 1996 vêm do Censo Agropecuário, por isso alguns tipos mudam de patamar entre os dois anos.", ["pecuaria"])
    print("ppm_rebanhos", len(F["ppm_rebanhos"]["itens"]))

    # ---------------------------------------------------------------- PPM: produtos de origem animal
    cats = ex.categorias_sidra(74, 80)
    ids = {n: i for n, i in cats.items() if i != 0}
    d_q, u_q = sidra_u(74, 106, 80, list(ids.values()))
    d_v, _ = sidra_u(74, 215, 80, list(ids.values()))
    itens = {}
    for n, i in ids.items():
        itens[n] = {"Quantidade produzida": {"unidade": u_q.get(i, "unidades").lower(), "anual": d_q.get(i, {})},
                    "Valor da produção (R$ milhões de 2025)": {"unidade": "R$ milhões de 2025", "anual": deflaciona(d_v.get(i, {}), 1e3)}}
    F["ppm_origem"] = bloco(
        "Produção de origem animal", "Produto", itens, ["Quantidade produzida", "Valor da produção (R$ milhões de 2025)"], "IBGE — Pesquisa da Pecuária Municipal (SIDRA 74)", SIDRA + "74",
        "Quantidade anual e valor da produção (corrigido pelo IPCA médio de cada ano para reais de 2025).",
        "A produção de leite, ovos e mel responde a clima, custo de ração e preço; o painel não aponta um lado melhor.", ["pecuaria"])
    print("ppm_origem", len(F["ppm_origem"]["itens"]))

    # ---------------------------------------------------------------- PAM: lavouras
    cats = ex.categorias_sidra(5457, 782)
    ids = {n.rstrip("*"): i for n, i in cats.items() if i != 0}
    variaveis = {"Quantidade produzida": 214, "Área plantada": 8331, "Rendimento médio": 112, "Valor da produção (R$ milhões de 2025)": 215}
    por_var, unid = {}, {}
    for var, cod in variaveis.items():
        por_var[var], unid[var] = sidra_u(5457, cod, 782, list(ids.values()))
        time.sleep(1)
    itens = {}
    for n, i in ids.items():
        itens[n] = {}
        for var in variaveis:
            serie = por_var[var].get(i, {})
            if var.startswith("Valor"):
                itens[n][var] = {"unidade": "R$ milhões de 2025", "anual": deflaciona(serie, 1e3)}
            else:
                itens[n][var] = {"unidade": unid[var].get(i, "").lower(), "anual": serie}
    F["pam_lavouras"] = bloco(
        "Produção agrícola por lavoura", "Lavoura", itens, list(variaveis), "IBGE — Produção Agrícola Municipal (SIDRA 5457)", SIDRA + "5457",
        "Valores anuais de cada lavoura (temporárias e permanentes); o valor da produção é corrigido pelo IPCA médio de cada ano para reais de 2025.",
        "A PAM sai com cerca de um ano de atraso, e a produção depende muito do clima e do preço internacional; o painel não aponta um lado melhor.", ["agro"])
    print("pam_lavouras", len(F["pam_lavouras"]["itens"]))

    # ---------------------------------------------------------------- PEVS: silvicultura e extração vegetal
    for chave, tab, v_q, v_v, cl, nome, rot, pref_ok in (
        ("pevs_silvicultura", 291, 142, 143, 194, "Silvicultura por produto", "Produto da silvicultura", ("1.1 ", "1.2 ", "1.3 ", "1.3.1 ", "1.3.2 ", "2")),
        ("pevs_extracao", 289, 144, 145, 193, "Extração vegetal nativa por produto", "Produto extrativo", ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")),
    ):
        cats = ex.categorias_sidra(tab, cl)
        ids = {n: i for n, i in cats.items() if (i == 0 or any(n.startswith(p) for p in pref_ok)) and n.count(".") <= 2}
        d_q, u_q = sidra_u(tab, v_q, cl, list(ids.values()))
        d_v, _ = sidra_u(tab, v_v, cl, list(ids.values()))
        itens = {}
        for n, i in ids.items():
            itens[("Total" if i == 0 else n.split(" - ", 1)[-1])] = {
                "Quantidade produzida": {"unidade": u_q.get(i, "").lower(), "anual": d_q.get(i, {})},
                "Valor da produção (R$ milhões de 2025)": {"unidade": "R$ milhões de 2025", "anual": deflaciona(d_v.get(i, {}), 1e3)}}
        F[chave] = bloco(
            nome, rot, itens, ["Quantidade produzida", "Valor da produção (R$ milhões de 2025)"], f"IBGE — Produção da Extração Vegetal e da Silvicultura (SIDRA {tab})", SIDRA + str(tab),
            "Quantidade anual e valor da produção, corrigido pelo IPCA médio de cada ano para reais de 2025.",
            "O valor acompanha preços de mercado; o painel não aponta um lado melhor.", ["silvicultura"])
        print(chave, len(F[chave]["itens"]))
    return F


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    pay = json.load(open(ARQ, encoding="utf-8"))
    pay["filtros"] = coletar()
    json.dump(pay, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("gravado em", ARQ)
