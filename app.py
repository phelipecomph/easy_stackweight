import streamlit as st
from pages import edit_rules, single_essays, sequence_essays

# Configuração geral do app
st.set_page_config(page_title="Main", layout="wide")

st.title("Tela Inicial")
st.write("Selecione a Tela que deseja no menu lateral")
