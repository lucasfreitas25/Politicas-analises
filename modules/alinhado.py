"""Comparação alinhada: mesmo número de meses desde a posse e opção de excluir 2020 (pandemia) do governo Bolsonaro."""
import pandas as pd
import streamlit as st

from modules.data_loader import get_pnadc_data, get_ipca_data
from modules.ui_components import fmt_br, render_source

MODOS = {
    "mesmo_periodo": "Mesmo período (primeiros meses de cada governo)",
    "sem_2020": "Bolsonaro sem 2020 (pandemia)",
    "completo": "Mandatos completos",
}


def _janela(df, col_gov_ini, n):
    return df.iloc[:n] if n else df


def _metricas(df_pnad, df_ipca, modo):
    """Devolve (n_meses_b, n_meses_l, dict de valores) para cada governo conforme o modo."""
    pb = df_pnad[df_pnad["ano"].between(2019, 2022)].reset_index(drop=True)
    pl = df_pnad[df_pnad["ano"] >= 2023].reset_index(drop=True)
    ib = df_ipca[df_ipca["ano"].between(2019, 2022)].reset_index(drop=True)
    il = df_ipca[df_ipca["ano"] >= 2023].reset_index(drop=True)

    if modo == "mesmo_periodo":
        n = min(len(pl), len(il))
        pb, pl, ib, il = pb.iloc[:n], pl.iloc[:n], ib.iloc[:n], il.iloc[:n]
    elif modo == "sem_2020":
        pb = pb[pb["ano"] != 2020]
        ib = ib[ib["ano"] != 2020]

    def resumo(p, i):
        acum = ((1 + i["ipca_mensal"] / 100).prod() - 1) * 100
        meses = len(i)
        return {
            "meses_pnad": len(p), "meses_ipca": meses,
            "desemprego": p["taxa_desocupacao"].mean(),
            "renda_ini": p["rendimento_medio_real"].iloc[0], "renda_fim": p["rendimento_medio_real"].iloc[-1],
            "ipca_acum": acum, "ipca_ano": ((1 + acum / 100) ** (12 / meses) - 1) * 100,
        }

    return resumo(pb, ib), resumo(pl, il)


def render_comparacao_alinhada():
    st.subheader("Comparação alinhada: mesmo período e pandemia")
    st.caption("Lula ainda está no mandato, então o confronto de 48 meses contra 44–45 meses embute uma diferença de tamanho. "
               "Aqui dá para olhar só os primeiros meses de cada governo, ou tirar 2020 do governo Bolsonaro.")
    modo = st.radio("Recorte:", list(MODOS), format_func=MODOS.get, horizontal=True, key="modo_alinhado")

    df_pnad, _ = get_pnadc_data()
    df_ipca = get_ipca_data()[0]
    if df_pnad.empty or df_ipca.empty:
        st.info("Séries mensais indisponíveis.")
        return
    b, l = _metricas(df_pnad, df_ipca, modo)

    linhas = [
        ("Desemprego médio (PNAD, %)", fmt_br(b["desemprego"]), fmt_br(l["desemprego"]), l["desemprego"] < b["desemprego"], "↓ menor é melhor"),
        ("Rendimento real: variação do primeiro ao último dado (%)",
         f"{b['renda_fim'] / b['renda_ini'] * 100 - 100:+.1f}".replace(".", ","), f"{l['renda_fim'] / l['renda_ini'] * 100 - 100:+.1f}".replace(".", ","),
         (l["renda_fim"] / l["renda_ini"]) > (b["renda_fim"] / b["renda_ini"]), "↑ maior é melhor"),
        ("IPCA acumulado no recorte (%)", fmt_br(b["ipca_acum"]), fmt_br(l["ipca_acum"]), l["ipca_acum"] < b["ipca_acum"], "↓ menor é melhor"),
        ("IPCA anualizado (% a.a.)", fmt_br(b["ipca_ano"]), fmt_br(l["ipca_ano"]), l["ipca_ano"] < b["ipca_ano"], "↓ menor é melhor"),
    ]
    tabela = pd.DataFrame([{
        "Indicador": n, "Como ler": d, f"Bolsonaro ({b['meses_ipca']} meses de IPCA)": vb, f"Lula ({l['meses_ipca']} meses de IPCA)": vl,
        "Melhor": "Lula" if lula else "Bolsonaro",
    } for n, vb, vl, lula, d in linhas])
    from modules.ui_components import mostrar_tabela
    mostrar_tabela(tabela, titulo_col="Indicador", width="stretch", hide_index=True)

    render_source("IBGE — PNAD Contínua (tabelas 6381 e 6405) e IPCA (tabela 1419); cálculo do painel",
                  "https://sidra.ibge.gov.br/tabela/6381")
    notas = {
        "mesmo_periodo": f"Recorte: os primeiros {l['meses_ipca']} meses de cada governo (janeiro/2019 a {l['meses_ipca']} meses depois, e janeiro/2023 até o dado mais recente). "
                         "Os dois lados passam por fases diferentes do ciclo, e o primeiro recorte inclui a pandemia.",
        "sem_2020": "Retira todos os meses de 2020 do governo Bolsonaro (choque da pandemia). Não retira 2021, em que a economia ainda se recuperava e a inflação subiu. "
                    "Como o desemprego mede o nível, o valor muda; o IPCA acumulado perde 12 meses, e por isso a taxa anualizada é a leitura mais justa.",
        "completo": "Mandato inteiro do Bolsonaro (48 meses) contra os meses já disponíveis do governo Lula.",
    }
    st.caption(notas[modo] + " Valores de renda estão a preços do último mês da série do IBGE, não do ano de cada governo. "
               "Indicadores anuais (PIB, CAGED, dívida, segurança) só têm dados fechados por ano e não entram nesta tabela.")
