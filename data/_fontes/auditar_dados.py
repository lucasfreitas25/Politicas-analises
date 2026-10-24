"""
Auditoria de consistência: o mesmo número (por exemplo, "Lula 3 em 2025") precisa ser igual em todas as telas do painel.

1. Compara, ano a ano, as séries da versão padrão de cada aba (macro.json, pnadc.json, comexstat.json, conab.json, ppm.json, seguranca.json, ...)
   com as séries longas das versões comparadas (historico.json e historico_extra.json) e lista diferenças acima da tolerância.
2. Refaz a média de cada mandato a partir dos valores anuais e compara com o que está guardado.
3. Confere se cada ano está no governo certo.

Execute:  python data/_fontes/auditar_dados.py        (sai com código 1 se houver divergência acima da tolerância)
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
GOV_ANO = {}
for g, ini, fim in (("FHC 1", 1995, 1998), ("FHC 2", 1999, 2002), ("Lula 1", 2003, 2006), ("Lula 2", 2007, 2010), ("Dilma 1", 2011, 2014),
                    ("Dilma 2", 2015, 2015), ("Temer", 2016, 2018), ("Bolsonaro", 2019, 2022), ("Lula 3", 2023, 2030)):
    for a in range(ini, fim + 1):
        GOV_ANO[a] = g


def carrega(nome):
    return json.load(open(os.path.join(RAIZ, nome), encoding="utf-8"))


H = carrega("historico.json")["indicadores"]
H.update(carrega("historico_extra.json")["indicadores"])


def media_ano(pares):
    acc = {}
    for a, v in pares:
        acc.setdefault(a, []).append(v)
    return {a: sum(l) / len(l) for a, l in acc.items() if l}


def series_padrao():
    """(rótulo, chave em historico, {ano: valor na versão padrão}, tolerância relativa, onde está)"""
    s = []
    macro = carrega("macro.json")
    s.append(("PIB (% ao ano)", "pib", {x["ano"]: x["crescimento_pib_pct"] for x in macro["pib_anual"] if not x.get("parcial")}, 0.03, "macro.json pib_anual"))
    ia = [x for x in macro["indicadores_anuais"] if not x.get("parcial")]
    s.append(("Selic média (% a.a.)", "selic", {x["ano"]: x["selic_media"] for x in ia}, 0.03, "macro.json selic_media"))
    s.append(("Dólar médio (R$/US$)", "dolar", {x["ano"]: x["dolar_medio"] for x in ia}, 0.03, "macro.json dolar_medio"))
    s.append(("Dívida bruta (% PIB)", "divida_bruta", {x["ano"]: x["divida_bruta_pib_pct"] for x in ia}, 0.03, "macro.json (fim do ano)"))
    s.append(("Dívida líquida (% PIB)", "divida_liquida", {x["ano"]: x["divida_liquida_pib_pct"] for x in ia}, 0.03, "macro.json (fim do ano)"))
    s.append(("Saldo comercial (US$ bi)", "saldo_comercial", {x["ano"]: x["balanca_comercial_saldo_bi_usd"] for x in ia}, 0.03, "macro.json (MDIC)"))
    s.append(("Salário mínimo nominal (R$)", None, {x["ano"]: x["salario_minimo_reais"] for x in ia}, 0.0, "só leitura"))
    pn = carrega("pnadc.json")
    s.append(("Desemprego médio (%)", "desemprego", media_ano([(x["ano"], x["taxa_desocupacao"]) for x in pn["series_mensal"]]), 0.04, "pnadc.json: média dos trimestres móveis"))
    s.append(("CAGED: saldo do ano (mil vagas)", "caged", {x["ano"]: x["saldo_postos_formais"] / 1000 for x in pn["caged"] if not x.get("parcial")}, 0.05, "pnadc.json caged (soma de 12 meses)"))
    cs = carrega("comexstat.json")["anual"]
    s.append(("Exportações (US$ bi)", "exportacoes", {x["ano"]: x["exportacoes_bi_usd"] for x in cs if not x.get("parcial")}, 0.03, "comexstat.json (MDIC)"))
    s.append(("Importações (US$ bi)", "importacoes", {x["ano"]: x["importacoes_bi_usd"] for x in cs if not x.get("parcial")}, 0.03, "comexstat.json (MDIC)"))
    cn = carrega("conab.json")
    s.append(("Safra de grãos (milhões t)", "safra", {x["ano_referencia"]: x["producao_total_milhoes_t"] for x in cn}, 0.04, "conab.json"))
    sg = carrega("seguranca.json")["mortes_violentas"]
    s.append(("Mortes violentas por 100 mil", "homicidios", {x["ano"]: x["taxa_mvi_100k"] for x in sg}, 0.10, "seguranca.json (FBSP) x Atlas da Violência"))
    ed = carrega("educacao.json")
    s.append(("IDEB anos iniciais", "ideb_iniciais", {x["ano"]: x["anos_iniciais"] for x in ed["ideb"]}, 0.0, "educacao.json"))
    s.append(("IDEB anos finais", "ideb_finais", {x["ano"]: x["anos_finais"] for x in ed["ideb"]}, 0.0, "educacao.json"))
    s.append(("IDEB ensino médio", "ideb_medio", {x["ano"]: x["ensino_medio"] for x in ed["ideb"]}, 0.0, "educacao.json"))
    ipca = carrega("ipca.json")["resumo_governos"]
    s.append(("IPCA do ano (%)", "ipca", {x["ano"]: x["ipca_anual"] for g in ipca.values() for x in g["anos"] if x.get("meses") == 12}, 0.02, "ipca.json resumo_governos"))
    ppm = carrega("ppm.json")
    bov = {x["ano"]: x["cabecas"] / 1e6 for x in ppm["efetivos"] if x["tipo_rebanho"] == "Bovino"}
    s.append(("Rebanho bovino (milhões)", "rebanho_bovino", bov, 0.01, "ppm.json"))
    leite = {x["ano"]: x["valor"] / 1e6 for x in ppm["produtos"] if x["produto"] == "Leite" and x.get("variavel", "").startswith("Produ")}
    s.append(("Leite (bilhões de litros)", "leite", leite, 0.01, "ppm.json"))
    return s


def main():
    problemas, avisos = 0, 0
    print("=" * 96)
    print("1) MESMO ANO EM DUAS TELAS: versão padrão x séries longas das versões comparadas (2019 em diante)")
    print("=" * 96)
    for rotulo, chave, padrao, tol, onde in series_padrao():
        if chave is None or chave not in H:
            continue
        longo = {int(a): v for a, v in H[chave]["anual"].items()}
        anos = sorted(a for a in set(padrao) & set(longo) if a >= 2019)
        ruins = []
        for a in anos:
            p, l = padrao[a], longo[a]
            rel = abs(p - l) / max(abs(p), abs(l), 1e-9)
            if rel > tol:
                ruins.append((a, p, l, rel))
        print(f"{'OK     ' if not ruins else 'DIVERGE'} {rotulo:34s} {len(anos):2d} anos · {onde}")
        for a, p, l, rel in ruins:
            problemas += 1
            print(f"           {a} ({GOV_ANO.get(a)}): versão padrão {p:,.3f}  x  séries longas {l:,.3f}   (diferença de {100 * rel:.1f}%)")

    print()
    print("=" * 96)
    print("2) ANO NO GOVERNO CERTO (2016 = Temer, 2015 = Dilma 2) e média de cada mandato refeita a partir dos anos")
    print("=" * 96)
    for chave, ind in H.items():
        anual = {int(a): v for a, v in ind["anual"].items()}
        por_gov = {}
        for a, v in anual.items():
            g = GOV_ANO.get(a)
            if g and a >= 1995:
                por_gov.setdefault(g, []).append(v)
        sem_lado = []
        for g, v in ind["mandato"].items():
            if g not in por_gov:
                continue
            m = sum(por_gov[g]) / len(por_gov[g])
            # só vale para indicadores cuja agregação é a média simples dos anos
            if abs(m - v) <= max(0.015 * abs(v), 0.02):
                continue
            sem_lado.append(g)
        n_ok = sum(1 for g in ind["mandato"] if g in por_gov)
        igual = n_ok - len(sem_lado)
        if igual == n_ok:
            print(f"média simples ✔  {chave}")
        elif igual == 0:
            avisos += 1
            print(f"não é média simples (variação, acumulado ou último valor)  {chave}")
        else:
            avisos += 1
            print(f"MISTO  {chave}: {igual} de {n_ok} mandatos batem com a média simples; diferem: {', '.join(sem_lado)}")
    print()
    print(f"Resultado: {problemas} divergência(s) acima da tolerância na comparação entre telas; {avisos} indicador(es) com agregação que não é média simples (conferir o método).")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
