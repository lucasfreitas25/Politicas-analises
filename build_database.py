import os
import json
import requests
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_sidra_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def governo_do_ano(ano):
    if 2019 <= ano <= 2022:
        return "Bolsonaro"
    if ano >= 2023:
        return "Lula"
    return "Temer"

def fetch_sgs(codigo, inicio="01/01/2019"):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={inicio}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=40)
        if r.status_code == 200:
            return [(int(x["data"][-4:]), int(x["data"][3:5]), float(x["valor"])) for x in r.json()]
    except Exception as e:
        print(f"Erro SGS {codigo}: {e}")
    return []

def resumir_ipca(ipca_records):
    """Acumulados, médias e extremos de 12 meses calculados a partir da série mensal oficial (BCB 433 = IPCA/IBGE)."""
    resumo = {}
    mensal = [(r["ano"], r["mes"], r["ipca_mensal"]) for r in ipca_records]
    for gov, a0, a1 in (("Bolsonaro", 2019, 2022), ("Lula", 2023, 2100)):
        idx, anos, doze = 1.0, {}, []
        for i, (ano, mes, v) in enumerate(mensal):
            if a0 <= ano <= a1:
                idx *= 1 + v / 100
                anos.setdefault(ano, []).append(v)
                # Só janelas de 12 meses inteiramente dentro do mandato
                if i >= 11 and mensal[i - 11][0] >= a0:
                    acc = 1.0
                    for _, _, w in mensal[i - 11:i + 1]:
                        acc *= 1 + w / 100
                    doze.append(((acc - 1) * 100, f"{mes:02d}/{ano}"))
        if not anos:
            continue
        n_meses = sum(len(v) for v in anos.values())
        lista_anos = []
        for ano, vals in sorted(anos.items()):
            acc = 1.0
            for v in vals:
                acc *= 1 + v / 100
            lista_anos.append({"ano": ano, "ipca_anual": round((acc - 1) * 100, 2), "meses": len(vals)})
        maior = max(doze) if doze else (0, "")
        menor = min(doze) if doze else (0, "")
        resumo[gov] = {
            "periodo": f"{a0}-{lista_anos[-1]['ano']} ({n_meses} meses)",
            "meses": n_meses,
            "acumulado_total_pct": round((idx - 1) * 100, 2),
            "media_anual_pct": round((idx ** (12 / n_meses) - 1) * 100, 2),
            "maior_12m_pct": round(maior[0], 2),
            "maior_12m_mes": maior[1],
            "menor_12m_pct": round(menor[0], 2),
            "menor_12m_mes": menor[1],
            "anos": lista_anos,
        }
    return resumo

def coletar_pib_anual():
    """Variação real anual (SIDRA 6784) complementada pelo acumulado em 4 trimestres (SIDRA 5932) para os anos sem Contas Anuais."""
    pib = {}
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/9810/p/2018-2030")
    for row in (raw or [])[1:]:
        try:
            pib[int(row["D3C"])] = {"crescimento_pib_pct": float(row["V"]), "parcial": False}
        except (ValueError, KeyError):
            pass
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/6562/p/last%2012/c11255/90707")
    for row in (raw or [])[1:]:
        try:
            cod, val = row["D3C"], float(row["V"])
        except (ValueError, KeyError):
            continue
        ano, tri = int(cod[:4]), int(cod[4:])
        if ano not in pib or pib[ano].get("parcial"):
            pib[ano] = {"crescimento_pib_pct": val, "parcial": tri != 4,
                        "nota": None if tri == 4 else f"Acumulado em 4 trimestres até o {tri}º tri/{ano}"}
    if not pib:
        # Fallback offline (IBGE, Contas Nacionais; 2026 = acumulado 4 tri até o 2º tri)
        pib = {2018: 1.7, 2019: 1.3, 2020: -3.3, 2021: 4.8, 2022: 3.0, 2023: 3.2, 2024: 3.4, 2025: 2.3}
        pib = {a: {"crescimento_pib_pct": v, "parcial": False} for a, v in pib.items()}
        pib[2026] = {"crescimento_pib_pct": 1.9, "parcial": True, "nota": "Acumulado em 4 trimestres até o 2º tri/2026"}
    return [{"ano": a, "governo": governo_do_ano(a), **v} for a, v in sorted(pib.items()) if a >= 2018]

# Dados sem API pública estável: MDIC/Secex (balança) e decretos do salário mínimo.
BALANCA_SALARIO = {
    2019: (48.0, 998), 2020: (50.4, 1045), 2021: (61.4, 1100), 2022: (61.5, 1212),
    2023: (98.9, 1320), 2024: (74.2, 1412), 2025: (68.3, 1518), 2026: (None, 1621),
}

def coletar_indicadores_bcb():
    """Selic meta (432), PTAX venda (1), DBGG %PIB (13762), DLSP %PIB (4513),
    resultado primário 12m %PIB (5793, sinal invertido: + = superávit) e juros nominais 12m %PIB (5727)."""
    series = {nome: fetch_sgs(cod) for nome, cod in (("selic", 432), ("dolar", 1), ("dbgg", 13762),
                                                      ("dlsp", 4513), ("nfsp_primario", 5793), ("juros", 5727))}
    if not series["selic"]:
        return INDICADORES_FALLBACK
    out = []
    for ano in range(2019, 2100):
        selic = [v for a, _, v in series["selic"] if a == ano]
        if not selic:
            break
        dolar = [v for a, _, v in series["dolar"] if a == ano]
        def ultimo(nome):
            vals = [(m, v) for a, m, v in series[nome] if a == ano]
            return (max(vals)[1], max(vals)[0]) if vals else (None, None)
        dbgg, mes_ref = ultimo("dbgg")
        dlsp, _ = ultimo("dlsp")
        nfsp, _ = ultimo("nfsp_primario")
        juros, _ = ultimo("juros")
        balanca, salario = BALANCA_SALARIO.get(ano, (None, None))
        out.append({
            "ano": ano,
            "governo": governo_do_ano(ano),
            "selic_fim_ano": selic[-1],
            "selic_media": round(sum(selic) / len(selic), 2),
            "dolar_fim_ano": round(dolar[-1], 2) if dolar else None,
            "dolar_medio": round(sum(dolar) / len(dolar), 2) if dolar else None,
            "balanca_comercial_saldo_bi_usd": balanca,
            "divida_bruta_pib_pct": dbgg,
            "divida_liquida_pib_pct": dlsp,
            "resultado_primario_pib_pct": round(-nfsp, 2) if nfsp is not None else None,
            "juros_nominais_pib_pct": juros,
            "salario_minimo_reais": salario,
            "mes_referencia": mes_ref,
            "parcial": mes_ref is not None and mes_ref < 12,
        })
    return out

INDICADORES_FALLBACK = [
    {"ano": 2019, "governo": "Bolsonaro", "selic_fim_ano": 4.5, "selic_media": 6.04, "dolar_fim_ano": 4.03, "dolar_medio": 3.95, "balanca_comercial_saldo_bi_usd": 48.0, "divida_bruta_pib_pct": 74.44, "divida_liquida_pib_pct": 54.7, "resultado_primario_pib_pct": -0.84, "juros_nominais_pib_pct": 5.81, "salario_minimo_reais": 998, "mes_referencia": 12, "parcial": False},
    {"ano": 2020, "governo": "Bolsonaro", "selic_fim_ano": 2.0, "selic_media": 2.89, "dolar_fim_ano": 5.2, "dolar_medio": 5.16, "balanca_comercial_saldo_bi_usd": 50.4, "divida_bruta_pib_pct": 86.94, "divida_liquida_pib_pct": 61.37, "resultado_primario_pib_pct": -9.24, "juros_nominais_pib_pct": 13.34, "salario_minimo_reais": 1045, "mes_referencia": 12, "parcial": False},
    {"ano": 2021, "governo": "Bolsonaro", "selic_fim_ano": 9.25, "selic_media": 4.54, "dolar_fim_ano": 5.58, "dolar_medio": 5.4, "balanca_comercial_saldo_bi_usd": 61.4, "divida_bruta_pib_pct": 77.31, "divida_liquida_pib_pct": 55.11, "resultado_primario_pib_pct": 0.72, "juros_nominais_pib_pct": 4.26, "salario_minimo_reais": 1100, "mes_referencia": 12, "parcial": False},
    {"ano": 2022, "governo": "Bolsonaro", "selic_fim_ano": 13.75, "selic_media": 12.55, "dolar_fim_ano": 5.22, "dolar_medio": 5.17, "balanca_comercial_saldo_bi_usd": 61.5, "divida_bruta_pib_pct": 71.68, "divida_liquida_pib_pct": 56.13, "resultado_primario_pib_pct": 1.25, "juros_nominais_pib_pct": 4.57, "salario_minimo_reais": 1212, "mes_referencia": 12, "parcial": False},
    {"ano": 2023, "governo": "Lula", "selic_fim_ano": 11.75, "selic_media": 13.3, "dolar_fim_ano": 4.84, "dolar_medio": 5.0, "balanca_comercial_saldo_bi_usd": 98.9, "divida_bruta_pib_pct": 73.83, "divida_liquida_pib_pct": 60.43, "resultado_primario_pib_pct": -2.28, "juros_nominais_pib_pct": 8.84, "salario_minimo_reais": 1320, "mes_referencia": 12, "parcial": False},
    {"ano": 2024, "governo": "Lula", "selic_fim_ano": 12.25, "selic_media": 10.94, "dolar_fim_ano": 6.19, "dolar_medio": 5.39, "balanca_comercial_saldo_bi_usd": 74.2, "divida_bruta_pib_pct": 76.27, "divida_liquida_pib_pct": 61.3, "resultado_primario_pib_pct": -0.4, "juros_nominais_pib_pct": 8.47, "salario_minimo_reais": 1412, "mes_referencia": 12, "parcial": False},
    {"ano": 2025, "governo": "Lula", "selic_fim_ano": 15.0, "selic_media": 14.42, "dolar_fim_ano": 5.5, "dolar_medio": 5.59, "balanca_comercial_saldo_bi_usd": 68.3, "divida_bruta_pib_pct": 78.64, "divida_liquida_pib_pct": 65.24, "resultado_primario_pib_pct": -0.43, "juros_nominais_pib_pct": 8.34, "salario_minimo_reais": 1518, "mes_referencia": 12, "parcial": False},
    {"ano": 2026, "governo": "Lula", "selic_fim_ano": 13.75, "selic_media": 14.47, "dolar_fim_ano": 5.01, "dolar_medio": 5.14, "balanca_comercial_saldo_bi_usd": None, "divida_bruta_pib_pct": 82.87, "divida_liquida_pib_pct": 69.27, "resultado_primario_pib_pct": -0.62, "juros_nominais_pib_pct": 9.48, "salario_minimo_reais": 1621, "mes_referencia": 8, "parcial": True},
]

ITENS_IPCA = {
    "7171": ("Alimentação no domicílio", "Agregado"), "7173": ("Arroz", "Alimento"), "12222": ("Feijão-carioca", "Alimento"),
    "7283": ("Carnes", "Alimento"), "7291": ("Contrafilé", "Alimento"), "12393": ("Leite longa vida", "Alimento"),
    "7392": ("Café moído", "Alimento"), "7375": ("Pão francês", "Alimento"), "7385": ("Óleo de soja", "Alimento"),
    "7355": ("Ovo de galinha", "Alimento"), "7657": ("Gasolina", "Energia"), "7482": ("Gás de botijão", "Energia"),
    "7485": ("Energia elétrica residencial", "Energia"),
}

def coletar_itens_ipca():
    """Variação acumulada de preços por mandato, encadeando a variação mensal oficial do IPCA (SIDRA 1419 até 2019; 7060 desde 2020)."""
    cods = ",".join(ITENS_IPCA)
    mensal = {}
    for tab, per in ((1419, "201901-201912"), (7060, "202001-210012")):
        raw = fetch_sidra_json(f"https://apisidra.ibge.gov.br/values/t/{tab}/n1/all/v/63/p/{per}/c315/{cods}")
        for row in (raw or [])[1:]:
            try:
                mensal.setdefault(row["D4C"], {})[row["D3C"]] = float(row["V"])
            except (ValueError, KeyError):
                pass
    if not mensal:
        return None
    def acumular(serie, ini, fim):
        acc, n = 1.0, 0
        for per in sorted(serie):
            if ini <= per <= fim:
                acc *= 1 + serie[per] / 100
                n += 1
        return round((acc - 1) * 100, 1), n
    itens = []
    for cod, (nome, grupo) in ITENS_IPCA.items():
        serie = mensal.get(cod, {})
        if not serie:
            continue
        var_b, n_b = acumular(serie, "201901", "202212")
        var_l, n_l = acumular(serie, "202301", "210012")
        itens.append({"codigo": cod, "item": nome, "grupo": grupo, "variacao_bolsonaro_pct": var_b, "meses_bolsonaro": n_b,
                      "variacao_lula_pct": var_l, "meses_lula": n_l, "ultimo_mes": max(serie)})
    return {"fonte": "IBGE/SIDRA tabelas 1419 e 7060 (variação mensal do IPCA encadeada)", "itens": itens}

def coletar_minorias():
    """Desocupação (v4099) e rendimento habitual real (v5933) da PNAD Contínua trimestral,
    por sexo (tabelas 4093 e 5436) e por cor ou raça (tabelas 6402 e 6405)."""
    consultas = [
        ("desocupacao", "sexo", 4093, 4099, "c2/4,5"),
        ("desocupacao", "raca", 6402, 4099, "c86/2776,2777,2779"),
        ("rendimento", "sexo", 5436, 5933, "c2/4,5"),
        ("rendimento", "raca", 6405, 5933, "c86/2776,2777,2779"),
    ]
    linhas = {}
    for indicador, recorte, tab, var, classif in consultas:
        raw = fetch_sidra_json(f"https://apisidra.ibge.gov.br/values/t/{tab}/n1/all/v/{var}/p/201801-210004/{classif}")
        for row in (raw or [])[1:]:
            try:
                valor = float(row["V"])
            except (ValueError, KeyError):
                continue
            cod = row["D3C"]
            item = linhas.setdefault(cod, {"periodo_codigo": cod, "periodo": f"{cod[5]}º tri/{cod[:4]}",
                                           "ano": int(cod[:4]), "governo": governo_do_ano(int(cod[:4]))})
            item[f"{indicador}_{row['D4N'].lower()}"] = valor
    return sorted(linhas.values(), key=lambda x: x["periodo_codigo"])

def coletar_gini():
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/7435/n1/all/v/10681/p/all")
    out = []
    for row in (raw or [])[1:]:
        try:
            ano = int(row["D3C"])
            out.append({"ano": ano, "governo": governo_do_ano(ano), "gini": float(row["V"])})
        except (ValueError, KeyError):
            pass
    return out

# Séries SGS de inadimplência da carteira de crédito (% da carteira com atraso superior a 90 dias).
# Títulos conferidos no catálogo de dados abertos do BCB.
INAD_SERIES = {
    "total": 21082,                 # carteira total (PF + PJ)
    "pf_total": 21084,              # pessoas físicas — total
    "pf_livres": 21112,             # PF recursos livres — total
    "pf_direcionados": 21145,       # PF recursos direcionados — total
    "cartao_rotativo": 21127,
    "cartao_parcelado": 21128,
    "cartao_total": 21129,
    "cheque_especial": 21113,
    "credito_pessoal_nao_consignado": 21114,
    "consignado_total": 21119,
    "veiculos": 21121,
    "imobiliario": 21151,
    "rural": 21148,
}

def coletar_inadimplencia():
    """Série mensal de inadimplência (BCB/SGS) — apenas carteiras com atraso, foco em pessoas físicas."""
    por_mes = {}
    for nome, codigo in INAD_SERIES.items():
        for ano, mes, valor in fetch_sgs(codigo, "01/01/2018"):
            item = por_mes.setdefault((ano, mes), {"ano": ano, "mes": mes, "periodo": f"{ano}-{mes:02d}",
                                                  "governo": governo_do_ano(ano)})
            item[nome] = valor
    return [por_mes[k] for k in sorted(por_mes)]

# Subitens do IPCA ligados às contas da casa (SIDRA 1419 para 2018–2019 e 7060 de 2020 em diante)
CONTAS_CASA = {"7485": "energia_eletrica", "7451": "agua_esgoto", "7483": "gas_encanado", "7482": "gas_botijao"}

def coletar_contas_casa():
    """Variação mensal do IPCA de energia elétrica, taxa de água e esgoto e gás, mais o IPCA geral (BCB 433)."""
    cods = ",".join(CONTAS_CASA)
    mensal = {}
    for tab, per in ((1419, "201901-201912"), (7060, "202001-210012")):
        raw = fetch_sidra_json(f"https://apisidra.ibge.gov.br/values/t/{tab}/n1/all/v/63/p/{per}/c315/{cods}")
        for row in (raw or [])[1:]:
            try:
                mensal.setdefault(row["D3C"], {})[CONTAS_CASA[row["D4C"]]] = float(row["V"])
            except (ValueError, KeyError):
                pass
    for ano, mes, valor in fetch_sgs(433, "01/01/2019"):
        mensal.setdefault(f"{ano}{mes:02d}", {})["ipca_geral"] = valor
    return [{"periodo_codigo": k, "ano": int(k[:4]), "mes": int(k[4:]), "governo": governo_do_ano(int(k[:4])), **mensal[k]}
            for k in sorted(mensal)]

def coletar_saneamento():
    """Cobertura de água e esgoto nos domicílios (PNAD Contínua anual, IBGE).
    Esgoto adequado = rede geral/pluvial + fossa séptica ligada à rede. A PNAD não divulga 2020 e 2021."""
    anos = {}
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/7192/n1/all/v/9988/p/all/c1/6795/c11558/47930,47931")
    for row in (raw or [])[1:]:
        try:
            ano = int(row["D3C"]); v = float(row["V"])
        except (ValueError, KeyError):
            continue
        campo = "esgoto_rede_pct" if row["D5C"] == "47930" else "esgoto_fossa_ligada_pct"
        anos.setdefault(ano, {})[campo] = v
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6731/n1/all/v/9784/p/all/c1/6795/c825/46285")
    for row in (raw or [])[1:]:
        try:
            anos.setdefault(int(row["D3C"]), {})["agua_rede_pct"] = float(row["V"])
        except (ValueError, KeyError):
            pass
    raw = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6732/n1/all/v/9976/p/all/c1/6795/c826/46293")
    for row in (raw or [])[1:]:
        try:
            anos.setdefault(int(row["D3C"]), {})["agua_diaria_pct"] = float(row["V"])
        except (ValueError, KeyError):
            pass
    out = []
    for ano in sorted(anos):
        d = anos[ano]
        if "esgoto_rede_pct" in d and "esgoto_fossa_ligada_pct" in d:
            d["esgoto_adequado_pct"] = round(d["esgoto_rede_pct"] + d["esgoto_fossa_ligada_pct"], 1)
        out.append({"ano": ano, "governo": governo_do_ano(ano), **d})
    return out

def build_data():
    print("Iniciando coleta e consolidação dos dados oficiais do IBGE, CONAB e BCB...")

    # 1. MERCADO DE TRABALHO (PNADC)
    # Tabela 6381: Taxa de desocupação mensal dos trimestres móveis
    print("Coletando PNADC Desocupação...")
    raw_desoc = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6381/n1/all/v/4099/p/last%2096/d/v4099%201")
    desoc_list = []
    if raw_desoc and len(raw_desoc) > 1:
        for row in raw_desoc[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    periodo = row.get("D3N", "")
                    code = row.get("D3C", "")
                    desoc_list.append({
                        "periodo_codigo": code,
                        "periodo": periodo,
                        "taxa_desocupacao": fval
                    })
                except ValueError:
                    pass

    # Tabela 6390: Rendimento médio real habitual
    print("Coletando PNADC Rendimento Real...")
    raw_rend = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6390/n1/all/v/5933/p/last%2096/d/v5933%201")
    rend_list = []
    if raw_rend and len(raw_rend) > 1:
        for row in raw_rend[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    rend_list.append({
                        "periodo_codigo": row.get("D3C", ""),
                        "periodo": row.get("D3N", ""),
                        "rendimento_medio_real": fval
                    })
                except ValueError:
                    pass

    # Tabela 6392: Massa de rendimento real habitual
    print("Coletando PNADC Massa Salarial...")
    raw_massa = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6392/n1/all/v/6293/p/last%2096/d/v6293%201")
    massa_list = []
    if raw_massa and len(raw_massa) > 1:
        for row in raw_massa[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    massa_list.append({
                        "periodo_codigo": row.get("D3C", ""),
                        "periodo": row.get("D3N", ""),
                        "massa_rendimento_real_milhoes": fval
                    })
                except ValueError:
                    pass

    # Tabela 6320: População ocupada
    print("Coletando PNADC População Ocupada...")
    raw_pop = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/6320/n1/all/v/4090/p/last%2096/c11913/0/d/v4090%201")
    pop_list = []
    if raw_pop and len(raw_pop) > 1:
        for row in raw_pop[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    pop_list.append({
                        "periodo_codigo": row.get("D3C", ""),
                        "periodo": row.get("D3N", ""),
                        "populacao_ocupada_mil": fval
                    })
                except ValueError:
                    pass

    # Merge PNADC por periodo_codigo
    pnad_map = {}
    for item in desoc_list:
        p = item["periodo_codigo"]
        # Determinar governo pelo ano no código (formato YYYYMM)
        ano = int(str(p)[:4]) if str(p)[:4].isdigit() else 2022
        gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Temer/Anterior")
        pnad_map[p] = {
            "periodo_codigo": p,
            "periodo": item["periodo"],
            "ano": ano,
            "governo": gov,
            "taxa_desocupacao": item["taxa_desocupacao"],
            "rendimento_medio_real": None,
            "massa_rendimento_real_milhoes": None,
            "populacao_ocupada_mil": None
        }
    for item in rend_list:
        p = item["periodo_codigo"]
        if p in pnad_map:
            pnad_map[p]["rendimento_medio_real"] = item["rendimento_medio_real"]
    for item in massa_list:
        p = item["periodo_codigo"]
        if p in pnad_map:
            pnad_map[p]["massa_rendimento_real_milhoes"] = item["massa_rendimento_real_milhoes"]
    for item in pop_list:
        p = item["periodo_codigo"]
        if p in pnad_map:
            pnad_map[p]["populacao_ocupada_mil"] = item["populacao_ocupada_mil"]

    pnad_final = sorted(list(pnad_map.values()), key=lambda x: str(x["periodo_codigo"]))
    
    # CAGED Saldo anual
    # Saldo anual de empregos formais — SÉRIE COM AJUSTES do MTE (inclui declarações fora do prazo).
    # 2019 = CAGED antigo; 2020 em diante = Novo CAGED (metodologia diferente, ver Nota Técnica do MTE).
    # Fonte: MTE, apresentação "Estatísticas mensais do emprego formal – Novo Caged", dez/2025 (pág. 11);
    # 2026 = acumulado jan–ago (divulgação de set/2026). Os valores das primeiras divulgações de cada ano
    # (ex.: 2020 = +142.690) foram revisados depois — NÃO use as divulgações originais.
    caged_data = [
        {"ano": 2019, "governo": "Bolsonaro", "saldo_postos_formais": 644079, "meses": 12, "parcial": False},
        {"ano": 2020, "governo": "Bolsonaro", "saldo_postos_formais": -189393, "meses": 12, "parcial": False},
        {"ano": 2021, "governo": "Bolsonaro", "saldo_postos_formais": 2782295, "meses": 12, "parcial": False},
        {"ano": 2022, "governo": "Bolsonaro", "saldo_postos_formais": 2014894, "meses": 12, "parcial": False},
        {"ano": 2023, "governo": "Lula", "saldo_postos_formais": 1455279, "meses": 12, "parcial": False},
        {"ano": 2024, "governo": "Lula", "saldo_postos_formais": 1677575, "meses": 12, "parcial": False},
        {"ano": 2025, "governo": "Lula", "saldo_postos_formais": 1279498, "meses": 12, "parcial": False},
        {"ano": 2026, "governo": "Lula", "saldo_postos_formais": 1134033, "meses": 8, "parcial": True, "nota": "Acumulado jan-ago/2026"}
    ]

    with open(os.path.join(DATA_DIR, "pnadc.json"), "w", encoding="utf-8") as f:
        json.dump({"series_mensal": pnad_final, "caged": caged_data}, f, ensure_ascii=False, indent=2)

    # 2. INFLAÇÃO (IPCA - IBGE e BCB)
    print("Coletando IPCA (BCB 433 e SIDRA 7060)...")
    ipca_mensal_raw = []
    try:
        r_bcb = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json", headers=HEADERS, timeout=15)
        if r_bcb.status_code == 200:
            ipca_mensal_raw = r_bcb.json()
    except Exception as e:
        print("Erro BCB 433:", e)

    ipca_records = []
    # Filtrar de 2018 até o presente
    for item in ipca_mensal_raw:
        dt = item.get("data", "")
        if "/" in dt:
            parts = dt.split("/")
            ano = int(parts[2])
            mes = int(parts[1])
            if ano >= 2018:
                try:
                    val = float(item.get("valor", 0))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    ipca_records.append({
                        "data": dt,
                        "ano": ano,
                        "mes": mes,
                        "mes_ano": f"{mes:02d}/{ano}",
                        "governo": gov,
                        "ipca_mensal": val
                    })
                except ValueError:
                    pass

    # Calcular índice acumulado no mandato para cada governo
    # Bolsonaro: Jan 2019 a Dez 2022
    # Lula: Jan 2023 a atual
    idx_bols = 100.0
    idx_lula = 100.0
    for r in ipca_records:
        if 2019 <= r["ano"] <= 2022:
            idx_bols *= (1 + r["ipca_mensal"] / 100.0)
            r["indice_acumulado_mandato"] = round(idx_bols - 100.0, 2)
        elif r["ano"] >= 2023:
            idx_lula *= (1 + r["ipca_mensal"] / 100.0)
            r["indice_acumulado_mandato"] = round(idx_lula - 100.0, 2)
        else:
            r["indice_acumulado_mandato"] = 0.0

    # IPCA por Grupos do IBGE (Tabela 7060)
    print("Coletando IPCA Grupos (SIDRA 7060)...")
    grupos_codes = {
        "7170": "Alimentação e bebidas",
        "7445": "Habitação",
        "7486": "Artigos de residência",
        "7558": "Vestuário",
        "7625": "Transportes",
        "7660": "Saúde e cuidados pessoais",
        "7712": "Despesas pessoais",
        "7766": "Educação",
        "7786": "Comunicação"
    }
    raw_grupos = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/7060/n1/all/v/63,2265/p/last%2060/c315/7170,7445,7486,7558,7625,7660,7712,7766,7786/d/v63%202,v2265%202")
    grupos_records = []
    if raw_grupos and len(raw_grupos) > 1:
        for row in raw_grupos[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    grp_code = row.get("D4C")
                    grp_name = grupos_codes.get(grp_code, row.get("D4N"))
                    var_id = row.get("D2C") # 63 = mensal, 2265 = acumulado 12m
                    grupos_records.append({
                        "periodo": row.get("D3N"),
                        "periodo_codigo": row.get("D3C"),
                        "grupo": grp_name,
                        "variavel": "Mensal" if var_id == "63" else "Acumulado 12M",
                        "valor": fval
                    })
                except ValueError:
                    pass

    ipca_consolidado = {
        "serie_historica": ipca_records,
        "grupos": grupos_records,
        "resumo_governos": resumir_ipca(ipca_records)
    }
    with open(os.path.join(DATA_DIR, "ipca.json"), "w", encoding="utf-8") as f:
        json.dump(ipca_consolidado, f, ensure_ascii=False, indent=2)

    # 3. PAM (Produção Agrícola Municipal - IBGE)
    print("Coletando PAM (SIDRA 1612)...")
    pam_url = "https://apisidra.ibge.gov.br/values/t/1612/n1/all/v/109,214,215/p/2018,2019,2020,2021,2022,2023,2024/c81/2713,2711,2702,2692,2696,2697,2688/d/v109%201,v214%201,v215%201"
    raw_pam = fetch_sidra_json(pam_url)
    pam_records = []
    if raw_pam and len(raw_pam) > 1:
        for row in raw_pam[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    ano = int(row.get("D3C"))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    pam_records.append({
                        "ano": ano,
                        "governo": gov,
                        "cultura": row.get("D4N"),
                        "cultura_cod": row.get("D4C"),
                        "variavel": row.get("D2N"),
                        "variavel_cod": row.get("D2C"), # 109: area colhida (ha), 214: qtd produzida (t), 215: valor (mil R$)
                        "unidade": row.get("MN"),
                        "valor": fval
                    })
                except ValueError:
                    pass

    with open(os.path.join(DATA_DIR, "pam.json"), "w", encoding="utf-8") as f:
        json.dump(pam_records, f, ensure_ascii=False, indent=2)

    # 4. CONAB: data/conab.json é curado manualmente a partir dos levantamentos oficiais (sem API pública estável).

    # 5. PPM (Pesquisa da Pecuária Municipal - IBGE)
    print("Coletando PPM Efetivos e Produtos...")
    ppm_efetivos_url = "https://apisidra.ibge.gov.br/values/t/3939/n1/all/v/105/p/2018,2019,2020,2021,2022,2023,2024/c79/2670,32794,2677/d/v105%201"
    raw_ppm_efet = fetch_sidra_json(ppm_efetivos_url)
    ppm_efet_list = []
    if raw_ppm_efet and len(raw_ppm_efet) > 1:
        for row in raw_ppm_efet[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    ano = int(row.get("D3C"))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    ppm_efet_list.append({
                        "ano": ano,
                        "governo": gov,
                        "tipo_rebanho": row.get("D4N"),
                        "tipo_rebanho_cod": row.get("D4C"),
                        "cabecas": float(val)
                    })
                except ValueError:
                    pass

    ppm_prod_url = "https://apisidra.ibge.gov.br/values/t/74/n1/all/v/106,215/p/2018,2019,2020,2021,2022,2023,2024/c80/2682,2685,2687/d/v106%201,v215%201"
    raw_ppm_prod = fetch_sidra_json(ppm_prod_url)
    ppm_prod_list = []
    if raw_ppm_prod and len(raw_ppm_prod) > 1:
        for row in raw_ppm_prod[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    ano = int(row.get("D3C"))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    ppm_prod_list.append({
                        "ano": ano,
                        "governo": gov,
                        "produto": row.get("D4N"),
                        "variavel": row.get("D2N"), # Quantidade ou Valor
                        "unidade": row.get("MN"),
                        "valor": float(val)
                    })
                except ValueError:
                    pass

    with open(os.path.join(DATA_DIR, "ppm.json"), "w", encoding="utf-8") as f:
        json.dump({"efetivos": ppm_efet_list, "produtos": ppm_prod_list}, f, ensure_ascii=False, indent=2)

    # 6. PEVS (Produção da Extração Vegetal e da Silvicultura - IBGE)
    print("Coletando PEVS Silvicultura e Extração...")
    pevs_silv_url = "https://apisidra.ibge.gov.br/values/t/291/n1/all/v/143/p/2018,2019,2020,2021,2022,2023,2024/c194/0,3455,3456,3457,3458/d/v143%201"
    raw_pevs_silv = fetch_sidra_json(pevs_silv_url)
    silv_list = []
    if raw_pevs_silv and len(raw_pevs_silv) > 1:
        for row in raw_pevs_silv[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    ano = int(row.get("D3C"))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    silv_list.append({
                        "ano": ano,
                        "governo": gov,
                        "produto": row.get("D4N"),
                        "tipo": "Silvicultura",
                        "valor_producao_mil_reais": float(val)
                    })
                except ValueError:
                    pass

    pevs_extr_url = "https://apisidra.ibge.gov.br/values/t/289/n1/all/v/145/p/2018,2019,2020,2021,2022,2023,2024/c193/0,3403,3406,3409/d/v145%201"
    raw_pevs_extr = fetch_sidra_json(pevs_extr_url)
    extr_list = []
    if raw_pevs_extr and len(raw_pevs_extr) > 1:
        for row in raw_pevs_extr[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    ano = int(row.get("D3C"))
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    extr_list.append({
                        "ano": ano,
                        "governo": gov,
                        "produto": row.get("D4N"),
                        "tipo": "Extração Vegetal",
                        "valor_producao_mil_reais": float(val)
                    })
                except ValueError:
                    pass

    with open(os.path.join(DATA_DIR, "pevs.json"), "w", encoding="utf-8") as f:
        json.dump({"silvicultura": silv_list, "extracao": extr_list}, f, ensure_ascii=False, indent=2)

    # 7. PIM-PF (Pesquisa Industrial Mensal - IBGE)
    print("Coletando PIM-PF (SIDRA 8888)...")
    pim_url = "https://apisidra.ibge.gov.br/values/t/8888/n1/all/v/12607,11604/p/last%2084/c544/129314,129315,129316/d/v12607%202,v11604%202"
    raw_pim = fetch_sidra_json(pim_url)
    pim_records = []
    if raw_pim and len(raw_pim) > 1:
        for row in raw_pim[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    p_cod = row.get("D3C")
                    ano = int(str(p_cod)[:4]) if str(p_cod)[:4].isdigit() else 2022
                    gov = "Bolsonaro (2019-2022)" if 2019 <= ano <= 2022 else ("Lula (2023-atual)" if ano >= 2023 else "Base 2018")
                    v_cod = row.get("D2C") # 12607 = Indice sazonal, 11604 = Acumulado 12m
                    pim_records.append({
                        "periodo_codigo": p_cod,
                        "periodo": row.get("D3N"),
                        "ano": ano,
                        "governo": gov,
                        "atividade": row.get("D4N"),
                        "variavel": "Índice com ajuste sazonal (2022=100)" if v_cod == "12607" else "Acumulado em 12 meses (%)",
                        "valor": fval
                    })
                except ValueError:
                    pass

    with open(os.path.join(DATA_DIR, "pim.json"), "w", encoding="utf-8") as f:
        json.dump(pim_records, f, ensure_ascii=False, indent=2)

    # 8. MACROECONOMIA & CONTAS NACIONAIS (PIB, SELIC, CÂMBIO, BALANÇA, DÍVIDA)
    print("Consolidando Indicadores Macroeconômicos...")
    # PIB Trimestral SIDRA 5932
    raw_pib = fetch_sidra_json("https://apisidra.ibge.gov.br/values/t/5932/n1/all/v/6564/p/last%2032/c11255/90707/d/v6564%201")
    pib_trim = []
    if raw_pib and len(raw_pib) > 1:
        for row in raw_pib[1:]:
            val = row.get("V")
            if val not in (None, "...", "-"):
                try:
                    fval = float(val)
                    trim_txt = row.get("D3N", "")
                    pib_trim.append({
                        "trimestre": trim_txt,
                        "taxa_contra_trim_anterior_ajustada": fval
                    })
                except ValueError:
                    pass

    pib_anual = coletar_pib_anual()
    indicadores_anuais = coletar_indicadores_bcb()

    macro_data = {
        "pib_trimestral": pib_trim,
        "pib_anual": pib_anual,
        "indicadores_anuais": indicadores_anuais
    }
    with open(os.path.join(DATA_DIR, "macro.json"), "w", encoding="utf-8") as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=2)

    # 9. PREÇOS DE ALIMENTOS E ENERGIA (subitens do IPCA) + GINI
    print("Coletando subitens do IPCA (SIDRA 1419 e 7060)...")
    itens = coletar_itens_ipca()
    if itens:
        with open(os.path.join(DATA_DIR, "precos_itens_ipca.json"), "w", encoding="utf-8") as f:
            json.dump(itens, f, ensure_ascii=False, indent=2)

    print("Coletando Índice de Gini (SIDRA 7435)...")
    gini = coletar_gini()
    if gini:
        with open(os.path.join(DATA_DIR, "gini.json"), "w", encoding="utf-8") as f:
            json.dump(gini, f, ensure_ascii=False, indent=2)

    print("Coletando inadimplência da carteira de crédito (BCB SGS)...")
    inad = coletar_inadimplencia()
    if inad:
        with open(os.path.join(DATA_DIR, "inadimplencia_bcb.json"), "w", encoding="utf-8") as f:
            json.dump(inad, f, ensure_ascii=False, indent=2)

    print("Coletando custos de energia, água e gás (IPCA) e cobertura de saneamento (PNAD)...")
    casa = coletar_contas_casa()
    if casa:
        with open(os.path.join(DATA_DIR, "contas_casa.json"), "w", encoding="utf-8") as f:
            json.dump(casa, f, ensure_ascii=False, indent=2)
    san = coletar_saneamento()
    if san:
        with open(os.path.join(DATA_DIR, "saneamento_ibge.json"), "w", encoding="utf-8") as f:
            json.dump(san, f, ensure_ascii=False, indent=2)

    print("Coletando desocupação e renda por sexo e cor/raça (SIDRA 4093, 6402, 5436, 6405)...")
    minorias = coletar_minorias()
    if minorias:
        with open(os.path.join(DATA_DIR, "minorias_pnad.json"), "w", encoding="utf-8") as f:
            json.dump(minorias, f, ensure_ascii=False, indent=2)

    # O scorecard (data/scorecard.json) é curado manualmente e NÃO é sobrescrito aqui.

    print("Consolidação concluída com sucesso! Todos os arquivos JSON foram gerados em data/.")

if __name__ == "__main__":
    build_data()
