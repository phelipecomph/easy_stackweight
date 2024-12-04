import streamlit as st
import pandas as pd
import json

RULES_FILE = "rules.json"

def write_rule(filters, rule_name, rule_weight, rule_decay_rate, df):
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
        "peso": int(rule_weight),
        "decaimento": float(rule_decay_rate)
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

def new_rule_component(filters, df):
    # Adicionar nova regra
    st.sidebar.header("Adicionar Nova Regra")
    rule_name = st.sidebar.text_input("Nome da Regra")
    rule_weight = st.sidebar.number_input("Peso da Regra", min_value=0, step=1)
    rule_decay_rate = st.sidebar.number_input("Decaimento do Peso", min_value=0.0, max_value=1.0, step=0.1)
    if st.sidebar.button("Adicionar Regra"):
        if not rule_name:
            st.error("Por favor, forneça um nome para a regra.")
        else:
            write_rule(filters, rule_name, rule_weight, rule_decay_rate, df)
            st.success("Regra adicionada com sucesso!")