import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import html
from modules.data_loader import get_scorecard
from modules.historico_ui import base, render_seletor, PADRAO, quadro_html, nomes_governos, _valor_txt, seta_txt, LEGENDA, CMP
from modules.ui_components import (
    COR_MANDATO,
    PARTIDO,
    PERIODO,
    COR_CLARA,
    render_source,
    apply_plotly_theme,
    COLOR_BOLSONARO,
    COLOR_LULA,
    COLOR_ACCENT,
    COLOR_GOLD
)

def _comparador_historico(a, b, todos):
    """Mesmo confronto frente a frente, para quaisquer dois governos (ou todos), com as cores do partido de cada presidente."""
    d = base()
    inds = {k: v for k, v in d["indicadores"].items()}
    rotulo = {f"{v['eixo']} · {v['nome']}": k for k, v in inds.items()}
    escolha = st.selectbox("Selecione o indicador para o confronto direto:", list(rotulo), index=0, key="cmp_ind_hist")
    k = rotulo[escolha]
    ind = {**inds[k], "chave": k}
    governos = nomes_governos(d)
    if a == b and not todos:
        st.info("Escolha dois governos diferentes.")
        return
    va, vb = ind["mandato"].get(a), ind["mandato"].get(b)
    venc = None
    if not todos and va is not None and vb is not None and va != vb and not ind.get("sem_lado_melhor") and k not in ("dolar", "importacoes"):
        venc = b if (vb > va) == ind["maior_melhor"] else a

    if not todos:
        col_a, col_vs, col_b = st.columns([5, 2, 5])
        for col, g in ((col_a, a), (col_b, b)):
            cor, clara = COR_MANDATO[g], COR_CLARA[g]
            selo = ('<span class="badge-winner-bols" style="font-size: 0.85rem; padding: 5px 14px;">Vantagem Estatística</span>' if venc == g
                    else '<span style="color: #94a3b8; font-size: 0.8rem;">Resultado do Período</span>')
            with col:
                st.markdown(
                    f'<div style="background: rgba(148,163,184,0.10); border: 2px solid {cor}; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
                    f'<h3 style="color: {clara}; margin-bottom: 4px; font-weight: 800;">Governo {html.escape(g)}</h3>'
                    f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 12px;">{PARTIDO[g]} · {PERIODO[g]}</p>'
                    f'<div style="font-size: 2rem; font-weight: 900; color: #ffffff; font-family: monospace;">{_valor_txt(ind, g)}</div>'
                    f'<div style="margin-top: 14px;">{selo}</div></div>', unsafe_allow_html=True)
        with col_vs:
            st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:100%;min-height:140px;font-size:2rem;font-weight:900;color:#94a3b8;">VS</div>',
                        unsafe_allow_html=True)
        if ind.get("sem_lado_melhor") or k in ("dolar", "importacoes"):
            st.info("Neste indicador não há um lado melhor (mais gasto, dólar mais alto ou mais importação não é bom nem ruim por si só); os números mostram o que aconteceu.")
        elif venc is None and (va is None or vb is None):
            st.info("Falta dado comparável para um dos governos (*): a série oficial não cobre esse período.")
        st.markdown("---")

    sel = governos if todos else [a, b]
    linhas = [(g, ind["mandato"].get(g)) for g in sel]
    fig = go.Figure(go.Bar(
        x=[g for g, _ in linhas], y=[v if v is not None else 0 for _, v in linhas],
        marker=dict(color=[COR_MANDATO[g] if v is not None else "rgba(100,116,139,0.25)" for g, v in linhas]),
        text=[_valor_txt(ind, g) for g, _ in linhas], textposition="outside",
        textfont=dict(color="#ffffff", size=13, family="Plus Jakarta Sans, sans-serif"),
        hovertemplate="<b>%{x}</b><br>%{y} " + ind["unidade"] + "<extra></extra>"))
    apply_plotly_theme(fig, title=f"Confronto numérico: {ind['nome']} ({ind['unidade']}) · {seta_txt(ind)}")
    fig.update_layout(hovermode="closest", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    simbolo, desc = CMP[ind["comparabilidade"]]
    st.markdown(
        f'<div class="info-box"><b>Análise e contexto:</b><br/>{html.escape(ind["metodo"])} {html.escape(ind.get("nota", ""))}<br/>'
        f'<b>Comparabilidade:</b> {simbolo} {html.escape(desc)}. * = dado de outra metodologia ou sem dado comparável; † = ano parcial.</div>', unsafe_allow_html=True)
    render_source(html.escape(ind["fonte"]), ind["url"])
    if todos:
        st.caption("Para ver todos os indicadores de uma vez, use a Visão Geral com \"Todos os governos\".")


def render_tab_head_to_head():
    a, b, todos = render_seletor()
    st.markdown('<div class="section-title">Comparador Direto Frente a Frente (Head-to-Head)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Escolha dois governos e qualquer indicador oficial para confrontá-los diretamente em valores absolutos e com contexto. '
        'O padrão é Bolsonaro x Lula 3; dá para comparar quaisquer mandatos desde FHC.</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="info-box"><b>Qual página usar?</b> Aqui você escolhe <b>um indicador por vez</b> e vê o confronto em detalhe. '
                'Para o panorama de todos os indicadores juntos, use a <b>Visão Geral & Scorecard</b>.</div>', unsafe_allow_html=True)
    if (a, b) != PADRAO or todos:
        _comparador_historico(a, b, todos)
        return

    scorecard_data = get_scorecard()
    indicators = scorecard_data.get("indicadores", [])

    if not indicators:
        st.warning("Indicadores não encontrados.")
        return

    ind_names = [ind["indicador"] for ind in indicators]
    ind_sel_name = st.selectbox("Selecione o Indicador para Confronto Direto:", ind_names, index=0)

    selected_ind = next(item for item in indicators if item["indicador"] == ind_sel_name)
    if selected_ind["melhor"] == "empate":
        st.info("≈ Neste indicador a diferença é pequena ou depende de contexto — nenhum dos períodos foi marcado como melhor.")

    # Layout do confronto direto
    col_b, col_vs, col_l = st.columns([5, 2, 5])
    
    with col_b:
        badge_b = '<span class="badge-winner-bols" style="font-size: 0.85rem; padding: 5px 14px;">Vantagem Estatística</span>' if selected_ind['melhor'] == 'bolsonaro' else '<span style="color: #94a3b8; font-size: 0.8rem;">Resultado do Período</span>'
        card_b = (
            f'<div style="background: rgba(37, 99, 235, 0.16); border: 2px solid #3b82f6; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
            f'<h3 style="color: #93c5fd; margin-bottom: 4px; font-weight: 800;">Governo Bolsonaro</h3>'
            f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 12px;">(2019 — 2022)</p>'
            f'<div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; font-family: monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{selected_ind["bolsonaro"]}</div>'
            f'<div style="margin-top: 14px;">{badge_b}</div>'
            f'</div>'
        )
        st.markdown(card_b, unsafe_allow_html=True)

    with col_vs:
        card_vs = (
            '<div style="display: flex; align-items: center; justify-content: center; height: 100%; min-height: 140px; font-size: 2rem; font-weight: 900; color: #94a3b8; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">'
            'VS'
            '</div>'
        )
        st.markdown(card_vs, unsafe_allow_html=True)

    with col_l:
        badge_l = '<span class="badge-winner-lula" style="font-size: 0.85rem; padding: 5px 14px;">Vantagem Estatística</span>' if selected_ind['melhor'] == 'lula' else '<span style="color: #94a3b8; font-size: 0.8rem;">Resultado do Período</span>'
        card_l = (
            f'<div style="background: rgba(220, 38, 38, 0.16); border: 2px solid #ef2b2d; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
            f'<h3 style="color: #fca5a5; margin-bottom: 4px; font-weight: 800;">Governo Lula</h3>'
            f'<p style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 12px;">(2023 — atual)</p>'
            f'<div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; font-family: monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{selected_ind["lula"]}</div>'
            f'<div style="margin-top: 14px;">{badge_l}</div>'
            f'</div>'
        )
        st.markdown(card_l, unsafe_allow_html=True)

    st.markdown("---")

    # Gráfico de barras comparativo do indicador selecionado
    b_num = selected_ind.get("bolsonaro_num")
    l_num = selected_ind.get("lula_num")
    unidade = selected_ind.get("unidade", "")

    if b_num is not None and l_num is not None:
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=["Bolsonaro (2019-2022)", "Lula (2023-atual)"],
            y=[b_num, l_num],
            marker_color=[COLOR_BOLSONARO, COLOR_LULA],
            text=[selected_ind["bolsonaro"], selected_ind["lula"]],
            textposition="outside",
            textfont=dict(color="#ffffff", size=13, family="Plus Jakarta Sans, sans-serif"),
            hovertemplate="<b>Governo:</b> %{x}<br><b>Valor:</b> %{y} " + unidade + "<extra></extra>"
        ))
        apply_plotly_theme(fig_comp, title=f"Confronto Numérico: {selected_ind['indicador']} ({unidade})")
        st.plotly_chart(fig_comp, width="stretch")

    # Detalhamento e Nota Explicativa
    st.markdown(f"""
    <div class="info-box">
      <b>Análise Oficial e Contexto Histórico:</b><br/>
      {selected_ind['observacao']}<br/>
      <span style="font-size: 0.8rem;">Fonte: <a href="{selected_ind.get('fonte_url', '#')}" target="_blank" style="color:#38bdf8;">{selected_ind.get('fonte', '—')}</a></span>
    </div>
    """, unsafe_allow_html=True)
