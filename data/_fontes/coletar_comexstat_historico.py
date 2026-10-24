"""
Exportações, importações e saldo anuais do MDIC/ComexStat de 1997 a 2017 (a versão padrão já tem 2018 em diante em comexstat.json).
Grava data/comexstat_historico.json. A API limita o ritmo das consultas, então demora (cerca de 8 s por consulta, com cache). Execute:
    python data/_fontes/coletar_comexstat_historico.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coletar_comexstat as cx  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comexstat_historico.json")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    saida = {}
    for ano in range(1997, 2018):
        exp, imp = cx.total("export", f"{ano}-01", f"{ano}-12"), cx.total("import", f"{ano}-01", f"{ano}-12")
        saida[str(ano)] = {"exportacoes_bi_usd": round(exp, 1), "importacoes_bi_usd": round(imp, 1), "saldo_bi_usd": round(exp - imp, 1)}
        print(ano, saida[str(ano)], flush=True)
        json.dump(saida, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
