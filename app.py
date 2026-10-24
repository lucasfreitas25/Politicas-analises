import streamlit as st
import os

# Configuração da página Streamlit (deve ser a primeira chamada do Streamlit)
st.set_page_config(
    page_title="Observatório: Governo Bolsonaro vs Governo Lula | Dados Oficiais & Checagens 2026",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar estilos CSS customizados
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Importar módulos de visualização
from modules.ui_components import render_hero_banner
from modules.ux import render_tipos_fonte, render_print_button, render_acessibilidade
from modules.tabs_overview import render_tab_overview
from modules.tabs_labor import render_tab_labor
from modules.tabs_inflation import render_tab_inflation
from modules.tabs_food_basket import render_tab_food_basket
from modules.tabs_agro_conab import render_tab_agro_conab
from modules.tabs_industry import render_tab_industry
from modules.tabs_livestock import render_tab_livestock
from modules.tabs_forestry import render_tab_forestry
from modules.tabs_macro import render_tab_macro
from modules.tabs_social_environment import render_tab_social_environment
from modules.tabs_education import render_tab_education
from modules.tabs_security import render_tab_security
from modules.tabs_social_inclusion import render_tab_social_inclusion
from modules.tabs_indebtedness import render_tab_indebtedness
from modules.tabs_head_to_head import render_tab_head_to_head
from modules.tabs_policy_balance import render_tab_policy_balance
from modules.tabs_fact_check import render_tab_fact_check
from modules.tabs_audit import render_tab_audit
from modules.tabs_environment import render_tab_environment
from modules.tabs_campaign import render_tab_campaign
from modules.tabs_home_costs import render_tab_home_costs
from modules.tabs_trade import render_tab_trade
from modules.tabs_health import render_tab_health
from modules.historico_ui import render_seletor, render_aba_comparada, ABAS_COMPARAVEIS, PADRAO
from modules.tabs_methodology import render_tab_methodology


def pagina(funcao, titulo, icone, url, padrao=False):
    return st.Page(funcao, title=titulo, icon=icone, url_path=url, default=padrao)


# Navegação agrupada por seções (substitui o rádio único de 16 itens)
navegacao = st.navigation({
    "Início": [
        pagina(render_tab_overview, "Visão Geral & Scorecard", "🌟", "visao-geral", padrao=True),
        pagina(render_tab_head_to_head, "Comparador Direto", "⚖️", "comparador"),
        pagina(render_tab_policy_balance, "Políticas, Leis & Repercussão", "📜", "politicas"),
    ],
    "Eleição 2026": [
        pagina(render_tab_fact_check, "Checagem: Lula x Flávio", "🗳️", "checagem-eleicao-2026"),
        pagina(render_tab_campaign, "Propostas de campanha", "📋", "propostas-campanha"),
    ],
    "Economia & Bolso": [
        pagina(render_tab_labor, "Mercado de Trabalho", "👥", "trabalho"),
        pagina(render_tab_inflation, "Inflação (IPCA)", "📈", "inflacao"),
        pagina(render_tab_food_basket, "Cesta Básica & Preços", "🛒", "cesta-basica"),
        pagina(render_tab_indebtedness, "Inadimplência", "💳", "inadimplencia"),
        pagina(render_tab_home_costs, "Energia, Água & Esgoto", "🚰", "energia-agua-esgoto"),
        pagina(render_tab_macro, "PIB, Juros, Câmbio & Dívida", "🏛️", "macroeconomia"),
        pagina(render_tab_social_environment, "Fiscal, Pobreza & Desigualdade", "🧾", "fiscal-social-ambiental"),
    ],
    "Setores Produtivos": [
        pagina(render_tab_agro_conab, "Agropecuária & Grãos", "🌾", "agro"),
        pagina(render_tab_trade, "Comércio Exterior (ComexStat)", "🚢", "comercio-exterior"),
        pagina(render_tab_industry, "Indústria (PIM-PF)", "🏭", "industria"),
        pagina(render_tab_livestock, "Pecuária (PPM)", "🐄", "pecuaria"),
        pagina(render_tab_forestry, "Silvicultura & Extrativismo", "🌲", "silvicultura"),
    ],
    "Sociedade": [
        pagina(render_tab_education, "Educação", "🎓", "educacao"),
        pagina(render_tab_health, "Saúde", "🏥", "saude"),
        pagina(render_tab_security, "Segurança Pública", "🛡️", "seguranca"),
        pagina(render_tab_social_inclusion, "Mulheres, Raça & Minorias", "🤝", "inclusao"),
        pagina(render_tab_environment, "Meio Ambiente & Clima", "🌳", "meio-ambiente"),
    ],
    "Políticas & Transparência": [
        pagina(render_tab_audit, "Auditoria dos Dados", "🔎", "auditoria"),
        pagina(render_tab_methodology, "Metodologia & Fontes", "📚", "metodologia"),
    ],
}, expanded=True)

# Banner Superior
render_hero_banner()
# A página padrão é servida na raiz, e aí url_path vem vazio
pagina_atual = navegacao.url_path or "visao-geral"
render_tipos_fonte(pagina_atual)

# Barra Lateral (Sidebar)
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0 12px 0; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
      <div>
        <div style="font-weight: 800; font-size: 1.1rem; color: #ffffff; letter-spacing: -0.02em;">Observatório Oficial</div>
        <div style="font-size: 0.72rem; color: #38bdf8; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">GOVERNOS DE FHC A LULA 3 · 1995–2026</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Ações rápidas")
    if st.button("Sincronizar dados oficiais (API)", width="stretch",
                 help="Baixa de novo as séries do IBGE (SIDRA) e do Banco Central (SGS). Bases curadas (scorecard, checagens, CONAB) não são alteradas."):
        with st.spinner("Conectando às APIs do IBGE SIDRA e Banco Central..."):
            try:
                import build_database
                build_database.build_data()
                st.cache_data.clear()
                st.success("✔ Base de dados oficiais sincronizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro na sincronização: {e}")

    render_print_button()
    render_acessibilidade()

    st.markdown("""
    <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.6; margin-top: 10px;">
      <b style="color: #cbd5e1;">Fontes primárias:</b><br/>
      IBGE (SIDRA) · Banco Central (SGS) · MTE (CAGED) · MDIC (ComexStat) · CONAB · Inpe · FBSP · DIEESE · CNC<br/>
      <b style="color: #cbd5e1;">Checagens:</b> Agência Lupa · Aos Fatos · Ranking dos Políticos · Estadão Verifica<br/><br/>
      <i style="color: #64748b;">Dados auditados em 21/10/2026. Veja a página "Auditoria dos Dados".</i>
    </div>
    """, unsafe_allow_html=True)

# Renderizar página selecionada. Nas abas com série longa, o seletor no topo troca os governos comparados na aba inteira;
# o padrão (Bolsonaro x Lula 3) mostra a aba original, completa.
if pagina_atual in ABAS_COMPARAVEIS:
    gov_a, gov_b, gov_todos = render_seletor()
    # Na Visão Geral, um par diferente usa o mesmo painel (cartões, radar, placar e tabela) com outros governos
    padrao_ou_vg = ((gov_a, gov_b) == PADRAO or pagina_atual == "visao-geral") and not gov_todos
    if padrao_ou_vg or not render_aba_comparada(pagina_atual, gov_a, gov_b, gov_todos):
        navegacao.run()
else:
    navegacao.run()

# Rodapé Global
st.markdown("---")
st.markdown("""
<div class="info-box" style="font-size: 0.82rem;">
  <b>Aviso:</b> este painel é informativo e apartidário. Reúne dados públicos oficiais e, quando indicado, estudos e checagens de terceiros, sempre com link da fonte.
  A escolha de leis e programas é uma <b>seleção</b> das mais conhecidas, não o conjunto completo, e a cobertura varia de governo para governo (veja o quadro no topo de cada página).
  Resultados de indicadores não provam, sozinhos, que um governo causou a mudança: economia, clima, pandemia e cenário internacional também pesam.
  Encontrou um erro? Avise quem publicou o painel, com o link da página e da fonte.
</div>
<div style="text-align: center; color: #94a3b8; font-size: 0.82rem; padding: 14px 0;">
  <b style="color: #cbd5e1;">Observatório Estatístico</b> • Desenvolvido em Python & Streamlit •
  Dados oficiais (IBGE, BCB, MTE, MDIC, CONAB, Inpe, FBSP, DIEESE, CNC) e checagens de agências independentes • Revisado em outubro de 2026
</div>
""", unsafe_allow_html=True)
