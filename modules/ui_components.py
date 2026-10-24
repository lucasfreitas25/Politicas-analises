import html as html_mod
import re
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Paleta vibrante e de alto contraste
COLOR_BOLSONARO = "#3B82F6"   # Azul Real Vibrante
COLOR_LULA = "#EF2B2D"        # Carmim / Coral Vibrante
COLOR_ACCENT = "#10B981"      # Verde Esmeralda
COLOR_NEUTRAL = "#94A3B8"     # Slate Claro
COLOR_GOLD = "#F59E0B"        # Âmbar Dourado

_RE_CELULAR = re.compile(r"Mobi|Android|iPhone|iPad|iPod|Windows Phone", re.I)


def celular_pelo_navegador():
    """Palpite pelo User-Agent do navegador (o Streamlit não sabe a largura da tela no servidor)."""
    try:
        return bool(_RE_CELULAR.search(st.context.headers.get("User-Agent", "") or ""))
    except Exception:
        return False


def eh_celular():
    """Modo celular: o que está marcado no botão da barra lateral, ou o palpite pelo navegador enquanto ele não existir."""
    if "modo_celular" in st.session_state:
        return bool(st.session_state["modo_celular"])
    return celular_pelo_navegador()


def quebrar(texto, largura=30):
    """Quebra um texto em linhas de até `largura` caracteres com <br>, para títulos e rótulos longos caberem na tela do celular."""
    linhas, atual = [], ""
    for palavra in str(texto).split(" "):
        if atual and len(atual) + 1 + len(palavra) > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = (atual + " " + palavra).strip()
    if atual:
        linhas.append(atual)
    return "<br>".join(linhas)


def _ajuste_celular(fig, title, height):
    """Título menor e quebrado em linhas, legenda embaixo (sem cobrir o título), margens enxutas e eixos legíveis."""
    titulo = quebrar(title, 34)
    n_titulo = titulo.count("<br>") + 1
    n_leg = sum(1 for t in fig.data if getattr(t, "showlegend", None) is not False and getattr(t, "name", None))
    linhas_leg = max(1, -(-n_leg // 2)) if n_leg > 1 else 0
    alt = max(330, min(int(height), 520)) if height <= 520 else int(height)
    fig.update_layout(
        title={"text": f"<b>{titulo}</b>", "font": {"size": 13}, "x": 0.02, "xanchor": "left", "y": 1 - 26 / alt, "yanchor": "top"},
        margin={"l": 8, "r": 12, "t": 36 + 17 * n_titulo + 20 * linhas_leg + 14, "b": 36},
        plot_bgcolor="#111827",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.0, "xanchor": "left", "x": 0, "font": {"size": 10}, "title": {"text": ""}},
        height=alt,
    )
    fig.update_xaxes(automargin=True, tickfont={"size": 10}, title_font={"size": 11}, nticks=6)
    fig.update_yaxes(automargin=True, tickfont={"size": 10}, title_font={"size": 11})
    for a in fig.layout.annotations or []:
        a.font = dict(color="#ffffff", size=9)


def finalizar_celular(fig):
    """Última passagem antes de desenhar: vale mesmo quando a página mexeu na legenda ou nas margens depois do tema.
    Garante legenda acima do gráfico (sem cobrir o título), título inteiro e rótulos do radar dentro da tela."""
    titulo = re.sub(r"<[^>]+>", " ", (fig.layout.title.text or "")).replace("  ", " ").strip()
    n_titulo = quebrar(titulo, 34).count("<br>") + 1 if titulo else 0
    n_leg = sum(1 for t in fig.data if getattr(t, "showlegend", None) is not False and getattr(t, "name", None))
    linhas_leg = max(1, -(-n_leg // 2)) if n_leg > 1 else 0
    alt = int(fig.layout.height or 420)
    m = fig.layout.margin
    polar = any(t.type == "scatterpolar" for t in fig.data)
    fig.update_layout(
        title={"text": f"<b>{quebrar(titulo, 34)}</b>", "font": {"size": 13}, "x": 0.02, "xanchor": "left", "y": 1 - 26 / alt, "yanchor": "top"} if titulo else {},
        margin={"l": max(min(int(m.l or 8), 60), 44 if polar else 8), "r": max(min(int(m.r or 12), 60), 44 if polar else 12),
                "t": (36 + 17 * n_titulo + 20 * linhas_leg + 14) if titulo else 30, "b": max(int(m.b or 36), 36)},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.0, "xanchor": "left", "x": 0, "font": {"size": 10}, "title": {"text": ""}},
    )
    if polar:
        fig.update_layout(height=min(alt, 400))
        fig.update_polars(domain=dict(x=[0.2, 0.8], y=[0.06, 0.92]), angularaxis=dict(tickfont=dict(size=10)), radialaxis=dict(tickfont=dict(size=9)))
    return fig


def ativar_modo_celular():
    """Faz todo st.plotly_chart passar por finalizar_celular quando o modo celular está ligado."""
    if getattr(st, "_celular_ativo", False):
        return
    original = st.plotly_chart

    def plotly_chart(figure_or_data, *args, **kwargs):
        if eh_celular():
            try:
                finalizar_celular(figure_or_data)
            except Exception:
                pass
        return original(figure_or_data, *args, **kwargs)

    st.plotly_chart = plotly_chart
    st._celular_ativo = True


def mostrar_tabela(df, titulo_col=None, max_linhas_celular=80, **kwargs):
    """No computador, a tabela de sempre (st.dataframe). No celular, um cartão por linha, para não precisar rolar de lado.
    Tabelas com mais de `max_linhas_celular` linhas continuam como tabela (cartões ficariam longos demais)."""
    if not eh_celular() or len(df) > max_linhas_celular:
        return st.dataframe(df, **kwargs)
    colunas = list(df.columns)
    titulo_col = titulo_col or next((c for c in colunas if str(c).lower() in ("indicador", "política", "politica", "norma", "tributo")), colunas[0])
    cartoes = []
    for _, linha in df.iterrows():
        itens = []
        for c in colunas:
            if c == titulo_col:
                continue
            v = linha[c]
            if v is None or (isinstance(v, float) and v != v) or str(v).strip() == "":
                continue
            txt = html_mod.escape(str(v))
            if str(v).startswith("http"):
                txt = f'<a href="{html_mod.escape(str(v), quote=True)}" target="_blank">abrir ↗</a>'
            itens.append(f'<div class="tab-item"><span>{html_mod.escape(str(c))}</span><b>{txt}</b></div>')
        cartoes.append(f'<div class="ind-card"><div class="ind-card-t"><b>{html_mod.escape(str(linha[titulo_col]))}</b></div>{"".join(itens)}</div>')
    st.markdown("".join(cartoes), unsafe_allow_html=True)


def _eixo_sem_folga(fig):
    """Eixo de categorias com anotações: o Plotly abre espaço vazio nas pontas para caber o texto das anotações.
    Fixa o eixo nos dados e ancora cada anotação para o lado de dentro, assim o gráfico ocupa a largura toda."""
    if not fig.layout.annotations:
        return
    cats = []
    for t in fig.data:
        xs = getattr(t, "x", None)
        if xs is None:
            continue
        for v in xs:
            if isinstance(v, str) and v not in cats:
                cats.append(v)
    if len(cats) < 12:
        return
    fig.update_xaxes(type="category", range=[-0.5, len(cats) - 0.5])
    for a in fig.layout.annotations:
        if isinstance(a.x, str) and a.x in cats:
            f = cats.index(a.x) / (len(cats) - 1)
            a.xanchor = "right" if f > 0.65 else ("left" if f < 0.35 else "center")


def _legenda_junto_do_titulo(fig):
    """Legenda logo abaixo do título (à esquerda) e margem de cima só do tamanho necessário: antes sobrava um vão de 40 px quando a legenda tinha muitos governos."""
    nomes = [str(t.name) for t in fig.data if getattr(t, "showlegend", None) is not False and getattr(t, "name", None)]
    if len(nomes) < 2:
        fig.update_layout(margin=dict(t=58))
        return
    largura = sum(len(n) * 7 + 46 for n in nomes)
    linhas = max(1, -(-largura // 760))
    fig.update_layout(margin=dict(t=34 + 22 * linhas + 12),
                      legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0))


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
    _eixo_sem_folga(fig)
    _legenda_junto_do_titulo(fig)
    if st.session_state.get("modo_daltonico"):
        _aplicar_daltonismo(fig)
    if eh_celular():
        _ajuste_celular(fig, title, height)
    return fig


CVD_MAP = {"#3b82f6": "#0072B2", "#ef2b2d": "#E69F00", "#60a5fa": "#56B4E9", "#f87171": "#E69F00"}


def _aplicar_daltonismo(fig):
    """Paleta segura para daltonismo (azul/laranja), padrões nas barras e traços distintos nas linhas."""
    for tr in fig.data:
        marker = getattr(tr, "marker", None)
        cor = getattr(marker, "color", None) if marker is not None else None
        if isinstance(cor, str):
            novo = CVD_MAP.get(cor.lower())
            if novo:
                tr.marker.color = novo
                if tr.type == "bar":
                    tr.marker.pattern = dict(shape="/" if novo == "#E69F00" else "", fgcolor="rgba(0,0,0,0.35)")
        elif isinstance(cor, (list, tuple)) and tr.type == "bar":
            cores = [CVD_MAP.get(str(c).lower(), c) for c in cor]
            tr.marker.color = cores
            tr.marker.pattern = dict(shape=["/" if c == "#E69F00" else "" for c in cores], fgcolor="rgba(0,0,0,0.35)")
        line = getattr(tr, "line", None)
        lcor = getattr(line, "color", None) if line is not None else None
        if isinstance(lcor, str) and lcor.lower() in CVD_MAP:
            tr.line.color = CVD_MAP[lcor.lower()]
            if lcor.lower() in ("#ef2b2d", "#f87171"):
                tr.line.dash = "dash"

def render_hero_banner():
    banner_html = (
        '<div class="hero-container">'
        '<div class="hero-title">Observatório de Governos: Brasil, de FHC a Lula 3</div>'
        '<div class="hero-subtitle">'
        'Dados e políticas de cada governo, lado a lado e sem tomar partido. Escolha os governos que quiser comparar (o padrão é Bolsonaro x Lula 3), com base principalmente em dados públicos oficiais do '
        '<b>IBGE</b>, <b>Banco Central</b>, <b>Ministério do Trabalho</b>, <b>CONAB</b> e <b>Inpe</b>, complementada por estudos de entidades, checagens e reportagens. '
        'Cada página indica os tipos de fonte usados.'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

GOV_COLORS = {"Bolsonaro": COLOR_BOLSONARO, "Lula": COLOR_LULA}

# Paleta por mandato com base no partido do presidente na época, variando o tom entre mandatos do mesmo partido:
# PSDB (FHC) azul-ciano tucano · PT (Lula e Dilma) vermelho · MDB (Temer) verde · PSL/PL (Bolsonaro) azul.
# Bolsonaro foi eleito pelo PSL, ficou sem partido de nov/2019 a nov/2021 e se filiou ao PL; o azul é a cor dos dois partidos.
PARTIDO = {"FHC 1": "PSDB", "FHC 2": "PSDB", "Lula 1": "PT", "Lula 2": "PT", "Lula 3": "PT",
           "Dilma 1": "PT", "Dilma 2": "PT", "Temer": "MDB", "Bolsonaro": "PSL/PL"}
COR_MANDATO = {
    "FHC 1": "#22D3EE", "FHC 2": "#0891B2",
    "Lula 1": "#B91C1C", "Lula 2": "#DC2626", "Lula 3": COLOR_LULA,
    "Dilma 1": "#FECACA", "Dilma 2": "#F87171",
    "Temer": "#22C55E", "Bolsonaro": COLOR_BOLSONARO,
}
COR_CLARA = {
    "FHC 1": "#A5F3FC", "FHC 2": "#67E8F9",
    "Lula 1": "#FCA5A5", "Lula 2": "#FCA5A5", "Lula 3": "#FCA5A5",
    "Dilma 1": "#FEE2E2", "Dilma 2": "#FECACA",
    "Temer": "#86EFAC", "Bolsonaro": "#93C5FD",
}
PERIODO = {"FHC 1": "1995–98", "FHC 2": "1999–2002", "Lula 1": "2003–06", "Lula 2": "2007–10", "Dilma 1": "2011–14",
           "Dilma 2": "2015–mai/16", "Temer": "mai/16–2018", "Bolsonaro": "2019–22", "Lula 3": "2023–atual"}


def classe_gov(governo):
    """Classe CSS de um mandato (gx-fhc-1, gx-lula-3...)."""
    return "gx-" + governo.lower().replace(" ", "-")


def hex_rgba(cor, alfa):
    cor = cor.lstrip("#")
    r, g, b = int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16)
    return f"rgba({r},{g},{b},{alfa})"


def css_governos():
    """Regras de cor de cada mandato para os cartões, selos e tabela da Visão Geral (mesmo visual de Bolsonaro x Lula)."""
    regras = []
    for g, cor in COR_MANDATO.items():
        c, clara = classe_gov(g), COR_CLARA[g]
        regras.append(
            f".gov-row.{c}{{background:{hex_rgba(cor, 0.14)} !important;border-left:4px solid {cor} !important;"
            f"border-top:1px solid {hex_rgba(cor, 0.2)} !important;border-bottom:1px solid {hex_rgba(cor, 0.2)} !important;"
            f"border-right:1px solid {hex_rgba(cor, 0.2)} !important;}}"
            f".gov-val.{c},.val-main.{c},.gov-name.{c},.compare-val.{c}{{color:{clara} !important;}}"
            f".mini-badge.{c}{{background:{cor} !important;color:#0b0f19 !important;}}"
            f".score-table .val-cell.win-{c}{{background:{hex_rgba(cor, 0.12)} !important;border-left-color:{cor} !important;}}"
            f".resumo-lado.{c}{{color:{clara} !important;}} .resumo-lado.{c}.vence{{background:{hex_rgba(cor, 0.13)} !important;border-color:{cor} !important;}}"
            f".resumo-lado.{c} .compare-val{{color:{clara} !important;}}"
            f".kpi-card.borda-{c},.prop-card.borda-{c}{{border-top:3px solid {cor} !important;}}"
        )
    return "<style>" + "".join(regras) + "</style>"


# Cores das faixas de veredito das checagens (verde = verdade ... vermelho = mentira)
VERDICT_COLORS = {
    "Verdade": "#10B981",
    "Meia-verdade": "#F59E0B",
    "Mentira": "#EF4444",
    "Sem comprovação": "#94A3B8",
}
VERDICT_ORDER = ["Verdade", "Meia-verdade", "Mentira", "Sem comprovação"]

def gov_color(governo):
    if governo in COR_MANDATO:
        return COR_MANDATO[governo]
    for nome, cor in GOV_COLORS.items():
        if nome in str(governo):
            return cor
    return "#64748b"

def render_section_header(title, subtitle):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)

_SERIES = re.compile(r"\b(SGS|SIDRA|tabelas?)\s+(\d{1,6}(?:(?:,\s*|\s+e\s+)\d{1,6})*)")
SGS_GENERICO = "https://www3.bcb.gov.br/sgspub/"


def _link_serie(sistema, numero):
    if sistema == "SGS":
        return f'<a href="https://api.bcb.gov.br/dados/serie/bcdata.sgs.{numero}/dados?formato=csv" target="_blank">{numero}</a>'
    return f'<a href="https://sidra.ibge.gov.br/tabela/{numero}" target="_blank">{numero}</a>'


def _linkar_series(texto):
    """Transforma 'SGS 433', 'SGS 21082, 21084 e 21145' e 'SIDRA 7060' em links para as séries exatas usadas."""
    def troca(m):
        sistema = "SGS" if m.group(1) == "SGS" else "SIDRA"
        numeros = re.sub(r"\d{1,6}", lambda n: _link_serie(sistema, n.group(0)), m.group(2))
        return f"{m.group(1)} {numeros}"

    out, dentro_de_link = [], False
    for p in re.split(r"(<[^>]+>)", texto):
        if p.startswith("<"):
            dentro_de_link = p.lower().startswith("<a ") or (dentro_de_link and not p.lower().startswith("</a"))
            out.append(p)
        else:
            out.append(p if dentro_de_link else _SERIES.sub(troca, p))
    return "".join(out)


def render_source(text, url=None):
    """Rodapé de fonte padronizado abaixo de gráficos e tabelas. Códigos de série (SGS, SIDRA) viram links diretos."""
    text = _linkar_series(text)
    if url == SGS_GENERICO:
        url = None  # os links das séries já apontam para os dados exatos
    link = f' · <a href="{html_mod.escape(url, quote=True)}" target="_blank">abrir fonte ↗</a>' if url else ""
    st.markdown(f'<div class="source-note">Fonte: {text}{link}</div>', unsafe_allow_html=True)

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

def render_kpi_card(title, val_bols, val_lula, unit="", note="", nome_a="Bolsonaro (2019-22)", nome_b="Lula (2023-atual)",
                    cls_a="bolsonaro", cls_b="lula"):
    """Cartão com os dois governos empilhados. Por padrão Bolsonaro x Lula; cls_a/cls_b trocam as cores (classes gx-...)."""
    estilo_a = ' style="color: #93c5fd;"' if cls_a == "bolsonaro" else ""
    estilo_b = ' style="color: #fca5a5;"' if cls_b == "lula" else ""
    card_html = (
        '<div class="kpi-card">'
        '<div class="kpi-title">'
        f'<span>{title}</span>'
        f'<span style="font-size: 0.75rem; color: #38bdf8; font-weight: 600;">{unit}</span>'
        '</div>'
        f'<div class="gov-row {cls_a}">'
        f'<span class="gov-name {cls_a}"{estilo_a}>{nome_a}</span>'
        f'<span class="gov-val {cls_a}">{val_bols}</span>'
        '</div>'
        f'<div class="gov-row {cls_b}">'
        f'<span class="gov-name {cls_b}"{estilo_b}>{nome_b}</span>'
        f'<span class="gov-val {cls_b}">{val_lula}</span>'
        '</div>'
        f'<div class="kpi-foot">{note}</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
