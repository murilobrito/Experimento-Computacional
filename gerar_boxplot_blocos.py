#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gera boxplots por bloco, usando estatisticas_blocos.csv.
Permite visualizar a estabilidade dos blocos.
"""

import csv
import matplotlib.pyplot as plt

ARQUIVO = "estatisticas_blocos.csv"


def carregar_estatisticas_por_bloco(caminho):
    blocos = []
    lista_medianas = []
    dicionario_medianas = []

    with open(caminho, "r") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            blocos.append(int(linha["bloco"]))
            lista_medianas.append(float(linha["lista_mediana"]))
            dicionario_medianas.append(float(linha["dict_mediana"]))

    return blocos, lista_medianas, dicionario_medianas


def gerar_boxplot_blocos(blocos, lista_medianas, dicionario_medianas):
    plt.figure()
    plt.boxplot([lista_medianas, dicionario_medianas],
                labels=["Lista (medianas por bloco)", "Dicionário (medianas por bloco)"])
    plt.title("Boxplot das Medianas por Bloco")
    plt.ylabel("Tempo (ns)")
    plt.savefig("boxplot_blocos.png", dpi=300, bbox_inches="tight")
    plt.close()


def main():
    blocos, listas, dicts = carregar_estatisticas_por_bloco(ARQUIVO)
    gerar_boxplot_blocos(blocos, listas, dicts)
    print("Gráfico por bloco gerado: boxplot_blocos.png")


if __name__ == "__main__":
    main()