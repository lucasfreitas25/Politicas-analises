import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_scorecard
from modules.ui_components import (
    render_kpi_card,
    apply_plotly_theme,
    render_section_header,
    COLOR_BOLSONARO,
    COLOR_LULA,
)

RADAR = [
    # (rótulo, indicador do scorecard, quanto maior melhor?)
    ("Crescimento do PIB", "Crescimento médio anual do PIB", True),
    ("Desemprego", "Taxa de desocupação média", False),
    ("Renda real", "Rendimento médio real habitual (fim do período)", True),
    ("Inflação", "IPCA médio anualizado", False),
    ("Juros (Selic)", "Taxa Selic média", False),
    ("Dívida bruta", "Dívida bruta do governo geral (% PIB)", False),
    ("Violência (MVI)", "Mortes violentas intencionais (total anual)", False),
    ("Pobreza", "Pobreza (linha do Banco Mundial)", False),
    ("Desmatamento", "Desmatamento na Amazônia (PRODES, média anual)", False),
]


def _radar_scores(indicadores):
    """Índice relativo: o melhor resultado recebe 100 e o outro recebe a razão entre os dois valores."""
    por_nome = {i["indicador"]: i for i in indicadores}
    labels, sb, sl = [], [], []
    for rotulo, nome, maior_melhor in RADAR:
        item = por_nome.get(nome)
        if not item:
            continue
        b, l = abs(item["bolsonaro_num"]), abs(item["lula_num"])
        if maior_melhor:
            sb.append(100 * b / max(b, l))
            sl.append(100 * l / max(b, l))
        else:
            sb.append(100 * min(b, l) / b)
            sl.append(100 * min(b, l) / l)
        labels.append(rotulo)
    return labels, sb, sl


DIRECAO_TXT = {True: "↑ maior é melhor", False: "↓ menor é melhor"}


def _classificar(indicadores):
    """Quem está melhor em cada indicador, olhando só para a direção (maior ou menor é melhor) — sem medir o tamanho da diferença."""
    linhas = []
    for i in indicadores:
        if i.get("no_grafico"):
            continue
        b = i.get("grafico_b", i["bolsonaro_num"])
        l = i.get("grafico_l", i["lula_num"])
        maior_melhor = i.get("maior_melhor", True)
        if b == l:
            continue
        lula_melhor = (l > b) if maior_melhor else (l < b)
        if i["melhor"] == "empate":
            grupo = "Depende de contexto"
        else:
            grupo = "Lula" if lula_melhor else "Bolsonaro"
        linhas.append({
            "indicador": i["indicador"], "categoria": i["categoria"], "grupo": grupo, "direcao": DIRECAO_TXT[maior_melhor],
            "valor_b": i["bolsonaro"], "valor_l": i["lula"],
        })
    return linhas


def _grafico_placar(indicadores):
    """Contagem simples: em quantos indicadores cada governo está melhor (cada indicador vale 1)."""
    linhas = _classificar(indicadores)
    if not linhas:
        return
    df = pd.DataFrame(linhas)
    total = len(df)
    n = {g: int((df["grupo"] == g).sum()) for g in ("Bolsonaro", "Depende de contexto", "Lula")}
    cor = {"Bolsonaro": COLOR_BOLSONARO, "Depende de contexto": "#64748B", "Lula": COLOR_LULA}
    rotulo = {"Bolsonaro": "Bolsonaro está melhor", "Depende de contexto": "Depende de contexto", "Lula": "Lula está melhor"}

    # (a) Placar geral: uma barra com os três grupos
    fig = go.Figure()
    for g in ("Bolsonaro", "Depende de contexto", "Lula"):
        fig.add_trace(go.Bar(
            y=["Todos os indicadores"], x=[n[g]], name=rotulo[g], orientation="h", marker_color=cor[g],
            text=[(f"{n[g]} de {total}" if n[g] >= 3 else str(n[g])) if n[g] else ""], textposition="inside", insidetextanchor="middle", textangle=0,
            textfont=dict(color="#ffffff", size=15), hovertemplate=f"{rotulo[g]}: %{{x}} indicadores<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    apply_plotly_theme(fig, title="Placar geral: em quantos indicadores cada governo está melhor", height=200)
    fig.update_layout(hovermode="closest", margin=dict(l=20, r=20, t=75, b=30), legend=dict(orientation="h", y=1.18, x=0.5, xanchor="center"))
    fig.update_xaxes(range=[0, total], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)

    # (b) Por categoria
    cats = list(dict.fromkeys(df["categoria"]))
    fig = go.Figure()
    for g in ("Bolsonaro", "Depende de contexto", "Lula"):
        xs, textos, hovers = [], [], []
        for c in cats:
            sub = df[(df["categoria"] == c) & (df["grupo"] == g)]
            xs.append(len(sub))
            textos.append(str(len(sub)) if len(sub) else "")
            hovers.append("<br>".join(f"• {t} ({d})" for t, d in zip(sub["indicador"], sub["direcao"])) or "—")
        fig.add_trace(go.Bar(
            y=cats, x=xs, name=rotulo[g], orientation="h", marker_color=cor[g], text=textos, textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=13), customdata=hovers, showlegend=False,
            hovertemplate="<b>%{y}</b><br>" + rotulo[g] + ": %{x}<br>%{customdata}<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    apply_plotly_theme(fig, title="Por categoria: quantos indicadores cada governo leva", height=max(380, 30 * len(cats) + 130))
    fig.update_layout(hovermode="closest", margin=dict(l=20, r=20, t=70, b=40))
    fig.update_xaxes(dtick=1, title="Número de indicadores", zeroline=False)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Cada indicador vale 1 ponto, e o gráfico só conta quem está melhor em cada um — já considerando que em alguns indicadores menor é melhor "
        "(desemprego, inflação, juros, dívida, mortes) e em outros maior é melhor (PIB, renda, safra, empregos). "
        "Não mede o tamanho da diferença nem o peso de cada tema, então o placar não diz quem governa melhor. "
        "\"Depende de contexto\" marca o indicador em que os números favorecem um lado, mas pandemia, ano eleitoral ou períodos de tamanhos diferentes relativizam. "
        "Para comparar períodos de 48 e 44–45 meses, acumulados viram taxa ao ano e o CAGED vira média mensal; o IPCA acumulado fica de fora para não contar duas vezes."
    )

    # (c) Quais são: lista por grupo, com a direção de cada indicador
    abas = st.tabs([f"Lula está melhor ({n['Lula']})", f"Bolsonaro está melhor ({n['Bolsonaro']})", f"Depende de contexto ({n['Depende de contexto']})"])
    for aba, g in zip(abas, ("Lula", "Bolsonaro", "Depende de contexto")):
        with aba:
            sub = df[df["grupo"] == g][["categoria", "indicador", "direcao", "valor_b", "valor_l"]].rename(columns={
                "categoria": "Categoria", "indicador": "Indicador", "direcao": "Como ler", "valor_b": "Bolsonaro (2019–22)", "valor_l": "Lula (2023–26)"})
            st.dataframe(sub, use_container_width=True, hide_index=True, height=min(80 + 36 * len(sub), 620),
                         column_config={"Indicador": st.column_config.TextColumn(width="large")})


def _celula_valor(valor, vence, lado, neutro):
    """Valor principal em destaque, detalhe entre parênteses em linha menor e selo próprio (sem quebrar ao lado do número)."""
    texto = html.escape(str(valor))
    principal, detalhe = (texto.split(" (", 1) + [""])[:2] if " (" in texto else (texto, "")
    detalhe = f"({detalhe}" if detalhe else ""
    selo = ""
    if neutro:
        selo = '<span class="mini-badge mb-tie">≈ DEPENDE</span>'
    elif vence:
        selo = f'<span class="mini-badge {"mb-lula" if lado == "lula" else "mb-bols"}">✓ MELHOR</span>'
    classe = f"val-cell {'win-' + ('l' if lado == 'lula' else 'b') if vence and not neutro else ''}"
    cor = "#93c5fd" if lado == "bolsonaro" else "#fda4af"
    return (f'<td class="{classe}"><div class="val-top">{selo}</div>'
            f'<div class="val-main" style="color:{cor};">{principal}</div>'
            f'<div class="val-detail">{detalhe}</div></td>')


def render_tab_overview():
    render_section_header(
        "Painel Executivo & Scorecard Geral",
        "Síntese dos principais indicadores dos mandatos de Jair Bolsonaro (2019–2022) e Luiz Inácio Lula da Silva (2023–2026), "
        "com dados conferidos contra as fontes oficiais em 20/10/2026.",
    )

    scorecard_data = get_scorecard()
    indicators = scorecard_data.get("indicadores", [])
    meta = scorecard_data.get("metadados", {})
    por_nome = {i["indicador"]: i for i in indicators}

    # 1. KPI Cards Grid (valores lidos do scorecard)
    destaques = [
        ("Crescimento médio do PIB", "Crescimento médio anual do PIB"),
        ("Desemprego médio", "Taxa de desocupação média"),
        ("Inflação acumulada (IPCA)", "IPCA acumulado no mandato"),
        ("Empregos formais (CAGED)", "Saldo de empregos formais (CAGED)"),
        ("Dívida bruta (% PIB)", "Dívida bruta do governo geral (% PIB)"),
        ("Selic média", "Taxa Selic média"),
    ]
    cols = st.columns(3)
    for i, (titulo, nome) in enumerate(destaques):
        item = por_nome.get(nome)
        if not item:
            continue
        with cols[i % 3]:
            render_kpi_card(title=titulo, val_bols=item["bolsonaro"], val_lula=item["lula"],
                            unit=item.get("fonte", "").split(" — ")[0], note=item["observacao"])

    vant_b = sum(1 for i in indicators if i["melhor"] == "bolsonaro")
    vant_l = sum(1 for i in indicators if i["melhor"] == "lula")
    empates = sum(1 for i in indicators if i["melhor"] == "empate")
    st.caption(
        f"Nos {len(indicators)} indicadores do scorecard: resultado mais favorável com Lula em {vant_l}, com Bolsonaro em {vant_b} "
        f"e empate/depende de contexto em {empates}. {meta.get('criterio_melhor', '')}"
    )

    st.markdown("---")

    # 2. Radar calculado a partir do scorecard
    st.subheader("Radar Comparativo (índice relativo, 0–100)")
    st.caption("Em cada eixo, o período com melhor resultado recebe 100 e o outro recebe a proporção entre os dois valores. "
               "Calculado a partir do scorecard abaixo — não há notas atribuídas à mão.")

    categories, values_bolsonaro, values_lula = _radar_scores(indicators)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values_bolsonaro + [values_bolsonaro[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Governo Bolsonaro (2019-2022)',
        line=dict(color=COLOR_BOLSONARO, width=3),
        fillcolor='rgba(59, 130, 246, 0.25)',
        hovertemplate="%{theta}: %{r:.0f}<extra>Bolsonaro</extra>"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=values_lula + [values_lula[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Governo Lula (2023-atual)',
        line=dict(color=COLOR_LULA, width=3),
        fillcolor='rgba(244, 63, 94, 0.25)',
        hovertemplate="%{theta}: %{r:.0f}<extra>Lula</extra>"
    ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0e1526",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e293b", tickfont=dict(color="#cbd5e1", size=10)),
            angularaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif"))
        ),
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor="#111827",
        height=500,
        margin=dict(l=70, r=70, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(color="#ffffff", size=12))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # 3. Placar quantitativo + tabela comparativa
    st.subheader("Tabela Comparativa Consolidada dos Indicadores")
    _grafico_placar(indicators)
    st.markdown("---")
    df_score = pd.DataFrame(indicators)

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        categorias_disponiveis = ["Todas"] + sorted(list(df_score["categoria"].unique()))
        cat_sel = st.selectbox("Filtrar por Categoria:", categorias_disponiveis, key="score_cat")
    with col_f2:
        busca = st.text_input("Buscar indicador:", "", placeholder="Ex: PIB, Selic, Desocupação, Safra...", key="score_search")

    df_filtered = df_score.copy()
    if cat_sel != "Todas":
        df_filtered = df_filtered[df_filtered["categoria"] == cat_sel]
    if busca:
        df_filtered = df_filtered[
            df_filtered["indicador"].str.contains(busca, case=False) |
            df_filtered["observacao"].str.contains(busca, case=False)
        ]

    table_rows = []
    for _, row in df_filtered.iterrows():
        neutro = row["melhor"] == "empate"
        fonte = ""
        if row.get("fonte_url"):
            fonte = f"<br/><a href='{row['fonte_url']}' target='_blank' style='color:#38bdf8; font-size:0.75rem;'>📎 {html.escape(row['fonte'])}</a>"
        maior_melhor = bool(row.get("maior_melhor", True))
        direcao = f'<div class="dir-tag {"dir-up" if maior_melhor else "dir-down"}">{DIRECAO_TXT[maior_melhor]}</div>'
        table_rows.append(
            "<tr>"
            f"<td><b style='color: #ffffff;'>{html.escape(row['categoria'])}</b></td>"
            f"<td><b style='color: #38bdf8;'>{html.escape(row['indicador'])}</b>{direcao}</td>"
            + _celula_valor(row["bolsonaro"], row["melhor"] == "bolsonaro", "bolsonaro", neutro)
            + _celula_valor(row["lula"], row["melhor"] == "lula", "lula", neutro)
            + f"<td style='color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;'>{html.escape(row['observacao'])}{fonte}</td>"
            "</tr>"
        )

    html_table = (
        '<table class="custom-table score-table">'
        '<thead><tr>'
        '<th>Categoria</th>'
        '<th>Indicador</th>'
        '<th>Governo Bolsonaro (2019-2022)</th>'
        '<th>Governo Lula (2023-atual)</th>'
        '<th>Contexto & Fonte Oficial</th>'
        '</tr></thead>'
        f"<tbody>{''.join(table_rows)}</tbody>"
        '</table>'
    )
    st.markdown(html_table, unsafe_allow_html=True)

    # 4. Box de Contexto Macroeconômico
    info_html = (
        '<div class="info-box">'
        '<b>📌 Contextualização Macroeconômica Crucial:</b><br/>'
        '• <b>Governo Bolsonaro (2019–2022):</b> Marcado pelo impacto da pandemia de COVID-19 em 2020 (PIB de -3,3%), '
        'seguida por choque inflacionário e desorganização de cadeias globais em 2021/2022 e pela deflação pontual do '
        'segundo semestre de 2022 via corte de impostos (ICMS sobre combustíveis e energia). Encerrou o mandato com mercado de trabalho em recuperação '
        '(desemprego em 7,9%), superávit primário e dívida bruta em 71,7% do PIB.<br/>'
        '• <b>Governo Lula (2023–2026):</b> Herdou Selic de 13,75% e foi impulsionado pela supersafra de 2023 e pela resiliência do emprego. '
        'Beneficiou-se de reformas prévias (Trabalhista, Previdência, Marco do Saneamento, Autonomia do BC) e recuperou o poder de compra via '
        'valorização do salário mínimo, mas enfrenta déficits primários, Selic de até 15% (2025), dívida bruta em alta '
        '(82,9% do PIB em ago/2026) e endividamento recorde das famílias.'
        '</div>'
    )
    st.markdown(info_html, unsafe_allow_html=True)
