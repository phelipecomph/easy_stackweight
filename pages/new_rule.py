import streamlit as st
import pandas as pd
import numpy as np


# Exemplo de DataFrame
def _create_example_dataframe():
    np.random.seed(42)
    data = {
        'Categoria': np.random.choice(['A', 'B', 'C'], size=100),
        'Valor Inteiro': np.random.randint(1, 100, size=100),
        'Valor Float': np.random.uniform(0, 1, size=100).round(2),
        'Texto': np.random.choice(['X', 'Y', 'Z'], size=100),
    }
    return pd.DataFrame(data)

# Função da tela de filtros
def screen_newRules():
    st.title("Filtro de DataFrame Interativo")
    st.write("Este aplicativo permite filtrar um DataFrame com base em colunas selecionadas e exibe a contagem de linhas correspondentes.")

    # Carregar DataFrame
    df = _create_example_dataframe()

    # Seleção de colunas a filtrar
    st.sidebar.header("Configuração de Filtros")
    selected_columns = st.sidebar.multiselect(
        "Selecione as colunas para adicionar filtros:",
        options=df.columns,
        default=df.columns
    )

    # Criar filtros dinâmicos
    st.sidebar.header("Filtros por Coluna")
    filters = {}
    for col in selected_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_value = float(df[col].min())
            max_value = float(df[col].max())
            range_selected = st.sidebar.slider(
                f"Filtro de intervalo para {col}",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value)
            )
            filters[col] = range_selected
        else:
            unique_values = df[col].unique()
            selected_values = st.sidebar.multiselect(
                f"Filtro para {col}",
                options=unique_values,
                default=unique_values
            )
            filters[col] = selected_values

    # Filtrar DataFrame
    filtered_df = df.copy()
    for col, criteria in filters.items():
        if pd.api.types.is_numeric_dtype(df[col]):
            filtered_df = filtered_df[
                (filtered_df[col] >= criteria[0]) & (filtered_df[col] <= criteria[1])
            ]
        else:
            filtered_df = filtered_df[filtered_df[col].isin(criteria)]

    # Mostrar resultados
    st.write("### Linhas Correspondentes")
    num_filtered = len(filtered_df)
    num_original = len(df)
    percentage = (num_filtered / num_original) * 100
    st.write(f"**Número de linhas:** {num_filtered} ({percentage:.2f}%)")

    st.write("### Dados Filtrados")
    st.dataframe(filtered_df)


screen_newRules()