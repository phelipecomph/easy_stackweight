import streamlit as st
import pandas as pd
import math
import json

from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

RULES_FILE = "rules.json"

def write_rule(filters, rule_name, rule_weight, df):
    # Gerar a regra em formato de string
    rule_parts = []

    for col in filters:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Obtém os limites do filtro
            min_val, max_val = filters[col]

            # Obtém os limites da variável no DataFrame
            col_min, col_max = df[col].min(), df[col].max()

            # Constrói as condições com base nos limites
            conditions = []
            if min_val > col_min:  # Inclui condição >= apenas se min_val não for o valor mínimo
                conditions.append(f"(vars.get('{col}') >= {min_val})")
            if max_val < col_max:  # Inclui condição <= apenas se max_val não for o valor máximo
                conditions.append(f"(vars.get('{col}') <= {max_val})")

            # Adiciona a condição da coluna à regra final
            if conditions:
                rule_parts.append(" & ".join(conditions))
        else:
            # Condição para colunas não numéricas
            rule_parts.append(f"vars.get('{col}') in {filters[col]}")

    # Gerar a regra completa
    rule_string = " & ".join(rule_parts)

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

def apply_filters(df, filters):
    # Filtrar DataFrame
    filtered_df = df.copy()
    for col, criteria in filters.items():
        if pd.api.types.is_numeric_dtype(df[col]):
            if isinstance(criteria, tuple):
                filtered_df = filtered_df[
                    (filtered_df[col] >= criteria[0]) & (filtered_df[col] <= criteria[1])
                ]
            else:
                filtered_df = filtered_df[filtered_df[col].isin(criteria)]
        else:
            filtered_df = filtered_df[filtered_df[col].isin(criteria)]
    return filtered_df

def toggle_button(col):
    # Exibe o botão redondo para alternar o tipo de filtro
    filter_type = st.session_state[f"filter_type_{col}"]

    toggle_button = st.sidebar.button(
        "",
        icon=":material/change_circle:",
        key=f"toggle_{col}",  # Garante chave única por coluna
        help=f"Clique para alternar o tipo de filtro para {col}",
        use_container_width=False
    )

    if toggle_button:
        # Alternar o tipo de filtro no session_state
        new_filter_type = "Valores Específicos" if filter_type == "Intervalo Numérico" else "Intervalo Numérico"
        st.session_state[f"filter_type_{col}"] = new_filter_type

    return filter_type

def filter_element(filter_type, df, col, filters):
    # Definir o filtro baseado no tipo de filtro selecionado
    if pd.api.types.is_numeric_dtype(df[col]):
        if filter_type == "Intervalo Numérico":
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
            # Caso o filtro seja para valores específicos, mostrar um multiselect
            unique_values = df[col].unique()
            selected_values = st.sidebar.multiselect(
                f"Filtro para {col}",
                options=unique_values,
                default=[]  # Começa vazio
            )
            # Filtro vazio considera todos os valores
            filters[col] = selected_values if selected_values else unique_values
    else:
        if filter_type == "Intervalo Numérico":
            # Para colunas não numéricas, desabilitar o intervalo e usar multiselect
            unique_values = df[col].unique()
            selected_values = st.sidebar.multiselect(
                f"Filtro para {col}",
                options=unique_values,
                default=[]  # Começa vazio
            )
            filters[col] = selected_values if selected_values else unique_values
        else:
            unique_values = df[col].unique()
            selected_values = st.sidebar.multiselect(
                f"Filtro para {col}",
                options=unique_values,
                default=[]  # Começa vazio
            )
            filters[col] = selected_values if selected_values else unique_values

def new_rule_container(selected_columns, filters, df):
    # Adicionar nova regra
    st.write("### Adicionar Filtros como nova Regra")
    rule_name = st.text_input("Nome da Regra")
    rule_weight = st.number_input("Peso da Regra", min_value=0, step=1)
    add_rule_button = st.button("Adicionar Regra")

    if add_rule_button:
        if not rule_name or not selected_columns:
            st.error("Por favor, preencha o nome da regra e selecione pelo menos uma coluna.")
        else:
            write_rule(filters, rule_name, rule_weight, df)
            st.success("Regra adicionada com sucesso!")

def result_container(filtered_df, df):
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


# Função da tela de filtros
def screen_newRules():
    st.title("Filtro de DataFrame Interativo")
    st.write("Este aplicativo permite filtrar um DataFrame com base em colunas selecionadas e exibe a contagem de linhas correspondentes.")

    # Input para alterar o número de amostras no DataFrame
    st.sidebar.header("Configuração de Amostras")
    sample_size = st.sidebar.number_input(
        "Número de amostras a carregar:",
        min_value=1,  # Valor mínimo de amostras
        value=10000,  # Valor padrão
        step=100  # Passo para ajuste
    )

    # Carregar DataFrame
    df = load_data(method='csv', path='data/conteudo_adaptativoc2_dados_selecionados.csv')
    try: df.sample(sample_size)
    except ValueError: pass

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
        # Se o tipo de filtro não estiver no session_state, inicializa como "Intervalo Numérico"
        if f"filter_type_{col}" not in st.session_state:
            st.session_state[f"filter_type_{col}"] = "Intervalo Numérico"

        filter_type = toggle_button(col)
        filter_element(filter_type, df, col, filters)


    filtered_df = apply_filters(df, filters)
    
    result_container(filtered_df, df)
    new_rule_container(selected_columns, filters, df)

if __name__ == '__main__':
    screen_newRules()
