#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
experimento_busca.py
Experimento: Busca em Lista (range) vs Dicionário (dict) em Python
Configuração fixa (padrão para entrega):
    - NUM_ELEMENTOS = 7_000_000
    - NUM_BUSCAS = 4_000_000
    - N_BLOCKS = 4
    - TAMANHO_SAMPLE = 1000

Arquivos de saída:
    - resultados_amostras.csv      (1000 amostras representativas)
    - estatisticas_blocos.csv      (estatísticas por bloco)
    - estatisticas_completas.txt   (estatísticas globais)

Referências / templates usados no relatório:
    - /mnt/data/Rubricas de Correção.pdf
    - /mnt/data/Descrição-Template Resposta Trabalho Computação Experimental.pdf

Observações:
    - O código foi modularizado para clareza e testabilidade.
    - Docstrings seguem o estilo Google.
    - Testado para rodar em máquinas com ~8 GB RAM (feche apps pesados antes de executar).
"""

from __future__ import annotations

import csv
import math
import random
import time
from array import array
from typing import Any, Dict, List, Optional, Tuple

# -----------------------
# CONSTANTES DE CONFIGURAÇÃO (MANTIDAS FIXAS)
# -----------------------
NUM_ELEMENTOS: int = 7_000_000     # tamanho da lista e do dicionário (A)
NUM_BUSCAS: int = 4_000_000        # número total de buscas (B)
N_BLOCKS: int = 4                  # número de blocos para divisão interna
TAMANHO_SAMPLE: int = 1000         # número de amostras a salvar no CSV (C)

PROGRESS_STEP: int = 100_000       # passo de progresso dentro de cada bloco

# -----------------------
# TIPOS AUXILIARES
# -----------------------
Estatisticas = Dict[str, float]
BlocoStats = Dict[str, Any]
Amostra = Tuple[int, int, int]  # (valor, tempo_lista_ns, tempo_dict_ns)


# -----------------------
# FUNÇÕES DE INFRAESTRUTURA
# -----------------------
def criar_estruturas(num_elementos: int) -> Tuple[range, Dict[int, bool]]:
    """
    Cria as estruturas de teste: uma 'lista' representada por range()
    e um dicionário com chaves de 0..num_elementos-1.

    Args:
        num_elementos: número de elementos a gerar.

    Returns:
        Uma tupla (lista_range, dicionario).
    """
    lista_range = range(num_elementos)
    dicionario = dict.fromkeys(range(num_elementos), True)
    return lista_range, dicionario


def medir_busca_lista(valor: int, lista_range: range) -> int:
    """
    Mede o tempo (ns) para verificar se 'valor' está em 'lista_range'.

    Args:
        valor: valor a buscar.
        lista_range: objeto range representando a "lista".

    Returns:
        Tempo em nanossegundos (int).
    """
    t0 = time.perf_counter_ns()
    _ = valor in lista_range
    t1 = time.perf_counter_ns()
    return t1 - t0


def medir_busca_dict(valor: int, dicionario: Dict[int, bool]) -> int:
    """
    Mede o tempo (ns) para verificar se 'valor' está em 'dicionario'.

    Args:
        valor: valor a buscar.
        dicionario: dicionário com chaves.

    Returns:
        Tempo em nanossegundos (int).
    """
    t0 = time.perf_counter_ns()
    _ = valor in dicionario
    t1 = time.perf_counter_ns()
    return t1 - t0


# -----------------------
# FUNÇÕES ESTATÍSTICAS
# -----------------------
def calcular_estatisticas_simples(valores: List[int]) -> Estatisticas:
    """
    Calcula estatísticas descritivas básicas para uma lista de inteiros.

    Estatísticas retornadas: n, media, mediana, pstdev (desvio padrão populacional),
    q1, q3, min, max.

    Args:
        valores: lista de inteiros (tempos em ns).

    Returns:
        Dicionário com as estatísticas.
    """
    n = len(valores)
    if n == 0:
        raise ValueError("Lista de valores vazia para cálculo estatístico.")

    # média
    s = sum(valores)
    mean = s / n

    # desvio padrão populacional (pstdev)
    ssd = sum((x - mean) ** 2 for x in valores)
    pstdev = math.sqrt(ssd / n)

    minimo = min(valores)
    maximo = max(valores)

    # quantis (usamos uma cópia ordenada)
    sorted_vals = sorted(valores)

    def quantil(sorted_arr: List[int], q: float) -> float:
        """
        Calcula o quantil q em [0,1] com interpolação linear.
        """
        pos = q * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        return sorted_arr[lo] * (1 - frac) + sorted_arr[hi] * frac

    mediana = quantil(sorted_vals, 0.5)
    q1 = quantil(sorted_vals, 0.25)
    q3 = quantil(sorted_vals, 0.75)

    return {
        "n": float(n),
        "media": float(mean),
        "mediana": float(mediana),
        "pstdev": float(pstdev),
        "q1": float(q1),
        "q3": float(q3),
        "min": float(minimo),
        "max": float(maximo),
    }


# -----------------------
# FUNÇÕES DE I/O
# -----------------------
def salvar_amostras_csv(amostras: List[Amostra], nome_arquivo: str = "resultados_amostras.csv") -> None:
    """
    Salva amostras representativas em CSV.

    Args:
        amostras: lista de tuplas (valor, tempo_lista_ns, tempo_dict_ns).
        nome_arquivo: nome do arquivo CSV a ser criado.
    """
    with open(nome_arquivo, "w", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["valor", "tempo_lista_ns", "tempo_dict_ns"])
        for linha in amostras:
            escritor.writerow(linha)


def salvar_estatisticas_blocos_csv(estat_blocos: List[BlocoStats], nome_arquivo: str = "estatisticas_blocos.csv") -> None:
    """
    Salva estatísticas resumidas por bloco em CSV.

    Args:
        estat_blocos: lista de dicionários com estatísticas por bloco.
        nome_arquivo: nome do CSV de saída.
    """
    header = [
        "bloco", "n",
        "lista_media", "lista_mediana", "lista_pstdev", "lista_q1", "lista_q3", "lista_min", "lista_max",
        "dict_media", "dict_mediana", "dict_pstdev", "dict_q1", "dict_q3", "dict_min", "dict_max"
    ]
    with open(nome_arquivo, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for s in estat_blocos:
            writer.writerow([
                s["bloco"], s["n"],
                s["lista_media"], s["lista_mediana"], s["lista_pstdev"], s["lista_q1"], s["lista_q3"], s["lista_min"], s["lista_max"],
                s["dict_media"], s["dict_mediana"], s["dict_pstdev"], s["dict_q1"], s["dict_q3"], s["dict_min"], s["dict_max"]
            ])


def salvar_estatisticas_completas_txt(stats_lista: Estatisticas, stats_dict: Estatisticas, nome_arquivo: str = "estatisticas_completas.txt") -> None:
    """
    Salva estatísticas globais (lista e dicionário) em um arquivo de texto formatado.

    Args:
        stats_lista: estatísticas para a lista.
        stats_dict: estatísticas para o dicionário.
        nome_arquivo: nome do arquivo de saída.
    """
    with open(nome_arquivo, "w") as f:
        f.write("=== EXPERIMENTO: BUSCA EM LISTA VS DICIONÁRIO (POR BLOCOS) ===\n\n")
        f.write(f"Elementos: {NUM_ELEMENTOS:,}\n")
        f.write(f"Buscas totais: {NUM_BUSCAS:,}\n")
        f.write(f"Número de blocos: {N_BLOCKS}\n\n")

        f.write("=== ESTATÍSTICAS GLOBAIS - LISTA ===\n")
        for k, v in stats_lista.items():
            f.write(f"{k}: {v}\n")

        f.write("\n=== ESTATÍSTICAS GLOBAIS - DICIONÁRIO ===\n")
        for k, v in stats_dict.items():
            f.write(f"{k}: {v}\n")


# -----------------------
# FLUXO PRINCIPAL DO EXPERIMENTO (POR BLOCOS)
# -----------------------
def executar_experimento_por_blocos() -> None:
    """
    Executa o experimento completo, dividido em blocos.

    O fluxo principal:
        1. Cria estruturas (lista e dicionário).
        2. Para cada bloco:
           - executa BLOCK_SIZE buscas
           - coleta tempos por bloco
           - calcula estatísticas do bloco e armazena em 'estatisticas_blocos'
        3. Após todos os blocos, calcula estatísticas globais (todas as medidas)
        4. Salva arquivos de saída: amostras CSV, estatísticas por bloco CSV e estatísticas globais TXT
    """
    # validações simples
    if N_BLOCKS <= 0:
        raise ValueError("N_BLOCKS deve ser >= 1.")
    if NUM_BUSCAS <= 0:
        raise ValueError("NUM_BUSCAS deve ser > 0.")
    if NUM_ELEMENTOS <= 0:
        raise ValueError("NUM_ELEMENTOS deve ser > 0.")
    if TAMANHO_SAMPLE < 0:
        raise ValueError("TAMANHO_SAMPLE não pode ser negativo.")

    # preparo
    lista_range, dicionario = criar_estruturas(NUM_ELEMENTOS)
    block_size = NUM_BUSCAS // N_BLOCKS
    # coletores globais (arrays compactos)
    tempos_lista = array('I')  # tempos em ns (unsigned int)
    tempos_dict = array('I')
    amostras: List[Amostra] = []
    estatisticas_blocos: List[BlocoStats] = []

    print("CONFIGURAÇÃO DO EXPERIMENTO:")
    print(f"- Elementos (lista/dicionário): {NUM_ELEMENTOS:,}")
    print(f"- Buscas totais:                {NUM_BUSCAS:,}")
    print(f"- Blocos:                       {N_BLOCKS}")
    print(f"- Buscas por bloco (aprox):     {block_size:,}")
    print(f"- Amostras salvas (CSV):        {TAMANHO_SAMPLE:,}\n")

    tempo_inicio_total = time.perf_counter()

    for bloco in range(N_BLOCKS):
        print(f"Iniciando bloco {bloco + 1}/{N_BLOCKS}...")
        inicio_bloco = time.perf_counter()
        bloco_coletor_lista: List[int] = []
        bloco_coletor_dict: List[int] = []

        for i in range(block_size):
            valor = random.randint(0, NUM_ELEMENTOS - 1)

            tl = medir_busca_lista(valor, lista_range)
            td = medir_busca_dict(valor, dicionario)

            # append em coletores compactos (garantimos corte caso valor exceda uint32)
            tempos_lista.append(int(min(tl, 2**32 - 1)))
            tempos_dict.append(int(min(td, 2**32 - 1)))

            bloco_coletor_lista.append(int(min(tl, 2**32 - 1)))
            bloco_coletor_dict.append(int(min(td, 2**32 - 1)))

            # coletar amostras representativas (apenas primeiras TAMANHO_SAMPLE)
            if len(amostras) < TAMANHO_SAMPLE:
                amostras.append((valor, tl, td))

            # progresso interno
            if (i + 1) % PROGRESS_STEP == 0:
                pct = (i + 1) / block_size * 100
                tempo_decorrido = time.perf_counter() - inicio_bloco
                print(f" Bloco {bloco+1}: {i+1:,}/{block_size:,} ({pct:.1f}%) — {tempo_decorrido:.1f}s")

        # calcular estatísticas do bloco e armazenar
        stats_l = calcular_estatisticas_simples(bloco_coletor_lista)
        stats_d = calcular_estatisticas_simples(bloco_coletor_dict)

        bloco_stats: BlocoStats = {
            "bloco": bloco + 1,
            "n": stats_l["n"],
            "lista_media": stats_l["media"],
            "lista_mediana": stats_l["mediana"],
            "lista_pstdev": stats_l["pstdev"],
            "lista_q1": stats_l["q1"],
            "lista_q3": stats_l["q3"],
            "lista_min": stats_l["min"],
            "lista_max": stats_l["max"],
            "dict_media": stats_d["media"],
            "dict_mediana": stats_d["mediana"],
            "dict_pstdev": stats_d["pstdev"],
            "dict_q1": stats_d["q1"],
            "dict_q3": stats_d["q3"],
            "dict_min": stats_d["min"],
            "dict_max": stats_d["max"],
        }
        estatisticas_blocos.append(bloco_stats)

        tempo_fim_bloco = time.perf_counter()
        print(f"Bloco {bloco+1} concluído em {tempo_fim_bloco - inicio_bloco:.1f}s\n")

    tempo_fim_total = time.perf_counter()
    print(f"Coleta completa. Tempo total: {tempo_fim_total - tempo_inicio_total:.1f}s\n")

    # salvar amostras e estatísticas por bloco
    salvar_amostras_csv(amostras)
    salvar_estatisticas_blocos_csv(estatisticas_blocos)

    # calcular e salvar estatísticas globais
    stats_glob_lista = calcular_estatisticas_simples(list(tempos_lista))
    stats_glob_dict = calcular_estatisticas_simples(list(tempos_dict))
    salvar_estatisticas_completas_txt(stats_glob_lista, stats_glob_dict)

    # impressão resumo
    print("RESUMO ESTATÍSTICO GLOBAL (exemplo resumido):")
    print(f"- LISTA: média = {stats_glob_lista['media']:.2f} ns, mediana = {stats_glob_lista['mediana']:.2f} ns, pstdev = {stats_glob_lista['pstdev']:.2f} ns")
    print(f"- DICIONÁRIO: média = {stats_glob_dict['media']:.2f} ns, mediana = {stats_glob_dict['mediana']:.2f} ns, pstdev = {stats_glob_dict['pstdev']:.2f} ns")
    print("\nArquivos gerados:")
    print("- resultados_amostras.csv")
    print("- estatisticas_blocos.csv")
    print("- estatisticas_completas.txt")
    print("\nExperimento finalizado com sucesso.")


# -----------------------
# PONTO DE ENTRADA
# -----------------------
if __name__ == "__main__":
    # Execução principal do script
    try:
        executar_experimento_por_blocos()
    except Exception as e:
        print(f"Erro durante a execução do experimento: {e}")
        raise