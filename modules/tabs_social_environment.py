import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_macro_data, get_sociais_ambientais_data, get_gini_data
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
)

SGS_URL = "https://www3.bcb.gov.br/sgspub/"


def _rotulo_ano(row):
    return f"{row['ano']}*" if row.get("parcial") else str(row["ano"])


def _bar_by_gov(x, y, governos, title, fmt, hover_unit, height=400):
    fig = go.Figure(go.Bar(
        x=x, y=y, marker_color=[gov_color(g) for g in governos],
        text=[fmt(v) if v is not None and not pd.isna(v) else "" for v in y], textposition="outside",
        textfont=dict(color="#ffffff", size=11),
        hovertemplate="<b>%{x}</b><br>%{y:.2f} " + hover_unit + "<extra></extra>",
    ))
    apply_plotly_theme(fig, title=title, height=height)
    return fig


def render_tab_social_environment():
    render_section_header(
        "🧾 Contas Públicas, Pobreza & Desigualdade",
        "Resultado primário, dívida líquida e custo de juros (Banco Central), pobreza e desigualdade de renda (IBGE). Dados ambientais estão na página \"Meio Ambiente & Clima\".",
    )

    _, _, df_ind = get_macro_data()
    extras = get_sociais_ambientais_data()
    df_gini = get_gini_data()
    df_pob = pd.DataFrame(extras.get("pobreza", {}).get("serie", []))

    # ---------------- Cartões-resumo
    def ultimo(df, gov, col):
        sub = df[(df["governo"] == gov) & df[col].notna()]
        return sub.iloc[-1] if not sub.empty else None

    c1, c2, c3 = st.columns(3)
    if not df_ind.empty and "resultado_primario_pib_pct" in df_ind:
        b = ultimo(df_ind, "Bolsonaro", "divida_liquida_pib_pct")
        l = ultimo(df_ind, "Lula", "divida_liquida_pib_pct")
        with c1:
            render_compare_stat("Dívida líquida do setor público (% PIB)", f"{fmt_br(b['divida_liquida_pib_pct'])}%", f"{fmt_br(l['divida_liquida_pib_pct'])}%",
                                f"Dez/{b['ano']} ➔ {int(l['mes_referencia']):02d}/{l['ano']} · BCB SGS 4513", better="bolsonaro")
        b = ultimo(df_ind, "Bolsonaro", "juros_nominais_pib_pct")
        l = ultimo(df_ind, "Lula", "juros_nominais_pib_pct")
        with c2:
            render_compare_stat("Gasto com juros da dívida (% PIB, 12 meses)", f"{fmt_br(b['juros_nominais_pib_pct'])}%", f"{fmt_br(l['juros_nominais_pib_pct'])}%",
                                "Selic alta encarece a dívida · BCB SGS 5727", better="bolsonaro")
    if not df_pob.empty:
        with c3:
            render_compare_stat("População na pobreza", "31,6%", "23,1%", "2022 ➔ 2024 · menor nível desde 2012 (IBGE/SIS)", better="lula")

    c4, c5, c6 = st.columns(3)
    with c4:
        render_compare_stat("Extrema pobreza", "5,9%", "3,5%", "2022 ➔ 2024 · IBGE/SIS", better="lula")
    if not df_gini.empty:
        g22 = df_gini[df_gini["ano"] == 2022]["gini"]
        g_last = df_gini.iloc[-1]
        with c5:
            render_compare_stat("Índice de Gini (desigualdade)", fmt_br(g22.iloc[0], 3) if not g22.empty else "—", fmt_br(g_last["gini"], 3),
                                f"2022 ➔ {g_last['ano']} · quanto menor, menos desigual", better="lula")
    if not df_ind.empty and "resultado_primario_pib_pct" in df_ind:
        b = ultimo(df_ind, "Bolsonaro", "resultado_primario_pib_pct")
        l = ultimo(df_ind, "Lula", "resultado_primario_pib_pct")
        with c6:
            render_compare_stat("Resultado primário (% PIB, 12 meses)", f"{b['resultado_primario_pib_pct']:+.2f}%".replace(".", ","),
                                f"{l['resultado_primario_pib_pct']:+.2f}%".replace(".", ","),
                                f"Dez/{b['ano']} ➔ {int(l['mes_referencia']):02d}/{l['ano']} · + superávit / − déficit", better="bolsonaro")

    st.markdown("---")

    # ---------------- Fiscal
    st.subheader("1. Resultado primário do setor público consolidado (% do PIB)")
    st.caption("Receitas menos despesas, sem contar juros. Positivo = superávit; negativo = déficit. * = acumulado em 12 meses até o mês mais recente.")
    if not df_ind.empty and "resultado_primario_pib_pct" in df_ind:
        d = df_ind.dropna(subset=["resultado_primario_pib_pct"])
        fig = _bar_by_gov([_rotulo_ano(r) for _, r in d.iterrows()], d["resultado_primario_pib_pct"], d["governo"],
                          "Resultado primário (% do PIB)", lambda v: f"{v:+.2f}%".replace(".", ","), "% do PIB")
        fig.add_hline(y=0, line_color="#64748b", line_width=1)
        st.plotly_chart(fig, use_container_width=True)
        render_source("Banco Central — SGS 5793 (necessidade de financiamento primário, sinal invertido)", SGS_URL)
        st.markdown(
            '<div class="info-box"><b>Leitura:</b> o rombo de 2020 (-9,2% do PIB) veio dos gastos emergenciais da pandemia. '
            'Os superávits de 2021–22 contaram com inflação alta (que eleva a arrecadação) e receitas extraordinárias de commodities. '
            'O déficit de 2023 inclui o pagamento de cerca de R$ 92 bi em precatórios adiados pela PEC de 2021. '
            'Pela ótica do governo central, 2022 fechou com superávit de 0,5% do PIB — por isso a fala de Lula sobre ter herdado '
            '"déficit de 2,8%" foi classificada como falsa pelas agências de checagem.</div>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("2. Dívida bruta x dívida líquida (% PIB)")
            fig = go.Figure()
            x = [_rotulo_ano(r) for _, r in df_ind.iterrows()]
            fig.add_trace(go.Scatter(x=x, y=df_ind["divida_bruta_pib_pct"], name="Dívida bruta (DBGG)", mode="lines+markers",
                                     line=dict(color="#F59E0B", width=3)))
            fig.add_trace(go.Scatter(x=x, y=df_ind["divida_liquida_pib_pct"], name="Dívida líquida (DLSP)", mode="lines+markers",
                                     line=dict(color="#38BDF8", width=3)))
            fig.add_vrect(x0=-0.5, x1=3.5, fillcolor="#3B82F6", opacity=0.06, line_width=0, annotation_text="Bolsonaro", annotation_position="top left")
            fig.add_vrect(x0=3.5, x1=len(x) - 0.5, fillcolor="#F43F5E", opacity=0.06, line_width=0, annotation_text="Lula", annotation_position="top left")
            apply_plotly_theme(fig, title="Endividamento público (% do PIB)", height=400)
            st.plotly_chart(fig, use_container_width=True)
            render_source("Banco Central — SGS 13762 e 4513", SGS_URL)
        with col_b:
            st.subheader("3. Custo dos juros da dívida (% PIB)")
            d = df_ind.dropna(subset=["juros_nominais_pib_pct"])
            fig = _bar_by_gov([_rotulo_ano(r) for _, r in d.iterrows()], d["juros_nominais_pib_pct"], d["governo"],
                              "Juros nominais pagos (% do PIB, 12 meses)", lambda v: f"{v:.1f}%".replace(".", ","), "% do PIB")
            st.plotly_chart(fig, use_container_width=True)
            render_source("Banco Central — SGS 5727. Em 2020 inclui efeito de swaps cambiais.", SGS_URL)

    st.markdown("---")

    # ---------------- Pobreza e desigualdade
    col_p, col_g = st.columns(2)
    with col_p:
        st.subheader("4. Pobreza e extrema pobreza (% da população)")
        if not df_pob.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_pob["ano"].astype(str), y=df_pob["pobreza_pct"], name="Pobreza (US$ 6,85/dia PPC)",
                                 marker_color=[gov_color(g) for g in df_pob["governo"]],
                                 text=df_pob["pobreza_pct"].apply(lambda v: f"{v:.1f}%".replace(".", ",")), textposition="outside"))
            fig.add_trace(go.Scatter(x=df_pob["ano"].astype(str), y=df_pob["extrema_pobreza_pct"], name="Extrema pobreza (US$ 2,15/dia PPC)",
                                     mode="lines+markers+text", line=dict(color="#F59E0B", width=3),
                                     text=df_pob["extrema_pobreza_pct"].apply(lambda v: "" if pd.isna(v) else f"{v:.1f}%".replace(".", ",")),
                                     textposition="top center"))
            apply_plotly_theme(fig, title="Proporção da população abaixo das linhas do Banco Mundial", height=420)
            st.plotly_chart(fig, use_container_width=True)
            render_source(extras["pobreza"]["fonte"] + ". " + extras["pobreza"]["nota"], extras["pobreza"]["url"])
    with col_g:
        st.subheader("5. Desigualdade de renda (Gini)")
        if not df_gini.empty:
            d = df_gini[df_gini["ano"] >= 2016]
            fig = go.Figure(go.Scatter(
                x=d["ano"].astype(str), y=d["gini"], mode="lines+markers+text",
                marker=dict(size=9, color=[gov_color(g) for g in d["governo"]]), line=dict(color="#94A3B8", width=2),
                text=d["gini"].apply(lambda v: f"{v:.3f}".replace(".", ",")), textposition="top center",
                hovertemplate="<b>%{x}</b><br>Gini: %{y:.3f}<extra></extra>",
            ))
            apply_plotly_theme(fig, title="Índice de Gini do rendimento domiciliar per capita", height=420)
            st.plotly_chart(fig, use_container_width=True)
            render_source("IBGE — PNAD Contínua, SIDRA 7435", "https://sidra.ibge.gov.br/tabela/7435")

