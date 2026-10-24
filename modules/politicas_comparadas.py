"""Dados da página de Políticas, Leis & Repercussão para qualquer par de governos (ou todos), no mesmo formato da base de Bolsonaro e Lula."""
import pandas as pd
from modules.data_loader import load_json
from modules.programas_ui import programas_unificados

COLUNAS_LEIS = ["data", "governo", "norma", "tipo", "area", "resumo", "situacao", "texto_oficial", "manchete", "url_imprensa"]
SEM_REPERC = {"nivel": "Sem dado", "evidencia": "", "fonte": "", "url": ""}


def leis_unificadas():
    """Leis de FHC a Temer (base histórica) somadas às de Bolsonaro e Lula 3 já existentes no painel."""
    hist = pd.DataFrame(load_json("leis_historicas.json"))
    atual = pd.DataFrame(load_json("leis_sancionadas.json"))
    if not atual.empty:
        atual["governo"] = atual["governo"].replace({"Lula": "Lula 3"})
    partes = [d[COLUNAS_LEIS] for d in (hist, atual) if not d.empty]
    tudo = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUNAS_LEIS)
    tudo["data"] = pd.to_datetime(tudo["data"])
    return tudo.sort_values("data")


def faixa_situacao(s):
    """Reduz o texto livre de situação às mesmas cinco faixas usadas na base de Bolsonaro e Lula."""
    s = (s or "").strip()
    baixa = s.lower()
    if "suspensa" in baixa or baixa.startswith("alterado"):
        return "Em vigor em parte"
    if baixa.startswith("em vigor") or baixa.startswith(("em andamento", "prorrogado", "moeda em vigor")):
        return "Em vigor"
    if baixa.startswith("conclu"):
        return "Concluída"
    return "Deixou de valer"


def politicas_unificadas(govs):
    """Programas e políticas dos governos escolhidos, com as colunas da base original (politicas.json) mais os itens com link de fonte."""
    itens, _ = programas_unificados()
    linhas = []
    for p in itens:
        if p["governo"] not in govs:
            continue
        rep = p.get("repercussao")
        linhas.append({
            "id": p["id"], "area": p["area"], "governo": p["governo"], "ano": p["ano"], "politica": p["programa"], "descricao": p["em_uma_frase"],
            "impactos_positivos": " ".join(i["texto"] for i in p["beneficios"]) or "Não encontramos ponto positivo medido nas fontes consultadas.",
            "impactos_negativos": " ".join(i["texto"] for i in p["criticas"]) or "Não encontramos crítica relevante nas fontes consultadas.",
            "pos_itens": p["beneficios"], "neg_itens": p["criticas"],
            "status": p["situacao"], "status_categoria": faixa_situacao(p["situacao"]),
            "fonte": p["base_legal"]["nome"], "base_url": p["base_legal"].get("url", ""),
            "repercussao": rep if isinstance(rep, dict) else SEM_REPERC,
        })
    return pd.DataFrame(linhas)
