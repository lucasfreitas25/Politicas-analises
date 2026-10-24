import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_minorias_data, get_seguranca_data, get_sociais_ambientais_data, get_politicas_data
from modules.tabs_policy_balance import render_policy_card
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
)

SIDRA = "https://sidra.ibge.gov.br/tabela/"
GRUPOS = [
    ("homens", "Homens", "#60A5FA", "solid"), ("mulheres", "Mulheres", "#F472B6", "solid"),
    ("branca", "Brancos", "#E2E8F0", "dot"), ("parda", "Pardos", "#F59E0B", "dot"), ("preta", "Pretos", "#A78BFA", "dot"),
]


def _faixas_governo(fig, periodos):
    """Sombreia os trimestres de cada governo num eixo categórico."""
    idx_b = [i for i, p in enumerate(periodos) if 2019 <= int(p[-4:]) <= 2022]
    idx_l = [i for i, p in enumerate(periodos) if int(p[-4:]) >= 2023]
    if idx_b:
        fig.add_vrect(x0=idx_b[0] - 0.5, x1=idx_b[-1] + 0.5, fillcolor="#3B82F6", opacity=0.06, line_width=0,
                      annotation_text="Bolsonaro", annotation_position="top left")
    if idx_l:
        fig.add_vrect(x0=idx_l[0] - 0.5, x1=idx_l[-1] + 0.5, fillcolor="#EF2B2D", opacity=0.06, line_width=0,
                      annotation_text="Lula", annotation_position="top left")


def render_tab_social_inclusion():
    render_section_header(
        "Mulheres, Raça & Minorias",
        "Desemprego e renda por sexo e cor/raça (IBGE, série trimestral oficial), violência contra negros, mulheres e pessoas trans, "
        "terras indígenas e as políticas de cada governo para esses grupos.",
    )

    df, curado = get_minorias_data()
    df_mvi, _, _ = get_seguranca_data()
    extras = get_sociais_ambientais_data()

    # ---------------- Cartões (fim de 2022 x dado mais recente)
    if not df.empty:
        df["razao_mulher_homem"] = 100 * df["rendimento_mulheres"] / df["rendimento_homens"]
        df["razao_parda_branca"] = 100 * df["rendimento_parda"] / df["rendimento_branca"]
        df["razao_preta_branca"] = 100 * df["rendimento_preta"] / df["rendimento_branca"]
        fim_b = df[df["periodo_codigo"] == "202204"].iloc[0]
        ult = df.iloc[-1]
        ref = f"4º tri/2022 ➔ {ult['periodo']}"

        c1, c2, c3 = st.columns(3)
        with c1:
            render_compare_stat("Renda das mulheres (% da dos homens)", f"{fmt_br(fim_b['razao_mulher_homem'])}%",
                                f"{fmt_br(ult['razao_mulher_homem'])}%", ref + " · SIDRA 5436", better="lula")
        with c2:
            render_compare_stat("Renda de pretos (% da de brancos)", f"{fmt_br(fim_b['razao_preta_branca'])}%",
                                f"{fmt_br(ult['razao_preta_branca'])}%", ref + " · SIDRA 6405",
                                better="lula" if ult["razao_preta_branca"] > fim_b["razao_preta_branca"] else "bolsonaro")
        with c3:
            render_compare_stat("Desemprego de pretos", f"{fmt_br(fim_b['desocupacao_preta'])}%",
                                f"{fmt_br(ult['desocupacao_preta'])}%", ref + f" · brancos: {fmt_br(ult['desocupacao_branca'])}%", better="lula")
        c4, c5, c6 = st.columns(3)
        with c4:
            render_compare_stat("Desemprego de mulheres", f"{fmt_br(fim_b['desocupacao_mulheres'])}%",
                                f"{fmt_br(ult['desocupacao_mulheres'])}%", ref + f" · homens: {fmt_br(ult['desocupacao_homens'])}%", better="lula")
        ti = extras.get("terras_indigenas", {}).get("serie", [])
        if len(ti) == 2:
            with c5:
                render_compare_stat("Terras indígenas homologadas", str(ti[0]["homologadas"]), str(ti[1]["homologadas"]),
                                    f"{ti[0]['periodo']} x {ti[1]['periodo']} · Funai/MPI", better="lula")
        if not df_mvi.empty:
            b = df_mvi[df_mvi["governo"] == "Bolsonaro"].iloc[-1]
            l = df_mvi[df_mvi["governo"] == "Lula"].iloc[-1]
            with c6:
                render_compare_stat("Feminicídios por ano", fmt_br(b["feminicidios"], 0), fmt_br(l["feminicidios"], 0),
                                    f"{b['ano']} ➔ {l['ano']} · recorde da série (FBSP)", better="bolsonaro")

        st.markdown("---")

        # ---------------- Desemprego por grupo
        st.subheader("1. Taxa de desemprego por sexo e cor/raça (%)")
        st.caption("PNAD Contínua trimestral. A distância entre os grupos encolheu com a queda geral do desemprego, mas pretos e pardos seguem acima de brancos, e mulheres acima de homens.")
        periodos = df["periodo"].tolist()
        fig = go.Figure()
        for chave, nome, cor, traco in GRUPOS:
            fig.add_trace(go.Scatter(x=periodos, y=df[f"desocupacao_{chave}"], name=nome, mode="lines",
                                     line=dict(color=cor, width=2.5, dash=traco),
                                     hovertemplate="%{x}<br>" + nome + ": %{y:.1f}%<extra></extra>"))
        _faixas_governo(fig, periodos)
        apply_plotly_theme(fig, title="Desocupação por grupo (%)", height=430)
        fig.update_xaxes(nticks=10, tickangle=-30)
        st.plotly_chart(fig, width="stretch")
        render_source("IBGE — PNAD Contínua, tabelas 4093 (sexo) e 6402 (cor ou raça)", SIDRA + "6402")

        # ---------------- Desigualdade de renda
        st.subheader("2. Desigualdade de renda: quanto cada grupo ganha em relação ao de referência (%)")
        st.caption("Rendimento habitual real de todos os trabalhos. 100% = igualdade. O intervalo vazio (2º tri/2020 a 1º tri/2022) "
                   "não é erro: o IBGE não divulga esse recorte para o período em que a pesquisa foi feita por telefone, na pandemia.")
        fig = go.Figure()
        for col, nome, cor in (("razao_mulher_homem", "Mulheres / homens", "#F472B6"),
                               ("razao_parda_branca", "Pardos / brancos", "#F59E0B"),
                               ("razao_preta_branca", "Pretos / brancos", "#A78BFA")):
            fig.add_trace(go.Scatter(x=periodos, y=df[col], name=nome, mode="lines", line=dict(color=cor, width=3),
                                     hovertemplate="%{x}<br>" + nome + ": %{y:.1f}%<extra></extra>"))
        _faixas_governo(fig, periodos)
        apply_plotly_theme(fig, title="Razão de rendimentos entre grupos (%)", height=420)
        fig.update_xaxes(nticks=10, tickangle=-30)
        st.plotly_chart(fig, width="stretch")
        render_source("IBGE — PNAD Contínua, tabelas 5436 (sexo) e 6405 (cor ou raça); cálculo do painel", SIDRA + "6405")

    st.markdown("---")

    # ---------------- Violência
    st.subheader("3. Violência contra grupos vulneráveis")
    hn = curado.get("homicidios_negros", {})
    if hn:
        cols = st.columns(len(hn["destaques"]))
        for col, d in zip(cols, hn["destaques"]):
            with col:
                st.markdown(
                    f'<div class="kpi-card compare-stat"><div class="compare-title">{d["indicador"]}</div>'
                    f'<div class="compare-values"><span class="compare-val" style="color:#f8fafc !important;">{d["valor"]}</span></div>'
                    f'<div class="compare-foot">{d["detalhe"]}</div></div>',
                    unsafe_allow_html=True,
                )
        render_source(hn["fonte"], hn["url"])

    col_f, col_t = st.columns(2)
    with col_f:
        if not df_mvi.empty:
            fig = go.Figure(go.Bar(x=df_mvi["ano"].astype(str), y=df_mvi["feminicidios"],
                                   marker_color=[gov_color(g) for g in df_mvi["governo"]],
                                   text=df_mvi["feminicidios"].apply(lambda v: fmt_br(v, 0)), textposition="outside"))
            apply_plotly_theme(fig, title="Feminicídios registrados por ano (nº de casos)", height=380)
            st.plotly_chart(fig, width="stretch")
            render_source("FBSP — Anuários Brasileiros de Segurança Pública")
    with col_t:
        trans = pd.DataFrame(curado.get("pessoas_trans", {}).get("serie", []))
        if not trans.empty:
            fig = go.Figure(go.Bar(x=trans["ano"].astype(str), y=trans["assassinatos"],
                                   marker_color=[gov_color(g) for g in trans["governo"]],
                                   text=trans["assassinatos"].apply(lambda v: "s/ dado" if pd.isna(v) else fmt_br(v, 0)), textposition="outside"))
            apply_plotly_theme(fig, title="Assassinatos de pessoas trans e travestis (nº de casos por ano)", height=380)
            st.plotly_chart(fig, width="stretch")
            render_source(curado["pessoas_trans"]["fonte"] + ". " + curado["pessoas_trans"]["nota"], curado["pessoas_trans"]["url"])

    ti_meta = extras.get("terras_indigenas", {})
    if ti_meta:
        st.markdown(f'<div class="info-box"><b>Povos indígenas:</b> {ti_meta["nota"]}</div>', unsafe_allow_html=True)
        render_source(ti_meta["fonte"], ti_meta["url"])

    # ---------------- Políticas
    st.markdown("---")
    st.subheader("4. Políticas para mulheres, negros, indígenas e LGBTQIA+")
    pol = get_politicas_data()
    pol = pol[pol["area"] == "Direitos & Minorias"] if not pol.empty else pol
    col_b, col_l = st.columns(2)
    for col, gov in ((col_b, "Bolsonaro"), (col_l, "Lula")):
        with col:
            for _, row in pol[pol["governo"] == gov].iterrows():
                render_policy_card(row)
    st.caption("A lista completa, em todas as áreas, está na página \"Políticas: Impactos Positivos e Negativos\".")
