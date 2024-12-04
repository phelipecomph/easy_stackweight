import streamlit as st

from utils.load_data import load_data
from skillStack.simulate_skillstack import simulate_stack

from components.new_rule_component import new_rule_component
from components.filter_componet import filter_component, apply_filters, toggle_button

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
        # Se o tipo de filtro não estiver no session_state, inicializa como "Intervalo Numérico"
        if f"filter_type_{col}" not in st.session_state:
            st.session_state[f"filter_type_{col}"] = "Intervalo Numérico"

        filter_type = toggle_button(col)
        filter_component(filter_type, df, col, filters)

    # Aplicar filtros ao DataFrame
    filtered_df = apply_filters(df, filters)

    # Mostrar resultados
    result_container(filtered_df, df)
    new_rule_component(filters, df)

if __name__ == '__main__':
    page_sequenceEssays()

