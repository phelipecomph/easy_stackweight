from skillStack.skill_stack import SkillStack
from typing import List, Union, Literal
import plotly.express as px
import pandas as pd
import json

def _load_rules():
    with open("rules.json", "r") as f:
        loaded_rules = json.load(f)

    # Reconstruir as lambdas
    for rule in loaded_rules:
        rule["regra"] = eval(rule["regra"])
    return loaded_rules

# Função para verificar as regras
def _check_rules(variables, rules):
    weights = {}
    decays = {}
    for rule_dict in rules:
        rule_name = rule_dict["habilidade"]
        rule_func = rule_dict["regra"]
        rule_weight = rule_dict["peso"]
        rule_decay = rule_dict["decaimento"]
        if not rule_name in weights:
            weights[rule_name] = 0
            decays[rule_name] = rule_decay
        try:
            if rule_func(variables):
                weights[rule_name] += rule_weight
        except TypeError:
            pass

    return weights, decays


def _mean_stack(stacks:List[dict]):
    all_keys = set().union(*(d['stack_result'].keys() for d in stacks))

    # Calcular a média considerando valores ausentes como 0
    result = {}
    for key in all_keys:
        values = [d['stack_result'].get(key, 0) for d in stacks]  # Usa 0 para valores ausentes
        #print(values)
        result[key] = sum(values) / len(stacks)
    
    return result

def simulate_stack(
    df_essays: Union[pd.DataFrame, str],
    new_rules: List[dict] = [],
    cods: List[int] = [],
    sequence_method: bool = False,
    show_n: int = 10,
    output_type: Literal["xlsx", "csv", "print", "df", "stacks", "plot", "anim"] = "stacks",
    output_path: str = "output",
) -> Union[None, dict, pd.DataFrame]:
    RULES = _load_rules()
    rules = new_rules + RULES

    # Verifica se df_essays é uma string (caminho para arquivo)
    if isinstance(df_essays, str):
        try:
            if df_essays.endswith(".csv"):
                df_essays = pd.read_csv(df_essays)
            elif df_essays.endswith(".xlsx"):
                df_essays = pd.read_excel(df_essays)
            else:
                raise ValueError("Formato de arquivo não suportado. Use .csv ou .xlsx")
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo: {e}")

    # Filtra os dados pelo código fornecido
    if cods == []:
        cods = df_essays["cod_correcao_redacao"].values
    df = df_essays[df_essays["cod_correcao_redacao"].isin(cods)]

    # Inicializa a pilha de habilidades
    stack = SkillStack()
    output_data = []
    animation_data = []
    for idx, row in enumerate(df.itertuples(index=False), start=1):  # Usar índice sequencial
        if not sequence_method:
            stack = SkillStack()

        weights, decays = _check_rules(row._asdict(), rules)
        stack.update(weights, decays)
        stack_result = stack.stack
        output_data.append(
            {
                "cod_correcao_redacao": row.cod_correcao_redacao,
                "stack_result": stack_result,
            }
        )

        # Coleta dados para animação (apenas habilidades com valores > 0)
        for skill, weight in stack_result.items():
            if weight > 0:
                animation_data.append(
                    {
                        "iteration": idx,  # Índice sequencial
                        "skill": skill,
                        "weight": weight,
                    }
                )

    # Processa a saída com base no tipo
    if output_type == "print":
        for item in output_data:
            print(f"cod({item['cod_correcao_redacao']}): {item['stack_result']}")

    elif output_type == "csv":
        df["pilha"] = output_data
        df.to_csv(f"{output_path}.csv", index=False)
        print(f"Resultados salvos em {output_path}.csv")

    elif output_type == "xlsx":
        df["pilha"] = output_data
        df.to_excel(f"{output_path}.xlsx", index=False)
        print(f"Resultados salvos em {output_path}.xlsx")

    elif output_type == "df":
        df["pilha"] = output_data
        return df
    
    elif output_type == "stacks":
        return output_data

    elif output_type == "plot":
        df_plot = pd.DataFrame(list(_mean_stack(output_data).items()), columns=["Regra", "Peso"])
        df_plot = df_plot.loc[df_plot['Peso'] > 0]
        df_plot = df_plot.sort_values(by="Peso", ascending=False)
        
        # Criar o gráfico de barras com Plotly
        fig = px.bar(df_plot, x="Regra", y="Peso", title="Pilha Média")
        return fig

    elif output_type == "anim":
        df_anim = pd.DataFrame(animation_data)
        fig = px.bar(
            df_anim,
            x="skill",
            y="weight",
            color="skill",
            animation_frame="iteration",
            title="Evolução da Pilha ao Longo do Tempo",
            labels={"iteration": "Redação", "weight": "Peso", "skill": "Habilidade"},
            range_y=[0, 20],
        )
        return fig