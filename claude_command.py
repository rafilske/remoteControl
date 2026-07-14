import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.patches import Patch
from datetime import datetime

# =========================================================
# 🎨 CONFIGURAÇÕES GERAIS
# =========================================================
CONFIG = {
    "cor_sucesso": "#2ca02c",
    "cor_falha":   "#d62728",
    "cor_fundo":   "#f9f9f9",
    "cor_grid":    "#dddddd",
    "alpha":       0.85,
    "dpi":         300,
    "figsize":     (18, 10),
}

# =========================================================
# 📂 CAMINHOS
# =========================================================
PASTA_BASE       = r"C:\Users\nsn101555\OneDrive - nansen.com.br\Área de Trabalho\Nansen\Comandos Remotos"
ARQUIVO_EXCEL    = "comandos.xlsx"
CAMINHO_PLANILHA = os.path.join(PASTA_BASE, ARQUIVO_EXCEL)

# =========================================================
# 📅 FILTRO DE PERÍODO  ← edite aqui para filtrar datas
# =========================================================
FILTRO_DATA_INICIO = None   # Ex: "01/01/2024" ou None para sem filtro
FILTRO_DATA_FIM    = None   # Ex: "31/03/2024" ou None para sem filtro

# =========================================================
# 📊 LEITURA E PREPARAÇÃO DOS DADOS
# =========================================================
def carregar_dados(caminho: str) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df.columns = df.columns.str.strip()
    return df


def detectar_colunas(df: pd.DataFrame) -> tuple[str, str, str]:
    col_success = next(c for c in df.columns if "success rate" in c.lower())
    col_tipo    = next(c for c in df.columns if "tipo"    in c.lower() or "comando" in c.lower())
    col_data    = next(c for c in df.columns if "date"    in c.lower())
    return col_success, col_tipo, col_data


def aplicar_filtro_periodo(df: pd.DataFrame, col_data: str,
                            inicio: str | None, fim: str | None) -> pd.DataFrame:
    if inicio:
        df = df[df[col_data] >= pd.to_datetime(inicio, dayfirst=False)]
    if fim:
        df = df[df[col_data] <= pd.to_datetime(fim, dayfirst=False)]
    return df


def preparar_tabela(df: pd.DataFrame, col_data: str,
                    col_tipo: str, col_success: str) -> pd.DataFrame:
    df[col_data]   = pd.to_datetime(df[col_data], dayfirst=False, errors="coerce")
    df             = df.dropna(subset=[col_data])
    df["Status"]   = df[col_success].apply(lambda x: "Sucesso" if x > 0 else "Falha")

    tabela = (
        df.groupby([col_data, col_tipo, "Status"])
          .size()
          .unstack(fill_value=0)
    )
    tabela["Total"]    = tabela.sum(axis=1)
    tabela["Sucesso_%"] = tabela.get("Sucesso", 0) / tabela["Total"] * 100
    tabela["Falha_%"]   = tabela.get("Falha",   0) / tabela["Total"] * 100
    return tabela


def extrair_series(tabela: pd.DataFrame, datas: list, tipo: str) -> dict:
    suc_pct, fal_pct, suc_abs, fal_abs = [], [], [], []
    for data in datas:
        if (data, tipo) in tabela.index:
            linha = tabela.loc[(data, tipo)]
            suc_pct.append(linha["Sucesso_%"])
            fal_pct.append(linha["Falha_%"])
            suc_abs.append(int(linha.get("Sucesso", 0)))
            fal_abs.append(int(linha.get("Falha",   0)))
        else:
            suc_pct.append(0); fal_pct.append(0)
            suc_abs.append(0); fal_abs.append(0)
    return {"suc_pct": suc_pct, "fal_pct": fal_pct,
            "suc_abs": suc_abs, "fal_abs": fal_abs}

# =========================================================
# 🔢 RÓTULOS DAS BARRAS
# =========================================================
def rotular(ax, posicoes: np.ndarray, series: dict, cfg: dict) -> None:
    for px, suc, fal, abs_suc, abs_fal in zip(
        posicoes,
        series["suc_pct"], series["fal_pct"],
        series["suc_abs"], series["fal_abs"]
    ):
        if suc > 5:
            ax.text(px, suc / 2,
                    f"{suc:.1f}%\n({abs_suc})",
                    ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")
        if fal > 5:
            ax.text(px, suc + fal / 2,
                    f"{fal:.1f}%\n({abs_fal})",
                    ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")

# =========================================================
# 📋 TABELA RESUMO
# =========================================================
def construir_resumo(datas: list, corte: dict, religa: dict) -> pd.DataFrame:
    resumo = pd.DataFrame({
        "Data":             [d.strftime("%d/%m/%Y") for d in datas],
        "Corte – Sucesso":  corte["suc_abs"],
        "Corte – Falha":    corte["fal_abs"],
        "Corte – Total":    [s + f for s, f in zip(corte["suc_abs"], corte["fal_abs"])],
        "Corte – Taxa (%)": [f"{p:.1f}" for p in corte["suc_pct"]],
        "Religa – Sucesso": religa["suc_abs"],
        "Religa – Falha":   religa["fal_abs"],
        "Religa – Total":   [s + f for s, f in zip(religa["suc_abs"], religa["fal_abs"])],
        "Religa – Taxa (%)": [f"{p:.1f}" for p in religa["suc_pct"]],
    })

    # Linha de totais
    totais = {
        "Data":              "TOTAL",
        "Corte – Sucesso":   sum(corte["suc_abs"]),
        "Corte – Falha":     sum(corte["fal_abs"]),
        "Corte – Total":     sum(corte["suc_abs"]) + sum(corte["fal_abs"]),
        "Religa – Sucesso":  sum(religa["suc_abs"]),
        "Religa – Falha":    sum(religa["fal_abs"]),
        "Religa – Total":    sum(religa["suc_abs"]) + sum(religa["fal_abs"]),
    }
    tot_c = totais["Corte – Total"]
    tot_r = totais["Religa – Total"]
    totais["Corte – Taxa (%)"]  = f"{totais['Corte – Sucesso']  / tot_c * 100:.1f}" if tot_c else "0.0"
    totais["Religa – Taxa (%)"] = f"{totais['Religa – Sucesso'] / tot_r * 100:.1f}" if tot_r else "0.0"

    resumo = pd.concat([resumo, pd.DataFrame([totais])], ignore_index=True)
    return resumo

# =========================================================
# 📈 PLOTAGEM
# =========================================================
def plotar(datas: list, corte: dict, religa: dict, cfg: dict) -> plt.Figure:
    n = len(datas)
    x_corte  = np.arange(n)
    x_religa = np.arange(n) + n + 2
    labels   = [d.strftime("%d/%m") for d in datas]

    resumo = construir_resumo(datas, corte, religa)

    fig = plt.figure(figsize=cfg["figsize"], facecolor=cfg["cor_fundo"])
    gs  = gridspec.GridSpec(2, 1, height_ratios=[3, 1.4], hspace=0.55)

    # ------ GRÁFICO ------
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor(cfg["cor_fundo"])

    for x_pos, series, alpha in [
        (x_corte,  corte,  cfg["alpha"]),
        (x_religa, religa, cfg["alpha"]),
    ]:
        ax.bar(x_pos, series["suc_pct"],
               color=cfg["cor_sucesso"], alpha=alpha,
               edgecolor="white", linewidth=0.8)
        ax.bar(x_pos, series["fal_pct"],
               bottom=series["suc_pct"],
               color=cfg["cor_falha"], alpha=alpha,
               edgecolor="white", linewidth=0.8)
        rotular(ax, x_pos, series, cfg)

    ax.set_xticks(list(x_corte) + list(x_religa))
    ax.set_xticklabels(labels + labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_ylabel("Percentual (%)", fontsize=10)
    ax.set_title("COPEL – COMANDOS REMOTOS", fontweight="bold", fontsize=14, pad=14)
    ax.grid(axis="y", linestyle="--", color=cfg["cor_grid"], alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    sep_x = n + 0.9
    ax.axvline(sep_x, linestyle="--", linewidth=1, color="#888888")
    ax.text((n - 1) / 2,          108, "CORTE",  ha="center", fontsize=12, fontweight="bold")
    ax.text(n + 2 + (n - 1) / 2,  108, "RELIGA", ha="center", fontsize=12, fontweight="bold")

    ax.legend(handles=[
        Patch(facecolor=cfg["cor_sucesso"], label="Sucesso"),
        Patch(facecolor=cfg["cor_falha"],   label="Falha"),
    ], ncol=2, framealpha=0.5, fontsize=9)

    # ------ TABELA RESUMO ------
    ax_t = fig.add_subplot(gs[1])
    ax_t.axis("off")

    col_labels = list(resumo.columns)
    cell_data  = resumo.values.tolist()

    table = ax_t.table(
        cellText=cell_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.4)

    # Estilo do cabeçalho e linha de total
    n_rows = len(cell_data)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif row == n_rows:          # linha TOTAL
            cell.set_facecolor("#dce8f5")
            cell.set_text_props(fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f2f2f2")
        else:
            cell.set_facecolor("white")

    ax_t.set_title("Resumo por Data", fontsize=10, fontweight="bold", pad=6)

    # Período no rodapé
    periodo = (
        f"Período: {datas[0].strftime('%d/%m/%Y')} – {datas[-1].strftime('%d/%m/%Y')}"
        if datas else ""
    )
    fig.text(0.99, 0.01, periodo, ha="right", fontsize=8, color="#666666")
    fig.text(0.01, 0.01, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}",
             ha="left", fontsize=8, color="#666666")

    return fig

# =========================================================
# 🚀 EXECUÇÃO PRINCIPAL
# =========================================================
def main():
    df = carregar_dados(CAMINHO_PLANILHA)
    col_success, col_tipo, col_data = detectar_colunas(df)

    df[col_data] = pd.to_datetime(df[col_data], dayfirst=False, errors="coerce")
    df = df.dropna(subset=[col_data])
    df = aplicar_filtro_periodo(df, col_data, FILTRO_DATA_INICIO, FILTRO_DATA_FIM)

    tabela = preparar_tabela(df, col_data, col_tipo, col_success)
    datas  = sorted(tabela.index.get_level_values(0).unique())

    corte  = extrair_series(tabela, datas, "Corte")
    religa = extrair_series(tabela, datas, "Religa")

    fig = plotar(datas, corte, religa, CONFIG)

    saida_png = os.path.join(PASTA_BASE, "comandos_remotos.png")
    fig.savefig(saida_png, dpi=CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)

    saida_xlsx = os.path.join(PASTA_BASE, "resumo_comandos.xlsx")
    resumo = construir_resumo(datas, corte, religa)
    resumo.to_excel(saida_xlsx, index=False)

    print(f"\n✅ Gráfico salvo em:  {saida_png}")
    print(f"✅ Resumo salvo em:   {saida_xlsx}")


if __name__ == "__main__":
    main()