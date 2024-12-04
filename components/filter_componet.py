import streamlit as st
import pandas as pd
import math

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

def filter_component(filter_type, df, col, filters):
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