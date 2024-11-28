import streamlit as st
import pandas as pd
import numpy as np
import math
from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

# Função da tela de filtros
def screen_newRules():
    st.title("Filtro de DataFrame Interativo")
    st.write("Este aplicativo permite filtrar um DataFrame com base em colunas selecionadas e exibe a contagem de linhas correspondentes.")

    # Carregar DataFrame
    df = load_data(method='csv', path='data/conteudo_adaptativoc2_dados_selecionados.csv')

    # Seleção de colunas a filtrar
    st.sidebar.header("Configuração de Filtros")
    selected_columns = st.sidebar.multiselect(
        "Selecione as colunas para adicionar filtros:",
        options=df.columns,
        default=[]
    )

    # Criar filtros dinâmicos
    st.sidebar.header("Filtros por Coluna")
    filters = {}
    for col in selected_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if pd.api.types.is_integer_dtype(df[col]):
                # int 
                min_value = int(df[col].min())
                max_value = math.ceil(df[col].max(),)
                step = 1 
            else: 
                # float
                min_value = float(df[col].min())
                max_value = float(df[col].max())
                step = 0.01
            range_selected = st.sidebar.slider(
                f"Filtro de intervalo para {col}",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value),
                step=step
            )
            filters[col] = range_selected
        else:
            unique_values = df[col].unique()
            selected_values = st.sidebar.multiselect(
                f"Filtro para {col}",
                options=unique_values,
                default=[]  # Começa vazio
            )
            # Filtro vazio considera todos os valores
            filters[col] = selected_values if selected_values else unique_values

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
    st.dataframe(filtered_df.head(1000))

    processed_result = simulate_stack(filtered_df, output_type="plot")
    st.write(processed_result)

if __name__ == '__main__':
    screen_newRules()
