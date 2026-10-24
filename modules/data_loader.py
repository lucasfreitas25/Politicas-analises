import os
import json
import streamlit as st
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@st.cache_data(ttl=3600)
def _carregar(filepath, mtime):
    """O mtime entra na chave do cache: quando o arquivo muda, o painel recarrega sem precisar reiniciar."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        return _carregar(filepath, os.path.getmtime(filepath))
    return {}

def get_pnadc_data():
    data = load_json("pnadc.json")
    series = data.get("series_mensal", [])
    caged = data.get("caged", [])
    df_series = pd.DataFrame(series)
    df_caged = pd.DataFrame(caged)
    return df_series, df_caged

def get_ipca_data():
    data = load_json("ipca.json")
    df_hist = pd.DataFrame(data.get("serie_historica", []))
    df_grupos = pd.DataFrame(data.get("grupos", []))
    resumo = data.get("resumo_governos", {})
    return df_hist, df_grupos, resumo

def get_pam_data():
    data = load_json("pam.json")
    return pd.DataFrame(data)

def get_conab_data():
    data = load_json("conab.json")
    return pd.DataFrame(data)

def get_ppm_data():
    data = load_json("ppm.json")
    df_efetivos = pd.DataFrame(data.get("efetivos", []))
    df_produtos = pd.DataFrame(data.get("produtos", []))
    return df_efetivos, df_produtos

def get_pevs_data():
    data = load_json("pevs.json")
    df_silv = pd.DataFrame(data.get("silvicultura", []))
    df_extr = pd.DataFrame(data.get("extracao", []))
    return df_silv, df_extr

def get_pim_data():
    data = load_json("pim.json")
    return pd.DataFrame(data)

def get_macro_data():
    data = load_json("macro.json")
    df_trim = pd.DataFrame(data.get("pib_trimestral", []))
    df_anual = pd.DataFrame(data.get("pib_anual", []))
    df_ind = pd.DataFrame(data.get("indicadores_anuais", []))
    return df_trim, df_anual, df_ind

def get_scorecard():
    return load_json("scorecard.json")

def get_educacao_data():
    data = load_json("educacao.json")
    df_ideb = pd.DataFrame(data.get("ideb", []))
    df_analf = pd.DataFrame(data.get("analfabetismo_pnadc", []))
    df_orc = pd.DataFrame(data.get("orcamento_mec_bi_reais", []))
    programas = data.get("programas_impacto", [])
    return df_ideb, df_analf, df_orc, programas

def get_seguranca_data():
    data = load_json("seguranca.json")
    df_mvi = pd.DataFrame(data.get("mortes_violentas", []))
    df_armas = pd.DataFrame(data.get("armas_e_drogas", []))
    destaques = data.get("destaques", {})
    return df_mvi, df_armas, destaques

def get_cesta_basica_data():
    data = load_json("cesta_basica.json")
    df_dieese = pd.DataFrame(data.get("custo_dieese_sp", []))
    itens_ipca = data.get("itens_especificos_ipca", [])
    return df_dieese, itens_ipca

def get_mulheres_minorias_data():
    data = load_json("mulheres_minorias.json")
    df_desemp = pd.DataFrame(data.get("desemprego_por_grupo", []))
    df_razao = pd.DataFrame(data.get("razao_salarial", []))
    politicas = data.get("politicas_impacto", [])
    return df_desemp, df_razao, politicas

def get_inadimplencia_data():
    """Pontos verificados de pessoas e famílias com contas em atraso (CNC, Serasa) e balanço do Desenrola."""
    return load_json("inadimplencia.json")

def get_inadimplencia_bcb():
    """Série mensal oficial de inadimplência da carteira de crédito (Banco Central, SGS)."""
    return pd.DataFrame(load_json("inadimplencia_bcb.json"))

def get_acoes_governo_data():
    data = load_json("acoes_governo.json")
    return pd.DataFrame(data)

def get_checagens_data():
    data = load_json("checagens_2026.json")
    return pd.DataFrame(data.get("checagens", [])), data.get("metadados", {})

def get_sociais_ambientais_data():
    return load_json("indicadores_sociais_ambientais.json")

def get_gini_data():
    return pd.DataFrame(load_json("gini.json"))

def get_precos_itens_data():
    data = load_json("precos_itens_ipca.json")
    return pd.DataFrame(data.get("itens", [])), data.get("fonte", "")

def get_auditoria_data():
    return pd.DataFrame(load_json("auditoria.json"))

def get_politicas_data():
    return pd.DataFrame(load_json("politicas.json"))

def get_minorias_data():
    return pd.DataFrame(load_json("minorias_pnad.json")), load_json("minorias_curado.json")

def get_contas_casa():
    """Variação mensal do IPCA de energia, água/esgoto e gás, mais contexto (bandeiras, tarifa social, saneamento)."""
    return pd.DataFrame(load_json("contas_casa.json")), load_json("contas_casa_contexto.json")

def get_saneamento_ibge():
    return pd.DataFrame(load_json("saneamento_ibge.json"))

def get_leis_data():
    return pd.DataFrame(load_json("leis_sancionadas.json"))

def get_propostas_data():
    return load_json("propostas_campanha.json")
