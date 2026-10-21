import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Paleta vibrante e de alto contraste
COLOR_BOLSONARO = "#3B82F6"   # Azul Real Vibrante
COLOR_LULA = "#F43F5E"        # Carmim / Coral Vibrante
COLOR_ACCENT = "#10B981"      # Verde Esmeralda
COLOR_NEUTRAL = "#94A3B8"     # Slate Claro
COLOR_GOLD = "#F59E0B"        # Âmbar Dourado

def apply_plotly_theme(fig, title="", height=420):
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 15, "family": "Plus Jakarta Sans, sans-serif", "color": "#FFFFFF"},
            "x": 0.02,
            "xanchor": "left",
            "y": 0.98,
            "yanchor": "top"
        },
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0e1526",
        height=height,
        margin={"l": 50, "r": 30, "t": 90, "b": 50},
        font={"family": "Plus Jakarta Sans, sans-serif", "color": "#E2E8F0", "size": 12},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.01,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"size": 12, "color": "#F8FAFC"}
        },
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=13,
            font_color="#ffffff",
            font_family="Plus Jakarta Sans, sans-serif"
        ),
        xaxis=dict(
            gridcolor="#1e293b",
            showgrid=True,
            zeroline=False,
            tickfont=dict(color="#cbd5e1", size=11),
            title_font=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif")
        ),
        yaxis=dict(
            gridcolor="#1e293b",
            showgrid=True,
            zeroline=False,
            tickfont=dict(color="#cbd5e1", size=11),
            title_font=dict(color="#ffffff", size=12, family="Plus Jakarta Sans, sans-serif")
        )
    )
    return fig

def render_hero_banner():
    banner_html = (
        '<div class="hero-container">'
        '<div class="hero-title">📊 Observatório Macroeconômico: Governo Bolsonaro vs. Governo Lula</div>'
        '<div class="hero-subtitle">'
        'Análise comparativa aprofundada, independente e baseada estritamente em dados públicos oficiais do '
        '<b>IBGE</b> (PNAD Contínua, IPCA, PAM, PPM, PEVS, PIM-PF, Contas Nacionais), <b>CONAB</b>, <b>Banco Central do Brasil</b> e <b>Ministério do Trabalho</b>.'
        '</div>'
        '<div class="hero-badges">'
        '<span class="badge-tag badge-ibge">🏛️ IBGE SIDRA Oficial</span>'
        '<span class="badge-tag badge-conab">🌾 CONAB Grãos</span>'
        '<span class="badge-tag badge-bcb">🏦 Banco Central (SGS)</span>'
        '<span class="badge-tag" style="background: rgba(59, 130, 246, 0.18); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4);">💼 Novo CAGED</span>'
        '<span class="badge-tag" style="background: rgba(168, 85, 247, 0.18); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4);">⏱️ 2019 — 2026</span>'
        '<span class="badge-tag" style="background: rgba(239, 68, 68, 0.16); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4);">🗳️ Checagens Eleição 2026</span>'
        '<span class="badge-tag" style="background: rgba(148, 163, 184, 0.16); color: #e2e8f0; border: 1px solid rgba(148, 163, 184, 0.4);">🔎 Dados auditados em 20/10/2026</span>'
        '</div>'
        '</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

GOV_COLORS = {"Bolsonaro": COLOR_BOLSONARO, "Lula": COLOR_LULA}

# Cores das faixas de veredito das checagens (verde = verdade ... vermelho = mentira)
VERDICT_COLORS = {
    "Verdade": "#10B981",
    "Meia-verdade": "#F59E0B",
    "Mentira": "#EF4444",
    "Sem comprovação": "#94A3B8",
}
VERDICT_ORDER = ["Verdade", "Meia-verdade", "Mentira", "Sem comprovação"]

def gov_color(governo):
    for nome, cor in GOV_COLORS.items():
        if nome in str(governo):
            return cor
    return "#64748b"

def render_section_header(title, subtitle):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def render_source(text, url=None):
    """Rodapé de fonte padronizado abaixo de gráficos e tabelas."""
    link = f' · <a href="{url}" target="_blank">abrir fonte ↗</a>' if url else ""
    st.markdown(f'<div class="source-note">📎 Fonte: {text}{link}</div>', unsafe_allow_html=True)

def render_compare_stat(title, val_bols, val_lula, foot="", better=None):
    """Cartão compacto 'antes ➔ depois'. better: 'bolsonaro', 'lula' ou None (sem destaque)."""
    cls_b = " is-better" if better == "bolsonaro" else ""
    cls_l = " is-better" if better == "lula" else ""
    st.markdown(
        '<div class="kpi-card compare-stat">'
        f'<div class="compare-title">{title}</div>'
        '<div class="compare-values">'
        f'<span class="compare-val bolsonaro{cls_b}">{val_bols}</span>'
        '<span class="compare-arrow">➔</span>'
        f'<span class="compare-val lula{cls_l}">{val_lula}</span>'
        '</div>'
        f'<div class="compare-foot">{foot}</div>'
        '</div>',
        unsafe_allow_html=True
    )

def fmt_br(valor, casas=1):
    """Formata número no padrão brasileiro (1.234,5)."""
    if valor is None:
        return "—"
    txt = f"{valor:,.{casas}f}"
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")

def render_kpi_card(title, val_bols, val_lula, unit="", note=""):
    card_html = (
        '<div class="kpi-card">'
        '<div class="kpi-title">'
        f'<span>{title}</span>'
        f'<span style="font-size: 0.75rem; color: #38bdf8; font-weight: 600;">{unit}</span>'
        '</div>'
        '<div class="gov-row bolsonaro">'
        '<span class="gov-name" style="color: #93c5fd;">Bolsonaro (2019-22)</span>'
        f'<span class="gov-val bolsonaro">{val_bols}</span>'
        '</div>'
        '<div class="gov-row lula">'
        '<span class="gov-name" style="color: #fda4af;">Lula (2023-atual)</span>'
        f'<span class="gov-val lula">{val_lula}</span>'
        '</div>'
        f'<div class="kpi-foot">{note}</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
