📁 Descrição dos Arquivos do Repositório

Este repositório contém todos os scripts, resultados e gráficos utilizados no experimento de comparação de desempenho entre busca em listas e busca em dicionários em Python.
Abaixo está um resumo simples da função de cada arquivo.

📌 Scripts Python

experimento_busca.py

Realiza o experimento principal: gera valores aleatórios, monta lista e dicionário, executa buscas e registra os tempos.

calcular_estatisticas.py

Lê os resultados e calcula estatísticas descritivas (média, mediana, desvio-padrão, quartis, etc.).

analise_resultados.py

Faz a análise final: engloba testes de hipótese (Welch t-test) e consolida resultados no formato textual.

gerar_graficos.py

Gera gráficos gerais (histograma, densidade, boxplot) comparando os tempos de busca.

gerar_boxplot_blocos.py

Cria boxplots divididos em blocos (grupos de linhas) para estudar variações internas da distribuição.

📊 Arquivos de Resultados (CSV / TXT)

resultados_amostras.csv

Contém todos os dados brutos do experimento: valor buscado, tempo na lista e tempo no dicionário.

estatisticas_completas.txt

Versão textual com estatísticas descritivas completas da lista e do dicionário.

estatisticas_amostra_completa.csv

Estatísticas descritivas organizadas em CSV (média, mediana, quartis, mínimo, máximo, n, etc.).

estatisticas_blocos.csv

Estatísticas calculadas separadamente por blocos de amostras (para identificar padrões internos).

resultados_console.txt

Saída completa do experimento, incluindo estatísticas e teste t exibidos no terminal.

📈 Gráficos Gerados

histograma.png

Histograma comparando a distribuição dos tempos de busca.

densidade.png

Gráfico de densidade (KDE) das distribuições.

boxplot.png

Boxplot geral com listas e dicionários lado a lado.

boxplot_blocos.png

Boxplot dividido por blocos (ex.: blocos de 50 ou 100 amostras).

