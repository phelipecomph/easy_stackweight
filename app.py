import streamlit as st
from pages import new_rule, edit_rules

# Configuração geral do app
st.set_page_config(page_title="Main", layout="wide")

st.title("Tela Inicial")
st.write("Selecione a Tela que deseja no menu lateral")
