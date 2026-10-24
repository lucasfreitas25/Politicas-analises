"""
Gera data/programas_governo.json: programas e leis de cada governo, em linguagem simples, com pontos positivos e críticas.

Regras do painel:
- só entra afirmação que apareceu em fonte citável; cada ponto leva o link da fonte;
- quando só há dado de quem fez a política (governo ou setor interessado), isso está dito no próprio texto;
- quando não achamos avaliação independente, o painel diz isso em vez de preencher.

Hoje cobre a área Saúde. A estrutura (campo "area") já aceita as demais áreas.

Execute:  python data/_fontes/gerar_programas_governo.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "programas_governo.json")
PL = "https://www.planalto.gov.br/ccivil_03/"


def p(texto, fonte, url):
    return {"texto": texto, "fonte": fonte, "url": url}


SAUDE = [
    # ------------------------------------------------------------------ FHC 1 (1995–1998)
    dict(governo="FHC 1", ano="1996", programa="Remédios gratuitos para HIV/aids",
         frase="Quem vive com HIV passou a ter direito, por lei, de receber os remédios de graça pelo SUS.",
         base=("Lei 9.313/1996", PL + "leis/l9313.htm"), situacao="Em vigor",
         bom=[p("Garantiu em lei a distribuição gratuita dos antirretrovirais a todos os portadores do HIV e doentes de aids.", "Lei 9.313/1996 (Planalto)", PL + "leis/l9313.htm"),
              p("Uma avaliação da sustentabilidade da distribuição universal aponta bom desempenho da política.", "Revista de Saúde Pública, 2006", "https://scielosp.org/pdf/rsp/2006.v40suppl0/70-79/pt")],
         ruim=[p("Os preços dos remédios novos e patenteados pesam no orçamento do SUS; movimentos sociais defendem produzir no país e quebrar patentes para depender menos das farmacêuticas.", "Outras Palavras (coluna do GTPI, 2024)", "https://outraspalavras.net/outrasaude/a-luta-contra-as-patentes-e-uma-luta-pela-vida")]),
    dict(governo="FHC 1", ano="1996", programa="CPMF, o \"imposto do cheque\" para a saúde",
         frase="Um imposto sobre cada movimentação bancária, criado para colocar mais dinheiro na saúde. Acabou em 2007.",
         base=("Lei 9.311/1996 e EC 12/1996", PL + "leis/l9311.htm"), situacao="Encerrado (2007)",
         bom=[p("Foi uma das principais tentativas de dar mais dinheiro e estabilidade ao financiamento do SUS.", "Ipea, Texto para Discussão 1846 (2013)", "https://repositorio.ipea.gov.br/bitstream/11058/1580/1/TD_1846.pdf"),
              p("Segundo o Ipea, o fim da CPMF em 2007 não prejudicou o financiamento da saúde, porque a EC 29 já tinha elevado o gasto.", "Ipea, Texto para Discussão 1846 (2013)", "https://repositorio.ipea.gov.br/bitstream/11058/1580/1/TD_1846.pdf")],
         ruim=[p("Não aumentou o orçamento do SUS na proporção do que arrecadava, porque recursos de outras fontes deixaram de ser aplicados em saúde, e parte da arrecadação passou a ter outros destinos.", "Migalhas (procuradores do RS)", "https://www.migalhas.com.br/quentes/19995/reparticao-da-arrecadacao-da-cpmf-e-determinada-pela-constituicao-federal--dizem-procuradores-do-rs")]),
    # ------------------------------------------------------------------ FHC 2 (1999–2002)
    dict(governo="FHC 2", ano="1999", programa="Lei dos Genéricos",
         frase="Criou o remédio genérico no Brasil: mesmo princípio ativo da marca, vendido mais barato.",
         base=("Lei 9.787/1999", PL + "leis/l9787.htm"), situacao="Em vigor",
         bom=[p("Os primeiros 182 registros de genéricos saíram em 2000, um ano depois da regulamentação.", "Agência Câmara", "https://www.camara.leg.br/radio/programas/reportagem-especial/555529-genericos-origem-e-questoes-legais"),
              p("Em 2025 os genéricos já respondiam por mais de 38% do mercado de medicamentos, segundo a associação do setor (PróGenéricos).", "Viva (cita a PróGenéricos)", "https://viva.com.br/saude-e-bem-estar/apos-26-anos-genericos-representam-quase-40-do-mercado-de-medicamentos.html")],
         ruim=[p("A economia de cerca de R$ 130 bilhões em 20 anos é estimativa da própria indústria de genéricos, que tem interesse no tema. Não encontramos crítica relevante nem cálculo independente nas fontes consultadas.", "Agência Câmara (cita a PróGenéricos)", "https://www.camara.leg.br/radio/programas/reportagem-especial/555529-genericos-origem-e-questoes-legais")]),
    dict(governo="FHC 2", ano="2000", programa="Dinheiro mínimo obrigatório para a saúde (EC 29)",
         frase="Obrigou União, estados e municípios a aplicar um mínimo do orçamento em saúde pública.",
         base=("Emenda Constitucional 29/2000", PL + "constituicao/emendas/emc/emc29.htm"), situacao="Em vigor (regulamentada pela LC 141/2012)",
         bom=[p("O dinheiro público aplicado em ações e serviços de saúde subiu de 2,89% do PIB em 2000 para 3,91% em 2011.", "Ipea, Texto para Discussão 1846 (2013)", "https://repositorio.ipea.gov.br/bitstream/11058/1580/1/TD_1846.pdf")],
         ruim=[p("A parte da União foi atrelada à variação nominal do PIB, regra que críticos consideram sem sustentabilidade.", "Migalhas (procuradores do RS)", "https://www.migalhas.com.br/quentes/19995/reparticao-da-arrecadacao-da-cpmf-e-determinada-pela-constituicao-federal--dizem-procuradores-do-rs"),
               p("A regulamentação só veio em 2012, com a LC 141, 12 anos depois; segundo o Ipea, o efeito poderia ter sido maior sem a demora.", "Ipea, Texto para Discussão 1846 (2013)", "https://repositorio.ipea.gov.br/bitstream/11058/1580/1/TD_1846.pdf")]),
    # ------------------------------------------------------------------ Lula 1 (2003–2006)
    dict(governo="Lula 1", ano="2004", programa="SAMU 192",
         frase="Ambulâncias com médico e enfermeiro, acionadas pelo telefone 192, para urgências em todo o país.",
         base=("Decreto 5.055/2004", PL + "_ato2004-2006/2004/decreto/d5055.htm"), situacao="Em vigor",
         bom=[p("De 2015 a 2019 a cobertura cresceu e chegou a 85% da população, segundo estudo censitário.", "Pesquisa FAPESP", "https://revistapesquisa.fapesp.br/ambulancias-do-samu-alcancam-85-da-populacao-mas-atendimento-e-desigual/")],
         ruim=[p("A cobertura é desigual: de 77,2% no Norte a 94,6% no Sul, e os 1.820 municípios sem cobertura são, em sua maioria, pequenos (51,8% têm menos de 10 mil habitantes).", "Pesquisa FAPESP", "https://revistapesquisa.fapesp.br/ambulancias-do-samu-alcancam-85-da-populacao-mas-atendimento-e-desigual/")]),
    dict(governo="Lula 1", ano="2004", programa="Farmácia Popular",
         frase="Rede de farmácias com remédios baratos ou de graça, que depois ganhou parceria com farmácias privadas.",
         base=("Lei 10.858/2004", PL + "_ato2004-2006/2004/lei/l10.858.htm"), situacao="Em vigor (ampliado em 2023 e 2025)",
         bom=[p("Autorizou a Fiocruz a vender medicamentos a preço de custo, ampliando o acesso a remédios.", "Lei 10.858/2004 (Planalto)", PL + "_ato2004-2006/2004/lei/l10.858.htm"),
              p("Em 2025 o governo atual zerou o preço dos 41 itens, o que beneficiaria mais de 1 milhão de pessoas por ano que pagavam parte do valor (estimativa do Ministério).", "Poder360", "https://www.poder360.com.br/poder-saude/governo-anuncia-gratuidade-dos-41-medicamentos-no-farmacia-popular/")],
         ruim=[p("O TCU condenou 59 empresas por irregularidades no programa em 2020; a falha mais comum foi não comprovar a compra ou o estoque dos remédios.", "TCU", "https://portal.tcu.gov.br/imprensa/noticias/tcu-identifica-irregularidades-no-programa-farmacia-popular-do-brasil"),
               p("A CGU indicou irregularidades de R$ 2,6 bilhões; os valores variam conforme a fonte e o período.", "Poder360", "https://www.poder360.com.br/poder-saude/saude/cgu-indica-irregularidades-de-r-26-bi-no-farmacia-popular/")]),
    dict(governo="Lula 1", ano="2004", programa="Brasil Sorridente",
         frase="Política de saúde bucal no SUS: equipes de dentista nos postos e centros de especialidades odontológicas.",
         base=("Lei 14.572/2023 (formalizou a política em lei)", PL + "_ato2023-2026/2023/lei/L14572.htm"), situacao="Em vigor",
         bom=[p("Nasceu do levantamento SB Brasil 2003, que mostrou muita perda de dentes. O SB Brasil 2010 apresentou melhora em relação a 2003.", "Revista Ciência Plural (UFRN), 2019", "https://periodicos.ufrn.br/rcp/article/download/16980/12233"),
              p("Um estudo do ciclo da política (2004–2016) concluiu que ela foi implementada com sucesso.", "Repositório da Enap", "https://repositorio.enap.gov.br/handle/1/3301")],
         ruim=[p("O mesmo trabalho aponta que o SB Brasil 2010 não atingiu as metas propostas e ficou abaixo do recomendado pela OMS.", "Revista Ciência Plural (UFRN), 2019", "https://periodicos.ufrn.br/rcp/article/download/16980/12233")]),
    # ------------------------------------------------------------------ Lula 2 (2007–2010)
    dict(governo="Lula 2", ano="2007", programa="Quebra de patente do remédio efavirenz (aids)",
         frase="O governo autorizou a produção de uma versão mais barata de um remédio contra a aids, sem a permissão do dono da patente.",
         base=("Licença compulsória de maio de 2007", "https://www.aidsmap.com/news/may-2007/brazil-issues-compulsory-license-efavirenz"), situacao="Concluída",
         bom=[p("Um estudo da Fiocruz de 2013 concluiu que a medida gerou economia de mais de US$ 100 milhões na compra do remédio entre 2007 e 2011, e o número de pacientes tratados subiu de 75 mil para 105 mil.", "Fiocruz (Arca)", "https://www.arca.fiocruz.br/handle/icict/24418")],
         ruim=[p("A fabricante (Merck) se disse \"profundamente decepcionada\"; críticos argumentam que quebrar patentes reduz o incentivo a pesquisar novos remédios.", "aidsmap", "https://www.aidsmap.com/news/may-2007/brazil-issues-compulsory-license-efavirenz")]),
    dict(governo="Lula 2", ano="2008", programa="UPA 24 horas",
         frase="Unidades de Pronto Atendimento: serviços de urgência 24 horas, entre o posto de saúde e o hospital.",
         base=("Portaria 1.601/2011 (diretrizes das UPAs)", "https://www.saude.mt.gov.br/storage/old/files/1601-[4733-150811-SES-MT].pdf"), situacao="Em vigor",
         bom=[p("Em municípios do Rio de Janeiro (2000–2011) houve queda significativa das mortes em hospitais (−16%) e na rua (−27%), mas sem efeito significativo na taxa geral de mortalidade, o que sugere que parte das mortes mudou de lugar.", "Ipea, Rocha e Fernandes", "https://ppe.ipea.gov.br/index.php/ppe/article/viewFile/1626/1234"),
              p("O número de unidades cresceu mais de 400% entre 2011 e 2016.", "Ciência & Saúde Coletiva, 2022", "https://scielosp.org/article/csc/2022.v27n9/3627-3636")],
         ruim=[p("Uma auditoria do TCU em Goiás encontrou 16 de 23 obras de UPAs e UBSs atrasadas, com problemas de qualidade e de acessibilidade.", "Mais Goiás (TCU)", "https://www.maisgoias.com.br/cidades/tcu-encontra-irregularidades-em-obras-de-unidades-de-saude-no-estado-de-goias/"),
               p("Há poucas pesquisas de avaliação focadas nas UPAs.", "Ciência & Saúde Coletiva, 2022", "https://scielosp.org/article/csc/2022.v27n9/3627-3636")]),
    # ------------------------------------------------------------------ Dilma 1 (2011–2014)
    dict(governo="Dilma 1", ano="2011", programa="Rede Cegonha",
         frase="Cuidado da gestante e do bebê, do pré-natal ao parto, para reduzir mortes de mães e recém-nascidos.",
         base=("Rede Cegonha (instituída em 2011); avaliação na Ciência & Saúde Coletiva, 2021", "https://scielosp.org/pdf/csc/2021.v26n3/772-772/pt"), situacao="Em vigor",
         bom=[p("Uma avaliação de 606 maternidades (2016–2017) mostrou avanços na humanização do parto.", "Ciência & Saúde Coletiva, 2021 (edição especial)", "https://scielosp.org/pdf/csc/2021.v26n3/772-772/pt"),
              p("O objetivo declarado é reduzir a mortalidade materna e neonatal por um modelo de atenção qualificado e humanizado.", "Ciência & Saúde Coletiva, 2021", "https://scielosp.org/pdf/csc/2021.v26n3/772-772/pt")],
         ruim=[p("A mesma avaliação mostra que muitos desafios permanecem; os autores apontam dificuldade de monitorar e avaliar as maternidades no dia a dia.", "Ciência & Saúde Coletiva, 2021", "https://www.scielo.br/j/csc/a/DjZVSFLg47T3vgFwYy6Mh3q/?lang=pt"),
               p("Não encontramos avaliação nacional que meça o efeito direto do programa sobre a mortalidade.", "Painel de dados (busca em fontes abertas)", "https://scielosp.org/pdf/csc/2021.v26n3/772-772/pt")]),
    dict(governo="Dilma 1", ano="2012", programa="Lei que define o que conta como gasto em saúde (LC 141)",
         frase="Regulamentou a EC 29: disse o que pode ser contado como gasto em saúde e o mínimo de cada nível de governo.",
         base=("Lei Complementar 141/2012", PL + "leis/lcp/lcp141.htm"), situacao="Em vigor (a regra do mínimo da União foi alterada pela EC 95 em 2016)",
         bom=[p("Estabeleceu regras para o que vale como gasto em ações e serviços públicos de saúde, tornando a fiscalização possível.", "LC 141/2012 (Planalto)", PL + "leis/lcp/lcp141.htm")],
         ruim=[p("Chegou 12 anos depois da EC 29; segundo o Ipea, o efeito poderia ter sido maior sem a demora.", "Ipea, Texto para Discussão 1846 (2013)", "https://repositorio.ipea.gov.br/bitstream/11058/1580/1/TD_1846.pdf")]),
    dict(governo="Dilma 1", ano="2013", programa="Mais Médicos",
         frase="Levou médicos, brasileiros e estrangeiros (muitos de Cuba), para cidades pequenas e periferias sem médico.",
         base=("Lei 12.871/2013", PL + "_ato2011-2014/2013/lei/l12871.htm"), situacao="Alterado (reformulado em 2019 e 2023)",
         bom=[p("Um estudo de economistas da FGV, com 2.940 municípios, encontrou queda de 4,6% nas internações e de 5,9% nas internações por doenças infecciosas em 2015; a economia equivaleria a um terço do orçamento do programa.", "Band B (estudo da FGV)", "https://www.bandab.com.br/politica/como-mais-medicos-economizou-um-terco-do-orcamento-ao-diminuir-internacoes-hospitalares/amp/"),
              p("Uma pesquisa da UnB, com mais de 570 estudos, calculou economia de R$ 30 milhões em 10 anos com internações evitáveis (número bem menor que o da FGV; a fonte não explica a diferença).", "Brasil de Fato (pesquisa da UnB)", "https://www.brasildefato.com.br/2024/01/05/mais-medicos-resulta-em-economia-de-r-30-milhoes-em-internacoes-no-sus")],
         ruim=[p("O CFM e a AMB foram ao STF contra o programa e criticaram a entrada de médicos sem prova de competência técnica (Revalida). Segundo o CFM, o pedido foi rejeitado pelo plenário.", "Conselho Federal de Medicina", "https://portal.cfm.org.br/artigos/criticas-ao-mais-medicos/"),
               p("O acordo com Cuba acabou em 2018, por divergência sobre o Revalida; o relator no STF entendia que os cubanos deveriam receber o valor integral, e não só uma parte.", "Poder360 e CFM", "https://www.poder360.com.br/governo/cfm-defende-revalida-como-condicao-para-permanencia-de-medicos-cubanos/")]),
    # ------------------------------------------------------------------ Temer (2016–2018)
    dict(governo="Temer", ano="2016", programa="Teto de gastos (EC 95) e a saúde",
         frase="Congelou, por 20 anos, o gasto federal total, corrigido só pela inflação, e fixou o mínimo da saúde no valor de 2017.",
         base=("Emenda Constitucional 95/2016", PL + "constituicao/emendas/emc/emc95.htm"), situacao="Substituída pelo novo regime fiscal em 2023 (LC 200/2023)",
         bom=[p("Objetivo declarado: conter o crescimento da despesa e estabilizar a dívida pública. O programa \"Uma Ponte para o Futuro\" já propunha um limite para as despesas de custeio.", "Uma Ponte para o Futuro (PMDB, 2015), p. 18", "https://www.epsjv.fiocruz.br/sites/default/files/files/ponteparaofuturo.pdf")],
         ruim=[p("Entidades da reforma sanitária e o Conselho Nacional de Saúde estimaram perda de R$ 22,5 bilhões para o SUS entre 2018 e 2020.", "Entidades da Reforma Sanitária (CNS, Cebes)", "https://cebes.org.br/site/wp-content/uploads/2020/04/Entidades-da-Reforma-Sanitaria-contra-a-EC-95.pdf"),
               p("A Associação Brasileira de Economia da Saúde estimou R$ 36,9 bilhões de perda entre 2018 e 2022, sem contar os créditos da Covid. Todas essas estimativas vêm de quem critica o teto e usam períodos e bases diferentes.", "Esther Dweck, Carta Capital (cita a ABrES)", "https://www.ie.ufrj.br/images/IE/IEnaMidia/2022/09/Esther%20Dweck,%20Carta%20Capital,%2006%20de%20Setembro%20de%202022.pdf")]),
    dict(governo="Temer", ano="2017", programa="Nova Política Nacional de Atenção Básica",
         frase="Mudou as regras dos postos de saúde e das equipes de Saúde da Família, flexibilizando a composição das equipes.",
         base=("Portaria 2.436/2017", "https://cdr.saude.sp.gov.br/wp-content/uploads/2022/09/PORTARIA-No-2.436-DE-21-DE-SETEMBRO-DE-2017.pdf"), situacao="Em vigor (alterada depois)",
         bom=[p("Passou a reconhecer e financiar outros tipos de equipes além da Saúde da Família tradicional.", "Ciência & Saúde Coletiva, 2020", "https://scielosp.org/pdf/csc/2020.v25n4/1327-1338/pt")],
         ruim=[p("O Conselho Nacional de Saúde recomendou a revogação da portaria em outubro de 2017, por não terem sido apresentados os impactos assistenciais e financeiros.", "Conselho Nacional de Saúde, Recomendação 051/2017", "https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/recomendacoes/2017/recomendacao-no-051.pdf"),
               p("Uma dissertação da UERJ (2021) sustenta que a portaria enfraqueceu a universalidade, a integralidade e a participação popular no SUS.", "UERJ (dissertação, 2021)", "https://www.bdtd.uerj.br:8443/bitstream/1/17668/2/Disserta%c3%a7%c3%a3o%20-%20Amanda%20Firme%20Carletto%20-%202021%20-%20Completa.pdf")]),
    # ------------------------------------------------------------------ Bolsonaro (2019–2022)
    dict(governo="Bolsonaro", ano="2019", programa="Previne Brasil",
         frase="Mudou a forma de repassar dinheiro da atenção básica aos municípios: parte por número de pessoas cadastradas e parte por desempenho.",
         base=("Previne Brasil (Portaria 2.979/2019), descrito na Ciência & Saúde Coletiva, 2020", "https://scielosp.org/pdf/csc/2020.v25n4/1189-1196/pt"), situacao="Segundo artigo recente, substituído por novo modelo federal em 2024",
         bom=[p("O cadastro de pessoas na atenção básica subiu 26% depois do anúncio do programa, de 81 para 103 milhões.", "Ciência & Saúde Coletiva, 2020", "https://scielosp.org/pdf/csc/2020.v25n4/1189-1196/pt")],
         ruim=[p("Estudos apontam desafios com as desigualdades regionais e a garantia de cobertura universal, e perdas financeiras em alguns municípios por causa do cálculo por população cadastrada.", "Repositório AEDB (revisão da literatura)", "https://repositorio.aedb.br/jspui/bitstream/123456789/210/1/Previne%20Brasil%20-%20avan%c3%a7os%20e%20retrocessos%20no%20financiamento%20da%20sa%c3%bade%20p%c3%bablica.pdf")]),
    dict(governo="Bolsonaro", ano="2019", programa="Médicos pelo Brasil",
         frase="Programa criado para substituir o Mais Médicos, com uma agência própria (Adaps) para contratar médicos para a atenção básica.",
         base=("Lei 13.958/2019", PL + "_ato2019-2022/2019/lei/L13958.htm"), situacao="Em vigor",
         bom=[p("Nos primeiros nove meses, o programa teve cerca de 23 mil médicos interessados, 97,1% de ocupação das vagas e 95,4% de permanência. Os autores do estudo são ligados à própria Adaps.", "Ciência & Saúde Coletiva, 2023", "https://scielosp.org/pdf/csc/2023.v28n11/3273-3279/pt")],
         ruim=[p("Foi anunciado em 2019, mas só fez a primeira chamada em 2022; pouco menos de 5 mil vagas foram preenchidas. Críticos falam em privatização da atenção básica.", "Outras Palavras", "https://outraspalavras.net/outrasaude/os-esquecidos-do-medicos-pelo-brasil/"),
               p("Com a saída dos cubanos, 8.157 postos ficaram vagos, muitos em áreas de difícil acesso.", "O Povo (2021)", "https://www.opovo.com.br/noticias/politica/2021/12/27/apos-3-anos-gestao-bolsonaro-tenta-efetivar-substituto-do-mais-medicos.html")]),
    dict(governo="Bolsonaro", ano="2020–2022", programa="Resposta à pandemia de Covid-19",
         frase="Quatro ministros da Saúde, divergências sobre tratamentos e compra de vacinas a partir do fim de 2020.",
         base=("Relatório final da CPI da Pandemia (Senado, 26/10/2021)", "https://www12.senado.leg.br/radio/1/noticia/2021/10/26/com-pedido-de-indiciamento-de-bolsonaro-cpi-aprova-relatorio-final"), situacao="Encerrado",
         bom=[p("O governo contratou a CoronaVac em janeiro de 2021 e outras vacinas, e o SUS aplicou centenas de milhões de doses.", "Ministério da Saúde (dados citados no painel)", "https://www12.senado.leg.br/radio/1/noticia/2021/10/26/com-pedido-de-indiciamento-de-bolsonaro-cpi-aprova-relatorio-final")],
         ruim=[p("A CPI da Pandemia aprovou em 26/10/2021, por 7 votos a 4, um relatório que pediu o indiciamento de Bolsonaro e outras 79 pessoas e empresas, entre elas por atraso na compra de vacinas.", "Agência Senado (Rádio Senado)", "https://www12.senado.leg.br/radio/1/noticia/2021/10/26/com-pedido-de-indiciamento-de-bolsonaro-cpi-aprova-relatorio-final"),
               p("O país passou de 700 mil mortes por Covid-19 em março de 2023, como mostra o gráfico desta página.", "Ministério da Saúde, via imprensa", "https://www.jornalopcao.com.br/ultimas-noticias/covid-19-brasil-encerra-ano-com-7-675-973-casos-e-193-875-mortes-304598/")]),
    dict(governo="Bolsonaro", ano="2022", programa="Piso salarial da enfermagem",
         frase="Lei que criou um salário mínimo nacional para enfermeiros, técnicos e auxiliares de enfermagem.",
         base=("Lei 14.434/2022", PL + "_ato2019-2022/2022/lei/L14434.htm"), situacao="Em vigor, com assistência financeira da União (suspensa pelo STF em 2022 antes disso)",
         bom=[p("Fixou piso de R$ 4.750 para enfermeiros, 70% disso para técnicos e 50% para auxiliares.", "Istoé Dinheiro", "https://istoedinheiro.com.br/barroso-suspende-lei-que-estabelece-piso-para-profissionais-da-enfermagem"),
              p("O Cofen disse que os estudos de impacto foram apresentados à União, estados e municípios; o então ex-ministro Alexandre Padilha afirmou que o custo não passa de 3% do que o sistema público gasta.", "Istoé Dinheiro", "https://istoedinheiro.com.br/barroso-suspende-lei-que-estabelece-piso-para-profissionais-da-enfermagem")],
         ruim=[p("O novo regime fiscal (LC 200/2023) prevê assistência financeira da União aos fundos de saúde de estados e municípios para cumprirem o piso dos enfermeiros, técnicos e auxiliares, o que mostra que o piso segue valendo. A data em que a suspensão acabou não foi verificada aqui.", "LC 200/2023 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp200.htm"),
               p("Em setembro de 2022 o ministro Barroso suspendeu a lei, por risco de demissões em massa e fechamento de leitos; uma pesquisa citada na decisão indicou que 51% das instituições reduziriam leitos e 77% reduziriam a equipe.", "Istoé Dinheiro", "https://istoedinheiro.com.br/barroso-suspende-lei-que-estabelece-piso-para-profissionais-da-enfermagem")]),
    # ------------------------------------------------------------------ Lula 3 (2023–)
    dict(governo="Lula 3", ano="2023", programa="Retomada do Mais Médicos",
         frase="O governo relançou o Mais Médicos em março de 2023, com novas vagas e a formação de especialistas.",
         base=("Lei 14.621/2023", PL + "_ato2023-2026/2023/lei/L14621.htm"), situacao="Em vigor",
         bom=[p("Segundo o Ministério da Saúde, os médicos em atuação passaram de 13,7 mil para 27,3 mil entre 2023 e 2025 (alta de 99%). É número do próprio governo.", "Poder360 (dados do Ministério da Saúde)", "https://www.poder360.com.br/poder-saude/mais-medicos-amplia-em-99-quantidade-de-profissionais-em-3-anos/")],
         ruim=[p("Entidades médicas dizem que faltam condições de trabalho que façam o profissional ir e ficar em regiões remotas; segundo levantamento do Ministério, 41% dos participantes de edições anteriores desistiram por falta de perspectiva profissional.", "Futuro da Saúde", "https://futurodasaude.com.br/novo-mais-medicos/embed/")]),
    dict(governo="Lula 3", ano="2025", programa="Farmácia Popular 100% gratuita",
         frase="Desde fevereiro de 2025, os 41 remédios do programa são de graça.",
         base=("Programa Farmácia Popular do Brasil", "https://www.poder360.com.br/poder-saude/governo-anuncia-gratuidade-dos-41-medicamentos-no-farmacia-popular/"), situacao="Em vigor",
         bom=[p("A gratuidade é considerada acerto por 89% dos entrevistados, a medida mais aprovada do governo na pesquisa.", "AtlasIntel/Bloomberg, via InfoMoney (out/2026)", "https://www.infomoney.com.br/politica/farmacia-popular-e-a-medida-mais-aprovada-do-governo-lula-aponta-atlasintel/")],
         ruim=[p("Há denúncias de fraudes no programa: o Ministério informou, entre jan/2023 e set/2024, 1.238 farmácias suspensas e 363 descredenciadas (dados do governo).", "CNN Brasil", "https://www.cnnbrasil.com.br/nacional/governo-amplia-farmacia-popular-em-meio-a-denuncias-de-fraudes-no-programa/"),
               p("O TCU apontou desigualdade: em municípios com menos de 40 mil habitantes, o programa chegava a 58,7% da população no Nordeste e a 33,2% no Norte.", "TCU (via Gazeta do Povo)", "https://www.gazetadopovo.com.br/economia/tcu-alertou-sobre-fraudes-no-programa-farmacia-popular-rombo-de-r-25-bilhoes/")]),
    dict(governo="Lula 3", ano="2023", programa="Movimento Nacional pela Vacinação",
         frase="Campanha para recuperar a vacinação infantil, que vinha caindo desde 2016.",
         base=("Ministério da Saúde", "https://www.jornalopcao.com.br/saude/ministerio-da-saude-celebra-crescimento-da-cobertura-vacinal-infantil-662512/"), situacao="Em andamento",
         bom=[p("Até 30/11/2024 a 1ª dose da tríplice viral chegou a 95,69% e a pólio oral a 95,58% (meta de 95%), dados parciais do Ministério.", "Jornal Opção (dados do Ministério da Saúde)", "https://www.jornalopcao.com.br/saude/ministerio-da-saude-celebra-crescimento-da-cobertura-vacinal-infantil-662512/"),
              p("Os municípios na meta passaram de 855 (2022) para 2.408 (2024) na 2ª dose da tríplice viral.", "Medicina S/A (dados do Ministério da Saúde)", "https://medicinasa.com.br/?p=127059")],
         ruim=[p("Um estudo da CNM concluiu que, em 2024, só a BCG e a 1ª dose da tríplice viral bateram a meta, e que a pólio não atinge 95% desde 2016.", "Confederação Nacional de Municípios (CNM)", "https://cnm.org.br/biblioteca/download/16281"),
               p("Em 2023, menos de 20% da população vivia em municípios que atingiram a meta da pólio.", "Anuário VacinaBR (IQC/Unicef)", "https://www.unicef.org/brazil/comunicados-de-imprensa/brasil-vive-crise-prolongada-na-vacinacao-infantil-apesar-de-melhora-em-2023-mostra-anuario-vacinabr")]),
]


def main():
    itens = []
    for i, x in enumerate(SAUDE, start=1):
        itens.append({
            "id": f"saude-{i}", "area": "Saúde", "governo": x["governo"], "ano": x["ano"], "programa": x["programa"], "em_uma_frase": x["frase"],
            "base_legal": {"nome": x["base"][0], "url": x["base"][1]}, "situacao": x["situacao"], "beneficios": x["bom"], "criticas": x["ruim"],
        })
    payload = {
        "metadados": {
            "atualizado_em": "2026-10-23",
            "aviso": "A lista é uma seleção dos programas mais conhecidos, não o conjunto completo, e governos sem item (por exemplo Dilma 2) ainda não foram mapeados nesta área.",
            "areas": ["Saúde"],
        },
        "programas": itens,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(len(itens), "programas gravados em", OUT)


if __name__ == "__main__":
    main()
