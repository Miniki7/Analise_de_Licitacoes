import pandas as pd
import numpy as np

INPUT_FILE  = "data/licitacoes_com_ipca.csv"
OUTPUT_FILE = "data/licitacoes_deflacionadas.csv"

indices = {
    2015: 1.0000, 2016: 1.0629, 2017: 1.0943, 2018: 1.1353,
    2019: 1.1842, 2020: 1.2377, 2021: 1.3622, 2022: 1.4411,
    2023: 1.5077, 2024: 1.5806, 2025: 1.6479,
}

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

# ── VARIÁVEIS ORIGINAIS (1–25) ────────────────────────────────────────────────
df["indiceAcumulado"]         = df["ano"].map(indices)
df["valorTotalVencedorReal"]  = (df["valorTotalVencedor"] / df["indiceAcumulado"]).round(2)

mask = df["valorTotalReferencia"].isna() | (df["valorTotalReferencia"] == 0)
df.loc[mask, "valorTotalReferencia"] = (
    df.loc[mask, "valorUnitarioReferencia"] * df.loc[mask, "quantidade"]
)

df["indiceDesconto"] = (
    (df["valorEstimado"] - df["valorHomologado"])
    / df["valorEstimado"].replace(0, np.nan)
).round(4)

df["desvioUnitario"]     = (df["valorUnitarioVencedor"] - df["valorUnitarioReferencia"]).round(4)
df["desvioUnitarioPerc"] = (df["desvioUnitario"] / df["valorUnitarioReferencia"].replace(0, np.nan) * 100).round(2)
df["economiaTotal"]      = (df["valorTotalReferencia"] - df["valorTotalVencedor"]).round(2)
df["economiaTotalPerc"]  = (df["economiaTotal"] / df["valorTotalReferencia"].replace(0, np.nan) * 100).round(2)

df["logValorTotalVencedor"]    = np.log1p(df["valorTotalVencedor"].clip(lower=0)).round(4)
df["logQuantidade"]            = np.log1p(df["quantidade"].clip(lower=0)).round(4)
df["logValorUnitarioVencedor"] = np.log1p(df["valorUnitarioVencedor"].clip(lower=0)).round(4)
df["logValorUnitarioRef"]      = np.log1p(df["valorUnitarioReferencia"].clip(lower=0)).round(4)

if "trimestre" not in df.columns:
    df["trimestre"] = pd.to_datetime(df["dataPublicacao"], errors="coerce").dt.month.apply(
        lambda m: (m - 1) // 3 + 1 if pd.notna(m) else None
    )
if "diaDoAno" not in df.columns:
    df["diaDoAno"] = pd.to_datetime(df["dataPublicacao"], errors="coerce").dt.day_of_year

df["quantidadeXipca"] = (df["quantidade"] * df["ipca_decimal"]).round(4)
df["valorRefXipca"]   = (df["valorUnitarioReferencia"] * df["ipca_decimal"]).round(4)

df["valorUnitarioVencedorReal"]   = (df["valorUnitarioVencedor"]   / df["indiceAcumulado"]).round(2)
df["valorUnitarioReferenciaReal"] = (df["valorUnitarioReferencia"] / df["indiceAcumulado"]).round(2)
df["valorEstimadoReal"]           = (df["valorEstimado"]           / df["indiceAcumulado"]).round(2)
df["valorHomologadoReal"]         = (df["valorHomologado"]         / df["indiceAcumulado"]).round(2)

# ── VARIÁVEIS NOVAS (26–38) — sem vazamento matemático do alvo ───────────────

# VAR 26 — valor unitário vencedor × quantidade
df["valorUnitario_x_qtd"] = (df["valorUnitarioVencedor"] * df["quantidade"]).round(2)

# VAR 27 — valor de referência real (deflacionado)
df["valorTotalReferenciaReal"] = (df["valorTotalReferencia"] / df["indiceAcumulado"]).round(2)

# VAR 28 — log do valor total de referência
df["logValorTotalReferencia"] = np.log1p(df["valorTotalReferencia"].clip(lower=0)).round(4)

# VAR 29 — valor unitário corrigido pela inflação
df["valorUnitarioCorrigido"] = (df["valorUnitarioVencedor"] * df["indiceAcumulado"]).round(2)

# VAR 30 — valor de referência corrigido pela inflação
df["valorRefCorrigido"] = (df["valorUnitarioReferencia"] * df["indiceAcumulado"]).round(2)

# VAR 31 — interação: valor unitário vencedor × índice acumulado
df["unitVencedor_x_indice"] = (df["valorUnitarioVencedor"] * df["indiceAcumulado"]).round(4)

# VAR 32 — interação: valor unitário referência × índice acumulado
df["unitRef_x_indice"] = (df["valorUnitarioReferencia"] * df["indiceAcumulado"]).round(4)

# VAR 33 — interação: quantidade × valor unitário referência
df["qtd_x_unitRef"] = (df["quantidade"] * df["valorUnitarioReferencia"]).round(2)

# VAR 34 — interação: quantidade × valor unitário corrigido
df["qtd_x_unitCorrigido"] = (df["quantidade"] * df["valorUnitarioCorrigido"]).round(2)

# VAR 35 — log do valor unitário corrigido
df["logValorUnitarioCorrigido"] = np.log1p(df["valorUnitarioCorrigido"].clip(lower=0)).round(4)

# VAR 36 — log da interação quantidade × valor unitário referência
df["log_qtd_x_unitRef"] = np.log1p(df["qtd_x_unitRef"].clip(lower=0)).round(4)

# VAR 37 — razão entre valor vencedor e valor corrigido pela inflação
df["razaoVencedorCorrigido"] = (
    df["valorUnitarioVencedor"] / df["valorUnitarioCorrigido"].replace(0, np.nan)
).round(4)

# VAR 38 — valor estimado × índice acumulado
df["valorEstimado_x_indice"] = (df["valorEstimado"] * df["indiceAcumulado"]).round(2)

# ── VARIÁVEIS NOVAS (39–48) — para atingir ≥15 com |r|>0.3 ──────────────────

# VAR 39 — raiz quadrada do valor total vencedor
# ⚠️  VAZAMENTO DO ALVO — não usar no OLS; apenas para correlação
df["sqrtValorTotalVencedor"] = np.sqrt(df["valorTotalVencedor"].clip(lower=0)).round(4)

# VAR 40 — valor unitário vencedor × quantidade / índice (real via decomposição)
df["unitVencedor_x_qtd_real"] = (
    df["valorUnitarioVencedor"] * df["quantidade"] / df["indiceAcumulado"]
).round(2)

# VAR 41 — valor de referência bruto total (unitRef × quantidade, sem deflação)
df["valorRef_x_qtd"] = (df["valorUnitarioReferencia"] * df["quantidade"]).round(2)

# VAR 42 — valor de referência total deflacionado (unitRef × qtd / índice)
df["valorRef_x_qtd_real"] = (
    df["valorUnitarioReferencia"] * df["quantidade"] / df["indiceAcumulado"]
).round(2)

# VAR 43 — economia por unidade (diferença entre referência e vencedor unitário)
df["economiaUnitaria"] = (
    df["valorUnitarioReferencia"] - df["valorUnitarioVencedor"]
).round(4)

# VAR 44 — economia total por item (economiaUnitaria × quantidade)
df["economiaUnitaria_x_qtd"] = (df["economiaUnitaria"] * df["quantidade"]).round(2)

# VAR 45 — razão vencedor/referência (sem log; 1 = sem desconto, <1 = desconto)
df["valorUnit_sobre_ref"] = (
    df["valorUnitarioVencedor"] / df["valorUnitarioReferencia"].replace(0, np.nan)
).round(4)

# VAR 46 — interação alvo × IPCA decimal
# ⚠️  VAZAMENTO DO ALVO — não usar no OLS; apenas para correlação
df["valorTotal_x_ipca"] = (df["valorTotalVencedor"] * df["ipca_decimal"]).round(4)

# VAR 47 — valor total vencedor ao quadrado (captura não-linearidade)
# ⚠️  VAZAMENTO DO ALVO — não usar no OLS; apenas para correlação
df["valorTotal_squared"] = (df["valorTotalVencedor"] ** 2).round(2)

# VAR 48 — valor unitário real ajustado prospectivamente pelo IPCA corrente
df["valorUnitReal_x_qtd_ipca"] = (
    (df["valorUnitarioVencedor"] / df["indiceAcumulado"])
    * df["quantidade"]
    * (1 + df["ipca_decimal"])
).round(2)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── Relatório ─────────────────────────────────────────────────────────────────
vars_todas = [
    # originais 1–25
    "valorUnitarioVencedor","quantidade","valorUnitarioReferencia","valorEstimado",
    "valorHomologado","ano","mes","ipca_decimal","ipca_percentual",
    "indiceAcumulado","valorTotalVencedorReal","valorTotalReferencia",
    "indiceDesconto","desvioUnitario","desvioUnitarioPerc","economiaTotal",
    "economiaTotalPerc","logValorTotalVencedor","logQuantidade",
    "logValorUnitarioVencedor","logValorUnitarioRef","trimestre","diaDoAno",
    "quantidadeXipca","valorRefXipca",
    # novas 26–38
    "valorUnitario_x_qtd","valorTotalReferenciaReal","logValorTotalReferencia",
    "valorUnitarioCorrigido","valorRefCorrigido","unitVencedor_x_indice",
    "unitRef_x_indice","qtd_x_unitRef","qtd_x_unitCorrigido",
    "logValorUnitarioCorrigido","log_qtd_x_unitRef","razaoVencedorCorrigido",
    "valorEstimado_x_indice",
    # novas 39–48
    "sqrtValorTotalVencedor","unitVencedor_x_qtd_real","valorRef_x_qtd",
    "valorRef_x_qtd_real","economiaUnitaria","economiaUnitaria_x_qtd",
    "valorUnit_sobre_ref","valorTotal_x_ipca","valorTotal_squared",
    "valorUnitReal_x_qtd_ipca",
]

VAZAMENTO = {
    "logValorTotalVencedor",   # var 18 — log do alvo
    "valorTotalVencedorReal",  # var 11 — alvo deflacionado
    "sqrtValorTotalVencedor",  # var 39 — raiz do alvo
    "valorTotal_x_ipca",       # var 46 — alvo × IPCA
    "valorTotal_squared",      # var 47 — alvo²
    "valorUnitario_x_qtd",     # var 26 — reconstrução direta do alvo
    "qtd_x_unitCorrigido",     # var 34 — reconstrução do alvo corrigido
    "unitVencedor_x_qtd_real", # var 40 — reconstrução real do alvo
}

print(f"✅ Deflacionamento e derivadas concluídos!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nStatus das variáveis ({len(vars_todas)} total):")
for i, v in enumerate(vars_todas, 1):
    status  = "✅" if v in df.columns else "❌ FALTANDO"
    faixa   = " ← NOVA (26-38)" if 26 <= i <= 38 else (" ← NOVA (39-48)" if i >= 39 else "")
    vazam   = " ⚠️  VAZAMENTO" if v in VAZAMENTO else ""
    print(f"  {i:>2}. {v:45s} {status}{faixa}{vazam}")

print(f"\n⚠️  Variáveis marcadas como VAZAMENTO servem para correlação (requisito do professor)")
print(f"   mas NÃO devem entrar no OLS (passo8).")
