import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
)


def _governo(ano):
    return "Bolsonaro" if ano <= 2022 else "Lula"


def _barras_destino(dados, ano, titulo):
    df = pd.DataFrame(dados[str(ano)])
    fig = go.Figure(go.Bar(
        x=df["bi_usd"], y=df["pais"], orientation="h", marker_color="#38BDF8",
        text=[f"US$ {fmt_br(v)} bi ({fmt_br(p)}%)" for v, p in zip(df["bi_usd"], df["pct"])], textposition="outside",
        hovertemplate="%{y}: US$ %{x:.1f} bi<extra></extra>"))
    apply_plotly_theme(fig, title=titulo, height=380)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, df["bi_usd"].max() * 2.0])
    fig.update_layout(hovermode="closest", margin=dict(l=20, r=30, t=70, b=30))
    st.plotly_chart(fig, width="stretch")


def render_tab_trade():
    render_section_header(
        "Comércio Exterior (ComexStat)",
        "Exportações, importações e saldo da balança comercial brasileira, com os principais destinos e a pauta de produtos, direto da base oficial do MDIC.",
    )
    dados = load_json("comexstat.json")
    if not dados:
        st.warning("Base do ComexStat não encontrada (data/comexstat.json). Rode data/_fontes/coletar_comexstat.py.")
        return
    anual = pd.DataFrame(dados["anual"])
    anual["governo"] = anual["ano"].apply(_governo)
    parcial = dados.get("parcial_2026")

    # ---------------- Cartões
    por_ano = anual.set_index("ano")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_compare_stat("Saldo comercial (último ano)", f"US$ {fmt_br(por_ano.loc[2022, 'saldo_bi_usd'])} bi", f"US$ {fmt_br(por_ano.loc[2025, 'saldo_bi_usd'])} bi",
                            "2022 ➔ 2025", better="bolsonaro" if por_ano.loc[2022, "saldo_bi_usd"] > por_ano.loc[2025, "saldo_bi_usd"] else "lula")
    with c2:
        render_compare_stat("Exportações", f"US$ {fmt_br(por_ano.loc[2022, 'exportacoes_bi_usd'])} bi", f"US$ {fmt_br(por_ano.loc[2025, 'exportacoes_bi_usd'])} bi",
                            "2022 ➔ 2025", better="lula" if por_ano.loc[2025, "exportacoes_bi_usd"] > por_ano.loc[2022, "exportacoes_bi_usd"] else "bolsonaro")
    with c3:
        render_compare_stat("Importações", f"US$ {fmt_br(por_ano.loc[2022, 'importacoes_bi_usd'])} bi", f"US$ {fmt_br(por_ano.loc[2025, 'importacoes_bi_usd'])} bi",
                            "2022 ➔ 2025 · não há lado melhor: mais importação também reflete consumo e investimento")

    st.markdown("---")

    # ---------------- Série anual
    st.subheader("1. Exportações, importações e saldo por ano")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=anual["ano"].astype(str), y=anual["exportacoes_bi_usd"], name="Exportações", marker_color="#10B981",
                         hovertemplate="%{x}: US$ %{y:.1f} bi<extra>Exportações</extra>"))
    fig.add_trace(go.Bar(x=anual["ano"].astype(str), y=anual["importacoes_bi_usd"], name="Importações", marker_color="#94A3B8",
                         hovertemplate="%{x}: US$ %{y:.1f} bi<extra>Importações</extra>"))
    fig.add_trace(go.Scatter(x=anual["ano"].astype(str), y=anual["saldo_bi_usd"], name="Saldo", mode="lines+markers+text",
                             text=[fmt_br(v) for v in anual["saldo_bi_usd"]], textposition="top center",
                             line=dict(color="#F59E0B", width=3), marker=dict(size=8)))
    fig.update_layout(barmode="group")
    apply_plotly_theme(fig, title="Balança comercial (US$ bilhões, FOB)", height=440)
    st.plotly_chart(fig, width="stretch")
    st.caption("2018 foi o último ano do governo anterior ao de Bolsonaro e serve só de referência. Valores em dólares correntes, sem correção pela inflação americana.")

    # ---------------- Cor por governo: saldo
    colunas = st.columns(2)
    with colunas[0]:
        fig = go.Figure(go.Bar(x=anual["ano"].astype(str), y=anual["saldo_bi_usd"], marker_color=[gov_color(g) for g in anual["governo"]],
                               text=[fmt_br(v) for v in anual["saldo_bi_usd"]], textposition="outside"))
        apply_plotly_theme(fig, title="Saldo por ano e governo (US$ bi)", height=380)
        st.plotly_chart(fig, width="stretch")
    with colunas[1]:
        st.markdown("**Média anual por governo (anos fechados)**")
        resumo = anual[anual["ano"] >= 2019].groupby("governo")[["exportacoes_bi_usd", "importacoes_bi_usd", "saldo_bi_usd"]].mean().round(1)
        resumo.columns = ["Exportações", "Importações", "Saldo"]
        resumo["Anos"] = anual[anual["ano"] >= 2019].groupby("governo")["ano"].count()
        st.dataframe(resumo.reset_index().rename(columns={"governo": "Governo"}), width="stretch", hide_index=True)
        st.caption("Bolsonaro: 2019–2022 (4 anos). Lula: 2023–2025 (3 anos fechados). Médias de períodos de tamanhos diferentes.")

    if parcial:
        st.markdown(
            f'<div class="info-box"><b>2026 de janeiro ao mês {parcial["meses"]} (setembro):</b> exportações de US$ {fmt_br(parcial["exp_2026"])} bi '
            f'(mesmo período de 2025: US$ {fmt_br(parcial["exp_2025"])} bi), importações de US$ {fmt_br(parcial["imp_2026"])} bi '
            f'(US$ {fmt_br(parcial["imp_2025"])} bi) e saldo de US$ {fmt_br(parcial["saldo_2026"])} bi (US$ {fmt_br(parcial["saldo_2025"])} bi em 2025).</div>',
            unsafe_allow_html=True)
    render_source(dados["fonte"], dados["url"])

    st.markdown("---")

    # ---------------- Destinos
    st.subheader("2. Para onde o Brasil exporta")
    col_a, col_b = st.columns(2)
    with col_a:
        _barras_destino(dados["destinos_exportacao"], 2022, "Principais destinos em 2022 (Bolsonaro)")
    with col_b:
        _barras_destino(dados["destinos_exportacao"], 2025, "Principais destinos em 2025 (Lula)")
    st.caption("Mudança na concentração depende sobretudo da demanda externa e dos preços; a política comercial influencia, mas não explica sozinha.")

    # ---------------- Pauta
    st.subheader("3. O que o Brasil exporta")
    col_c, col_d = st.columns(2)
    for col, ano, gov in ((col_c, 2022, "Bolsonaro"), (col_d, 2025, "Lula")):
        with col:
            df = pd.DataFrame(dados["pauta_exportacao"][str(ano)])
            df["secao"] = df["secao"].apply(lambda t: (t.split(";")[0])[:34] + ("…" if len(t.split(";")[0]) > 34 else ""))
            fig = go.Figure(go.Bar(x=df["bi_usd"], y=df["secao"], orientation="h", marker_color=gov_color(gov),
                                   text=[f"{fmt_br(p)}%" for p in df["pct"]], textposition="outside",
                                   hovertemplate="%{y}: US$ %{x:.1f} bi<extra></extra>"))
            apply_plotly_theme(fig, title=f"Pauta por seção em {ano} ({gov})", height=420)
            fig.update_yaxes(autorange="reversed", tickfont=dict(size=10))
            fig.update_xaxes(range=[0, df["bi_usd"].max() * 1.3])
            fig.update_layout(hovermode="closest", margin=dict(l=20, r=30, t=70, b=30))
            st.plotly_chart(fig, width="stretch")
    render_source(dados["fonte"] + ". Seções do Sistema Harmonizado.", dados["url"])
    st.markdown(f'<div class="info-box"><b>Como ler:</b> {html.escape(dados["nota"])}</div>', unsafe_allow_html=True)
