import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =========================================================
# 🎨 CORES (EDITÁVEL)
# =========================================================
COR_SUCESSO = "#2ca02c"
COR_FALHA = "#d62728"

ALPHA_CORTE = 0.75
ALPHA_RELIGA = 0.75

# =========================================================
# 📂 CAMINHO
# =========================================================
PASTA_BASE = r"C:\Users\nsn101555\OneDrive - nansen.com.br\Área de Trabalho\Nansen\Comandos Remotos"
ARQUIVO_EXCEL = "comandos.xlsx"

CAMINHO_PLANILHA = os.path.join(PASTA_BASE, ARQUIVO_EXCEL)

# =========================================================
# 📊 LEITURA
# =========================================================
df = pd.read_excel(CAMINHO_PLANILHA)
df.columns = df.columns.str.strip()

# =========================================================
# 🔎 DETECÇÃO DINÂMICA DAS COLUNAS
# =========================================================
col_success = [c for c in df.columns if "success rate" in c.lower()][0]
col_tipo = [c for c in df.columns if "tipo" in c.lower() or "comando" in c.lower()][0]
col_data = [c for c in df.columns if "date" in c.lower()][0]

# =========================================================
# 📅 TRATAMENTO DE DATAS
# =========================================================
df[col_data] = pd.to_datetime(df[col_data], dayfirst=False, errors="coerce")
df = df.dropna(subset=[col_data])

# =========================================================
# 📊 STATUS
# =========================================================
df["Status"] = df[col_success].apply(
    lambda x: "Sucesso" if x > 0 else "Falha"
)

tabela = (
    df.groupby([col_data, col_tipo, "Status"])
      .size()
      .unstack(fill_value=0)
)

tabela["Total"] = tabela.sum(axis=1)
tabela["Sucesso_%"] = tabela.get("Sucesso", 0) / tabela["Total"] * 100
tabela["Falha_%"] = tabela.get("Falha", 0) / tabela["Total"] * 100

# =========================================================
# 📈 PREPARAÇÃO DADOS
# =========================================================
datas = sorted(tabela.index.get_level_values(0).unique())

sucesso_corte, falha_corte = [], []
abs_sucesso_corte, abs_falha_corte = [], []

sucesso_religa, falha_religa = [], []
abs_sucesso_religa, abs_falha_religa = [], []

for data in datas:

    if (data, "Corte") in tabela.index:
        linha = tabela.loc[(data, "Corte")]
        sucesso_corte.append(linha["Sucesso_%"])
        falha_corte.append(linha["Falha_%"])
        abs_sucesso_corte.append(linha.get("Sucesso", 0))
        abs_falha_corte.append(linha.get("Falha", 0))
    else:
        sucesso_corte.append(0)
        falha_corte.append(0)
        abs_sucesso_corte.append(0)
        abs_falha_corte.append(0)

    if (data, "Religa") in tabela.index:
        linha = tabela.loc[(data, "Religa")]
        sucesso_religa.append(linha["Sucesso_%"])
        falha_religa.append(linha["Falha_%"])
        abs_sucesso_religa.append(linha.get("Sucesso", 0))
        abs_falha_religa.append(linha.get("Falha", 0))
    else:
        sucesso_religa.append(0)
        falha_religa.append(0)
        abs_sucesso_religa.append(0)
        abs_falha_religa.append(0)

# =========================================================
# 📈 EIXO X (BLOCOS)
# =========================================================
n = len(datas)

x_corte = np.arange(n)
x_religa = np.arange(n) + n + 1

plt.figure(figsize=(16, 5))

# =========================================================
# 🔹 BARRAS CORTE
# =========================================================
plt.bar(
    x_corte,
    sucesso_corte,
    color=COR_SUCESSO,
    alpha=ALPHA_CORTE,
    edgecolor="black",
    linewidth=0.6
)

plt.bar(
    x_corte,
    falha_corte,
    bottom=sucesso_corte,
    color=COR_FALHA,
    alpha=ALPHA_CORTE,
    edgecolor="black",
    linewidth=0.6
)

# =========================================================
# 🔹 BARRAS RELIGA
# =========================================================
plt.bar(
    x_religa,
    sucesso_religa,
    color=COR_SUCESSO,
    alpha=ALPHA_RELIGA,
    edgecolor="black",
    linewidth=0.6
)

plt.bar(
    x_religa,
    falha_religa,
    bottom=sucesso_religa,
    color=COR_FALHA,
    alpha=ALPHA_RELIGA,
    edgecolor="black",
    linewidth=0.6
)

# =========================================================
# 🔢 RÓTULOS NAS BARRAS
# =========================================================
def rotular(posicoes, sucesso_pct, falha_pct,
             sucesso_abs, falha_abs):

    for px, suc, fal, abs_suc, abs_fal in zip(
        posicoes,
        sucesso_pct,
        falha_pct,
        sucesso_abs,
        falha_abs
    ):

        abs_suc = int(abs_suc)
        abs_fal = int(abs_fal)

        if suc > 0:
            plt.text(
                px,
                suc / 2,
                f"{suc:.1f}%\n({abs_suc})",
                ha="center",
                va="center",
                color="white",
                fontsize=11,
                fontweight="bold"
            )

        if fal > 0:
            plt.text(
                px,
                suc + fal / 2,
                f"{fal:.1f}%\n({abs_fal})",
                ha="center",
                va="center",
                color="black",
                fontsize=11,
                fontweight="bold"
            )

rotular(
    x_corte,
    sucesso_corte,
    falha_corte,
    abs_sucesso_corte,
    abs_falha_corte
)

rotular(
    x_religa,
    sucesso_religa,
    falha_religa,
    abs_sucesso_religa,
    abs_falha_religa
)

# =========================================================
# 📅 DIA DA SEMANA + DATA
# =========================================================
dias_semana = {
    "Monday": "Seg",
    "Tuesday": "Ter",
    "Wednesday": "Qua",
    "Thursday": "Qui",
    "Friday": "Sex",
    "Saturday": "Sáb",
    "Sunday": "Dom"
}

labels = [
    f"{d.strftime('%d/%m')}\n{dias_semana[d.strftime('%A')]}"
    for d in datas
]

plt.xticks(
    list(x_corte) + list(x_religa),
    labels + labels,
    rotation=0
)

# =========================================================
# 🎨 LAYOUT
# =========================================================
plt.ylim(0, 110)

plt.yticks(np.arange(0, 101, 10))

plt.ylabel("Percentual (%)")
plt.title("COPEL - COMANDOS REMOTOS", fontweight="bold")

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.axvline(
    n,
    linestyle="--",
    linewidth=1
)

plt.text(
    (n - 1) / 2,
    103,
    "CORTE",
    ha="center",
    fontsize=12,
    fontweight="bold"
)

plt.text(
    n + 1 + (n - 1) / 2,
    103,
    "RELIGA",
    ha="center",
    fontsize=12,
    fontweight="bold"
)

# =========================================================
# ✅ LEGENDA
# =========================================================
plt.legend(
    handles=[
        Patch(facecolor=COR_SUCESSO, label="Sucesso"),
        Patch(facecolor=COR_FALHA, label="Falha")
    ],
    ncol=2
)

plt.tight_layout()

# =========================================================
# 💾 SALVAR
# =========================================================
saida = os.path.join(
    PASTA_BASE,
    "comandos_remotos.png"
)

plt.savefig(
    saida,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"\n✅ Gráfico atualizado gerado:\n{saida}")