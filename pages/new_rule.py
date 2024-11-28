import streamlit as st
import pandas as pd
import math
import json

from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

RULES_FILE = "rules.json"

def write_rule(filters, rule_name, rule_weight, df):
    # Gerar a regra em formato de string
    rule_string = " & ".join([
        f"(vars.get('{col}') >= {filters[col][0]}) & (vars.get('{col}') <= {filters[col][1]})"
        if pd.api.types.is_numeric_dtype(df[col]) else
        f"vars.get('{col}') in {filters[col]}"
        for col in filters
    ])

    # Criar o dicionário da nova regra
    new_rule = {
        "habilidade": rule_name,
        "regra": f"lambda vars: {rule_string}",
        "peso": int(rule_weight)
    }

    # Salvar a regra no arquivo JSON
    try:
        with open(RULES_FILE, "r") as f:
            rules = json.load(f)
    except FileNotFoundError:
        rules = []

    rules.append(new_rule)

    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)


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
                max_value = math.ceil(df[col].max())
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

    # Simulação e gráfico
    fig = simulate_stack(filtered_df, output_type="plot")
    st.plotly_chart(fig)

    # Adicionar nova regra
    st.write("### Adicionar Filtos como nova Regra")
    rule_name = st.text_input("Nome da Regra")
    rule_weight = st.number_input("Peso da Regra", min_value=0, step=1)
    add_rule_button = st.button("Adicionar Regra")

    if add_rule_button:
        if not rule_name or not selected_columns:
            st.error("Por favor, preencha o nome da regra e selecione pelo menos uma coluna.")
        else:
            write_rule(filters, rule_name, rule_weight, df)
            st.success("Regra adicionada com sucesso!")

if __name__ == '__main__':
    screen_newRules()
