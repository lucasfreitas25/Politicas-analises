import streamlit as st
import pandas as pd
import json
import os
from modules.data_loader import DATA_DIR
from modules.ux import TIPOS_FONTE, GLOSSARIO


def _botao_arquivo(col, arquivo, rotulo, nome):
    caminho = os.path.join(DATA_DIR, arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            col.download_button(label=rotulo, data=f.read(), file_name=nome, mime="application/json", width="stretch")


def render_tab_methodology():
    st.markdown('<div class="section-title">Metodologia, Fontes & Glossário</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Como os números são escolhidos e calculados, o que o painel não consegue medir, quais tipos de fonte aparecem em cada página e como reproduzir tudo.</div>',
        unsafe_allow_html=True
    )

    # 1. Tipos de fonte
    st.subheader("1. Tipos de fonte")
    st.caption("Cada página mostra, no topo, quais destes tipos usa. Dado oficial e opinião não têm o mesmo peso, e o painel não os mistura sem avisar.")
    for chave, (rotulo, cor, desc) in TIPOS_FONTE.items():
        st.markdown(
            f'<div class="kpi-card" style="border-left:4px solid {cor};padding:10px 14px;margin-bottom:6px;"><b>{rotulo}</b><br/>'
            f'<span style="color:#cbd5e1;font-size:0.88rem;">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. Critérios
    st.subheader("2. Critérios de comparação")
    st.markdown("""
    <div class="kpi-card">
      <ol style="color: #e2e8f0; line-height: 1.8; margin-bottom: 0;">
        <li><b>Períodos.</b> Bolsonaro: 1/1/2019 a 31/12/2022 (48 meses). Lula: 1/1/2023 até o dado mais recente de cada série, então o segundo período é mais curto e muda a cada atualização.
          Por isso a Visão Geral tem o modo <b>"mesmo período"</b> (primeiros meses de cada governo, lado a lado) e a opção de ver o governo Bolsonaro sem 2020.</li>
        <li><b>Placar de indicadores.</b> Cada indicador vale um ponto para quem teve o melhor resultado, respeitando a direção (em alguns, <i>menor é melhor</i>, como desemprego e inflação). Não há pesos: um indicador de nicho vale o mesmo que o PIB. O recorte por eixo existe para isso ficar visível.</li>
        <li><b>Valores reais.</b> Rendimentos e valores em reais são deflacionados pelo IPCA quando a fonte permite; onde não, o texto avisa que o valor é nominal.</li>
        <li><b>Seleção de indicadores.</b> Entram os que têm série oficial acessível e comparável nos dois períodos. Isso <b>não é uma amostra neutra do que importa</b>: o que não tem série pública aberta (por exemplo, parte das contas de saúde e de segurança) fica de fora, e a escolha dos eixos é do painel.</li>
        <li><b>Dado ausente.</b> Quando não foi possível verificar um número na fonte primária, o painel mostra "Sem dado" em vez de estimar. As correções feitas estão na página <i>Auditoria dos Dados</i>.</li>
        <li><b>Checagens.</b> As faixas (Verdade, Meia-verdade, Mentira, entre outras) são das agências de checagem; o painel só agrupa falas repetidas, mostra contrapontos e resume. Agências escolhem o que checar, então a contagem não mede quem mente mais.</li>
        <li><b>Políticas e leis.</b> A classificação "positivo/negativo" aponta efeitos citados em fontes; a repercussão e o status ("em vigor", "revogada", "perdeu efeito") são classificações do painel com link da fonte.</li>
        <li><b>Propostas de campanha.</b> São promessas dos planos e entrevistas, não resultados. Onde só há resumo de imprensa, a fonte indicada é a reportagem, e o texto do plano registrado no TSE prevalece.</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Limites
    st.subheader("3. O que o painel não consegue medir")
    st.markdown("""
    <div class="info-box">
      <ul style="margin-bottom:0;">
        <li><b>Causalidade.</b> Os números mostram o que aconteceu durante cada governo, não o que cada governo causou. Pandemia (2020-21), guerra na Ucrânia (2022), El Niño e seca (2023-24), ciclo global de juros e heranças de gestões anteriores pesam nos dois lados.</li>
        <li><b>Defasagem e revisão.</b> Séries do IBGE, MTE e Banco Central são revisadas depois da divulgação; dados de segurança e educação saem com atraso de meses a anos.</li>
        <li><b>Mudanças de metodologia.</b> CAGED (antigo para Novo, em 2020), PNAD em modo telefone (2020-21) e SNIS para SINISA limitam comparações diretas.</li>
        <li><b>Escalas diferentes.</b> Itens como armas apreendidas e queimadas dependem de como cada órgão conta; comparar anos só vale dentro da mesma fonte.</li>
        <li><b>Eleição em andamento.</b> Checagens e propostas mudam diariamente até o 2º turno. O debate da Globo de 23/10 ainda não está refletido.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 4. Glossário (central)
    st.subheader("4. Glossário")
    busca = st.text_input("Buscar sigla ou termo", key="glos_busca", placeholder="ex.: CAGED, PRODES, Gini")
    linhas = [{"Sigla": k, "Significado": v} for k, v in sorted(GLOSSARIO.items())]
    df_glos = pd.DataFrame(linhas)
    if busca:
        mask = df_glos.apply(lambda r: busca.lower() in (r["Sigla"] + " " + r["Significado"]).lower(), axis=1)
        df_glos = df_glos[mask]
    st.dataframe(df_glos, width="stretch", hide_index=True)
    st.caption("As siglas também aparecem com explicação ao passar o mouse (sublinhado pontilhado) nos textos principais.")

    st.markdown("---")

    # 5. Reprodutibilidade
    st.subheader("5. Como reproduzir")
    st.markdown("""
    1. As séries oficiais vêm das APIs públicas do IBGE (SIDRA) e do Banco Central (SGS) e são coletadas por `build_database.py` (botão "Sincronizar" na barra lateral).
    2. Bases curadas (scorecard, políticas, leis, propostas, checagens, auditoria) são geradas pelos scripts em `data/_fontes/`, cada valor com a URL de origem no próprio arquivo.
    3. Os arquivos abaixo são exatamente os que alimentam as páginas.
    """)

    st.subheader("6. Baixar os dados")
    st.caption("Para auditoria ou uso em Python, Excel e R.")
    arquivos = [
        ("scorecard.json", "Scorecard (JSON)", "scorecard.json"),
        ("auditoria.json", "Auditoria dos dados (JSON)", "auditoria.json"),
        ("politicas.json", "Políticas (JSON)", "politicas.json"),
        ("leis_sancionadas.json", "Leis e normas (JSON)", "leis_sancionadas.json"),
        ("propostas_campanha.json", "Propostas de campanha (JSON)", "propostas_campanha.json"),
        ("checagens_2026.json", "Checagens 2026 (JSON)", "checagens_2026.json"),
    ]
    for i in range(0, len(arquivos), 3):
        cols = st.columns(3)
        for col, (arq, rot, nome) in zip(cols, arquivos[i:i + 3]):
            _botao_arquivo(col, arq, rot, nome)

    cols = st.columns(2)
    pnadc_path = os.path.join(DATA_DIR, "pnadc.json")
    if os.path.exists(pnadc_path):
        with open(pnadc_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        csv_data = pd.DataFrame(d.get("series_mensal", [])).to_csv(index=False).encode("utf-8-sig")
        cols[0].download_button("PNAD Contínua (CSV)", data=csv_data, file_name="ibge_pnadc_trabalho.csv", mime="text/csv", width="stretch")
    conab_path = os.path.join(DATA_DIR, "conab.json")
    if os.path.exists(conab_path):
        with open(conab_path, "r", encoding="utf-8") as f:
            csv_con = pd.DataFrame(json.load(f)).to_csv(index=False).encode("utf-8-sig")
        cols[1].download_button("CONAB Safras (CSV)", data=csv_con, file_name="conab_safras_graos.csv", mime="text/csv", width="stretch")
