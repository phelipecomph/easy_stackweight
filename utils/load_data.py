import numpy as np
import pandas as pd

def load_data(method='random', **kwargs):
    if method == 'random':
        return _create_example_dataframe()
    elif method == 'csv':
        return _load_from_csv(**kwargs)
    else:
        raise ValueError("Método inválido. Escolha 'random' ou 'csv'.")

# Exemplo de DataFrame
def _create_example_dataframe():
    np.random.seed(42)
    data = {
        'Categoria': np.random.choice(['A', 'B', 'C'], size=100),
        'Valor Inteiro': np.random.randint(1, 100, size=100),
        'Valor Float': np.random.uniform(0, 1, size=100).round(2),
        'Texto': np.random.choice(['X', 'Y', 'Z'], size=100),
    }
    return pd.DataFrame(data)

def _load_from_csv(path: str):
    return pd.read_csv(path)
