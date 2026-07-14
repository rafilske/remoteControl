import pandas as pd
import os
import matplotlib.pyplot as plt
import re
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# =========================================================
# 📊 Processa um Excel individual
# =========================================================
def processar_excel(caminho):
    df = pd.read_excel(caminho)

    total = len(df)
    sucesso = (df["Success Rate(%)"] > 0.0).sum()
    falha = (df["Success Rate(%)"] == 0.0).sum()

    return total, sucesso, falha

# =========================================================
# 🔎 Extrai tipo (corte/religa) e data do nome
# =========================================================
def extrair_info_nome(nome_arquivo):
    nome = nome_arquivo.lower()

    if "corte" in nome:
        tipo = "Corte"
    elif "religa" in nome:
        tipo = "Religa"
    else:
        return None, None

    match = re.search(r"(\d{2}-\d{2})", nome)
    data = match.group(1) if match else None

    return tipo, data

# =========================================================
# 📂 Consolida dados de todos os arquivos
# =========================================================
def consolidar_dados(pasta):
    dados = {}

    for arquivo in os.listdir(pasta):
        if not arquivo.endswith(".xlsx"):
            continue

        tipo, data = extrair_info_nome(arquivo)
        if not tipo or not data:
            continue

        caminho = os.path.join(pasta, arquivo)
        total, sucesso, falha = processar_excel(caminho)

        if data not in dados:
            dados[data] = {
                "Corte": {"Total": 0, "Sucesso": 0, "Falha": 0},
                "Religa": {"Total": 0, "Sucesso": 0, "Falha": 0},
            }

        dados[data][tipo]["Total"] += total
        dados[data][tipo]["Sucesso"] += sucesso
        dados[data][tipo]["Falha"] += falha

    return dados

# =========================================================
# 📈 Gráfico consolidado (2 colunas por dia, stacked)
# =========================================================
def gerar_grafico_consolidado(dados, pasta_saida):
    datas = sorted(dados.keys())
    x = range(len(datas))
    largura = 0.35

    corte_sucesso = [dados[d]["Corte"]["Sucesso"] for d in datas]
    corte_falha = [dados[d]["Corte"]["Falha"] for d in datas]
    religa_sucesso = [dados[d]["Religa"]["Sucesso"] for d in datas]
    religa_falha = [dados[d]["Religa"]["Falha"] for d in datas]

    corte_total = [dados[d]["Corte"]["Total"] for d in datas]
    religa_total = [dados[d]["Religa"]["Total"] for d in datas]

    plt.figure(figsize=(14, 5))

    # Corte
    barras_corte_sucesso = plt.bar(
        [i - largura / 2 for i in x],
        corte_sucesso,
        largura,
        label="Corte – Sucesso"
    )

    barras_corte_falha = plt.bar(
        [i - largura / 2 for i in x],
        corte_falha,
        largura,
        bottom=corte_sucesso,
        label="Corte – Falha"
    )

    # Religa
    barras_religa_sucesso = plt.bar(
        [i + largura / 2 for i in x],
        religa_sucesso,
        largura,
        label="Religa – Sucesso"
    )

    barras_religa_falha = plt.bar(
        [i + largura / 2 for i in x],
        religa_falha,
        largura,
        bottom=religa_sucesso,
        label="Religa – Falha"
    )

    # =====================================================
    # 🔢 Rótulos dentro das barras
    # =====================================================
    def rotular_barras(barras, valores, totais):
        for barra, valor, total in zip(barras, valores, totais):
            if valor == 0:
                continue
            pct = (valor / total * 100) if total else 0
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_y() + barra.get_height() / 2,
                f"{valor}\n({pct:.1f}%)",
                ha="center",
                va="center",
                fontsize=9,
                color="white"
            )

    rotular_barras(barras_corte_sucesso, corte_sucesso, corte_total)
    rotular_barras(barras_corte_falha, corte_falha, corte_total)
    rotular_barras(barras_religa_sucesso, religa_sucesso, religa_total)
    rotular_barras(barras_religa_falha, religa_falha, religa_total)

    plt.xticks(x, datas)
    plt.xlabel("Data do Comando")
    plt.ylabel("Quantidade")
    plt.title("COPEL – Consolidado Diário | Corte x Religa")
    plt.legend(ncol=2)
    plt.grid(axis="y")

    caminho = os.path.join(
        pasta_saida,
        "consolidado_diario_corte_religa_stacked.png"
    )

    plt.tight_layout()
    plt.savefig(caminho, dpi=300)
    plt.close()

    print(f"📈 Imagem gerada: {caminho}")

# =========================================================
# 🚀 EXECUÇÃO PRINCIPAL
# =========================================================
PASTA_BASE = r"C:\Users\nsn101555\OneDrive - nansen.com.br\Área de Trabalho\Nansen\Comandos Remotos"

dados_consolidados = consolidar_dados(PASTA_BASE)

gerar_grafico_consolidado(dados_consolidados, PASTA_BASE)

print("\n✅ Gráfico consolidado final gerado com sucesso.")
