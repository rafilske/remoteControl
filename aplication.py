import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =========================================================
# 🎨 CORES (EDITÁVEL)
# =========================================================
COR_SUCESSO = "#2ca02c"
COR_FALHA   = "#d62728"
COR_BYPASS  = "#ff7f0e"

ALPHA_CORTE  = 0.75
ALPHA_RELIGA = 0.75

# =========================================================
# 🔢 CONFIGURAÇÃO DOS RÓTULOS
# =========================================================
LIMIAR_INTERNO = 12
LIMITE_Y = 140

# =========================================================
# 📂 CAMINHO
# =========================================================
PASTA_BASE    = r"C:\Users\nsn101555\OneDrive - nansen.com.br\Área de Trabalho\Nansen\Comandos Remotos"
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
col_tipo      = [c for c in df.columns if "tipo"      in c.lower() or "comando"  in c.lower()][0]
col_data      = [c for c in df.columns if "date"      in c.lower()][0]
col_resultado = [c for c in df.columns if "resultado" in c.lower()][0]

# =========================================================
# 📅 TRATAMENTO DE DATAS
# =========================================================
df[col_data] = pd.to_datetime(df[col_data], dayfirst=False, errors="coerce")
df = df.dropna(subset=[col_data])

# =========================================================
# 📊 STATUS — lido diretamente da coluna "Resultado"
# =========================================================
df["Status"] = df[col_resultado].str.strip()

# =========================================================
# 📊 AGRUPAMENTO
# =========================================================
tabela = (
    df.groupby([col_data, col_tipo, "Status"])
      .size()
      .unstack(fill_value=0)
)

for col in ("Sucesso", "Falha", "Bypass"):
    if col not in tabela.columns:
        tabela[col] = 0

tabela["Total"]     = tabela[["Sucesso", "Falha", "Bypass"]].sum(axis=1)
tabela["Sucesso_%"] = tabela["Sucesso"] / tabela["Total"] * 100
tabela["Falha_%"]   = tabela["Falha"]   / tabela["Total"] * 100
tabela["Bypass_%"]  = tabela["Bypass"]  / tabela["Total"] * 100

# =========================================================
# 📈 PREPARAÇÃO DOS DADOS POR TIPO
# =========================================================
datas = sorted(tabela.index.get_level_values(0).unique())

def extrair_series(tipo):
    suc_pct, fal_pct, byp_pct = [], [], []
    suc_abs, fal_abs, byp_abs = [], [], []

    for data in datas:
        if (data, tipo) in tabela.index:
            linha = tabela.loc[(data, tipo)]
            suc_pct.append(linha["Sucesso_%"])
            fal_pct.append(linha["Falha_%"])
            byp_pct.append(linha["Bypass_%"])
            suc_abs.append(int(linha["Sucesso"]))
            fal_abs.append(int(linha["Falha"]))
            byp_abs.append(int(linha["Bypass"]))
        else:
            suc_pct.append(0); fal_pct.append(0); byp_pct.append(0)
            suc_abs.append(0); fal_abs.append(0); byp_abs.append(0)

    return suc_pct, fal_pct, byp_pct, suc_abs, fal_abs, byp_abs

(sucesso_corte,  falha_corte,  bypass_corte,
 abs_suc_corte,  abs_fal_corte, abs_byp_corte)  = extrair_series("Corte")

(sucesso_religa, falha_religa, bypass_religa,
 abs_suc_religa, abs_fal_religa, abs_byp_religa) = extrair_series("Religa")

# =========================================================
# 📈 EIXO X
# =========================================================
n        = len(datas)
x_corte  = np.arange(n)
x_religa = np.arange(n) + n + 1

fig, ax = plt.subplots(figsize=(16, 6))

# =========================================================
# 🔹 BARRAS
# =========================================================
def plotar_barras(posicoes, suc_pct, fal_pct, byp_pct, alpha):
    ax.bar(posicoes, suc_pct,
           color=COR_SUCESSO, alpha=alpha,
           edgecolor="black", linewidth=0.6)

    ax.bar(posicoes, fal_pct,
           bottom=suc_pct,
           color=COR_FALHA, alpha=alpha,
           edgecolor="black", linewidth=0.6)

    bottom_byp = [s + f for s, f in zip(suc_pct, fal_pct)]
    ax.bar(posicoes, byp_pct,
           bottom=bottom_byp,
           color=COR_BYPASS, alpha=alpha,
           edgecolor="black", linewidth=0.6)

plotar_barras(x_corte,  sucesso_corte,  falha_corte,  bypass_corte,  ALPHA_CORTE)
plotar_barras(x_religa, sucesso_religa, falha_religa, bypass_religa, ALPHA_RELIGA)

# =========================================================
# 🔢 RÓTULOS INTELIGENTES (interno ou externo com seta)
# =========================================================
def rotular_segmento(ax, px, y_centro, y_topo_barra, pct, qtd, cor_texto, offset_externo):
    """
    Se o segmento for grande o suficiente → rótulo interno.
    Caso contrário → rótulo externo com anotação (seta).
    offset_externo: deslocamento em % do eixo Y para o texto externo,
                    acumulado por barra para evitar sobreposição entre externos.
    Retorna o novo offset acumulado.
    """
    texto = f"{pct:.1f}%\n({qtd})"

    if pct >= LIMIAR_INTERNO:
        # Rótulo dentro da barra
        ax.text(px, y_centro, texto,
                ha="center", va="center",
                color=cor_texto, fontsize=10, fontweight="bold")
        return offset_externo  # não consome espaço externo

    else:
        # Rótulo fora da barra com seta
        y_texto = min(
            y_topo_barra + offset_externo + 4,
            LIMITE_Y - 20
        )
        ax.annotate(
            texto,
            xy=(px, y_centro),
            xytext=(px, y_texto),
            ha="center", va="bottom",
            fontsize=9, fontweight="bold", color="black",
            arrowprops=dict(
                arrowstyle="->,head_width=0.2,head_length=0.3",
                color="gray",
                lw=0.8
            )
        )
        return offset_externo + 10  # empilha próximo externo acima


def rotular(posicoes, suc_pct, fal_pct, byp_pct,
             suc_abs,  fal_abs,  byp_abs):

    for px, suc, fal, byp, a_s, a_f, a_b in zip(
        posicoes,
        suc_pct, fal_pct, byp_pct,
        suc_abs, fal_abs, byp_abs
    ):
        topo_barra  = suc + fal + byp
        offset_ext  = 0  # acumulador de rótulos externos por barra

        # — Sucesso (segmento inferior)
        if suc > 0:
            offset_ext = rotular_segmento(
                ax,
                px,
                y_centro      = suc / 2,
                y_topo_barra  = topo_barra,
                pct           = suc,
                qtd           = a_s,
                cor_texto     = "white",
                offset_externo= offset_ext
            )

        # — Falha (segmento do meio)
        if fal > 0:
            offset_ext = rotular_segmento(
                ax,
                px,
                y_centro      = suc + fal / 2,
                y_topo_barra  = topo_barra,
                pct           = fal,
                qtd           = a_f,
                cor_texto     = "black",
                offset_externo= offset_ext
            )

        # — Bypass (segmento superior)
        if byp > 0:
            offset_ext = rotular_segmento(
                ax,
                px,
                y_centro      = suc + fal + byp / 2,
                y_topo_barra  = topo_barra,
                pct           = byp,
                qtd           = a_b,
                cor_texto     = "white",
                offset_externo= offset_ext
            )

rotular(x_corte,  sucesso_corte,  falha_corte,  bypass_corte,
        abs_suc_corte,  abs_fal_corte,  abs_byp_corte)

rotular(x_religa, sucesso_religa, falha_religa, bypass_religa,
        abs_suc_religa, abs_fal_religa, abs_byp_religa)

# =========================================================
# 📅 DIA DA SEMANA + DATA
# =========================================================
dias_semana = {
    "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
    "Thursday": "Qui", "Friday": "Sex",
    "Saturday": "Sáb", "Sunday": "Dom"
}

labels = [
    f"{d.strftime('%d/%m')}\n{dias_semana[d.strftime('%A')]}"
    for d in datas
]

ax.set_xticks(list(x_corte) + list(x_religa))
ax.set_xticklabels(labels + labels, rotation=0)

# =========================================================
# 🎨 LAYOUT
# =========================================================
ax.set_ylim(0, LIMITE_Y)
ax.set_yticks(np.arange(0, 101, 10))
ax.set_ylabel("Percentual (%)")
ax.set_title("COPEL - COMANDOS REMOTOS", fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)

ax.axvline(n, linestyle="--", linewidth=1)

TITULO_Y = LIMITE_Y - 8

ax.text(
    (n - 1) / 2,
    TITULO_Y,
    "CORTE",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
    bbox=dict(
        facecolor="white",
        edgecolor="black",
        alpha=0.85,
        boxstyle="round,pad=0.3"
    )
)

ax.text(
    n + 1 + (n - 1) / 2,
    TITULO_Y,
    "RELIGA",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
    bbox=dict(
        facecolor="white",
        edgecolor="black",
        alpha=0.85,
        boxstyle="round,pad=0.3"
    )
)

# =========================================================
# ✅ LEGENDA
# =========================================================
ax.legend(
    handles=[
        Patch(facecolor=COR_SUCESSO, label="Sucesso"),
        Patch(facecolor=COR_FALHA,   label="Falha"),
        Patch(facecolor=COR_BYPASS,  label="Bypass"),
    ],
    ncol=3
)

plt.tight_layout()

# =========================================================
# 💾 SALVAR
# =========================================================
saida = os.path.join(PASTA_BASE, "comandos_remotos.png")
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n✅ Gráfico atualizado gerado:\n{saida}")