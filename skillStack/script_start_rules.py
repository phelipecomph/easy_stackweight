import json

RULES = [
    {"habilidade": "habilidade_teste", "regra": "lambda vars: (vars.get('trecho_outro_genero_9') == 0)", "peso": 10},
    {"habilidade": "outra_habilidade_teste", "regra": "lambda vars: (vars.get('trecho_outro_genero_9') == 0) & (vars.get('num_pontuacao_eixo_2')>=120)", "peso": 5},
]

with open("rules.json", "w") as f:
    json.dump(RULES, f)