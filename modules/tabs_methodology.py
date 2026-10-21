import streamlit as st
import pandas as pd
import json
import os
from modules.data_loader import DATA_DIR

def render_tab_methodology():
    st.markdown('<div class="section-title">📚 Metodologia, Fontes Oficiais & Glossário</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Transparência metodológica completa, fontes primárias de dados, glossário de siglas do IBGE/Governo Federal e download dos microdados.</div>',
        unsafe_allow_html=True
    )

    # 1. Glossário de Siglas
    st.subheader("1. Glossário Completo das Siglas e Pesquisas")
    
    glossario = [
        {"Sigla": "IBGE", "Nome Completo": "Instituto Brasileiro de Geografia e Estatística", "Órgão / Descrição": "Principal provedor de dados geográficos e estatísticos oficiais do Brasil."},
        {"Sigla": "IPCA", "Nome Completo": "Índice Nacional de Preços ao Consumidor Amplo", "Órgão / Descrição": "Indicador oficial de inflação do Brasil, calculado mensalmente pelo IBGE com base no consumo de famílias com renda de 1 a 40 salários mínimos."},
        {"Sigla": "PAM", "Nome Completo": "Produção Agrícola Municipal", "Órgão / Descrição": "Pesquisa anual do IBGE que levanta área plantada, área colhida, quantidade produzida e valor da produção de 64 culturas temporárias e permanentes em todos os municípios do país."},
        {"Sigla": "CONAB", "Nome Completo": "Companhia Nacional de Abastecimento", "Órgão / Descrição": "Empresa pública vinculada ao Governo Federal que monitora as safras de grãos, estoques reguladores e abastecimento alimentar do país."},
        {"Sigla": "PEVS", "Nome Completo": "Produção da Extração Vegetal e da Silvicultura", "Órgão / Descrição": "Pesquisa anual do IBGE que quantifica a produção de florestas cultivadas (silvicultura: eucalipto, pinus, carvão, celulose) e a extração vegetal de espécies nativas (açaí, castanha, borracha)."},
        {"Sigla": "PPM", "Nome Completo": "Pesquisa da Pecuária Municipal", "Órgão / Descrição": "Pesquisa anual do IBGE sobre os efetivos da pecuária (bovinos, suínos, galináceos, ovinos) e a produção de leite, ovos de galinha, mel e lã."},
        {"Sigla": "PIM-PF", "Nome Completo": "Pesquisa Industrial Mensal - Produção Física", "Órgão / Descrição": "Pesquisa mensal do IBGE de acompanhamento do volume de produção física da indústria brasileira (extrativa e de transformação)."},
        {"Sigla": "PNADC", "Nome Completo": "Pesquisa Nacional por Amostra de Domicílios Contínua", "Órgão / Descrição": "Pesquisa contínua do IBGE que mede a taxa de desocupação, rendimento médio real habitual e massa de rendimento dos trabalhadores."},
        {"Sigla": "CAGED", "Nome Completo": "Cadastro Geral de Empregados e Desempregados (Novo CAGED)", "Órgão / Descrição": "Registro administrativo mensal do Ministério do Trabalho e Emprego (MTE) que apura admissões, desligamentos e saldo líquido de empregos com carteira assinada (CLT)."},
        {"Sigla": "BCB / SGS", "Nome Completo": "Banco Central do Brasil / Sistema Gerenciador de Séries Temporais", "Órgão / Descrição": "Autoridade monetária responsável pela taxa Selic, câmbio oficial PTAX, contas externas e dívida pública federal."},
        {"Sigla": "MDIC", "Nome Completo": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços", "Órgão / Descrição": "Responsável pelos dados de exportação, importação e superávit da balança comercial via sistema ComexStat."}
    ]

    df_glossario = pd.DataFrame(glossario)
    st.dataframe(df_glossario, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 2. Critérios Metodológicos Imparciais
    st.subheader("2. Critérios Metodológicos de Comparação")
    st.markdown("""
    <div class="kpi-card">
      <h4 style="color: #38bdf8; margin-bottom: 12px;">Diretrizes de Integridade e Rigor Estatístico:</h4>
      <ol style="color: #e2e8f0; line-height: 1.8; margin-bottom: 0;">
        <li><b>Delimitação Temporal Rigorosa:</b><br/>
          • <b>Governo Jair Bolsonaro:</b> 1º de janeiro de 2019 a 31 de dezembro de 2022 (48 meses completos).<br/>
          • <b>Governo Luiz Inácio Lula da Silva:</b> 1º de janeiro de 2023 ao presente (acompanhamento contínuo).
        </li>
        <li><b>Valores Reais Deflacionados:</b><br/>
          Séries de rendimento médio e massa salarial são expressas em valores reais (a preços constantes), corrigidas pelo IPCA acumulado, expurgando o efeito ilusório da inflação.
        </li>
        <li><b>Sem Viés Seletivo (Cherry-Picking):</b><br/>
          Todos os indicadores solicitados foram incorporados na íntegra a partir das tabelas públicas do SIDRA/IBGE e BCB SGS.
        </li>
        <li><b>Consideração de Choques Exógenos:</b><br/>
          Ambos os governos operaram sob choques globais e climáticos relevantes: a crise sanitária mundial de COVID-19 (2020-2021), a Guerra na Ucrânia e o choque de commodities/energia (2022), o fenômeno climático severo El Niño (2023-2024) e ciclos globais divergentes de juros e demanda internacional.
        </li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Download dos Dados Consolidados
    st.subheader("3. Baixar Microdados Consolidados (Exportação)")
    st.caption("Faça o download dos conjuntos de dados utilizados para auditoria ou uso em outras ferramentas analíticas (Python, Excel, R).")

    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        scorecard_path = os.path.join(DATA_DIR, "scorecard.json")
        if os.path.exists(scorecard_path):
            with open(scorecard_path, "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Baixar Scorecard Geral (JSON)",
                    data=f.read(),
                    file_name="scorecard_bolsonaro_vs_lula.json",
                    mime="application/json"
                )

    with col_d2:
        pnadc_path = os.path.join(DATA_DIR, "pnadc.json")
        if os.path.exists(pnadc_path):
            with open(pnadc_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                df_exp = pd.DataFrame(d.get("series_mensal", []))
                csv_data = df_exp.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 Baixar PNAD Contínua (CSV)",
                    data=csv_data,
                    file_name="ibge_pnadc_trabalho.csv",
                    mime="text/csv"
                )

    with col_d3:
        conab_path = os.path.join(DATA_DIR, "conab.json")
        if os.path.exists(conab_path):
            with open(conab_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                df_con = pd.DataFrame(d)
                csv_con = df_con.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 Baixar CONAB Safras (CSV)",
                    data=csv_con,
                    file_name="conab_safras_graos.csv",
                    mime="text/csv"
                )
