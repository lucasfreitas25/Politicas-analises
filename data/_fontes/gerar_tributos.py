"""
Gera data/tributos.json: tributos criados, aumentados, reduzidos e extintos em cada governo (FHC a Lula 3).

Regras do painel:
- é um levantamento do painel, não uma lista oficial: entram os tributos federais mais conhecidos, cada um com a norma conferida no Planalto;
- "Criação" = tributo ou regime de tributação novo (campo qtd diz quantos); mudança de alíquota de tributo que já existia é "Aumento" ou "Redução" e
  não conta como imposto criado;
- só entra afirmação que apareceu na norma ou na fonte citada; o que é opinião de parte interessada vem dito no texto;
- categoria: Em vigor | Extinto ou revogado | Barrado ou revertido | Contestado ou em transição.

Execute:  python data/_fontes/gerar_tributos.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tributos.json")
PL = "https://www.planalto.gov.br/ccivil_03/"


def f(texto, fonte, url):
    return {"texto": texto, "fonte": fonte, "url": url}


def t(governo, ano, tributo, tipo, acao, categoria, resumo, situacao, norma, url, fontes, qtd=1, **extra):
    d = dict(governo=governo, ano=ano, tributo=tributo, tipo=tipo, acao=acao, categoria=categoria, resumo=resumo, situacao=situacao,
             norma={"nome": norma, "url": url}, fontes=fontes, qtd=qtd if acao == "Criação" else 0)
    d.update(extra)
    return d


TRIBUTOS = [
    # ---------------------------------------------------------------- FHC 1 (1995–1998)
    t("FHC 1", "1996", "CPMF (imposto do cheque)", "Contribuição", "Criação", "Extinto ou revogado",
      "Cobrança sobre cada movimentação bancária, criada para financiar a saúde.",
      "Extinta em 31/12/2007: o Senado rejeitou a prorrogação (PEC 89/2007) por 45 votos a 34, faltando 4 para os 49 necessários.",
      "Lei 9.311/1996 e EC 12/1996", PL + "leis/l9311.htm",
      [f("Senado rejeita a prorrogação da CPMF.", "Agência Senado, dez/2007", "https://www12.senado.leg.br/noticias/materias/2007/12/13/senado-rejeita-prorrogacao-da-cpmf")]),
    t("FHC 1", "1996", "Taxa de Fiscalização de Serviços de Energia Elétrica", "Taxa", "Criação", "Em vigor",
      "Taxa anual paga pelas empresas de energia para financiar a fiscalização da Aneel.",
      "Prevista no art. 12 da lei, que segue com texto vigente no Planalto.",
      "Lei 9.427/1996, art. 12", PL + "leis/l9427cons.htm", []),
    t("FHC 1", "1996", "Lei Kandir (ICMS sobre exportações)", "Imposto estadual", "Redução", "Em vigor",
      "Desonerou de ICMS as exportações de produtos primários e semielaborados.",
      "Em vigor, com alterações.", "Lei Complementar 87/1996", PL + "leis/lcp/lcp87.htm", []),
    # ---------------------------------------------------------------- FHC 2 (1999–2002)
    t("FHC 2", "2000", "Contribuição do FUST (1% da receita de telecomunicações)", "Contribuição", "Criação", "Em vigor",
      "Contribuição de 1% sobre a receita das operadoras de telecomunicações para financiar a universalização dos serviços.",
      "O texto da lei segue vigente no Planalto.", "Lei 9.998/2000, art. 6º", PL + "leis/l9998.htm", []),
    t("FHC 2", "2000", "Contribuição universidade-empresa (CIDE-Royalties)", "Contribuição", "Criação", "Em vigor",
      "Contribuição paga por quem paga royalties ou compra tecnologia do exterior, para financiar a interação universidade-empresa.",
      "O texto da lei segue vigente no Planalto.", "Lei 10.168/2000, art. 2º", PL + "leis/l10168.htm", []),
    t("FHC 2", "2001", "Contribuição de 10% sobre o FGTS na demissão sem justa causa", "Contribuição", "Criação", "Extinto ou revogado",
      "Adicional de 10% pago pelo empregador, sobre o FGTS, quando demite sem justa causa.",
      "Extinta a partir de 1º/1/2020 (Lei 13.932/2019, art. 12), já no governo Bolsonaro.",
      "Lei Complementar 110/2001, art. 1º", PL + "leis/lcp/lcp110.htm",
      [f("A partir de 1º de janeiro de 2020 fica extinta a contribuição social instituída pelo art. 1º da LC 110/2001.", "Lei 13.932/2019, art. 12 (Planalto)", PL + "_ato2019-2022/2019/lei/L13932.htm")]),
    t("FHC 2", "2001", "CIDE-Combustíveis", "Contribuição", "Criação", "Em vigor",
      "Contribuição sobre a importação e a venda de petróleo, gás e derivados e álcool combustível.",
      "Em vigor, mas com alíquotas reduzidas a zero ou quase zero para vários produtos por decretos a partir de 2003–2004.",
      "Lei 10.336/2001 e EC 33/2001", PL + "leis/leis_2001/l10336.htm",
      [f("Decreto reduziu as alíquotas da Cide sobre petróleo e derivados.", "Decreto 5.060/2004 (Planalto)", PL + "_ato2004-2006/2004/decreto/d5060.htm")]),
    # ---------------------------------------------------------------- Lula 1 (2003–2006)
    t("Lula 1", "2003", "Contribuição previdenciária de servidores aposentados e pensionistas", "Contribuição", "Criação", "Em vigor",
      "Passou a cobrar contribuição previdenciária também de servidores públicos aposentados e pensionistas.",
      "Em vigor, com mudanças da reforma de 2019 (EC 103).", "Emenda Constitucional 41/2003", PL + "constituicao/emendas/emc/emc41.htm", []),
    t("Lula 1", "2004", "PIS/Cofins-Importação", "Contribuição", "Criação", "Em vigor",
      "Contribuições que passaram a incidir sobre produtos e serviços importados.",
      "Em vigor, com alterações.", "Lei 10.865/2004", PL + "_ato2004-2006/2004/lei/l10.865.htm", []),
    # ---------------------------------------------------------------- Lula 2 (2007–2010)
    t("Lula 2", "2007", "Fim da CPMF", "Contribuição", "Extinção", "Extinto ou revogado",
      "O governo tentou prorrogar a CPMF até 2011 e perdeu a votação no Senado por 4 votos.",
      "A cobrança acabou em 31/12/2007. Foi uma das principais derrotas do governo Lula.",
      "PEC 89/2007 (rejeitada)", "https://www12.senado.leg.br/noticias/materias/2007/12/13/senado-rejeita-prorrogacao-da-cpmf",
      [f("Senado rejeita a prorrogação da CPMF.", "Agência Senado, dez/2007", "https://www12.senado.leg.br/noticias/materias/2007/12/13/senado-rejeita-prorrogacao-da-cpmf")]),
    t("Lula 2", "2008", "Alta do IOF sobre crédito", "Imposto", "Aumento", "Em vigor",
      "Em 3/1/2008, logo após o fim da CPMF, o IOF diário para pessoa física dobrou (de 0,0041% para 0,0082%) e foi criado um adicional de 0,38% sobre operações de crédito.",
      "O IOF segue em vigor; suas alíquotas foram alteradas várias vezes depois. A ligação com o fim da CPMF é a leitura de fontes acadêmicas, não declaração oficial.",
      "Decreto 6.339/2008", PL + "_ato2007-2010/2008/decreto/d6339.htm",
      [f("Decreto dobrou o IOF diário da pessoa física e criou o adicional de 0,38%; houve pedido de sustação no Senado (PDS 10/2008).", "Migalhas e monografia do IDP", "https://www.migalhas.com.br/depeso/52007/a-extincao-da-cpmf-causa-bombardeio-tributario")]),
    # ---------------------------------------------------------------- Dilma 1 (2011–2014)
    t("Dilma 1", "2011", "Desoneração da folha de pagamento (CPRB)", "Contribuição", "Redução", "Contestado ou em transição",
      "Setores trocaram a contribuição sobre a folha por um percentual do faturamento, o que reduziu o imposto para muitas empresas.",
      "Prorrogada até 2027 pela Lei 14.784/2023 e, depois da disputa de 2023–2024, em fim gradual até 2027 (Lei 14.973/2024).",
      "Lei 12.546/2011, arts. 7º e 8º", PL + "_ato2011-2014/2011/lei/l12546.htm",
      [f("Prorroga até 31/12/2027 os prazos dos arts. 7º e 8º da Lei 12.546.", "Lei 14.784/2023 (Planalto)", PL + "_ato2023-2026/2023/lei/L14784.htm")]),
    t("Dilma 1", "2012", "Redução temporária do IPI de automóveis", "Imposto", "Redução", "Extinto ou revogado",
      "O IPI sobre carros foi reduzido para estimular as vendas, com volta gradual às alíquotas anteriores.",
      "Temporária: a recomposição gradual foi até 31/12/2013.", "Decreto 7.971/2013 (prorrogação)", "https://www12.senado.leg.br/orcamento/documentos/ldo/2015/elaboracao/projeto-de-lei/proposta-do-poder-executivo/anexo-iv.11-2013-compensacao-da-renuncia-de-receitas",
      [f("Decreto de 28/3/2013 prorrogou a redução do IPI de automóveis com recomposição gradual.", "Senado, anexo da LDO 2015", "https://www12.senado.leg.br/orcamento/documentos/ldo/2015/elaboracao/projeto-de-lei/proposta-do-poder-executivo/anexo-iv.11-2013-compensacao-da-renuncia-de-receitas")]),
    t("Dilma 1", "2013", "PIS/Cofins zero na cesta básica", "Contribuição", "Redução", "Em vigor",
      "Zerou PIS/Cofins sobre carnes, café, açúcar, óleo de soja, manteiga, margarina, sabão, pasta de dente e papel higiênico, entre outros.",
      "Em vigor. A lista de produtos é a do anexo de renúncias do Senado.", "Lei 12.839/2013", PL + "_ato2011-2014/2013/lei/l12839.htm",
      [f("Lista de produtos da desoneração da cesta básica.", "Senado, anexo da LDO 2015", "https://www12.senado.leg.br/orcamento/documentos/ldo/2015/elaboracao/projeto-de-lei/proposta-do-poder-executivo/anexo-iv.11-2013-compensacao-da-renuncia-de-receitas")]),
    # ---------------------------------------------------------------- Dilma 2 (2015–2016)
    t("Dilma 2", "2015", "Tentativa de recriar a CPMF", "Contribuição", "Criação", "Barrado ou revertido",
      "O governo estudou recriar a CPMF para cobrir um rombo de cerca de R$ 80 bilhões no orçamento do ano seguinte.",
      "Não saiu do papel: o governo desistiu depois da reação de empresários, governadores, parlamentares e do vice-presidente Michel Temer. Não chegou a ser votada.",
      "Proposta (não virou norma)", "https://congressoemfoco.com.br/noticias/apos-resistencias-governo-desiste-de-recriar-cpmf",
      [f("Após resistências, governo desiste de recriar a CPMF.", "Congresso em Foco", "https://congressoemfoco.com.br/noticias/apos-resistencias-governo-desiste-de-recriar-cpmf")], qtd=0),
    # ---------------------------------------------------------------- Temer (2016–2018)
    t("Temer", "2017", "Aumento do PIS/Cofins sobre combustíveis", "Contribuição", "Aumento", "Contestado ou em transição",
      "Decreto de 20/7/2017 elevou as alíquotas de PIS/Cofins sobre gasolina, diesel e etanol.",
      "Quatro liminares chegaram a barrar o decreto, por violar a legalidade tributária e a anterioridade nonagesimal, mas foram derrubadas em segunda instância (relato de out/2017). Não encontramos a decisão final de mérito.",
      "Decreto 9.101/2017", PL + "_ato2015-2018/2017/decreto/D9101.htm",
      [f("As liminares contra o Decreto 9.101/2017 foram concedidas em série em julho e agosto de 2017 e derrubadas em instâncias superiores.", "Jornal Contábil e Congresso em Foco", "https://jornalcontabil.com.br/noticia/justica-barra-aumento-de-impostos-sobre-combustiveis-outra-vez/")]),
    # ---------------------------------------------------------------- Bolsonaro (2019–2022)
    t("Bolsonaro", "2022", "Corte do IPI (25% e depois 35%)", "Imposto", "Redução", "Contestado ou em transição",
      "Decretos de 2022 reduziram o IPI da maioria dos produtos industrializados.",
      "O STF (ministro Moraes) suspendeu os decretos em maio de 2022 e parte do decreto de 29/7/2022 em agosto, a pedido do Amazonas, por afetar a Zona Franca de Manaus. Em setembro ele revogou as liminares, depois que novo decreto restabeleceu as alíquotas de 170 produtos feitos na Zona Franca, e depois encerrou as ações por perda de objeto.",
      "Decreto 10.979/2022 e Decreto 11.158/2022", PL + "_ato2019-2022/2022/decreto/D11158.htm",
      [f("Moraes revoga liminar que suspendeu corte de IPI.", "Poder360", "https://www.poder360.com.br/justica/moraes-revoga-liminar-que-suspendeu-corte-de-ipi/"),
       f("Moraes suspende redução de IPI na Zona Franca de Manaus.", "Correio Braziliense", "https://www.correiobraziliense.com.br/economia/2022/08/5028017-moraes-concede-nova-vitoria-a-zona-franca-de-manaus-e-suspende-reducao-de-ipi.html")], reducao_impedida=True),
    t("Bolsonaro", "2022", "PIS/Cofins e Cide zerados sobre combustíveis", "Contribuição", "Redução", "Barrado ou revertido",
      "As alíquotas de PIS/Cofins e Cide sobre combustíveis ficaram zeradas até dezembro de 2022.",
      "Revertida pelo governo seguinte: a MP 1.157/2023 manteve a isenção da gasolina e do etanol só até 28/2/2023 (gasolina voltou a pagar R$ 0,47 por litro em 1º/3/2023) e a do diesel até 31/12/2023.",
      "Decretos de 2021–2022 e MP 1.157/2023", PL + "_ato2023-2026/2023/mpv/mpv1157.htm",
      [f("Governo Lula cobrará R$ 0,47 de imposto sobre o litro da gasolina.", "Poder360", "https://www.poder360.com.br/economia/gasolina-sera-reonerada-em-r-047-a-partir-de-4a-feira/")], reducao_impedida=True),
    t("Bolsonaro", "2022", "Teto do ICMS sobre combustíveis, energia, comunicações e transporte", "Imposto estadual", "Redução", "Contestado ou em transição",
      "Considerou esses itens essenciais, o que limita a alíquota de ICMS, e definiu que o ICMS dos combustíveis incide uma só vez.",
      "Em vigor, mas com ações no STF (ADI 7191, ADIN 7181) citadas no próprio Planalto.",
      "Leis Complementares 192/2022 e 194/2022", PL + "leis/lcp/lcp194.htm", []),
    # ---------------------------------------------------------------- Lula 3 (2023–)
    t("Lula 3", "2023", "Tributação de fundos exclusivos e de investimentos no exterior", "Regime de tributação", "Criação", "Em vigor",
      "Fundos exclusivos passaram a ter cobrança periódica (come-cotas) e rendimentos no exterior passaram a ser taxados em 15% ao ano.",
      "Em vigor desde 1º/1/2024.", "Lei 14.754/2023", PL + "_ato2023-2026/2023/lei/L14754.htm",
      [f("Resumo da lei: tributação anual de 15% de aplicações no exterior e come-cotas semestral.", "Renova Invest (resumo)", "https://renovainvest.com.br/blog/lei-14754-2023-tributacao-offshore-fundos-exclusivos/")]),
    t("Lula 3", "2023", "Tributação das apostas (bets)", "Regime de tributação", "Criação", "Em vigor",
      "Operadoras pagam 12% sobre a receita das apostas (o que sobra depois dos prêmios) e os apostadores pagam 15% de Imposto de Renda sobre o prêmio líquido.",
      "Em vigor. Segundo uma fonte, a LC 224/2025 elevou gradualmente o percentual das operadoras.",
      "Lei 14.790/2023", PL + "_ato2023-2026/2023/lei/L14790.htm",
      [f("A alíquota de 12% incide sobre o GGR das operadoras; os apostadores pagam IRPF de 15% sobre o prêmio líquido.", "Mattos Filho e Estratégia Concursos", "https://www.mattosfilho.com.br/unico/tributacao-apostas-quota-fixa/")]),
    t("Lula 3", "2023", "Reforma tributária: IBS, CBS e Imposto Seletivo", "Imposto", "Criação", "Contestado ou em transição",
      "Cria o IBS e a CBS (que juntos substituem PIS, Cofins, ICMS e ISS) e o Imposto Seletivo, sobre bens e serviços prejudiciais à saúde ou ao meio ambiente.",
      "Em transição de 2026 a 2033: a CBS substitui PIS e Cofins em 2027 e o ICMS e o ISS acabam em 2033. A alíquota de referência estimada é de cerca de 26,5%, ainda não fixada em lei.",
      "EC 132/2023 e LC 214/2025", PL + "constituicao/emendas/emc/emc132.htm",
      [f("Cronograma da reforma tributária de 2026 a 2033.", "Jettax (resumo do cronograma)", "https://www.jettax.com.br/blog/cronograma-e-fases-da-reforma-tributaria-de-2026-a-2033/")], qtd=3),
    t("Lula 3", "2023", "Reoneração dos combustíveis", "Contribuição", "Aumento", "Em vigor",
      "A cobrança de PIS/Cofins sobre gasolina e etanol voltou em 1º/3/2023; a isenção do diesel estava prevista até 31/12/2023.",
      "Em vigor. O Ministério da Fazenda estimou ganho de R$ 28,9 bilhões de março a dezembro de 2023 (estimativa do governo).",
      "MP 1.157/2023", PL + "_ato2023-2026/2023/mpv/mpv1157.htm",
      [f("Governo Lula cobrará R$ 0,47 de imposto sobre o litro da gasolina.", "Poder360", "https://www.poder360.com.br/economia/gasolina-sera-reonerada-em-r-047-a-partir-de-4a-feira/")]),
    t("Lula 3", "2023", "Desoneração da folha: prorrogação até 2027", "Contribuição", "Redução", "Contestado ou em transição",
      "Lula vetou a prorrogação da desoneração da folha, o Congresso derrubou o veto (Lei 14.784/2023) e o ministro Zanin (STF) a suspendeu em abril de 2024.",
      "Governo e Congresso fecharam acordo: a Lei 14.973/2024 acaba com a desoneração aos poucos até 2027. O STF ainda julgava o caso em 2026 (ADI 7633), segundo as fontes.",
      "Leis 14.784/2023 e 14.973/2024", PL + "_ato2023-2026/2024/lei/L14973.htm",
      [f("Zanin votou pela inconstitucionalidade da lei de 2023, mas manteve a de 2024.", "Teletime e Monitor Mercantil", "https://teletime.com.br/17/10/2025/zanin-vota-contra-desoneracao-mas-mantem-acordo-para-compensacao/")], reducao_impedida=True),
    t("Lula 3", "2024", "Imposto de importação de 20% em compras de até US$ 50 (\"taxa das blusinhas\")", "Imposto", "Aumento", "Barrado ou revertido",
      "Desde 1º/8/2024, compras internacionais de até US$ 50 passaram a pagar 20% de imposto de importação, além do ICMS estadual.",
      "Em maio de 2026 uma medida provisória zerou o imposto federal nessa faixa; o ICMS continua e a MP ainda precisa ser analisada pelo Congresso.",
      "Lei 14.902/2024 (Mover), que revogou a isenção do Decreto-Lei 1.804/1980", PL + "_ato2023-2026/2024/lei/L14902.htm",
      [f("'Taxa das blusinhas' começa a valer.", "Jornal Opção", "https://www.jornalopcao.com.br/ultimas-noticias/taxa-blusinhas-comeca-a-valer-nesta-quinta-feira-625672/"),
       f("Lula assina MP que zera imposto federal da taxa das blusinhas.", "O Povo", "https://mais.opovo.com.br/jornal/economia/2026/05/12/lula-assina-mp-que-zera-imposto-federal-da-taxa-das-blusinhas.html")]),
    t("Lula 3", "2025", "Alta do IOF por decreto", "Imposto", "Aumento", "Contestado ou em transição",
      "Decreto de 22/5/2025 elevou o IOF sobre crédito, câmbio e seguros para reforçar a arrecadação.",
      "O Congresso derrubou o decreto (PDL 176/2025); o ministro Moraes suspendeu os dois atos, e em 16/7/2025 restabeleceu o decreto, exceto uma regra sobre risco sacado.",
      "Decreto 12.466/2025", PL + "_ato2023-2026/2025/decreto/D12466.htm",
      [f("Moraes mantém o decreto do IOF, menos a regra do risco sacado.", "Poder360", "https://www.poder360.com.br/poder-congresso/decisao-sobre-o-iof-indica-perda-para-o-congresso-e-o-planalto/")]),
    t("Lula 3", "2025", "Imposto de importação zero em 11 alimentos", "Imposto", "Redução", "Em vigor",
      "Zerou o imposto de importação de itens como carne bovina desossada (era 10,8%), café torrado (9%), azeite (9%), açúcar, milho, sardinha e massas, para conter o preço dos alimentos.",
      "Em vigor desde 14/3/2025, sem prazo para voltar. Vale só para carne bovina desossada; sardinha dentro de cota.",
      "Resolução do Gecex/Camex (mar/2025)", "https://www.cnnbrasil.com.br/economia/macroeconomia/veja-lista-de-alimentos-que-terao-impostos-zerados-pelo-governo/",
      [f("Governo zera imposto de importação de 11 alimentos.", "Correio da Manhã", "https://www.correiodamanha.com.br/politica/2025/03/amp/188598-governo-zera-imposto-de-importacao-de-11-alimentos.html")]),
    t("Lula 3", "2025", "Isenção de Imposto de Renda até R$ 5 mil por mês", "Imposto", "Redução", "Em vigor",
      "Quem ganha até R$ 5 mil por mês deixa de pagar Imposto de Renda, com desconto decrescente até R$ 7.350.",
      "Em vigor desde janeiro de 2026.", "Lei 15.270/2025", PL + "_ato2023-2026/2025/lei/L15270.htm",
      [f("Resumo da lei: isenção até R$ 5 mil e desconto até R$ 7.350.", "Hondatar (resumo)", "https://www.hondatar.com.br/publicada-a-lei-15-270-2025-sancao-do-pl-1087-2025-que-amplia-a-isencao-do-irpf-e-tributa-lucros-e-dividendos-a-partir-de-2026/")]),
    t("Lula 3", "2025", "Tributação mínima de altas rendas e de dividendos", "Imposto", "Criação", "Em vigor",
      "Quem recebe mais de R$ 600 mil por ano passa a pagar um imposto mínimo de até 10%, e dividendos acima de R$ 50 mil por mês têm retenção de 10%.",
      "Em vigor desde janeiro de 2026.", "Lei 15.270/2025", PL + "_ato2023-2026/2025/lei/L15270.htm",
      [f("Resumo da lei: tributação mínima de até 10% e retenção de 10% sobre dividendos.", "Hondatar (resumo)", "https://www.hondatar.com.br/publicada-a-lei-15-270-2025-sancao-do-pl-1087-2025-que-amplia-a-isencao-do-irpf-e-tributa-lucros-e-dividendos-a-partir-de-2026/")], qtd=2),
]


def main():
    for i, x in enumerate(TRIBUTOS, start=1):
        x["id"] = f"trib-{i}"
        x.setdefault("reducao_impedida", False)
    payload = {
        "metadados": {
            "atualizado_em": "2026-10-23",
            "aviso": ("Levantamento do painel, não é lista oficial: reúne os tributos federais mais conhecidos de cada governo, cada um com a norma conferida no Planalto. "
                      "Mudança de alíquota de um tributo que já existia aparece como Aumento ou Redução e não conta como imposto criado. "
                      "O número de criados soma os tributos e regimes novos de cada linha. Resumos de terceiros estão sinalizados."),
        },
        "tributos": TRIBUTOS,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(len(TRIBUTOS), "linhas gravadas em", OUT)


if __name__ == "__main__":
    main()
