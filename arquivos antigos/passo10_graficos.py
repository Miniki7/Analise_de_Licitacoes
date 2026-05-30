# ══════════════════════════════════════════════════════════════════════════════
# PASSO 10 — Visualizações para a apresentação
# Gráfico 1: Evolução nominal vs real + IPCA
# Gráfico 2: Scatter IPCA vs crescimento nominal
# Gráfico 3: Índice de desconto por ano
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

AGG_FILE      = "data/agregado_anual.csv"
DESCONTO_FILE = "data/padrao1_desconto_anual.csv"

OUT_1 = "data/evolucao_valores.png"
OUT_2 = "data/correlacao_ipca.png"
OUT_3 = "data/padroes_orcamentarios.png"

# Paleta
AZUL    = "#1a6fbf"
LARANJA = "#e07b2a"
CINZA   = "#c8c8c8"
VERMELHO= "#c0392b"
FUNDO   = "#f9f9f9"
TEXTO   = "#2c2c2c"

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "font.size":       11,
    "axes.titlesize":  13,
    "axes.titleweight":"bold",
    "axes.edgecolor":  "#cccccc",
    "axes.grid":       True,
    "grid.color":      "#e5e5e5",
    "grid.linestyle":  "--",
    "grid.linewidth":  0.6,
    "figure.facecolor": FUNDO,
    "axes.facecolor":   FUNDO,
})

agg = pd.read_csv(AGG_FILE, sep=";", encoding="utf-8-sig")
des = pd.read_csv(DESCONTO_FILE, sep=";", encoding="utf-8-sig")

anos = agg["ano"].astype(int)

# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Evolução nominal vs real + IPCA ao fundo
# ════════════════════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(12, 6))

# Barras de IPCA no fundo (eixo secundário)
ax2 = ax1.twinx()
ax2.bar(anos, agg["ipca_percentual"], color=CINZA, alpha=0.55,
        width=0.6, label="IPCA (%)", zorder=1)
ax2.set_ylabel("IPCA anual (%)", color="#888888", fontsize=10)
ax2.tick_params(axis="y", labelcolor="#888888")
ax2.set_ylim(0, agg["ipca_percentual"].max() * 3.5)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax2.grid(False)

# Linhas no eixo principal
ax1.plot(anos, agg["valor_medio_nominal"], color=AZUL,    linewidth=2.5,
         marker="o", markersize=6, label="Valor médio nominal", zorder=3)
ax1.plot(anos, agg["valor_medio_real"],    color=LARANJA, linewidth=2.5,
         marker="s", markersize=6, linestyle="--", label="Valor médio real (deflac.)", zorder=3)

ax1.set_xlabel("Ano", fontsize=11)
ax1.set_ylabel("Valor médio por item (R$)", fontsize=11)
ax1.set_title("Evolução dos Valores de Licitações — Nominal vs Real (2015–2025)", pad=14)
ax1.set_xticks(anos)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))

# Legendas combinadas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.9)

plt.tight_layout()
plt.savefig(OUT_1, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 1 salvo: {OUT_1}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2 — Scatter IPCA vs crescimento nominal
# ════════════════════════════════════════════════════════════════════════════
agg_sorted = agg.sort_values("ano").copy()
agg_sorted["cresc_nominal_pct"] = agg_sorted["valor_medio_nominal"].pct_change() * 100
scatter = agg_sorted.dropna(subset=["cresc_nominal_pct"])

x = scatter["ipca_percentual"].values
y = scatter["cresc_nominal_pct"].values
slope, intercept, r, p, _ = stats.linregress(x, y)
x_line = np.linspace(x.min() - 0.5, x.max() + 0.5, 100)
y_line = slope * x_line + intercept

fig, ax = plt.subplots(figsize=(9, 6))

ax.scatter(x, y, color=AZUL, s=90, zorder=4, label="Ano")

# Rótulo de cada ponto
for _, row in scatter.iterrows():
    ax.annotate(str(int(row["ano"])),
                xy=(row["ipca_percentual"], row["cresc_nominal_pct"]),
                xytext=(5, 4), textcoords="offset points",
                fontsize=9, color=TEXTO)

ax.plot(x_line, y_line, color=VERMELHO, linewidth=1.8, linestyle="--",
        label=f"Tendência  r = {r:.2f}  p = {p:.3f}", zorder=3)

ax.axhline(0, color="#aaaaaa", linewidth=0.8, linestyle=":")
ax.axvline(0, color="#aaaaaa", linewidth=0.8, linestyle=":")

ax.set_xlabel("IPCA do ano (%)", fontsize=11)
ax.set_ylabel("Crescimento nominal dos valores (%)", fontsize=11)
ax.set_title("Correlação: IPCA Anual × Crescimento dos Valores de Licitações", pad=14)
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax.legend(framealpha=0.9)

plt.tight_layout()
plt.savefig(OUT_2, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 2 salvo: {OUT_2}")


""" # ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Índice de desconto por ano + média histórica
# ════════════════════════════════════════════════════════════════════════════
media_hist = des["desconto_medio_pct"].mean()

fig, ax = plt.subplots(figsize=(12, 6))

cores_barras = [AZUL if v >= media_hist else LARANJA for v in des["desconto_medio_pct"]]
bars = ax.bar(des["ano"].astype(int), des["desconto_medio_pct"],
              color=cores_barras, width=0.6, zorder=3, alpha=0.88)

# Linha da média histórica
ax.axhline(media_hist, color=VERMELHO, linewidth=2, linestyle="--", zorder=4,
           label=f"Média histórica: {media_hist:.1f}%")

# Rótulos nas barras
for bar, val in zip(bars, des["desconto_medio_pct"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=9.5, color=TEXTO)

# Legenda de cores
from matplotlib.patches import Patch
legend_extra = [
    Patch(color=AZUL,    label=f"Acima da média (≥ {media_hist:.1f}%)"),
    Patch(color=LARANJA, label=f"Abaixo da média (< {media_hist:.1f}%)"),
]
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles + legend_extra, [l for l in [f"Média histórica: {media_hist:.1f}%"] + [p.get_label() for p in legend_extra]],
          framealpha=0.9, loc="upper right")

ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Índice de desconto médio (%)", fontsize=11)
ax.set_title("Índice de Desconto por Ano\n(% de redução entre valor estimado e valor homologado)", pad=14)
ax.set_xticks(des["ano"].astype(int))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.set_ylim(0, des["desconto_medio_pct"].max() * 1.25)

plt.tight_layout()
plt.savefig(OUT_3, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 3 salvo: {OUT_3}")

print("\n🎨 Todos os gráficos gerados com sucesso!")
 """
 # ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Índice de desconto por ano + média histórica
# ════════════════════════════════════════════════════════════════════════════

# Filtra apenas anos com desconto válido (não nulo, finito e positivo)
# Anos sem licitações homologadas geram NaN/0/-inf e contaminam a média
des_valido = des[
    des["desconto_medio_pct"].notna() &
    np.isfinite(des["desconto_medio_pct"]) &
    (des["desconto_medio_pct"] > 0)
].copy()

media_hist = des_valido["desconto_medio_pct"].mean()

fig, ax = plt.subplots(figsize=(12, 6))

cores_barras = [AZUL if v >= media_hist else LARANJA for v in des_valido["desconto_medio_pct"]]
bars = ax.bar(des_valido["ano"].astype(int), des_valido["desconto_medio_pct"],
              color=cores_barras, width=0.6, zorder=3, alpha=0.88)

# Linha da média histórica
ax.axhline(media_hist, color=VERMELHO, linewidth=2, linestyle="--", zorder=4,
           label=f"Média histórica: {media_hist:.1f}%")

# Rótulos nas barras
for bar, val in zip(bars, des_valido["desconto_medio_pct"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=9.5, color=TEXTO)

# Legenda de cores
from matplotlib.patches import Patch
legend_extra = [
    Patch(color=AZUL,    label=f"Acima da média (≥ {media_hist:.1f}%)"),
    Patch(color=LARANJA, label=f"Abaixo da média (< {media_hist:.1f}%)"),
]
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles + legend_extra, [l for l in [f"Média histórica: {media_hist:.1f}%"] + [p.get_label() for p in legend_extra]],
          framealpha=0.9, loc="upper right")

ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Índice de desconto médio (%)", fontsize=11)
ax.set_title("Índice de Desconto por Ano\n(% de redução entre valor estimado e valor homologado)", pad=14)
# xticks mostra todos os anos do CSV, barras só onde há dado válido
ax.set_xticks(des["ano"].astype(int))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.set_ylim(0, des_valido["desconto_medio_pct"].max() * 1.25)

plt.tight_layout()
plt.savefig(OUT_3, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 3 salvo: {OUT_3}")

print("\n🎨 Todos os gráficos gerados com sucesso!")