from skill_stack import SkillStack
from typing import List, Union, Literal
import pandas as pd


RULES = [
    #{"habilidade": "nome da habilidade", "regra": função Lambda, "peso": valor do peso},
    {"habilidade": "habilidade_teste",'regra': lambda vars: (vars.get('trecho_outro_genero_9') == 0),'peso': 10},
    {"habilidade": "outra_habilidade_teste",'regra': lambda vars: (vars.get('trecho_outro_genero_9') == 0) & (vars.get('num_pontuacao_eixo_2')>=120),'peso': 5},
]

# Função para verificar as regras
def _check_rules(variables, rules):
    results = {}
    for rule_dict in rules:
        rule_name = rule_dict["habilidade"]
        rule_func = rule_dict["regra"]
        rule_weight = rule_dict["peso"]
        if not rule_name in results:
            results[rule_name] = 0

        if rule_func(variables):
            results[rule_name] += rule_weight
    return results


def _mean_stack(stacks:List[dict]):
    all_keys = set().union(*(d.keys() for d in stacks))

    # Calcular a média considerando valores ausentes como 0
    result = {}
    for key in all_keys:
        values = [d.get(key, 0) for d in stacks]  # Usa 0 para valores ausentes
        result[key] = sum(values) / len(stacks)
    
    return result

def simulate_stack(
    df_essays: Union[pd.DataFrame, str],
    new_rules: List[dict],
    cods: List[int] = [],
    sequence_method: bool = False,
    show_n: int = 10,
    output_type: Literal["xlsx", "csv", "print", "df", "stacks", "plot"] = "stacks",
    output_path: str = "output",
) -> Union[None, dict, pd.DataFrame]:
    rules = new_rules | RULES

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
    for _, row in df.iterrows():
        if not sequence_method:
            stack = SkillStack()

        weights = _check_rules(dict(row), rules)
        stack.update(weights)
        result = [
            f"{str(key).rjust(2,'0')}: {str(stack.stack[key]).ljust(5,'0')}"
            for key in stack.greater(show_n)
        ]
        output_data.append(
            {
                "cod_correcao_redacao": row["cod_correcao_redacao"],
                "stack_result": result,
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
        stack = _mean_stack(output_data)
        return stack