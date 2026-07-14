README – Geração de Relatório Corte e Religa
===========================================

OBJETIVO
--------
Este documento descreve o uso do script Python responsável por analisar arquivos
Excel de comandos remotos (Corte e Religa) e gerar automaticamente uma imagem (.png)
contendo uma tabela consolidada de resultados.

O QUE O CÓDIGO FAZ
-----------------
- Localiza automaticamente os arquivos Excel de Corte e Religa
- Analisa a coluna Success
- Classifica os resultados
   Success  0  - Sucesso
   Success == 0 - Falha Total
- Calcula
   Total de medidores
   Quantidade de sucessos
   Quantidade de falhas totais
   Percentual de sucesso e falha
- Gera uma única imagem PNG contendo os resultados consolidados

ESTRUTURA ESPERADA DA PASTA
---------------------------
- corte 28 Switch Relay Statistic.xlsx
- religa 28 Switch Relay Statistic.xlsx
- aplication.py
- resultado_corte_religa_tabela.png (gerado automaticamente)

REQUISITOS
----------
- Python 3.9 ou superior
- Bibliotecas Python
  - pandas
  - matplotlib
  - openpyxl

INSTALAÇÃO DAS DEPENDÊNCIAS
--------------------------
Executar no PowerShell ou Prompt de Comando

py -m pip install pandas matplotlib openpyxl

ESTRUTURA ESPERADA DO EXCEL
--------------------------
- O arquivo deve conter a coluna Success
- As colunas H e I são desconsideradas
- Regras aplicadas
  Success  0  - Sucesso
  Success == 0 - Falha Total

COMO EXECUTAR
-------------
1. Ajustar o caminho da variável PASTA_BASE no código, se necessário
2. Executar o script

   py aplication.py

RESULTADO GERADO
----------------
- Arquivo gerado
  resultado_corte_religa_tabela.png

- Conteúdo da imagem
   Success
   Total Failure
   Total
  Para Corte e Religa

