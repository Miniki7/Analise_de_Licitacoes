import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

INPUT_FILE  = "data/licitacoes_deflacionadas.csv"
OUTPUT_FILE = "data/correlacoes.csv"
HEATMAP_FILE = "data/heatmap_correlacoes.png"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

alvo = "valorTotalVencedor"

# ── AS VARIÁVEIS CANDIDATAS (exatamente as definidas no trabalho) ───────────
candidatas = [
    # Grupo 1 — diretas
    "valorUnitarioVencedor",        # 1
    "quantidade",                   # 2
    "valorUnitarioReferencia",      # 3
    "valorEstimado",                # 4
    "valorHomologado",              # 5
    "ano",                          # 6
    "mes",                          # 7
    "ipca_decimal",                 # 8
    "ipca_percentual",              # 9
    # Grupo 2 — derivadas (10–25)
    "indiceAcumulado",              # 10
    "valorTotalVencedorReal",       # 11
    "valorTotalReferencia",         # 12
    "indiceDesconto",               # 13
    "desvioUnitario",               # 14
    "desvioUnitarioPerc",           # 15
    "economiaTotal",                # 16
    "economiaTotalPerc",            # 17
    "logValorTotalVencedor",        # 18
    "logQuantidade",                # 19
    "logValorUnitarioVencedor",     # 20
    "logValorUnitarioRef",          # 21
    "trimestre",                    # 22
    "diaDoAno",                     # 23
    "quantidadeXipca",              # 24
    "valorRefXipca",                # 25
    # Grupo 3 — novas derivadas (26–38)
    "valorUnitario_x_qtd",          # 26
    "valorTotalReferenciaReal",     # 27
    "logValorTotalReferencia",      # 28
    "valorUnitarioCorrigido",       # 29
    "valorRefCorrigido",            # 30
    "unitVencedor_x_indice",        # 31
    "unitRef_x_indice",             # 32
    "qtd_x_unitRef",                # 33
    "qtd_x_unitCorrigido",          # 34
    "logValorUnitarioCorrigido",    # 35
    "log_qtd_x_unitRef",            # 36
    "razaoVencedorCorrigido",       # 37
    "valorEstimado_x_indice",       # 38
    # Grupo 4 — novas candidatas (39–48)
    "sqrtValorTotalVencedor",       # 39 ⚠️ vazamento
    "unitVencedor_x_qtd_real",      # 40 ⚠️ vazamento
    "valorRef_x_qtd",               # 41
    "valorRef_x_qtd_real",          # 42
    "economiaUnitaria",             # 43
    "economiaUnitaria_x_qtd",       # 44
    "valorUnit_sobre_ref",          # 45
    "valorTotal_x_ipca",            # 46 ⚠️ vazamento
    "valorTotal_squared",           # 47 ⚠️ vazamento
    "valorUnitReal_x_qtd_ipca",     # 48
]

# Confirma quais estão presentes
faltando = [v for v in candidatas if v not in df.columns]
if faltando:
    print(f"⚠️  Variáveis faltando no CSV: {faltando}")
    print("   Verifique se os passos 2, 3 e 4 foram rodados corretamente.")

candidatas = [v for v in candidatas if v in df.columns and v != alvo]

# ── CALCULAR CORRELAÇÕES ───────────────────────────────────────────────────────
resultados = []
alvo_serie = df[alvo].dropna()

for i, var in enumerate(candidatas, 1):
    serie = df[var].dropna()
    idx_comum = alvo_serie.index.intersection(serie.index)
    if len(idx_comum) < 30:
        resultados.append({
            "numero": i, "variavel": var,
            "correlacao_r": None, "p_valor": None,
            "significativa": "N/A — poucos dados",
            "bem_correlacionada": "N/A",
            "forca": "N/A", "direcao": "N/A",
        })
        continue
    x = alvo_serie.loc[idx_comum]
    y = serie.loc[idx_comum]
    if y.std() == 0:
        resultados.append({
            "numero": i, "variavel": var,
            "correlacao_r": 0.0, "p_valor": 1.0,
            "significativa": "Não ❌ (variância zero)",
            "bem_correlacionada": "Não ❌",
            "forca": "Nenhuma", "direcao": "N/A",
        })
        continue
    r, p = stats.pearsonr(x, y)
    resultados.append({
        "numero":             i,
        "variavel":           var,
        "correlacao_r":       round(r, 4),
        "p_valor":            round(p, 4),
        "significativa":      "Sim ✅" if p < 0.05 else "Não ❌",
        "bem_correlacionada": "Sim ✅" if abs(r) > 0.3 else "Não ❌",
        "forca": (
            "Forte"          if abs(r) >= 0.70 else
            "Moderada"       if abs(r) >= 0.40 else
            "Fraca-moderada" if abs(r) >= 0.30 else
            "Fraca"
        ),
        "direcao": "Positiva" if r > 0 else "Negativa",
    })

resultado_df = pd.DataFrame(resultados)
resultado_df_sorted = resultado_df.dropna(subset=["correlacao_r"]).sort_values(
    "correlacao_r", key=abs, ascending=False
)

resultado_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── RELATÓRIO ─────────────────────────────────────────────────────────────────
bem_corr = resultado_df[resultado_df["bem_correlacionada"] == "Sim ✅"]

print(f"✅ Correlações calculadas!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{'='*65}")
print(f"  Total de variáveis testadas  : {len(resultado_df)}")
print(f"  Bem correlacionadas (|r|>0.3): {len(bem_corr)}  "
      f"{'✅ REQUISITO ATINGIDO' if len(bem_corr) >= 15 else '❌ ABAIXO DE 15'}")
print(f"{'='*65}")
print(f"\n📊 RANKING POR FORÇA DE CORRELAÇÃO:")
print(resultado_df_sorted[["numero","variavel","correlacao_r","p_valor","forca","significativa","bem_correlacionada"]].to_string(index=False))

# ── HEATMAP DE CORRELAÇÃO DE PEARSON ──────────────────────────────────────────
vars_validas = resultado_df.dropna(subset=["correlacao_r"])["variavel"].tolist()
cols_heatmap = [alvo] + vars_validas
cols_heatmap = [c for c in cols_heatmap if c in df.columns]

corr_matrix = df[cols_heatmap].corr(method="pearson")

n = len(cols_heatmap)
fig_w = max(20, n * 0.55)
fig_h = max(16, n * 0.45)

fig, ax = plt.subplots(figsize=(fig_w, fig_h))

sns.heatmap(
    corr_matrix,
    ax=ax,
    annot=True,
    fmt=".2f",
    annot_kws={"size": 7},
    cmap="RdYlGn",
    vmin=-1, vmax=1,
    center=0,
    linewidths=0.4,
    linecolor="#cccccc",
    square=True,
    cbar_kws={"shrink": 0.6, "label": "Correlação de Pearson (r)"},
)

ax.set_title(
    f"Mapa de Calor — Correlação de Pearson\nalvo: {alvo}  |  {n} variáveis",
    fontsize=14, fontweight="bold", pad=18
)
ax.tick_params(axis="x", labelsize=8, rotation=45)
ax.tick_params(axis="y", labelsize=8, rotation=0)

plt.tight_layout()
plt.savefig(HEATMAP_FILE, dpi=150, bbox_inches="tight")
plt.close()

print(f"\n🖼️  Heatmap salvo em: {HEATMAP_FILE}")
""" import pandas as pd
import numpy as np
from scipy import stats

INPUT_FILE  = "data/licitacoes_deflacionadas.csv"
OUTPUT_FILE = "data/correlacoes.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

alvo = "valorTotalVencedor"

# ── AS 25 VARIÁVEIS CANDIDATAS (exatamente as definidas no trabalho) ───────────
candidatas = [
    # Grupo 1 — diretas
    "valorUnitarioVencedor",        # 1
    "quantidade",                   # 2
    "valorUnitarioReferencia",      # 3
    "valorEstimado",                # 4
    "valorHomologado",              # 5
    "ano",                          # 6
    "mes",                          # 7
    "ipca_decimal",                 # 8
    "ipca_percentual",              # 9
    # Grupo 2 — derivadas (10–25)
    "indiceAcumulado",              # 10
    "valorTotalVencedorReal",       # 11
    "valorTotalReferencia",         # 12
    "indiceDesconto",               # 13
    "desvioUnitario",               # 14
    "desvioUnitarioPerc",           # 15
    "economiaTotal",                # 16
    "economiaTotalPerc",            # 17
    "logValorTotalVencedor",        # 18
    "logQuantidade",                # 19
    "logValorUnitarioVencedor",     # 20
    "logValorUnitarioRef",          # 21
    "trimestre",                    # 22
    "diaDoAno",                     # 23
    "quantidadeXipca",              # 24
    "valorRefXipca",                # 25
    # Grupo 3 — novas derivadas (26–38)
    "valorUnitario_x_qtd",          # 26
    "valorTotalReferenciaReal",     # 27
    "logValorTotalReferencia",      # 28
    "valorUnitarioCorrigido",       # 29
    "valorRefCorrigido",            # 30
    "unitVencedor_x_indice",        # 31
    "unitRef_x_indice",             # 32
    "qtd_x_unitRef",                # 33
    "qtd_x_unitCorrigido",          # 34
    "logValorUnitarioCorrigido",    # 35
    "log_qtd_x_unitRef",            # 36
    "razaoVencedorCorrigido",       # 37
    "valorEstimado_x_indice",       # 38
    # Grupo 4 — novas candidatas (39–48)
    "sqrtValorTotalVencedor",       # 39 ⚠️ vazamento
    "unitVencedor_x_qtd_real",      # 40 ⚠️ vazamento
    "valorRef_x_qtd",               # 41
    "valorRef_x_qtd_real",          # 42
    "economiaUnitaria",             # 43
    "economiaUnitaria_x_qtd",       # 44
    "valorUnit_sobre_ref",          # 45
    "valorTotal_x_ipca",            # 46 ⚠️ vazamento
    "valorTotal_squared",           # 47 ⚠️ vazamento
    "valorUnitReal_x_qtd_ipca",     # 48
]

# Confirma quais estão presentes
faltando = [v for v in candidatas if v not in df.columns]
if faltando:
    print(f"⚠️  Variáveis faltando no CSV: {faltando}")
    print("   Verifique se os passos 2, 3 e 4 foram rodados corretamente.")

candidatas = [v for v in candidatas if v in df.columns and v != alvo]

# ── CALCULAR CORRELAÇÕES ───────────────────────────────────────────────────────
resultados = []
alvo_serie = df[alvo].dropna()

for i, var in enumerate(candidatas, 1):
    serie = df[var].dropna()
    idx_comum = alvo_serie.index.intersection(serie.index)
    if len(idx_comum) < 30:
        resultados.append({
            "numero": i, "variavel": var,
            "correlacao_r": None, "p_valor": None,
            "significativa": "N/A — poucos dados",
            "bem_correlacionada": "N/A",
            "forca": "N/A", "direcao": "N/A",
        })
        continue
    x = alvo_serie.loc[idx_comum]
    y = serie.loc[idx_comum]
    if y.std() == 0:
        resultados.append({
            "numero": i, "variavel": var,
            "correlacao_r": 0.0, "p_valor": 1.0,
            "significativa": "Não ❌ (variância zero)",
            "bem_correlacionada": "Não ❌",
            "forca": "Nenhuma", "direcao": "N/A",
        })
        continue
    r, p = stats.pearsonr(x, y)
    resultados.append({
        "numero":             i,
        "variavel":           var,
        "correlacao_r":       round(r, 4),
        "p_valor":            round(p, 4),
        "significativa":      "Sim ✅" if p < 0.05 else "Não ❌",
        "bem_correlacionada": "Sim ✅" if abs(r) > 0.3 else "Não ❌",
        "forca": (
            "Forte"          if abs(r) >= 0.70 else
            "Moderada"       if abs(r) >= 0.40 else
            "Fraca-moderada" if abs(r) >= 0.30 else
            "Fraca"
        ),
        "direcao": "Positiva" if r > 0 else "Negativa",
    })

resultado_df = pd.DataFrame(resultados)
resultado_df_sorted = resultado_df.dropna(subset=["correlacao_r"]).sort_values(
    "correlacao_r", key=abs, ascending=False
)

resultado_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── RELATÓRIO ─────────────────────────────────────────────────────────────────
bem_corr = resultado_df[resultado_df["bem_correlacionada"] == "Sim ✅"]

print(f"✅ Correlações calculadas!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{'='*65}")
print(f"  Total de variáveis testadas  : {len(resultado_df)}")
print(f"  Bem correlacionadas (|r|>0.3): {len(bem_corr)}  "
      f"{'✅ REQUISITO ATINGIDO' if len(bem_corr) >= 15 else '❌ ABAIXO DE 15'}")
print(f"{'='*65}")
print(f"\n📊 RANKING POR FORÇA DE CORRELAÇÃO:")
print(resultado_df_sorted[["numero","variavel","correlacao_r","p_valor","forca","significativa","bem_correlacionada"]].to_string(index=False))
 """