#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para geração de gráficos do experimento:
- Boxplot (lista vs dicionário)
- Histograma (lista vs dicionário)
- Densidade aproximada (por histogramas normalizados)

Entrada:
    resultados_amostras.csv
        colunas: valor, tempo_lista_ns, tempo_dict_ns

Saída:
    boxplot.png
    histograma.png
    densidade.png
"""

import csv
import matplotlib.pyplot as plt

ARQUIVO = "resultados_amostras.csv"


def carregar_dados(caminho):
    tempos_lista = []
    tempos_dict = []

    with open(caminho, "r") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            tempos_lista.append(int(linha["tempo_lista_ns"]))
            tempos_dict.append(int(linha["tempo_dict_ns"]))

    return tempos_lista, tempos_dict


def gerar_boxplot(tempos_lista, tempos_dict):
    plt.figure()
    plt.boxplot([tempos_lista, tempos_dict], labels=["Lista", "Dicionário"])
    plt.title("Boxplot — Tempos de Busca (ns)")
    plt.ylabel("Tempo (ns)")
    plt.savefig("boxplot.png", dpi=300, bbox_inches="tight")
    plt.close()


def gerar_histograma(tempos_lista, tempos_dict):
    plt.figure()
    plt.hist(tempos_lista, bins=50, alpha=0.5)
    plt.hist(tempos_dict, bins=50, alpha=0.5)
    plt.title("Histograma — Tempos de Busca (ns)")
    plt.xlabel("Tempo (ns)")
    plt.ylabel("Frequência")
    plt.savefig("histograma.png", dpi=300, bbox_inches="tight")
    plt.close()


def gerar_densidade(tempos_lista, tempos_dict):
    plt.figure()
    plt.hist(tempos_lista, bins=80, density=True, alpha=0.5)
    plt.hist(tempos_dict, bins=80, density=True, alpha=0.5)
    plt.title("Densidade Aproximada — Lista vs Dicionário")
    plt.xlabel("Tempo (ns)")
    plt.ylabel("Densidade Aproximada")
    plt.savefig("densidade.png", dpi=300, bbox_inches="tight")
    plt.close()


def main():
    print("Carregando dados...")
    tempos_lista, tempos_dict = carregar_dados(ARQUIVO)

    print("Gerando boxplot...")
    gerar_boxplot(tempos_lista, tempos_dict)

    print("Gerando histograma...")
    gerar_histograma(tempos_lista, tempos_dict)

    print("Gerando densidade...")
    gerar_densidade(tempos_lista, tempos_dict)

    print("\nGráficos gerados com sucesso:")
    print("- boxplot.png")
    print("- histograma.png")
    print("- densidade.png")


if __name__ == "__main__":
    main()