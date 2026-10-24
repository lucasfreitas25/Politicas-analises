"""
Gera data/planos_governo.json: principais propostas dos planos com que cada presidente foi eleito (1994–2022)
e o programa "Uma Ponte para o Futuro" (PMDB, 2015), adotado como base pelo governo Temer.

Cada proposta é uma paráfrase do painel com a página do PDF em que o trecho aparece (conferida por busca de
palavra-chave na página; ver conferir_paginas()). O texto do plano prevalece sobre o resumo.

Execute:  python data/_fontes/gerar_planos_governo.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "planos_governo.json")

# (mandato, título, ano, partido/coligação, url do PDF, observação, [(tema, proposta, página, palavra-chave para conferir)])
PLANOS = [
    ("FHC 1", "Mãos à Obra, Brasil: proposta de governo", 1994, "PSDB (coligação com PFL e PTB)",
     "https://static.scielo.org/scielobooks/b27wf/pdf/cardoso-9788599662663.pdf",
     "Edição de 2008 do Centro Edelstein (SciELO Livros); as páginas são as do PDF.",
     [("Prioridades", "Cinco metas prioritárias: emprego, educação, saúde, agricultura e segurança.", 11, r"cinco metas"),
      ("Impostos", "Mandar ao Congresso uma reforma tributária que simplifique os tributos e estimule o investimento.", 12, r"reforma tribut.ria que"),
      ("Estatais", "Acelerar as privatizações, com estimativa de R$ 15 bilhões em quatro anos para infraestrutura.", 13, r"privatiza..o ser. acelerado"),
      ("Infraestrutura", "Atrair o setor privado para obras por concessões e parcerias com empresas públicas.", 12, r"concess.es"),
      ("Social", "Criar o programa Comunidade Solidária, ampliando projetos de alimentação e combate à fome.", 11, r"Comunidade Solid"),
      ("Trabalho e renda", "Política de salário mínimo com ganhos reais, compatível com as contas da Previdência.", 66, r"ganhos reais"),
      ("Educação", "Descentralizar a merenda escolar para os municípios e criar padrões de qualidade para o livro didático.", 55, r"merenda"),
      ("Agro e terra", "Reforma agrária para democratizar o acesso à terra.", 50, r"Reforma agr.ria")]),
    ("FHC 2", "Avança, Brasil: proposta de governo", 1998, "PSDB (coligação com PFL, PPB, PTB e PSD)",
     "https://static.scielo.org/scielobooks/62rp6/pdf/cardoso-9788599662687.pdf",
     "Edição de 2008 do Centro Edelstein (SciELO Livros); as páginas são as do PDF.",
     [("Contas públicas", "Combater os déficits nos três níveis de governo e garantir o equilíbrio das contas da Previdência.", 11, r"d.ficits or.ament.rios"),
      ("Estatais", "Levar adiante o programa de privatização, com o Estado como regulador.", 11, r"programa de privatiza"),
      ("Impostos", "Reforma tributária para tornar o sistema mais racional e simples.", 26, r"reforma tribut.ria que tome"),
      ("Emprego", "Acelerar o crescimento para gerar os 7,8 milhões de postos de trabalho necessários até 2002.", 12, r"7,8 milh"),
      ("Social", "Apoiar programas de bolsa-escola de estados e municípios.", 15, r"bolsa-escola"),
      ("Saúde", "Ampliar as equipes de Saúde da Família e o número de agentes comunitários.", 15, r"sa.de da fam.lia"),
      ("Educação", "Usar parte do Fundef na formação e qualificação de professores.", 75, r"Fundef"),
      ("Agro e terra", "Prosseguir com a reforma agrária por assentamentos e outras formas de acesso à terra.", 15, r"reforma agr.ria via assentamentos")]),
    ("Lula 1", "Programa de Governo 2002: Crescimento, Emprego e Inclusão Social", 2002, "PT (coligação Lula Presidente: PT, PL, PCdoB, PMN e PCB)",
     "https://files.cercomp.ufg.br/weby/up/16/o/pplgbt-148.pdf",
     "Cópia hospedada pela UFG; as páginas são as do PDF.",
     [("Economia", "Reduzir a fragilidade externa como primeiro passo para crescer.", 11, r"fr ?agilidade externa"),
      ("Impostos", "Reforma tributária já no primeiro ano, desonerando a produção e a exportação.", 14, r"primeiro ano"),
      ("Previdência", "Enfrentar a questão da Previdência com iniciativas de curto, médio e longo prazo.", 18, r"previdenci.ria"),
      ("Trabalho e renda", "Reajuste progressivo do poder de compra do salário mínimo.", 31, r"reajuste progressivo"),
      ("Emprego", "Programa nacional de incentivo ao primeiro emprego para jovens.", 24, r"primeiro emprego"),
      ("Social", "Programa de combate à fome e política de garantia de renda mínima.", 43, r"fome"),
      ("Agro e terra", "Reforma agrária como instrumento de inclusão social.", 21, r"Reforma Agr.ria . instrumento")]),
    ("Lula 2", "Lula Presidente: Programa de Governo 2007/2010", 2006, "PT (coligação A Força do Povo: PT, PCdoB e PRB)",
     "https://files.cercomp.ufg.br/weby/up/16/o/pplgbt-91.pdf",
     "Cópia hospedada pela UFG; as páginas são as do PDF.",
     [("Social", "Aprimorar o Bolsa Família e oferecer trabalho e renda aos beneficiários.", 29, r"Bolsa Fam.lia"),
      ("Social", "Continuar o Fome Zero, com alimentação escolar, compra de alimentos e restaurantes populares.", 30, r"Fome Zero"),
      ("Educação", "Aprovar o Fundeb e criar o piso salarial nacional dos professores.", 18, r"Piso Salarial"),
      ("Educação", "Continuar o ProUni, criar novas universidades e abrir vagas nas federais.", 18, r"continuidade do PROUNI"),
      ("Trabalho e renda", "Política de recuperação do salário mínimo, negociada entre governo, empresas, trabalhadores e aposentados.", 20, r"poder de compra do sal.rio m.nimo"),
      ("Infraestrutura", "Levar energia a todos (Luz para Todos) e ampliar saneamento e transporte público.", 11, r"luz para todos"),
      ("Instituições", "Reforma política com fidelidade partidária e financiamento público de campanhas.", 14, r"Reforma Pol.tica")]),
    ("Dilma 1", "Os 13 compromissos programáticos de Dilma Rousseff", 2010, "PT (coligação Para o Brasil Seguir Mudando)",
     "https://siac.fpabramo.org.br/uploads/acervo/Programa-de-governo-presidencia_2010.pdf",
     "Acervo da Fundação Perseu Abramo; as páginas são as do PDF.",
     [("Social", "Erradicar a pobreza absoluta e seguir reduzindo as desigualdades.", 6, r"Erradicar a pobreza"),
      ("Moradia", "Minha Casa, Minha Vida com mais 2 milhões de moradias.", 8, r"dois milh.es de moradias"),
      ("Educação", "Construir 6 mil creches e pré-escolas e 10 mil quadras esportivas cobertas.", 7, r"6 mil creches"),
      ("Petróleo", "Usar a riqueza do pré-sal em um fundo de longo prazo para saúde, educação, ciência e cultura.", 2, r"Fundo de Longo Prazo"),
      ("Economia", "Política macroeconômica com equilíbrio fiscal e controle da inflação.", 5, r"equil.brio fiscal"),
      ("Emprego", "Ampliar programas de inserção de jovens no mercado de trabalho.", 7, r"inser..o de jovens"),
      ("Segurança", "Enfrentar o crime organizado, consolidando o Pronasci.", 9, r"Pronasci")]),
    ("Dilma 2", "Mais Mudanças, Mais Futuro: programa de governo Dilma Rousseff", 2014, "PT (coligação Com a Força do Povo)",
     "https://www.conjur.com.br/wp-content/uploads/2023/09/programa-governo-dilma-2014.pdf",
     "Cópia hospedada pelo Conjur; as páginas são as do PDF.",
     [("Instituições", "Reforma política com participação popular por meio de plebiscito.", 30, r"plebiscito"),
      ("Instituições", "Combate sem tréguas à corrupção.", 30, r"combate sem tr.guas"),
      ("Educação", "Pronatec 2: mais 12 milhões de vagas em cursos técnicos até 2015.", 30, r"12 milh.es de vagas"),
      ("Educação", "Escola obrigatória a partir dos 4 anos de idade a partir de 2016.", 20, r"seis para quatro anos"),
      ("Economia", "Manter inflação baixa e estável, rigor fiscal e ampliar o investimento público.", 9, r"infla..o baixa e est.vel")]),
    ("Temer", "Uma Ponte para o Futuro", 2015, "PMDB (Fundação Ulysses Guimarães)",
     "https://www.epsjv.fiocruz.br/sites/default/files/files/ponteparaofuturo.pdf",
     "Temer não disputou eleição como cabeça de chapa: este é o programa do PMDB de out/2015, que o governo adotou como base. Cópia hospedada pela Fiocruz.",
     [("Contas públicas", "Limite por lei para as despesas de custeio, abaixo do crescimento do PIB.", 18, r"limite para as despesas de custeio"),
      ("Contas públicas", "Acabar com as vinculações constitucionais de gastos, como saúde e educação.", 9, r"acabar com as vincula"),
      ("Previdência", "Criar idade mínima para a aposentadoria.", 11, r"idade m.nima"),
      ("Trabalho", "Permitir que convenções coletivas prevaleçam sobre a lei, salvo direitos básicos.", 19, r"conven..es coletivas prevale"),
      ("Estatais", "Concessões amplas em logística e infraestrutura e volta do regime de concessão no petróleo.", 18, r"concess.es amplas"),
      ("Comércio", "Abertura comercial e acordos com EUA, União Europeia e Ásia, com ou sem o Mercosul.", 18, r"abertura comercial"),
      ("Impostos", "Simplificar impostos e unificar o ICMS, com cobrança no estado de destino.", 19, r"unificando a legisla..o do ICMS"),
      ("Economia", "Em até 3 anos, estabilizar a dívida/PIB e levar a inflação ao centro da meta de 4,5%.", 18, r"centro da meta")]),
    ("Bolsonaro", "O Caminho da Prosperidade: proposta de plano de governo", 2018, "PSL (coligação Brasil Acima de Tudo, Deus Acima de Todos: PSL e PRTB)",
     "https://static.cdn.pleno.news/2018/08/Jair-Bolsonaro-proposta_PSC.pdf",
     "Cópia do plano registrado no TSE, hospedada pelo Pleno News; as páginas são as do PDF.",
     [("Estado", "Reduzir o número de ministérios.", 17, r"REDU..O DE MINIST"),
      ("Economia", "Ministério da Economia unindo Fazenda, Planejamento e Indústria; Banco Central independente.", 53, r"Minist.rio da Economia"),
      ("Contas públicas", "Reduzir a dívida em 20% com privatizações, concessões e venda de imóveis da União.", 56, r"reduzir em 20%"),
      ("Previdência", "Introduzir aos poucos um regime de capitalização com contas individuais.", 57, r"capitaliza..o"),
      ("Trabalho", "Carteira de trabalho verde e amarela, voluntária, em que o contrato individual prevalece sobre a CLT.", 64, r"verde e amarela"),
      ("Segurança", "Reduzir a maioridade penal para 16 anos e acabar com progressão de penas e saídas temporárias.", 32, r"maioridade penal"),
      ("Segurança", "Reformular o Estatuto do Desarmamento e dar excludente de ilicitude a policiais.", 32, r"excludente de ilicitude"),
      ("Social", "Renda mínima para todas as famílias, acima do valor do Bolsa Família.", 63, r"renda m.nima"),
      ("Saúde", "Mais Médicos: médicos cubanos poderiam ficar e receber o salário integral se aprovados no Revalida.", 40, r"REVALIDA"),
      ("Educação", "Ênfase na educação infantil, básica e técnica, \"sem doutrinar\".", 22, r"sem doutrinar")]),
    ("Lula 3", "Diretrizes para o Programa de Reconstrução e Transformação do Brasil", 2022, "PT (coligação Brasil da Esperança)",
     "https://cdn-images.rtp.pt/icm/noticias/docs/a5/a5f5b3a8e137ccabb1c5c7adfe4248c5_d15611df61e0d84cc0751b513212d492.pdf",
     "Versão registrada da coligação Brasil da Esperança (Lula-Alckmin), cópia hospedada pela RTP; as páginas são as do PDF.",
     [("Contas públicas", "Revogar o teto de gastos e criar um novo regime fiscal.", 10, r"revogar o teto de gastos"),
      ("Social", "Bolsa Família renovado e ampliado, com urgência.", 5, r"Bolsa Fam.lia renovado"),
      ("Trabalho e renda", "Retomar a política de valorização do salário mínimo.", 4, r"valoriza..o do sal.rio m.nimo"),
      ("Trabalho", "Revogar os marcos regressivos da legislação trabalhista e restabelecer a justiça do trabalho gratuita.", 4, r"legisla..o trabalhista"),
      ("Impostos", "Reforma tributária em que os pobres paguem menos e os muito ricos paguem imposto de renda.", 11, r"reforma tribut.ria solid.ria"),
      ("Estatais", "Opor-se à privatização da Petrobras e da Pré-Sal Petróleo (PPSA).", 14, r"privatiza..o, em curso, da Petrobras"),
      ("Meio ambiente", "Combate ao desmatamento ilegal e desmatamento líquido zero.", 17, r"desmatamento l.quido zero")]),
]


# Agrupa temas parecidos para o filtro ficar curto
TEMA_UNIFICADO = {"Trabalho": "Trabalho e renda", "Emprego": "Trabalho e renda", "Estado": "Instituições",
                  "Comércio": "Economia", "Petróleo": "Estatais e energia", "Estatais": "Estatais e energia"}


def conferir_paginas(pasta):
    """Confere se a palavra-chave de cada proposta aparece na página citada (usado com os PDFs baixados em `pasta`)."""
    import re
    from pypdf import PdfReader
    arquivos = {"FHC 1": "fhc1994", "FHC 2": "fhc1998", "Lula 1": "lula2002", "Lula 2": "lula2006", "Dilma 1": "dilma2010",
                "Dilma 2": "dilma2014", "Temer": "temer2015", "Bolsonaro": "bolsonaro2018", "Lula 3": "lula2022"}
    falhas = 0
    for gov, *_r, itens in PLANOS:
        paginas = [p.extract_text() or "" for p in PdfReader(os.path.join(pasta, arquivos[gov] + ".pdf")).pages]
        for tema, texto, pag, chave in itens:
            ok = re.search(chave, re.sub(r"\s+", " ", paginas[pag - 1]), re.I) is not None
            if not ok:
                falhas += 1
                print("FALHA", gov, pag, chave, "|", texto[:60])
    print("propostas:", sum(len(p[-1]) for p in PLANOS), "falhas:", falhas)


def main():
    payload = {
        "metadados": {
            "atualizado_em": "2026-10-22",
            "aviso": "Promessas de campanha, não resultados. Cada item é uma paráfrase do painel, com a página do PDF em que o trecho aparece; "
                     "o texto original do plano prevalece. Os planos de 1994 e 1998 estão na edição do Centro Edelstein; os demais são cópias "
                     "hospedadas por terceiros dos documentos divulgados pelas campanhas.",
        },
        "planos": [{"governo": g, "titulo": t, "ano": a, "partido": pt, "url": u, "nota": n,
                    "propostas": [{"tema": TEMA_UNIFICADO.get(te, te), "texto": tx, "pagina": pg} for te, tx, pg, _k in itens]}
                   for g, t, a, pt, u, n, itens in PLANOS],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("gravado:", OUT)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--conferir":
        conferir_paginas(sys.argv[2])
    else:
        main()
