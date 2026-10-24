import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_contas_casa, get_saneamento_ibge, get_politicas_data
from modules.tabs_policy_balance import render_policy_card
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
    COLOR_BOLSONARO,
    COLOR_LULA,
)

SIDRA_7060 = "https://sidra.ibge.gov.br/tabela/7060"
ITENS = [
    ("energia_eletrica", "Energia elétrica residencial", "#F59E0B"),
    ("agua_esgoto", "Taxa de água e esgoto", "#38BDF8"),
    ("gas_botijao", "Gás de botijão", "#EF2B2D"),
    ("gas_encanado", "Gás encanado", "#A78BFA"),
]


def _acum(valores):
    x = 1.0
    for v in valores:
        x *= 1 + v / 100
    return (x - 1) * 100


def _faixas(fig, periodos):
    b = [p for p in periodos if p <= "2022-12"]
    l = [p for p in periodos if p >= "2023-01"]
    if b:
        fig.add_vrect(x0=b[0], x1=b[-1], fillcolor="#3B82F6", opacity=0.07, line_width=0, annotation_text="Bolsonaro", annotation_position="top left")
    if l:
        fig.add_vrect(x0=l[0], x1=l[-1], fillcolor="#EF2B2D", opacity=0.07, line_width=0, annotation_text="Lula", annotation_position="top left")


def render_tab_home_costs():
    render_section_header(
        "Energia, Água & Esgoto: custos e cobertura",
        "Quanto subiram a conta de luz, a taxa de água e esgoto e o gás em cada mandato (IPCA/IBGE), e quantos domicílios têm água e esgoto adequados (PNAD/IBGE).",
    )

    df, ctx = get_contas_casa()
    san = get_saneamento_ibge()
    if df.empty:
        st.warning("Série de contas da casa não encontrada (data/contas_casa.json). Rode build_database.py.")
        return

    df = df.copy()
    df["periodo"] = df["ano"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
    b, l = df[df["ano"] <= 2022], df[df["ano"] >= 2023]
    n_b, n_l = len(b), len(l)
    ult = df.iloc[-1]
    ref_ult = f"{int(ult['mes']):02d}/{int(ult['ano'])}"

    # ---------------- Cartões
    acc = {c: (_acum(b[c].dropna()), _acum(l[c].dropna())) for c, _, _ in ITENS + [("ipca_geral", "", "")]}
    c1, c2, c3 = st.columns(3)
    with c1:
        render_compare_stat("Energia elétrica residencial (IPCA)", f"+{fmt_br(acc['energia_eletrica'][0])}%", f"+{fmt_br(acc['energia_eletrica'][1])}%",
                            f"Acumulado: {n_b} meses (Bolsonaro) x {n_l} meses (Lula). IPCA geral: +{fmt_br(acc['ipca_geral'][0])}% e +{fmt_br(acc['ipca_geral'][1])}%", better="bolsonaro")
    with c2:
        render_compare_stat("Taxa de água e esgoto (IPCA)", f"+{fmt_br(acc['agua_esgoto'][0])}%", f"+{fmt_br(acc['agua_esgoto'][1])}%",
                            "Cada período contra a inflação geral do mesmo período", better="bolsonaro")
    with c3:
        render_compare_stat("Gás de botijão (IPCA)", f"+{fmt_br(acc['gas_botijao'][0])}%", f"+{fmt_br(acc['gas_botijao'][1])}%",
                            "Programa Gás do Povo (gratuito) começou em nov/2025", better="lula")
    if not san.empty:
        a22 = san[san["ano"] == 2022].iloc[0]
        ult_s = san[san["esgoto_adequado_pct"].notna()].iloc[-1]
        c4, c5, c6 = st.columns(3)
        with c4:
            render_compare_stat("Domicílios com esgoto adequado", f"{fmt_br(a22['esgoto_adequado_pct'])}%", f"{fmt_br(ult_s['esgoto_adequado_pct'])}%",
                                f"2022 ➔ {int(ult_s['ano'])} · rede geral/pluvial ou fossa ligada à rede", better="lula")
        with c5:
            render_compare_stat("Domicílios com água da rede geral", f"{fmt_br(a22['agua_rede_pct'])}%", f"{fmt_br(ult_s['agua_rede_pct'])}%",
                                f"2022 ➔ {int(ult_s['ano'])} · principal forma de abastecimento", better="lula")
        with c6:
            render_compare_stat("Água de rede com fornecimento diário", f"{fmt_br(a22['agua_diaria_pct'])}%", f"{fmt_br(ult_s['agua_diaria_pct'])}%",
                                f"2022 ➔ {int(ult_s['ano'])} · % dos domicílios", better="lula")

    st.markdown("---")

    # ---------------- Índice acumulado
    st.subheader("1. Quanto subiram os preços desde jan/2019 (índice, base 100)")
    st.caption("Variações mensais do IPCA encadeadas a partir de janeiro de 2019. A linha tracejada é a inflação geral: acima dela, o item subiu mais que os preços em média.")
    periodos = df["periodo"].tolist()
    fig = go.Figure()
    for col, nome, cor in ITENS[:2] + [("ipca_geral", "IPCA geral", "#E2E8F0")]:
        idx, valores = 100.0, []
        for v in df[col].fillna(0):
            idx *= 1 + v / 100
            valores.append(round(idx, 2))
        fig.add_trace(go.Scatter(x=periodos, y=valores, name=nome, mode="lines", line=dict(color=cor, width=3 if col != "ipca_geral" else 2, dash="dot" if col == "ipca_geral" else "solid"),
                                 hovertemplate="%{x}<br>" + nome + ": %{y:.1f}<extra></extra>"))
    _faixas(fig, periodos)
    apply_plotly_theme(fig, title="Energia elétrica, água e esgoto e IPCA geral (jan/2019 = 100)", height=430)
    fig.update_xaxes(nticks=10, tickangle=-30)
    st.plotly_chart(fig, width="stretch")
    render_source("IBGE — IPCA, SIDRA 1419 (2019) e 7060 (2020 em diante), variação mensal. Último mês: " + ref_ult, SIDRA_7060)

    # ---------------- Variação real por mandato
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("2. Variação real por mandato")
        st.caption("Quanto cada item subiu acima (+) ou abaixo (−) da inflação geral do mesmo período.")
        escolhidos = st.pills("Produtos", [n for _, n, _ in ITENS], selection_mode="multi", default=[n for _, n, _ in ITENS], key="casa_produtos",
                              help="Toque para tirar ou pôr energia, água e esgoto, gás de botijão e gás encanado.") or [n for _, n, _ in ITENS]
        itens_sel = [(c, n, k) for c, n, k in ITENS if n in escolhidos]
        rotulos = [n for _, n, _ in itens_sel]
        reais_b = [((1 + acc[c][0] / 100) / (1 + acc["ipca_geral"][0] / 100) - 1) * 100 for c, _, _ in itens_sel]
        reais_l = [((1 + acc[c][1] / 100) / (1 + acc["ipca_geral"][1] / 100) - 1) * 100 for c, _, _ in itens_sel]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rotulos, y=reais_b, name="Bolsonaro", marker_color=COLOR_BOLSONARO, text=[f"{v:+.1f}%".replace(".", ",") for v in reais_b], textposition="outside"))
        fig.add_trace(go.Bar(x=rotulos, y=reais_l, name="Lula", marker_color=COLOR_LULA, text=[f"{v:+.1f}%".replace(".", ",") for v in reais_l], textposition="outside"))
        fig.update_layout(barmode="group")
        fig.add_hline(y=0, line_color="#64748b", line_width=1)
        apply_plotly_theme(fig, title="Variação acima da inflação (%)", height=420)
        st.plotly_chart(fig, width="stretch")
        render_source("Cálculo do painel: (1 + variação do item) / (1 + IPCA geral) − 1, em cada mandato.", SIDRA_7060)
    with col_b:
        st.subheader("3. Variação ano a ano")
        item = st.segmented_control("Item", [n for _, n, _ in ITENS], default="Energia elétrica residencial", key="casa_item") or "Energia elétrica residencial"
        col = next(c for c, n, _ in ITENS if n == item)
        anos = sorted(df["ano"].unique())
        vals = [_acum(df[df["ano"] == a][col].dropna()) for a in anos]
        rot = [f"{a}*" if a == int(ult["ano"]) and int(ult["mes"]) < 12 else str(a) for a in anos]
        fig = go.Figure(go.Bar(x=rot, y=vals, marker_color=[gov_color("Bolsonaro" if a <= 2022 else "Lula") for a in anos],
                               text=[f"{v:+.1f}%".replace(".", ",") for v in vals], textposition="outside"))
        apply_plotly_theme(fig, title=f"{item}: variação em cada ano (%)", height=420)
        st.plotly_chart(fig, width="stretch")
        render_source("IBGE — IPCA. * = ano em curso (parcial, até " + ref_ult + ").", SIDRA_7060)

    # ---------------- Contexto de energia
    st.markdown("---")
    st.subheader("4. Por que a conta de luz subiu")
    band = ctx.get("bandeiras_2025", {})
    soc = ctx.get("tarifa_social", {})
    colx, coly = st.columns(2)
    with colx:
        if band:
            linhas = "".join(f"<tr><td>{html.escape(i['periodo'])}</td><td>{html.escape(i['bandeira'])}</td><td>{html.escape(i['acrescimo'])}</td></tr>" for i in band["itens"])
            st.markdown(
                '<div class="kpi-card"><h4 style="color:#fbbf24;margin-bottom:8px;">Bandeiras tarifárias em 2025</h4>'
                f'<table class="custom-table"><thead><tr><th>Período</th><th>Bandeira</th><th>Acréscimo</th></tr></thead><tbody>{linhas}</tbody></table>'
                f'<div style="color:#cbd5e1;font-size:0.84rem;">{html.escape(band["motivo"])}</div>'
                f'<div class="policy-foot"><a href="{band["url"]}" target="_blank">{html.escape(band["fonte"])}</a></div></div>',
                unsafe_allow_html=True,
            )
    with coly:
        if soc:
            st.markdown(
                '<div class="kpi-card"><h4 style="color:#34d399;margin-bottom:8px;">Tarifa social ampliada (Luz do Povo)</h4>'
                f'<div style="color:#e2e8f0;font-size:0.88rem;line-height:1.55;">{html.escape(soc["resumo"])}</div>'
                f'<div class="policy-foot"><a href="{soc["url"]}" target="_blank">{html.escape(soc["fonte"])}</a></div></div>',
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div class="info-box"><b>Atenção ao que o IPCA mede:</b> é a variação do preço da tarifa, não o valor da sua conta, que também depende do consumo. '
        'A bandeira vermelha e os reajustes anuais das distribuidoras (aprovados pela Aneel) pesam no número; a tarifa social reduz a conta de quem tem direito, '
        'mas o custo é repassado aos demais consumidores pelo encargo CDE.</div>',
        unsafe_allow_html=True,
    )

    # ---------------- Cobertura de água e esgoto
    st.markdown("---")
    st.subheader("5. Água e esgoto nos domicílios (IBGE)")
    if not san.empty:
        st.caption("PNAD Contínua anual. O IBGE não divulga 2020 e 2021 (pandemia); a série de esgoto começa em 2019 por mudança de metodologia.")
        fig = go.Figure()
        d_agua = san[san["agua_rede_pct"].notna()]
        fig.add_trace(go.Scatter(x=d_agua["ano"].astype(str), y=d_agua["agua_rede_pct"], name="Água da rede geral", mode="lines+markers+text",
                                 line=dict(color="#38BDF8", width=3), text=d_agua["agua_rede_pct"].apply(lambda v: f"{v:.1f}%".replace(".", ",")), textposition="top center"))
        d_esg = san[san["esgoto_adequado_pct"].notna()]
        fig.add_trace(go.Scatter(x=d_esg["ano"].astype(str), y=d_esg["esgoto_adequado_pct"], name="Esgoto adequado", mode="lines+markers+text",
                                 line=dict(color="#A78BFA", width=3), text=d_esg["esgoto_adequado_pct"].apply(lambda v: f"{v:.1f}%".replace(".", ",")), textposition="bottom center"))
        fig.add_hline(y=90, line_dash="dot", line_color="#10B981", annotation_text="Meta legal de esgoto: 90% (2033)", annotation_position="top left")
        fig.update_yaxes(range=[55, 100])
        apply_plotly_theme(fig, title="Domicílios com água da rede e esgoto adequado (%)", height=430)
        st.plotly_chart(fig, width="stretch")
        render_source("IBGE — PNAD Contínua, SIDRA 6731 (água) e 7192 (esgoto adequado = rede geral/pluvial + fossa séptica ligada à rede).", "https://sidra.ibge.gov.br/tabela/7192")

    marco = ctx.get("saneamento_marco_legal", {})
    if marco:
        st.markdown(
            '<div class="info-box"><b>Marco Legal do Saneamento (Lei 14.026/2020):</b> '
            f'{html.escape(marco["meta"])}<br/>• <b>Estudo Trata Brasil/GO Associados:</b> {html.escape(marco["estudo"])} '
            f'(<a href="{marco["url_estudo"]}" target="_blank">fonte</a>)<br/>'
            f'• <b>Outra medida de cobertura:</b> {html.escape(marco["cobertura_trata_brasil"])} (<a href="{marco["url_cobertura"]}" target="_blank">fonte</a>)<br/>'
            f'• {html.escape(marco["gargalo"])}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Os percentuais do IBGE (domicílios) e do Trata Brasil/SNIS (população atendida pelos prestadores) medem coisas diferentes e não são comparáveis entre si.")

    # ---------------- Políticas relacionadas
    pol = get_politicas_data()
    if not pol.empty:
        rel = pol[pol["politica"].str.contains("Marco do Saneamento|Gás do Povo", regex=True)]
        if not rel.empty:
            st.markdown("---")
            st.subheader("6. Políticas relacionadas")
            cols = st.columns(len(rel))
            for col, (_, row) in zip(cols, rel.iterrows()):
                with col:
                    render_policy_card(row)
