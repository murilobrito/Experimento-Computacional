#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import numpy as np
import math
import statistics
from scipy.stats import t as student_t

# ==========================================
# CONFIGURAÇÃO DO ARQUIVO
# ==========================================

CSV_AMOSTRAS = "resultados_amostras.csv"   # Deve estar na mesma pasta

# ==========================================
# CARREGAR DADOS
# ==========================================

tempos_lista = []
tempos_dict = []
amostras_raw = []

with open(CSV_AMOSTRAS, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # assume cabeçalhos: valor, tempo_lista_ns, tempo_dict_ns
        tl = int(row["tempo_lista_ns"])
        td = int(row["tempo_dict_ns"])
        tempos_lista.append(tl)
        tempos_dict.append(td)
        amostras_raw.append((int(row["valor"]), tl, td))

tempos_lista = np.array(tempos_lista)
tempos_dict = np.array(tempos_dict)

print("==========================================")
print(" TAMANHO DA AMOSTRA ")
print("==========================================")
print(f"n_lista      = {len(tempos_lista)}")
print(f"n_dicionario = {len(tempos_dict)}\n")

# ==========================================
# ESTATÍSTICAS DESCRITIVAS
# ==========================================

def resumo(v):
    return {
        "n": len(v),
        "mean": float(np.mean(v)),
        "median": float(np.median(v)),
        "std_pop": float(np.std(v, ddof=0)),
        "q1": float(np.quantile(v, 0.25)),
        "q3": float(np.quantile(v, 0.75)),
        "min": int(np.min(v)),
        "max": int(np.max(v)),
    }

res_lista = resumo(tempos_lista)
res_dict = resumo(tempos_dict)

print("==========================================")
print(" ESTATÍSTICA DESCRITIVA - LISTA ")
print("==========================================")
for k, v in res_lista.items():
    print(f"{k}: {v}")
print()

print("==========================================")
print(" ESTATÍSTICA DESCRITIVA - DICIONÁRIO ")
print("==========================================")
for k, v in res_dict.items():
    print(f"{k}: {v}")
print()

# ==========================================
# WELCH T-TEST (EXATO VIA SCIPY)
# ==========================================

mx, my = res_lista["mean"], res_dict["mean"]
vx, vy = res_lista["std_pop"]**2, res_dict["std_pop"]**2
nx, ny = res_lista["n"], res_dict["n"]

# erro padrão
se = math.sqrt(vx/nx + vy/ny)

# estatística t
t_stat = (mx - my) / se

# graus de liberdade (Welch-Satterthwaite)
df = (vx/nx + vy/ny)**2 / ((vx*vx)/(nx*nx*(nx-1)) + (vy*vy)/(ny*ny*(ny-1)))

# p-value exato — bicaudal
p_two = 2 * student_t.sf(abs(t_stat), df)

# unicaudais
p_left = student_t.cdf(t_stat, df)     # lista < dicionário
p_right = 1 - p_left                   # lista > dicionário

print("==========================================")
print(" TESTE DE HIPÓTESE - WELCH T-TEST ")
print("==========================================")
print(f"t_stat = {t_stat}")
print(f"df     = {df}")
print(f"p_two  (bicaudal)     = {p_two}")
print(f"p_left (lista < dict) = {p_left}")
print(f"p_right(lista > dict) = {p_right}")
print("==========================================")