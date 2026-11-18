# ==============================================================================
# MODELO PARA A PROVA — PAINEL STREAMLIT COM PLOTLY EXPRESS
# ------------------------------------------------------------------------------
# COMO USAR NA PROVA:
#   1. Coloque o arquivo de dados da prova (CSV ou XLSX) na MESMA pasta deste app.py
#   2. Procure no código os blocos marcados com  >>> MUDE AQUI <<<
#   3. Troque nome do arquivo, nomes das colunas, valores do filtro, cores e títulos
#   4. Rode localmente:   streamlit run app.py
#   5. Suba no GitHub e faça o deploy (veja o arquivo DEPLOY.md)
#
# DICA DE OURO: antes de mexer em qualquer gráfico, descubra os nomes EXATOS das
# colunas e dos valores. Descomente as linhas de "DIAGNÓSTICO" lá embaixo.
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px   # A prova exige SÓ plotly.express (nada de graph_objects)


# >>> MUDE AQUI <<< Título que aparece na aba do navegador
st.set_page_config(page_title="Painel IQVU - Belo Horizonte", layout="wide")


# ==============================================================================
# 1. CONFIGURAÇÕES — QUASE TUDO QUE MUDA NA PROVA FICA AQUI EM CIMA
# ==============================================================================

# >>> MUDE AQUI <<< Nome do arquivo de dados (tem que estar na pasta do app.py)
ARQUIVO = "dados.csv"

# >>> MUDE AQUI <<< Nomes das colunas do arquivo da prova
COL_GRUPO = "NOMEUP"    # coluna que separa as categorias comparadas (aqui: o bairro)
COL_ANO = "ANO"         # coluna de tempo (eixo X dos gráficos de evolução)
COL_VALOR = "IQVU"      # coluna do índice/valor principal (eixo Y)
COL_SERIE = "SERIE"     # coluna usada no filtro extra (se a prova não tiver, veja o filtro abaixo)

# >>> MUDE AQUI <<< Os dois itens que a prova manda comparar (escreva IGUAL ao arquivo)
GRUPO_1 = "Taquaril"
GRUPO_2 = "Santa Ines"

# >>> MUDE AQUI <<< Valor do filtro extra (ex.: só "SERIE HISTORICA")
VALOR_SERIE = "SERIE HISTORICA"

# >>> MUDE AQUI <<< Cores de cada item (a prova costuma dar o código hexadecimal)
COR_1 = "#FF6B6B"
COR_2 = "#00F5D4"
CORES = {GRUPO_1: COR_1, GRUPO_2: COR_2}   # usado no color_discrete_map dos gráficos

# >>> MUDE AQUI <<< Colunas das "dimensões" usadas nos gráficos 4 (empilhado),
# 6 (radar) e 8 (dispersão).  Formato:  "nome da coluna no arquivo": "nome bonito no gráfico"
DIMENSOES = {
    "Educacao": "Educação",
    "Saude": "Saúde",
    "Habitacao": "Habitação",
    "Infraestrutura": "Infraestrutura",
    "Cultura": "Cultura",
}

# >>> MUDE AQUI <<< Colunas do eixo X e Y do gráfico de dispersão (questão 8)
DISPERSAO_X = "Educacao"
DISPERSAO_Y = "Saude"

# >>> MUDE AQUI <<< Assunto/textos usados nos títulos
ASSUNTO = "IQVU"
TITULO_PAINEL = "Painel Streamlit do IQVU de Belo Horizonte — Taquaril e Santa Inês"
FONTE = "Fonte dos dados: dados abertos da Prefeitura de Belo Horizonte — https://dados.pbh.gov.br/"


# ==============================================================================
# 2. CARREGAR OS DADOS COM PANDAS
# ==============================================================================
# Abra o arquivo no Bloco de Notas antes para ver como ele é:
#   - Separado por ";"  -> sep=";"     |  Separado por ","  -> sep=","
#   - Números como 0,412 -> decimal=","  |  Números como 0.412 -> pode apagar o decimal
#   - Se der UnicodeDecodeError (acentos quebrados) -> troque encoding para "latin-1"

# ---- OPÇÃO A: arquivo CSV (padrão) ----
df = pd.read_csv(ARQUIVO, sep=";", decimal=",", encoding="utf-8")

# ---- OPÇÃO B: arquivo EXCEL (.xlsx) ----
# Se for Excel: comente a linha do read_csv acima, descomente a de baixo
# e ADICIONE "openpyxl" no requirements.txt (senão o deploy quebra!)
# df = pd.read_excel(ARQUIVO, engine="openpyxl")

# Limpeza básica: tira espaços sobrando dos nomes das colunas e dos textos
df.columns = df.columns.str.strip()
df[COL_GRUPO] = df[COL_GRUPO].astype(str).str.strip()

# ---- DIAGNÓSTICO (descomente na prova para conferir os nomes, depois comente de novo) ----
# st.write(df.columns.tolist())          # nomes exatos das colunas
# st.write(df[COL_GRUPO].unique())       # nomes exatos dos bairros/itens
# st.write(df[COL_SERIE].unique())       # valores existentes na coluna do filtro
# st.dataframe(df.head())                # primeiras linhas


# ==============================================================================
# 3. FILTRO EXIGIDO NA PROVA
# ==============================================================================
# Mantém só os dois itens pedidos E só o valor de série pedido.
df_filtrado = df[
    (df[COL_GRUPO].isin([GRUPO_1, GRUPO_2])) &
    (df[COL_SERIE] == VALOR_SERIE)
].copy()
# Se a prova NÃO tiver filtro de série, use só a primeira condição:
# df_filtrado = df[df[COL_GRUPO].isin([GRUPO_1, GRUPO_2])].copy()

# Ordena por ano para as linhas dos gráficos não ficarem "embaralhadas"
df_filtrado = df_filtrado.sort_values(COL_ANO)

# Tabela enxuta só com as 3 colunas principais (usada na tabela e em vários gráficos)
df_tabela = df_filtrado[[COL_GRUPO, COL_ANO, COL_VALOR]]

# Ano mais recente da base (a prova pediu 2016 no simulado — aqui é calculado sozinho)
ANO_FINAL = df_filtrado[COL_ANO].max()
ANO_INICIAL = df_filtrado[COL_ANO].min()


# ==============================================================================
# 4. DATAFRAMES AUXILIARES (questões 4, 5 e 6)
# ==============================================================================
# Pega só a linha do ano final de cada item e "derrete" (melt) as colunas de dimensão
# em linhas: Bairro | Dimensao | Valor.  Isso monta sozinho o que o simulado tinha fixo.
df_ultimo_ano = df_filtrado[df_filtrado[COL_ANO] == ANO_FINAL]

dados_longo = df_ultimo_ano.melt(
    id_vars=COL_GRUPO,
    value_vars=list(DIMENSOES.keys()),
    var_name="Dimensao",
    value_name="Valor",
).rename(columns={COL_GRUPO: "Bairro"})
dados_longo["Dimensao"] = dados_longo["Dimensao"].map(DIMENSOES)

# Questão 4 — colunas Bairro, Dimensao, Valor
dados_empilhado = dados_longo[["Bairro", "Dimensao", "Valor"]]

# Questão 6 — colunas Bairro, Dimensao, Nota
dados_radar = dados_longo.rename(columns={"Valor": "Nota"})[["Bairro", "Dimensao", "Nota"]]

# Questão 5 — colunas Bairro e o valor principal no ano final
dados_pizza = df_ultimo_ano[[COL_GRUPO, COL_VALOR]].rename(columns={COL_GRUPO: "Bairro"})

# Se a prova der os valores PRONTOS (fixos), você pode montar à mão assim:
# dados_pizza = pd.DataFrame([
#     {"Bairro": "Taquaril", "IQVU": 0.568},
#     {"Bairro": "Santa Ines", "IQVU": 0.756},
# ])


# ==============================================================================
# 5. TÍTULO E BARRA LATERAL
# ==============================================================================
st.title(TITULO_PAINEL)

st.sidebar.header("Controles")
opcao = st.sidebar.radio("Selecione a visualização:", ["Tabela", "Gráficos"])


# ==============================================================================
# 6. TABELA
# ==============================================================================
if opcao == "Tabela":
    st.header(f"Tabela do {ASSUNTO} (Série Histórica)")
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)


# ==============================================================================
# 7. GRÁFICOS — um bloco por questão. Se a prova não pedir algum, apague o bloco.
# ==============================================================================
else:
    st.header(f"Gráficos do {ASSUNTO} — {GRUPO_1} e {GRUPO_2}")

    # --------------------------------------------------------------------------
    # QUESTÃO 1 — LINHA INDIVIDUAL (item 1)
    # markers=True  -> bolinhas nos pontos
    # update_xaxes(type="category") -> eixo X só com os anos que existem (sem 1997,5...)
    # --------------------------------------------------------------------------
    st.subheader(f"1. Gráfico de Linha — {GRUPO_1}")
    df_grupo_1 = df_tabela[df_tabela[COL_GRUPO] == GRUPO_1]

    fig_linha_1 = px.line(
        df_grupo_1,
        x=COL_ANO,
        y=COL_VALOR,
        markers=True,
        title=f"Evolução do {ASSUNTO} — {GRUPO_1} ({ANO_INICIAL} a {ANO_FINAL})",
        template="plotly_dark",
    )
    fig_linha_1.update_traces(line_color=COR_1, line_width=3, marker_size=8)
    fig_linha_1.update_xaxes(type="category")
    st.plotly_chart(fig_linha_1, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 2 — LINHA INDIVIDUAL (item 2) — igual à 1, só troca o item e a cor
    # --------------------------------------------------------------------------
    st.subheader(f"2. Gráfico de Linha — {GRUPO_2}")
    df_grupo_2 = df_tabela[df_tabela[COL_GRUPO] == GRUPO_2]

    fig_linha_2 = px.line(
        df_grupo_2,
        x=COL_ANO,
        y=COL_VALOR,
        markers=True,
        title=f"Evolução do {ASSUNTO} — {GRUPO_2} ({ANO_INICIAL} a {ANO_FINAL})",
        template="plotly_dark",
    )
    fig_linha_2.update_traces(line_color=COR_2, line_width=3, marker_size=8)
    fig_linha_2.update_xaxes(type="category")
    st.plotly_chart(fig_linha_2, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 3 — BARRAS AGRUPADAS (lado a lado)
    # color=...           -> uma cor por item
    # barmode="group"     -> barras lado a lado
    # color_discrete_map  -> força a cor de cada item
    # --------------------------------------------------------------------------
    st.subheader("3. Gráfico de Barras Agrupadas")
    fig_barras = px.bar(
        df_tabela,
        x=COL_ANO,
        y=COL_VALOR,
        color=COL_GRUPO,
        barmode="group",
        title=f"Comparativo Anual de {ASSUNTO} (Barras Agrupadas)",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_barras.update_xaxes(type="category")
    st.plotly_chart(fig_barras, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 4 — BARRAS EMPILHADAS
    # barmode="stack" -> uma barra por item, com as dimensões empilhadas por cor
    # --------------------------------------------------------------------------
    st.subheader(f"4. Gráfico de Barras Empilhadas (Dimensões em {ANO_FINAL})")
    fig_empilhado = px.bar(
        dados_empilhado,
        x="Bairro",
        y="Valor",
        color="Dimensao",
        barmode="stack",
        title=f"Composição do {ASSUNTO} por Dimensão — Ano {ANO_FINAL} (Barras Empilhadas)",
        template="plotly_dark",
    )
    st.plotly_chart(fig_empilhado, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 5 — PIZZA
    # names  -> fatias (categorias)   |  values -> tamanho das fatias
    # textinfo="percent+label+value" -> mostra %, nome e valor ao mesmo tempo
    # --------------------------------------------------------------------------
    st.subheader("5. Gráfico de Pizza")
    fig_pizza = px.pie(
        dados_pizza,
        names="Bairro",
        values=COL_VALOR,
        title=f"Proporção do {ASSUNTO} entre os Bairros ({ANO_FINAL})",
        color="Bairro",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_pizza.update_traces(textinfo="percent+label+value")
    st.plotly_chart(fig_pizza, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 6 — RADAR (com px.line_polar, SEM graph_objects)
    # r      -> valor (distância do centro)   |  theta -> nomes das pontas
    # line_close=True  -> fecha o polígono
    # fill="toself"    -> pinta o polígono por dentro
    # range=[0, 1]     -> eixo radial de 0 a 1 (ajuste se a escala da prova for outra)
    # --------------------------------------------------------------------------
    st.subheader("6. Gráfico de Radar")
    fig_radar = px.line_polar(
        dados_radar,
        r="Nota",
        theta="Dimensao",
        color="Bairro",
        line_close=True,
        title=f"Perfil Multidimensional (Gráfico de Radar - {ANO_FINAL})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_radar.update_traces(fill="toself")
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    st.plotly_chart(fig_radar, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 7 — ÁREA (parecido com linha, mas pinta a área embaixo)
    # --------------------------------------------------------------------------
    st.subheader("7. Gráfico de Área")
    fig_area = px.area(
        df_tabela,
        x=COL_ANO,
        y=COL_VALOR,
        color=COL_GRUPO,
        title=f"Evolução em Área do {ASSUNTO} ({ANO_INICIAL} a {ANO_FINAL})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_area.update_xaxes(type="category")
    st.plotly_chart(fig_area, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 8 — DISPERSÃO / BOLHAS
    # Usa df_filtrado (precisa das colunas de dimensão, que não estão no df_tabela)
    # size       -> tamanho da bolha proporcional à coluna
    # hover_data -> colunas extras que aparecem ao passar o mouse
    # --------------------------------------------------------------------------
    st.subheader("8. Gráfico de Dispersão (Bolhas)")
    fig_dispersao = px.scatter(
        df_filtrado,
        x=DISPERSAO_X,
        y=DISPERSAO_Y,
        color=COL_GRUPO,
        size=COL_VALOR,
        hover_data=[COL_ANO],
        title=f"Dispersão: {DIMENSOES.get(DISPERSAO_X, DISPERSAO_X)} vs "
              f"{DIMENSOES.get(DISPERSAO_Y, DISPERSAO_Y)} (Tamanho = {ASSUNTO})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    st.plotly_chart(fig_dispersao, use_container_width=True)

    # --------------------------------------------------------------------------
    # QUESTÃO 9 — BOXPLOT (mediana, quartis, mínimo e máximo)
    # points="all" -> mostra todos os pontos em cima das caixas
    # --------------------------------------------------------------------------
    st.subheader("9. Gráfico Boxplot")
    fig_box = px.box(
        df_tabela,
        x=COL_GRUPO,
        y=COL_VALOR,
        color=COL_GRUPO,
        points="all",
        title=f"Distribuição Estatística do {ASSUNTO} (Boxplot)",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    st.plotly_chart(fig_box, use_container_width=True)


# ==============================================================================
# 8. FONTE DOS DADOS (obrigatória no painel)
# ==============================================================================
st.markdown("---")
st.caption(FONTE)
