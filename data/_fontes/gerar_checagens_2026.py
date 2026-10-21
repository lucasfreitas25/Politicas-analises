"""
Gera data/checagens_2026.json a partir das checagens publicadas por agências
independentes (Lupa, Aos Fatos, Ranking dos Políticos e Estadão Verifica)
sobre falas de Lula (PT) e Flávio Bolsonaro (PL) na eleição presidencial de 2026.

Regras de curadoria:
- Cada registro é UMA checagem de UMA agência. A mesma fala pode aparecer
  checada por agências diferentes (com vereditos às vezes diferentes) — isso é
  mantido de propósito, para transparência.
- O veredito original da agência é preservado em "veredito_original"; a
  coluna "categoria" apenas o agrupa em 4 faixas comparáveis.
- Só entram checagens com veredito explícito publicado pela agência.

Execute:  python data/_fontes/gerar_checagens_2026.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checagens_2026.json")

URL = {
    "lupa_band": "https://www.agencialupa.org/checagem/2026/10/18/ao-vivo-checagem-do-debate-entre-lula-e-flavio-bolsonaro-na-band/",
    "rank_band": "https://ranking.org.br/en/articles/checagem-debate-lula-flavio-bolsonaro-band-2-turno-2026",
    "rank_jn_f": "https://ranking.org.br/en/articles/checagem-entrevista-flavio-bolsonaro-jornal-nacional-2-turno-2026",
    "rank_jn_l": "https://ranking.org.br/artigos/checagem-entrevista-lula-jornal-nacional-2-turno-2026",
    "lupa_f_ago": "https://www.agencialupa.org/checagem/2026/08/28/ao-vivo-checagem-da-entrevista-de-flavio-bolsonaro-ao-jornal-nacional/",
    "lupa_l_ago": "https://www.agencialupa.org/checagem/2026/08/27/ao-vivo-checagem-da-entrevista-de-lula-ao-jornal-nacional/",
    "af_l_out": "https://www.aosfatos.org/noticias/checamos-lula-globo-segundo-turno/",
    "af_f_out": "https://www.aosfatos.org/noticias/checamos-flavio-bolsonaro-globo-segundo-turno/",
    "af_l_ago": "https://www.aosfatos.org/noticias/checamos-entrevista-lula-globo/",
    "af_band": "https://www.aosfatos.org/noticias/checamos-lula-flavio-bolsonaro-debate-band/",
    "est_band": "https://www.estadao.com.br/estadao-verifica/checamos-o-debate-entre-lula-e-flavio-na-band/",
}

EVENTOS = {
    "ago_l": ("Entrevista TV Globo — 1º turno", "2026-08-27"),
    "ago_f": ("Entrevista TV Globo — 1º turno", "2026-08-28"),
    "out_l": ("Entrevista TV Globo — 2º turno", "2026-10-15"),
    "out_f": ("Entrevista TV Globo — 2º turno", "2026-10-16"),
    "band": ("Debate Band — 2º turno", "2026-10-18"),
}

AGENCIA = {"lupa": "Agência Lupa", "af": "Aos Fatos", "rank": "Ranking dos Políticos", "est": "Estadão Verifica"}

CATEGORIA = {
    "Verdadeiro": "Verdade",
    "Verdadeiro, com ressalva": "Verdade",
    "Falta contexto": "Meia-verdade",
    "Exagerado": "Meia-verdade",
    "Impreciso": "Meia-verdade",
    "Subestimado": "Meia-verdade",
    "Enganoso": "Meia-verdade",
    "Omissão": "Meia-verdade",
    "Já existe": "Meia-verdade",
    "Falso": "Mentira",
    "Insustentável": "Sem comprovação",
    "Sem comprovação": "Sem comprovação",
}

L, F = "Lula", "Flávio Bolsonaro"

# (candidato, evento, agência, url, tema, afirmação, veredito, explicação)
R = []


def add(cand, ev, ag, url, tema, fala, ver, expl):
    R.append((cand, ev, ag, url, tema, fala, ver, expl))


# ---------------------------------------------------------------- Lupa — entrevista Lula 27/08
u = URL["lupa_l_ago"]
add(L, "ago_l", "lupa", u, "Corrupção & Escândalos", "Lulinha \"está sendo acusado de [...] um crime que nós descobrimos na Previdência Social\"", "Falta contexto", "A CGU aponta que os descontos indevidos do INSS cresceram a partir de 2019, mas há relatos de origem anterior (2016 e até 2005). A CGU estima R$ 6,3 bi descontados entre 2019 e 2024.")
add(L, "ago_l", "lupa", u, "Corrupção & Escândalos", "Sobre Lulinha: \"não tem nenhuma acusação\"", "Verdadeiro", "Lulinha é investigado em três inquéritos da PF autorizados pelo STF, mas não havia denúncia formal do Ministério Público na data da entrevista.")
add(L, "ago_l", "lupa", u, "Economia", "\"Este país estava crescendo 7,5%\" (2010)", "Verdadeiro", "Segundo o IBGE, o PIB cresceu 7,5% em 2010, último ano do segundo mandato de Lula.")
add(L, "ago_l", "lupa", u, "Economia", "O país \"só cresceu 3% [em] 2023, 2024, 2025\"", "Falso", "O PIB cresceu 3% ou mais em quatro anos antes de 2023: 3,9% (2011), 3,0% (2013), 4,8% (2021) e 3,0% (2022).")
add(L, "ago_l", "lupa", u, "Segurança Pública", "\"Nós fizemos a operação Carbono Oculto\"", "Falta contexto", "Foi operação conjunta de órgãos federais (PF, Receita) e paulistas (MPSP, polícias Civil e Militar), em agosto de 2025.")
add(L, "ago_l", "lupa", u, "Educação & Emprego", "\"Quando eu cheguei na presidência, tínhamos 5 milhões de [universitários] no mercado de trabalho\"", "Verdadeiro", "Em 2003 havia cerca de 5,5 milhões de ocupados com ensino superior; em 2025, cerca de 25,5 milhões.")
add(L, "ago_l", "lupa", u, "Corrupção & Escândalos", "Sobre Roberta Luchsinger: \"Eu não conheço essa moça\"", "Falso", "A lobista publicou fotos com Lula em dez/2021, mai/2022 e jun/2022.")
add(L, "ago_l", "lupa", u, "Social", "\"Eu já acabei com a fome duas vezes\"", "Exagerado", "O Brasil saiu do Mapa da Fome da ONU (subnutrição < 2,5%), mas 1,2 milhão de pessoas seguem em insegurança alimentar grave.")
add(L, "ago_l", "lupa", u, "Educação & Emprego", "\"[Fiz] mais de 200 institutos federais\"", "Exagerado", "A Lupa contabiliza 169 institutos federais criados nos três mandatos de Lula.")

# ---------------------------------------------------------------- Aos Fatos — entrevista Lula 27/08
add(L, "ago_l", "af", URL["af_l_ago"], "Corrupção & Escândalos", "Sobre Roberta Luchsinger: \"Eu não conheço essa moça\"", "Falso", "A lobista publicou ao menos duas fotos com Lula no Instagram (out/2022 e nov/2022).")

# ---------------------------------------------------------------- Lupa — entrevista Flávio 28/08
u = URL["lupa_f_ago"]
add(F, "ago_f", "lupa", u, "Corrupção & Escândalos", "\"Eu não fui buscar dinheiro [da] Lei Rouanet [para o filme Dark Horse]\"", "Falta contexto", "A Rouanet não financia longas-metragens. A sócia da produtora pediu R$ 8,59 mi via Rouanet para outros eventos (negado).")
add(F, "ago_f", "lupa", u, "Corrupção & Escândalos", "\"Não teve nenhuma contrapartida [...] para esse investidor [Vorcaro]\"", "Falta contexto", "Não há prova de contrapartida de Flávio, mas a PF indica que Vorcaro oferecia vantagens a políticos em troca de favores.")
add(F, "ago_f", "lupa", u, "Corrupção & Escândalos", "Detalhes do contrato e origem dos recursos do filme \"já tá apresentada\"", "Falso", "A perícia privada não reproduziu contratos nem extratos e não esclareceu a origem dos R$ 20,9 mi gastos no Brasil.")
add(F, "ago_f", "lupa", u, "Corrupção & Escândalos", "\"Eu pedia muito que houvesse a CPMI do Banco Master\"", "Exagerado", "Flávio não assinou três dos cinco pedidos de CPI; assinou dois, após a divulgação de seus áudios com Vorcaro.")
add(F, "ago_f", "lupa", u, "Política & Instituições", "\"Até fontes jornalísticas são ameaçadas [por decisões do STF]\"", "Verdadeiro", "Em 2026 houve busca na casa de jornalista e operação contra fonte, criticadas por Abraji e CPJ.")
add(F, "ago_f", "lupa", u, "Economia", "\"O Pix, que foi ali criado no governo do presidente Bolsonaro\"", "Falso", "O Pix foi concebido em 2018 pelo BC, no governo Temer; foi lançado em 2020, já sob Bolsonaro.")
add(F, "ago_f", "lupa", u, "Economia", "\"Não tem taxa no Pix porque o Bolsonaro exigiu\"", "Falta contexto", "Pix é gratuito para pessoas físicas por regra do BC; não há evidência de exigência presidencial.")
add(F, "ago_f", "lupa", u, "Relações Exteriores", "Eduardo Bolsonaro \"nunca pediu tarifas\" para empresas brasileiras", "Falta contexto", "Eduardo admitiu ter discutido a possibilidade de tarifas com autoridades dos EUA e chamou a decisão de \"sucesso\".")
add(F, "ago_f", "lupa", u, "Trajetória dos candidatos", "Homenagem a Adriano da Nóbrega \"foi feita há mais de 20 anos\"", "Verdadeiro", "Moção de louvor em 2003 e Medalha Tiradentes em 2005.")
add(F, "ago_f", "lupa", u, "Trajetória dos candidatos", "Adriano da Nóbrega \"não tinha feito absolutamente nada de errado\" na época", "Falso", "A primeira acusação contra Nóbrega é de maio de 2003; ele recebeu a medalha em 2005, preso por homicídio.")
add(F, "ago_f", "lupa", u, "Economia", "\"14% [Selic] é o maior juro real do mundo\"", "Verdadeiro", "O Brasil tem o maior juro real do mundo (9,67%); Flávio citou a Selic nominal, outra medida.")
add(F, "ago_f", "lupa", u, "Política & Instituições", "\"Não foi encontrada uma arma no [ataque] do dia 8 de janeiro\"", "Falta contexto", "A denúncia da PGR vai além do 8/1 e inclui plano de assassinato; vídeos mostram furto de armas do GSI no dia.")
add(F, "ago_f", "lupa", u, "Fiscal & Contas Públicas", "\"O atual governo já criou mais 22 mil [cargos comissionados]\"", "Exagerado", "Foram 5,7 mil cargos comissionados a mais (46.989 → 52.780). Os 22 mil se referem a novos servidores.")
add(F, "ago_f", "lupa", u, "Política & Instituições", "\"Jamais questionei [...] o processo eleitoral\"", "Falso", "Há registros de Flávio desconfiando das urnas em 2014, 2018, 2021 e 2022.")
add(F, "ago_f", "lupa", u, "Meio Ambiente & Energia", "Eventos climáticos extremos são \"cíclicos\"", "Falso", "Segundo o IPCC, a atividade humana é a principal causa do aquecimento global (consenso desde os anos 1990).")

# ---------------------------------------------------------------- Aos Fatos — Lula 15/10
u = URL["af_l_out"]
add(L, "out_l", "af", u, "Economia", "\"A gente era a sétima economia do mundo\"", "Verdadeiro", "Banco Mundial: PIB de 2010 de US$ 2,21 tri, 7º maior.")
add(L, "out_l", "af", u, "Economia", "\"A economia crescia 7,5% ao ano\"", "Verdadeiro", "Aos Fatos diz que Lula \"disse corretamente\"; no corpo do texto ressalva que 7,5% foi o crescimento de 2010 (após -0,1% em 2009), não uma média anual.")
add(L, "out_l", "af", u, "Educação & Emprego", "\"Tínhamos criado 22 milhões de empregos em oito anos\"", "Impreciso", "A RAIS registra 15,4 milhões de empregos formais em 2003–2010; 22 mi só incluindo o governo Dilma.")
add(L, "out_l", "af", u, "Política & Instituições", "Bolsonaro \"desmontou dez ministérios\"", "Verdadeiro", "Dez ministérios foram extintos em 2019, com funções absorvidas por outras pastas.")
add(L, "out_l", "af", u, "Fiscal & Contas Públicas", "PEC da Transição aprovada antes da posse", "Verdadeiro", "Aprovada em dez/2022, ampliou o teto em R$ 145 bi para 2023.")
add(L, "out_l", "af", u, "Política & Instituições", "PP, União Brasil, PSD e MDB participaram do ministério", "Verdadeiro", "Os quatro integraram o governo; PP e União saíram em 2025.")
add(L, "out_l", "af", u, "Política & Instituições", "Aprovou \"99%\" do que enviou ao Congresso", "Exagerado", "Houve derrubadas de vetos (marco temporal, desoneração, dosimetria) e rejeição de indicado ao STF; cerca de 23% das MPs viraram lei.")
add(L, "out_l", "af", u, "Relações Exteriores", "Comércio com EUA caiu 9% e com a China subiu 20%", "Impreciso", "Direção correta, números errados: EUA -6,8% e China +11,1% (jan–set/2026).")
add(L, "out_l", "af", u, "Relações Exteriores", "Comércio cresceu 15% com Indonésia, 16% com Alemanha e 13% com Vietnã", "Impreciso", "Alemanha (+15,8%) e Vietnã (+14,1%) próximos; Indonésia só +2,2%.")
add(L, "out_l", "af", u, "Corrupção & Escândalos", "Márcio Canella, preso no dia, tinha a mãe de Flávio como suplente", "Verdadeiro", "Rogéria Bolsonaro foi indicada 1ª suplente em fev/2026.")
add(L, "out_l", "af", u, "Fiscal & Contas Públicas", "Orçamento de 2027 prevê superávit primário", "Verdadeiro", "PLOA 2027 projeta cerca de R$ 18,8 bi (≈0,1% do PIB).")
add(L, "out_l", "af", u, "Fiscal & Contas Públicas", "\"Ficou um déficit de 2,8%\" (lida pelo Aos Fatos como o déficit do 1º ano do 3º mandato)", "Verdadeiro, com ressalva", "Aos Fatos registrou como fato (\"Também é fato\") que houve déficit no primeiro ano do governo, mas o próprio texto cita o TCU: déficit primário de 2,4% do PIB em 2023, não 2,8%. O Ranking dos Políticos interpretou a mesma fala como herança de Bolsonaro e a classificou como falsa.")
add(L, "out_l", "af", u, "Endividamento", "78% das famílias estavam endividadas quando assumiu", "Verdadeiro", "CNC: 77,9% em dez/2022. Em set/2026 o índice estava em 81,7%.")
add(L, "out_l", "af", u, "Economia", "Pagou dívida de US$ 30 bi com o FMI", "Verdadeiro", "A dívida, de 2002, foi quitada em 2005.")
add(L, "out_l", "af", u, "Meio Ambiente & Energia", "Grande parte do setor elétrico é privada", "Verdadeiro", "Estimativa de 2017: 60% da geração e 71% da distribuição privadas; Eletrobras privatizada em 2022.")
add(L, "out_l", "af", u, "Fiscal & Contas Públicas", "Havia mais de 6 mil obras paradas quando assumiu", "Verdadeiro", "\"Dados confirmam\", segundo o Aos Fatos; o texto observa que o MEC registrava 5.642 obras paradas e a Saúde cerca de 6.300, com escopos diferentes.")

# ---------------------------------------------------------------- Ranking — Lula 15/10
u = URL["rank_jn_l"]
add(L, "out_l", "rank", u, "Educação & Emprego", "Criou 22 milhões de empregos formais em oito anos", "Falso", "Caged: 15,04 milhões de 2003 a 2010; RAIS: 15,4 milhões.")
add(L, "out_l", "rank", u, "Economia", "Brasil voltou a ter recorde na balança comercial", "Falso", "O MDIC projeta US$ 84,4 bi em 2026, o 2º maior da série — não recorde (2023: US$ 98,9 bi).")
add(L, "out_l", "rank", u, "Economia", "Era a 7ª economia e crescia 7,5% ao ano", "Impreciso", "Ranking correto, mas 7,5% foi só 2010; a média dos governos Lula foi ~4% a.a.")
add(L, "out_l", "rank", u, "Economia", "Levou a economia de 12ª para 10ª, chegará a 8ª", "Impreciso", "O Brasil era 11º em 2022 e terminou 2025 em 11º; FMI projeta 10º em 2026.")
add(L, "out_l", "rank", u, "Relações Exteriores", "Perdeu 9% no comércio com EUA e cresceu 20% com a China", "Impreciso", "Jan–set/2026: exportações aos EUA -6,5%; à China +12%.")
add(L, "out_l", "rank", u, "Fiscal & Contas Públicas", "Herdou um déficit de 2,8%", "Falso", "O governo central fechou 2022 com superávit primário de 0,5% do PIB (R$ 54,1 bi).")
add(L, "out_l", "rank", u, "Endividamento", "72% da população estava endividada quando assumiu", "Falso", "Peic/CNC: 78% das famílias em dez/2022 e 82% em jul/2026.")
add(L, "out_l", "rank", u, "Endividamento", "Desenrola 3 compra dívidas de até R$ 4 mil e injeta ~R$ 150 bi", "Impreciso", "O programa abrange dívidas até R$ 10 mil; R$ 150 bi é o estoque elegível, não o gasto da União.")
add(L, "out_l", "rank", u, "Fiscal & Contas Públicas", "Perdoou R$ 12,7 bi em dívidas de MEIs", "Impreciso", "O valor anunciado é R$ 12,6 bi, via projeto de lei; efeito só a partir de 2027.")
add(L, "out_l", "rank", u, "Economia", "Devia US$ 30 bi ao FMI e emprestou US$ 15 bi depois do subprime", "Impreciso", "Quitou US$ 15,5 bi em 2005; em 2009 emprestou US$ 10 bi ao Fundo.")
add(L, "out_l", "rank", u, "Fiscal & Contas Públicas", "Orçamento de 2027 prevê superávit de 0,1%", "Verdadeiro", "PLOA 2027 prevê superávit efetivo de ~0,1% do PIB.")
add(L, "out_l", "rank", u, "Política & Instituições", "Aprovou \"99% de tudo que a gente queria aprovar\"", "Falso", "Em 2023–2024, 22 de 59 projetos do Executivo viraram lei (~37%); 20 de 131 MPs aprovadas.")
add(L, "out_l", "rank", u, "Fiscal & Contas Públicas", "Encontrou 100 mil obras paralisadas", "Falso", "TCU contou 8,6 mil obras paradas em 2023 e 11.941 em 2024.")
add(L, "out_l", "rank", u, "Economia", "Bolsonaro privatizou a Petrobras \"a troco de banana\"", "Falso", "A Petrobras segue sob controle da União; foram privatizadas Eletrobras e BR Distribuidora.")
add(L, "out_l", "rank", u, "Política & Instituições", "Todos os partidos participaram do ministério", "Impreciso", "Os partidos tiveram pastas, mas a federação União Progressista saiu em set/2025.")
add(L, "out_l", "rank", u, "Social", "Acabou com a fome em 2014; havia 33 milhões passando fome na volta", "Impreciso", "Saída do Mapa da Fome foi sob Dilma; 33,1 mi é estimativa da Rede Penssan (pela FAO, ~15 mi).")
add(L, "out_l", "rank", u, "Saúde", "Mais Médicos tinha só 12 mil médicos quando voltou", "Verdadeiro", "12.843 médicos ativos em dez/2022.")
add(L, "out_l", "rank", u, "Saúde", "Fez 15 milhões de cirurgias eletivas em 2025", "Verdadeiro", "O SUS realizou 14,7 milhões, recorde.")
add(L, "out_l", "rank", u, "Corrupção & Escândalos", "Disse a Vorcaro que seria investigado e \"um mês depois\" o banco fechou", "Falso", "Reunião em dez/2024; liquidação do Master em nov/2025, ~11 meses depois.")
add(L, "out_l", "rank", u, "Corrupção & Escândalos", "Toffoli e Mendonça estão implicados no caso Master", "Impreciso", "A PF cita Toffoli por reuniões com Vorcaro; Mendonça é alvo de outra acusação, sem ligação com Vorcaro.")
add(L, "out_l", "rank", u, "Política & Instituições", "Fez a primeira reforma do Judiciário com Gilmar Mendes e Marco Aurélio", "Impreciso", "A EC 45/2004 é do governo Lula, mas o pacto foi com Nelson Jobim.")
add(L, "out_l", "rank", u, "Política & Instituições", "Dino pediu vista para julgar os casos na mesma sessão", "Verdadeiro", "Em set/2026, Dino defendeu julgamento conjunto antes de pedir vista.")
add(L, "out_l", "rank", u, "Segurança Pública", "Projeto quis reduzir a maioridade penal para 14 anos", "Impreciso", "A emenda fixa 16 anos como regra geral; 14 só para crimes graves específicos.")
add(L, "out_l", "rank", u, "Segurança Pública", "Governo vai financiar 138 presídios", "Verdadeiro", "Programa de mai/2026 destina R$ 330,6 mi para 138 unidades de segurança máxima.")
add(L, "out_l", "rank", u, "Segurança Pública", "Lei Antifacção aprovada aumenta penas", "Verdadeiro", "Lei 15.358/2026, sancionada em 24/03/2026.")
add(L, "out_l", "rank", u, "Corrupção & Escândalos", "Canella foi preso pela PF e tinha a mãe de Flávio como suplente", "Verdadeiro", "Prisão em 15/10 na Operação Unha e Carne; Rogéria Bolsonaro era 1ª suplente.")
add(L, "out_l", "rank", u, "Relações Exteriores", "Ligou para Trump por quase 1h30 sobre o Conselho de Segurança da ONU", "Verdadeiro", "Ligação de 1h20 em 21/08/2026.")

# ---------------------------------------------------------------- Aos Fatos — Flávio 16/10
u = URL["af_f_out"]
add(F, "out_f", "af", u, "Economia", "Dizer que ele privatizaria Petrobras, Caixa e BB é \"terrorismo\" do PT", "Omissão", "Omitiu falas próprias (\"privatizar 95%\" das estatais, fev/2026) e da equipe sobre o BB.")
add(F, "out_f", "af", u, "Fiscal & Contas Públicas", "\"A dívida do Brasil está em 11 trilhões de reais\"", "Verdadeiro", "DBGG de R$ 11,1 tri (82,9% do PIB) em ago/2026.")
add(F, "out_f", "af", u, "Meio Ambiente & Energia", "Margem Equatorial poderia trazer \"mais de 100 bilhões de reais de largada\"", "Enganoso", "Sem registros que sustentem; produção comercial estimada só entre 2032 e 2036.")
add(F, "out_f", "af", u, "Corrupção & Escândalos", "Produtora do Dark Horse \"prestou contas de tudo\"", "Falso", "Perícia sem notas, recibos ou extratos; o perito não acessou o fundo que bancou ~70% das despesas.")
add(F, "out_f", "af", u, "Corrupção & Escândalos", "Dinheiro de Vorcaro era \"totalmente lícito\"", "Sem comprovação", "A PF investiga lavagem, evasão de divisas e corrupção; inquérito em andamento.")
add(F, "out_f", "af", u, "Corrupção & Escândalos", "PF confirmou áudio de Vorcaro sobre documentário de Lula", "Falso", "A PF afirmou que Vorcaro nunca prestou depoimento com esse conteúdo.")
add(F, "out_f", "af", u, "Política & Instituições", "Tentativa de golpe se limitou à invasão dos prédios em 8/1", "Falso", "PF e PGR descrevem articulação golpista desde 2022; STF condenou Jair Bolsonaro em set/2025.")
add(F, "out_f", "af", u, "Segurança Pública", "Governo Lula é \"recordista em criminalidade\"", "Falso", "Mortes violentas caíram para 19,1/100 mil em 2025, menor da série; recorde é de feminicídios.")
add(F, "out_f", "af", u, "Economia", "Governo é \"recordista em empresas fechadas\"", "Falso", "Recorde de falências foi em 2015 (1.828); 862 em 2024 e 734 em 2025 (Serasa).")
add(F, "out_f", "af", u, "Economia", "Governo é \"recordista em indústrias que vão para o Paraguai\"", "Falso", "Não há levantamento; 232 empresas aderiram à maquila desde 2007, mantendo operação no Brasil.")
add(F, "out_f", "af", u, "Segurança Pública", "Flávio Dino entrou na Maré \"sem nenhum policial\"", "Falso", "PF e PRF confirmaram escolta à paisana; polícias estaduais apoiaram.")
add(F, "out_f", "af", u, "Segurança Pública", "Queda de homicídios em 2019 se deveu ao aumento de CACs", "Falso", "Atlas da Violência atribui a fatores demográficos, programas estaduais e Estatuto do Desarmamento.")
add(F, "out_f", "af", u, "Segurança Pública", "Comprar arma para defender propriedade está na Constituição", "Falso", "Legítima defesa está no Código Penal (art. 25), não na Constituição.")
add(F, "out_f", "af", u, "Segurança Pública", "Estatuto do Desarmamento \"autoriza marginais a comprarem armas de guerra\"", "Falso", "A Lei 10.826/2003 criminaliza porte de armas restritas sem autorização.")
add(F, "out_f", "af", u, "Saúde", "Promete criar prontuário eletrônico único", "Já existe", "A RNDS existe desde 2020 (governo Bolsonaro), com mais de 5 bi de registros.")

# ---------------------------------------------------------------- Ranking — Flávio 16/10
u = URL["rank_jn_f"]
add(F, "out_f", "rank", u, "Corrupção & Escândalos", "Cita \"o Vacarezza\" no Instituto Lula", "Falso", "O instituto é dirigido por Paulo Okamotto; o citado no relato é Vaccari Neto.")
add(F, "out_f", "rank", u, "Corrupção & Escândalos", "Programa de Luciano Huck recebeu \"160 milhões\" do Master", "Impreciso", "Mensagens da PF citam ~R$ 109 mi; R$ 160 mi é teto de estimativas.")
add(F, "out_f", "rank", u, "Corrupção & Escândalos", "Produtora do Dark Horse \"prestou contas de tudo\"", "Impreciso", "Balanço de R$ 75,2 mi, mas contratos do fundo Havengate não divulgados.")
add(F, "out_f", "rank", u, "Corrupção & Escândalos", "Defesa de Vorcaro confirmou que a voz no áudio era dele", "Verdadeiro", "O advogado confirmou a voz.")
add(F, "out_f", "rank", u, "Segurança Pública", "Superintendente da PF no Rio trocado por \"maus resultados\" (2019)", "Falso", "A PF negou; a superintendência teve seu melhor resultado em três anos.")
add(F, "out_f", "rank", u, "Segurança Pública", "Dino entrou na Maré \"sem nenhum policial\"", "Falso", "A PF fez a segurança do ministro.")
add(F, "out_f", "rank", u, "Segurança Pública", "Governo \"recordista em criminalidade\"", "Falso", "Taxa de MVI de 19,1/100 mil em 2025, menor desde 2012.")
add(F, "out_f", "rank", u, "Segurança Pública", "Lula \"trocou os 27 superintendentes\" da PF", "Impreciso", "18 no início; 26 de 27 ao longo da gestão.")
add(F, "out_f", "rank", u, "Segurança Pública", "Queda de 17% nos homicídios em 2019 derruba tese sobre armas", "Impreciso", "A queda foi de 19% e vinha de 2018; armas recentes demais para explicar.")
add(F, "out_f", "rank", u, "Segurança Pública", "Santos é o \"segundo maior porto exportador de cocaína do mundo\"", "Impreciso", "UNODC (2022) cita Santos entre hubs, sem ranking; situação anterior ao governo.")
add(F, "out_f", "rank", u, "Segurança Pública", "Governo \"recordista em mulheres assassinadas\"", "Verdadeiro", "Recorde de 1.571 feminicídios em 2025 (+4%).")
add(F, "out_f", "rank", u, "Fiscal & Contas Públicas", "Dívida em \"R$ 11 trilhões\"", "Verdadeiro", "R$ 11,1 tri (82,9% do PIB) em ago/2026.")
add(F, "out_f", "rank", u, "Economia", "Focus de 2022 previa juros perto de 7%; Selic hoje em 14%", "Verdadeiro", "Focus de set/2022 projetava 7,5% para 2025; Selic de 14% em ago/2026.")
add(F, "out_f", "rank", u, "Fiscal & Contas Públicas", "Estatais: R$ 18 bi de superávit com Bolsonaro e R$ 36 bi de prejuízo com Lula", "Impreciso", "TCU: +R$ 17,46 bi (2019–22) e -R$ 18,48 bi (2023–mai/26).")
add(F, "out_f", "rank", u, "Fiscal & Contas Públicas", "Imóveis da União valem R$ 1,7 trilhão", "Impreciso", "~R$ 1,8 tri, mas muitos inalienáveis; vendáveis ~R$ 97 bi.")
add(F, "out_f", "rank", u, "Social", "Bolsonaro \"triplicou\" o Bolsa Família, de R$ 190 para R$ 600", "Impreciso", "Os R$ 600 valiam só até dez/2022.")
add(F, "out_f", "rank", u, "Política & Instituições", "Governo tem \"39 ministérios\"", "Impreciso", "Hoje são 38.")
add(F, "out_f", "rank", u, "Fiscal & Contas Públicas", "Dívida ativa da União de \"quase 3 trilhões\"", "Verdadeiro", "R$ 2,7 tri segundo a PGFN.")
add(F, "out_f", "rank", u, "Endividamento", "Governo \"recordista em pessoas endividadas\"", "Verdadeiro", "Peic/CNC: 82% das famílias endividadas em jul/2026, recorde.")
add(F, "out_f", "rank", u, "Fiscal & Contas Públicas", "Bolsonaro extinguiu \"mais de 20 mil cargos\"", "Verdadeiro", "Decreto 9.725/2019 extinguiu 21 mil cargos e funções.")
add(F, "out_f", "rank", u, "Meio Ambiente & Energia", "Lula \"não conseguiu iniciar a exploração na margem equatorial\"", "Falso", "Ibama licenciou em out/2025; Petrobras perfura o poço Morpho.")
add(F, "out_f", "rank", u, "Meio Ambiente & Energia", "Governo \"recordista em queimadas na Amazônia\"", "Impreciso", "Recorde do Amazonas foi em 2024; até 12/10/2026, 12% abaixo da média histórica.")
add(F, "out_f", "rank", u, "Política & Instituições", "Inelegibilidade de parentes \"até terceiro grau\"", "Impreciso", "A Constituição limita a parentes até o segundo grau.")
add(F, "out_f", "rank", u, "Política & Instituições", "Governo não autoriza faixa azul em SP \"por birra\"", "Impreciso", "A Prefeitura aguarda a Senatran, que autorizou outras dez avenidas.")
add(F, "out_f", "rank", u, "Política & Instituições", "Moro se demitiu, sem ser dispensado por Bolsonaro", "Verdadeiro", "Moro anunciou a saída em 24/04/2020.")
add(F, "out_f", "rank", u, "Trajetória dos candidatos", "Cláudio Lottenberg presidiu o Albert Einstein", "Verdadeiro", "Presidente executivo de 2001 a 2016.")

# ---------------------------------------------------------------- Lupa — debate Band 18/10
u = URL["lupa_band"]
add(L, "band", "lupa", u, "Economia", "\"Este país cresceu 7,5% em 2010\"", "Verdadeiro", "Dado do IBGE.")
add(F, "band", "lupa", u, "Fiscal & Contas Públicas", "\"O atual governo tá deixando 11 trilhões de reais [de dívida]\"", "Verdadeiro", "DBGG de R$ 11,1 tri (82,9% do PIB) em ago/2026.")
add(F, "band", "lupa", u, "Segurança Pública", "Com a Lei Antifacção, líderes \"vão ficar até 80 anos presos\"", "Falta contexto", "Pena de 20 a 40 anos com agravantes, mas o Código Penal limita o cumprimento a 40 anos.")
add(L, "band", "lupa", u, "Segurança Pública", "\"Eu já fiz a Lei Antifacção, ela foi aprovada\"", "Verdadeiro", "Lei 15.358/2026, originada em projeto do Executivo.")
add(F, "band", "lupa", u, "Corrupção & Escândalos", "Áudio de Vorcaro: \"R$ 30 milhões para o Instituto Lula\"", "Insustentável", "Sem prova de pagamento; PF e PGR negam a existência do depoimento.")
add(F, "band", "lupa", u, "Social", "Bolsonaro \"passou para no mínimo R$ 600 o Bolsa Família\"", "Exagerado", "R$ 600 só de jun a dez/2022; a proposta de orçamento de 2023 previa R$ 400.")
add(F, "band", "lupa", u, "Segurança Pública", "Governo \"coloca nas ruas marginais perigosos\" por falta de vagas", "Falso", "Não há soltura automática por falta de vaga; decisões são judiciais.")
add(F, "band", "lupa", u, "Social", "Bolsa Família era R$ 190 e Bolsonaro \"triplicou\"", "Exagerado", "O salto veio do auxílio emergencial e da reestruturação temporária de 2022.")
add(L, "band", "lupa", u, "Fiscal & Contas Públicas", "\"Anistiei 12,6 bilhões de dívida dos MEI\"", "Verdadeiro", "PLC aprovado em 16/10, perdoa ~R$ 12,6 bi; aguarda sanção.")
add(F, "band", "lupa", u, "Fiscal & Contas Públicas", "\"R$ 7 bilhões que você gastou em viagens com a Janja\"", "Falso", "O valor cobre todo o governo federal (2023–2025), não só Lula e Janja.")
add(L, "band", "lupa", u, "Trajetória dos candidatos", "Flávio foi o único de 49 deputados a votar contra a licença-maternidade de 6 meses (2009)", "Verdadeiro", "Único voto contra na Alerj.")
add(L, "band", "lupa", u, "Economia", "Salário mínimo comprava 1,8 cesta básica; hoje compra 2,2", "Exagerado", "Em SP: 1,62 em ago/2022 e 1,8 em ago/2026. O 2,2 não se sustenta.")
add(F, "band", "lupa", u, "Corrupção & Escândalos", "Roberta Luchsinger \"fez acusações muito graves\" contra Lula", "Falta contexto", "Não há acusação formal contra Lula; Lulinha é investigado em três inquéritos.")
add(L, "band", "lupa", u, "Fiscal & Contas Públicas", "Governo anterior deixou \"um déficit de 2,8%\"", "Falso", "Governo central teve superávit de R$ 54,1 bi (0,5% do PIB) em 2022.")
add(F, "band", "lupa", u, "Trajetória dos candidatos", "\"O filho do Lula bateu na própria mulher\"", "Insustentável", "Inquérito de 2024 arquivado sem denúncia por falta de provas.")
add(F, "band", "lupa", u, "Segurança Pública", "\"Mais de 40 milhões moram em áreas dominadas por narcoterroristas\"", "Subestimado", "Estudos estimam de 50 a 68,7 milhões vivendo sob governança criminal.")
add(F, "band", "lupa", u, "Política & Instituições", "\"73% dos presidiários votaram em você\"", "Falta contexto", "72,57% nas seções prisionais, que incluem não presos; só presos provisórios votam.")
add(L, "band", "lupa", u, "Economia", "\"Nós fizemos 270 bilhões de reserva\"", "Subestimado", "Reservas chegaram a US$ 288,6 bi no fim de 2010.")
add(F, "band", "lupa", u, "Relações Exteriores", "Esquerda argentina deixou miséria que a direita teve de consertar", "Falta contexto", "Pobreza subiu a 52,9% no início de Milei, caiu e voltou a 32,3% em 2026.")
add(L, "band", "lupa", u, "Segurança Pública", "Governo Bolsonaro liberou \"mais de 1 milhão de armas\"", "Verdadeiro", "Sou da Paz e Igarapé: mais de 1 milhão de novas armas registradas em 2019–2022.")
add(L, "band", "lupa", u, "Segurança Pública", "Liberou \"1 bilhão e 100 milhões de balas\"", "Insustentável", "Nenhum dado público sustenta esse número.")
add(F, "band", "lupa", u, "Segurança Pública", "\"Você vai para a praia com medo de ser assaltado\" no atual governo", "Falta contexto", "Policiamento ostensivo é atribuição das polícias estaduais.")
add(L, "band", "lupa", u, "Economia", "País \"só voltou a crescer acima de 3%\" quando ele voltou", "Falso", "PIB cresceu 3,9% (2011), 3,0% (2013), 4,8% (2021) e 3,0% (2022).")
add(F, "band", "lupa", u, "Segurança Pública", "Lula vetou o fim da saidinha e o Congresso derrubou", "Verdadeiro", "Veto derrubado em 28/05/2024.")
add(F, "band", "lupa", u, "Segurança Pública", "Lula \"acionou a justiça\" para a saidinha voltar", "Falso", "A ação no STF (ADI 7663) é da Anacrim, não do governo.")
add(L, "band", "lupa", u, "Fiscal & Contas Públicas", "\"Apresentamos um orçamento com superávit de 0,1%\"", "Verdadeiro", "PLOA 2027: superávit de R$ 18,6 bi (0,13% do PIB).")
add(L, "band", "lupa", u, "Fiscal & Contas Públicas", "É a primeira vez que apresenta resultado positivo", "Falta contexto", "Previsões de equilíbrio viraram déficit: 2024 (R$ -47,6 bi) e 2025 (R$ -61,6 bi).")
add(L, "band", "lupa", u, "Segurança Pública", "Condenado por crime hediondo não tem saidinha", "Verdadeiro", "Lei 14.843/2024.")
add(L, "band", "lupa", u, "Economia", "\"Nós criamos o Simples\"", "Falta contexto", "O Simples é de 1996 (FHC); Lula criou o Simples Nacional (2006).")
add(L, "band", "lupa", u, "Trajetória dos candidatos", "Flávio empregou parentes de miliciano do Escritório do Crime", "Verdadeiro", "Empregou mãe e esposa de Adriano da Nóbrega até nov/2018.")
add(L, "band", "lupa", u, "Economia", "\"O PIB industrial é de 3,4%\"", "Exagerado", "PIB industrial: 3,3% em 2024 e 1,4% em 2025.")
add(F, "band", "lupa", u, "Relações Exteriores", "Foi aos EUA defender as empresas e o governo não fez nada", "Falso", "Diplomatas acompanharam a audiência do USTR; ministros tiveram reuniões de alto nível.")
add(F, "band", "lupa", u, "Fiscal & Contas Públicas", "Lula \"gastou mais 350 bilhões para tentar se reeleger\"", "Exagerado", "Estadão soma R$ 354 bi em medidas, mas R$ 55 bi são renúncias e só R$ 34 bi estão fora do orçamento.")
add(F, "band", "lupa", u, "Política & Instituições", "Eduardo Bolsonaro \"tá exilado, perseguido\"", "Exagerado", "Mudou-se em mar/2025 antes de ser investigado; condenado pelo STF em jun/2026.")
add(F, "band", "lupa", u, "Segurança Pública", "\"Com você, a criminalidade explodiu no Brasil\"", "Falso", "Mortes violentas caíram 8,2% em 2025 (19,1/100 mil, menor da série); roubos de celular -18,6%.")
add(F, "band", "lupa", u, "Segurança Pública", "\"Você liberou as armas para os traficantes\"", "Falso", "Nenhum ato de Lula facilitou acesso; ele revogou regras de 2019.")
add(F, "band", "lupa", u, "Segurança Pública", "Lula \"está deixando entrar\" arma ilegal no país", "Insustentável", "PF apreendeu 9.373 armas em 2023–2026, 6,5% mais que em 2019–2022.")
add(F, "band", "lupa", u, "Segurança Pública", "Não houve redução de roubo de celular", "Falso", "Roubos de celular caíram 37,4% (492.905 em 2022 → 308.723 em 2025).")
add(F, "band", "lupa", u, "Segurança Pública", "Não há combate a quem revende celular roubado", "Falso", "Lei 15.397/2026 elevou penas; Operação Última Chamada recuperou milhares de aparelhos.")
add(L, "band", "lupa", u, "Economia", "Inflação de alimentos: 56% com Bolsonaro, 13% com ele", "Verdadeiro", "IPCA: alimentos subiram 54,2% de jan/2019 a jul/2022 e 13,6% nos 43 primeiros meses de Lula; Lula arredondou.")
add(F, "band", "lupa", u, "Corrupção & Escândalos", "Lula foi \"condenado no STJ, no STF, em todas as instâncias\"", "Falso", "As condenações nunca foram confirmadas pelo STF; foram anuladas em 2021.")

# ---------------------------------------------------------------- Ranking — debate Band 18/10 (Lula)
u = URL["rank_band"]
for tema, fala, ver, expl in [
    ("Corrupção & Escândalos", "Governo já recuperou R$ 100 bi da quadrilha do INSS", "Falso", "Medidas judiciais bloquearam pouco mais de R$ 6 bi."),
    ("Corrupção & Escândalos", "Quadrilha do \"Careca do INSS\" foi montada sob Bolsonaro", "Impreciso", "Descontos indevidos começaram em 2017–18 e cresceram a partir de 2019."),
    ("Corrupção & Escândalos", "Flávio mantém escritório com o \"Careca do INSS\"", "Impreciso", "Empresas dividem endereço; não há sociedade documentada."),
    ("Corrupção & Escândalos", "Vorcaro fez fraude de R$ 60 bi", "Impreciso", "Prejuízo confirmado ao FGC é R$ 51,8 bi."),
    ("Corrupção & Escândalos", "Governo já pagou R$ 3,5 bi aos aposentados", "Verdadeiro", "Mais de R$ 3,5 bi a mais de 5 milhões de beneficiários."),
    ("Trajetória dos candidatos", "Flávio mentiu 43 vezes sobre o caso Vorcaro", "Verdadeiro", "Aos Fatos documentou 43 declarações enganosas."),
    ("Corrupção & Escândalos", "Vorcaro está preso", "Verdadeiro", "Preventiva desde 04/03/2026."),
    ("Corrupção & Escândalos", "Lulinha tem três inquéritos; Mendonça é o relator", "Verdadeiro", "Mendonça relata dois; Dino, o terceiro."),
    ("Fiscal & Contas Públicas", "Governo anterior \"ficou um déficit de 2,8%\"", "Falso", "Superávit de R$ 54,1 bi (0,5% do PIB) em 2022."),
    ("Fiscal & Contas Públicas", "Orçamento com superávit de 0,1% é inédito", "Falso", "A meta de 2026 já previa superávit de 0,25%."),
    ("Fiscal & Contas Públicas", "É o único presidente com superávit em todos os governos", "Falso", "Déficit de R$ 230,5 bi em 2023; R$ 92,2 bi até jun/2026."),
    ("Economia", "País \"não tinha reserva\" quando assumiu", "Falso", "Havia US$ 37,65 bi em reservas em jan/2003."),
    ("Social", "Correção do Bolsa Família \"é obrigação, é lei\"", "Falso", "A lei permite, mas não obriga indexação; piso ficou sem reajuste de mar/2023 a set/2026."),
    ("Economia", "Devia US$ 30 bi ao FMI, tinha US$ 272 bi de reservas, crescia 7,5%", "Impreciso", "Pagou US$ 15,5 bi ao FMI; reservas de US$ 288,6 bi; 7,5% só em 2010."),
    ("Economia", "Crescimento acima de 3% desde que assumiu", "Impreciso", "3,2% (2023), 3,4% (2024), mas 2,3% (2025)."),
    ("Economia", "Salário mínimo comprava 1,8 cesta e hoje compra 2,2", "Impreciso", "Dieese: ~1,79 em 2025; o mínimo do governo anterior foi 1,5 (abr/2022)."),
    ("Economia", "Bolsonaro nunca deu aumento real ao salário mínimo", "Impreciso", "Em 2019 houve ganho real de 1,14% pela regra herdada; depois, não."),
    ("Economia", "Foi o primeiro a ganhar grau de investimento", "Verdadeiro", "Em 2008–2009; hoje a um degrau na Moody's."),
    ("Economia", "Inflação de alimentos: 56,17% antes e 13% agora", "Verdadeiro", "Alimentação no domicílio: 56,16% (2019–22) e 13,6% desde 2023."),
    ("Economia", "Petrobras foi privatizada \"a preço de banana\"", "Falso", "Petrobras segue sob controle da União (privatizada foi a Eletrobras)."),
    ("Fiscal & Contas Públicas", "Perdoou R$ 12,7 bi de dívidas de MEI", "Impreciso", "R$ 12,6 bi, em proposta que vale só a partir de 2027."),
    ("Endividamento", "Desenrola chegará a R$ 300 bi com descontos de até 92%", "Impreciso", "Dívida elegível de R$ 150 bi, desconto mínimo de 90%."),
    ("Economia", "Nova Indústria Brasil já aplicou R$ 725 bi", "Impreciso", "R$ 750 bi disponibilizados, não aplicados; BNDES liberou R$ 330 bi."),
    ("Economia", "Data centers devem deixar 10% dos dados com o governo", "Impreciso", "Redata exige 10% da capacidade ofertada ao mercado interno."),
    ("Segurança Pública", "Celular Seguro é lei aprovada no Congresso", "Impreciso", "É programa do Ministério da Justiça, não lei."),
    ("Economia", "Criou Lei Geral da Microempresa, Simples, MEI e Super Simples", "Impreciso", "O Simples federal original é de 1996 (FHC)."),
    ("Economia", "Flávio e aliados querem privatizar a Petrobras", "Impreciso", "Flávio prometeu privatizar 95% das estatais, mas nega a Petrobras."),
    ("Economia", "PIB industrial cresceu 3,4%", "Verdadeiro", "Indústria cresceu 3,3% em 2024; arredondamento aceitável."),
    ("Economia", "Existem 17,5 milhões de MEIs", "Verdadeiro", "17,16 milhões em jun/2026."),
    ("Economia", "Governo só pode recomprar a BR depois de 2029", "Verdadeiro", "Cláusula de não concorrência Petrobras–Vibra até 2029."),
    ("Economia", "Flávio falou em privatizar 95% das estatais", "Verdadeiro", "Declaração em evento do BTG."),
    ("Saúde", "Mais Médicos foi de 12 mil para 27 mil médicos", "Verdadeiro", "12.843 em dez/2022 e ~26.400 em ago/2025."),
    ("Saúde", "Farmácia Popular dá 40 remédios gratuitos", "Verdadeiro", "Desde fev/2025, os 41 itens são gratuitos."),
    ("Educação & Emprego", "Criou universidade indígena com sede em Brasília", "Verdadeiro", "Lei 15.418/2026."),
    ("Saúde", "780 mil pessoas morreram na pandemia", "Falso", "Ministério da Saúde: 716.075 óbitos até abr/2025."),
    ("Saúde", "Bolsonaro teve três ministros da Saúde", "Impreciso", "Foram quatro: Mandetta, Teich, Pazuello e Queiroga."),
    ("Segurança Pública", "Criou a Lei Antifacção e aumentou a pena", "Verdadeiro", "Lei 15.358/2026."),
    ("Segurança Pública", "Estuprador e agressor de mulher não têm saidinha", "Verdadeiro", "Mantida a vedação para crimes hediondos com violência."),
    ("Segurança Pública", "Mandou a PEC da Segurança em 26 de março", "Impreciso", "Foi entregue ao Congresso em 23/04/2025."),
    ("Segurança Pública", "Governo Bolsonaro liberou mais de 1 milhão de armas e 1,1 bi de balas", "Impreciso", "Acervo CAC passou de 350 mil para mais de 1 milhão; Sou da Paz conta 994 mi de munições vendidas."),
    ("Política & Instituições", "Flávio não pode dar indulto individual", "Impreciso", "A graça é prerrogativa presidencial; STF limitou em crimes contra a democracia."),
    ("Trajetória dos candidatos", "Flávio foi o único de 49 a votar contra licença-maternidade como deputado federal", "Impreciso", "Foi como deputado estadual na Alerj (45 a 1)."),
    ("Corrupção & Escândalos", "Flávio comprou casa de R$ 10 mi com dinheiro do BRB", "Impreciso", "Financiamento BRB real, mas imóvel custou R$ 5,97 mi."),
    ("Trajetória dos candidatos", "Flávio impediu prisão de PM acusado de matar criança", "Impreciso", "Atuou como advogado em recurso negado; o PM já estava solto antes."),
    ("Trajetória dos candidatos", "Flávio empregou parentes do chefe do Escritório do Crime \"que matou Marielle\"", "Impreciso", "Empregou parentes de Nóbrega, mas a polícia descartou o grupo no caso Marielle."),
    ("Corrupção & Escândalos", "Flávio cobrava pedágio e estacionamento em hospitais federais", "Impreciso", "Inquérito atribuiu as cobranças a milícia, não a ele."),
    ("Trajetória dos candidatos", "Jair Bolsonaro \"mentia 11 vezes por dia\"", "Falso", "Aos Fatos: média de 4,58 declarações falsas/distorcidas por dia."),
]:
    add(L, "band", "rank", u, tema, fala, ver, expl)

# ---------------------------------------------------------------- Ranking — debate Band 18/10 (Flávio)
for tema, fala, ver, expl in [
    ("Segurança Pública", "Armas e munições liberadas sob Bolsonaro \"não existe\"", "Falso", "Acervo CAC passou de 1 milhão de armas; 994 mi de munições vendidas."),
    ("Segurança Pública", "\"Recorde de criminalidade\"", "Falso", "2025 teve a menor taxa de MVI desde 2012."),
    ("Segurança Pública", "Com a Lei Antifacção, líderes ficam até 80 anos presos", "Impreciso", "Pena pode chegar a 80, mas o cumprimento é limitado a 40 anos."),
    ("Segurança Pública", "Santos é o 2º maior porto exportador de cocaína, \"legado deste governo\"", "Impreciso", "UNODC (2022) cita Santos sem ranking, antes do governo atual."),
    ("Segurança Pública", "\"Recorde de mulher assassinada\"", "Verdadeiro", "Recorde de 1.571 feminicídios em 2025."),
    ("Segurança Pública", "Mais de 770 mil assassinados em 20 anos de PT", "Verdadeiro", "Atlas da Violência soma mais de 770 mil homicídios nos ~17 anos de PT."),
    ("Segurança Pública", "Sargento Dias foi morto por preso da saidinha", "Verdadeiro", "Jan/2024, preso que não voltou da saidinha de Natal."),
    ("Segurança Pública", "Lula vetou o fim da saidinha", "Verdadeiro", "Veto derrubado em mai/2024."),
    ("Segurança Pública", "Cadastro de pedófilos está em vigor, mas Lula não implementa", "Verdadeiro", "Lei sancionada em nov/2024; cadastro não implementado."),
    ("Economia", "Juros futuros caíram 2% desde que chegou ao 2º turno", "Impreciso", "Caíram menos: DI jan/2028 de 13,51% para 12,6%."),
    ("Fiscal & Contas Públicas", "Dívida de R$ 11 tri é \"mais um recorde negativo\"", "Impreciso", "Recorde só em reais nominais; em % do PIB o pico foi 2020 (governo Bolsonaro)."),
    ("Social", "Bolsonaro elevou o Bolsa Família a no mínimo R$ 600", "Impreciso", "Os R$ 600 eram temporários até dez/2022; mantidos pela PEC da Transição."),
    ("Social", "Bolsa Família subiu \"três reais por dia\", primeiro aumento em quatro anos", "Verdadeiro", "Piso subiu R$ 91/mês, primeiro reajuste desde mar/2023."),
    ("Corrupção & Escândalos", "Careca do INSS pagou algo ao filho de Lula", "Impreciso", "Relatório cita mesada com base em testemunha; quebra de sigilo não achou pagamentos diretos."),
    ("Corrupção & Escândalos", "Frei Chico é vice de sindicato que \"roubou os aposentados\"", "Impreciso", "Sindnapi é investigado; Frei Chico não é alvo direto."),
    ("Corrupção & Escândalos", "Bolsonaro mandou MP contra corrupção no INSS e a culpa é do PT", "Impreciso", "Emenda que enfraqueceu a MP veio de deputado do PSB com apoio do PT; Bolsonaro sancionou a lei de 2022."),
    ("Corrupção & Escândalos", "Lulinha mora na Espanha", "Verdadeiro", "Cobertura das investigações o situa na Espanha."),
    ("Corrupção & Escândalos", "Cerca de 5 milhões de aposentados foram roubados", "Verdadeiro", "5,1 milhões pediram e receberam ressarcimento."),
    ("Política & Instituições", "PT governou 20 dos últimos 24 anos", "Impreciso", "Foram cerca de 17 anos."),
    ("Corrupção & Escândalos", "Dos presentes, só Lula foi condenado e preso por corrupção", "Impreciso", "Ficou 580 dias preso, mas as condenações foram anuladas pelo STF (8 a 3)."),
    ("Política & Instituições", "73% dos presos votaram em Lula", "Impreciso", "Em 2022 foram 79,8% em seções prisionais; só presos provisórios votam (~4.900 votos)."),
    ("Política & Instituições", "Lula foi condenado pelo TSE várias vezes por fake news", "Impreciso", "Há um direito de resposta, não \"várias\" condenações."),
    ("Política & Instituições", "Mais de 50 milhões escolheram a mudança", "Verdadeiro", "Flávio teve 56.104.503 votos no 1º turno."),
    ("Política & Instituições", "É a sétima eleição presidencial de Lula", "Verdadeiro", "1989, 1994, 1998, 2002, 2006, 2022 e 2026."),
    ("Trajetória dos candidatos", "Cláudio Lottenberg presidiu o Albert Einstein", "Verdadeiro", "Presidente executivo 2001–2016."),
    ("Relações Exteriores", "Governo \"não mandou ninguém\" aos EUA no tarifaço", "Falso", "Alckmin negociou com o Secretário de Comércio; Mauro Vieira foi a Washington."),
    ("Relações Exteriores", "\"Ninguém trabalhou para tarifar\"", "Impreciso", "Trump ligou a tarifa ao julgamento de Jair Bolsonaro; Eduardo fez lobby nos EUA."),
    ("Relações Exteriores", "Maduro está preso e Lula mandou o vice à posse no Irã", "Verdadeiro", "EUA capturaram Maduro em jan/2026; Alckmin foi à posse iraniana em 2024."),
    ("Saúde", "Lula tomou a vacina que Bolsonaro comprou", "Verdadeiro", "Contrato da CoronaVac em jan/2021; Lula vacinado em mar/2021."),
]:
    add(F, "band", "rank", u, tema, fala, ver, expl)

# ---------------------------------------------------------------- Aos Fatos — debate Band (apenas vereditos explícitos)
u = URL["af_band"]
add(F, "band", "af", u, "Corrupção & Escândalos", "\"Careca do INSS\" fazia parte do governo Lula", "Falso", "Rótulo FALSO publicado pelo Aos Fatos.")
add(F, "band", "af", u, "Segurança Pública", "\"A criminalidade explodiu no Brasil\"", "Falso", "Mortes violentas caíram para o menor nível da série em 2025.")
add(F, "band", "af", u, "Economia", "Recorde de empresas fechadas no atual governo", "Falso", "Recorde de falências foi em 2015.")
add(F, "band", "af", u, "Fiscal & Contas Públicas", "Lula e Janja gastaram R$ 7 bi em viagens", "Falso", "O valor é de todo o governo federal.")
add(F, "band", "af", u, "Relações Exteriores", "Governo Lula não fez nada contra o tarifaço dos EUA", "Falso", "Houve mais de 30 reuniões desde jul/2025.")
add(F, "band", "af", u, "Segurança Pública", "Governo Lula considera abusadores de crianças doentes, não criminosos", "Falso", "Rótulo FALSO publicado pelo Aos Fatos.")
add(L, "band", "af", u, "Economia", "Após sair, o país só cresceu mais de 3% quando ele voltou", "Falso", "PIB cresceu mais de 3% em 2011, 2021 e 2022.")

# ---------------------------------------------------------------- Estadão Verifica — debate Band (texto original da página)
u = URL["est_band"]
for cand, tema, fala, ver, expl in [
    (L, "Economia", "Foi o primeiro presidente a conseguir dois graus de investimento", "Verdadeiro", "Fitch e S&P concederam o grau de investimento em 2008 e a Moody's em 2009, no 2º mandato de Lula."),
    (L, "Economia", "O Brasil crescia 7,5% e só voltou a crescer mais de 3,5% quando ele retornou", "Enganoso", "O PIB cresceu 7,5% em 2010, mas também 4,6% em 2021 (dado citado pelo Estadão), sob Bolsonaro."),
    (L, "Economia", "Seu governo criou o MEI e há 17,5 milhões de MEIs", "Verdadeiro", "Há 17,56 milhões de MEIs ativos; a figura foi criada em 2008."),
    (L, "Economia", "Devia US$ 30 bi ao FMI em 2003; pagou e deixou US$ 270 bi em reservas", "Verdadeiro", "Dívida de US$ 30,4 bi contraída em 2002 e quitada antecipadamente em 2005."),
    (L, "Corrupção & Escândalos", "O governo já devolveu R$ 3,5 bi aos afetados pelos descontos do INSS", "Verdadeiro", "DataPrev: R$ 3,52 bi pagos a 5 milhões de aposentados e pensionistas."),
    (L, "Trajetória dos candidatos", "Flávio contou 43 mentiras sobre seu envolvimento com Vorcaro", "Verdadeiro", "Referência a levantamento do Aos Fatos sobre as declarações de Flávio a respeito do banqueiro."),
    (L, "Corrupção & Escândalos", "Flávio comprou uma casa de R$ 10 milhões", "Exagerado", "A mansão no Lago Sul custou R$ 6,2 milhões, segundo a declaração de bens."),
    (L, "Trajetória dos candidatos", "Jair Bolsonaro mentia 11 vezes por dia", "Exagerado", "Artigo 19 e Aos Fatos contaram pouco mais de quatro declarações falsas ou enganosas por dia."),
    (L, "Trajetória dos candidatos", "Dos 49 deputados estaduais, Flávio foi o único a votar contra ampliar a licença-maternidade", "Verdadeiro", "Em 2009, foi o único voto contra ampliar de 120 para 180 dias a licença das servidoras."),
    (L, "Política & Instituições", "Na manifestação pró-Flávio havia um torpedo americano", "Verdadeiro", "Manifestantes levaram um míssil inflável à Avenida Paulista com a frase \"Trump nuke Brazil\"."),
    (L, "Economia", "Flávio já falou que quer privatizar 95% das estatais", "Verdadeiro", "Declaração na CEO Conference 2026 do BTG Pactual."),
    (L, "Economia", "O governo Bolsonaro não ajustou o salário mínimo acima da inflação em nenhum ano", "Enganoso", "Em 2019 houve ganho real de 1,14% (R$ 998); nos outros três anos, não."),
    (L, "Saúde", "Mais Médicos chegou a 18 mil, tinha 12 mil quando ele voltou e hoje tem 27 mil", "Impreciso", "Eram 18,2 mil em 2015 e 13,7 mil no início de 2023, não 12 mil."),
    (F, "Segurança Pública", "Com a Lei Antifacção, líderes de facções vão ficar 80 anos presos", "Enganoso", "A pena pode dobrar para 80 anos, mas o Código Penal limita o cumprimento a 40."),
    (F, "Política & Instituições", "O PT governou o país em 20 dos últimos 24 anos", "Exagerado", "Somando Lula e Dilma, o PT governou cerca de 17 anos e 4 meses."),
    (F, "Corrupção & Escândalos", "O filme de Lula recebeu R$ 30 milhões \"por fora\" de Vorcaro no Instituto Lula", "Falta contexto", "A Veja citou áudios, mas a PF afirmou que Vorcaro não prestou depoimento com esse teor nem entregou documentos."),
    (F, "Fiscal & Contas Públicas", "Lula gastou R$ 7 bilhões com viagens da primeira-dama Janja", "Enganoso", "Os R$ 7,35 bi referem-se a viagens de cerca de 475 mil pessoas de 34 órgãos federais (jan/2023–mai/2026), não só da Presidência."),
    (F, "Corrupção & Escândalos", "O irmão de Lula é vice de um sindicato que roubou os aposentados", "Falta contexto", "Frei Chico é diretor do Sindnapi, investigado na Operação Sem Desconto, mas ele próprio não é investigado."),
    (F, "Corrupção & Escândalos", "Bolsonaro mandou MP contra a corrupção no INSS e o PT foi contra", "Falta contexto", "A MP 871/2019 previa revalidação anual; o Congresso a flexibilizou e, em 2022, a regra foi alterada de novo."),
    (F, "Política & Instituições", "Lula recebeu 73% dos votos nos presídios", "Falta contexto", "Foram 72,6% dos votos válidos em seções de presídios, que incluem agentes e servidores; só presos provisórios votam."),
    (F, "Segurança Pública", "\"Nunca quis tirar\" a identificação das munições", "Falso", "Flávio apoiou o PL 3.723/2019, que revogava a exigência de rastreio em munições e armas."),
    (F, "Política & Instituições", "Lula está dando emprego a condenados do Mensalão", "Falso", "Não há registro de cargos para condenados do Mensalão no 3º mandato."),
    (F, "Economia", "O governo Lula tem recorde de empresas fechando", "Falta contexto", "Houve mais CNPJs baixados, mas 2025 teve recorde de aberturas (5,1 milhões contra 2,8 milhões encerrados)."),
    (F, "Segurança Pública", "Pela proposta de Lula, traficantes ficariam fora da redução da maioridade penal", "Enganoso", "A Constituição equipara o tráfico a crime hediondo, incluído na proposta discutida pelo PT."),
    (F, "Segurança Pública", "Mais de 40 milhões de brasileiros moram em áreas dominadas por facções", "Subestimado", "Estudos estimam 50 milhões (Cambridge) e 68 milhões (FBSP/Datafolha)."),
    (F, "Segurança Pública", "Lula entrou na Justiça para garantir a volta da saidinha", "Enganoso", "Não há registro; Lula vetou parcialmente o fim da saidinha em 2024, e o veto foi derrubado."),
    (F, "Corrupção & Escândalos", "Lula se reuniu com Haddad, Galípolo e Vorcaro prometendo ajudar o Banco Master", "Enganoso", "Houve encontro fora da agenda em dez/2024, mas, segundo o Estadão, Lula disse que cabia ao BC tratar o caso de forma técnica."),
    (F, "Economia", "Chegar na frente no 1º turno fez os juros futuros caírem 2%", "Verdadeiro", "A queda das taxas futuras passou de 2% nos dias seguintes ao 1º turno, atribuída pelo mercado à liderança de Flávio."),
]:
    add(cand, "band", "est", u, tema, fala, ver, expl)


# ---------------------------------------------------------------- Agrupamento de falas repetidas
# A mesma fala aparece checada por várias agências e, às vezes, repetida pelo candidato
# em mais de um evento. Cada regra: (candidato, trechos que identificam a fala, chave, título único).
# A primeira regra que casar vence — por isso as mais específicas vêm antes.
GRUPOS = [
    (L, ["2,8%"], "L-deficit", "\"Ficou um déficit de 2,8%\" — atribuído ao governo Bolsonaro"),
    (L, ["FMI"], "L-fmi", "Pagou US$ 30 bi ao FMI e deixou reservas elevadas"),
    (L, ["superávit de 0,1% é inédito", "primeira vez que apresenta"], "L-superavit-inedito", "Orçamento com superávit é inédito"),
    (L, ["2027 prevê superávit", "superávit de 0,1%\""], "L-orcamento-2027", "Orçamento de 2027 prevê superávit primário"),
    (L, ["só cresceu 3%", "só voltou a crescer acima", "só cresceu mais de 3%", "só cresceu acima de 3%", "voltou a crescer mais de 3,5%"], "L-pib-3", "O país só voltou a crescer acima de 3% quando Lula voltou"),
    (L, ["crescendo 7,5%", "cresceu 7,5%", "crescia 7,5%", "sétima economia"], "L-pib-2010", "O Brasil crescia 7,5% e era a 7ª economia do mundo (2010)"),
    (L, ["mentia 11 vezes"], "L-mentia", "Jair Bolsonaro mentia 11 vezes por dia"),
    (L, ["privatizar 95%"], "L-95", "Flávio falou em privatizar 95% das estatais"),
    (L, ["R$ 3,5 bi"], "L-inss-devolucao", "O governo já devolveu R$ 3,5 bi aos aposentados lesados no INSS"),
    (L, ["43 mentiras", "mentiu 43 vezes"], "L-43", "Flávio contou 43 mentiras sobre o caso Vorcaro"),
    (L, ["17,5 milhões de MEIs"], "L-meis", "O Brasil tem 17,5 milhões de MEIs"),
    (L, ["Luchsinger"], "L-luchsinger", "\"Eu não conheço essa moça\" (Roberta Luchsinger)"),
    (L, ["fome"], "L-fome", "Acabou com a fome"),
    (L, ["22 milhões de empregos"], "L-22mi", "Criou 22 milhões de empregos em oito anos"),
    (L, ["99%"], "L-99", "Aprovou 99% do que queria no Congresso"),
    (L, ["EUA caiu 9%", "9% no comércio com EUA"], "L-comercio", "Comércio com os EUA caiu 9% e com a China subiu 20%"),
    (L, ["Canella"], "L-canella", "Márcio Canella, preso, tinha a mãe de Flávio como suplente"),
    (L, ["MEI\"", "dívidas de MEI", "dívida dos MEI"], "L-mei", "Perdoou R$ 12,6–12,7 bi em dívidas de MEIs"),
    (L, ["Antifacção"], "L-antifaccao", "Criou a Lei Antifacção e aumentou as penas"),
    (L, ["hediondo", "Estuprador"], "L-saidinha", "Condenados por crimes hediondos não têm saidinha"),
    (L, ["cesta"], "L-cestas", "Salário mínimo comprava 1,8 cesta; hoje compra 2,2"),
    (L, ["56"], "L-alimentos", "Inflação de alimentos: 56% com Bolsonaro, 13% com Lula"),
    (L, ["Simples"], "L-simples", "Criou o Simples"),
    (L, ["PIB industrial"], "L-pib-industrial", "O PIB industrial cresceu 3,4%"),
    (L, ["milhão de armas", "1 bilhão e 100 milhões"], "L-armas", "Governo Bolsonaro liberou 1 milhão de armas e 1,1 bilhão de balas"),
    (L, ["licença-maternidade"], "L-licenca", "Flávio foi o único a votar contra a licença-maternidade de 6 meses"),
    (L, ["Escritório do Crime"], "L-nobrega", "Flávio empregou parentes do chefe do Escritório do Crime"),
    (L, ["preço de banana", "troco de banana"], "L-petrobras", "Bolsonaro privatizou a Petrobras \"a preço de banana\""),
    (L, ["Mais Médicos"], "L-mais-medicos", "Mais Médicos tinha 12 mil médicos e hoje tem 27 mil"),
    (L, ["R$ 10 mi", "R$ 10 milhões", "casa de R$ 10"], "L-mansao", "A casa de Flávio custou R$ 10 milhões"),
    (L, ["salário mínimo pela inflação", "aumento real ao salário mínimo", "salário mínimo acima da inflação"], "L-minimo", "Bolsonaro nunca deu aumento real ao salário mínimo"),
    (F, ["11 tri", "R$ 11 tri"], "F-divida", "A dívida pública está em R$ 11 trilhões, recorde negativo"),
    (F, ["80 anos"], "F-antifaccao", "Com a Lei Antifacção, líderes ficam até 80 anos presos"),
    (F, ["documentário", "R$ 30 milhões para o Instituto Lula", "por fora"], "F-vorcaro-lula", "Vorcaro pagou R$ 30 milhões a documentário/Instituto Lula"),
    (F, ["triplicou", "no mínimo R$ 600"], "F-bolsa", "Bolsonaro triplicou o Bolsa Família para R$ 600"),
    (F, ["R$ 7 bi", "R$ 7 bilhões"], "F-viagens", "Lula e Janja gastaram R$ 7 bilhões em viagens"),
    (F, ["criminalidade"], "F-crime", "A criminalidade explodiu / governo é recordista em criminalidade"),
    (F, ["Maré"], "F-dino", "Flávio Dino entrou na Maré sem policiais"),
    (F, ["CACs", "tese sobre armas"], "F-cacs", "A queda de homicídios em 2019 se deveu às armas de CACs"),
    (F, ["Santos"], "F-santos", "Santos é o 2º maior porto exportador de cocaína do mundo"),
    (F, ["mulheres assassinadas", "mulher assassinada"], "F-feminicidio", "Governo é recordista em mulheres assassinadas"),
    (F, ["prestou contas", "já tá apresentada"], "F-dark-horse", "A produtora do filme Dark Horse já prestou contas de tudo"),
    (F, ["empresas fechadas", "empresas fechando"], "F-empresas", "Governo é recordista em empresas fechadas"),
    (F, ["tarifaço", "não mandou ninguém", "defender as empresas"], "F-tarifaco", "O governo não fez nada contra o tarifaço dos EUA"),
    (F, ["vetou o fim da saidinha", "vetou a saidinha"], "F-saidinha", "Lula vetou o fim da saidinha"),
    (F, ["acionou a justiça", "entrou na Justiça"], "F-saidinha-justica", "Lula acionou a Justiça para a saidinha voltar"),
    (F, ["40 milhões"], "F-areas-faccoes", "Mais de 40 milhões moram em áreas dominadas por facções"),
    (F, ["juros futuros"], "F-juros", "Chegar à frente no 1º turno derrubou os juros futuros em 2%"),
    (F, ["20 dos últimos 24"], "F-pt-20", "O PT governou 20 dos últimos 24 anos"),
    (F, ["Frei Chico", "irmão de Lula"], "F-frei-chico", "O irmão de Lula é vice de sindicato que roubou aposentados"),
    (F, ["MP contra corrupção", "MP contra a corrupção"], "F-mp-inss", "Bolsonaro mandou MP contra a corrupção no INSS e o PT foi contra"),
    (F, ["73%"], "F-presos", "73% dos presos votaram em Lula"),
    (F, ["condenado no STJ", "só Lula foi condenado"], "F-condenado", "Lula foi condenado em todas as instâncias"),
    (F, ["Lottenberg"], "F-lottenberg", "Cláudio Lottenberg presidiu o Albert Einstein"),
    (F, ["Pix"], "F-pix", "O Pix foi criado no governo Bolsonaro e é gratuito por exigência dele"),
]

# ---------------------------------------------------------------- Contrapontos
# Argumentos de cada lado e de veículos com linhas editoriais diferentes, além das agências.
# "lado": a favor de quem o argumento pesa (candidato que fez a fala / contra a fala).
CP = {
    "poder_haddad": "https://www.poder360.com.br/economia/deficit-fiscal-ja-seria-de-r-130-bi-sob-bolsonaro-diz-haddad/",
    "gazeta_haddad": "https://www.gazetadopovo.com.br/economia/haddad-rombo-230-bilhoes-parte-herdada-bolsonaro/",
    "oeste_mises": "https://revistaoeste.com/politica/instituto-mises-contesta-declaracoes-de-lula-em-debate/",
    "metropoles_viagens": "https://www.metropoles.com/brasil/gastos-com-viagens-a-servico-somam-r-7-bilhoes-no-governo-lula",
    "oeste_viagens": "https://revistaoeste.com/politica/governo-lula-atinge-maior-gasto-com-diarias-e-passagens-em-11-anos/",
    "datafolha_crime": "https://www.diariodepernambuco.com.br/brasil/2026/05/11713943-41-dos-brasileiros-convivem-com-o-crime-organizado-na-vizinhanca.html",
    "faccoes_28mi": "https://www.maisgoias.com.br/brasil/faccoes-e-milicias-ja-atingem-28-milhoes-de-brasileiros-diz-estudo/",
    "anuario_2026": "https://www.jb.com.br/brasil/2026/07/1060384-brasil-tem-menor-taxa-de-mortes-violentas-intencionais-desde-2012.html",
    "camara_auxilio": "https://www.camara.leg.br/noticias/877290-ENTRA-EM-VIGOR-A-LEI-QUE-TORNA-PERMANENTE-O-AUXILIO-BRASIL-DE-R%24-400",
    "opovo_6x1": "https://mais.opovo.com.br/jornal/economia/2026/10/14/fim-da-escala-6x1-sem-reducao-de-salario-e-aprovado-no-senado.html",
}
CONTRAPONTOS = {
    "L-deficit": [
        ("A favor de Lula", "Poder360 / Gazeta do Povo", "Haddad argumenta que cerca de metade do déficit de R$ 230,5 bi de 2023 foi herança: R$ 92,4 bi em precatórios adiados pela PEC de 2021 e compensação aos estados pelo corte de ICMS de 2022. Sem os precatórios, o déficit de 2023 cairia para 1,3% do PIB.", CP["poder_haddad"]),
        ("A favor de Lula", "Aos Fatos", "Na entrevista de 15/10, o Aos Fatos leu a mesma fala como referência ao déficit do 1º ano do governo Lula e a registrou como fato, com a ressalva de que o TCU aponta 2,4% do PIB.", URL["af_l_out"]),
        ("Contra a fala", "Instituto Mises (via Revista Oeste)", "Reforça que o governo central fechou 2022 com superávit de R$ 54,1 bi; o déficit de R$ 228,5 bi surgiu em 2023, já no governo Lula.", CP["oeste_mises"]),
    ],
    "L-pib-3": [
        ("A favor de Lula", "Secom (via Agência Lupa)", "O governo argumenta que o crescimento médio entre 2011 e 2022 ficou abaixo de 1% ao ano, e que só agora houve três anos seguidos perto ou acima de 3%.", URL["lupa_l_ago"]),
        ("A favor de Lula", "Assessoria de Lula (via Estadão Verifica)", "O crescimento de 2021 reflete o efeito-base da recessão de 2020 (-3,3%); a média do mandato de Lula fica perto de 3% ao ano, contra 1,4% no governo Bolsonaro.", URL["est_band"]),
        ("Contra a fala", "Instituto Mises (via Revista Oeste)", "Lista anos acima de 3% fora dos governos Lula: 3,9% (2011), 4,8% (2021) e 3,0% (2022).", CP["oeste_mises"]),
    ],
    "L-cestas": [
        ("A favor de Lula", "DIEESE (via Agência Lupa)", "O poder de compra subiu de fato: 1,62 cesta em ago/2022 para 1,80 em ago/2026 (+11%); o ponto mais baixo do governo anterior foi 1,5 cesta (abr/2022).", URL["lupa_band"]),
        ("Contra a fala", "Instituto Mises (via Revista Oeste)", "O número citado (2,2 cestas) não aparece em nenhuma série: o correto é 1,8.", CP["oeste_mises"]),
    ],
    "L-simples": [
        ("A favor de Lula", "Ranking dos Políticos", "Lei Geral da Microempresa, Simples Nacional (2006), Super Simples e MEI (2008) foram criados nos governos Lula.", URL["rank_band"]),
        ("Contra a fala", "Instituto Mises (via Revista Oeste)", "O primeiro Simples federal é de 1996, governo FHC.", CP["oeste_mises"]),
    ],
    "L-fome": [
        ("A favor de Lula", "ONU/FAO (via Agência Lupa)", "O relatório SOFI 2025 tirou o Brasil do Mapa da Fome, com subnutrição abaixo de 2,5% da população — pela segunda vez (a primeira foi em 2014).", URL["lupa_l_ago"]),
        ("Contra a fala", "Agência Lupa / Aos Fatos", "Sair do Mapa não é erradicar a fome: 1,2 milhão de pessoas seguem em insegurança alimentar grave e 44,8 milhões não conseguem pagar uma dieta saudável.", URL["af_l_ago"]),
    ],
    "L-99": [
        ("A favor de Lula", "Aos Fatos / O Povo", "A agenda prioritária passou: reforma tributária, arcabouço fiscal, isenção do IR até R$ 5 mil e a PEC do fim da escala 6x1 (aprovada no Senado por 75 a 1 em 14/10/2026).", CP["opovo_6x1"]),
        ("Contra a fala", "Aos Fatos / Ranking dos Políticos", "Congresso derrubou vetos (marco temporal, licenciamento ambiental, desoneração), rejeitou indicado ao STF e só ~23% das MPs viraram lei.", URL["af_l_out"]),
    ],
    "L-armas": [
        ("A favor de Lula", "Instituto Sou da Paz (via Ranking dos Políticos)", "O acervo de CACs passou de cerca de 350 mil para mais de 1 milhão de armas, e foram vendidas 994 milhões de munições no período.", URL["rank_band"]),
        ("Contra a fala", "Agência Lupa", "O número exato de \"1,1 bilhão de balas\" não aparece em nenhuma base pública; só em material de campanha.", URL["lupa_band"]),
    ],
    "F-viagens": [
        ("A favor de Flávio", "Metrópoles / Revista Oeste", "O valor existe: R$ 7 bi em viagens a serviço de 2023 a 2025 (Portal da Transparência), mais que 2017–2022 somados; 2024 foi o recorde da série (R$ 2,37 bi). Com locomoção, 2025 teve o maior gasto desde 2014. O Estadão classificou a fala como \"enganosa\", e não \"falsa\".", CP["metropoles_viagens"]),
        ("Contra a fala", "Agência Lupa / Aos Fatos", "O total é de todo o governo federal (ministérios e órgãos), não de Lula e Janja — cujas viagens em aviões da FAB nem entram nesse número.", URL["lupa_band"]),
    ],
    "F-crime": [
        ("A favor de Flávio", "Datafolha / Fórum Brasileiro de Segurança Pública", "Facções e milícias já atuam nos bairros de 19% da população (28,5 milhões, +5 pontos em um ano); 41% dizem ver o crime organizado na vizinhança. Feminicídios e mortes por intervenção policial bateram recorde em 2025.", CP["faccoes_28mi"]),
        ("Contra a fala", "Anuário Brasileiro de Segurança Pública 2026", "As mortes violentas caíram 8,2% em 2025, para 19,1 por 100 mil — menor taxa desde 2012; roubos de celular caíram 37% desde 2022.", CP["anuario_2026"]),
    ],
    "F-bolsa": [
        ("A favor de Flávio", "Agência Câmara", "A Lei 14.342/2022, originada de medida provisória de Bolsonaro, tornou permanente o piso de R$ 400 do Auxílio Brasil — cerca do dobro da média do antigo Bolsa Família (R$ 187,91 em jan/2019, segundo a Lupa).", CP["camara_auxilio"]),
        ("Contra a fala", "Agência Lupa / Ranking dos Políticos", "Os R$ 600 valiam só até dez/2022, e a proposta de orçamento de 2023 do próprio governo previa R$ 400; o valor foi mantido pela PEC da Transição.", URL["lupa_band"]),
    ],
    "F-condenado": [
        ("A favor de Flávio", "Agência Lupa / Aos Fatos", "Lula foi condenado em 1ª instância, pelo TRF-4 e teve a condenação do triplex mantida pelo STJ (2019); o STF anulou os processos por incompetência da vara de Curitiba, sem julgar o mérito.", URL["af_l_ago"]),
        ("Contra a fala", "Agência Lupa", "O STF nunca confirmou as condenações: anulou-as em 2021, sem julgar o mérito, e os casos prescreveram.", URL["lupa_band"]),
    ],
    "F-divida": [
        ("A favor de Flávio", "Banco Central (SGS 13762)", "A dívida bruta subiu de 71,7% do PIB (dez/2022) para 82,9% (ago/2026) — alta de 11 pontos em menos de quatro anos.", "https://www3.bcb.gov.br/sgspub/"),
        ("Contra a fala", "Ranking dos Políticos", "Em reais nominais é recorde, mas em % do PIB o pico da série foi 2020 (87%), no governo Bolsonaro.", URL["rank_band"]),
    ],
    "F-antifaccao": [
        ("A favor de Flávio", "Ranking dos Políticos", "Com agravantes, a pena aplicada pode de fato chegar a 80 anos.", URL["rank_band"]),
        ("Contra a fala", "Agência Lupa / Estadão Verifica", "O Código Penal limita o tempo efetivo de prisão a 40 anos.", URL["lupa_band"]),
    ],
    "F-dark-horse": [
        ("A favor de Flávio", "Defesa da produtora (via Ranking dos Políticos)", "A produtora apresentou à Justiça um balanço de cerca de R$ 75,2 mi elaborado por perito.", URL["rank_jn_f"]),
        ("Contra a fala", "Aos Fatos / Agência Lupa", "A perícia não traz notas, recibos nem extratos, e não esclarece a origem dos recursos do fundo Havengate; a PF investiga.", URL["af_f_out"]),
    ],
    "F-tarifaco": [
        ("A favor de Flávio", "Agência Lupa", "Na audiência pública do USTR de julho, o governo de fato só enviou diplomatas da embaixada como observadores, enquanto Flávio participou.", URL["lupa_band"]),
        ("Contra a fala", "Ranking dos Políticos / Lupa", "Alckmin negociou com o Secretário de Comércio dos EUA, Mauro Vieira foi a Washington e houve mais de 30 reuniões desde jul/2025.", URL["rank_band"]),
    ],
    "F-presos": [
        ("A favor de Flávio", "TSE (via Agência Lupa)", "O número procede: Lula teve 72,57% dos votos válidos nas seções eleitorais em presídios no 1º turno.", URL["lupa_band"]),
        ("Contra a fala", "Ranking dos Políticos", "Só presos provisórios votam (poucos milhares de votos), e as seções incluem agentes e funcionários — não representam \"os presidiários\".", URL["rank_band"]),
    ],
    "F-pix": [
        ("A favor de Flávio", "Agência Lupa", "O Pix foi de fato lançado em novembro de 2020, já no governo Bolsonaro.", URL["lupa_f_ago"]),
        ("Contra a fala", "Agência Lupa", "O projeto foi concebido em 2018 no governo Temer, e a gratuidade para pessoas físicas é regra do BC, sem evidência de exigência presidencial.", URL["lupa_f_ago"]),
    ],
}


def agrupar(cand, fala, id_):
    for c, trechos, chave, titulo in GRUPOS:
        if c == cand and any(t.lower() in fala.lower() for t in trechos):
            return chave, titulo
    return f"u{id_}", fala


SEVERIDADE = {"Verdade": 0, "Meia-verdade": 1, "Sem comprovação": 2, "Mentira": 3}


def consolidar(checagens):
    """Uma linha por fala única, com os vereditos de todas as agências e eventos."""
    grupos = {}
    for c in checagens:
        grupos.setdefault(c["chave"], []).append(c)
    falas = []
    for chave, itens in grupos.items():
        cats = [i["categoria"] for i in itens]
        contagem = {k: cats.count(k) for k in set(cats)}
        maximo = max(contagem.values())
        empatadas = [k for k, v in contagem.items() if v == maximo]
        # Empate entre faixas: vereditos opostos viram "Meia-verdade" quando ela está no empate;
        # senão fica a faixa menos grave. Em ambos os casos a fala é marcada como divergente.
        categoria = "Meia-verdade" if "Meia-verdade" in empatadas else min(empatadas, key=SEVERIDADE.get)
        primeiro = min(itens, key=lambda i: (i["data"], i["id"]))
        falas.append({
            "chave": chave,
            "candidato": primeiro["candidato"],
            "fala": primeiro["titulo_fala"],
            "tema": primeiro["tema"],
            "categoria": categoria,
            "divergencia": len(contagem) > 1,
            "n_checagens": len(itens),
            "eventos": sorted({f'{i["evento"]} ({i["data"][8:10]}/{i["data"][5:7]})' for i in itens}),
            "repetida_em_eventos": len({i["data"] for i in itens}),
            "primeira_data": primeiro["data"],
            "vereditos": [{"agencia": i["agencia"], "veredito": i["veredito_original"], "categoria": i["categoria"],
                           "evento": i["evento"], "data": i["data"], "explicacao": i["explicacao"], "url": i["fonte_url"],
                           "afirmacao": i["afirmacao"]} for i in sorted(itens, key=lambda x: (x["data"], x["agencia"]))],
            "contrapontos": [{"lado": lado, "fonte": fonte, "texto": texto, "url": url}
                             for lado, fonte, texto, url in CONTRAPONTOS.get(chave, [])],
        })
    return sorted(falas, key=lambda f: (f["primeira_data"], f["candidato"]))


def main():
    out = []
    for i, (cand, ev, ag, url, tema, fala, ver, expl) in enumerate(R, start=1):
        nome_ev, data = EVENTOS[ev]
        chave, titulo = agrupar(cand, fala, i)
        out.append({
            "id": i,
            "chave": chave,
            "titulo_fala": titulo,
            "candidato": cand,
            "evento": nome_ev,
            "data": data,
            "agencia": AGENCIA[ag],
            "tema": tema,
            "afirmacao": fala,
            "veredito_original": ver,
            "categoria": CATEGORIA[ver],
            "explicacao": expl,
            "fonte_url": url,
        })
    payload = {
        "metadados": {
            "titulo": "Checagens de fatos — Lula (PT) x Flávio Bolsonaro (PL), eleição presidencial 2026",
            "atualizado_em": "2026-10-20",
            "cobertura": "Entrevistas na TV Globo (27–28/08 e 15–16/10) e debate da Band (18/10). Lula e Flávio não compareceram ao debate do 1º turno (Band, 23/08), e os demais debates do 1º turno foram cancelados.",
            "categorias": {
                "Verdade": "Verdadeiro, correto (inclui 'verdadeiro com ressalva').",
                "Meia-verdade": "Impreciso, exagerado, subestimado, enganoso, falta contexto ou omissão.",
                "Mentira": "Falso.",
                "Sem comprovação": "Insustentável / não há evidência pública que sustente a fala.",
            },
            "aviso": "Cada linha é uma checagem de uma agência. Agências escolhem quais falas checar e usam escalas diferentes; a mesma fala pode aparecer mais de uma vez com vereditos distintos. Contagens não medem 'quem mente mais' de forma absoluta.",
            "placares_oficiais": [
                {"agencia": "Ranking dos Políticos", "evento": "Debate Band (18/10)", "candidato": "Lula", "verdadeiro": 15, "impreciso": 23, "falso": 9, "url": URL["rank_band"]},
                {"agencia": "Ranking dos Políticos", "evento": "Debate Band (18/10)", "candidato": "Flávio Bolsonaro", "verdadeiro": 13, "impreciso": 13, "falso": 3, "url": URL["rank_band"]},
                {"agencia": "Ranking dos Políticos", "evento": "Entrevista Globo (15/10)", "candidato": "Lula", "verdadeiro": 8, "impreciso": 11, "falso": 8, "url": URL["rank_jn_l"]},
                {"agencia": "Ranking dos Políticos", "evento": "Entrevista Globo (16/10)", "candidato": "Flávio Bolsonaro", "verdadeiro": 9, "impreciso": 12, "falso": 5, "url": URL["rank_jn_f"]},
            ],
        },
        "checagens": out,
        "falas_unicas": consolidar(out),
    }
    sem_cp = [k for k in CONTRAPONTOS if k not in {c["chave"] for c in out}]
    if sem_cp:
        print("AVISO: contrapontos sem fala correspondente:", sem_cp)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"{len(out)} checagens gravadas em {OUT}")


if __name__ == "__main__":
    main()
