"""
Gera data/leis_sancionadas.json: principais leis, leis complementares e emendas constitucionais
sancionadas/promulgadas em cada governo. Números e datas foram conferidos no texto oficial (Planalto).

Cada linha: (governo, data ISO, norma, tipo, área, resumo, situação, [manchete, url_imprensa])
Execute:  python data/_fontes/gerar_leis.py
"""
import json
import os
import re

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leis_sancionadas.json")
PL = "https://www.planalto.gov.br/ccivil_03/"
B, L = "Bolsonaro", "Lula"


def url_oficial(norma, data):
    ano = int(data[:4])
    num = re.search(r"([\d\.]+)/", norma).group(1).replace(".", "")
    if norma.startswith("EC "):
        return f"{PL}constituicao/emendas/emc/emc{num}.htm"
    if norma.startswith("LC "):
        return f"{PL}leis/lcp/Lcp{num}.htm"
    pasta = "_ato2019-2022" if ano <= 2022 else "_ato2023-2026"
    prefixo = "l" if num in ("15397", "15418") else "L"
    return f"{PL}{pasta}/{ano}/lei/{prefixo}{num}.htm"


CAMARA = "https://www.camara.leg.br/noticias/"
LUPA = "https://www.agencialupa.org/checagem/2026/10/18/ao-vivo-checagem-do-debate-entre-lula-e-flavio-bolsonaro-na-band/"

LEIS = [
    # ---------------- Bolsonaro
    (B, "2019-09-05", "Lei 13.869/2019", "Lei", "Instituições", "Define os crimes de abuso de autoridade; sancionada com 36 dispositivos vetados.", "Em vigor",
     "Bolsonaro sanciona lei de abuso de autoridade com 19 artigos vetados (Conjur)", "https://www.conjur.com.br/2019-set-05/bolsonaro-sanciona-lei-abuso-19-vetos/"),
    (B, "2019-09-20", "Lei 13.874/2019", "Lei", "Economia", "Lei da Liberdade Econômica: reduz burocracia para abrir e operar negócios de baixo risco.", "Em vigor",
     "Bolsonaro sanciona a Lei da Liberdade Econômica (Agência Câmara)", CAMARA + "588685-bolsonaro-sanciona-a-lei-da-liberdade-economica/"),
    (B, "2019-11-12", "EC 103/2019", "Emenda", "Previdência", "Reforma da Previdência: idade mínima, novas alíquotas e regras de transição.", "Em vigor", "", ""),
    (B, "2019-12-24", "Lei 13.964/2019", "Lei", "Segurança", "Pacote Anticrime: endurece penas, eleva o tempo máximo de prisão a 40 anos e cria o juiz de garantias.", "Em vigor (partes validadas pelo STF)", "", ""),
    (B, "2020-02-06", "Lei 13.979/2020", "Lei", "Saúde", "Medidas de enfrentamento da emergência de saúde pública da Covid-19.", "Encerrada", "", ""),
    (B, "2020-04-02", "Lei 13.982/2020", "Lei", "Proteção social", "Cria o Auxílio Emergencial e amplia critérios do BPC durante a pandemia.", "Encerrada", "", ""),
    (B, "2020-07-06", "Lei 14.020/2020", "Lei", "Trabalho", "Programa de Manutenção do Emprego e da Renda (BEm): redução de jornada e suspensão de contratos.", "Encerrada", "", ""),
    (B, "2020-07-15", "Lei 14.026/2020", "Lei", "Saneamento", "Novo Marco Legal do Saneamento: licitação obrigatória e metas de 99% de água e 90% de esgoto até 2033.", "Em vigor", "", ""),
    (B, "2020-08-26", "EC 108/2020", "Emenda", "Educação", "Torna o Fundeb permanente e eleva a complementação da União.", "Em vigor", "", ""),
    (B, "2020-12-24", "Lei 14.112/2020", "Lei", "Economia", "Atualiza a lei de recuperação judicial e falências.", "Em vigor", "", ""),
    (B, "2021-02-24", "LC 179/2021", "Lei Complementar", "Economia", "Autonomia do Banco Central, com mandatos fixos para presidente e diretores.", "Em vigor", "", ""),
    (B, "2021-04-01", "Lei 14.133/2021", "Lei", "Gestão pública", "Nova Lei de Licitações e Contratos Administrativos.", "Em vigor", "", ""),
    (B, "2021-04-08", "Lei 14.134/2021", "Lei", "Energia", "Nova Lei do Gás: abre o mercado de gás natural à concorrência.", "Em vigor", "", ""),
    (B, "2021-07-12", "Lei 14.182/2021", "Lei", "Energia", "Autoriza a capitalização e a privatização da Eletrobras.", "Em vigor (executada em jun/2022)", "", ""),
    (B, "2021-07-28", "Lei 14.188/2021", "Lei", "Direitos e minorias", "Cria o crime de violência psicológica contra a mulher e o programa Sinal Vermelho.", "Em vigor", "", ""),
    (B, "2021-10-25", "Lei 14.230/2021", "Lei", "Instituições", "Reforma a Lei de Improbidade Administrativa.", "Em vigor", "", ""),
    (B, "2021-12-08", "EC 113/2021", "Emenda", "Fiscal", "Novo regime de pagamento de precatórios e mudança na correção do teto de gastos.", "Em parte derrubada pelo STF (2023)", "", ""),
    (B, "2021-12-16", "EC 114/2021", "Emenda", "Fiscal", "Complementa a regra dos precatórios e abre espaço para o Auxílio Brasil (\"PEC do Calote\").", "Em parte derrubada pelo STF (2023)", "", ""),
    (B, "2021-12-23", "Lei 14.273/2021", "Lei", "Infraestrutura", "Marco Legal das Ferrovias: autorizações para ferrovias privadas.", "Em vigor", "", ""),
    (B, "2021-12-29", "Lei 14.284/2021", "Lei", "Proteção social", "Cria o Auxílio Brasil, substituto do Bolsa Família.", "Substituída pelo Bolsa Família (2023)", "", ""),
    (B, "2021-12-29", "Lei 14.286/2021", "Lei", "Economia", "Marco Legal do Câmbio: simplifica operações em moeda estrangeira.", "Em vigor", "", ""),
    (B, "2022-01-06", "Lei 14.300/2022", "Lei", "Energia", "Marco legal da geração distribuída (energia solar em telhados).", "Em vigor (alterada em 2025)", "", ""),
    (B, "2022-05-18", "Lei 14.342/2022", "Lei", "Proteção social", "Torna permanente o piso de R$ 400 do Auxílio Brasil.", "Substituída pelo Bolsa Família (2023)", "Entra em vigor a lei que torna permanente o Auxílio Brasil de R$ 400 (Agência Câmara)", CAMARA + "877290-ENTRA-EM-VIGOR-A-LEI-QUE-TORNA-PERMANENTE-O-AUXILIO-BRASIL-DE-R%24-400"),
    (B, "2022-06-23", "LC 194/2022", "Lei Complementar", "Tributário", "Considera combustíveis, energia e telecomunicações bens essenciais e limita o ICMS sobre eles.", "Em vigor (questionada no STF, ADI 7191)", "", ""),
    (B, "2022-07-14", "EC 123/2022", "Emenda", "Fiscal", "\"PEC Kamikaze\": estado de emergência que permitiu ampliar benefícios sociais em ano eleitoral.", "Encerrada (efeitos em 2022)", "", ""),
    # ---------------- Lula
    (L, "2023-06-19", "Lei 14.601/2023", "Lei", "Proteção social", "Institui o novo Bolsa Família (piso de R$ 600 e adicionais por criança e gestante).", "Em vigor", "", ""),
    (L, "2023-07-03", "Lei 14.611/2023", "Lei", "Direitos e minorias", "Igualdade salarial: relatórios de transparência para empresas com 100+ empregados.", "Em vigor", "", ""),
    (L, "2023-07-13", "Lei 14.620/2023", "Lei", "Habitação", "Retoma o Minha Casa, Minha Vida.", "Em vigor", "", ""),
    (L, "2023-08-28", "Lei 14.663/2023", "Lei", "Trabalho", "Política permanente de valorização do salário mínimo (inflação + PIB).", "Em vigor (ganho real limitado a 2,5% desde 2025)", "", ""),
    (L, "2023-08-30", "LC 200/2023", "Lei Complementar", "Fiscal", "Novo arcabouço fiscal, no lugar do teto de gastos.", "Em vigor", "", ""),
    (L, "2023-10-03", "Lei 14.690/2023", "Lei", "Economia", "Programa Desenrola Brasil e limite de 100% para juros do rotativo do cartão.", "Em vigor (nova fase em 2026)", "", ""),
    (L, "2023-12-12", "Lei 14.754/2023", "Lei", "Tributário", "Tributa fundos exclusivos e aplicações no exterior (offshore).", "Em vigor", "", ""),
    (L, "2023-12-20", "EC 132/2023", "Emenda", "Tributário", "Reforma tributária do consumo: IBS, CBS e Imposto Seletivo.", "Em implantação (até 2033)", "", ""),
    (L, "2023-12-29", "Lei 14.790/2023", "Lei", "Economia", "Regula as apostas de quota fixa (bets) e tributa as plataformas.", "Em vigor (tributação elevada em 2025)", "", ""),
    (L, "2024-01-16", "Lei 14.818/2024", "Lei", "Educação", "Cria o Pé-de-Meia: poupança para estudantes do ensino médio público.", "Em vigor", "", ""),
    (L, "2024-04-11", "Lei 14.843/2024", "Lei", "Segurança", "Restringe a saída temporária de presos (\"saidinha\"); Lula vetou parte e o Congresso derrubou o veto em 28/05/2024.", "Em vigor", "Lula vetou o fim da saidinha e o Congresso derrubou (Agência Lupa)", LUPA),
    (L, "2024-10-09", "Lei 14.994/2024", "Lei", "Direitos e minorias", "Feminicídio vira crime autônomo, com pena de 20 a 40 anos.", "Em vigor", "Entra em vigor lei que amplia para até 40 anos a pena de feminicídio (Agência Câmara)", CAMARA + "1101978-ENTRA-EM-VIGOR-LEI-QUE-AMPLIA-PARA-ATE-40-ANOS-A-PENA-PARA-CASOS-DE-FEMINICIDIO"),
    (L, "2025-01-16", "LC 214/2025", "Lei Complementar", "Tributário", "Regulamenta o IBS, a CBS e o Imposto Seletivo.", "Em implantação", "", ""),
    (L, "2025-08-08", "Lei 15.190/2025", "Lei", "Meio ambiente", "Lei Geral do Licenciamento Ambiental, sancionada com 63 vetos; o Congresso derrubou a maioria em 27/11/2025.", "Em vigor (vetos derrubados)", "\"PL da Devastação\": Congresso derruba vetos de Lula (Movimento Econômico)", "https://movimentoeconomico.com.br/meio-ambiente/2025/11/27/pl-da-devastacao-congresso-derruba-vetos-de-lula-a-lei-do-licenciamento-ambiental/"),
    (L, "2025-11-26", "Lei 15.270/2025", "Lei", "Tributário", "Isenção do IR até R$ 5 mil, imposto mínimo para altas rendas e tributação de dividendos.", "Em vigor desde jan/2026", "Aumento de impostos: o que o governo Lula criou e elevou (Ranking dos Políticos)", "https://ranking.org.br/en/articles/aumento-de-impostos-o-que-o-governo-lula-criou-e-elevou-desde-2023"),
    (L, "2026-03-24", "Lei 15.358/2026", "Lei", "Segurança", "Lei Antifacção: penas de 20 a 40 anos para organização criminosa, dobradas para líderes.", "Em vigor", "Debate da Band: \"80 anos presos\" é falta de contexto (Agência Lupa)", LUPA),
    (L, "2026-04-30", "Lei 15.397/2026", "Lei", "Segurança", "Aumenta as penas de furto, roubo, estelionato e receptação.", "Em vigor", "Debate da Band: combate à receptação de celulares (Agência Lupa)", LUPA),
    (L, "2026-05-28", "Lei 15.418/2026", "Lei", "Direitos e minorias", "Cria a Universidade Federal Indígena.", "Em vigor", "", ""),
]

AGUARDANDO = [
    (L, "2026-10-14", "PEC 221/2019 (fim da escala 6x1)", "Emenda", "Trabalho", "Reduz a jornada de 44 para 40 horas sem corte de salário; aprovada no Senado por 75 a 1.", "Aguardando promulgação",
     "Fim da escala 6x1 sem redução de salário é aprovado no Senado (O Povo)", "https://mais.opovo.com.br/jornal/economia/2026/10/14/fim-da-escala-6x1-sem-reducao-de-salario-e-aprovado-no-senado.html"),
    (L, "2026-10-16", "PLC 186/2026 (anistia de dívidas de MEI)", "Projeto de lei", "Economia", "Perdoa cerca de R$ 12,6 bi em dívidas federais de 3,6 milhões de microempreendedores.", "Aguardando sanção", "", ""),
]


def main():
    saida = []
    for linha in LEIS:
        gov, data, norma, tipo, area, resumo, situacao, manchete, url_imp = linha
        saida.append({"governo": gov, "data": data, "norma": norma, "tipo": tipo, "area": area, "resumo": resumo,
                      "situacao": situacao, "texto_oficial": url_oficial(norma, data), "manchete": manchete, "url_imprensa": url_imp})
    for linha in AGUARDANDO:
        gov, data, norma, tipo, area, resumo, situacao, manchete, url_imp = linha
        saida.append({"governo": gov, "data": data, "norma": norma, "tipo": tipo, "area": area, "resumo": resumo,
                      "situacao": situacao, "texto_oficial": "", "manchete": manchete, "url_imprensa": url_imp})
    saida.sort(key=lambda x: x["data"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"{len(saida)} normas gravadas em {OUT}")


if __name__ == "__main__":
    main()
