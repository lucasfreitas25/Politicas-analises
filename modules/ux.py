"""
Apoio de experiência de uso e transparência: tipos de fonte por página, glossário central com tooltips,
impressão e modos de acessibilidade. Não depende de nenhum outro módulo do painel.
"""
import html
import re

import streamlit as st

# ---------------------------------------------------------------- tipos de fonte
TIPOS_FONTE = {
    "oficial": ("Dado oficial", "#10B981",
                "Séries e registros de órgãos públicos (IBGE, Banco Central, MTE, MDIC, Inep, Inpe, Planalto, STF, TSE). É o tipo mais confiável, mas tem defasagem e é revisado."),
    "entidade": ("Estudo de entidade", "#38BDF8",
                 "Levantamentos de entidades privadas ou não governamentais (DIEESE, FBSP, CNC, Serasa, ANTRA, SEEG, Trata Brasil, Todos Pela Educação). Metodologia da própria entidade."),
    "checagem": ("Checagem de agência", "#F59E0B",
                 "Verificações de agências de checagem (Lupa, Aos Fatos, Ranking dos Políticos, Estadão Verifica). As agências escolhem o que checar e usam escalas próprias."),
    "pesquisa": ("Pesquisa de opinião", "#A78BFA",
                 "Pesquisas de institutos como Datafolha, Quaest e AtlasIntel. Medem percepção, não fatos, e têm margem de erro."),
    "reportagem": ("Reportagem", "#94A3B8",
                   "Cobertura da imprensa de linhas editoriais variadas, usada como contraponto ou quando não há fonte primária aberta. Cada link aponta para a matéria."),
    "promessa": ("Promessa de campanha", "#EF2B2D",
                 "O que os candidatos prometem nos planos de governo. São intenções, não resultados; o texto registrado no TSE prevalece sobre qualquer resumo."),
    "curadoria": ("Cálculo do painel", "#64748B",
                  "Classificações e contas feitas por este painel (faixas Verdade/Meia-verdade/Mentira, placar de indicadores, índices, comparações alinhadas). Os critérios estão na Metodologia."),
}

PAGE_TIPOS = {
    "visao-geral": ["oficial", "entidade", "curadoria"],
    "comparador": ["oficial", "entidade", "curadoria"],
    "politicas": ["oficial", "reportagem", "pesquisa", "curadoria"],
    "checagem-eleicao-2026": ["checagem", "reportagem", "curadoria"],
    "propostas-campanha": ["promessa", "reportagem", "checagem", "oficial"],
    "trabalho": ["oficial"],
    "inflacao": ["oficial"],
    "cesta-basica": ["oficial", "entidade"],
    "inadimplencia": ["oficial", "entidade"],
    "energia-agua-esgoto": ["oficial", "entidade", "reportagem"],
    "macroeconomia": ["oficial"],
    "fiscal-social-ambiental": ["oficial"],
    "agro": ["oficial"],
    "industria": ["oficial"],
    "comercio-exterior": ["oficial"],
    "pecuaria": ["oficial"],
    "silvicultura": ["oficial"],
    "educacao": ["oficial", "entidade"],
    "saude": ["oficial", "reportagem", "curadoria"],
    "seguranca": ["entidade", "oficial", "checagem"],
    "inclusao": ["oficial", "entidade"],
    "meio-ambiente": ["oficial", "entidade", "reportagem"],
    "auditoria": ["curadoria"],
    "metodologia": ["curadoria"],
}


def render_tipos_fonte(url_path):
    tipos = PAGE_TIPOS.get(url_path or "", [])
    if not tipos:
        return
    pills = "".join(
        f'<span class="ft-pill" style="--c:{TIPOS_FONTE[t][1]};" title="{html.escape(TIPOS_FONTE[t][2], quote=True)}">{TIPOS_FONTE[t][0]}</span>'
        for t in tipos
    )
    st.markdown(f'<div class="fonte-tipos"><span class="ft-label">Tipos de fonte nesta página:</span>{pills}'
                '<span class="ft-hint">passe o mouse para ver o que cada um significa</span></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- glossário central
GLOSSARIO = {
    "SUS": "Sistema Único de Saúde: o sistema público de saúde do Brasil, gratuito e universal, financiado por União, estados e municípios.",
    "CNES": "Cadastro Nacional de Estabelecimentos de Saúde (DATASUS): registro de hospitais, postos, leitos e profissionais de saúde do país.",
    "DATASUS": "Departamento de Informática do SUS: reúne e publica os dados de saúde do Ministério da Saúde.",
    "UTI": "Unidade de Terapia Intensiva: leito para pacientes graves, com monitoramento e equipamentos especiais.",
    "OMS": "Organização Mundial da Saúde, órgão da ONU.",
    "Unicef": "Fundo das Nações Unidas para a Infância.",
    "PNI": "Programa Nacional de Imunizações, que organiza as vacinas do SUS.",
    "UPA": "Unidade de Pronto Atendimento: urgência 24 horas, entre o posto de saúde e o hospital.",
    "SAMU": "Serviço de Atendimento Móvel de Urgência: ambulâncias acionadas pelo telefone 192.",
    "Revalida": "Exame que valida no Brasil o diploma de médico formado no exterior.",
    "AMB": "Associação Médica Brasileira.",
    "CFM": "Conselho Federal de Medicina.",
    "IBGE": "Instituto Brasileiro de Geografia e Estatística: principal produtor de dados estatísticos oficiais do país.",
    "SIDRA": "Sistema IBGE de Recuperação Automática: banco de tabelas e API pública do IBGE.",
    "IPCA": "Índice Nacional de Preços ao Consumidor Amplo: a inflação oficial, calculada pelo IBGE.",
    "PNAD": "Pesquisa Nacional por Amostra de Domicílios (Contínua): mede desemprego, renda e características dos domicílios.",
    "PNADC": "Pesquisa Nacional por Amostra de Domicílios Contínua (IBGE).",
    "PIM-PF": "Pesquisa Industrial Mensal – Produção Física (IBGE): acompanha o volume produzido pela indústria.",
    "PAM": "Produção Agrícola Municipal (IBGE): área, produção e valor de culturas agrícolas.",
    "PPM": "Pesquisa da Pecuária Municipal (IBGE): rebanhos e produtos de origem animal.",
    "PEVS": "Produção da Extração Vegetal e da Silvicultura (IBGE).",
    "PRODES": "Programa do Inpe que mede o desmatamento anual por satélite (ano de agosto a julho).",
    "DETER": "Sistema do Inpe de alertas diários de desmatamento; não é a taxa oficial (PRODES).",
    "Novo CAGED": "Cadastro de empregos formais do Ministério do Trabalho (desde 2020, via eSocial). Divulga o saldo entre admissões e desligamentos.",
    "CAGED": "Cadastro Geral de Empregados e Desempregados (Ministério do Trabalho): saldo de empregos formais.",
    "MTE": "Ministério do Trabalho e Emprego.",
    "BCB": "Banco Central do Brasil.",
    "SGS": "Sistema Gerenciador de Séries Temporais do Banco Central: API pública de séries econômicas.",
    "Selic": "Taxa básica de juros da economia, definida pelo Copom do Banco Central.",
    "PTAX": "Taxa de câmbio de referência calculada pelo Banco Central (dólar).",
    "DBGG": "Dívida Bruta do Governo Geral: dívida do governo federal, estados e municípios, como % do PIB.",
    "DLSP": "Dívida Líquida do Setor Público: dívida bruta menos ativos do setor público, como % do PIB.",
    "PIB": "Produto Interno Bruto: valor de tudo o que a economia produz num período.",
    "MDIC": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (dados de comércio exterior, via Secex).",
    "ComexStat": "Sistema do MDIC/Secex com os dados oficiais de exportação e importação do Brasil, por produto, país e período.",
    "FOB": "Free on Board: valor da mercadoria no porto de embarque, sem frete e seguro. É o critério das exportações e do saldo comercial.",
    "CONAB": "Companhia Nacional de Abastecimento: acompanha as safras de grãos.",
    "Inep": "Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira.",
    "IDEB": "Índice de Desenvolvimento da Educação Básica (Inep), de 0 a 10: combina aprendizado e aprovação.",
    "Inpe": "Instituto Nacional de Pesquisas Espaciais: monitora desmatamento e queimadas por satélite.",
    "FBSP": "Fórum Brasileiro de Segurança Pública: publica o Anuário Brasileiro de Segurança Pública.",
    "MVI": "Mortes Violentas Intencionais: homicídios dolosos, latrocínios, lesões seguidas de morte e mortes por intervenção policial.",
    "CAC": "Caçadores, Atiradores e Colecionadores: categoria com regras próprias para posse de armas.",
    "SUSP": "Sistema Único de Segurança Pública.",
    "DIEESE": "Departamento Intersindical de Estatística e Estudos Socioeconômicos: faz a Pesquisa Nacional da Cesta Básica.",
    "CNC": "Confederação Nacional do Comércio de Bens, Serviços e Turismo.",
    "Peic": "Pesquisa de Endividamento e Inadimplência do Consumidor (CNC).",
    "Serasa": "Serasa Experian: bureau de crédito; publica o Mapa da Inadimplência.",
    "ANTRA": "Associação Nacional de Travestis e Transexuais: publica o dossiê anual de assassinatos de pessoas trans.",
    "SEEG": "Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa (Observatório do Clima).",
    "SNIS": "Sistema Nacional de Informações sobre Saneamento (substituído pelo SINISA em 2024).",
    "SINISA": "Sistema Nacional de Informações em Saneamento Básico.",
    "CDE": "Conta de Desenvolvimento Energético: encargo pago por todos os consumidores que financia subsídios como a tarifa social.",
    "Aneel": "Agência Nacional de Energia Elétrica: regula tarifas e bandeiras tarifárias.",
    "CadÚnico": "Cadastro Único para Programas Sociais do governo federal.",
    "BPC": "Benefício de Prestação Continuada: renda mensal de um salário mínimo a idosos e pessoas com deficiência de baixa renda.",
    "TCU": "Tribunal de Contas da União.",
    "STF": "Supremo Tribunal Federal.",
    "TSE": "Tribunal Superior Eleitoral.",
    "Ipea": "Instituto de Pesquisa Econômica Aplicada.",
    "UNODC": "Escritório das Nações Unidas sobre Drogas e Crime.",
    "EC": "Emenda Constitucional.",
    "LC": "Lei Complementar.",
    "PEC": "Proposta de Emenda à Constituição.",
    "MEI": "Microempreendedor Individual.",
    "IVA": "Imposto sobre Valor Agregado (na reforma tributária: CBS e IBS).",
    "ICMS": "Imposto sobre Circulação de Mercadorias e Serviços (estadual).",
    "IOF": "Imposto sobre Operações Financeiras.",
    "OCDE": "Organização para a Cooperação e Desenvolvimento Econômico.",
    "Gini": "Índice de 0 a 1 que mede a desigualdade de renda: quanto menor, menos desigual.",
    "ppm": "—",
    # --- leis e tributos
    "MP": "Medida Provisória: norma com força de lei editada pelo presidente, que vale por até 120 dias e precisa ser aprovada pelo Congresso.",
    "Decreto": "Ato do presidente que regulamenta uma lei ou trata da administração; não precisa passar pelo Congresso, mas não pode contrariar a lei.",
    "PDL": "Projeto de Decreto Legislativo: o Congresso usa para derrubar um decreto do presidente que passou do limite da lei.",
    "ADI": "Ação Direta de Inconstitucionalidade: pedido ao STF para derrubar uma lei ou decreto por ferir a Constituição.",
    "liminar": "Decisão provisória de um juiz, dada antes do julgamento final, para suspender algo de imediato.",
    "desoneração": "Corte ou isenção de imposto.",
    "reoneração": "Volta de um imposto que estava reduzido ou zerado.",
    "alíquota": "Percentual do imposto que incide sobre o valor (por exemplo, 20% de imposto de importação).",
    "alíquotas": "Percentuais do imposto que incidem sobre o valor.",
    "Cofins": "Contribuição para o Financiamento da Seguridade Social: tributo federal sobre o faturamento das empresas.",
    "PIS": "Programa de Integração Social: contribuição federal sobre o faturamento que financia o seguro-desemprego e o abono salarial.",
    "IPI": "Imposto sobre Produtos Industrializados: imposto federal cobrado de quem fabrica ou importa produtos industrializados.",
    "IRPF": "Imposto de Renda da Pessoa Física.",
    "CPMF": "Contribuição Provisória sobre Movimentação Financeira: o imposto do cheque, cobrado sobre cada movimentação bancária de 1997 a 2007.",
    "CIDE": "Contribuição de Intervenção no Domínio Econômico: tributo usado para corrigir ou financiar um setor (por exemplo, combustíveis).",
    "Cide": "Contribuição de Intervenção no Domínio Econômico: tributo usado para corrigir ou financiar um setor (por exemplo, combustíveis).",
    "IBS": "Imposto sobre Bens e Serviços: novo imposto de estados e municípios da reforma tributária, que substitui ICMS e ISS.",
    "CBS": "Contribuição sobre Bens e Serviços: novo tributo federal da reforma tributária, que substitui PIS e Cofins.",
    "ISS": "Imposto Sobre Serviços (municipal).",
    "Imposto Seletivo": "Imposto da reforma tributária sobre bens e serviços prejudiciais à saúde ou ao meio ambiente.",
    "GGR": "Gross Gaming Revenue: o que as casas de apostas arrecadam menos o que pagam em prêmios.",
    "come-cotas": "Cobrança antecipada de Imposto de Renda sobre fundos de investimento, feita duas vezes ao ano (maio e novembro).",
    "Zona Franca de Manaus": "Área com incentivos fiscais no Amazonas para atrair indústrias.",
    "Receita Federal": "Órgão do Ministério da Fazenda que arrecada tributos federais.",
    "Camex": "Câmara de Comércio Exterior: define alíquotas de importação e exportação.",
    "Gecex": "Comitê Executivo de Gestão da Camex: decide as alíquotas do imposto de importação.",
    "Tesouro": "Tesouro Nacional: órgão que administra as contas e a dívida do governo federal.",
    "FGTS": "Fundo de Garantia do Tempo de Serviço: reserva depositada pelo empregador na conta do trabalhador.",
    "CLT": "Consolidação das Leis do Trabalho: principal lei trabalhista do país.",
    "Fundeb": "Fundo de Manutenção e Desenvolvimento da Educação Básica: reparte recursos entre estados e municípios para a escola pública.",
    "Fundef": "Fundo do ensino fundamental (1996 a 2006), substituído pelo Fundeb.",
    "ProUni": "Programa Universidade para Todos: bolsas em faculdades particulares para estudantes de baixa renda.",
    "Enade": "Exame Nacional de Desempenho dos Estudantes: avalia cursos de graduação.",
    "Enem": "Exame Nacional do Ensino Médio.",
    "BNCC": "Base Nacional Comum Curricular: define o que todo aluno deve aprender em cada etapa.",
    "PISA": "Programa Internacional de Avaliação de Estudantes (OCDE): compara o aprendizado de jovens de 15 anos em vários países.",
    "SAEB": "Sistema de Avaliação da Educação Básica (Inep): provas que medem o aprendizado nas escolas.",
    "SNUC": "Sistema Nacional de Unidades de Conservação: regras de parques, reservas e outras áreas protegidas.",
    "PPCDAm": "Plano de Prevenção e Controle do Desmatamento na Amazônia.",
    "Ibama": "Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis: fiscaliza e multa crimes ambientais.",
    "Datafolha": "Instituto de pesquisa de opinião do grupo Folha.",
    "Quaest": "Instituto de pesquisa de opinião e eleitoral.",
    "AtlasIntel": "Instituto de pesquisa de opinião que usa coleta por internet.",
    "Atlas da Violência": "Publicação anual do Ipea e do Fórum Brasileiro de Segurança Pública com dados de homicídios no país.",
    "POF": "Pesquisa de Orçamentos Familiares (IBGE): mostra no que as famílias gastam.",
    "Mover": "Programa Mobilidade Verde e Inovação: incentivos à indústria automotiva (Lei 14.902/2024).",
    "Remessa Conforme": "Programa da Receita Federal para compras internacionais de plataformas cadastradas.",
    "Previne Brasil": "Modelo de financiamento da atenção primária do SUS criado em 2019.",
    "Mais Médicos": "Programa que leva médicos a regiões com poucos profissionais.",
    "EC 95": "Emenda Constitucional do teto de gastos (2016), que limitou o crescimento da despesa federal à inflação por 20 anos.",
    "teto de gastos": "Regra de 2016 que limitou o crescimento do gasto federal à inflação do ano anterior; substituída pelo arcabouço fiscal em 2023.",
    "arcabouço fiscal": "Regra fiscal de 2023 (LC 200) que limita o crescimento do gasto a uma parte do crescimento da receita.",
    "INSS": "Instituto Nacional do Seguro Social: paga aposentadorias e benefícios previdenciários.",
    "ONU": "Organização das Nações Unidas.",
    "Copom": "Comitê de Política Monetária do Banco Central: define a taxa Selic.",
    "ADCT": "Ato das Disposições Constitucionais Transitórias.",
}
GLOSSARIO.pop("ppm")

_PADRAO = None


def _regex():
    global _PADRAO
    if _PADRAO is None:
        termos = sorted(GLOSSARIO, key=len, reverse=True)
        _PADRAO = re.compile(r"(?<![\w\-])(" + "|".join(re.escape(t) for t in termos) + r")(?![\w\-])")
    return _PADRAO


def gl(texto_html, uma_vez=True):
    """Envolve siglas conhecidas em <abbr title='...'> (só fora de tags HTML). Cada sigla é marcada só na primeira ocorrência."""
    visto = set()

    def troca(m):
        termo = m.group(1)
        if uma_vez and termo in visto:
            return termo
        visto.add(termo)
        return f'<abbr title="{html.escape(GLOSSARIO[termo], quote=True)}">{termo}</abbr>'

    saida, ignorar = [], 0
    for p in re.split(r"(<[^>]+>)", texto_html):
        if p.startswith("<"):
            m = re.match(r"<(/?)(style|script|abbr|svg|textarea|code)\b", p, re.I)
            if m:
                ignorar = max(ignorar + (-1 if m.group(1) else 1), 0)
            saida.append(p)
        else:
            saida.append(p if ignorar else _regex().sub(troca, p))
    return "".join(saida)


def ativar_dicas_automaticas():
    """Faz todo st.markdown(..., unsafe_allow_html=True) do painel ganhar dica ao passar o mouse sobre siglas e termos do glossário."""
    if getattr(st, "_dicas_ativas", False):
        return
    original = st.markdown

    def markdown(body, *args, **kwargs):
        if kwargs.get("unsafe_allow_html") and isinstance(body, str) and "<abbr" not in body:
            try:
                body = gl(body)
            except Exception:
                pass
        return original(body, *args, **kwargs)

    st.markdown = markdown
    st._dicas_ativas = True


# ---------------------------------------------------------------- impressão e acessibilidade
def render_print_button():
    st.iframe(
        '<button onclick="window.parent.print()" style="width:100%;padding:8px 10px;border-radius:8px;border:1px solid #334155;'
        'background:#1e293b;color:#fff;font-weight:600;cursor:pointer;font-family:sans-serif;">Imprimir / salvar em PDF</button>',
        height=46,
    )


def render_acessibilidade():
    """Controles de leitura na barra lateral. Retorna nada; grava o estado em st.session_state."""
    st.caption("Leitura")
    st.toggle("Modo para daltonismo (cores e padrões)", key="modo_daltonico",
              help="Troca vermelho/azul por laranja/azul e adiciona padrões e traços diferentes em gráficos de barras e linhas.")
    if st.toggle("Tema claro (experimental)", key="tema_claro", help="Inverte as cores do painel para fundo claro. Alguns elementos podem ficar com contraste diferente."):
        st.markdown("<style>.stApp{filter:invert(1) hue-rotate(180deg);}</style>", unsafe_allow_html=True)
