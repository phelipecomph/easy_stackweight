import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

from components.new_rule_component import new_rule_component
from components.filter_componet import filter_component, apply_filters, toggle_button

def count_top_skills(df):
    # Supondo que stack_result tenha sido obtido corretamente de simulate_stack
    stack_result = simulate_stack(df, sequence_method=True, output_type="stacks")

    # Verificar se stack_result é uma lista válida e não vazia
    if not isinstance(stack_result, list) or not stack_result:
        st.error("Erro: stack_result não é uma lista válida.")
        return {}

    # Inicializar o contador para as habilidades que aparecem como top 1
    top_skills_counter = Counter()

    # Iterar sobre todas as redações
    for item in stack_result:
        # Verificar se o item contém a chave "stack_result" e se ela é um dicionário
        if isinstance(item.get("stack_result"), dict):
            # Obter o dicionário de habilidades
            skills_dict = item["stack_result"]

            # Ordenar as habilidades pelo peso (valor) de forma decrescente
            sorted_stack = sorted(skills_dict.items(), key=lambda x: x[1], reverse=True)

            # Pegar a habilidade top 1 (a com maior peso)
            top_skill = sorted_stack[0][0]  # nome da habilidade

            # Atualizar o contador para essa habilidade
            top_skills_counter[top_skill] += 1

    # Retornar o contador de habilidades que apareceram como top 1
    return top_skills_counter
    
def plot_top_skills(top_skills):
    """
    Cria um gráfico de barras para visualizar as habilidades que ficaram em top 1.
    """
    # Converte o dicionário para um DataFrame
    skills_df = pd.DataFrame(
        list(top_skills.items()), 
        columns=["Habilidade", "Frequência"]
    ).sort_values(by="Frequência", ascending=False)

    # Cria o gráfico
    fig = px.bar(
        skills_df, 
        x="Habilidade", 
        y="Frequência", 
        title="Frequência de Habilidades no Top 1 das Pilhas",
        labels={"Habilidade": "Habilidade", "Frequência": "Frequência"},
    )
    return fig

def result_container(filtered_df, df):
    # Mostrar resultados gerais
    st.write("### Linhas Correspondentes")
    num_filtered = len(filtered_df)
    num_original = len(df)
    percentage = (num_filtered / num_original) * 100
    st.write(f"**Número de linhas:** {num_filtered} ({percentage:.2f}%)")

    st.write("### Dados Filtrados")
    st.dataframe(filtered_df.head(1000))


def page_commonSkills():
    st.title("Análise de Habilidades no Top 1")
    st.write("Esta página apresenta uma análise sobre quantas vezes cada habilidade ficou no top 1 das pilhas do DataFrame filtrado.")

    # Input para alterar o número de amostras no DataFrame
    st.sidebar.header("Configuração de Amostras")
    sample_size = st.sidebar.number_input(
        "Número de amostras a carregar:",
        min_value=1, 
        value=10000, 
        step=100
    )

    # Carregar DataFrame
    df = load_data(method='csv', path='data/conteudo_adaptativoc2_dados_selecionados.csv')
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
        # Se o tipo de filtro não estiver no session_state, inicializa como "Intervalo Numérico"
        if f"filter_type_{col}" not in st.session_state:
            st.session_state[f"filter_type_{col}"] = "Intervalo Numérico"

        filter_type = toggle_button(col)
        filter_component(filter_type, df, col, filters)


    filtered_df = apply_filters(df, filters)

    result_container(filtered_df, df)
    new_rule_component(filters, df)

if __name__ == '__main__':
    page_commonSkills()
