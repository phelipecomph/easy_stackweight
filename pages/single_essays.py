import streamlit as st

from components.filter_componet import filter_component, apply_filters, toggle_button
from components.new_rule_component import new_rule_component

from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

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
def page_singleEssays():
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
    page_singleEssays()
