import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_cesta_basica_data, get_precos_itens_data, load_json
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    fmt_br,
    COLOR_BOLSONARO,
    COLOR_LULA,
)


def render_tab_food_basket():
    render_section_header(
        "Cesta Básica & Preços Específicos",
        "Custo da cesta básica (DIEESE), poder de compra do salário mínimo e variação oficial dos preços de alimentos, "
        "combustíveis e energia em cada mandato (IPCA/IBGE).",
    )

    df_dieese, _ = get_cesta_basica_data()
    cesta_nota = load_json("cesta_basica.json").get("nota_dieese", "")
    cesta = load_json("cesta_basica.json")
    poder = cesta.get("poder_compra_salario_minimo", {})
    df_itens, fonte_itens = get_precos_itens_data()

    # 1. Cards de destaque (lidos das bases)
    col1, col2, col3 = st.columns(3)
    if not df_itens.empty:
        alim = df_itens[df_itens["item"] == "Alimentação no domicílio"]
        if not alim.empty:
            a = alim.iloc[0]
            with col1:
                render_compare_stat("Inflação de alimentos no domicílio", f"+{fmt_br(a['variacao_bolsonaro_pct'])}%",
                                    f"+{fmt_br(a['variacao_lula_pct'])}%",
                                    f"Acumulado: {a['meses_bolsonaro']} meses (Bolsonaro) x {a['meses_lula']} meses (Lula) · IPCA", better="lula")
    if poder:
        with col2:
            render_compare_stat("Cestas que o salário mínimo compra (SP)", fmt_br(poder["agosto_2022"], 2), fmt_br(poder["agosto_2026"], 2),
                                f"Ago/2022 ➔ ago/2026 · mínima de {fmt_br(poder['minimo_governo_bolsonaro']['valor'], 1)} em {poder['minimo_governo_bolsonaro']['mes']}",
                                better="lula")
    if not df_dieese.empty:
        b = df_dieese[df_dieese["governo"] == "Bolsonaro"].iloc[-1]
        l = df_dieese[df_dieese["governo"] == "Lula"].iloc[-1]
        with col3:
            render_compare_stat("% do salário mínimo líquido gasto com a cesta (SP)", f"{fmt_br(b['pct_salario_minimo'])}%", f"{fmt_br(l['pct_salario_minimo'])}%",
                                f"Dez/{b['ano']} ➔ dez/{l['ano']} · DIEESE", better="lula")

    st.markdown("---")

    # 2. Variação oficial de preços por item
    st.subheader("1. Quanto cada item subiu em cada mandato (IPCA oficial)")
    st.caption("Variação acumulada, encadeando as variações mensais publicadas pelo IBGE. Bolsonaro: jan/2019–dez/2022. Lula: jan/2023 até o último mês disponível.")

    if not df_itens.empty:
        grupo = st.segmented_control("Grupo", ["Alimentos", "Energia", "Todos"], default="Alimentos", key="cesta_grupo")
        d = df_itens.copy()
        if grupo == "Alimentos":
            d = d[d["grupo"].isin(["Alimento", "Agregado"])]
        elif grupo == "Energia":
            d = d[d["grupo"] == "Energia"]
        d = d.sort_values("variacao_bolsonaro_pct")

        fig = go.Figure()
        fig.add_trace(go.Bar(y=d["item"], x=d["variacao_bolsonaro_pct"], name="Bolsonaro (48 meses)", orientation="h",
                             marker_color=COLOR_BOLSONARO, text=d["variacao_bolsonaro_pct"].apply(lambda v: f"{v:+.1f}%".replace(".", ",")),
                             textposition="outside", hovertemplate="%{y}: %{x:+.1f}%<extra>Bolsonaro</extra>"))
        fig.add_trace(go.Bar(y=d["item"], x=d["variacao_lula_pct"], name=f"Lula ({int(d['meses_lula'].max())} meses)", orientation="h",
                             marker_color=COLOR_LULA, text=d["variacao_lula_pct"].apply(lambda v: f"{v:+.1f}%".replace(".", ",")),
                             textposition="outside", hovertemplate="%{y}: %{x:+.1f}%<extra>Lula</extra>"))
        fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.06)
        apply_plotly_theme(fig, title="Variação acumulada de preços no mandato (%)", height=max(420, 78 * len(d) + 130))
        fig.update_layout(hovermode="closest")
        # Faixas alternadas e linhas entre os itens, para separar cada alimento
        for i in range(len(d)):
            if i % 2 == 0:
                fig.add_hrect(y0=i - 0.5, y1=i + 0.5, fillcolor="rgba(148,163,184,0.07)", line_width=0, layer="below")
            if i:
                fig.add_hline(y=i - 0.5, line_width=1, line_color="rgba(148,163,184,0.35)", layer="below")
        topo = max(d["variacao_bolsonaro_pct"].max(), d["variacao_lula_pct"].max())
        fundo = min(0, d["variacao_bolsonaro_pct"].min(), d["variacao_lula_pct"].min())
        fig.update_xaxes(range=[fundo * 1.6 - (8 if fundo < 0 else 0), topo * 1.18], zeroline=True, zerolinecolor="#94a3b8", zerolinewidth=1.5, showgrid=True)
        fig.update_yaxes(showgrid=False, tickfont=dict(size=13, color="#f8fafc"))
        st.plotly_chart(fig, width="stretch")
        render_source(f"{fonte_itens}. Último mês: {df_itens['ultimo_mes'].max()[4:]}/{df_itens['ultimo_mes'].max()[:4]}",
                      "https://sidra.ibge.gov.br/tabela/7060")

        st.markdown(
            '<div class="info-box"><b>Por que os preços se comportaram assim:</b><br/>'
            '• <b>2020–2022:</b> real desvalorizado, demanda chinesa, quebra de safras e a guerra na Ucrânia (2022) dispararam '
            'óleo de soja, feijão, carnes e leite.<br/>'
            '• <b>2023–2026:</b> supersafras derrubaram óleo e ovos; café disparou com quebras de safra globais; gasolina e energia '
            'subiram com a volta de tributos federais e reajustes tarifários após os cortes de 2022.<br/>'
            '• A política federal influencia pouco o preço de cada alimento no curto prazo: câmbio, clima e mercado internacional pesam mais.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 3. Gráficos do custo e horas trabalhadas (DIEESE)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("2. Custo da cesta básica (R$ nominais, SP)")
        if not df_dieese.empty:
            fig_cesta = go.Figure(go.Bar(
                x=df_dieese["ano"].astype(str), y=df_dieese["valor_cesta_sp"],
                marker_color=[COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b") for g in df_dieese["governo"]],
                text=df_dieese["valor_cesta_sp"].apply(lambda v: f"R$ {fmt_br(v, 0)}"), textposition="outside",
                textfont=dict(color="#ffffff", size=11), hovertemplate="<b>Ano:</b> %{x}<br><b>Custo:</b> R$ %{y:,.2f}<extra></extra>",
            ))
            apply_plotly_theme(fig_cesta, title="Custo nominal da cesta básica em São Paulo (R$)")
            st.plotly_chart(fig_cesta, width="stretch")

    with col_c2:
        st.subheader("3. Horas de trabalho para comprar a cesta")
        if not df_dieese.empty:
            fig_horas = go.Figure(go.Scatter(
                x=df_dieese["ano"].astype(str), y=df_dieese["horas_trabalho_necessarias"], mode="lines+markers+text",
                marker=dict(size=8, color="#fbbf24"), line=dict(color="#f59e0b", width=3),
                text=df_dieese["horas_trabalho_necessarias"].apply(lambda v: f"{v:.1f}h"), textposition="top center",
                textfont=dict(color="#ffffff", size=11), hovertemplate="<b>Ano:</b> %{x}<br><b>Jornada:</b> %{y:.1f} horas<extra></extra>",
            ))
            apply_plotly_theme(fig_horas, title="Horas de trabalho (salário mínimo) para comprar a cesta")
            st.plotly_chart(fig_horas, width="stretch")
    render_source("DIEESE — boletins de dezembro da Pesquisa Nacional da Cesta Básica (São Paulo). " + cesta_nota,
                  "https://www.dieese.org.br/analisecestabasica/2025/202512cestabasica.pdf")
