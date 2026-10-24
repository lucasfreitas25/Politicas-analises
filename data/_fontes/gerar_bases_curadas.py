"""
Gera as bases curadas manualmente (indicadores sem API pública estável ou que
exigem consolidação de várias fontes):

- data/scorecard.json                       → tabela comparativa principal
- data/indicadores_sociais_ambientais.json  → pobreza, desmatamento, analfabetismo
- data/auditoria.json                       → registro das correções feitas na revisão de out/2026

Execute:  python data/_fontes/gerar_bases_curadas.py
"""
import json
import os

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SGS = "https://www3.bcb.gov.br/sgspub/"


def sgs_csv(codigo):
    return f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv"
SIDRA = "https://sidra.ibge.gov.br/"
FBSP = "https://forumseguranca.org.br/anuario-brasileiro-seguranca-publica/"
SIS = "https://www.ibge.gov.br/estatisticas/sociais/trabalho/9221-sintese-de-indicadores-sociais.html"
LUPA_BAND = "https://www.agencialupa.org/checagem/2026/10/18/ao-vivo-checagem-do-debate-entre-lula-e-flavio-bolsonaro-na-band/"


def ler(nome, padrao=None):
    caminho = os.path.join(DATA, nome)
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return padrao


def fmt_pct(v, casas=1):
    return f"{v:.{casas}f}%".replace(".", ",")


def acumular(valores):
    x = 1.0
    for v in valores:
        x *= 1 + v / 100
    return (x - 1) * 100


def indicadores_dependentes():
    """Indicadores calculados a partir das séries baixadas pelo build_database.py (inadimplência, contas da casa, saneamento)."""
    saida = []
    inad = ler("inadimplencia_bcb.json", [])
    if inad:
        pf_b = [r["pf_total"] for r in inad if 2019 <= r["ano"] <= 2022 and "pf_total" in r]
        pf_l = [r["pf_total"] for r in inad if r["ano"] >= 2023 and "pf_total" in r]
        dez22 = next(r["pf_total"] for r in inad if r["periodo"] == "2022-12")
        ult = inad[-1]
        saida.append(ind("Inadimplência", "Inadimplência da carteira de crédito de pessoas físicas (atraso > 90 dias)",
                         f"{fmt_pct(dez22, 2)} (dez/2022)", f"{fmt_pct(ult['pf_total'], 2)} ({ult['mes']:02d}/{ult['ano']})", dez22, ult["pf_total"], "% da carteira", "bolsonaro",
                         f"Média no período: {fmt_pct(sum(pf_b) / len(pf_b), 2)} com Bolsonaro e {fmt_pct(sum(pf_l) / len(pf_l), 2)} com Lula. Cartão rotativo: {fmt_pct(next(r['cartao_rotativo'] for r in inad if r['periodo'] == '2022-12'), 1)} (dez/2022) e {fmt_pct(ult['cartao_rotativo'], 1)} ({ult['mes']:02d}/{ult['ano']}). A alta coincide com a Selic elevada e com o endividamento recorde das famílias (CNC).",
                         "Banco Central — SGS 21084 e 21127", sgs_csv(21084)))
    casa = ler("contas_casa.json", [])
    if casa:
        def serie(campo, a0, a1):
            return [r[campo] for r in casa if a0 <= r["ano"] <= a1 and campo in r]
        geral = (acumular(serie("ipca_geral", 2019, 2022)), acumular(serie("ipca_geral", 2023, 2100)))
        en = (acumular(serie("energia_eletrica", 2019, 2022)), acumular(serie("energia_eletrica", 2023, 2100)))
        ag = (acumular(serie("agua_esgoto", 2019, 2022)), acumular(serie("agua_esgoto", 2023, 2100)))
        saida.append(ind("Custo de Vida", "Energia elétrica residencial (IPCA)", f"+{fmt_pct(en[0])}", f"+{fmt_pct(en[1])}", round(en[0], 1), round(en[1], 1), "% acumulado", "bolsonaro",
                         f"Contra IPCA geral de +{fmt_pct(geral[0])} (Bolsonaro, 48 meses) e +{fmt_pct(geral[1])} (Lula, 45 meses): em termos reais, a conta de luz caiu no 1º período e subiu no 2º. Em 2025 houve bandeiras vermelhas (nível 2 em ago e set) e o IPCA de energia subiu 7,98% só em set/2026. A tarifa social foi ampliada em jul/2025.",
                         "IBGE — IPCA (SIDRA 1419/7060)", SIDRA + "tabela/7060"))
        saida.append(ind("Custo de Vida", "Taxa de água e esgoto (IPCA)", f"+{fmt_pct(ag[0])}", f"+{fmt_pct(ag[1])}", round(ag[0], 1), round(ag[1], 1), "% acumulado", "bolsonaro",
                         f"Ao ano: {fmt_pct((1 + ag[0] / 100) ** (12 / 48) * 100 - 100)} com Bolsonaro e {fmt_pct((1 + ag[1] / 100) ** (12 / 45) * 100 - 100)} com Lula. Reajustes seguem as agências reguladoras e contratos de concessão.",
                         "IBGE — IPCA (SIDRA 1419/7060)", SIDRA + "tabela/7060"))
    san = ler("saneamento_ibge.json", [])
    if san:
        a22 = next(r for r in san if r["ano"] == 2022)
        ult = [r for r in san if "esgoto_adequado_pct" in r][-1]
        saida.append(ind("Saneamento", "Domicílios com esgoto adequado (rede ou fossa ligada à rede)", fmt_pct(a22["esgoto_adequado_pct"]) + " (2022)", fmt_pct(ult["esgoto_adequado_pct"]) + f" ({ult['ano']})",
                         a22["esgoto_adequado_pct"], ult["esgoto_adequado_pct"], "% dos domicílios", "lula",
                         "Avanço de 2,1 pontos em três anos. A PNAD não coleta o dado em 2020 e 2021. A meta legal é de 90% de coleta e tratamento até 2033, e o estudo do Trata Brasil/GO Associados (jul/2026) concluiu que o ritmo atual não a cumprirá.",
                         "IBGE — PNAD Contínua (SIDRA 7192)", SIDRA + "tabela/7192"))
    return saida


def salvar(nome, obj):
    with open(os.path.join(DATA, nome), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("gravado:", nome)


def ind(cat, nome, b, l, bn, ln, unidade, melhor, obs, fonte, url):
    return {"categoria": cat, "indicador": nome, "bolsonaro": b, "lula": l, "bolsonaro_num": bn, "lula_num": ln,
            "unidade": unidade, "melhor": melhor, "observacao": obs, "fonte": fonte, "fonte_url": url}


SCORECARD = {
    "metadados": {
        "titulo": "Comparativo Bolsonaro (2019–2022) x Lula (2023–2026)",
        "atualizado_em": "2026-10-20",
        "periodo_bolsonaro": "jan/2019 a dez/2022 (48 meses)",
        "periodo_lula": "jan/2023 até o dado mais recente de cada série (em geral ago ou set/2026)",
        "criterio_melhor": "'melhor' indica qual período teve o resultado mais favorável no indicador; 'empate' quando a diferença é pequena ou depende de contexto. Não é juízo de mérito: choques externos (pandemia, guerra, clima, juros globais) pesam nos dois mandatos.",
        "fontes": ["IBGE/SIDRA", "Banco Central (SGS)", "MTE (Novo CAGED)", "MDIC/Secex", "CONAB", "FBSP", "Inpe/PRODES", "CNC/Peic", "DIEESE"],
    },
    "indicadores": [
        ind("Crescimento Econômico", "Crescimento médio anual do PIB", "1,5% a.a.", "3,0% a.a.", 1.45, 2.97, "% ao ano", "lula",
            "Bolsonaro: 1,3% (2019), -3,3% (2020, pandemia), 4,8% (2021), 3,0% (2022). Lula: 3,2% (2023), 3,4% (2024), 2,3% (2025); 2026 acumula 1,9% em 4 trimestres até o 2º tri (fora da média).",
            "IBGE — Contas Nacionais (SIDRA 6784 e 5932)", SIDRA + "tabela/6784"),
        ind("Mercado de Trabalho", "Taxa de desocupação média", "12,1%", "6,7%", 12.06, 6.74, "%", "lula",
            "Média dos trimestres da PNAD Contínua. Pico de 14,9% (2020/21). Com Lula: 8,8% no 1º tri/2023, mínima de 5,1% no 4º tri/2025 e 5,3% em jun–ago/2026.",
            "IBGE — PNAD Contínua (SIDRA 4099/6381)", SIDRA + "tabela/4099"),
        ind("Mercado de Trabalho", "Saldo de empregos formais (CAGED)", "+5.25 milhões (48 meses)".replace(".", ","), "+5.55 milhões (44 meses)".replace(".", ","), 5251875, 5546385, "postos formais", "lula",
            "Série com ajustes do MTE. Bolsonaro: +644 mil (2019, CAGED antigo), −189 mil (2020, pandemia), +2,78 mi (2021) e +2,01 mi (2022). Lula: +1,46 mi (2023), +1,68 mi (2024), +1,28 mi (2025, menor saldo anual do Novo CAGED) e +1,13 mi em jan–ago/2026. Média mensal: 109.4 mil com Bolsonaro e 126.1 mil com Lula. 2020 é o único ano negativo; 2021 é recuperação de uma base deprimida.".replace(".", ",", 0),
            "MTE — Novo CAGED (série com ajustes)", "https://static.poder360.com.br/2026/01/Caged-apresentacao-dez-2025-1.pdf"),
        ind("Poder de Compra", "Rendimento médio real habitual (fim do período)", "R$ 3.317 (out–dez/2022)", "R$ 3.777 (jun–ago/2026)", 3317, 3777, "R$ de ago/2026", "lula",
            "Valores deflacionados para a mesma data. Bolsonaro terminou 1,0% abaixo do início (R$ 3.351 em out–dez/2018); com Lula, alta de 13,9% desde o fim de 2022.",
            "IBGE — PNAD Contínua (SIDRA 6390)", SIDRA + "tabela/6390"),
        ind("Inflação", "IPCA acumulado no mandato", "26,93% (48 meses)", "18,87% (45 meses)", 26.93, 18.87, "% acumulado", "lula",
            "Bolsonaro: 4,31% / 4,52% / 10,06% / 5,78%; pico de 12,13% em 12 meses (abr/2022). Lula: 4,62% / 4,83% / 4,26% / 3,95% (jan–set/2026); pico de 5,53% (abr/2025).",
            "IBGE — IPCA (BCB SGS 433)", sgs_csv(433)),
        ind("Inflação", "IPCA médio anualizado", "6,14% a.a.", "4,72% a.a.", 6.14, 4.72, "% ao ano", "lula",
            "Taxa anual equivalente ao acumulado de cada período (corrige a diferença no número de meses).", "IBGE — IPCA (BCB SGS 433)", sgs_csv(433)),
        ind("Inflação", "Alimentação no domicílio (IPCA)", "+56,1%", "+14,0%", 56.1, 14.0, "% acumulado", "lula",
            "Óleo de soja (+140,7%), feijão (+112,8%) e carnes (+72,6%) puxaram a alta com Bolsonaro; com Lula, café (+44,3%) e gasolina (+32,2%) foram os maiores aumentos.",
            "IBGE — SIDRA 1419/7060", SIDRA + "tabela/7060"),
        ind("Agropecuária", "Maior safra de grãos do mandato (CONAB)", "271,4 Mt (2021/22)", "361,7 Mt (2025/26)", 271.4, 361.7, "milhões de toneladas", "lula",
            "Safra 2024/25: 350,2 Mt (12º lev., set/2025); 2025/26: 361,7 Mt (set/2026). Clima e preços internacionais pesam mais que a política federal de curto prazo.",
            "CONAB — levantamentos de safra", "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-graos"),
        ind("Setor Externo", "Maior superávit comercial do mandato", "US$ 61,5 bi (2022)", "US$ 98,9 bi (2023)", 61.5, 98.9, "US$ bilhões", "lula",
            "2023 é o recorde da série. Depois: US$ 74,2 bi (2024) e US$ 68,1 bi (2025), com exportações recordes de US$ 348,3 bi em 2025 (valores do ComexStat em 21/10/2026; o MDIC revisa os números e versões anteriores traziam 68,3 e 348,7).",
            "MDIC/Secex — ComexStat", "https://comexstat.mdic.gov.br/pt/geral"),
        ind("Monetário & Juros", "Taxa Selic média", "6,5% a.a.", "13,3% a.a.", 6.51, 13.27, "% ao ano", "bolsonaro",
            "Mínima histórica de 2,00% em 2020–21; 13,75% no fim de 2022. Com Lula, chegou a 15,00% (jun/2025) e estava em 13,75% em out/2026. O BC é autônomo desde 2021.",
            "Banco Central — SGS 432", sgs_csv(432)),
        ind("Câmbio", "Dólar PTAX médio", "R$ 4,92", "R$ 5,28", 4.92, 5.28, "R$/US$", "bolsonaro",
            "Média das médias anuais. O dólar fechou 2024 em R$ 6,19 (máxima nominal) e estava em R$ 5,01 em out/2026.", "Banco Central — SGS 1", sgs_csv(1)),
        ind("Fiscal", "Dívida bruta do governo geral (% PIB)", "71,7% (dez/2022)", "82,9% (ago/2026)", 71.68, 82.87, "% do PIB", "bolsonaro",
            "Bolsonaro: 74,4% → 86,9% (pandemia) → 71,7% (inflação alta infla o PIB nominal). Lula: alta contínua com déficits e juros elevados. Em % do PIB, o pico da série segue sendo 2020.",
            "Banco Central — SGS 13762", sgs_csv(13762)),
        ind("Fiscal", "Resultado primário do setor público (média anual, % PIB)", "-2,0% (+0,4% sem 2020)", "-0,9%", -2.03, -0.93, "% do PIB", "empate",
            "Bolsonaro: déficit de 9,2% do PIB em 2020 (pandemia) e superávits em 2021–22. Lula: déficit de 2,3% em 2023 (inclui precatórios represados) e déficits menores depois.",
            "Banco Central — SGS 5793 (sinal invertido)", sgs_csv(5793)),
        ind("Indústria", "Produção industrial (índice médio, 2022=100)", "99,4", "102,8", 99.4, 102.8, "índice", "lula",
            "Média do índice dessazonalizado da PIM-PF disponível na base em cada período.", "IBGE — PIM-PF (SIDRA 8888)", SIDRA + "tabela/8888"),
        ind("Segurança Pública", "Mortes violentas intencionais (total anual)", "47.508 (2022)", "40.775 (2025)", 47508, 40775, "mortes", "lula",
            "Taxa de 23,4 (2022) para 19,1 por 100 mil (2025), a menor desde 2012. A queda é tendência desde 2018 e depende muito das políticas estaduais.",
            "FBSP — Anuário 2026", FBSP),
        ind("Segurança Pública", "Feminicídios (anual)", "1.455 (2022)", "1.571 (2025)", 1455, 1571, "casos", "bolsonaro",
            "Recorde da série em 2025 (+4%), pelo quarto ano seguido. Valores da edição 2026 do Anuário, que revisa anos anteriores. Especialistas atribuem parte da alta à melhora na notificação.", "FBSP — Anuário 2026", FBSP),
        ind("Social", "Pobreza (linha do Banco Mundial)", "31,6% (2022)", "23,1% (2024)", 31.6, 23.1, "% da população", "lula",
            "Menor nível da série iniciada em 2012. Extrema pobreza: 5,9% (2022) → 3,5% (2024).", "IBGE — Síntese de Indicadores Sociais", SIS),
        ind("Social", "Índice de Gini (renda domiciliar per capita)", "0,517 (2022)", "0,511 (2025)", 0.517, 0.511, "índice (0 a 1)", "lula",
            "Quanto menor, menos desigual. Mínima da série em 2024 (0,504); leve alta em 2025.", "IBGE — PNAD Contínua (SIDRA 7435)", SIDRA + "tabela/7435"),
        ind("Educação", "Taxa de analfabetismo (15 anos ou mais)", "5,6% (2022)", "4,9% (2025)", 5.6, 4.9, "% da população", "lula",
            "Queda gradual e estrutural, puxada pela substituição de gerações.", "IBGE — PNAD Contínua Educação (SIDRA 7113)", SIDRA + "tabela/7113"),
        ind("Custo de Vida", "Cestas básicas compradas pelo salário mínimo (SP)", "1,62 (ago/2022)", "1,80 (ago/2026)", 1.62, 1.80, "cestas", "lula",
            "Ganho de 11,3%. No debate da Band, Lula falou em \"2,2 cestas\" — número classificado como exagerado pelas checagens.", "DIEESE, via Agência Lupa", LUPA_BAND),
        ind("Meio Ambiente", "Desmatamento na Amazônia (PRODES, média anual)", "11.403 km²", "7.104 km²", 11403, 7104, "km²/ano", "lula",
            "Bolsonaro: 10.129 / 10.851 / 13.038 / 11.594 km². Lula: 9.064 (2023; o período ago/22–jul/23 cobre os dois governos) / 6.518 / 5.731 km² (2025, consolidado). A estimativa de 2026 (3.335 km², 16/10/2026) é a menor da série desde 1988 e ainda não entra na média.",
            "Inpe — PRODES", "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates"),
    ] + indicadores_dependentes(),
}

# ---------------------------------------------------------------- direção de cada indicador (para o gráfico de placar)
# True = quanto maior, melhor. Os campos grafico_* corrigem comparações entre períodos de tamanhos diferentes
# (48 meses de Bolsonaro x 44–45 de Lula): acumulados viram taxa ao ano e o CAGED vira média mensal.
DIRECAO = {
    "Crescimento médio anual do PIB": True,
    "Taxa de desocupação média": False,
    "Saldo de empregos formais (CAGED)": True,
    "Rendimento médio real habitual (fim do período)": True,
    "IPCA acumulado no mandato": False,
    "IPCA médio anualizado": False,
    "Alimentação no domicílio (IPCA)": False,
    "Maior safra de grãos do mandato (CONAB)": True,
    "Maior superávit comercial do mandato": True,
    "Taxa Selic média": False,
    "Dólar PTAX médio": False,
    "Dívida bruta do governo geral (% PIB)": False,
    "Resultado primário do setor público (média anual, % PIB)": True,
    "Produção industrial (índice médio, 2022=100)": True,
    "Mortes violentas intencionais (total anual)": False,
    "Feminicídios (anual)": False,
    "Pobreza (linha do Banco Mundial)": False,
    "Índice de Gini (renda domiciliar per capita)": False,
    "Taxa de analfabetismo (15 anos ou mais)": False,
    "Cestas básicas compradas pelo salário mínimo (SP)": True,
    "Desmatamento na Amazônia (PRODES, média anual)": False,
    "Inadimplência da carteira de crédito de pessoas físicas (atraso > 90 dias)": False,
    "Energia elétrica residencial (IPCA)": False,
    "Taxa de água e esgoto (IPCA)": False,
    "Domicílios com esgoto adequado (rede ou fossa ligada à rede)": True,
}


def _ao_ano(pct, meses):
    return ((1 + pct / 100) ** (12 / meses) - 1) * 100


def aplicar_direcao(indicadores):
    for i in indicadores:
        nome = i["indicador"]
        if nome not in DIRECAO:
            raise KeyError(f"Indicador sem direção definida: {nome}")
        i["maior_melhor"] = DIRECAO[nome]
        if nome == "Saldo de empregos formais (CAGED)":
            i.update(grafico_b=round(i["bolsonaro_num"] / 48), grafico_l=round(i["lula_num"] / 44), grafico_rotulo="Empregos formais criados por mês (CAGED)")
        elif nome == "IPCA acumulado no mandato":
            i["no_grafico"] = True  # já representado por "IPCA médio anualizado"
        elif nome in ("Alimentação no domicílio (IPCA)", "Energia elétrica residencial (IPCA)", "Taxa de água e esgoto (IPCA)"):
            meses_l = 45
            i.update(grafico_b=round(_ao_ano(i["bolsonaro_num"], 48), 2), grafico_l=round(_ao_ano(i["lula_num"], meses_l), 2),
                     grafico_rotulo=nome.replace(" (IPCA)", "") + ", ao ano (IPCA)")
    return indicadores


aplicar_direcao(SCORECARD["indicadores"])

# Comparabilidade entre os dois períodos: "ok" = mesma série e mesma metodologia; "ajustado" = períodos de tamanhos ou datas
# diferentes, com ajuste ou ressalva simples; "ressalva" = metodologia, cobertura ou natureza do número diferem entre os lados.
COMPARAB = {
    "Crescimento médio anual do PIB": ("ok", "Mesma série (Contas Nacionais). Lula tem só anos fechados; 2026 fica fora da média."),
    "Taxa de desocupação média": ("ok", "Mesma pesquisa (PNAD Contínua). Em 2020–21 parte das entrevistas foi por telefone."),
    "Saldo de empregos formais (CAGED)": ("ressalva", "2019 vem do CAGED antigo e 2020 em diante do Novo CAGED (metodologia diferente); os períodos têm 48 e 44 meses, então o placar usa a média mensal."),
    "Rendimento médio real habitual (fim do período)": ("ajustado", "Mesma série, deflacionada para a mesma data, mas o fim do período de Lula é o dado mais recente, não o fim do mandato."),
    "IPCA acumulado no mandato": ("ajustado", "Períodos de 48 e 45 meses; por isso o placar usa o IPCA médio anualizado."),
    "IPCA médio anualizado": ("ok", "Taxa anual equivalente em cada período, o que corrige a diferença no número de meses."),
    "Alimentação no domicílio (IPCA)": ("ajustado", "Acumulado em 48 e 45 meses; o placar usa a taxa anual equivalente."),
    "Maior safra de grãos do mandato (CONAB)": ("ressalva", "É um máximo, que favorece o período com mais safras (4 contra 3), e a safra 2025/26 ainda é estimativa da CONAB, não resultado final."),
    "Maior superávit comercial do mandato": ("ressalva", "É um máximo entre 4 anos contra 3; o recorde depende do câmbio e do preço de commodities, não só de política."),
    "Taxa Selic média": ("ok", "Mesma série do Banco Central, média diária de cada período."),
    "Dólar PTAX médio": ("ok", "Mesma série do Banco Central, média das médias anuais."),
    "Dívida bruta do governo geral (% PIB)": ("ajustado", "Estoque no fim de cada período; o de Lula é o dado mais recente (ago/2026), não o fim do mandato."),
    "Resultado primário do setor público (média anual, % PIB)": ("ok", "Mesma série do Banco Central; o valor sem 2020 mostra o efeito da pandemia."),
    "Produção industrial (índice médio, 2022=100)": ("ajustado", "Média do índice dessazonalizado em períodos de tamanhos diferentes."),
    "Mortes violentas intencionais (total anual)": ("ressalva", "Compara um ano de cada governo (2022 e 2025), não o mandato inteiro; o Fórum revisa anos anteriores a cada edição do Anuário e o registro depende de cada estado."),
    "Feminicídios (anual)": ("ressalva", "Compara um ano de cada governo; a notificação e a tipificação do crime mudaram ao longo da série, o que pode explicar parte da alta."),
    "Pobreza (linha do Banco Mundial)": ("ajustado", "Mesma série do IBGE, mas o último ano disponível de Lula é 2024; 2020–21 teve coleta atípica."),
    "Índice de Gini (renda domiciliar per capita)": ("ok", "Mesma série da PNAD Contínua; 2025 é o dado mais recente."),
    "Taxa de analfabetismo (15 anos ou mais)": ("ok", "Mesma série da PNAD Contínua."),
    "Cestas básicas compradas pelo salário mínimo (SP)": ("ok", "Mesmo mês (agosto), mesma cesta e mesma cidade do DIEESE."),
    "Desmatamento na Amazônia (PRODES, média anual)": ("ressalva", "O ano PRODES vai de agosto a julho: 2023 cobre meses dos dois governos; Lula tem 3 anos contra 4 de Bolsonaro."),
    "Inadimplência da carteira de crédito de pessoas físicas (atraso > 90 dias)": ("ajustado", "Mesma série do Banco Central, comparando um ponto no fim de cada período; a média do período está na observação."),
    "Energia elétrica residencial (IPCA)": ("ajustado", "Acumulado em 48 e 45 meses; o placar usa a taxa anual equivalente."),
    "Taxa de água e esgoto (IPCA)": ("ajustado", "Acumulado em 48 e 45 meses; o placar usa a taxa anual equivalente."),
    "Domicílios com esgoto adequado (rede ou fossa ligada à rede)": ("ok", "Mesma série da PNAD; não há coleta em 2020 e 2021."),
}


def aplicar_comparabilidade(indicadores):
    for i in indicadores:
        nivel, texto = COMPARAB.get(i["indicador"], ("ajustado", "Sem classificação."))
        i["comparabilidade"], i["comparabilidade_nota"] = nivel, texto


aplicar_comparabilidade(SCORECARD["indicadores"])

SOCIAIS_AMBIENTAIS = {
    "metadados": {"atualizado_em": "2026-10-20"},
    "pobreza": {
        "fonte": "IBGE — Síntese de Indicadores Sociais (linhas do Banco Mundial de US$ 6,85 e US$ 2,15 PPC)", "url": SIS,
        "nota": "2020 foi atípico por causa do Auxílio Emergencial. Pobreza: série revisada da SIS 2025; extrema pobreza de 2021–2022 da edição de 2023. Extrema pobreza de 2019–2020 não localizada na mesma base.",
        "serie": [
            {"ano": 2019, "governo": "Bolsonaro", "pobreza_pct": 32.6, "extrema_pobreza_pct": None},
            {"ano": 2020, "governo": "Bolsonaro", "pobreza_pct": 31.1, "extrema_pobreza_pct": None},
            {"ano": 2021, "governo": "Bolsonaro", "pobreza_pct": 36.8, "extrema_pobreza_pct": 9.0},
            {"ano": 2022, "governo": "Bolsonaro", "pobreza_pct": 31.6, "extrema_pobreza_pct": 5.9},
            {"ano": 2023, "governo": "Lula", "pobreza_pct": 27.3, "extrema_pobreza_pct": 4.4},
            {"ano": 2024, "governo": "Lula", "pobreza_pct": 23.1, "extrema_pobreza_pct": 3.5},
        ],
    },
    "desmatamento_prodes": {
        "fonte": "Inpe — PRODES Amazônia Legal (ano de agosto a julho), TerraBrasilis", "url": "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates",
        "nota": "O ano PRODES vai de agosto a julho: o dado de 2023 (ago/2022–jul/2023) cobre 5 meses de Bolsonaro e 7 de Lula. Série do TerraBrasilis (atualizada em 16/10/2026): 2025 consolidado em 5.731 km² (a estimativa de out/2025 era 5.796) e 2026 é estimativa (3.335 km²), fora das médias.",
        "serie": [
            {"ano": 2018, "governo": "Temer", "km2": 7536}, {"ano": 2019, "governo": "Bolsonaro", "km2": 10129},
            {"ano": 2020, "governo": "Bolsonaro", "km2": 10851}, {"ano": 2021, "governo": "Bolsonaro", "km2": 13038},
            {"ano": 2022, "governo": "Bolsonaro", "km2": 11594}, {"ano": 2023, "governo": "Lula", "km2": 9064},
            {"ano": 2024, "governo": "Lula", "km2": 6518}, {"ano": 2025, "governo": "Lula", "km2": 5731},
            {"ano": 2026, "governo": "Lula", "km2": 3335, "estimativa": True},
        ],
    },
    "analfabetismo": {
        "fonte": "IBGE — PNAD Contínua Educação (SIDRA 7113)", "url": SIDRA + "tabela/7113",
        "serie": [
            {"ano": 2019, "governo": "Bolsonaro", "taxa": 6.1}, {"ano": 2022, "governo": "Bolsonaro", "taxa": 5.6},
            {"ano": 2023, "governo": "Lula", "taxa": 5.4}, {"ano": 2024, "governo": "Lula", "taxa": 5.3},
            {"ano": 2025, "governo": "Lula", "taxa": 4.9},
        ],
    },
}

SOCIAIS_AMBIENTAIS["desmatamento_cerrado"] = {
    "fonte": "Inpe — PRODES Cerrado (ano de agosto a julho)", "url": "https://data.inpe.br/wp-content/uploads/sites/3/2025/10/2025_1022NT_PRODESCerrado_2025.pdf",
    "nota": "No Cerrado o desmatamento subiu até 2023 (maior desde 2015) e só depois caiu. Grande parte é legal (autorizada pelos estados, dentro do Código Florestal).",
    "serie": [
        {"ano": 2019, "governo": "Bolsonaro", "km2": 6319}, {"ano": 2020, "governo": "Bolsonaro", "km2": 7905},
        {"ano": 2021, "governo": "Bolsonaro", "km2": 8531}, {"ano": 2022, "governo": "Bolsonaro", "km2": 10689},
        {"ano": 2023, "governo": "Lula", "km2": 11012}, {"ano": 2024, "governo": "Lula", "km2": 8174},
        {"ano": 2025, "governo": "Lula", "km2": 7235},
        {"ano": 2026, "governo": "Lula", "km2": 5517, "estimativa": True},
    ],
}
SOCIAIS_AMBIENTAIS["queimadas"] = {
    "fonte": "Inpe — Programa Queimadas (focos de calor no Brasil, satélite de referência): contagem das linhas dos CSVs anuais", "url": "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/",
    "nota": "Contagem direta dos arquivos anuais abertos do Inpe (satélite de referência). 2024 teve a seca mais severa da série e o maior número de focos desde 2010; 2025 já é o ano completo. Focos de calor não são área queimada nem equivalem a incêndios distintos.",
    "serie": [
        {"ano": 2019, "governo": "Bolsonaro", "focos": 197632}, {"ano": 2020, "governo": "Bolsonaro", "focos": 222797},
        {"ano": 2021, "governo": "Bolsonaro", "focos": 184081}, {"ano": 2022, "governo": "Bolsonaro", "focos": 200763},
        {"ano": 2023, "governo": "Lula", "focos": 189901}, {"ano": 2024, "governo": "Lula", "focos": 278299},
        {"ano": 2025, "governo": "Lula", "focos": 136393},
    ],
}
SOCIAIS_AMBIENTAIS["emissoes"] = {
    "fonte": "SEEG 13 — Observatório do Clima (GtCO2e, GWP-AR5)", "url": "https://www.poder360.com.br/poder-sustentavel/brasil-reduz-167-das-emissoes-de-gases-do-efeito-estufa/",
    "nota": "Cada edição do SEEG revisa toda a série; por isso só são mostrados os anos da edição mais recente obtidos nesta revisão. A queda de 16,7% em 2024 é a 2ª maior desde 1990, puxada pela redução do desmatamento (-32,5% nas emissões por uso da terra).",
    "serie": [
        {"ano": 2023, "governo": "Lula", "brutas": 2.576, "liquidas": 1.920},
        {"ano": 2024, "governo": "Lula", "brutas": 2.145, "liquidas": 1.489},
    ],
}
SOCIAIS_AMBIENTAIS["terras_indigenas"] = {
    "fonte": "Ministério dos Povos Indígenas (balanço de mar/2026, Agência Gov) e Instituto Socioambiental (ISA)", "url": "https://acervo.socioambiental.org/acervo/area-protegida/terra-indigena-uirapuru-ti",
    "nota": "Bolsonaro não homologou nenhuma terra indígena (2019–2022). Lula chegou a 20 terras homologadas desde 2023 em 18/11/2025, quando assinou as quatro mais recentes (Manoki, Uirapuru, Estação Parecis e Kaxuyana-Tunayana, cerca de 2,45 milhões de hectares no total das quatro); a Funai lista mais de 240 áreas ainda pendentes. Em 2023 o Congresso aprovou o marco temporal (Lei 14.701) derrubando vetos de Lula.",
    "serie": [{"governo": "Bolsonaro", "periodo": "2019–2022", "homologadas": 0}, {"governo": "Lula", "periodo": "2023–nov/2025", "homologadas": 20}],
}

MINORIAS = {
    "metadados": {"atualizado_em": "2026-10-20", "nota": "Séries trimestrais de desemprego e renda por sexo e cor/raça vêm da API do IBGE (arquivo minorias_pnad.json, gerado pelo build_database.py)."},
    "homicidios_negros": {
        "fonte": "Atlas da Violência 2025 (Ipea/FBSP) e Anuário Brasileiro de Segurança Pública 2026",
        "url": "https://www.poder360.com.br/poder-pesquisas/pessoas-negras-sao-77-dos-homicidios-no-brasil/",
        "destaques": [
            {"indicador": "Vítimas de homicídio que eram negras (2023)", "valor": "77,0%", "detalhe": "35.213 de 45.747 homicídios"},
            {"indicador": "Taxa de homicídio de negros x não negros (2023)", "valor": "28,9 x 10,6", "detalhe": "por 100 mil habitantes"},
            {"indicador": "Risco relativo de um negro ser assassinado", "valor": "2,7x", "detalhe": "2,4x em 2013; 2,8x em 2022 — a desigualdade cresceu na década"},
            {"indicador": "Vítimas negras de mortes por intervenção policial (2025)", "valor": "82%", "detalhe": "Anuário 2026; 79,9% dos homicídios dolosos"},
        ],
    },
    "pessoas_trans": {
        "fonte": "ANTRA — Dossiês anuais de assassinatos de pessoas trans", "url": "https://www.band.com.br/noticias/80-pessoas-trans-e-travestis-foram-assassinadas-no-brasil-em-2025-202601260814",
        "nota": "A ANTRA alerta para subnotificação: em 2025 os assassinatos caíram, mas as tentativas de homicídio subiram. O Brasil lidera o ranking mundial pelo 18º ano. 2021 (140 casos) conferido na cobertura do dossiê da época.",
        "serie": [
            {"ano": 2019, "governo": "Bolsonaro", "assassinatos": 124}, {"ano": 2020, "governo": "Bolsonaro", "assassinatos": 175},
            {"ano": 2021, "governo": "Bolsonaro", "assassinatos": 140}, {"ano": 2022, "governo": "Bolsonaro", "assassinatos": 131},
            {"ano": 2023, "governo": "Lula", "assassinatos": 145}, {"ano": 2024, "governo": "Lula", "assassinatos": 122},
            {"ano": 2025, "governo": "Lula", "assassinatos": 80},
        ],
    },
}

INADIMPLENCIA = {
    "metadados": {"atualizado_em": "2026-10-20",
                  "nota": "A série mensal oficial da carteira de crédito (Banco Central) está em inadimplencia_bcb.json. Os pontos abaixo são as únicas medições de pessoas e famílias com contas em atraso que conseguimos confirmar em fonte pública; não formam série contínua."},
    "pessoas_e_familias": [
        {"fonte": "CNC — Peic (famílias com contas em atraso)", "ponto": "Out/2022", "valor": "30,3%", "detalhe": "Recorde da série na época", "url": "https://maisretorno.com/portal/brasil-tem-recorde-de-303-das-familias-inadimplentes-em-outubro-mostra-cnc"},
        {"fonte": "CNC — Peic (famílias com contas em atraso)", "ponto": "Abr/2025", "valor": "29,1%", "detalhe": "", "url": "https://www12.senado.leg.br/noticias/infomaterias/2026/05/dividas-em-recorde-assombram-as-familias-brasileiras"},
        {"fonte": "CNC — Peic (famílias com contas em atraso)", "ponto": "Abr/2026", "valor": "29,7%", "detalhe": "12,3% dessas famílias dizem que não conseguirão quitar as dívidas", "url": "https://www12.senado.leg.br/noticias/infomaterias/2026/05/dividas-em-recorde-assombram-as-familias-brasileiras"},
        {"fonte": "Serasa Experian (pessoas negativadas)", "ponto": "Fev/2026", "valor": "81,7 milhões", "detalhe": "Alta de 38,1% em dez anos", "url": "https://www.serasa.com.br/imprensa/10-anos-do-mapa-de-inadimplencia/"},
        {"fonte": "Serasa Experian (pessoas negativadas)", "ponto": "Ago/2026", "valor": "≈ 84 milhões", "detalhe": "Maior número da série, após 20 meses seguidos de alta (fontes citam 83,9 e 84,0 milhões)", "url": "https://www.serasaexperian.com.br/conteudos/indicadores-economicos/"},
    ],
    "desenrola": {
        "fonte": "Ministério da Fazenda e B3, via Istoé Dinheiro (balanço intermediário de dez/2023)", "url": "https://istoedinheiro.com.br/desenrola-aponta-renegociacao-r-29-bi-dividas",
        "resumo": "10,7 milhões de pessoas renegociaram R$ 29 bilhões até dez/2023; na faixa 2, 1 milhão de pessoas renegociaram R$ 5 bi com descontos médios de 90% à vista e 85% parcelado.",
        "desenrola_3": "Desenrola 3 (2026): R$ 150 bi em dívidas elegíveis, desconto mínimo de 90% e dívidas de até R$ 10 mil (Ranking dos Políticos, 15/10/2026).",
    },
}

CASA_CONTEXTO = {
    "metadados": {"atualizado_em": "2026-10-20"},
    "bandeiras_2025": {
        "fonte": "Aneel, via Tribuna de Minas (02/09/2025)", "url": "https://tribunademinas.com.br/noticias/economia/02-09-2025/bandeira-vermelha-conta-de-luz.html",
        "itens": [{"periodo": "Início de 2025", "bandeira": "Verde/amarela", "acrescimo": "R$ 0 a R$ 1,88 por 100 kWh"},
                  {"periodo": "Jun e jul/2025", "bandeira": "Vermelha 1", "acrescimo": "R$ 4,46 por 100 kWh"},
                  {"periodo": "Ago e set/2025", "bandeira": "Vermelha 2", "acrescimo": "R$ 7,87 por 100 kWh"}],
        "motivo": "Baixo nível dos reservatórios das hidrelétricas, que obriga o uso de termelétricas, mais caras.",
    },
    "tarifa_social": {
        "fonte": "Governo federal, via Cenário Energia", "url": "https://cenarioenergia.com.br/2025/07/07/programa-luz-do-povo-entra-em-vigor-e-garante-energia-gratuita-para-60-milhoes-de-brasileiros/",
        "resumo": "Desde 5/jul/2025, famílias do CadÚnico com renda de até meio salário mínimo per capita e consumo de até 80 kWh/mês têm isenção da energia, sem pedir nada. Custo estimado de até R$ 10 bi/ano, pago pela CDE (encargo na conta de todos os consumidores).",
    },
    "saneamento_marco_legal": {
        "meta": "99% da população com água e 90% com coleta e tratamento de esgoto até 2033 (Lei 14.026/2020).",
        "estudo": "Trata Brasil e GO Associados (jul/2026): 51 projetos de concessão, PPP e desestatização entre 2020 e 2026, com cerca de R$ 423,5 bi em investimentos previstos e 2,4 mil municípios; o Brasil investiu cerca de R$ 29,1 bi em 2024. Conclusão: o país não cumprirá as metas de 2033.",
        "url_estudo": "https://www.conjur.com.br/2026-jul-16/investimento-em-saneamento-e-insuficiente-para-cumprir-meta-ate-2033/",
        "cobertura_trata_brasil": "Dados de 2025 (SNIS/SINISA): cerca de 83% a 85% da população com água tratada, 55% a 56% com coleta de esgoto e 45% a 46% do esgoto gerado tratado. A metodologia mudou do SNIS para o SINISA em 2024, o que afeta a comparação entre anos.",
        "url_cobertura": "https://capitalaberto.com.br/empresas/2026/09/saneamento-busca-folego-para-cumprir-meta-de-2033",
        "gargalo": "Para o analista da Fitch citado pela Capital Aberto, \"o gargalo não é o dinheiro, é a bancabilidade\" dos projetos; juros altos encarecem o crédito do setor.",
    },
}

AUDITORIA = [
    ("Macroeconomia", "Selic no fim de 2025", "12,50%", "15,00%", "BCB SGS 432", "Erro grave: a Selic subiu a 15% em jun/2025."),
    ("Macroeconomia", "Selic no fim de 2026", "11,50% (projeção apresentada como fato)", "13,75% (out/2026)", "BCB SGS 432", ""),
    ("Macroeconomia", "Selic média de Lula (scorecard)", "11,95%", "13,27%", "BCB SGS 432", ""),
    ("Macroeconomia", "Dólar no fim de 2024", "R$ 5,75", "R$ 6,19", "BCB SGS 1 (PTAX venda)", ""),
    ("Macroeconomia", "Dívida bruta (dez/2024)", "77,8%", "76,3%", "BCB SGS 13762", "Também corrigidos 2021 (78,3 → 77,3), 2023 (74,3 → 73,8), 2025 (79,2 → 78,6) e 2026 (80,1 projetado → 82,9 em ago)."),
    ("Macroeconomia", "Dívida bruta usada no scorecard para Lula", "77,8% (dez/2024)", "82,9% (ago/2026, dado mais recente)", "BCB SGS 13762", ""),
    ("Macroeconomia", "PIB 2019", "1,2%", "1,3%", "IBGE SIDRA 6784", "Revisão das Contas Nacionais."),
    ("Macroeconomia", "PIB 2026", "2,1% (projeção apresentada como fato)", "1,9% acumulado em 4 trimestres até o 2º tri (parcial)", "IBGE SIDRA 5932", ""),
    ("Macroeconomia", "Crescimento médio de Lula", "2,8% a.a.", "3,0% a.a. (2023–2025)", "IBGE", ""),
    ("Macroeconomia", "Balança comercial 2026", "US$ 65,0 bi (projeção)", "Removido — ano em curso", "MDIC/Secex", ""),
    ("Inflação", "IPCA 2025", "4,10%", "4,26%", "IBGE (BCB SGS 433)", ""),
    ("Inflação", "IPCA acumulado de Lula", "14,85%", "18,87% (jan/2023–set/2026)", "IBGE (BCB SGS 433)", ""),
    ("Inflação", "IPCA médio anual de Lula", "4,45%", "4,72%", "Cálculo sobre a série oficial", ""),
    ("Inflação", "Maior IPCA 12m de Lula", "5,19% (set/2023)", "5,53% (abr/2025)", "Cálculo sobre a série oficial", ""),
    ("Inflação", "Menor IPCA 12m de Bolsonaro", "2,13% (mai/2020)", "1,88% (mai/2020)", "Cálculo sobre a série oficial", ""),
    ("Alimentos", "Tabela de preços de 7 alimentos", "Preços e variações sem fonte (ex.: carnes -12,6% e feijão -13,4% com Lula)", "Variações oficiais do IPCA: carnes +18,5%, feijão +3,0%, café +44,3% com Lula", "IBGE SIDRA 1419/7060", "Os valores anteriores não batiam com nenhuma série oficial."),
    ("Trabalho", "Saldo CAGED de Lula", "+6,06 milhões", "+5,55 milhões (jan/2023–ago/2026)", "MTE — Novo CAGED (série com ajustes)", "Revisão 2: ver linha \"CAGED — revisão com série ajustada\"."),
    ("Trabalho", "Saldo CAGED 2024", "1.685.250", "1.677.575", "MTE", ""),
    ("Trabalho", "Saldo CAGED 2025", "1.740.000 (estimado)", "1.279.498", "MTE", ""),
    ("Trabalho", "Saldo CAGED 2026", "1.150.000 (estimado)", "1.134.033 (jan–ago)", "MTE", ""),
    ("Trabalho", "Saldo CAGED 2022", "2.013.161", "2.013.261", "MTE", "Erro de digitação."),
    ("Trabalho", "Desemprego médio Bolsonaro / Lula", "11,5% / 7,1%", "12,1% / 6,7%", "IBGE SIDRA 4099", ""),
    ("Trabalho", "Rendimento real no fim de cada período", "R$ 3.090 / R$ 3.280", "R$ 3.317 / R$ 3.777", "IBGE SIDRA 6390", "Os valores anteriores não correspondiam à série deflacionada."),
    ("Segurança", "Feminicídios 2024", "1.410", "1.504", "FBSP Anuário 2026", ""),
    ("Segurança", "Mortes violentas 2024", "44.800 (taxa 19,9)", "44.127 (taxa 20,8)", "FBSP Anuários 2025/2026", ""),
    ("Segurança", "Mortes violentas 2025", "Ausente", "40.775 (taxa 19,1)", "FBSP Anuário 2026", "Dado novo."),
    ("Segurança", "Taxas de 2022 e 2023", "21,6 e 20,8", "23,3 e 22,8 (base Censo 2022)", "FBSP", ""),
    ("Agro", "Safra 2024/25", "326,9 Mt", "350,2 Mt", "CONAB 12º levantamento", ""),
    ("Agro", "Safra 2025/26", "334,5 Mt (estimativa antiga)", "361,7 Mt", "CONAB, set/2026", ""),
    ("Agro", "Safra 2022/23", "322,8 Mt", "324,4 Mt (revisado)", "CONAB", ""),
    ("Educação", "Analfabetismo mais recente", "5,2% (2024)", "5,3% (2024) e 4,9% (2025)", "IBGE SIDRA 7113", ""),
    ("Visão geral", "Gráfico radar", "Notas de 0 a 100 digitadas à mão, sem fórmula", "Calculadas a partir do scorecard (normalização por indicador)", "—", "Antes não havia critério reproduzível."),
    ("Minorias", "Desemprego por sexo e raça", "Valores anuais sem fonte (ex.: mulheres 8,1% em 2024)", "Série trimestral oficial (SIDRA 4093 e 6402)", "IBGE — PNAD Contínua", "Agora coletada pela API."),
    ("Minorias", "Razão salarial mulher/homem", "78,5% (2022) → 81,8% (2024), sem fonte", "77,9% (4º tri/2022) → 80,3% (2º tri/2026)", "IBGE SIDRA 5436", "Rendimento habitual real de todos os trabalhos."),
    ("Checagens", "Falas repetidas", "Mesma fala contada várias vezes (por agência e por evento)", "237 checagens consolidadas em 172 falas únicas", "—", "A visão por falas únicas virou o padrão; a lista completa por agência continua disponível."),
    ("Checagens (2ª revisão)", "Lupa e Ranking dos Políticos", "—", "194 de 194 checagens reconferidas na página original: todas conferem, inclusive os placares oficiais", "Agência Lupa; Ranking dos Políticos", ""),
    ("Checagens (2ª revisão)", "Estadão Verifica", "5 checagens copiadas de fonte secundária (Coletivo Bereia), 2 com rótulo errado", "28 checagens extraídas do texto original; mansão de R$ 10 mi = \"exagerado\" (não \"enganoso\"); salário mínimo = \"enganoso\" (não \"falso\")", "Estadão Verifica", "A fonte secundária resumia mal os rótulos."),
    ("Checagens (2ª revisão)", "Aos Fatos — rótulos", "\"Verdadeiro, com ressalva\" em 2 falas de Lula; \"Falta contexto\" no prontuário de Flávio", "\"Verdadeiro\" (7,5% e obras paradas) e \"Já existe\" (prontuário), como no texto da agência", "Aos Fatos", ""),
    ("Checagens (2ª revisão)", "Aos Fatos — fala omitida", "Fala de Lula sobre déficit de 2,8% (Globo, 15/10) não estava na base", "Incluída: Aos Fatos a tratou como fato (déficit do 1º ano do governo), enquanto o Ranking a classificou como falsa", "Aos Fatos", "Exemplo de como o mesmo trecho recebe leituras diferentes."),
    ("Checagens (2ª revisão)", "Contrapontos", "3 com fonte trocada ou informação que não estava na fonte citada", "Fonte corrigida (Lupa no lugar de Aos Fatos) e trechos sem respaldo removidos", "—", ""),
    ("Segurança (2ª revisão)", "Feminicídios 2019–2023", "1.330 / 1.354 / 1.341 / 1.447 / 1.467", "1.326 / 1.350 / 1.347 / 1.455 / 1.475", "Anuários FBSP (edição 2026 para 2021–2023)", "O Anuário revisa anos anteriores a cada edição."),
    ("Segurança (2ª revisão)", "Mortes violentas 2021 e taxa de 2022", "47.503 (22,3) e taxa 23,3", "48.431 (24,0) e taxa 23,4", "Anuário FBSP 2023", ""),
    ("Social (2ª revisão)", "Pobreza 2021", "36,7%", "36,8% (série revisada da SIS 2025)", "IBGE — SIS", ""),
    ("Políticas (2ª revisão)", "BEm (2020)", "\"Mais de 20 milhões de acordos\"", "Cerca de 10 milhões de trabalhadores", "TCU / governo federal", ""),
    ("Políticas (2ª revisão)", "Leilão do 5G", "\"R$ 47 bi em compromissos\"", "Valor econômico estimado de R$ 47,2 bi; outorgas de R$ 7,4 bi", "Anatel / Teletime", ""),
    ("Políticas (2ª revisão)", "Eletrobras", "União com \"cerca de 40% do capital\"", "De ~72% para 45% do capital votante, voto limitado a 10%", "Chesf — demonstrações 2022", ""),
    ("Políticas (2ª revisão)", "Pé-de-Meia", "Custo de R$ 7 a 8 bi/ano", "R$ 12,5 bi/ano (TCU), com bloqueio de R$ 6 bi em jan/2025", "TCU", ""),
    ("Políticas (2ª revisão)", "MEC no governo Bolsonaro", "\"Cinco ministros\"; \"cerca de 200 escolas\" cívico-militares", "Quatro ministros empossados; 202 a 216 escolas", "MEC / imprensa", ""),
    ("Links (2ª revisão)", "Fontes quebradas", "CAGED (404), CNC/Peic (404), CONAB (certificado inválido), raiz do SIDRA (bloqueada)", "Trocadas por páginas que respondem e por tabelas específicas do SIDRA", "—", "A página do IBGE (SIS) bloqueia apenas acesso automatizado e foi mantida."),
    ("Trabalho (3ª revisão)", "CAGED — revisão com série ajustada", "2020: +142.690 · 2021: +2.776.733 · 2022: +2.013.161/2.013.261 · 2023: +1.483.598 (valores das primeiras divulgações de cada ano)", "2020: −189.393 · 2021: +2.782.295 · 2022: +2.014.894 · 2023: +1.455.279 (série com ajustes de dez/2025)", "MTE — Novo CAGED, apresentação de dez/2025 (pág. 11)", "O painel do MTE usa a série com ajustes (declarações fora do prazo). 2020 virou negativo. Total Bolsonaro: +5,25 mi; Lula: +5,55 mi."),
    ("Inadimplência (3ª revisão)", "Página \"Endividamento\"", "Famílias endividadas (CNC), inadimplentes e negativados (Serasa) em séries anuais sem fonte confirmada", "Página \"Inadimplência\": só carteiras em atraso (BCB, série mensal oficial) e pontos de contas em atraso confirmados (CNC e Serasa)", "Banco Central — SGS 21082 a 21151", "Séries removidas: Serasa 2019–2024 (63,8 → 72,5 mi) e CNC 2019–2025, que não conseguimos confirmar."),
    ("Inadimplência (3ª revisão)", "Balanço do Desenrola", "15,2 milhões de pessoas, R$ 53,1 bi e desconto médio de 83%", "10,7 milhões de pessoas e R$ 29 bi até dez/2023 (balanço intermediário); faixa 2 com descontos médios de 90% e 85%", "Ministério da Fazenda e B3, via Istoé Dinheiro", "Não encontramos balanço final do programa."),
    ("Saneamento (3ª revisão)", "Marco do Saneamento — números do setor", "Rascunho com \"66 leilões, R$ 370 bi, 1.550 cidades\" (da busca, não da fonte)", "51 projetos, R$ 423,5 bi previstos e 2,4 mil municípios (Trata Brasil/GO Associados, jul/2026)", "Conjur", "Conferido na matéria original antes de entrar no painel."),
    ("Repercussão (3ª revisão)", "AtlasIntel — Desenrola 67% e Pé-de-Meia 61%", "Apareciam só no resumo da busca", "Confirmados em duas matérias independentes (Plantão Brasil e Fetec-PR); Gás do Povo 60% também confirmado", "AtlasIntel/Bloomberg (3 a 8/out/2026)", "O InfoMoney lista só parte das medidas."),
    ("Auditoria de pendências (4ª revisão)", "Cesta básica do DIEESE (São Paulo, dez/ano)", "2018: 467,41 · 2023: 772,51 · 2024: 810,15 · 2025: 835,40; % do salário mínimo de 2022 = 65,3%", "2018: 471,44 · 2023: 761,01 · 2024: 841,29 · 2025: 845,95; % do salário mínimo líquido de 2022 = 70,58%", "DIEESE — boletins de dezembro (2018 a 2025)", "Os valores de 2018, 2023, 2024 e 2025 estavam errados. O percentual agora é do salário mínimo líquido, como o DIEESE calcula."),
    ("Auditoria de pendências (4ª revisão)", "IDEB nacional", "2017: 5,8/4,7/3,8 · série parava em 2023", "2019, 2021, 2023 e 2025 (6,3 / 5,3 / 4,5 no último); 2017 removido por não ter sido confirmado", "Inep (divulgação de 05/08/2026) e Exame", "O IDEB 2025 saiu em 5/ago/2026."),
    ("Auditoria de pendências (4ª revisão)", "Orçamento do MEC", "R$ 118,5 bi (2019) a R$ 169,5 bi (2025), sem fonte, com 2025 projetado", "Despesa paga, em R$ bi de dez/2024: 164,6 · 152,3 · 151,9 · 156,4 · 172,6 · 174,9 (2019 a 2024)", "Todos Pela Educação, com Siafi", "Valores deflacionados pelo IPCA; 2025 ainda não disponível."),
    ("Auditoria de pendências (4ª revisão)", "Queimadas 2021 e 2022", "Em branco", "184.081 e 200.763 focos (também 2020 = 222.797 e 2025 = 136.393, ano completo)", "Inpe — CSVs anuais do Programa Queimadas", "Contagem direta das linhas dos arquivos abertos."),
    ("Auditoria de pendências (4ª revisão)", "Assassinatos de pessoas trans em 2021", "Em branco", "140 casos", "ANTRA, via CNN Brasil", ""),
    ("Auditoria de pendências (4ª revisão)", "Armas e drogas (segurança)", "Registros de CACs 783.385 x 142.000; apreensão de cocaína 398,5 x 215,2 t; maconha 1.850 x 1.120 t", "Armas apreendidas pela PF: 8.812 (2019–2022) x 9.373 (2023–out/2026); acervo de CACs de ~350 mil para mais de 1 milhão", "Agência Lupa e Instituto Sou da Paz", "Os números de drogas e de registros de CACs não foram confirmados e saíram do painel."),
    ("Auditoria de pendências (4ª revisão)", "Textos soltos (inflação e silvicultura)", "\"Deflação de grãos no atacado\", \"estados como MS, MG, PR e BA\" e \"mais de 80%\" sem cálculo", "Frases ligadas a dados: IPCA 4,62% / 4,83% / 4,26% (2023–25) e silvicultura = 84% do valor florestal em 2024", "IBGE (IPCA e PEVS)", "Afirmações sem fonte foram removidas."),
    ("Transparência e usabilidade (5ª revisão)", "Texto do painel e da Metodologia", "\"Baseada estritamente em dados públicos oficiais\" e \"Sem viés seletivo… na íntegra\"", "Texto passou a dizer que a base é principalmente oficial, com estudos de entidades, checagens e reportagens, e a Metodologia lista critérios, limites e o que o painel não mede", "Revisão do próprio painel", "As frases anteriores prometiam mais do que o painel entrega: há seleção de indicadores e fontes não oficiais."),
    ("Transparência e usabilidade (5ª revisão)", "Tipos de fonte por página", "Não havia", "Cada página mostra os tipos de fonte usados (dado oficial, estudo de entidade, checagem, pesquisa, reportagem, promessa, cálculo do painel)", "Painel", ""),
    ("Transparência e usabilidade (5ª revisão)", "Comparação de períodos de tamanhos diferentes", "Só mandato completo (48 x 44–45 meses)", "Modos \"mesmo período\", \"Bolsonaro sem 2020\" e mandatos completos para desemprego, renda real e IPCA; filtro de eixos no placar", "IBGE (PNAD, IPCA); cálculo do painel", "Indicadores anuais (PIB, CAGED, dívida, segurança) ficam fora do recorte alinhado por não terem série mensal fechada."),
    ("Transparência e usabilidade (5ª revisão)", "Propostas de campanha: texto dos planos", "Só resumos de imprensa", "53 propostas com página conferida nos PDFs dos planos de Lula (84 págs.) e Flávio (76 págs.)", "Programa de governo de Lula e plano de Flávio (PDFs); o arquivo do TSE bloqueou download automático, então foram usadas cópias de Congresso em Foco e Poder360", "Páginas confirmadas por busca de palavra-chave na página; textos são paráfrases do painel."),
    ("Transparência e usabilidade (5ª revisão)", "UOL Confere e Comprova", "Não incluídos", "Buscados; nenhum veredito explícito sobre falas dos candidatos foi encontrado, então não entram na contagem", "Buscas em 21/10/2026", "Debate da Globo (23/10) ainda não aconteceu."),
    ("Educação (6ª revisão)", "Dados recentes da aba de Educação", "Só IDEB, analfabetismo e orçamento até 2024", "Adicionados PISA 2025 (leitura 408, matemática 377, ciências 409; 2018 e 2022 para comparação), ICA 56% ➔ 59% ➔ 66%, Censo Escolar 2025 (tempo integral 15,1% ➔ 25,8%, internet nas escolas 82,8% ➔ 94,5%) e Pé-de-Meia com a ressalva de que são números do MEC", "OCDE/Inep (via Poder360), Inep (ICA), Agência Brasil/Censo Escolar, Gazeta SP", "Orçamento pago do MEC em 2025, notas do Enem 2025 e Saeb 2025 não foram localizados em fonte confirmável e estão listados como pendentes na aba."),
    ("Educação (6ª revisão)", "Orçamento do MEC 2025 e 2026", "Série de valores pagos terminava em 2024", "Incluído o orçamento atualizado (dotação) do Portal da Transparência: R$ 236,17 bi (2025) e R$ 269,60 bi (2026, em execução), em reais correntes, em cartão separado", "Portal da Transparência (valores informados pelo usuário; o site bloqueia acesso automatizado)", "Não é comparável com a série do Anuário (valores pagos deflacionados). O valor pago de 2025 e 2026 continua pendente."),
    ("Saúde (7ª revisão)", "Nova página de Saúde", "Não havia", "Expectativa de vida e mortalidade infantil (IBGE), dengue, Covid-19 (óbitos acumulados), vacinação (municípios na meta) e as políticas de saúde, todos com fonte", "IBGE, Ministério da Saúde via imprensa e boletins, CNM", "Gasto federal em saúde por ano, cobertura vacinal nacional, filas do SUS e dados de 2019–2021 de mortalidade infantil não foram confirmados e estão listados como pendentes na página. Os números de dengue e Covid vêm de painéis oficiais citados pela imprensa e variam conforme a data de corte."),
    ("Comércio exterior (7ª revisão)", "Nova página Comércio Exterior (ComexStat)", "Superávit comercial só no scorecard, sem série própria", "Exportações, importações e saldo de 2018 a 2025, 2026 parcial até setembro contra o mesmo período de 2025, destinos e pauta por seção, direto da API do ComexStat/MDIC", "MDIC/Secex — ComexStat (API pública)", "Os números de 2022 a 2024 conferem com o scorecard (61,5, 98,9 e 74,2). Para 2025 o MDIC já revisou: 68,1 de saldo e 348,3 de exportações, contra 68,3 e 348,7 nas versões anteriores; o scorecard foi atualizado."),
    ("Meio ambiente (8ª revisão)", "PRODES Amazônia 2025 e 2026", "2025 = 5.796 km² (estimativa de out/2025)", "2025 = 5.731 km² (consolidado) e 2026 = 3.335 km² (estimativa de 16/10/2026, menor da série); Cerrado 2026 = 5.517 km² (estimativa)", "Inpe — TerraBrasilis (arquivo de taxas do painel PRODES) e Poder360 (16/10/2026)", "Médias por governo continuam só com anos consolidados; a estimativa de 2026 aparece no gráfico, marcada."),
    ("Série histórica (8ª revisão)", "Página FHC a Lula 3", "Só Bolsonaro x Lula 3", "15 indicadores para 9 mandatos desde 1995 (PIB, IPCA, Selic, saldo comercial, desemprego, salário mínimo real, renda, Gini, pobreza, extrema pobreza, homicídios, dívida líquida e bruta, primário, desmatamento)", "Banco Central (SGS), Ipeadata (IBGE harmonizado pelo Ipea, Atlas da Violência) e Inpe (TerraBrasilis)", "Adaptações: desemprego antes de 2013 é a PNAD antiga reescalada pela razão PNADC/PNAD de 2013–2014 (estimativa do painel); dívida e primário só desde 2001–2006, sem preencher com outra metodologia; 2016 conta para Temer nos dados anuais. Valores por mandato podem diferir um pouco do scorecard Bolsonaro x Lula por usarem outra agregação (ex.: média geométrica do PIB)."),
    ("Série histórica (9ª revisão)", "Todos os governos em cada aba", "Página separada só com 15 indicadores", "Seletor no topo de 18 abas (padrão Bolsonaro x Lula 3, com opção de todos os governos): ao trocar o par, a aba inteira é refeita no mesmo formato para os governos escolhidos, com 35 indicadores (IDEB, PISA, analfabetismo, CAGED, inflação de alimentos, dólar, exportações, importações, safra, indústria, abate, tarifa de energia, inadimplência, saúde, desemprego de pretos e pardos e os 15 anteriores)", "Banco Central (SGS), Ipeadata, Inep (planilha oficial do Ideb e relatório PISA 2025), Inpe", "Onde não há série comparável o quadro mostra *; onde o valor vem de outra metodologia (PNAD antiga reescalada, Censo, projeção do IBGE, CAGED antigo) o número leva *. Cada linha tem link 'dados ↗' para a série exata; nos rodapés, códigos SGS e SIDRA viram links diretos."),
    ("Visão Geral (10ª revisão)", "Visão Geral para qualquer par de governos", "Outros pares tinham um visual diferente do Bolsonaro x Lula", "Mesmos cartões, resumo em 10 números, radar, placar com eixos e tabela consolidada para os 72 pares possíveis; cores pelo partido do presidente na época (PSDB, PT, MDB, PSL/PL), com tons diferentes para mandatos do mesmo partido", "Base histórica do painel (Banco Central, Ipeadata, Inep, Inpe)", "No radar de outros pares, cada eixo é a posição do governo entre os nove mandatos (0 = pior, 100 = melhor), porque vários indicadores podem ser negativos. Câmbio e importações entram como 'depende de contexto'. A comparação alinhada (mesmo período) só existe para Bolsonaro x Lula 3."),
    ("Fontes (11ª revisão)", "Links de fonte", "Links do Ipeadata quebravam no meio (aspas e parênteses no endereço) e três páginas passaram a pedir login (Agência Gov e Inep)", "Cada série aponta para a página oficial legível (SIDRA, Banco Central, CONAB, Atlas da Violência, IBGE); o dado bruto do Ipeadata virou link complementar com endereço codificado; substituídos os links fora do ar", "Varredura automática de 164 links em 22/10/2026", "Também corrigida a nota das terras indígenas: os ~2,5 milhões de hectares eram só das quatro homologações de 18/11/2025, não do total de 20."),
    ("Abas e propostas (12ª revisão)", "Outros governos em todas as abas e planos de governo", "Ao trocar o par, as abas temáticas mudavam de layout; não havia os planos dos presidentes eleitos", "Abas temáticas mantêm o formato do Bolsonaro x Lula (cartões A ➔ B, gráficos numerados com fonte, gráficos mês a mês desde a posse e contexto no fim) para qualquer par; aba Propostas ganhou 67 propostas dos planos de FHC (1994, 1998), Lula (2002, 2006, 2022), Dilma (2010, 2014), Temer (Ponte para o Futuro, 2015) e Bolsonaro (2018)", "PDFs dos planos (SciELO/Centro Edelstein, UFG, Fundação Perseu Abramo, Conjur, Fiocruz, Pleno News, RTP); séries mensais do Banco Central e Ipeadata", "Cada proposta foi conferida por palavra-chave na página citada do PDF (67 de 67). São paráfrases do painel; o texto original prevalece."),
    ("Saúde (13ª revisão)", "Médicos, leitos, hospitais, gasto federal e vacinação", "A aba tinha só expectativa de vida, dengue, Covid e municípios na meta de vacinação", "Médicos por 10 mil habitantes e leitos do SUS (CNES/DATASUS, 2010–2025), hospitais gerais, despesa da União na função Saúde (Tesouro/SICONFI, 2014–2025, em valores de 2025 e % do PIB) e cobertura vacinal 2000–2025 (OMS/Unicef)", "CNES/DATASUS via Ipeadata; Tesouro Nacional (SICONFI/DCA); OMS (API aberta); Banco Central (PIB e IPCA)", "A série de médicos do CNES conta cadastros e difere da Demografia Médica (597 mil médicos em 2024). A vacinação usa a estimativa da OMS, que difere um pouco do Ministério (ex.: pólio 2019: 72% na OMS e 84% no Ministério). Cobertura da atenção primária, filas e gasto de estados e municípios seguem pendentes."),
    ("Saúde (13ª revisão)", "Programas de saúde de cada governo", "Só 2 políticas de saúde (Bolsonaro e Lula 3)", "21 programas de FHC a Lula 3, em linguagem simples, cada um com pontos positivos, críticas e link da fonte; leis conferidas no Planalto", "Planalto, Ipea, Tesouro, TCU, CGU, CNS, Ciência & Saúde Coletiva, Fiocruz e imprensa", "Onde só há dado do governo ou do setor interessado, o texto avisa. Duas situações foram corrigidas na conferência: a EC 95 consta como substituída pela LC 200/2023, e o piso da enfermagem como em vigor com assistência da União (não verificamos a data exata do fim da suspensão do STF). Dilma 2 e vários programas menores ainda não foram mapeados."),
    ("Cores e comparações (13ª revisão)", "Cores dos governos e queda da pobreza/Gini", "Lula em coral e Dilma em vermelho escuro; pobreza, Gini e dívida apareciam como variação negativa (\"-11 x -8\")", "Lula em vermelho forte e Dilma em vermelho claro; pobreza, extrema pobreza e Gini passaram a \"queda no mandato\" (positivo = caiu, maior queda = melhor); dívida e tarifa indicam \"negativo = caiu\"", "Conferência por força bruta de todos os pares de mandatos (13 casos com dois valores negativos)", "A lógica de quem é \"melhor\" já estava correta (menor é melhor, então o mais negativo vence); o problema era de leitura, não de conta."),
    ("Pipeline", "build_database.py", "Sobrescrevia o scorecard com versão menor (12 de 17 itens) e gravava valores fixos", "Selic, câmbio, dívida, PIB, IPCA e Gini vêm das APIs; scorecard e CONAB não são mais sobrescritos", "—", ""),
]


if __name__ == "__main__":
    salvar("scorecard.json", SCORECARD)
    salvar("indicadores_sociais_ambientais.json", SOCIAIS_AMBIENTAIS)
    salvar("minorias_curado.json", MINORIAS)
    salvar("inadimplencia.json", INADIMPLENCIA)
    salvar("contas_casa_contexto.json", CASA_CONTEXTO)
    salvar("auditoria.json", [dict(zip(("area", "item", "antes", "depois", "fonte", "observacao"), a)) for a in AUDITORIA])
