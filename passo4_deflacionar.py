import pandas as pd
import numpy as np

INPUT_FILE  = "data/licitacoes_com_ipca.csv"
OUTPUT_FILE = "data/licitacoes_deflacionadas.csv"

# Índices acumulados desde 2015 (base = 1.0)
indices = {
    2015: 1.0000,
    2016: 1.0629,
    2017: 1.0943,
    2018: 1.1353,
    2019: 1.1842,
    2020: 1.2377,
    2021: 1.3622,
    2022: 1.4411,
    2023: 1.5077,
    2024: 1.5806,
    2025: 1.6479,
}

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

# ── VAR 10 — indiceAcumulado ───────────────────────────────────────────────────
df["indiceAcumulado"] = df["ano"].map(indices)

# ── VAR 11 — valorTotalVencedorReal ───────────────────────────────────────────
df["valorTotalVencedorReal"] = (df["valorTotalVencedor"] / df["indiceAcumulado"]).round(2)

# ── VAR 12 — valorTotalReferencia (já vem do passo 2, garante existência) ─────
# valorUnitarioReferencia × quantidade como fallback se estiver zerado
mask = df["valorTotalReferencia"].isna() | (df["valorTotalReferencia"] == 0)
df.loc[mask, "valorTotalReferencia"] = (
    df.loc[mask, "valorUnitarioReferencia"] * df.loc[mask, "quantidade"]
)

# ── VAR 13 — indiceDesconto = (valorEstimado - valorHomologado) / valorEstimado
df["indiceDesconto"] = (
    (df["valorEstimado"] - df["valorHomologado"])
    / df["valorEstimado"].replace(0, np.nan)
).round(4)

# ── VAR 14 — desvioUnitario ───────────────────────────────────────────────────
df["desvioUnitario"] = (df["valorUnitarioVencedor"] - df["valorUnitarioReferencia"]).round(4)

# ── VAR 15 — desvioUnitarioPerc ───────────────────────────────────────────────
df["desvioUnitarioPerc"] = (
    df["desvioUnitario"] / df["valorUnitarioReferencia"].replace(0, np.nan) * 100
).round(2)

# ── VAR 16 — economiaTotal ────────────────────────────────────────────────────
df["economiaTotal"] = (df["valorTotalReferencia"] - df["valorTotalVencedor"]).round(2)

# ── VAR 17 — economiaTotalPerc ────────────────────────────────────────────────
df["economiaTotalPerc"] = (
    df["economiaTotal"] / df["valorTotalReferencia"].replace(0, np.nan) * 100
).round(2)

# ── VAR 18 — logValorTotalVencedor ────────────────────────────────────────────
df["logValorTotalVencedor"] = np.log1p(df["valorTotalVencedor"].clip(lower=0)).round(4)

# ── VAR 19 — logQuantidade ────────────────────────────────────────────────────
df["logQuantidade"] = np.log1p(df["quantidade"].clip(lower=0)).round(4)

# ── VAR 20 — logValorUnitarioVencedor ─────────────────────────────────────────
df["logValorUnitarioVencedor"] = np.log1p(df["valorUnitarioVencedor"].clip(lower=0)).round(4)

# ── VAR 21 — logValorUnitarioRef ──────────────────────────────────────────────
df["logValorUnitarioRef"] = np.log1p(df["valorUnitarioReferencia"].clip(lower=0)).round(4)

# ── VAR 22 — trimestre (já vem do passo 2) ────────────────────────────────────
# Garante que existe; recalcula se necessário
if "trimestre" not in df.columns:
    df["trimestre"] = pd.to_datetime(df["dataPublicacao"], errors="coerce").dt.month.apply(
        lambda m: (m - 1) // 3 + 1 if pd.notna(m) else None
    )

# ── VAR 23 — diaDoAno (já vem do passo 2) ────────────────────────────────────
if "diaDoAno" not in df.columns:
    df["diaDoAno"] = pd.to_datetime(df["dataPublicacao"], errors="coerce").dt.day_of_year

# ── VAR 24 — quantidadeXipca ──────────────────────────────────────────────────
df["quantidadeXipca"] = (df["quantidade"] * df["ipca_decimal"]).round(4)

# ── VAR 25 — valorRefXipca ────────────────────────────────────────────────────
df["valorRefXipca"] = (df["valorUnitarioReferencia"] * df["ipca_decimal"]).round(4)

# ── Versões reais extras (úteis no OLS) ───────────────────────────────────────
df["valorUnitarioVencedorReal"]   = (df["valorUnitarioVencedor"]   / df["indiceAcumulado"]).round(2)
df["valorUnitarioReferenciaReal"] = (df["valorUnitarioReferencia"] / df["indiceAcumulado"]).round(2)
df["valorEstimadoReal"]           = (df["valorEstimado"]           / df["indiceAcumulado"]).round(2)
df["valorHomologadoReal"]         = (df["valorHomologado"]         / df["indiceAcumulado"]).round(2)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── Relatório ─────────────────────────────────────────────────────────────────
vars_25 = [
    "valorUnitarioVencedor","quantidade","valorUnitarioReferencia","valorEstimado",
    "valorHomologado","ano","mes","ipca_decimal","ipca_percentual",
    "indiceAcumulado","valorTotalVencedorReal","valorTotalReferencia",
    "indiceDesconto","desvioUnitario","desvioUnitarioPerc","economiaTotal",
    "economiaTotalPerc","logValorTotalVencedor","logQuantidade",
    "logValorUnitarioVencedor","logValorUnitarioRef","trimestre","diaDoAno",
    "quantidadeXipca","valorRefXipca",
]

print(f"✅ Deflacionamento e derivadas concluídos!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nStatus das 25 variáveis:")
for i, v in enumerate(vars_25, 1):
    status = "✅" if v in df.columns else "❌ FALTANDO"
    print(f"  {i:>2}. {v:35s} {status}")
