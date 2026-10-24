# 📊 Observatório de Governos: Brasil, de FHC a Lula 3

Aplicação interativa em **Python** e **Streamlit** que reúne dados oficiais, políticas, leis e impostos de cada governo brasileiro desde **Fernando Henrique Cardoso (1995)** até o atual governo de **Lula (2023–atual)**. Em todas as páginas dá para escolher quais governos comparar; **o padrão é Bolsonaro x Lula 3**.

A plataforma é alimentada por bases públicas oficiais do **IBGE (SIDRA)**, **CONAB**, **Banco Central do Brasil (SGS)**, **Ministério do Trabalho e Emprego (CAGED)**, **MDIC (ComexStat)**, **Ipea**, **Inpe** e pelo texto das normas no **Planalto**, com checagens e estudos de terceiros sempre sinalizados.

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

## Atualização de 21/10/2026
- Tipos de fonte por página (`modules/ux.py`), glossário central e Metodologia reescrita (critérios, limites, downloads).
- Visão Geral: "Resumo em 10 números" e filtro de eixos no placar.
- Propostas de campanha: 53 trechos com página conferida nos PDFs dos planos (`data/_fontes/gerar_propostas.py`).
- Acessibilidade: modo para daltonismo, tema claro experimental, CSS para celular e impressão.

## Série histórica (22/10/2026)
- Seletor de governos no topo das abas temáticas e da Visão Geral (`modules/historico_ui.py`): padrão Bolsonaro x Lula 3 (aba original); outro par ou "Todos os governos" refaz a aba com 35 indicadores para 9 mandatos desde 1995.
- Coleta: `python data/_fontes/coletar_historico.py` (Banco Central, Ipeadata e Inpe/TerraBrasilis) gera `data/historico.json`. Ao final ele roda `alinhar_com_versao_padrao.py`, que iguala Bolsonaro e Lula 3 aos números da versão padrão de cada aba (macro, PNAD, CONAB, ComexStat); o comércio exterior de 1997–2017 vem de `coletar_comexstat_historico.py` (`data/comexstat_historico.json`).
- `python data/_fontes/coletar_filtros.py` grava em `historico_extra.json` as séries por tipo (rebanho, produto de origem animal, lavoura, silvicultura, extrativismo) usadas nos filtros das abas comparadas.
- `python data/_fontes/auditar_dados.py` confere se o mesmo ano e governo dá o mesmo número nas duas versões e se a média de cada mandato bate com os anos (sai com código 1 se houver divergência).
- PRODES atualizado pela série oficial do TerraBrasilis: 2025 consolidado = 5.731 km²; 2026 estimado = 3.335 km².

## Saúde e programas por governo (23/10/2026)
- Aba Saúde: médicos, leitos, hospitais, gasto federal, vacinação, dengue, Covid e programas de cada governo. Séries em `data/saude_series.json`
  (`python data/_fontes/coletar_saude.py`: Ipeadata/CNES, Tesouro/SICONFI e API da OMS); textos em `data/saude.json` (`gerar_saude.py`).
- `data/programas_governo.json` (`gerar_programas_governo.py`): programas de FHC a Lula 3 com pontos positivos, críticas e fonte (hoje só Saúde).

## Publicação, links e cobertura (outubro/2026)

- **Instalar:** `pip install -r requirements.txt` roda o painel; `requirements-dados.txt` inclui o necessário para os coletores em `data/_fontes/`.
- **Verificar links:** `python data/_fontes/verificar_links.py` testa todos os links do painel. Respostas 401/403/429 são só avisos (sites que bloqueiam robôs); 404 e erro de rede são listados como quebrados. Falhas isoladas de rede podem ser passageiras; rode de novo antes de concluir.
- **Programas de FHC a Temer:** `data/_fontes/programas_outras_areas.py` guarda 18 programas (Educação, Economia, Energia, Proteção Social, Segurança, Direitos, Meio Ambiente, Trabalho), cada um com benefícios, críticas e links. Rodar `gerar_programas_governo.py` regenera `programas_governo.json`.
- **Cobertura desigual:** Bolsonaro e Lula 3 têm dezenas de políticas com repercussão em pesquisas; os governos anteriores têm de 1 a 8 programas cada (Dilma 2 só 1) e não têm repercussão. A página de Políticas mostra a contagem de cada governo.

## Séries longas extras e padronização das abas (outubro/2026)

- `python data/_fontes/coletar_historico_extra.py` gera `data/historico_extra.json`, que o painel junta a `historico.json`:
  - IPCA por item e por grupo de consumo (IBGE/SIDRA 58, 655, 2938, 1419 e 7060, desde 1991): "Quanto cada item subiu" e "Decomposição do IPCA" para todos os governos;
  - cesta básica do Dieese em São Paulo (custo real e horas de trabalho, desde 1994);
  - Conab (área e produtividade dos grãos), PAM (lavouras, área e valor), PPM (rebanhos, leite, ovos e mel), PEVS (silvicultura e extração vegetal);
  - PIM-PF por seções (extrativa e transformação, desde 2002), emissões de gases de efeito estufa (Our World in Data) e destinos e pauta das exportações (ComexStat, desde 1997).
- Cada aba temática segue um molde fixo (`MOLDE` em `modules/historico_ui.py`) com as mesmas seções numeradas para qualquer par de governos; onde não há série, a seção mostra "Sem dado".
- O par escolhido fica guardado em `gov_a`/`gov_b`/`gov_todos`, separado das chaves dos campos, para não voltar a "FHC 1 x FHC 1" ao trocar de página.

## Modo celular e filtro de governos

- O painel liga o **modo celular** sozinho quando o navegador é de celular (User-Agent); o botão "Modo celular" na barra lateral força ligado ou desligado em qualquer tela. Nesse modo as tabelas largas viram cartões empilhados, os títulos de gráfico quebram em linhas, a legenda fica acima do gráfico e os gráficos de itens de preço ganham altura.
- Com "Todos os governos" ligado há o filtro **"Governos mostrados"** para tirar ou pôr cada mandato; a escolha vale para todas as abas e fica em `gov_lista`.

## Filtros dos gráficos
- Todo gráfico com tempo no eixo x passa por `filtrar_periodo` (`modules/ui_components.py`): mostra só os anos dos governos escolhidos na página e, com 4 anos ou mais, um deslizante "📅 Período" para recortar o gráfico. Gráficos sem tempo no eixo seguem como estão.
- No celular, tabelas viram cartões (40 por vez, com "Ver mais") e os vereditos por evento da checagem viram blocos com barra empilhada.
