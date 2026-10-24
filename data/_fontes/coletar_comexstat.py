"""
Coleta dados de comércio exterior da API pública do ComexStat (MDIC) e grava data/comexstat.json.

Anos fechados: 2018 a 2025. 2026 aparece só com os meses já divulgados e é comparado com o mesmo intervalo de 2025.
Execute:  python data/_fontes/coletar_comexstat.py
"""
import json
import os
import time

import requests

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comexstat.json")
BASE = "https://api-comexstat.mdic.gov.br"
SITE = "https://comexstat.mdic.gov.br/pt/home"


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_comexstat_cache.json")


def _cache():
    return json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}


def post(corpo, tentativas=30):
    chave = json.dumps(corpo, sort_keys=True)
    guardado = _cache()
    if chave in guardado:
        return guardado[chave]
    lista = _post(corpo, tentativas)
    guardado[chave] = lista
    json.dump(guardado, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return lista


def _post(corpo, tentativas):
    for _ in range(tentativas):
        r = requests.post(f"{BASE}/general?language=pt", json=corpo, timeout=60, verify=False)
        if r.status_code == 400:
            raise RuntimeError(f"Requisição inválida: {r.text[:200]}")
        if r.status_code == 200:
            time.sleep(8)
            return r.json()["data"]["list"]
        time.sleep(20)
    raise RuntimeError(f"ComexStat sem resposta para {corpo}")


def consulta(fluxo, de, ate, detalhes, metrica="metricFOB"):
    corpo = {"flow": fluxo, "monthDetail": False, "period": {"from": de, "to": ate}, "details": detalhes, "metrics": [metrica], "filters": []}
    return post(corpo)


def ultimo_mes_2026():
    r = requests.get(f"{BASE}/general/dates/years", timeout=30, verify=False)
    r.raise_for_status()
    for mes in range(12, 0, -1):
        try:
            lista = consulta("export", f"2026-{mes:02d}", f"2026-{mes:02d}", [])
        except RuntimeError:
            continue
        if lista and float(lista[0]["metricFOB"]) > 0:
            return mes
    return 0


def total(fluxo, de, ate):
    return sum(float(x["metricFOB"]) for x in consulta(fluxo, de, ate, [])) / 1e9


def main():
    mes = ultimo_mes_2026()
    anos = []
    for ano in range(2018, 2026):
        exp, imp = total("export", f"{ano}-01", f"{ano}-12"), total("import", f"{ano}-01", f"{ano}-12")
        anos.append({"ano": ano, "exportacoes_bi_usd": round(exp, 1), "importacoes_bi_usd": round(imp, 1), "saldo_bi_usd": round(exp - imp, 1), "parcial": False})
        print(anos[-1])
    comparacao = None
    if mes:
        e26, i26 = total("export", f"2026-01", f"2026-{mes:02d}"), total("import", f"2026-01", f"2026-{mes:02d}")
        e25, i25 = total("export", "2025-01", f"2025-{mes:02d}"), total("import", "2025-01", f"2025-{mes:02d}")
        comparacao = {"meses": mes, "exp_2026": round(e26, 1), "imp_2026": round(i26, 1), "saldo_2026": round(e26 - i26, 1),
                      "exp_2025": round(e25, 1), "imp_2025": round(i25, 1), "saldo_2025": round(e25 - i25, 1)}
        print(comparacao)

    # Principais destinos das exportações: 2022 (último ano de Bolsonaro) x 2025 (último ano fechado de Lula)
    destinos = {}
    for ano in (2022, 2025):
        lista = consulta("export", f"{ano}-01", f"{ano}-12", ["country"])
        tot = sum(float(x["metricFOB"]) for x in lista)
        top = sorted(lista, key=lambda x: -float(x["metricFOB"]))[:8]
        destinos[str(ano)] = [{"pais": x["country"], "bi_usd": round(float(x["metricFOB"]) / 1e9, 1), "pct": round(100 * float(x["metricFOB"]) / tot, 1)} for x in top]

    # Pauta por seção do Sistema Harmonizado (agro, minério, petróleo etc.)
    pauta = {}
    for ano in (2022, 2025):
        lista = consulta("export", f"{ano}-01", f"{ano}-12", ["section"])
        tot = sum(float(x["metricFOB"]) for x in lista)
        top = sorted(lista, key=lambda x: -float(x["metricFOB"]))[:8]
        pauta[str(ano)] = [{"secao": x["section"], "bi_usd": round(float(x["metricFOB"]) / 1e9, 1), "pct": round(100 * float(x["metricFOB"]) / tot, 1)} for x in top]

    payload = {
        "fonte": "MDIC/Secex — ComexStat (valores FOB em US$, API pública)", "url": SITE,
        "nota": "Anos de 2018 a 2025 fechados. 2026 só com os meses divulgados; compare com o mesmo intervalo de 2025. Valores em dólares correntes, sem correção pela inflação americana.",
        "anual": anos, "parcial_2026": comparacao, "destinos_exportacao": destinos, "pauta_exportacao": pauta,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("gravado:", OUT)


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
