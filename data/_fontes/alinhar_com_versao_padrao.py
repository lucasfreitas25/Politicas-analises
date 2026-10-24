"""
Faz as séries longas (historico.json) usadas nas versões comparadas darem o MESMO número que a versão padrão (macro.json, pnadc.json, conab.json,
comexstat.json) para os anos e governos que as duas telas mostram (2019 em diante). Antes, a mesma série vinha de fontes ou recortes diferentes:
PIB (média geométrica x simples), Selic e dólar (série efetiva x meta/PTAX), desemprego e Caged de Lula 3 (anos fechados x meses de 2026),
safra (vintage do Ipeadata x CONAB) e comércio exterior (balanço de pagamentos do BC x MDIC).

Regra: da primeira data da versão padrão em diante usa-se o dado dela; antes disso, a série longa original, com o aviso de metodologia.

Uso: roda sozinho (python data/_fontes/alinhar_com_versao_padrao.py) sobre data/historico.json e é chamado ao final de coletar_historico.py.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOVS_NOVOS = {"Bolsonaro": (2019, 2022), "Lula 3": (2023, 2030)}


def _carrega(nome):
    return json.load(open(os.path.join(RAIZ, nome), encoding="utf-8"))


def _media(valores):
    return round(sum(valores) / len(valores), 2) if valores else None


def _por_governo(anual, anos_gov=GOVS_NOVOS):
    return {g: [v for a, v in anual.items() if ini <= int(a) <= fim and v is not None] for g, (ini, fim) in anos_gov.items()}


def _atualiza(ind, novos, parcial=(), estimativa=(), metodo=None, nota=None, mandato=None, outra=None):
    """Troca os anos de 'novos' na série anual, recalcula o mandato de Bolsonaro e Lula 3 e registra o que é parcial ou estimado."""
    ind["anual"].update({str(a): v for a, v in novos.items()})
    if mandato is None:
        por_gov = _por_governo({str(a): v for a, v in novos.items()})
        mandato = {g: _media(v) for g, v in por_gov.items() if v}
    ind["mandato"].update({g: v for g, v in mandato.items() if v is not None})
    if parcial:
        ind["parcial"] = sorted({int(a) for a in list(ind.get("parcial", [])) + list(parcial)})
    if estimativa:
        ind["estimativa"] = sorted({int(a) for a in list(ind.get("estimativa", [])) + list(estimativa)})
    if outra is not None:
        ind["outra_metodologia"] = outra
    if metodo:
        ind["metodo"] = metodo
    if nota:
        ind["nota"] = nota


def aplicar(ind):
    macro = _carrega("macro.json")
    ia = macro["indicadores_anuais"]
    anual_macro = lambda campo, parcial=True: {r["ano"]: r[campo] for r in ia if r.get(campo) is not None and (parcial or not r.get("parcial"))}
    parcial_macro = [r["ano"] for r in ia if r.get("parcial")]
    aviso = " Para Bolsonaro e Lula 3 o painel usa os mesmos dados da versão padrão da aba (a série longa original vale para os governos anteriores)."

    # PIB: média simples das taxas anuais, como na versão padrão; 2026 fica de fora porque ainda não fechou
    pib = {r["ano"]: r["crescimento_pib_pct"] for r in macro["pib_anual"] if not r.get("parcial") and r["ano"] >= 2019}
    ind["pib"]["mandato"] = {g: _media([v for a, v in ind["pib"]["anual"].items() if ini <= int(a) <= fim and v is not None]) for g, (ini, fim)
                             in {"FHC 1": (1995, 1998), "FHC 2": (1999, 2002), "Lula 1": (2003, 2006), "Lula 2": (2007, 2010), "Dilma 1": (2011, 2014),
                                 "Dilma 2": (2015, 2015), "Temer": (2016, 2018)}.items() if any(ini <= int(a) <= fim for a in ind["pib"]["anual"])}
    _atualiza(ind["pib"], pib, metodo="Média simples das taxas anuais de cada mandato." + aviso,
              nota="Lula 3 com 2023–2025 (2026 ainda não fechado). Bolsonaro e Lula 3 usam os valores da versão padrão; os demais, a série do Banco Central (SGS 7326).")

    # Selic e dólar: médias anuais da versão padrão (Selic meta do Copom e PTAX); Lula 3 inclui o ano parcial de 2026
    for chave, campo, nome in (("selic", "selic_media", "Selic média"), ("dolar", "dolar_medio", "Dólar médio")):
        novos = anual_macro(campo)
        _atualiza(ind[chave], novos, parcial=parcial_macro,
                  metodo=f"Média das médias anuais de cada mandato (Lula 3 inclui o ano parcial de 2026)." + aviso, outra=ind[chave].get("outra_metodologia"))

    # Resultado primário e dívidas: mesmos números da versão padrão
    for chave, campo in (("primario", "resultado_primario_pib_pct"),):
        novos = anual_macro(campo)
        _atualiza(ind[chave], novos, parcial=parcial_macro, metodo="Média anual do resultado primário (% do PIB) em cada mandato." + aviso)

    # Desemprego: média dos meses (trimestres móveis) de cada mandato, como na versão padrão
    pn = _carrega("pnadc.json")
    meses = {}
    for r in pn["series_mensal"]:
        meses.setdefault(int(r["ano"]), []).append((r["periodo_codigo"], r["taxa_desocupacao"]))
    anual_d = {a: _media([v for _, v in l]) for a, l in meses.items() if a >= 2019}
    mand = {}
    for g, (ini, fim) in GOVS_NOVOS.items():
        vals = [v for a, l in meses.items() if ini <= a <= fim for _, v in l]
        if vals:
            mand[g] = _media(vals)
    ultimo_ano = max(meses)
    parcial = [ultimo_ano] if len(meses[ultimo_ano]) < 12 else []
    _atualiza(ind["desemprego"], anual_d, parcial=parcial, mandato=mand,
              metodo=ind["desemprego"]["metodo"] + " Para Bolsonaro e Lula 3, a média de cada mandato é a dos meses (trimestres móveis) da PNAD Contínua, incluindo os meses de 2026 já divulgados.")

    # Caged: mesmos saldos anuais da versão padrão; média mensal do mandato = saldo total / meses
    cg = [r for r in pn["caged"] if r["ano"] >= 2019]
    anual_c = {r["ano"]: round(r["saldo_postos_formais"] / 1000, 1) for r in cg}
    mand = {}
    for g, (ini, fim) in GOVS_NOVOS.items():
        linhas = [r for r in cg if ini <= r["ano"] <= fim]
        if linhas:
            mand[g] = round(sum(r["saldo_postos_formais"] for r in linhas) / sum(r["meses"] for r in linhas) / 1000, 1)
    _atualiza(ind["caged"], anual_c, parcial=[r["ano"] for r in cg if r.get("parcial")], mandato=mand,
              metodo="Saldo de empregos formais por mês, em média, em cada mandato (saldo total dividido pelos meses)." + aviso)

    # Safra: CONAB, mesma tabela da versão padrão (2026 = estimativa da safra 2025/26)
    cn = {r["ano_referencia"]: r["producao_total_milhoes_t"] for r in _carrega("conab.json")}
    est = [a for a in cn if a >= 2026]
    _atualiza(ind["safra"], cn, estimativa=est, metodo="Média da produção de grãos de cada mandato; cada safra é atribuída ao ano em que termina (2024/25 = 2025)." + aviso,
              nota="Produção cresce com área e tecnologia ao longo de décadas. Lula 3 inclui a estimativa da safra 2025/26 (2026).")

    # Comércio exterior: MDIC/ComexStat (mesma fonte da versão padrão) de 1997 em diante
    cx = {r["ano"]: r for r in _carrega("comexstat.json")["anual"] if not r.get("parcial")}
    extra = {}
    try:
        extra = _carrega("comexstat_historico.json")  # 1997–2017, coletado por coletar_comexstat_historico.py
    except OSError:
        pass
    series = {"exportacoes": "exportacoes_bi_usd", "importacoes": "importacoes_bi_usd", "saldo_comercial": "saldo_bi_usd"}
    for chave, campo in series.items():
        novos = {a: r[campo] for a, r in cx.items()}
        novos.update({int(a): v[campo] for a, v in extra.items() if int(a) not in novos})
        gov_anos = {"FHC 1": (1995, 1998), "FHC 2": (1999, 2002), "Lula 1": (2003, 2006), "Lula 2": (2007, 2010), "Dilma 1": (2011, 2014),
                    "Dilma 2": (2015, 2015), "Temer": (2016, 2018), "Bolsonaro": (2019, 2022), "Lula 3": (2023, 2030)}
        mand = {}
        for g, (ini, fim) in gov_anos.items():
            vals = [novos[a] if a in novos else ind[chave]["anual"].get(str(a)) for a in range(ini, min(fim, 2025) + 1)]
            vals = [v for v in vals if v is not None]
            if vals:
                mand[g] = round(sum(vals) / len(vals), 1)
        outra = sorted(a for a in range(1995, 1997) if str(a) in ind[chave]["anual"])
        _atualiza(ind[chave], novos, mandato=mand, outra=outra, metodo="Média dos valores anuais (anos fechados), em dólares correntes, pelo MDIC/ComexStat (valores FOB).",
                  nota="De 1997 em diante a série é a do MDIC (a mesma da versão padrão); 1995 e 1996 vêm do balanço de pagamentos do Banco Central (marcados com *), "
                       "que usa outra metodologia. Dólares correntes: o valor depende de preços internacionais.")
        ind[chave]["fonte"] = "MDIC/Secex — ComexStat (valores FOB); 1995–1996: Banco Central (balanço de pagamentos)"
        ind[chave]["url"] = "https://comexstat.mdic.gov.br/pt/home"
    return ind


def main():
    caminho = os.path.join(RAIZ, "historico.json")
    d = json.load(open(caminho, encoding="utf-8"))
    aplicar(d["indicadores"])
    json.dump(d, open(caminho, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("historico.json alinhado com a versão padrão")
    for k in ("pib", "selic", "dolar", "primario", "desemprego", "caged", "safra", "exportacoes", "importacoes", "saldo_comercial"):
        print(k, {g: v for g, v in d["indicadores"][k]["mandato"].items() if g in ("Bolsonaro", "Lula 3")})


if __name__ == "__main__":
    main()
