"""
Gera data/leis_historicas.json: principais leis, leis complementares e emendas constitucionais de FHC a Temer (1995–2018),
no mesmo formato de data/leis_sancionadas.json (Bolsonaro e Lula 3).

Cada norma é localizada no texto oficial do Planalto, e o painel só a aceita se o número da norma aparecer na página.
A data vem do próprio texto ("Brasília, DD de mês de AAAA"), o governo é definido pela data e a situação é lida do cabeçalho
(revogada) ou do corpo ("Redação dada", que indica alteração). O resumo é do painel, em linguagem simples.
A lista é uma seleção das principais normas, não todas.

Execute:  python data/_fontes/gerar_leis_historicas.py
"""
import html
import json
import os
import re
import sys
import time

import requests

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leis_historicas.json")
BASE = "https://www.planalto.gov.br/ccivil_03/"
MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

# (tipo, número, ano, área, resumo)
NORMAS = [
    # ---------------- FHC 1
    ("Emenda", 5, 1995, "Infraestrutura", "Permite que os estados concedam a exploração do gás canalizado."),
    ("Emenda", 6, 1995, "Economia", "Acaba com a distinção entre empresa brasileira de capital nacional e de capital estrangeiro."),
    ("Emenda", 8, 1995, "Infraestrutura", "Abre os serviços de telecomunicações a empresas privadas por concessão."),
    ("Emenda", 9, 1995, "Energia", "Flexibiliza o monopólio da União sobre o petróleo, permitindo contratos com outras empresas."),
    ("Lei", 8987, 1995, "Infraestrutura", "Lei das Concessões: regras para o setor privado explorar serviços públicos."),
    ("Lei", 9099, 1995, "Instituições", "Cria os Juizados Especiais para causas simples e crimes de menor gravidade."),
    ("Lei", 9096, 1995, "Instituições", "Lei dos Partidos Políticos."),
    ("Lei", 9279, 1996, "Economia", "Lei de Propriedade Industrial, que passou a permitir patentes de remédios."),
    ("Lei", 9311, 1996, "Tributário", "Cria a CPMF, imposto sobre movimentações bancárias."),
    ("Lei", 9313, 1996, "Saúde", "Garante remédios gratuitos pelo SUS a quem vive com HIV."),
    ("Lei", 9394, 1996, "Educação", "Lei de Diretrizes e Bases da Educação (LDB)."),
    ("Lei", 9424, 1996, "Educação", "Cria o Fundef, fundo para o ensino fundamental e o salário dos professores."),
    ("Lei", 9427, 1996, "Energia", "Cria a Aneel, agência que regula a energia elétrica."),
    ("Lei", 9433, 1997, "Meio ambiente", "Política Nacional de Recursos Hídricos."),
    ("Lei", 9472, 1997, "Infraestrutura", "Lei Geral de Telecomunicações; cria a Anatel."),
    ("Lei", 9478, 1997, "Energia", "Lei do Petróleo; cria a ANP e acaba com o monopólio da Petrobras na exploração."),
    ("Lei", 9491, 1997, "Economia", "Programa Nacional de Desestatização (privatizações)."),
    ("Lei", 9503, 1997, "Segurança", "Código de Trânsito Brasileiro."),
    ("Lei", 9504, 1997, "Instituições", "Lei das Eleições."),
    ("Emenda", 16, 1997, "Instituições", "Permite a reeleição para presidente, governadores e prefeitos."),
    ("Lei", 9605, 1998, "Meio ambiente", "Lei de Crimes Ambientais."),
    ("Lei", 9656, 1998, "Saúde", "Regula os planos e seguros privados de saúde."),
    ("Emenda", 19, 1998, "Gestão pública", "Reforma administrativa: muda regras do serviço público."),
    ("Emenda", 20, 1998, "Previdência", "Reforma da Previdência: cria tempo mínimo de contribuição e limita aposentadorias."),
    # ---------------- FHC 2
    ("Lei", 9787, 1999, "Saúde", "Lei dos Genéricos."),
    ("Lei", 9782, 1999, "Saúde", "Cria a Anvisa, agência de vigilância sanitária."),
    ("Lei", 9876, 1999, "Previdência", "Cria o fator previdenciário no cálculo das aposentadorias."),
    ("Lei Complementar", 101, 2000, "Fiscal", "Lei de Responsabilidade Fiscal: limites para gastos e dívida de União, estados e municípios."),
    ("Lei", 9961, 2000, "Saúde", "Cria a ANS, agência dos planos de saúde."),
    ("Emenda", 26, 2000, "Habitação", "Inclui a moradia entre os direitos sociais da Constituição."),
    ("Emenda", 29, 2000, "Saúde", "Define o mínimo que União, estados e municípios devem aplicar em saúde."),
    ("Emenda", 31, 2000, "Proteção social", "Cria o Fundo de Combate e Erradicação da Pobreza."),
    ("Lei", 9985, 2000, "Meio ambiente", "Cria o Sistema Nacional de Unidades de Conservação (SNUC)."),
    ("Lei", 10098, 2000, "Direitos e minorias", "Normas de acessibilidade para pessoas com deficiência."),
    ("Lei", 10172, 2001, "Educação", "Plano Nacional de Educação 2001–2010."),
    ("Lei", 10219, 2001, "Proteção social", "Cria o Bolsa Escola, renda para famílias com crianças na escola."),
    ("Lei", 10257, 2001, "Habitação", "Estatuto da Cidade: regras de política urbana."),
    ("Lei", 10406, 2002, "Instituições", "Novo Código Civil."),
    ("Lei", 10438, 2002, "Energia", "Cria o Proinfa, a CDE e a tarifa social de energia (Baixa Renda)."),
    # ---------------- Lula 1
    ("Lei", 10639, 2003, "Educação", "Torna obrigatório ensinar história e cultura afro-brasileira nas escolas."),
    ("Lei", 10741, 2003, "Direitos e minorias", "Estatuto do Idoso."),
    ("Lei", 10826, 2003, "Segurança", "Estatuto do Desarmamento: regras para posse, porte e venda de armas."),
    ("Emenda", 41, 2003, "Previdência", "Reforma da Previdência dos servidores públicos."),
    ("Emenda", 45, 2004, "Instituições", "Reforma do Judiciário: cria o CNJ e o CNMP."),
    ("Lei", 10836, 2004, "Proteção social", "Cria o Bolsa Família."),
    ("Lei", 10848, 2004, "Energia", "Novo modelo do setor elétrico: leilões de energia e contratos regulados."),
    ("Lei", 11079, 2004, "Infraestrutura", "Lei das Parcerias Público-Privadas (PPPs)."),
    ("Lei", 11096, 2005, "Educação", "Cria o ProUni, bolsas em faculdades privadas."),
    ("Lei", 11101, 2005, "Economia", "Nova Lei de Falências e Recuperação de Empresas."),
    ("Lei", 11196, 2005, "Economia", "Lei do Bem: incentivos fiscais para inovação tecnológica."),
    ("Lei", 11284, 2006, "Meio ambiente", "Gestão de florestas públicas: concessão para manejo sustentável."),
    ("Lei", 11340, 2006, "Direitos e minorias", "Lei Maria da Penha contra a violência doméstica."),
    ("Lei", 11343, 2006, "Segurança", "Lei de Drogas."),
    ("Lei", 11346, 2006, "Proteção social", "Cria o Sistema Nacional de Segurança Alimentar (Sisan)."),
    ("Lei Complementar", 123, 2006, "Tributário", "Estatuto da Micro e Pequena Empresa e Simples Nacional."),
    ("Emenda", 53, 2006, "Educação", "Cria o Fundeb, que substituiu o Fundef."),
    # ---------------- Lula 2
    ("Lei", 11445, 2007, "Saneamento", "Marco do saneamento básico."),
    ("Lei", 11494, 2007, "Educação", "Regulamenta o Fundeb."),
    ("Lei", 11738, 2008, "Educação", "Cria o piso salarial nacional dos professores."),
    ("Lei", 11892, 2008, "Educação", "Cria os Institutos Federais de educação profissional."),
    ("Lei", 11947, 2009, "Proteção social", "Alimentação escolar (PNAE): 30% da compra deve vir da agricultura familiar."),
    ("Lei", 11977, 2009, "Habitação", "Cria o Minha Casa, Minha Vida."),
    ("Emenda", 62, 2009, "Fiscal", "Muda o pagamento de precatórios (dívidas judiciais do governo)."),
    ("Lei", 12187, 2009, "Meio ambiente", "Política Nacional sobre Mudança do Clima."),
    ("Lei", 12288, 2010, "Direitos e minorias", "Estatuto da Igualdade Racial."),
    ("Lei", 12305, 2010, "Meio ambiente", "Política Nacional de Resíduos Sólidos."),
    ("Lei", 12351, 2010, "Energia", "Regime de partilha de produção para o pré-sal."),
    # ---------------- Dilma 1
    ("Lei", 12382, 2011, "Trabalho", "Fixa por lei a regra de reajuste do salário mínimo até 2015."),
    ("Lei", 12435, 2011, "Proteção social", "Cria o Sistema Único de Assistência Social (Suas) em lei."),
    ("Lei", 12513, 2011, "Educação", "Cria o Pronatec, cursos técnicos e profissionalizantes."),
    ("Lei", 12527, 2011, "Instituições", "Lei de Acesso à Informação."),
    ("Lei", 12528, 2011, "Direitos e minorias", "Cria a Comissão Nacional da Verdade."),
    ("Lei", 12651, 2012, "Meio ambiente", "Novo Código Florestal."),
    ("Lei", 12711, 2012, "Educação", "Lei de Cotas nas universidades e institutos federais."),
    ("Lei", 12734, 2012, "Energia", "Novas regras de divisão dos royalties do petróleo."),
    ("Lei Complementar", 141, 2012, "Saúde", "Regulamenta o que conta como gasto em saúde e o mínimo de cada governo."),
    ("Lei", 12783, 2013, "Energia", "Renova concessões de energia e reduz a conta de luz."),
    ("Lei", 12846, 2013, "Instituições", "Lei Anticorrupção: responsabiliza empresas por corrupção."),
    ("Lei", 12850, 2013, "Segurança", "Define organização criminosa e a delação premiada."),
    ("Lei", 12871, 2013, "Saúde", "Cria o Mais Médicos."),
    ("Emenda", 72, 2013, "Trabalho", "Iguala os direitos das trabalhadoras domésticas aos dos demais empregados."),
    ("Lei", 12965, 2014, "Direitos e minorias", "Marco Civil da Internet."),
    ("Lei", 13005, 2014, "Educação", "Plano Nacional de Educação 2014–2024."),
    # ---------------- Dilma 2
    ("Lei Complementar", 150, 2015, "Trabalho", "Regulamenta os direitos das trabalhadoras domésticas."),
    ("Lei", 13104, 2015, "Direitos e minorias", "Cria o crime de feminicídio."),
    ("Lei", 13105, 2015, "Instituições", "Novo Código de Processo Civil."),
    ("Lei", 13123, 2015, "Meio ambiente", "Marco legal do acesso à biodiversidade e aos conhecimentos tradicionais."),
    ("Lei", 13146, 2015, "Direitos e minorias", "Estatuto da Pessoa com Deficiência."),
    ("Lei", 13189, 2015, "Trabalho", "Programa de Proteção ao Emprego: redução de jornada e salário com compensação do governo."),
    ("Lei", 13257, 2016, "Proteção social", "Marco Legal da Primeira Infância."),
    ("Lei", 13260, 2016, "Segurança", "Lei Antiterrorismo."),
    # ---------------- Temer
    ("Emenda", 93, 2016, "Fiscal", "Prorroga e amplia a Desvinculação de Receitas da União (DRU)."),
    ("Emenda", 95, 2016, "Fiscal", "Teto de gastos: congela o gasto federal por 20 anos, corrigido pela inflação."),
    ("Lei", 13303, 2016, "Gestão pública", "Lei das Estatais: regras de governança e de indicação de dirigentes."),
    ("Lei", 13334, 2016, "Infraestrutura", "Cria o Programa de Parcerias de Investimentos (PPI)."),
    ("Lei", 13365, 2016, "Energia", "Dá à Petrobras a opção de ser operadora dos campos do pré-sal, e não mais obrigatória."),
    ("Lei", 13415, 2017, "Educação", "Reforma do Ensino Médio."),
    ("Lei", 13429, 2017, "Trabalho", "Amplia a terceirização, inclusive da atividade principal da empresa."),
    ("Lei", 13445, 2017, "Direitos e minorias", "Nova Lei de Migração."),
    ("Lei", 13465, 2017, "Habitação", "Regularização fundiária rural e urbana."),
    ("Lei", 13467, 2017, "Trabalho", "Reforma trabalhista."),
    ("Lei", 13576, 2017, "Energia", "Cria o RenovaBio, política de biocombustíveis."),
    ("Lei Complementar", 159, 2017, "Fiscal", "Regime de Recuperação Fiscal para estados em crise."),
    ("Lei", 13655, 2018, "Instituições", "Muda a Lei de Introdução às Normas do Direito: segurança jurídica para gestores públicos."),
    ("Lei", 13709, 2018, "Direitos e minorias", "Lei Geral de Proteção de Dados (LGPD)."),
    ("Lei", 13718, 2018, "Direitos e minorias", "Cria o crime de importunação sexual."),
]


# Situações conferidas à mão no texto das próprias normas (o robô só lê o cabeçalho e marcas de alteração)
SITUACAO_MANUAL = {
    ("Lei", 9311): "Contribuição extinta em 2007 (Ipea, Texto para Discussão 1846)",
    ("Lei", 9424): "Revogada pela Lei 11.494/2007 (Fundeb)",
    ("Lei", 10172): "Plano de dez anos (2001–2010)",
    ("Lei", 10219): "Incorporada ao Bolsa Família em 2004 (a Lei 10.836 unificou os programas de transferência de renda)",
    ("Lei", 10836): "Revogada em 2021 (MP 1.061, convertida na Lei 14.284/2021, que criou o Auxílio Brasil); o Bolsa Família foi recriado em 2023",
    ("Lei", 11494): "Revogada pela Lei 14.113/2020 (novo Fundeb), ressalvado o art. 12",
    ("Lei", 12382): "As diretrizes valeram de 2012 a 2015; a Lei 14.663/2023 estabeleceu a política de valorização permanente a partir de 2024",
    ("Lei", 13005): "Plano de dez anos (2014–2024)",
    ("Lei", 13189): "A adesão ao programa era possível até 31/12/2016, prazo previsto na própria lei",
    ("Emenda", 93): "Em vigor, com partes revogadas",
}


def governo_por_data(iso):
    for nome, ini, fim in (("FHC 1", "1995-01-01", "1998-12-31"), ("FHC 2", "1999-01-01", "2002-12-31"), ("Lula 1", "2003-01-01", "2006-12-31"),
                           ("Lula 2", "2007-01-01", "2010-12-31"), ("Dilma 1", "2011-01-01", "2014-12-31"), ("Dilma 2", "2015-01-01", "2016-05-11"),
                           ("Temer", "2016-05-12", "2018-12-31"), ("Bolsonaro", "2019-01-01", "2022-12-31"), ("Lula 3", "2023-01-01", "2099-12-31")):
        if ini <= iso <= fim:
            return nome
    return None


def candidatos(tipo, n, ano):
    pontilhado = f"{n:,}".replace(",", ".")
    if tipo == "Emenda":
        return [BASE + f"constituicao/emendas/emc/emc{n}.htm", BASE + f"Constituicao/Emendas/Emc/emc{n}.htm",
                BASE + f"constituicao/emendas/emc/emc{n:02d}.htm", BASE + f"constituicao/emendas/emc/emc{n:02d}.htm".replace("emc/emc", "Emc/emc")]
    if tipo == "Lei Complementar":
        return [BASE + f"leis/lcp/lcp{n}.htm", BASE + f"leis/LCP/Lcp{n}.htm"]
    atos = {range(1995, 1999): [""], range(1999, 2003): [""], range(2003, 2007): ["_ato2003-2006/", "_ato2004-2006/"], range(2007, 2011): ["_ato2007-2010/"],
            range(2011, 2015): ["_ato2011-2014/"], range(2015, 2019): ["_ato2015-2018/"]}
    pastas = next(v for r, v in atos.items() if ano in r)
    c = [BASE + f"leis/l{n}.htm", BASE + f"leis/L{n}.htm", BASE + f"leis/l{n}cons.htm", BASE + f"leis/L{n}cons.htm", BASE + f"leis/L{n}compilado.htm", BASE + f"leis/{ano}/l{n}.htm", BASE + f"leis/leis_{ano}/l{n}.htm", BASE + f"leis/LEIS_{ano}/L{n}.htm",
         BASE + f"leis/{ano}/L{pontilhado}.htm", BASE + f"leis/{ano}/l{pontilhado}.htm"]
    for pasta in pastas:
        if pasta:
            c += [BASE + f"{pasta}{ano}/lei/l{n}.htm", BASE + f"{pasta}{ano}/lei/L{n}.htm", BASE + f"{pasta}{ano}/lei/l{pontilhado}.htm",
                  BASE + f"{pasta}{ano}/Lei/L{pontilhado}.htm", BASE + f"{pasta}{ano}/Lei/L{n}.htm", BASE + f"{pasta}{ano}/lei/L{pontilhado}.htm"]
    return c


def ler(url):
    r = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return None
    bruto = r.content
    if bruto[:2] in (b"\xff\xfe", b"\xfe\xff"):
        txt = bruto.decode("utf-16", errors="replace")
    else:
        txt = bruto.decode("cp1252", errors="replace")
    t = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    return re.sub(r"\s+", " ", t)


def conferir(tipo, n, ano, texto):
    pont = f"{n:,}".replace(",", ".")
    rotulo = {"Lei": r"LEI\s+N\s*[º°o]?\s*", "Lei Complementar": r"LEI\s+COMPLEMENTAR\s+N\s*[º°o]?\s*", "Emenda": r"EMENDA\s+CONSTITUCIONAL\s+N\s*[º°o]?\s*"}[tipo]
    return re.search(rotulo + (str(n) if tipo == "Emenda" else rf"({pont}|{n})") + r"\b", texto[:8000], re.I) is not None


def processar(tipo, n, ano, area, resumo):
    for url in candidatos(tipo, n, ano):
        try:
            texto = ler(url)
        except Exception:
            continue
        if not texto or not conferir(tipo, n, ano, texto):
            continue
        pont = f"{n:,}".replace(",", ".")
        # a data oficial está no próprio título da norma: "LEI Nº 9.961, DE 28 DE JANEIRO DE 2000"
        titulo = re.search(r"(?:LEI|EMENDA CONSTITUCIONAL|LEI COMPLEMENTAR)\s+N\s*[º°o]?\s*(?:" + re.escape(pont) + "|" + str(n) + r")\s*,?\s+DE\s+(\d{1,2})\s*[º°o]?\s+DE\s+(\w+)\s+DE\s+(\d{4})",
                           texto[:8000], re.I)
        data = titulo or re.search(r"Bras.lia\s*,?\s+(?:em\s+)?(\d{1,2})\s*[º°o]?\s+de\s+(\w+)\s+de\s+(\d{4})", texto)
        if not data:
            return None
        iso = f"{int(data.group(3)):04d}-{MESES[data.group(2).lower()]:02d}-{int(data.group(1)):02d}"
        cabecalho = texto[:700]
        if re.search(r"\(Revogad[ao][^)]*\)|\(Vig[eê]ncia encerrada[^)]*\)", cabecalho):
            situacao = "Revogada ou com vigência encerrada"
        elif re.search(r"Reda..o dada|Alterad[ao] pel|Vide Lei|\(Regulamento\)", texto):
            situacao = "Em vigor, com alterações"
        else:
            situacao = "Em vigor"
        situacao = SITUACAO_MANUAL.get((tipo, n), situacao)
        ementa = re.search(r"((?:Dispõe|Altera|Institui|Regulamenta|Estabelece|Cria|Autoriza|Define|Dá nova|Acrescenta|Torna|Modifica|Disciplina|Concede|Outorga|Regula|Abre|Revoga)[^.]{20,400}\.)", texto[:2500])
        return {"data": iso, "governo": governo_por_data(iso), "norma": f"{tipo if tipo != 'Emenda' else 'EC'} {n if tipo == 'Emenda' else f'{n:,}'.replace(',', '.')}/{iso[:4]}"
                .replace("Lei Complementar", "LC"), "tipo": tipo, "area": area, "resumo": resumo, "situacao": situacao,
                "texto_oficial": url, "ementa_oficial": (ementa.group(1) if ementa else "")[:300], "manchete": "", "url_imprensa": ""}
    return None


def main():
    saida, falhas = [], []
    for tipo, n, ano, area, resumo in NORMAS:
        r = processar(tipo, n, ano, area, resumo)
        if r:
            if r["data"][:4] != str(ano) and tipo != "Emenda":
                print("AVISO ano diferente:", tipo, n, ano, r["data"])
            saida.append(r)
        else:
            falhas.append((tipo, n, ano))
        time.sleep(0.3)
    saida.sort(key=lambda x: x["data"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print("normas gravadas:", len(saida), "| não localizadas:", falhas)


if __name__ == "__main__":
    main()
