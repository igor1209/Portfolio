import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Dashboard Salarial",
    layout="wide"
)

st.title("📊 Dashboard Salarial — Imersão Alura")

# ===============================
# CARREGAR E TRATAR DADOS
# ===============================
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv"
    )

    # Renomear colunas
    df.rename(columns={
        'work_year': 'ano',
        'experience_level': 'senioridade',
        'employment_type': 'contrato',
        'job_title': 'cargo',
        'salary': 'salario',
        'salary_currency': 'moeda',
        'salary_in_usd': 'usd',
        'employee_residence': 'residencia',
        'remote_ratio': 'remoto',
        'company_location': 'empresa',
        'company_size': 'tamanho_empresa'
    }, inplace=True)

    # Remover anos nulos (CORREÇÃO DO ERRO)
    df = df.dropna(subset=['ano'])
    df['ano'] = df['ano'].astype(int)

    # Traduzir categorias
    df['senioridade'] = df['senioridade'].map({
        'EN': 'Entrada',
        'MI': 'Intermediário',
        'SE': 'Sênior',
        'EX': 'Executivo'
    }).fillna(df['senioridade'])

    df['contrato'] = df['contrato'].map({
        'FT': 'Tempo Integral',
        'PT': 'Tempo Parcial',
        'CT': 'Contratado',
        'FL': 'Freelancer'
    }).fillna(df['contrato'])

    df['tamanho_empresa'] = df['tamanho_empresa'].map({
        'S': 'Pequena',
        'M': 'Média',
        'L': 'Grande'
    }).fillna(df['tamanho_empresa'])

    df['remoto'] = df['remoto'].map({
        0: 'Presencial',
        50: 'Híbrido',
        100: 'Remoto'
    }).fillna(df['remoto'])

    return df

df = carregar_dados()

# ===============================
# FILTROS (SIDEBAR)
# ===============================
st.sidebar.header("🎛️ Filtros")

anos_disponiveis = sorted(df['ano'].unique())
senioridades_disponiveis = sorted(df['senioridade'].unique())
remotos_disponiveis = sorted(df['remoto'].unique())

anos = st.sidebar.multiselect(
    "Ano",
    options=anos_disponiveis,
    default=anos_disponiveis
)

senioridades = st.sidebar.multiselect(
    "Senioridade",
    options=senioridades_disponiveis,
    default=senioridades_disponiveis
)

remotos = st.sidebar.multiselect(
    "Tipo de trabalho",
    options=remotos_disponiveis,
    default=remotos_disponiveis
)

df_filtrado = df[
    (df['ano'].isin(anos)) &
    (df['senioridade'].isin(senioridades)) &
    (df['remoto'].isin(remotos))
]

# ===============================
# MÉTRICAS
# ===============================
st.subheader("📌 Visão Geral")

col1, col2, col3 = st.columns(3)

col1.metric("Total de registros", f"{df_filtrado.shape[0]:,}")
col2.metric("Salário médio (USD)", f"${df_filtrado['usd'].mean():,.0f}")
col3.metric("Maior salário (USD)", f"${df_filtrado['usd'].max():,.0f}")

# ===============================
# GRÁFICOS
# ===============================
st.subheader("📈 Análises")

col1, col2 = st.columns(2)

# Salário por senioridade
with col1:
    st.markdown("**Salário médio por senioridade**")
    fig, ax = plt.subplots()
    (
        df_filtrado.groupby('senioridade')['usd']
        .mean()
        .sort_values()
        .plot(kind='bar', ax=ax)
    )
    ax.set_ylabel("USD")
    st.pyplot(fig)

# Salário por tipo de trabalho
with col2:
    st.markdown("**Salário médio por tipo de trabalho**")
    fig, ax = plt.subplots()
    (
        df_filtrado.groupby('remoto')['usd']
        .mean()
        .sort_values()
        .plot(kind='bar', ax=ax)
    )
    ax.set_ylabel("USD")
    st.pyplot(fig)

# ===============================
# TOP 10 CARGOS
# ===============================
st.subheader("🏆 Top 10 cargos mais bem pagos")

fig, ax = plt.subplots()
(
    df_filtrado.groupby('cargo')['usd']
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .plot(kind='barh', ax=ax)
)
ax.invert_yaxis()
ax.set_xlabel("USD")
st.pyplot(fig)

# ===============================
# EVOLUÇÃO SALARIAL
# ===============================
st.subheader("📉 Evolução salarial ao longo dos anos")

fig, ax = plt.subplots()
(
    df_filtrado.groupby('ano')['usd']
    .mean()
    .plot(kind='line', marker='o', ax=ax)
)
ax.set_ylabel("USD")
st.pyplot(fig)

# ===============================
# TABELA FINAL
# ===============================
st.subheader("📄 Dados filtrados")
st.dataframe(df_filtrado)
