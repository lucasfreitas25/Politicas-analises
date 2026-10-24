import streamlit as st
from modules.data_loader import get_auditoria_data
from modules.ui_components import render_section_header


def render_tab_audit():
    render_section_header(
        "Auditoria dos Dados (Pente-fino de 20/10/2026)",
        "Todos os números que estavam errados, desatualizados ou sem fonte na versão anterior do painel, o valor corrigido e de onde ele veio.",
    )

    df = get_auditoria_data()
    if df.empty:
        st.info("Nenhum registro de auditoria encontrado.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Correções registradas", len(df))
    c2.metric("Áreas revisadas", df["area"].nunique())
    c3.metric("Séries agora lidas direto das APIs", "Selic, câmbio, dívida, PIB, IPCA, Gini")

    st.markdown(
        '<div class="info-box"><b>Método:</b> cada indicador foi confrontado com a série oficial — APIs do Banco Central (SGS) e do IBGE (SIDRA) '
        'quando disponíveis, e publicações primárias (MTE/CAGED, MDIC, CONAB, FBSP, Inpe, CNC) nos demais casos. '
        'Projeções que apareciam como dado realizado foram removidas ou marcadas como parciais. '
        'Os scripts que geram as bases curadas ficam em <code>data/_fontes/</code>.</div>',
        unsafe_allow_html=True,
    )

    areas = ["Todas"] + sorted(df["area"].unique())
    area = st.segmented_control("Área", areas, default="Todas", key="aud_area")
    if area and area != "Todas":
        df = df[df["area"] == area]

    st.dataframe(
        df, width="stretch", hide_index=True, height=min(80 + 36 * len(df), 900),
        column_config={
            "area": "Área", "item": st.column_config.TextColumn("Indicador", width="medium"),
            "antes": st.column_config.TextColumn("Antes (incorreto)", width="medium"),
            "depois": st.column_config.TextColumn("Depois (corrigido)", width="medium"),
            "fonte": "Fonte oficial", "observacao": st.column_config.TextColumn("Observação", width="large"),
        },
    )

    st.markdown(
        '<div class="info-box"><b>Ainda não auditado</b> (sem série oficial acessível nesta revisão — use com cautela): '
        'valores anuais da cesta DIEESE, razão salarial por gênero/raça, IDEB, orçamento do MEC, dados Serasa, registros de CACs '
        'e apreensões de drogas, e o detalhamento por cultura da safra 2025/26.</div>',
        unsafe_allow_html=True,
    )
