import html
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from modules.data_loader import load_json
from modules.historico_ui import ano_gov, governos_da_pagina
from modules.programas_ui import render_programas
from modules.ux import gl
from modules.ui_components import (
    apply_plotly_theme,
    render_section_header,
    render_source,
    render_compare_stat,
    gov_color,
    fmt_br,
    COR_MANDATO,
)

META_VACINA = 95


def _fontes_extras(lista):
    return " · ".join(f'<a href="{u}" target="_blank">{html.escape(n)} ↗</a>' for n, u in lista)


def _simples(texto):
    """Caixa 'Em palavras simples' com as siglas explicadas ao passar o mouse."""
    st.markdown(f'<div class="simples-box"><b class="rot">Em palavras simples:</b> {gl(texto)}</div>', unsafe_allow_html=True)


def _barras_por_governo(anos, valores, titulo, texto_fn=None, altura=400, eixo_y=None, parcial=()):
    """Barras por ano coloridas pelo partido do presidente da época (uma série por governo, para a legenda mostrar quem é quem)."""
    fig = go.Figure()
    grupos = {}
    escolhidos = governos_da_pagina()
    for a, v in zip(anos, valores):
        g = ano_gov(int(a))
        if g in escolhidos:
            grupos.setdefault(g, []).append((a, v))
    for g, pares in grupos.items():
        xs = [str(a) + ("*" if a in parcial else "") for a, _ in pares]
        ys = [v for _, v in pares]
        fig.add_trace(go.Bar(
            x=xs, y=ys, name=g, marker=dict(color=COR_MANDATO.get(g), pattern=dict(shape=["/" if a in parcial else "" for a, _ in pares], fgcolor="rgba(15,23,42,0.55)")),
            text=[texto_fn(v) if texto_fn else fmt_br(v) for v in ys], textposition="outside", textfont=dict(size=10),
            hovertemplate="%{x}: %{y}<extra>" + g + "</extra>"))
    apply_plotly_theme(fig, title=titulo, height=altura)
    fig.update_layout(hovermode="closest", bargap=0.25)
    fig.update_xaxes(type="category", categoryorder="category ascending")
    if eixo_y:
        fig.update_yaxes(range=eixo_y)
    return fig


def _resumo_pressa(s, d):
    med = s["medicos_por_10mil"]["serie"]
    lt = s["leitos"]["sus_por_10mil"]
    gasto = s["gasto_federal_saude"]["serie"]
    vac = s["vacinacao_oms"]["poliomielite_3_doses"]
    ev = d["expectativa_vida"]["serie"][-1]
    itens = [
        f"<b>Médicos:</b> eram {fmt_br(med['2010'], 1)} por 10 mil habitantes em 2010 e {fmt_br(med['2025'], 1)} em 2025 (CNES).",
        f"<b>Leitos do SUS para internação:</b> caíram de {fmt_br(lt['2010'], 1)} por 10 mil habitantes em 2010 para {fmt_br(lt['2019'], 1)} em 2019 e voltaram a {fmt_br(lt['2025'], 1)} em 2025.",
        f"<b>Gasto federal com saúde (valores de 2025):</b> ficou perto de R$ {fmt_br(gasto['2019']['pago_real_2025_bi'], 0)} bi em 2019, passou de R$ {fmt_br(gasto['2020']['pago_real_2025_bi'], 0)} bi na pandemia, "
        f"caiu para R$ {fmt_br(gasto['2022']['pago_real_2025_bi'], 0)} bi em 2022 e chegou a R$ {fmt_br(gasto['2025']['pago_real_2025_bi'], 0)} bi em 2025.",
        f"<b>Vacina contra a pólio:</b> cobertura de {vac['2015']:.0f}% em 2015, {vac['2021']:.0f}% em 2021 e {vac['2025']:.0f}% em 2025 (meta: {META_VACINA}%), pela estimativa da OMS.",
        f"<b>Expectativa de vida:</b> {fmt_br(ev['anos'], 1)} anos em {ev['ano']}, a maior da série do IBGE.",
    ]
    st.markdown('<div class="pressa-box"><b>Para quem tem pouco tempo</b><ul>' + "".join(f"<li>{gl(i)}</li>" for i in itens) + "</ul></div>", unsafe_allow_html=True)


def render_tab_health():
    render_section_header(
        "Saúde",
        "SUS, médicos, hospitais, vacinação, doenças e os programas de saúde de cada governo, com o que se diz de bom e as críticas. "
        "Só entram números conferidos em fonte aberta; o que falta está listado no fim da página.",
    )
    d = load_json("saude.json")
    s = load_json("saude_series.json")
    if not d or not s:
        st.warning("Base de saúde não encontrada. Rode data/_fontes/gerar_saude.py e data/_fontes/coletar_saude.py.")
        return

    _resumo_pressa(s, d)
    ev, mi, den = d["expectativa_vida"], d["mortalidade_infantil"], d["dengue"]
    ev_s, mi_s = pd.DataFrame(ev["serie"]), pd.DataFrame(mi["serie"])
    med, lt = s["medicos_por_10mil"]["serie"], s["leitos"]["sus_por_10mil"]
    gasto = s["gasto_federal_saude"]["serie"]

    # ---------------- Cartões (último ano de Bolsonaro ➔ dado mais recente)
    c1, c2, c3 = st.columns(3)
    with c1:
        render_compare_stat("Médicos por 10 mil habitantes", fmt_br(med["2022"], 1), fmt_br(med["2025"], 1), "2022 ➔ 2025 · CNES (DATASUS)", better="lula")
    with c2:
        render_compare_stat("Leitos SUS por 10 mil habitantes", fmt_br(lt["2022"], 1), fmt_br(lt["2025"], 1), "2022 ➔ 2025 · praticamente estável (CNES)")
    with c3:
        render_compare_stat("Gasto federal em saúde (R$ bi de 2025)", fmt_br(gasto["2022"]["pago_real_2025_bi"], 0), fmt_br(gasto["2025"]["pago_real_2025_bi"], 0),
                            "2022 ➔ 2025 · despesa paga (Tesouro)")
    c4, c5, c6 = st.columns(3)
    with c4:
        render_compare_stat("Expectativa de vida (anos)", fmt_br(ev_s.iloc[3]["anos"]), fmt_br(ev_s.iloc[-1]["anos"]), "2022 ➔ 2024 · IBGE (2020–21 foram anos de Covid)", better="lula")
    with c5:
        render_compare_stat("Mortalidade infantil (por mil nascidos)", fmt_br(mi_s.iloc[0]["taxa"]), fmt_br(mi_s.iloc[-1]["taxa"]), "2022 ➔ 2024 · IBGE", better="lula")
    with c6:
        vac = s["vacinacao_oms"]["poliomielite_3_doses"]
        render_compare_stat("Vacina da pólio (% de cobertura)", f"{vac['2022']:.0f}%", f"{vac['2025']:.0f}%", f"2022 ➔ 2025 · meta de {META_VACINA}% (OMS/Unicef)", better="lula")

    st.markdown("---")

    # ---------------- 1. Médicos
    st.subheader("1. Médicos")
    anos = sorted(int(a) for a in med)
    st.plotly_chart(_barras_por_governo(anos, [med[str(a)] for a in anos], "Médicos por 10 mil habitantes (cores = partido do governo)", lambda v: fmt_br(v, 1)), width="stretch")
    _simples(f"O número de médicos por habitante quase dobrou: de {fmt_br(med['2010'], 1)} por 10 mil habitantes em 2010 para {fmt_br(med['2025'], 1)} em 2025. "
             "Em números absolutos, a Demografia Médica 2025 conta 597 mil médicos em 2024, contra 304 mil em 2010. "
             "O problema é a distribuição: 48 cidades com mais de 500 mil habitantes reúnem 58% dos médicos, e têm 31% da população. "
             "Os programas que levam médicos ao interior (como o Mais Médicos) estão na seção 8.")
    st.caption(s["medicos_por_10mil"]["nota"] + " O estudo Demografia Médica 2025 (USP/AMB) conta 597.428 médicos com registro até o fim de 2024 e projeta 635.706 para o fim de 2025; "
               "as fontes divergem sobre a razão por mil habitantes (2,81 a 2,98), por isso este painel usa a série oficial do CNES, que tem a mesma metodologia em todos os anos.")
    render_source(s["medicos_por_10mil"]["fonte"] + ' · <a href="https://www.poder360.com.br/poder-saude/brasil-deve-chegar-a-635-706-medicos-em-2025/" target="_blank">Demografia Médica 2025 (Poder360) ↗</a>'
                  ' · <a href="https://futurodasaude.com.br/?p=35759" target="_blank">distribuição por cidades (Futuro da Saúde) ↗</a>',
                  s["medicos_por_10mil"]["url"])

    st.markdown("---")

    # ---------------- 2. Hospitais e leitos
    st.subheader("2. Hospitais e leitos do SUS")
    anos_l = sorted(int(a) for a in lt)
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(_barras_por_governo(anos_l, [lt[str(a)] for a in anos_l], "Leitos de internação do SUS por 10 mil habitantes", lambda v: fmt_br(v, 1), altura=380), width="stretch")
    with col_b:
        uti = s["leitos"]["uti_sus_por_10mil"]
        anos_u = sorted(int(a) for a in uti)
        st.plotly_chart(_barras_por_governo(anos_u, [uti[str(a)] for a in anos_u], "Leitos de UTI e intermediários do SUS por 10 mil habitantes", lambda v: fmt_br(v, 1), altura=380), width="stretch")
    hosp = s["hospitais_gerais"]["serie"]
    _simples(f"O Brasil foi perdendo leitos de internação do SUS em relação à população: de {fmt_br(lt['2010'], 1)} por 10 mil habitantes (2010) para {fmt_br(lt['2019'], 1)} (2019). "
             f"Na pandemia os leitos de UTI quase dobraram ({fmt_br(uti['2019'], 1)} em 2019 e {fmt_br(uti['2021'], 1)} em 2021), mas depois voltaram a cair ({fmt_br(uti['2025'], 1)} em 2025). "
             f"O número de hospitais gerais ficou perto de 5 mil a 5,5 mil ({fmt_br(hosp['2010'], 0)} em 2010 e {fmt_br(hosp['2025'], 0)} em 2025). "
             "Menos leitos por habitante não significa, por si só, pior atendimento (parte do cuidado migrou para ambulatório e atenção básica), mas mostra que a capacidade de internação não acompanhou o crescimento da população.")
    st.caption(s["leitos"]["nota"] + " " + s["hospitais_gerais"]["nota"])
    render_source(s["leitos"]["fonte"], s["leitos"]["url"])

    st.markdown("---")

    # ---------------- 3. Gasto federal
    st.subheader("3. Quanto o governo federal gasta com saúde")
    anos_g = sorted(int(a) for a in gasto)
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(_barras_por_governo(anos_g, [gasto[str(a)]["pago_real_2025_bi"] for a in anos_g], "Despesa paga da União em saúde (R$ bi, valores de 2025)",
                                            lambda v: fmt_br(v, 0), altura=400), width="stretch")
    with col_b:
        st.plotly_chart(_barras_por_governo(anos_g, [gasto[str(a)]["pago_pct_pib"] for a in anos_g], "Despesa paga da União em saúde (% do PIB)",
                                            lambda v: fmt_br(v, 2), altura=400), width="stretch")
    _simples(f"Em valores de hoje, o governo federal gastava cerca de R$ {fmt_br(gasto['2014']['pago_real_2025_bi'], 0)} bi por ano em 2014 e R$ {fmt_br(gasto['2019']['pago_real_2025_bi'], 0)} bi em 2019: ficou praticamente parado entre 2014 e 2019 "
             f"(o teto de gastos passou a valer em 2017). Subiu para R$ {fmt_br(gasto['2020']['pago_real_2025_bi'], 0)} bi na pandemia, caiu para R$ {fmt_br(gasto['2022']['pago_real_2025_bi'], 0)} bi em 2022 "
             f"e chegou a R$ {fmt_br(gasto['2025']['pago_real_2025_bi'], 0)} bi em 2025. Em proporção da economia, passou de {fmt_br(gasto['2019']['pago_pct_pib'], 2)}% do PIB (2019) para {fmt_br(gasto['2025']['pago_pct_pib'], 2)}% (2025). "
             "Atenção: é só o que a União gasta; estados e municípios também financiam o SUS, e gastar mais não garante, sozinho, um atendimento melhor.")
    st.caption(s["gasto_federal_saude"]["nota"])
    render_source(s["gasto_federal_saude"]["fonte"], s["gasto_federal_saude"]["url"])

    st.markdown("---")

    # ---------------- 4. Vacinação
    st.subheader("4. Vacinação")
    vv = s["vacinacao_oms"]
    pol, sar = vv["poliomielite_3_doses"], vv["sarampo_1_dose"]
    escolhidos = governos_da_pagina()
    anos_v = sorted(int(a) for a in pol if ano_gov(int(a)) in escolhidos)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anos_v, y=[pol[str(a)] for a in anos_v], mode="lines+markers", name="Pólio (3 doses)", line=dict(color="#38BDF8", width=3)))
    fig.add_trace(go.Scatter(x=anos_v, y=[sar[str(a)] for a in anos_v], mode="lines+markers", name="Sarampo/tríplice viral (1ª dose)", line=dict(color="#F59E0B", width=3, dash="dot")))
    fig.add_hline(y=META_VACINA, line_dash="dash", line_color="#10B981", annotation_text=f"Meta: {META_VACINA}%", annotation_position="top left", annotation_font=dict(color="#10B981"))
    for g, ini, fim in (("FHC 1", 1995, 1998), ("FHC 2", 1999, 2002), ("Lula 1", 2003, 2006), ("Lula 2", 2007, 2010), ("Dilma 1", 2011, 2014),
                        ("Dilma 2", 2015, 2015), ("Temer", 2016, 2018), ("Bolsonaro", 2019, 2022), ("Lula 3", 2023, 2025)):
        if g not in escolhidos:
            continue
        fig.add_vrect(x0=max(ini, 2000) - 0.5, x1=fim + 0.5, fillcolor=COR_MANDATO[g], opacity=0.10, line_width=0, annotation_text=g if fim >= 2000 else None,
                      annotation_position="bottom left", annotation_font=dict(size=9, color=COR_MANDATO[g]))
    apply_plotly_theme(fig, title="Cobertura vacinal no Brasil (% das crianças, estimativa OMS/Unicef)", height=440)
    fig.update_yaxes(range=[60, 102])
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    _simples(f"A meta é vacinar pelo menos {META_VACINA}% das crianças. O Brasil bateu essa marca de forma consistente até 2015 ({pol['2015']:.0f}% na pólio). Depois a cobertura despencou, até {pol['2021']:.0f}% em 2021, "
             f"e desde 2022 se recupera: {pol['2025']:.0f}% em 2025 pela estimativa da OMS. Um estudo da Confederação Nacional de Municípios concluiu que a queda não se explica só pela pandemia, porque começou em 2016. "
             "O Ministério da Saúde divulgou 95,6% na pólio em 2024 (dado parcial, até novembro), número maior que o da OMS; as duas fontes usam metodologias diferentes.")
    st.caption(vv["nota"])
    render_source(vv["fonte"], vv["url"])
    vac = d["vacinacao"]
    df_v = pd.DataFrame(vac["municipios_meta"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_v["vacina"], y=df_v["2022"], name="2022", marker_color=COR_MANDATO["Bolsonaro"], text=df_v["2022"], textposition="outside"))
    fig.add_trace(go.Bar(x=df_v["vacina"], y=df_v["2024"], name="2024", marker_color=COR_MANDATO["Lula 3"], text=df_v["2024"], textposition="outside"))
    fig.update_layout(barmode="group", bargap=0.3)
    apply_plotly_theme(fig, title="Municípios que atingiram a meta de 95% (dado do Ministério da Saúde)", height=380)
    st.plotly_chart(fig, width="stretch")
    st.caption(vac["nota"])
    render_source(vac["fonte"] + f' · <a href="{vac["url_cnm"]}" target="_blank">estudo da CNM ↗</a>', vac["url"])

    st.markdown("---")

    # ---------------- 5. Expectativa de vida e mortalidade infantil
    st.subheader("5. Quanto o brasileiro vive e quantos bebês morrem")
    col_a, col_b = st.columns(2)
    with col_a:
        ev_s = ev_s[[ano_gov(int(a)) in governos_da_pagina() for a in ev_s["ano"]]]
        fig = go.Figure(go.Scatter(x=ev_s["ano"].astype(str), y=ev_s["anos"], mode="lines+markers+text", text=[fmt_br(v) for v in ev_s["anos"]],
                                   textposition="top center", line=dict(color="#10B981", width=3),
                                   marker=dict(size=10, color=[COR_MANDATO.get(ano_gov(int(a))) for a in ev_s["ano"]])))
        apply_plotly_theme(fig, title="Expectativa de vida ao nascer (anos, IBGE)", height=380)
        fig.update_yaxes(range=[71, 78])
        st.plotly_chart(fig, width="stretch")
        st.caption(ev["nota"])
        render_source(ev["fonte"] + f' · <a href="{ev["url_2024"]}" target="_blank">2024 ↗</a>', ev["url"])
    with col_b:
        st.plotly_chart(_barras_por_governo(list(mi_s["ano"]), list(mi_s["taxa"]), "Mortalidade infantil (por mil nascidos vivos, IBGE)", lambda v: fmt_br(v, 1), altura=380, eixo_y=[0, 16]), width="stretch")
        st.caption(mi["nota"])
        render_source(mi["fonte"], mi["url"])
    _simples("A expectativa de vida é quantos anos, em média, uma criança que nasce hoje deve viver. Ela caiu em 2020 e 2021, por causa da Covid-19, e já passou do nível anterior à pandemia. "
             "A mortalidade infantil é quantos bebês morrem antes de completar 1 ano para cada mil que nascem; vem caindo devagar.")

    st.markdown("---")

    # ---------------- 6. Dengue
    st.subheader("6. Dengue: mortes por ano")
    df_d = pd.DataFrame(den["mortes"])
    par = {int(a) for a, p in zip(df_d["ano"], df_d["parcial"]) if p}
    st.plotly_chart(_barras_por_governo(list(df_d["ano"]), list(df_d["valor"]), "Mortes confirmadas por dengue (* 2025 parcial, até a 39ª semana)", lambda v: fmt_br(v, 0), parcial=par), width="stretch")
    _simples("A dengue depende muito do clima e do vírus em circulação. Em 2024, infectologistas ouvidos pela imprensa apontaram o calor, as chuvas intermitentes e o El Niño, "
             "e o Ministério da Saúde destacou o retorno do sorotipo DENV-3, contra o qual a população tinha pouca proteção; foi o maior número de casos desde o início da série, em 2000. "
             "Por isso comparar governos só pelo número de mortes diz pouco sobre a gestão.")
    st.markdown(
        f'<div class="info-box"><b>Mesma data de corte (até a 39ª semana epidemiológica):</b> 2024 teve {fmt_br(den["casos_prov_se39"]["2024"], 0)} casos prováveis e '
        f'{fmt_br(den["mortes_se39"]["2024"], 0)} mortes; 2025 teve {fmt_br(den["casos_prov_se39"]["2025"], 0)} casos e {fmt_br(den["mortes_se39"]["2025"], 0)} mortes. '
        f'{html.escape(den["nota"])}</div>', unsafe_allow_html=True)
    render_source(den["fonte"] + ". " + _fontes_extras(den["fontes_extras"]), den["url"])

    st.markdown("---")

    # ---------------- 7. Covid
    st.subheader("7. Covid-19: óbitos acumulados")
    cov = d["covid"]
    df_c = pd.DataFrame(cov["marcos"])
    fig = go.Figure(go.Bar(x=df_c["data"], y=df_c["obitos_mil"], marker_color="#94A3B8", text=[f"~{v} mil" for v in df_c["obitos_mil"]], textposition="outside"))
    apply_plotly_theme(fig, title="Óbitos acumulados por Covid-19 desde 2020 (mil)", height=380)
    fig.update_yaxes(range=[0, 800])
    st.plotly_chart(fig, width="stretch")
    st.caption(cov["nota"] + " As barras são neutras de propósito: o acumulado reúne mortes de períodos e governos diferentes.")
    render_source(cov["fonte"] + ". " + _fontes_extras(cov["fontes_extras"]), cov["url"])

    st.markdown("---")

    # ---------------- 8. Programas
    render_programas("Saúde", [g for g in governos_da_pagina() if g in ("Bolsonaro", "Lula 3")] or ["Bolsonaro", "Lula 3"])
    st.caption("Para ver os programas de outros governos, use o seletor \"Governo A x Governo B\" no topo da página. "
               "A lista completa de políticas de todas as áreas está em \"Políticas, Leis & Repercussão\"; as propostas dos candidatos de 2026 estão em \"Propostas de campanha\".")
    mm = d["mais_medicos_especialistas"]
    st.markdown(f'<div class="info-box"><b>Mais Médicos Especialistas:</b> {html.escape(mm["nota"])}</div>', unsafe_allow_html=True)
    render_source(mm["fonte"], mm["url"])

    itens = "".join(f"<li>{html.escape(p)}</li>" for p in d["pendencias"])
    st.markdown(f'<div class="info-box"><b>O que ainda não foi possível confirmar:</b><ul style="margin-bottom:0;">{itens}</ul></div>', unsafe_allow_html=True)
