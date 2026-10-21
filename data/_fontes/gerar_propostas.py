"""
Gera data/propostas_campanha.json: propostas dos programas de governo de Lula (PT) e Flávio Bolsonaro (PL)
na eleição presidencial de 2026, por tema.

IMPORTANTE: são PROMESSAS de campanha, não fatos. Os textos oficiais registrados no TSE prevalecem sobre
qualquer resumo. As propostas vêm de reportagens que resumem os planos; quando só um resumo de terceiro
(com apoio de IA) cobre um ponto, isso está sinalizado. Quando uma fonte não menciona um tema, escrevemos
"não consta nas fontes consultadas" — o que NÃO prova que o plano seja omisso.

Execute:  python data/_fontes/gerar_propostas.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "propostas_campanha.json")

FONTES = {
    "cef": ("Congresso em Foco (14/08/2026)", "https://www.congressoemfoco.com.br/noticia/121276/fim-da-6x1-soberania-e-seguranca-o-plano-de-lula-para-novo-mandato"),
    "eml": ("Estado de Minas (31/08/2026)", "https://www.em.com.br/politica/2026/08/7490597-lula-2026-conheca-as-propostas-do-candidato-a-presidencia.html"),
    "forbes": ("Forbes Brasil (06/10/2026)", "https://forbes.com.br/forbes-money/2026/10/o-que-lula-quer-manter-e-mudar-na-economia-em-um-novo-mandato/"),
    "abl": ("Agência Brasil (18/09/2026)", "https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/lula-propoe-criar-ministerio-da-seguranca-e-aumento-real-do-minimo"),
    "efl": ("Estado de Minas (31/08/2026)", "https://www.em.com.br/politica/2026/08/7490602-flavio-bolsonaro-2026-conheca-as-principais-propostas-do-plano-de-governo.html"),
    "abf": ("Agência Brasil (18/09/2026)", "https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/flavio-bolsonaro-propoe-enxugar-estado-e-endurecer-acoes-de-seguranca"),
    "pg": ("planodegoverno2026.com.br — resumo de terceiro com apoio de IA, citando páginas do plano", "https://planodegoverno2026.com.br/candidatos/presidente/flavio-bolsonaro/"),
    "afl": ("Aos Fatos — entrevista de Flávio na Globo (16/10/2026)", "https://www.aosfatos.org/noticias/checamos-flavio-bolsonaro-globo-segundo-turno/"),
    "p360": ("Poder360 — íntegra do plano", "https://www.poder360.com.br/poder-flash/leia-a-integra-do-plano-de-governo-de-flavio-bolsonaro/"),
}

AUSENTE = "Não consta nas fontes consultadas."

# (tema, lula[(texto, fonte)], flavio[(texto, fonte)], nota de contexto, verificação)
TEMAS = [
    ("Economia e contas públicas",
     [("Manter o arcabouço fiscal e buscar \"redução sustentada das taxas de juros\" com inflação controlada.", "cef"),
      ("Reindustrialização com a Nova Indústria Brasil (crédito, compras públicas e incentivos) e processamento de minerais críticos e terras raras.", "cef"),
      ("Combater privilégios e distorções tributárias.", "cef")],
     [("\"Tesouraço\": corte de gastos e de pelo menos dez ministérios, com novas regras fiscais, superávit primário e queda da dívida/PIB para derrubar os juros.", "pg"),
      ("Conter o crescimento da folha de pagamento e digitalizar os serviços públicos.", "efl"),
      ("Priorizar recursos para saúde, educação e infraestrutura básica (sem valores).", "efl")],
     "Hoje: dívida bruta em 82,9% do PIB (ago/2026) e Selic em 13,75% (out/2026), segundo o Banco Central.",
     "Lula: \"orçamento com superávit é inédito\" foi classificado como falso pelo Ranking dos Políticos."),
    ("Impostos",
     [("Manter a isenção do IR até R$ 5 mil, compensada pela tributação de super-ricos, fundos exclusivos e offshore: \"colocar o pobre no orçamento e o rico no Imposto de Renda\".", "eml"),
      ("Isentar a cesta básica de tributos.", "abl"),
      ("Promete \"justiça tributária\" sem listar quais benefícios cortaria nem quanto arrecadaria.", "forbes")],
     [("Revisar a reforma tributária para reduzir o IVA (projetado em torno de 30%, contra 19% da média da OCDE) e cortar exceções.", "pg"),
      ("Reduzir tributos sobre energia elétrica e combustíveis.", "abf"),
      ("Fim gradual do IOF sobre câmbio e desoneração de exportações; \"menos impostos\" condicionado ao corte de gastos.", "pg")],
     "A isenção do IR até R$ 5 mil já está em vigor (Lei 15.270/2025). A reforma tributária do consumo tem transição até 2033.",
     ""),
    ("Estatais e privatizações",
     [("Petrobras volta à distribuição de combustíveis, amplia a capacidade de refino e a Transpetro ganha papel em logística de GNL.", "cef"),
      (AUSENTE + " (privatizações).", "eml")],
     [("Retomar o programa nacional de privatizações \"com critério\", caso a caso; estatais comandadas por recrutamento de mercado, com a Lei das Estatais fortalecida; a Caixa vira \"Banco da Prosperidade\".", "pg"),
      ("Acelerar concessões e parcerias privadas em saneamento.", "abf"),
      ("A campanha hoje promete não privatizar Petrobras, Banco do Brasil nem Caixa.", "afl")],
     "Em fev/2026, Flávio disse planejar \"privatizar 95%\" das estatais; em set/2026 a equipe disse que o BB estava em estudo, e depois a campanha negou os planos.",
     "Aos Fatos (16/10): ao chamar de \"terrorismo\" a acusação de privatização, Flávio omitiu falas anteriores suas."),
    ("Trabalho e renda",
     [("Fim da escala 6x1 e jornada de 40 horas semanais sem redução salarial (PEC aprovada no Senado, aguarda promulgação).", "cef"),
      ("Combater a \"pejotização espúria\"; regras para trabalhadores de aplicativo (remuneração, proteção previdenciária, transparência de algoritmos); planos de ação onde houver diferença salarial entre homens e mulheres.", "cef"),
      ("Aumento do salário mínimo sempre acima da inflação.", "abl")],
     [("Reduzir gradualmente o custo de contratar \"sem retirar direitos\", com contratos mais baratos para 18 a 24 anos e desempregados com mais de 50.", "pg"),
      ("Negociado sobre o legislado; manter o modelo atual de trabalho por aplicativo, com proteção previdenciária; banco nacional de vagas.", "pg"),
      ("A escala 6x1 não é tratada no resumo do plano. " + "Críticas à \"República Sindical\".", "pg")],
     "A PEC do 6x1 foi aprovada no Senado por 75 votos a 1 em 14/10/2026 (apoio de governo e oposição).",
     ""),
    ("Programas sociais",
     [("Manter e aprimorar o Bolsa Família; ampliar o Gás do Povo (Auxílio Gás) e o Minha Casa, Minha Vida.", "eml")],
     [("Manter os programas atuais, com combate a fraudes e retorno imediato ao benefício se o emprego não der certo.", "pg"),
      ("Proibir o uso do dinheiro de programas sociais em apostas online; programa \"Ganha, Ganha\" (juros menores e cashback via Caixa para quem conclui curso ou paga contas em dia).", "pg"),
      ("Vale para pagar creche privada; relançar o Casa Verde e Amarela, com meta de 2,5 milhões de moradias.", "abf")],
     "O piso do Bolsa Família sobe de R$ 600 para R$ 691 em out/2026 (reajuste de 15,04%).",
     ""),
    ("Saúde",
     [("Ampliar o Farmácia Popular com exames laboratoriais de diagnóstico e acompanhamento (hipertensão e diabetes).", "abl"),
      ("\"A maior rede pública de cuidado ao câncer do mundo\", com investimento em diagnóstico, equipamentos e medicamentos.", "abl"),
      ("Acelerar o prontuário único do cidadão e ampliar a IA no SUS para triagem e regulação.", "cef")],
     [("Prontuário eletrônico único ligado ao CPF, integrando rede pública e privada; IA para agendar consultas e exames na primeira vaga livre.", "pg"),
      ("Contratar a rede privada em horários ociosos; remédios em casa para idosos e crônicos; correção da tabela do SUS; produção nacional de vacinas e telessaúde.", "pg"),
      ("Manter a imunização; atendimento por telefone ou aplicativo onde faltam médicos.", "abf")],
     "O prontuário eletrônico já existe como Rede Nacional de Dados em Saúde (criada em 2020, com mais de 5 bilhões de registros).",
     "Aos Fatos: a promessa de Flávio de criar um prontuário único é de algo que \"já existe\"."),
    ("Educação",
     [("80% das crianças alfabetizadas na idade certa; ampliar o ensino em tempo integral e consolidar o Pé-de-Meia.", "cef"),
      ("Ampliar as creches e expandir os institutos federais, priorizando o interior e as periferias.", "abl")],
     [("Alfabetização pelo método fônico, com repasses atrelados a metas; programa Acolher (alunos de bom desempenho pagos para reforçar colegas).", "pg"),
      ("\"Escola sem doutrinação\"; mais escolas cívico-militares; vouchers para escolas e creches privadas onde faltar vaga pública.", "pg"),
      ("Ensino superior passa do MEC para o Ministério da Ciência e Tecnologia; escola nas férias; ensino técnico com o setor produtivo.", "abf")],
     "O programa federal de escolas cívico-militares foi encerrado em 2023; estados mantêm modelos próprios.",
     ""),
    ("Segurança pública",
     [("Criar o Ministério da Segurança Pública (o Congresso em Foco o condiciona à aprovação da PEC da Segurança; a Agência Brasil não cita a condição).", "cef"),
      ("R$ 10 bilhões para estados e municípios; fortalecer as FICCOs e asfixiar as finanças de facções e milícias; Pacto Nacional de Execução Penal; ampliar câmeras corporais.", "cef"),
      ("Regulamentar o SUSP e dar centralidade ao trabalho de inteligência.", "eml")],
     [("Declarar PCC, CV e milícias \"organizações narcoterroristas\"; cinco presídios federais de segurança máxima e meio milhão de vagas em quatro anos.", "pg"),
      ("Reduzir a maioridade penal: de 18 para 14 anos em crimes graves, segundo a Agência Brasil; o resumo de terceiro fala em 16 anos — as fontes divergem.", "abf"),
      ("Fim da progressão de regime para hediondos; castração química para estupradores condenados; 1 milhão de câmeras com reconhecimento facial e tropa militar nas fronteiras e portos.", "pg"),
      ("Mais segurança jurídica para os agentes em operações e direito dos cidadãos à legítima defesa.", "efl")],
     "Mortes violentas caíram para 19,1 por 100 mil em 2025 (menor taxa desde 2012), mas 19% da população vive em bairros com facções e milícias (Datafolha/FBSP, jun/2026).",
     "Flávio: \"com Lula a criminalidade explodiu\" foi classificado como falso por Lupa e Aos Fatos."),
    ("Armas",
     [("Manter os controles atuais de armas e munições, sem outros detalhes nas fontes.", "cef")],
     [("O resumo do plano não trata de posse, porte ou regras de armas.", "pg"),
      ("Cita o direito dos cidadãos à legítima defesa.", "efl")],
     "O acervo de CACs passou de ~350 mil para mais de 1 milhão de armas em 2019–2022; o decreto de 2023 reverteu a flexibilização.",
     "Aos Fatos: a legítima defesa está no Código Penal, não na Constituição."),
    ("Meio ambiente e clima",
     [("\"Desmatamento líquido zero até 2030\" em todos os biomas; ampliar o monitoramento por satélite e IA contra crimes ambientais.", "cef"),
      ("Liderar a transição energética.", "eml")],
     [("Zerar o desmatamento ilegal até 2029, com satélite e IA contra grilagem e garimpo; consolidar o mercado regulado de carbono e pagar por serviços ambientais.", "pg"),
      ("Flexibilizar o licenciamento, inclusive com autolicenciamento quando o órgão não decide no prazo; acabar com sobreposições entre Ibama e Funai.", "abf"),
      ("Ampliar a produção de petróleo e gás, inclusive com fraturamento hidráulico (fracking).", "abf"),
      ("Exigir transparência de ONGs financiadas do exterior.", "pg")],
     "Desmatamento na Amazônia: 5.796 km² em 2025 (menor em 11 anos); no Cerrado, 7.235 km². A Lei 15.190/2025 já flexibilizou o licenciamento.",
     ""),
    ("Energia e combustíveis",
     [("Ampliar a exploração de petróleo e gás junto com a transição; leilões de transmissão, baterias, modernização de hidrelétricas, hidrogênio de baixo carbono e biocombustíveis.", "cef"),
      ("Tarifas mais baixas aparecem como debate do próximo mandato, sem medida ou meta.", "forbes")],
     [("Reduzir tributos sobre energia elétrica e combustíveis; acelerar mineração com mais capital estrangeiro.", "abf"),
      ("Meta de estar entre os principais destinos de investimento em transição energética até 2030.", "pg")],
     "O IPCA de energia elétrica residencial subiu 30,5% de jan/2023 a set/2026, contra 12,5% de 2019 a 2022.",
     ""),
    ("Infraestrutura, saneamento e moradia",
     [("Novo PAC (obras públicas e concessões), com mais projetos de aeroportos, ferrovias e portos.", "forbes"),
      ("Expandir o Minha Casa, Minha Vida.", "eml"),
      ("Saneamento: " + AUSENTE.lower(), "eml")],
     [("R$ 900 bilhões em infraestrutura, majoritariamente privados (concessões, PPPs e fundo lastreado em imóveis da União).", "pg"),
      ("Universalizar água e esgoto até 2033 e \"nenhuma escola sem água\" até 2030; Casa Verde e Amarela com 2,5 milhões de moradias.", "pg")],
     "Cobertura de esgoto adequado: 71,4% dos domicílios em 2025 (IBGE). O Trata Brasil estima que a meta legal de 2033 não será cumprida no ritmo atual.",
     ""),
    ("Agro e indústria",
     [("Apoiar o agro exportador e a agricultura familiar; reindustrialização com a Nova Indústria Brasil e estímulo a setores de alta tecnologia.", "eml")],
     [("Não consta proposta específica para o agro nas fontes consultadas.", "pg"),
      ("Desoneração de exportações e abertura comercial gradual, com integração às cadeias globais de valor.", "pg")],
     "Safra de grãos de 2025/26: 361,7 milhões de toneladas (Conab, set/2026).",
     ""),
    ("Política externa e soberania",
     [("Política externa \"universalista\": mais acordos comerciais, BRICS, Sul Global e Mercosul; reforma de ONU, OMC, FMI e Banco Mundial; mercado comum de energia na América do Sul.", "cef"),
      ("Soberania como eixo (energia, minerais, digital); cita \"três ondas de tarifaços\" de Trump.", "cef"),
      ("Modernizar as Forças Armadas, reforçar o controle de fronteiras e proteger recursos minerais críticos.", "eml")],
     [("Retomar a adesão à OCDE; reaproximação com EUA, Argentina e Israel, negociando \"com todos\", da China à União Europeia.", "pg"),
      ("Abertura comercial gradual e integração às cadeias globais de valor.", "pg")],
     "Os EUA impuseram tarifa de 50% em 2025 e nova tarifa em jul/2026, sem acordo fechado.",
     "Flávio: \"o governo não fez nada contra o tarifaço\" foi classificado como falso por Lupa e Aos Fatos."),
    ("Tecnologia e inteligência artificial",
     [("Infraestrutura soberana de computação (supercomputadores e modelos de linguagem em português); IA em agro, saúde e finanças.", "cef"),
      ("Conteúdo local e energia renovável em data centers; Política Nacional de Letramento Digital; regulação de IA e direitos autorais.", "cef")],
     [("Digitalizar 100% dos serviços públicos federais, com identidade digital única; IA para agendamentos na saúde.", "pg"),
      ("Não há proposta de regulação de plataformas ou de IA no resumo.", "pg")],
     "",
     ""),
    ("Mulheres e minorias",
     [("Combater a violência contra a mulher.", "eml"),
      ("Exigir planos de ação, com metas progressivas, onde houver diferença salarial de gênero.", "cef"),
      ("Povos indígenas e minorias: " + AUSENTE.lower(), "eml")],
     [("Programa \"Saúde para Elas\" (unidades móveis); escritura de moradia preferencialmente no nome da mulher.", "pg"),
      ("População negra, LGBT e povos indígenas: " + AUSENTE.lower() + " A única menção é indireta, sobre sobreposição de Funai e Ibama.", "pg")],
     "Foram homologadas 20 terras indígenas de 2023 a mar/2026, e 240+ aguardam definição. Feminicídios bateram recorde em 2025 (1.571).",
     ""),
    ("Instituições e Estado",
     [("Fortalecer o papel do Estado no planejamento nacional.", "eml"),
      ("Plano de Integridade e Combate à Corrupção 2025–2027 e Portal da Transparência com dados abertos e IA.", "abl"),
      ("O plano reconhece R$ 50 bilhões em emendas parlamentares no orçamento de 2026, sem modelo fechado de substituição.", "cef")],
     [("Cortar dez ministérios, cargos comissionados e despesas; revisar o pacto federativo.", "abf"),
      ("Reforma administrativa e fim dos supersalários.", "pg"),
      ("Reformar o Judiciário (sem detalhes) e acabar com a reeleição presidencial.", "p360")],
     "",
     ""),
]


def main():
    temas = []
    for tema, lula, flavio, contexto, verificacao in TEMAS:
        temas.append({
            "tema": tema,
            "lula": [{"texto": t, "fonte": f} for t, f in lula],
            "flavio": [{"texto": t, "fonte": f} for t, f in flavio],
            "contexto": contexto,
            "verificacao": verificacao,
        })
    payload = {
        "metadados": {
            "atualizado_em": "2026-10-20",
            "aviso": "São promessas de campanha, não fatos. Os planos oficiais registrados no TSE prevalecem sobre qualquer resumo. "
                     "As propostas foram extraídas de reportagens que resumem os planos; o plano de Flávio Bolsonaro tem também um resumo de terceiro "
                     "com apoio de IA (sinalizado). \"Não consta nas fontes consultadas\" não prova que o plano seja omisso.",
            "planos": {"Lula": "Plano de governo da coligação de Lula (84 páginas, 13 eixos)",
                       "Flávio Bolsonaro": "\"Para o Brasil Vencer o Atraso\" (2027–2030, divulgado em 13/08/2026)"},
        },
        "fontes": {k: {"nome": n, "url": u} for k, (n, u) in FONTES.items()},
        "temas": temas,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"{len(temas)} temas gravados em {OUT}")


if __name__ == "__main__":
    main()
