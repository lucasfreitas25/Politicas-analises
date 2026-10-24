import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import get_educacao_data, load_json
from modules.ui_components import (
    render_compare_stat,
    fmt_br,
    render_source,
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def render_tab_education():
    st.markdown('<div class="section-title">Educação & Capital Humano</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Avaliação do IDEB (Inep), taxa de analfabetismo (IBGE PNAD Contínua), orçamento federal executado pelo MEC e programas estruturais (Novo Fundeb, Pé-de-Meia).</div>',
        unsafe_allow_html=True
    )

    df_ideb, df_analf, df_orc, programas = get_educacao_data()
    edu = load_json("educacao.json")

    # 1. Cards de Destaque (valores lidos da base)
    col1, col2, col3 = st.columns(3)
    if not df_ideb.empty:
        ini = df_ideb[df_ideb["governo"] == "Bolsonaro"].iloc[-1]
        fim = df_ideb.iloc[-1]
        with col1:
            render_compare_stat("IDEB do ensino médio", fmt_br(ini["ensino_medio"]), fmt_br(fim["ensino_medio"]),
                                f"{int(ini['ano'])} ➔ {int(fim['ano'])} · escala de 0 a 10 (Inep)", better="lula")
    if not df_analf.empty:
        a22 = df_analf[df_analf["ano"] == 2022].iloc[0]
        a_ult = df_analf.iloc[-1]
        with col2:
            render_compare_stat("Taxa de analfabetismo (15+ anos)", f"{fmt_br(a22['taxa_analfabetismo_15mais'])}%", f"{fmt_br(a_ult['taxa_analfabetismo_15mais'])}%",
                                f"2022 ➔ {int(a_ult['ano'])} · IBGE PNAD Contínua (SIDRA 7113)", better="lula")
    if not df_orc.empty:
        o22 = df_orc[df_orc["ano"] == 2022].iloc[0]
        o_ult = (df_orc[~df_orc["parcial"].eq(True)] if "parcial" in df_orc else df_orc).iloc[-1]
        with col3:
            render_compare_stat("Orçamento pago do MEC (R$ bi de dez/2024)", fmt_br(o22["orcamento_pago"]), fmt_br(o_ult["orcamento_pago"]),
                                f"2022 ➔ {int(o_ult['ano'])} · deflacionado pelo IPCA (Todos Pela Educação e Portal da Transparência)", better="lula")

    st.markdown("---")

    # 2. Gráfico do IDEB
    st.subheader("1. Evolução do IDEB por Etapa de Ensino (Inep / MEC)")
    st.caption("Índice de Desenvolvimento da Educação Básica (escala de 0 a 10).")

    if not df_ideb.empty:
        fig_ideb = go.Figure()
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["anos_iniciais"],
            name="Anos Iniciais (1º ao 5º ano)",
            marker_color="#38bdf8",
            text=df_ideb["anos_iniciais"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["anos_finais"],
            name="Anos Finais (6º ao 9º ano)",
            marker_color="#10b981",
            text=df_ideb["anos_finais"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.add_trace(go.Bar(
            x=df_ideb["ano"].astype(str),
            y=df_ideb["ensino_medio"],
            name="Ensino Médio",
            marker_color="#f59e0b",
            text=df_ideb["ensino_medio"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color="#ffffff", size=11)
        ))
        fig_ideb.update_layout(barmode="group")
        apply_plotly_theme(fig_ideb, title="IDEB Nacional por Ciclo de Ensino")
        st.plotly_chart(fig_ideb, width="stretch")
        render_source("Inep — " + edu.get("nota_ideb", "Ideb nacional"), edu.get("fonte_ideb"))

    # 3. Analfabetismo e Orçamento em duas colunas
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("Taxa de Analfabetismo (%) — IBGE")
        st.caption("Pessoas de 15 anos ou mais de idade que não sabem ler e escrever.")
        if not df_analf.empty:
            colors_analf = [
                COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
                for g in df_analf["governo"]
            ]
            fig_analf = go.Figure()
            fig_analf.add_trace(go.Scatter(
                x=df_analf["ano"].astype(str),
                y=df_analf["taxa_analfabetismo_15mais"],
                mode="lines+markers+text",
                marker=dict(size=8, color="#34d399"),
                line=dict(color="#10b981", width=3),
                text=df_analf["taxa_analfabetismo_15mais"].apply(lambda v: f"{v:.1f}%"),
                textposition="top center",
                textfont=dict(color="#ffffff", size=11),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Analfabetismo:</b> %{y:.1f}%<extra></extra>"
            ))
            apply_plotly_theme(fig_analf, title="Taxa de Analfabetismo Nacional (%)")
            st.plotly_chart(fig_analf, width="stretch")
            render_source(edu.get("nota_analfabetismo", "IBGE, PNAD Contínua Educação (SIDRA 7113)"), "https://sidra.ibge.gov.br/tabela/7113")

    with col_e2:
        st.subheader("Orçamento Executado do MEC (R$ bi)")
        st.caption("Volume financeiro total pago pelo Ministério da Educação. * 2026 é parcial (em execução) e está em valor corrente.")
        if not df_orc.empty:
            colors_orc = [
                COLOR_BOLSONARO if g == "Bolsonaro" else (COLOR_LULA if g == "Lula" else "#64748b")
                for g in df_orc["governo"]
            ]
            parcial = df_orc["parcial"].eq(True) if "parcial" in df_orc else pd.Series(False, index=df_orc.index)
            fig_orc = go.Figure()
            fig_orc.add_trace(go.Bar(
                x=[f"{a}*" if p_ else str(a) for a, p_ in zip(df_orc["ano"], parcial)],
                y=df_orc["orcamento_pago"],
                marker=dict(color=colors_orc, pattern=dict(shape=["/" if p_ else "" for p_ in parcial], fgcolor="rgba(255,255,255,0.55)")),
                text=[f"{v:.1f}".replace(".", ",") for v in df_orc["orcamento_pago"]],
                textposition="outside",
                textfont=dict(color="#ffffff", size=11),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Orçamento Pago:</b> R$ %{y:.1f} bilhões<extra></extra>"
            ))
            apply_plotly_theme(fig_orc, title="Orçamento Anual Pago do MEC (R$ Bilhões)")
            st.plotly_chart(fig_orc, width="stretch")
            render_source(edu.get("nota_orcamento", "Anuário Brasileiro da Educação Básica, Todos Pela Educação"), edu.get("fonte_orcamento"))
            dot = edu.get("orcamento_atualizado_portal")
            if dot:
                a, b = dot["serie"][0], dot["serie"][-1]
                st.markdown(
                    '<div class="kpi-card compare-stat" style="border-top:3px solid #EF2B2D;"><div class="compare-title">Orçamento atualizado do MEC (dotação, R$ correntes)</div>'
                    f'<div class="compare-values"><span class="compare-val" style="color:#fca5a5 !important;">R$ {fmt_br(a["bi"])} bi</span><span style="color:#64748b;"> ➔ </span>'
                    f'<span class="compare-val" style="color:#fca5a5 !important;">R$ {fmt_br(b["bi"])} bi</span></div>'
                    f'<div class="compare-foot">{a["ano"]} ➔ {b["ano"]} (em execução) · não é despesa paga</div></div>', unsafe_allow_html=True)
                render_source(dot["nota"], dot["url"])

    # ---------------- Dados mais recentes (PISA, ICA, Censo Escolar, Pé-de-Meia)
    mais = load_json("educacao.json")
    st.markdown("---")
    st.subheader("2. Aprendizado: PISA 2025 (divulgado em setembro/2026)")
    pisa = mais.get("pisa")
    if pisa:
        df_p = pd.DataFrame(pisa["serie"])
        fig_pisa = go.Figure()
        for col, nome, cor in (("leitura", "Leitura", "#38bdf8"), ("matematica", "Matemática", "#F59E0B"), ("ciencias", "Ciências", "#10b981")):
            fig_pisa.add_trace(go.Bar(x=df_p["ano"].astype(str), y=df_p[col], name=nome, marker_color=cor, text=df_p[col], textposition="outside"))
        fig_pisa.update_layout(barmode="group", bargap=0.3)
        apply_plotly_theme(fig_pisa, title="Nota média do Brasil no PISA (pontos)", height=470)
        fig_pisa.update_yaxes(range=[300, 440])
        st.plotly_chart(fig_pisa, width="stretch")
        o = pisa["ocde_2025"]
        st.caption(f"Média da OCDE em 2025: leitura {o['leitura']}, matemática {o['matematica']}, ciências {o['ciencias']}. " + pisa["nota"])
        render_source(pisa["fonte"], pisa["url"])

    st.subheader("3. Alfabetização na idade certa e escola em tempo integral")
    ica = mais.get("alfabetizacao_ica")
    cen = mais.get("censo_escolar")
    c1, c2, c3 = st.columns(3)
    if ica:
        s_ica = ica["serie"]
        with c1:
            st.markdown(
                '<div class="kpi-card compare-stat" style="border-top:3px solid #EF2B2D;"><div class="compare-title">Crianças alfabetizadas no 2º ano (ICA)</div>'
                f'<div class="compare-values"><span class="compare-val" style="color:#fca5a5 !important;">{s_ica[0]["pct"]}%</span><span style="color:#64748b;"> ➔ </span>'
                f'<span class="compare-val" style="color:#fca5a5 !important;">{s_ica[-1]["pct"]}%</span></div>'
                f'<div class="compare-foot">{s_ica[0]["ano"]} ➔ {s_ica[-1]["ano"]} · meta de 2025: 64% · só governo Lula (medido desde 2023)</div></div>', unsafe_allow_html=True)
    if cen:
        ti, net = cen["tempo_integral_publica_pct"], cen["escolas_com_internet_pct"]
        with c2:
            render_compare_stat("Rede pública em tempo integral (% das matrículas)", f"{fmt_br(ti['2021'])}%", f"{fmt_br(ti['2025'])}%", "2021 ➔ 2025 · Censo Escolar (Inep)", better="lula")
        with c3:
            render_compare_stat("Escolas com internet (%)", f"{fmt_br(net['2021'])}%", f"{fmt_br(net['2025'])}%", "2021 ➔ 2025 · Censo Escolar (declaratório)", better="lula")
        fl = cen["ensino_medio_publico_2022_2025"]
        st.markdown(
            f'<div class="info-box"><b>Ensino médio público, 2022 ➔ 2025 (variação relativa, Censo Escolar):</b> abandono {fl["abandono"]}%, reprovação {fl["reprovacao"]}%, '
            f'distorção idade-série {fl["distorcao_idade_serie"]}%. {cen["nota_fluxo"]} '
            f'Matrículas totais da educação básica: {fmt_br(cen["matriculas_2024_mi"])} mi (2024) ➔ {fmt_br(cen["matriculas_2025_mi"])} mi (2025). {cen["nota"]}</div>',
            unsafe_allow_html=True)
        render_source(cen["fonte"], cen["url"])
    pdm = mais.get("pe_de_meia")
    if pdm:
        st.markdown(f'<div class="info-box"><b>Pé-de-Meia:</b> {pdm["nota"]}</div>', unsafe_allow_html=True)
        render_source(pdm["fonte"], pdm["url"])
    if ica:
        render_source(ica["fonte"] + ". " + ica["nota"], ica["url"])

    if mais.get("pendencias"):
        itens = "".join(f"<li>{p_}</li>" for p_ in mais["pendencias"])
        st.markdown(f'<div class="info-box"><b>O que ainda não foi possível confirmar:</b><ul style="margin-bottom:0;">{itens}</ul></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 4. Programas Estruturantes de Impacto
    st.subheader("Principais Políticas Educacionais de Cada Mandato")
    for prog in programas:
        tag_color = "#3b82f6" if prog["governo"] == "Bolsonaro" else "#ef2b2d"
        card_prog = (
            f'<div class="kpi-card" style="margin-bottom: 16px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
            f'<h4 style="color: #ffffff; margin: 0;">{prog["programa"]}</h4>'
            f'<span style="background: {tag_color}; color: #ffffff; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">'
            f'Governo {prog["governo"]}'
            f'</span>'
            f'</div>'
            f'<p style="color: #cbd5e1; font-size: 0.88rem; margin-bottom: 10px;">{prog["descricao"]}</p>'
            f'<div style="background: rgba(16, 185, 129, 0.12); border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">'
            f'<b style="color: #34d399;">Impacto Positivo:</b> <span style="color: #e2e8f0; font-size: 0.85rem;">{prog["pontos_positivos"]}</span>'
            f'</div>'
            f'<div style="background: rgba(239, 68, 68, 0.12); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px;">'
            f'<b style="color: #f87171;">Desafios / Críticas Oficiais:</b> <span style="color: #e2e8f0; font-size: 0.85rem;">{prog["criticas"]}</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_prog, unsafe_allow_html=True)
