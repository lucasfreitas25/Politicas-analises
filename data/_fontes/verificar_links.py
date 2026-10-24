"""
Varre todos os links do painel (data/*.json e modules/*.py) e testa se respondem.
Uso: python data/_fontes/verificar_links.py [--saida relatorio_links.json]
Sai com código 1 se houver link quebrado (404, 410, erro de rede). Respostas 401/403/429 são só avisos
(muitos sites do governo bloqueiam robôs, mas abrem no navegador).
"""
import glob
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
import requests

RAIZ = __file__.replace("\\", "/").rsplit("/data/_fontes/", 1)[0]
PADRAO = re.compile(r"https?://[^\s\"'<>\)\]}]+")
UA = {"User-Agent": "Mozilla/5.0 (verificador de links do painel)"}


def coletar():
    achados = {}
    for caminho in glob.glob(f"{RAIZ}/data/*.json") + glob.glob(f"{RAIZ}/modules/*.py") + [f"{RAIZ}/app.py"]:
        try:
            texto = open(caminho, encoding="utf-8").read()
        except OSError:
            continue
        for u in PADRAO.findall(texto):
            u = u.rstrip(".,;")
            if "{" in u or "localhost" in u or "%s" in u:
                continue
            achados.setdefault(u, set()).add(caminho.replace(RAIZ + "/", ""))
    return achados


def testar(url):
    try:
        r = requests.get(url, headers=UA, timeout=25, stream=True, allow_redirects=True)
        codigo = r.status_code
        r.close()
        return url, codigo
    except requests.RequestException as e:
        return url, f"erro: {type(e).__name__}"


def main():
    achados = coletar()
    print(f"{len(achados)} links únicos")
    with ThreadPoolExecutor(max_workers=12) as ex:
        res = list(ex.map(testar, achados))
    quebrados = [(u, c) for u, c in res if isinstance(c, str) or c in (404, 410) or (isinstance(c, int) and c >= 500)]
    avisos = [(u, c) for u, c in res if c in (401, 403, 429)]
    for u, c in quebrados:
        print("QUEBRADO", c, u, "<-", sorted(achados[u])[:2])
    print(f"ok: {len(res) - len(quebrados) - len(avisos)} | avisos (bloqueio a robôs): {len(avisos)} | quebrados: {len(quebrados)}")
    if "--saida" in sys.argv:
        json.dump({"quebrados": quebrados, "avisos": avisos}, open(sys.argv[sys.argv.index("--saida") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if quebrados else 0)


if __name__ == "__main__":
    main()
