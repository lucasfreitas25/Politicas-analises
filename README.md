# 📊 Observatório Macroeconômico: Governo Bolsonaro vs. Governo Lula

Aplicação interativa desenvolvida em **Python** e **Streamlit** para análise comparativa rigorosa e aprofundada entre os governos de **Jair Bolsonaro (2019–2022)** e o atual governo de **Luiz Inácio Lula da Silva (2023–atual)**.

A plataforma é alimentada estritamente por bases públicas oficiais do **IBGE (SIDRA)**, **CONAB**, **Banco Central do Brasil (SGS)**, **Ministério do Trabalho e Emprego (CAGED)** e **MDIC (ComexStat)**.

---

## 🏛️ Dimensões e Indicadores Oficiais Abrangidos

1. **👥 Mercado de Trabalho (PNAD Contínua - IBGE & Novo CAGED):**
   - Taxa de desocupação mensal dos trimestres móveis (Tabela 6381).
   - Rendimento médio real habitual (Tabela 6390) — poder de compra deflacionado.
   - Massa de rendimento real habitual da economia (Tabela 6392).
   - População ocupada (Tabela 6320).
   - Saldo líquido anual de postos com carteira assinada (CLT) via Novo CAGED.

2. **📈 Inflação e Preços (IPCA - IBGE & Banco Central):**
   - Série histórica do IPCA mensal e acumulado em 12 meses.
   - Curva da inflação acumulada ao longo de cada mandato (Mês 1 ao Mês 48).
   - Decomposição pelos 9 grandes grupos da cesta de consumo (Alimentação, Transportes, Habitação, etc.).

3. **🌾 Agropecuária & Grãos (PAM - IBGE & CONAB):**
   - Safras históricas de grãos CONAB (Área plantada em Mha, Produção em Mt, Produtividade em kg/ha).
   - Produção Agrícola Municipal (PAM - Tabela 1612): Soja, Milho, Arroz, Feijão, Cana-de-açúcar, Café e Algodão.

4. **🏭 Indústria (PIM-PF - IBGE):**
   - Índice de produção física industrial com ajuste sazonal (Tabela 8888).
   - Comparativo setorial: Indústria Geral vs. Indústrias Extrativas (Petróleo e Minério) vs. Indústrias de Transformação.

5. **🐄 Pecuária Municipal (PPM - IBGE):**
   - Efetivo dos rebanhos: Bovinos, Suínos e Galináceos (Tabela 3939).
   - Produção de origem animal: Leite, Ovos de galinha e Mel de abelha (Tabela 74).

6. **🌲 Silvicultura & Extrativismo (PEVS - IBGE):**
   - Silvicultura (Tabela 291): Madeira em tora para celulose e papel, Carvão vegetal e Lenha.
   - Extração vegetal nativa (Tabela 289): Açaí, Castanha-do-Pará e Erva-Mate.

7. **🏛️ Macroeconomia & Finanças (Contas Nacionais IBGE, BCB & MDIC):**
   - Crescimento anual e trimestral do PIB real (% IBGE Contas Nacionais).
   - Saldo histórico e recordes da Balança Comercial Brasileira (MDIC / ComexStat).
   - Trajetória da taxa básica de juros (Selic Meta Copom) e Câmbio PTAX (USD/BRL).
   - Dívida Bruta do Governo Geral (% PIB).

8. **⚖️ Comparador Direto Frente a Frente (Head-to-Head):**
   - Seletor interativo de confronto direto entre quaisquer métricas.
   - Radar macroeconômico multidimensional normalizado (0 a 100).

9. **📚 Metodologia, Fontes Oficiais & Glossário:**
   - Glossário detalhado de todas as siglas federais.
   - Notas metodológicas sobre choques exógenos (Pandemia, Guerra, El Niño, Ciclos de Juros).
   - Botões de exportação de dados em CSV e JSON.

10. **🗳️ Checagem de Fatos — Eleição 2026 (Lula x Flávio Bolsonaro):**
   - 261 checagens de Agência Lupa, Aos Fatos, Ranking dos Políticos e Estadão Verifica (entrevistas na TV Globo e debate da Band).
   - Agrupadas em Verdade / Meia-verdade / Mentira / Sem comprovação, com o veredito original e o link de cada checagem.
   - Visão padrão por **falas únicas**: repetições (mesma fala em várias agências ou eventos) são agrupadas — 261 checagens viram 177 falas.
   - **Contrapontos** nas falas mais disputadas: argumento do próprio candidato e de veículos com linhas editoriais diferentes (Poder360, Metrópoles, Revista Oeste, Gazeta do Povo, Instituto Mises, Agência Câmara, Datafolha/FBSP).
   - Base gerada por `data/_fontes/gerar_checagens_2026.py`.

   **📜 Políticas: Impactos + e −:** 53 políticas dos dois governos em 12 áreas, cada uma com impactos positivos, negativos, status e fonte (`data/_fontes/gerar_politicas.py`).

   **🤝 Mulheres, Raça & Minorias:** desemprego e renda por sexo e cor/raça (API do IBGE), homicídios de negros, feminicídios, assassinatos de pessoas trans e terras indígenas.

   **🌳 Meio Ambiente & Clima:** desmatamento na Amazônia e no Cerrado, queimadas, emissões (SEEG) e políticas ambientais.

11. **🧾 Fiscal, Pobreza & Meio Ambiente:** resultado primário, dívida líquida, custo dos juros (BCB), pobreza e extrema pobreza (IBGE/SIS), Gini (SIDRA 7435) e desmatamento (Inpe/PRODES).

12. **🔎 Auditoria dos Dados:** registro de cada número corrigido na revisão de 20/10/2026 (valor antigo, valor novo e fonte).

13. **📋 Propostas de campanha:** 17 temas lado a lado (Lula x Flávio), com fonte de cada ponto, contexto de dados e checagens relacionadas (`data/_fontes/gerar_propostas.py`). São promessas, não fatos.

14. **📜 Políticas, Leis & Repercussão:** além de impactos positivos e negativos, mostra o que **deixou de valer**, a **repercussão** medida em pesquisa (AtlasIntel, Datafolha, Quaest) e a lista de **leis sancionadas** conferidas no Planalto (`gerar_politicas.py`, `gerar_leis.py`).

15. **💳 Inadimplência:** só carteiras em atraso (Banco Central, série mensal por modalidade) e pontos de contas atrasadas confirmados (CNC e Serasa).

16. **🚰 Energia, Água & Esgoto:** IPCA de energia, água/esgoto e gás por mandato, bandeiras tarifárias, tarifa social e cobertura de água e esgoto (IBGE).

---

## 🧪 Bases curadas manualmente

Indicadores sem API pública estável ficam em scripts versionáveis, separados do pipeline de APIs:

```bash
python data/_fontes/gerar_bases_curadas.py      # scorecard, pobreza/desmatamento, auditoria
python data/_fontes/gerar_checagens_2026.py     # checagens da eleição 2026
python data/_fontes/gerar_politicas.py          # políticas, status e repercussão
python data/_fontes/gerar_leis.py               # leis sancionadas
python data/_fontes/gerar_propostas.py          # propostas de campanha
```

`build_database.py` lê Selic, câmbio, dívida, resultado primário, PIB, IPCA (e subitens) e Gini direto das APIs, e **não** sobrescreve o scorecard nem a base da CONAB.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado no seu sistema com as bibliotecas necessárias:
```bash
pip install streamlit pandas plotly requests openpyxl
```

### 2. Iniciar a Aplicação Streamlit
No terminal, execute:
```bash
python -m streamlit run app.py
```
Acesse no seu navegador em: `http://localhost:8501`

### 3. Sincronização em Tempo Real (Opcional)
A plataforma já vem com bases consolidadas em `data/`. Para forçar uma nova varredura em tempo real nas APIs abertas do SIDRA/IBGE e Banco Central, clique no botão **"🔄 Sincronizar Dados Oficiais (API)"** na barra lateral da aplicação ou execute:
```bash
python build_database.py
```

---

## 📂 Estrutura de Arquivos

```
Politicas analises/
├── app.py                      # Ponto de entrada da aplicação Streamlit
├── build_database.py           # Pipeline de coleta e validação das APIs oficiais
├── static/
│   └── style.css               # Folha de estilos moderna (Dark/Light executive design)
├── modules/
│   ├── data_loader.py          # Carregador cacheado de dados e interfaces
│   ├── ui_components.py        # Cards de KPI, paleta padronizada e temas Plotly
│   ├── tabs_overview.py        # Visão Geral & Scorecard
│   ├── tabs_labor.py           # Mercado de Trabalho (PNAD Contínua & CAGED)
│   ├── tabs_inflation.py       # Inflação & Preços (IPCA Geral e Grupos)
│   ├── tabs_agro_conab.py      # Agropecuária (PAM & CONAB Safras)
│   ├── tabs_industry.py        # Indústria (PIM-PF)
│   ├── tabs_livestock.py       # Pecuária (PPM)
│   ├── tabs_forestry.py        # Silvicultura & Extrativismo (PEVS)
│   ├── tabs_macro.py           # Macroeconomia (PIB, Selic, Câmbio, Balança)
│   ├── tabs_head_to_head.py    # Comparador Direto Frente a Frente
│   └── tabs_methodology.py     # Metodologia, Fontes e Glossário
└── data/                       # Armazenamento estruturado de microdados (JSON)
    ├── pnadc.json
    ├── ipca.json
    ├── pam.json
    ├── conab.json
    ├── ppm.json
    ├── pevs.json
    ├── pim.json
    ├── macro.json
    └── scorecard.json
```
