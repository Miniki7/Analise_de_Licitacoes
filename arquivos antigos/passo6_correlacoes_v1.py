import pandas as pd
import numpy as np
from scipy import stats

INPUT_FILE  = "data/licitacoes_deflacionadas.csv"
OUTPUT_FILE = "data/correlacoes.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

# ── VARIÁVEL ALVO ──────────────────────────────────────────────────────────────
alvo = "valorTotalVencedor"

# ── CRIAR VARIÁVEIS DERIVADAS ──────────────────────────────────────────────────
# Evita log de zero/negativo
df["logValorTotalVencedor"]      = np.log1p(df["valorTotalVencedor"].clip(lower=0))
df["logQuantidade"]              = np.log1p(df["quantidade"].clip(lower=0))
df["logValorUnitarioVencedor"]   = np.log1p(df["valorUnitarioVencedor"].clip(lower=0))
df["logValorUnitarioReferencia"] = np.log1p(df["valorUnitarioReferencia"].clip(lower=0))
df["logValorTotalReferencia"]    = np.log1p(df["valorTotalReferencia"].clip(lower=0))

# Índice de desconto: quanto o vencedor ficou abaixo da referência (0 a 1)
df["indiceDesconto"] = (
    (df["valorUnitarioReferencia"] - df["valorUnitarioVencedor"])
    / df["valorUnitarioReferencia"].replace(0, np.nan)
).fillna(0)

# Economia gerada no item
df["economiaItem"] = df["valorTotalReferencia"] - df["valorTotalVencedor"]

# Valor unitário × índice acumulado
df["valorUnitarioCorrigido"] = df["valorUnitarioVencedor"] * df["indiceAcumulado"]

# Razão vencedor/referência (quanto o vencedor representa da referência)
df["razaoVencedorReferencia"] = (
    df["valorTotalVencedor"] / df["valorTotalReferencia"].replace(0, np.nan)
).fillna(0)

# Dummy: ano codificado como número (tendência temporal)
df["anoNumerico"] = df["ano"].astype(int)

# Variáveis dummies de modalidade (top modalidades viram 0/1)
top_modalidades = df["modalidade"].value_counts().head(5).index
for mod in top_modalidades:
    col = "modal_" + mod.lower().replace(" ", "_").replace("ã", "a").replace("ô", "o")[:20]
    df[col] = (df["modalidade"] == mod).astype(int)

# ── LISTA DE CANDIDATAS ────────────────────────────────────────────────────────
candidatas = [
    # Originais numéricas
    "quantidade",
    "valorUnitarioVencedor",
    "valorUnitarioReferencia",
    "valorTotalReferencia",
    "valorUnitarioVencedorReal",
    "valorUnitarioReferenciaReal",
    "valorTotalVencedorReal",
    "valorEstimado",
    "valorEstimadoReal",
    "ipca_percentual",
    "ipca_decimal",
    "indiceAcumulado",
    "anoNumerico",
    # Derivadas
    "logQuantidade",
    "logValorUnitarioVencedor",
    "logValorUnitarioReferencia",
    "logValorTotalReferencia",
    "indiceDesconto",
    "economiaItem",
    "valorUnitarioCorrigido",
    "razaoVencedorReferencia",
] + [c for c in df.columns if c.startswith("modal_")]

# Remove duplicatas e a própria alvo
candidatas = [c for c in dict.fromkeys(candidatas) if c != alvo and c in df.columns]

# ── CALCULAR CORRELAÇÕES ───────────────────────────────────────────────────────
resultados = []
alvo_serie = df[alvo].dropna()

for var in candidatas:
    serie = df[var].dropna()
    idx_comum = alvo_serie.index.intersection(serie.index)
    if len(idx_comum) < 30:
        continue
    x = alvo_serie.loc[idx_comum]
    y = serie.loc[idx_comum]
    if y.std() == 0:
        continue
    r, p = stats.pearsonr(x, y)
    resultados.append({
        "variavel":         var,
        "correlacao_r":     round(r, 4),
        "p_valor":          round(p, 4),
        "significativa":    "Sim ✅" if p < 0.05 else "Não ❌",
        "bem_correlacionada": "Sim ✅" if abs(r) > 0.3 else "Não ❌",
        "forca": (
            "Forte"          if abs(r) >= 0.70 else
            "Moderada"       if abs(r) >= 0.40 else
            "Fraca-moderada" if abs(r) >= 0.30 else
            "Fraca"
        ),
        "direcao": "Positiva" if r > 0 else "Negativa",
    })

resultado_df = pd.DataFrame(resultados).sort_values("correlacao_r", key=abs, ascending=False)

# ── SALVAR ─────────────────────────────────────────────────────────────────────
resultado_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── RELATÓRIO NO TERMINAL ──────────────────────────────────────────────────────
bem_corr = resultado_df[resultado_df["bem_correlacionada"] == "Sim ✅"]
nao_corr = resultado_df[resultado_df["bem_correlacionada"] == "Não ❌"]

print(f"✅ Correlações calculadas!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{'='*65}")
print(f"  Total de variáveis testadas : {len(resultado_df)}")
print(f"  Bem correlacionadas (|r|>0.3): {len(bem_corr)}  {'✅ REQUISITO ATINGIDO' if len(bem_corr) >= 15 else '❌ ABAIXO DE 15 — criar mais variáveis'}")
print(f"{'='*65}")
print(f"\n📊 RANKING COMPLETO:")
print(resultado_df.to_string(index=False))
print(f"\n📌 BEM CORRELACIONADAS ({len(bem_corr)}):")
print(bem_corr[["variavel","correlacao_r","forca","direcao","significativa"]].to_string(index=False))
