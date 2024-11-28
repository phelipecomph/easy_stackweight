import streamlit as st
import json
import os

RULES_FILE = "rules.json"

def load_rules():
    """Carrega as regras do arquivo JSON."""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return []

def save_rules(rules):
    """Salva as regras no arquivo JSON."""
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

def screen_editRules():
    st.title("Editor de Regras")
    st.write("Visualize, edite, crie ou delete regras diretamente no JSON.")

    if 'rerun' in st.session_state and st.session_state.rerun:
        st.session_state.rule_name = ''
        st.session_state.rule_text = ''
        st.session_state.rule_weight = 0
        st.session_state.rerun = False

    # Carregar regras do arquivo
    rules = load_rules()

    if not rules:
        st.warning("Nenhuma regra encontrada! Você pode criar uma nova regra abaixo.")

    # Editar e deletar regras existentes
    for i, rule in enumerate(rules):
        st.write(f"### Regra {i + 1}")
        
        # Campos editáveis
        habilidade = st.text_input(f"Nome da Habilidade (Regra {i + 1})", rule["habilidade"], key=f"habilidade_{i}")
        regra = st.text_area(f"String da Regra (Regra {i + 1})", rule["regra"], key=f"regra_{i}")
        peso = st.number_input(f"Peso (Regra {i + 1})", value=rule["peso"], min_value=0, step=1, key=f"peso_{i}")

        # Atualizar regra com novos valores
        rule["habilidade"] = habilidade
        rule["regra"] = regra
        rule["peso"] = peso

        # Botão para deletar a regra
        if st.button(f"Deletar Regra {i + 1}"):
            rules.pop(i)
            save_rules(rules)
            st.success(f"Regra {i + 1} deletada com sucesso!")
            st.rerun()  # Recarregar a página

    # Salvar todas as alterações
    if st.button("Salvar Alterações"):
        save_rules(rules)
        st.success("Regras salvas com sucesso!")

    st.write("---")
    st.write("### Criar Nova Regra")

    # Criar uma nova regra
    new_habilidade = st.text_input("Nome da Nova Habilidade", key="rule_name")
    new_regra = st.text_area("String da Nova Regra", key="rule_text")
    new_peso = st.number_input("Peso da Nova Regra", min_value=0, step=1, key="rule_weight")

    if st.button("Adicionar Nova Regra"):
        if not new_habilidade or not new_regra:
            st.error("Por favor, preencha todos os campos para criar uma nova regra.")
        else:
            new_rule = {
                "habilidade": new_habilidade,
                "regra": new_regra,
                "peso": int(new_peso)
            }
            rules.append(new_rule)
            save_rules(rules)
            st.success("Nova regra adicionada com sucesso!")

            del st.session_state.rule_name
            del st.session_state.rule_text
            del st.session_state.rule_weight
            st.session_state.rerun = True
            st.rerun()  # Recarregar a página

if __name__ == "__main__":
    screen_editRules()
