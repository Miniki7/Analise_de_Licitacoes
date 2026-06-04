# ══════════════════════════════════════════════════════════════════════════════
# PASSO 10 — Visualizações para a apresentação
# Gráfico 1: Evolução nominal vs real + IPCA
# Gráfico 2: Scatter IPCA vs crescimento nominal
# Gráfico 3: Índice de desconto por ano
# Gráfico 4: Valor total homologado por entidade por ano
# Gráfico 5: Sazonalidade — valor total vs quantidade por mês
# Gráfico 6: Desconto médio por modalidade ao longo dos anos
# Gráfico 7: Distribuição por tipo de objeto (requer passo2 atualizado)
# Gráfico 8: Previsão OLS 2026–2028 com intervalo de confiança e predição
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from scipy import stats

AGG_FILE        = "data/agregado_anual.csv"
DESCONTO_FILE   = "data/padrao1_desconto_anual.csv"
SAZON_FILE      = "data/padrao3_sazonalidade.csv"
LIC_FILE        = "data/licitacoes_deflacionadas.csv"
PREV_FILE       = "data/previsao_2026_2028.csv"

OUT_1 = "data/evolucao_valores.png"
OUT_2 = "data/correlacao_ipca.png"
OUT_3 = "data/padroes_orcamentarios.png"
OUT_4 = "data/gastos_por_entidade.png"
OUT_5 = "data/sazonalidade_valor_quantidade.png"
OUT_6 = "data/desconto_por_modalidade.png"
OUT_7 = "data/distribuicao_tipo_objeto.png"
OUT_8 = "data/previsao_ols_2026_2028.png"

AZUL     = "#1a6fbf"
LARANJA  = "#e07b2a"
VERDE    = "#27ae60"
ROXO     = "#8e44ad"
CINZA    = "#c8c8c8"
VERMELHO = "#c0392b"
AMARELO  = "#f39c12"
FUNDO    = "#f9f9f9"
TEXTO    = "#2c2c2c"

PALETA_ENTIDADES = [AZUL, LARANJA, VERDE, ROXO, AMARELO, "#16a085", "#c0392b", "#7f8c8d"]

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.edgecolor":   "#cccccc",
    "axes.grid":        True,
    "grid.color":       "#e5e5e5",
    "grid.linestyle":   "--",
    "grid.linewidth":   0.6,
    "figure.facecolor": FUNDO,
    "axes.facecolor":   FUNDO,
})

agg   = pd.read_csv(AGG_FILE,      sep=";", encoding="utf-8-sig")
des   = pd.read_csv(DESCONTO_FILE, sep=";", encoding="utf-8-sig")
sazon = pd.read_csv(SAZON_FILE,    sep=";", encoding="utf-8-sig")
df    = pd.read_csv(LIC_FILE,      sep=";", encoding="utf-8-sig")

anos = agg["ano"].astype(int)


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Evolução nominal vs real + IPCA ao fundo
# ════════════════════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(12, 6))

ax2 = ax1.twinx()
ax2.bar(anos, agg["ipca_percentual"], color=CINZA, alpha=0.55,
        width=0.6, label="IPCA (%)", zorder=1)
ax2.set_ylabel("IPCA anual (%)", color="#888888", fontsize=10)
ax2.tick_params(axis="y", labelcolor="#888888")
ax2.set_ylim(0, agg["ipca_percentual"].max() * 3.5)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax2.grid(False)

ax1.plot(anos, agg["valor_medio_nominal"], color=AZUL,   linewidth=2.5,
         marker="o", markersize=6, label="Valor médio nominal", zorder=3)
ax1.plot(anos, agg["valor_medio_real"],    color=LARANJA, linewidth=2.5,
         marker="s", markersize=6, linestyle="--", label="Valor médio real (deflac.)", zorder=3)

ax1.set_xlabel("Ano", fontsize=11)
ax1.set_ylabel("Valor médio por item (R$)", fontsize=11)
ax1.set_title("Evolução dos Valores de Licitações — Nominal vs Real (2015–2025)", pad=14)
ax1.set_xticks(anos)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))

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


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Índice de desconto por ano + média histórica
# ════════════════════════════════════════════════════════════════════════════
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

ax.axhline(media_hist, color=VERMELHO, linewidth=2, linestyle="--", zorder=4,
           label=f"Média histórica: {media_hist:.1f}%")

for bar, val in zip(bars, des_valido["desconto_medio_pct"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=9.5, color=TEXTO)

legend_extra = [
    Patch(color=AZUL,    label=f"Acima da média (≥ {media_hist:.1f}%)"),
    Patch(color=LARANJA, label=f"Abaixo da média (< {media_hist:.1f}%)"),
]
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles + legend_extra,
          [f"Média histórica: {media_hist:.1f}%"] + [p.get_label() for p in legend_extra],
          framealpha=0.9, loc="upper right")

ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Índice de desconto médio (%)", fontsize=11)
ax.set_title("Índice de Desconto por Ano\n(% de redução entre valor estimado e valor homologado)", pad=14)
ax.set_xticks(des["ano"].astype(int))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.set_ylim(0, des_valido["desconto_medio_pct"].max() * 1.25)

plt.tight_layout()
plt.savefig(OUT_3, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 3 salvo: {OUT_3}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 4 — Valor total homologado por entidade por ano
# ════════════════════════════════════════════════════════════════════════════
if "nomeEntidade" not in df.columns:
    print("⚠️  Gráfico 4 ignorado: coluna 'nomeEntidade' não encontrada.")
else:
    df_hom = df[df["situacao"].str.upper().str.strip() == "HOMOLOGADO"].drop_duplicates(subset=["ano","objeto"]).copy()
    ent_ano = df_hom.groupby(["ano","nomeEntidade"])["valorHomologado"].sum().reset_index()
    top_entidades = ent_ano.groupby("nomeEntidade")["valorHomologado"].sum().nlargest(6).index.tolist()
    ent_ano_top = ent_ano[ent_ano["nomeEntidade"].isin(top_entidades)].copy()
    pivot = ent_ano_top.pivot_table(index="ano",columns="nomeEntidade",values="valorHomologado",aggfunc="sum").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(pivot))
    for i, col in enumerate(pivot.columns):
        cor = PALETA_ENTIDADES[i % len(PALETA_ENTIDADES)]
        label = col.replace("PREFEITURA MUNICIPAL DE ","P.M. ").replace("FUNDAÇÃO ","FD. ").replace("MUNICIPAL ","MUN. ").title()
        ax.bar(pivot.index.astype(int), pivot[col]/1e6, bottom=bottom/1e6,
               color=cor, alpha=0.88, width=0.6, label=label, zorder=3)
        bottom += pivot[col].values

    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Valor homologado (R$ milhões)", fontsize=11)
    ax.set_title("Valor Total Homologado por Entidade\n(Top 6 entidades por volume)", pad=14)
    ax.set_xticks(pivot.index.astype(int))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:.0f}M"))
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    plt.tight_layout()
    plt.savefig(OUT_4, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Gráfico 4 salvo: {OUT_4}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 5 — Sazonalidade: valor total vs quantidade por mês
# ════════════════════════════════════════════════════════════════════════════
nomes_meses_abrev = {
    1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
    7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"
}
sazon = sazon.sort_values("mes")
sazon["nome_abrev"] = sazon["mes"].map(nomes_meses_abrev)

fig, ax1 = plt.subplots(figsize=(13, 6))
bars = ax1.bar(sazon["nome_abrev"], sazon["valor_total"]/1e6,
               color=AZUL, alpha=0.82, width=0.6, zorder=3, label="Valor total (R$ M)")
ax1.set_ylabel("Valor total homologado (R$ milhões)", fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:.0f}M"))

ax2 = ax1.twinx()
ax2.plot(sazon["nome_abrev"], sazon["qtd_licitacoes"],
         color=LARANJA, linewidth=2.5, marker="o", markersize=7, zorder=4, label="Qtd. licitações")
ax2.set_ylabel("Quantidade de licitações", color=LARANJA, fontsize=10)
ax2.tick_params(axis="y", labelcolor=LARANJA)
ax2.grid(False)

total_val = sazon["valor_total"].sum()
for bar, val in zip(bars, sazon["valor_total"]):
    pct = val / total_val * 100
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.3,
             f"{pct:.1f}%", ha="center", va="bottom", fontsize=8, color=TEXTO)

ax1.set_title("Sazonalidade das Licitações\nValor total vs Quantidade por mês", pad=14)
ax1.set_xlabel("Mês", fontsize=11)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", framealpha=0.9)

plt.tight_layout()
plt.savefig(OUT_5, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 5 salvo: {OUT_5}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 6 — Desconto médio por modalidade ao longo dos anos
# ════════════════════════════════════════════════════════════════════════════
df_hom6 = df[df["situacao"].str.upper().str.strip() == "HOMOLOGADO"].drop_duplicates(subset=["ano","objeto"]).copy()
df_hom6["indice_desconto_pct"] = (
    (df_hom6["valorEstimado"] - df_hom6["valorHomologado"])
    / df_hom6["valorEstimado"].replace(0, np.nan) * 100
)
df_hom6 = df_hom6[np.isfinite(df_hom6["indice_desconto_pct"])].copy()
top_modal = df_hom6["modalidade"].value_counts().head(4).index.tolist()
df_modal  = df_hom6[df_hom6["modalidade"].isin(top_modal)].copy()
modal_ano = df_modal.groupby(["ano","modalidade"])["indice_desconto_pct"].median().reset_index()

cores_modal = [AZUL, LARANJA, VERDE, ROXO]
fig, ax = plt.subplots(figsize=(13, 6))
for i, mod in enumerate(top_modal):
    sub = modal_ano[modal_ano["modalidade"]==mod].sort_values("ano")
    label = mod if len(mod)<=30 else mod[:28]+"…"
    ax.plot(sub["ano"].astype(int), sub["indice_desconto_pct"],
            color=cores_modal[i], linewidth=2.2, marker="o", markersize=6, label=label, zorder=3)

ax.axhline(0, color="#aaaaaa", linewidth=0.8, linestyle=":")
ax.set_xlabel("Ano", fontsize=11)
ax.set_ylabel("Desconto mediano (%)", fontsize=11)
ax.set_title("Desconto Mediano por Modalidade ao Longo dos Anos", pad=14)
ax.set_xticks(sorted(df_modal["ano"].unique()))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
plt.tight_layout()
plt.savefig(OUT_6, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico 6 salvo: {OUT_6}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 7 — Distribuição por tipo de objeto ao longo dos anos
# ════════════════════════════════════════════════════════════════════════════
if "tipoObjeto" not in df.columns:
    print("⚠️  Gráfico 7 ignorado: coluna 'tipoObjeto' não encontrada.")
else:
    df_hom7 = df[df["situacao"].str.upper().str.strip() == "HOMOLOGADO"].drop_duplicates(subset=["ano","objeto"]).copy()
    df_hom7["tipoObjeto"] = df_hom7["tipoObjeto"].str.strip().str.title()
    top_tipos = df_hom7["tipoObjeto"].value_counts().head(5).index.tolist()
    df_tipo   = df_hom7[df_hom7["tipoObjeto"].isin(top_tipos)].copy()
    tipo_ano  = df_tipo.groupby(["ano","tipoObjeto"])["valorHomologado"].sum().reset_index()
    pivot_tipo = tipo_ano.pivot_table(index="ano",columns="tipoObjeto",values="valorHomologado",aggfunc="sum").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(pivot_tipo))
    cores_tipo = [AZUL, LARANJA, VERDE, ROXO, AMARELO]
    for i, col in enumerate(pivot_tipo.columns):
        label = col if len(col)<=35 else col[:33]+"…"
        ax.bar(pivot_tipo.index.astype(int), pivot_tipo[col]/1e6, bottom=bottom/1e6,
               color=cores_tipo[i%len(cores_tipo)], alpha=0.88, width=0.6, label=label, zorder=3)
        bottom += pivot_tipo[col].values

    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Valor homologado (R$ milhões)", fontsize=11)
    ax.set_title("Valor Homologado por Tipo de Objeto ao Longo dos Anos\n(Top 5 categorias)", pad=14)
    ax.set_xticks(pivot_tipo.index.astype(int))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:.0f}M"))
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    plt.tight_layout()
    plt.savefig(OUT_7, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Gráfico 7 salvo: {OUT_7}")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 8 — Previsão OLS 2026–2028 com intervalos de confiança e predição
# ════════════════════════════════════════════════════════════════════════════
try:
    prev = pd.read_csv(PREV_FILE, sep=";", encoding="utf-8-sig")

    # Dados históricos para contexto (últimos 5 anos)
    hist = agg[agg["ano"] >= 2021][["ano","valor_medio_nominal"]].copy()

    anos_hist = hist["ano"].astype(int).tolist()
    vals_hist = hist["valor_medio_nominal"].tolist()
    anos_fut  = prev["ano"].astype(int).tolist()
    pont      = prev["previsao_pontual"].tolist()
    ic_inf    = prev["ic_confianca_inf"].tolist()
    ic_sup    = prev["ic_confianca_sup"].tolist()
    ip_inf    = prev["ip_predicao_inf"].tolist()
    ip_sup    = prev["ip_predicao_sup"].tolist()

    todos_anos = anos_hist + anos_fut

    fig, ax = plt.subplots(figsize=(13, 6))

    # Histórico
    ax.plot(anos_hist, vals_hist, color=AZUL, linewidth=2.5,
            marker="o", markersize=7, label="Histórico (nominal)", zorder=4)

    # Linha de conexão histórico → previsão (tracejada)
    ax.plot([anos_hist[-1], anos_fut[0]],
            [vals_hist[-1], pont[0]],
            color=AZUL, linewidth=1.5, linestyle=":", zorder=3)

    # Previsão pontual
    ax.plot(anos_fut, pont, color=VERDE, linewidth=2.5,
            marker="D", markersize=7, label="Previsão pontual", zorder=4)

    # Intervalo de predição (mais largo — faixa cinza)
    ax.fill_between(anos_fut, ip_inf, ip_sup,
                    alpha=0.15, color=CINZA, label="IP 95% (predição individual)")

    # Intervalo de confiança (mais estreito — faixa verde)
    ax.fill_between(anos_fut, ic_inf, ic_sup,
                    alpha=0.30, color=VERDE, label="IC 95% (valor médio)")

    # Rótulos nos pontos de previsão
    for ano, val, ci, cs in zip(anos_fut, pont, ic_inf, ic_sup):
        ax.annotate(f"R$ {val:,.0f}\n[{ci:,.0f} – {cs:,.0f}]",
                    xy=(ano, val), xytext=(0, 14), textcoords="offset points",
                    ha="center", fontsize=8.5, color=TEXTO,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", alpha=0.85))

    # Linha separadora histórico / futuro
    ax.axvline(x=2025.5, color="#aaaaaa", linewidth=1, linestyle="--", zorder=2)
    ax.text(2025.55, ax.get_ylim()[0] if ax.get_ylim()[0] > 0 else min(vals_hist)*0.85,
            "◄ Histórico   Previsão ►", fontsize=9, color="#888888")

    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("Valor médio por item (R$)", fontsize=11)
    ax.set_title("Previsão do Modelo OLS — 2026 a 2028\ncom Intervalo de Confiança e Intervalo de Predição (95%)", pad=14)
    ax.set_xticks(todos_anos)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(OUT_8, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Gráfico 8 salvo: {OUT_8}")

except FileNotFoundError:
    print("⚠️  Gráfico 8 ignorado: arquivo 'previsao_2026_2028.csv' não encontrado.")
    print("   → Rode o passo11_previsao.py antes de gerar este gráfico.")

print("\n🎨 Todos os gráficos gerados com sucesso!")
