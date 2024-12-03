import streamlit as st
import pandas as pd
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

# Novo contêiner para exibir os resultados das sequências
def sequence_result_container(df, filters):
    st.write("### Resultados por Sequência")
    sequences = df.groupby("cod_usuario")
    for user_id, group in sequences:
        # Ordenar pelo dat_envio
        group_sorted = group.sort_values(by="dat_envio")
        
        # Passar cada sequência para simulate_stack
        fig = simulate_stack(df, sequence_method=True, output_type="anim")
        
        st.write(f"**Usuário:** {user_id}")
        st.plotly_chart(fig, use_container_width=True)

# Contêiner de resultados (atualizado)
def result_container(filtered_df, df):
    # Mostrar resultados gerais
    st.write("### Linhas Correspondentes")
    num_filtered = len(filtered_df)
    num_original = len(df)
    percentage = (num_filtered / num_original) * 100
    st.write(f"**Número de linhas:** {num_filtered} ({percentage:.2f}%)")

    st.write("### Dados Filtrados")
    st.dataframe(filtered_df.head(1000))

    # Mostrar resultados por sequência
    sequence_result_container(filtered_df, df)

# Função da tela (atualizada)
def page_sequenceEssays():
    st.title("Filtro de Sequências de Redações")
    st.write("Este aplicativo permite filtrar um DataFrame e processar sequências de redações por usuário.")

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
    user_counts = df.groupby('cod_usuario')['cod_usuario'].transform('count')
    df = df[user_counts >= 3]

    try:
        df = df.sample(sample_size)
    except ValueError:
        st.warning("Número de amostras excede o tamanho do dataset.")

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
        # Inicializar tipo de filtro
        if f"filter_type_{col}" not in st.session_state:
            st.session_state[f"filter_type_{col}"] = "Intervalo Numérico"

        # Tipo de filtro e elemento de filtro
        filter_type = st.sidebar.radio(f"Tipo de Filtro: {col}", ["Intervalo Numérico", "Valores Específicos"], key=f"filter_type_{col}")
        if filter_type == "Intervalo Numérico":
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            filters[col] = st.sidebar.slider(f"Intervalo: {col}", min_value=min_val, max_value=max_val, value=(min_val, max_val))
        else:
            unique_values = df[col].unique()
            filters[col] = st.sidebar.multiselect(f"Valores: {col}", options=unique_values, default=unique_values)

    # Aplicar filtros ao DataFrame
    filtered_df = apply_filters(df, filters)

    # Mostrar resultados
    result_container(filtered_df, df)

    # Adicionar nova regra
    st.sidebar.header("Adicionar Nova Regra")
    rule_name = st.sidebar.text_input("Nome da Regra")
    rule_weight = st.sidebar.number_input("Peso da Regra", min_value=0, step=1)
    if st.sidebar.button("Adicionar Regra"):
        if not rule_name:
            st.error("Por favor, forneça um nome para a regra.")
        else:
            write_rule(filters, rule_name, rule_weight, df)
            st.success("Regra adicionada com sucesso!")

if __name__ == '__main__':
    page_sequenceEssays()

