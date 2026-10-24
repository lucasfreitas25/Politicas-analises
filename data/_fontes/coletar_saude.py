"""
Coleta as séries de saúde que têm fonte oficial aberta e grava data/saude_series.json:

- Médicos por 10 mil habitantes, leitos de internação (SUS e total), leitos de UTI e hospitais: CNES/DATASUS via Ipeadata
  (séries do Sistema de Indicadores de Saúde do IBGE).
- Despesa da União na função Saúde: Tesouro Nacional (SICONFI, Declaração de Contas Anuais, anexo I-E), 2014 em diante.
- PIB nominal (Banco Central, SGS 1207) e IPCA (arquivo do painel) para deflacionar e calcular % do PIB.
- Cobertura vacinal (poliomielite, 3 doses, e sarampo/tríplice viral, 1ª dose): estimativas OMS/Unicef (API aberta da OMS).

Execute:  python data/_fontes/coletar_saude.py
"""
import json
import os
import time
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, "saude_series.json")


def _get(url, tentativas=4):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=180) as r:
                return json.load(r)
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(5)


def ipea(codigo):
    v = _get(f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie%28SERCODIGO=%27{codigo}%27%29")["value"]
    return {int(x["VALDATA"][:4]): round(x["VALVALOR"], 3) for x in v if x.get("NIVNOME") == "Brasil" and x["VALVALOR"] is not None}


def ipea_url(codigo):
    return f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie%28SERCODIGO=%27{codigo}%27%29"


def indice_ipca_medio():
    """Índice anual médio do IPCA (base arbitrária), para levar valores de cada ano a preços de 2025."""
    mensal = _get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2012&dataFinal=31/12/2026")
    idx, v, por_ano = {}, 100.0, {}
    for x in mensal:
        v *= 1 + float(x["valor"]) / 100
        por_ano.setdefault(int(x["data"][6:]), []).append(v)
    return {a: sum(l) / len(l) for a, l in por_ano.items() if len(l) == 12}


def pib_nominal():
    v = _get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1207/dados?formato=json&dataInicial=01/01/2012&dataFinal=31/12/2026")
    return {int(x["data"][6:]): float(x["valor"]) for x in v}


def gasto_federal_saude():
    out = {}
    for ano in range(2014, 2026):
        d = _get(f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio={ano}&no_anexo=DCA-Anexo%20I-E&id_ente=1")["items"]
        linhas = {}
        for x in d:
            if x["conta"].strip() == "10 - Saúde" and x["coluna"] in ("Despesas Empenhadas", "Despesas Pagas"):
                if x.get("rotulo") in (None, "Total Geral da Despesa por Função"):
                    linhas.setdefault(x["coluna"], []).append(x["valor"])
        if linhas.get("Despesas Empenhadas") and linhas.get("Despesas Pagas"):
            assert all(len(v) == 1 for v in linhas.values()), (ano, linhas)
            out[ano] = {"empenhado": linhas["Despesas Empenhadas"][0], "pago": linhas["Despesas Pagas"][0]}
        time.sleep(1)
    return out


def who(codigo):
    d = _get(f"https://ghoapi.azureedge.net/api/{codigo}?$filter=SpatialDim%20eq%20%27BRA%27&$orderby=TimeDim")["value"]
    return {int(x["TimeDim"]): x["NumericValue"] for x in d if x["TimeDim"] >= 2000}


def main():
    medicos = ipea("SUS_NMMED10MHUF")
    leitos_sus = ipea("SIS_NMLTINTSUS1000HUF")
    leitos_tot = ipea("SIS_NMLTINT1000HUF")
    leitos_n = ipea("SIS_NMLTINTUF")
    uti_sus = ipea("SIS_NMLTCMPSUS1000HUF")
    hosp = ipea("SIS_HOSPGERUF")
    gasto = gasto_federal_saude()
    ipca, pib = indice_ipca_medio(), pib_nominal()
    base = ipca[2025]
    for ano, g in gasto.items():
        fator = base / ipca[ano]
        g["pago_real_2025_bi"] = round(g["pago"] * fator / 1e9, 1)
        g["empenhado_real_2025_bi"] = round(g["empenhado"] * fator / 1e9, 1)
        g["pago_bi"] = round(g["pago"] / 1e9, 1)
        g["empenhado_bi"] = round(g["empenhado"] / 1e9, 1)
        g["pago_pct_pib"] = round(100 * g["pago"] / pib[ano], 2) if ano in pib else None
        del g["pago"], g["empenhado"]
    payload = {
        "atualizado_em": time.strftime("%Y-%m-%d"),
        "medicos_por_10mil": {"serie": medicos, "fonte": "CNES/DATASUS via Ipeadata (SUS_NMMED10MHUF)", "url": ipea_url("SUS_NMMED10MHUF"),
                              "nota": "Número médio mensal de médicos cadastrados no CNES por 10 mil habitantes. Conta cadastros em estabelecimentos de saúde, "
                                      "então difere do total de médicos com registro nos conselhos (Demografia Médica) e pode contar o mesmo médico mais de uma vez."},
        "leitos": {"sus_por_10mil": leitos_sus, "total_por_10mil": leitos_tot, "total": leitos_n, "uti_sus_por_10mil": uti_sus,
                   "fonte": "CNES/DATASUS via Ipeadata (SIS_NMLTINTSUS1000HUF, SIS_NMLTINT1000HUF, SIS_NMLTINTUF, SIS_NMLTCMPSUS1000HUF)",
                   "url": ipea_url("SIS_NMLTINTSUS1000HUF"),
                   "nota": "Leitos de internação (média mensal). Os leitos complementares (UTI e unidade intermediária) cresceram na pandemia (2020–2021) e voltaram a cair depois."},
        "hospitais_gerais": {"serie": hosp, "fonte": "CNES/DATASUS via Ipeadata (SIS_HOSPGERUF)", "url": ipea_url("SIS_HOSPGERUF"),
                             "nota": "Média mensal de estabelecimentos do tipo hospital geral (públicos e privados)."},
        "gasto_federal_saude": {"serie": gasto, "fonte": "Tesouro Nacional — SICONFI, Declaração de Contas Anuais (DCA-Anexo I-E), função 10 Saúde, União",
                                "url": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio=2024&no_anexo=DCA-Anexo%20I-E&id_ente=1",
                                "nota": "Despesa da União na função Saúde (inclui tudo o que o governo federal gasta com saúde, não só o piso constitucional). "
                                        "Valores reais a preços médios de 2025 (IPCA); % do PIB com o PIB nominal do Banco Central (SGS 1207). "
                                        "2020 e 2021 incluem os créditos extraordinários da Covid-19. A série pública começa em 2014."},
        "vacinacao_oms": {"poliomielite_3_doses": who("WHS4_117"), "sarampo_1_dose": who("WHS4_100"),
                          "fonte": "OMS/Unicef — estimativas nacionais de cobertura (WUENIC), via API aberta da OMS",
                          "url": "https://ghoapi.azureedge.net/api/WHS4_117?$filter=SpatialDim%20eq%20%27BRA%27",
                          "nota": "Estimativas internacionais, calculadas a partir dos dados do Ministério da Saúde e de inquéritos; podem diferir um pouco dos números do SI-PNI "
                                  "(por exemplo, para 2019 a OMS estima 72% na pólio, e o Ministério divulgou 84%). A meta é 95%."},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("gravado:", OUT)
    print("gasto:", {a: (g["pago_bi"], g["pago_real_2025_bi"], g["pago_pct_pib"]) for a, g in gasto.items()})


if __name__ == "__main__":
    main()
