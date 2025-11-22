# analise_resultados.py
"""
Script para gerar estatísticas descritivas e testes inferenciais
a partir do arquivo 'resultados_amostras.csv' (formato: TSV ou CSV com separador tab ou vírgula).
Saídas:
- estatisticas_amostra_completa.csv  -> estatísticas por coluna (lista e dicionário)
- estatisticas_blocos.csv            -> (opcional) estatísticas por blocos se desejar
- resultados_console.txt             -> resumo legível com testes e números prontos para colar no relatório
"""

import os
import sys
import math
import csv
from collections import OrderedDict
import statistics as stats

# Tenta usar pandas e scipy se disponíveis (recomendado). Se não, usa modo fallback.
try:
    import pandas as pd
    import numpy as np
    from scipy import stats as sps
    SCIPY = True
except Exception:
    SCIPY = False

INPUT = 'resultados_amostras.csv'  # ajuste se necessário
SEP_TRY = [',', '\t', ';']

def read_table(path):
    # tenta inferir separador simples
    for sep in SEP_TRY:
        try:
            if SCIPY:
                df = pd.read_csv(path, sep=sep)
            else:
                # fallback com csv.reader
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=sep)
                    header = next(reader)
                    rows = list(reader)
                import numpy as np
                df = pd.DataFrame(rows, columns=header)
            # verifica se as colunas esperadas existem
            cols = [c.strip().lower() for c in df.columns]
            if any('lista' in c for c in cols) and any('dict' in c or 'dicion' in c for c in cols):
                return df
        except Exception:
            continue
    raise RuntimeError("Não foi possível ler o arquivo. Verifique separador e formatação (esperado: colunas 'tempo_lista_ns' e 'tempo_dict_ns').")

def ensure_numeric(series):
    # converte colunas para numéricas (inteiros)
    return pd.to_numeric(series, errors='coerce')

def descriptive_stats(arr):
    """Retorna dicionário com estatísticas. arr deve ser numpy array ou lista numérica."""
    n = int(len(arr))
    mean = float(np.mean(arr))
    median = float(np.median(arr))
    std_pop = float(np.std(arr, ddof=0))
    std_sample = float(np.std(arr, ddof=1))
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    mn = float(np.min(arr))
    mx = float(np.max(arr))
    return OrderedDict([
        ('n', n),
        ('mean', mean),
        ('median', median),
        ('std_pop', std_pop),
        ('std_sample', std_sample),
        ('q1', q1),
        ('q3', q3),
        ('min', mn),
        ('max', mx)
    ])

def welch_ttest(x, y):
    """Calcula t, df e p-values (two-tailed e one-tailed).
    Usa scipy se disponível; caso contrário calcula manualmente."""
    n1 = len(x); n2 = len(y)
    m1 = np.mean(x); m2 = np.mean(y)
    s1 = np.var(x, ddof=1); s2 = np.var(y, ddof=1)  # variâncias amostrais
    t = (m1 - m2) / math.sqrt(s1/n1 + s2/n2)
    # df de Welch:
    df = (s1/n1 + s2/n2)**2 / ((s1**2)/((n1**2)*(n1-1)) + (s2**2)/((n2**2)*(n2-1)))
    if SCIPY:
        # p two-tailed
        p_two = 2 * sps.t.sf(abs(t), df)
    else:
        # fallback: aproximação via t-distribution usando scipy não disponível -> usar math, mas sem p precisa
        p_two = None
    return {'t': float(t), 'df': float(df), 'p_two': p_two, 'p_left': None, 'p_right': None}

def main():
    if not os.path.exists(INPUT):
        print("Arquivo de entrada não encontrado:", INPUT)
        sys.exit(1)
    df = read_table(INPUT)
    # Normaliza nomes de colunas
    cols = {c.lower(): c for c in df.columns}
    # detecta colunas de interesse
    candidates = {k:v for k,v in cols.items()}
    # nomes esperados possíveis:
    col_lista = None
    col_dict = None
    for k in cols:
        if 'lista' in k or 'lista' in k.lower() or 'lista' in k:
            col_lista = cols[k]
        if 'dict' in k or 'dicion' in k:
            col_dict = cols[k]
        if 'tempo_lista' in k:
            col_lista = cols[k]
        if 'tempo_dict' in k or 'tempo_dict_ns' in k:
            col_dict = cols[k]
    if col_lista is None or col_dict is None:
        # tenta heurística por posição
        allcols = list(df.columns)
        if len(allcols) >= 3:
            col_lista = allcols[1]
            col_dict = allcols[2]
        else:
            raise RuntimeError("Não encontrei colunas esperadas. Colunas detectadas: {}".format(list(df.columns)))
    # converte para numérico
    df[col_lista] = ensure_numeric(df[col_lista])
    df[col_dict] = ensure_numeric(df[col_dict])
    # descartar NaN
    df = df.dropna(subset=[col_lista, col_dict])
    x = df[col_lista].astype(float).to_numpy()
    y = df[col_dict].astype(float).to_numpy()
    # estatísticas
    stats_lista = descriptive_stats(x)
    stats_dict = descriptive_stats(y)
    # teste de Welch (usando scipy se disponível)
    res_welch = welch_ttest(x, y)
    # se scipy disponível, calcula p unilateral também
    if SCIPY and res_welch['p_two'] is not None:
        p_two = res_welch['p_two']
        # p left: prob(mean_lista < mean_dict)
        # t negative implies mean(lista) < mean(dict)
        # compute cdf
        t = res_welch['t']; dfw = res_welch['df']
        p_left = sps.t.cdf(t, dfw)
        p_right = 1 - p_left
        res_welch['p_two'] = p_two
        res_welch['p_left'] = p_left
        res_welch['p_right'] = p_right
    # grava resultados em arquivo legível
    with open('resultados_console.txt', 'w', encoding='utf-8') as f:
        f.write("ESTATÍSTICA DESCRITIVA - LISTA\n")
        for k,v in stats_lista.items():
            f.write(f"{k}: {v}\n")
        f.write("\nESTATÍSTICA DESCRITIVA - DICIONÁRIO\n")
        for k,v in stats_dict.items():
            f.write(f"{k}: {v}\n")
        f.write("\nTESTE DE HIPÓTESE - WELCH T-TEST\n")
        f.write(f"t = {res_welch['t']}\n")
        f.write(f"df = {res_welch['df']}\n")
        f.write(f"p_two = {res_welch['p_two']}\n")
        f.write(f"p_left = {res_welch.get('p_left')}\n")
        f.write(f"p_right = {res_welch.get('p_right')}\n")
    # grava estatisticas em CSV para inclusão no anexo, útil para tabelas no documento
    if SCIPY:
        df_out = pd.DataFrame([stats_lista, stats_dict], index=['lista','dicionario']).T
        df_out.to_csv('estatisticas_amostra_completa.csv')
    else:
        # grava minimal
        with open('estatisticas_amostra_completa.csv', 'w', encoding='utf-8') as f:
            f.write('stat,lista,dicionario\n')
            for k in stats_lista:
                f.write(f"{k},{stats_lista[k]},{stats_dict[k]}\n")
    print("Cálculos concluídos. Arquivos gerados:\n - resultados_console.txt\n - estatisticas_amostra_completa.csv")
    print("Abra 'resultados_console.txt' para ver os números prontos para copiar e colar no relatório.")

if __name__ == '__main__':
    main()