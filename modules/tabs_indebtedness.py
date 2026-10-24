import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_inadimplencia_bcb, get_inadimplencia_data
from modules.ui_components import (
    mostrar_tabela,
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    fmt_br,
    COLOR_BOLSONARO,
    COLOR_LULA,
)

SGS_URL = "https://www3.bcb.gov.br/sgspub/"

# (coluna, rótulo, cor) das modalidades de crédito de pessoas físicas
MODALIDADES = [
    ("cartao_rotativo", "Cartão de crédito rotativo", "#EF2B2D"),
    ("cheque_especial", "Cheque especial", "#F59E0B"),
    ("credito_pessoal_nao_consignado", "Crédito pessoal não consignado", "#A78BFA"),
    ("cartao_parcelado", "Cartão parcelado", "#F87171"),
    ("veiculos", "Aquisição de veículos", "#38BDF8"),
    ("consignado_total", "Consignado (total)", "#10B981"),
    ("imobiliario", "Financiamento imobiliário", "#94A3B8"),
    ("rural", "Crédito rural (PF)", "#84CC16"),
]


def _faixas_governo(fig, periodos):
    idx_b = [i for i, p in enumerate(periodos) if "2019-01" <= p <= "2022-12"]
    idx_l = [i for i, p in enumerate(periodos) if p >= "2023-01"]
    if idx_b:
        fig.add_vrect(x0=periodos[idx_b[0]], x1=periodos[idx_b[-1]], fillcolor="#3B82F6", opacity=0.07, line_width=0,
                      annotation_text="Bolsonaro", annotation_position="top left")
    if idx_l:
        fig.add_vrect(x0=periodos[idx_l[0]], x1=periodos[idx_l[-1]], fillcolor="#EF2B2D", opacity=0.07, line_width=0,
                      annotation_text="Lula", annotation_position="top left")


def render_tab_indebtedness():
    render_section_header(
        "Inadimplência: carteiras em atraso e contas não pagas",
        "Só o que está em atraso: a taxa de inadimplência das carteiras de crédito de pessoas físicas (Banco Central: parcelas com mais de 90 dias de atraso) "
        "e as medições de pessoas e famílias com contas atrasadas.",
    )

    df = get_inadimplencia_bcb()
    extra = get_inadimplencia_data()
    if df.empty:
        st.warning("Série de inadimplência não encontrada (data/inadimplencia_bcb.json). Rode build_database.py.")
        return

    df = df[df["periodo"] >= "2019-01"].reset_index(drop=True)
    ult = df.iloc[-1]
    dez22 = df[df["periodo"] == "2022-12"].iloc[0]
    rotulo_ult = f"{int(ult['mes']):02d}/{int(ult['ano'])}"

    # ---------------- Cartões
    c1, c2, c3 = st.columns(3)
    with c1:
        render_compare_stat("Carteira de pessoas físicas em atraso", f"{fmt_br(dez22['pf_total'], 2)}%", f"{fmt_br(ult['pf_total'], 2)}%",
                            f"Dez/2022 ➔ {rotulo_ult} · % da carteira com atraso > 90 dias", better="bolsonaro")
    with c2:
        render_compare_stat("Cartão de crédito rotativo", f"{fmt_br(dez22['cartao_rotativo'], 1)}%", f"{fmt_br(ult['cartao_rotativo'], 1)}%",
                            "Dívida que passa do vencimento da fatura e vira rotativo", better="bolsonaro")
    with c3:
        render_compare_stat("Crédito pessoal não consignado", f"{fmt_br(dez22['credito_pessoal_nao_consignado'], 1)}%",
                            f"{fmt_br(ult['credito_pessoal_nao_consignado'], 1)}%", "Empréstimo pessoal sem desconto em folha", better="bolsonaro")
    c4, c5, c6 = st.columns(3)
    with c4:
        render_compare_stat("Financiamento de veículos", f"{fmt_br(dez22['veiculos'], 1)}%", f"{fmt_br(ult['veiculos'], 1)}%", "Pessoas físicas, recursos livres", better="bolsonaro")
    with c5:
        render_compare_stat("Crédito consignado (em folha)", f"{fmt_br(dez22['consignado_total'], 1)}%", f"{fmt_br(ult['consignado_total'], 1)}%", "A modalidade de menor risco para o banco", better="bolsonaro")
    with c6:
        render_compare_stat("Financiamento imobiliário", f"{fmt_br(dez22['imobiliario'], 1)}%", f"{fmt_br(ult['imobiliario'], 1)}%", "O único em queda no período", better="lula")

    st.markdown("---")

    # ---------------- Série principal
    st.subheader("1. Inadimplência da carteira de crédito (% com atraso superior a 90 dias)")
    st.caption("Mensal, desde jan/2019. Pessoas físicas em comparação com o total da carteira (pessoas físicas e empresas).")
    periodos = df["periodo"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=periodos, y=df["pf_total"], name="Pessoas físicas", mode="lines", line=dict(color="#EF2B2D", width=3),
                             hovertemplate="%{x}<br>Pessoas físicas: %{y:.2f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=periodos, y=df["total"], name="Carteira total", mode="lines", line=dict(color="#94A3B8", width=2, dash="dot"),
                             hovertemplate="%{x}<br>Total: %{y:.2f}%<extra></extra>"))
    _faixas_governo(fig, periodos)
    apply_plotly_theme(fig, title="Taxa de inadimplência (%)", height=430)
    fig.update_xaxes(nticks=10, tickangle=-30)
    st.plotly_chart(fig, width="stretch")
    render_source("Banco Central — SGS 21084 (pessoas físicas) e 21082 (total). Inclui operações com recursos livres e direcionados.", SGS_URL)

    # ---------------- Médias por mandato
    st.subheader("2. Média mensal por mandato")
    b = df[df["ano"] <= 2022]
    l = df[df["ano"] >= 2023]
    linhas = [("Total da carteira", "total"), ("Pessoas físicas", "pf_total"), ("PF — recursos livres", "pf_livres"), ("PF — recursos direcionados", "pf_direcionados")]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[n for n, _ in linhas], y=[b[c].mean() for _, c in linhas], name="Bolsonaro (2019–2022)", marker_color=COLOR_BOLSONARO,
                         text=[f"{b[c].mean():.2f}%".replace(".", ",") for _, c in linhas], textposition="outside"))
    fig.add_trace(go.Bar(x=[n for n, _ in linhas], y=[l[c].mean() for _, c in linhas], name=f"Lula (2023–{rotulo_ult})", marker_color=COLOR_LULA,
                         text=[f"{l[c].mean():.2f}%".replace(".", ",") for _, c in linhas], textposition="outside"))
    fig.update_layout(barmode="group")
    apply_plotly_theme(fig, title="Inadimplência média no período (% da carteira)", height=400)
    st.plotly_chart(fig, width="stretch")
    render_source("Banco Central — SGS 21082, 21084, 21112 e 21145; média simples dos meses de cada mandato.", SGS_URL)

    st.markdown("---")

    # ---------------- Modalidades
    st.subheader("3. Onde está o atraso: modalidades de crédito de pessoas físicas")
    escolha = st.multiselect("Modalidades", [m[1] for m in MODALIDADES], default=["Cartão de crédito rotativo", "Cheque especial", "Crédito pessoal não consignado", "Aquisição de veículos"], key="inad_mod")
    fig = go.Figure()
    for col, nome, cor in MODALIDADES:
        if nome in escolha:
            fig.add_trace(go.Scatter(x=periodos, y=df[col], name=nome, mode="lines", line=dict(color=cor, width=2.5),
                                     hovertemplate="%{x}<br>" + nome + ": %{y:.2f}%<extra></extra>"))
    _faixas_governo(fig, periodos)
    apply_plotly_theme(fig, title="Inadimplência por modalidade (%)", height=450)
    fig.update_xaxes(nticks=10, tickangle=-30)
    st.plotly_chart(fig, width="stretch")
    render_source("Banco Central — SGS 21127 (rotativo), 21113 (cheque especial), 21114 (pessoal), 21121 (veículos), 21119 (consignado), 21128 (parcelado), 21151 (imobiliário) e 21148 (rural).", SGS_URL)
    st.markdown(
        '<div class="info-box"><b>Como ler:</b> a inadimplência do <b>rotativo do cartão</b> é a mais alta do sistema (66,2% em ago/2026) porque só cai nesse crédito quem já não consegue pagar a fatura inteira. '
        'O Desenrola (2023) limitou os juros do rotativo a 100% da dívida, mas a taxa de atraso seguiu em alta. '
        'O <b>imobiliário</b> e o <b>consignado</b> têm garantia (imóvel e desconto em folha) e inadimplência baixa; o imobiliário é o único em queda desde dez/2022 (1,42% ➔ 1,24%). Chama atenção o <b>crédito rural de pessoas físicas</b>, que saltou de 0,77% para 9,69% no mesmo período.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ---------------- Pessoas e famílias
    st.subheader("4. Pessoas e famílias com contas em atraso")
    st.caption("São as únicas medições que conseguimos confirmar em fonte pública. Não formam uma série contínua e mudam de metodologia entre pesquisas.")
    pontos = pd.DataFrame(extra.get("pessoas_e_familias", []))
    if not pontos.empty:
        mostrar_tabela(
            pontos[["fonte", "ponto", "valor", "detalhe", "url"]], width="stretch", hide_index=True,
            column_config={"fonte": "Pesquisa", "ponto": "Mês", "valor": "Valor", "detalhe": st.column_config.TextColumn("Observação", width="large"),
                           "url": st.column_config.LinkColumn("Fonte", display_text="abrir ↗")},
        )

    # ---------------- Programas de renegociação
    des = extra.get("desenrola", {})
    if des:
        st.subheader("5. Renegociação de dívidas: Desenrola")
        st.markdown(
            f'<div class="info-box"><b>Balanço do Desenrola:</b> {des["resumo"]}<br/>{des["desenrola_3"]}<br/>'
            f'<span style="font-size:0.8rem;">Fonte: <a href="{des["url"]}" target="_blank">{des["fonte"]}</a>. '
            'Não encontramos o balanço final de encerramento do programa; os números são parciais.</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Contexto de política: veja \"Desenrola Brasil\" na página Políticas: Impactos + e −, com a repercussão medida em pesquisa (AtlasIntel, out/2026: 67% aprovam).")
