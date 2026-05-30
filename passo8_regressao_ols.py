# ══════════════════════════════════════════════════════════════════════════════
# PASSO 8 — Regressão OLS (Mínimos Quadrados Ordinários)
#
# Usa as variáveis bem correlacionadas (|r| > 0.3) identificadas no Passo 6.
# Remove variáveis que causam multicolinearidade (identidades matemáticas).
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

INPUT_LICITACOES = "data/licitacoes_deflacionadas.csv"
INPUT_CORRELACOES = "data/correlacoes.csv"
OUTPUT_RESULTADO  = "data/ols_resultado.csv"
OUTPUT_RESUMO     = "data/ols_resumo.txt"

# ── CARREGAR DADOS ─────────────────────────────────────────────────────────────
df   = pd.read_csv(INPUT_LICITACOES, sep=";", encoding="utf-8-sig")
corr = pd.read_csv(INPUT_CORRELACOES, sep=";", encoding="utf-8-sig")

alvo = "valorTotalVencedor"

# ── RECRIAR VARIÁVEIS DERIVADAS (mesmas do passo 6) ───────────────────────────
df["logQuantidade"]              = np.log1p(df["quantidade"].clip(lower=0))
df["logValorUnitarioVencedor"]   = np.log1p(df["valorUnitarioVencedor"].clip(lower=0))
df["logValorUnitarioReferencia"] = np.log1p(df["valorUnitarioReferencia"].clip(lower=0))
df["logValorTotalReferencia"]    = np.log1p(df["valorTotalReferencia"].clip(lower=0))
df["indiceDesconto"] = (
    (df["valorUnitarioReferencia"] - df["valorUnitarioVencedor"])
    / df["valorUnitarioReferencia"].replace(0, np.nan)
).fillna(0)
df["economiaItem"] = df["valorTotalReferencia"] - df["valorTotalVencedor"]
df["valorUnitarioCorrigido"] = df["valorUnitarioVencedor"] * df["indiceAcumulado"]
df["razaoVencedorReferencia"] = (
    df["valorTotalVencedor"] / df["valorTotalReferencia"].replace(0, np.nan)
).fillna(0)
df["anoNumerico"] = df["ano"].astype(int)
top_modalidades = df["modalidade"].value_counts().head(5).index
for mod in top_modalidades:
    col = "modal_" + mod.lower().replace(" ", "_").replace("ã","a").replace("ô","o")[:20]
    df[col] = (df["modalidade"] == mod).astype(int)

# ── SELECIONAR CANDIDATAS BEM CORRELACIONADAS (|r| > 0.3) ─────────────────────
bem_corr = corr[corr["bem_correlacionada"] == "Sim ✅"]["variavel"].tolist()

# ── REMOVER MULTICOLINEARIDADE ÓBVIA (identidades matemáticas) ────────────────
# valorTotalVencedor ≈ valorUnitarioVencedor × quantidade  → remove quantidade e unitário juntos
# valorTotalReferencia ≈ valorUnitarioReferencia × quantidade → idem
# versões "Real" são transformações lineares diretas dos nominais → remove reais
# economiaItem = valorTotalReferencia - valorTotalVencedor → colinear com referência
# logValorTotalReferencia é transformação de valorTotalReferencia → mantém só log
remover = {
    "quantidade",                  # identidade com valorUnitarioVencedor
    "valorUnitarioVencedor",       # identidade: total = unitario × qtd (mantemos log)
    "valorTotalReferencia",        # identidade com logValorTotalReferencia
    "valorUnitarioReferencia",     # identidade com logValorUnitarioReferencia
    "valorTotalVencedorReal",      # transformação linear direta do alvo
    "valorUnitarioVencedorReal",   # transformação linear de valorUnitarioVencedor
    "valorUnitarioReferenciaReal", # transformação linear de valorUnitarioReferencia
    "valorEstimadoReal",           # transformação linear de valorEstimado
    "valorHomologadoReal",         # transformação linear de valorHomologado
    "economiaItem",                # = valorTotalReferencia - alvo (vazamento)
    "razaoVencedorReferencia",     # derivada direta do alvo (vazamento)
    # ── vazamentos adicionais identificados em execução ──
    "logValorTotalVencedor",       # log do próprio alvo → vazamento direto
    "logValorUnitarioRef",         # duplicata de logValorUnitarioReferencia (nome alternativo)
}

candidatas = [v for v in bem_corr if v in df.columns and v not in remover and v != alvo]

# ── FALLBACK: se poucas variáveis passaram no filtro |r|>0.3, relaxa para |r|>0.1 ──
if len(candidatas) < 3:
    print(f"⚠️  Apenas {len(candidatas)} variável(is) com |r| > 0.3. Relaxando limiar para |r| > 0.1...")
    variaveis_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    variaveis_candidatas_fallback = [
        v for v in variaveis_numericas
        if v not in remover and v != alvo and v in df.columns
    ]
    df_temp = df[[alvo] + variaveis_candidatas_fallback].dropna()
    correlacoes_fallback = df_temp.corr()[alvo].drop(alvo).abs()
    extras = correlacoes_fallback[correlacoes_fallback > 0.1].index.tolist()
    # adiciona apenas as que ainda não estão em candidatas
    for v in extras:
        if v not in candidatas:
            candidatas.append(v)
    print(f"   → {len(candidatas)} variáveis após fallback.")

print(f"\nVariáveis selecionadas para o modelo ({len(candidatas)}):")
for v in candidatas:
    r_val = corr[corr["variavel"] == v]["correlacao_r"].values
    r_str = f"{r_val[0]:.4f}" if len(r_val) else "N/A (fallback)"
    print(f"  {v:40s}  r = {r_str}")

# ── PREPARAR MATRIX X e Y ──────────────────────────────────────────────────────
df_model = df[[alvo] + candidatas].dropna()
X = df_model[candidatas].copy()
Y = df_model[alvo]

# ── REMOÇÃO ITERATIVA POR VIF (elimina multicolinearidade residual) ───────────
# Remove a variável com maior VIF até todas ficarem abaixo de 10
print('\n── Eliminação iterativa por VIF (limiar = 10) ──')
while X.shape[1] >= 2:
    vif_iter = pd.Series(
        [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
        index=X.columns
    )
    max_vif = vif_iter.max()
    if max_vif <= 10:
        break
    remover_vif = vif_iter.idxmax()
    print(f"  Removendo '{remover_vif}' (VIF = {max_vif:.2f})")
    X = X.drop(columns=[remover_vif])

print(f'  → {X.shape[1]} variável(is) restantes após limpeza de VIF.\n')

X_const = sm.add_constant(X)

# ── RODAR OLS ──────────────────────────────────────────────────────────────────
modelo = sm.OLS(Y, X_const).fit()

# ── VIF (Variance Inflation Factor) — detecta multicolinearidade residual ──────
# VIF requer ao menos 2 variáveis preditoras para calcular correlação entre elas
if X.shape[1] >= 2:
    vif_data = pd.DataFrame({
        "variavel": X.columns,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    }).sort_values("VIF", ascending=False)
else:
    print("ℹ️  VIF não calculado: modelo com apenas 1 variável preditora (sem multicolinearidade possível).")
    vif_data = pd.DataFrame({"variavel": X.columns, "VIF": [float("nan")] * X.shape[1]})

# ── MONTAR TABELA DE COEFICIENTES ─────────────────────────────────────────────
coef_df = pd.DataFrame({
    "variavel":    modelo.params.index,
    "coeficiente": modelo.params.values.round(4),
    "erro_padrao": modelo.bse.values.round(4),
    "t_stat":      modelo.tvalues.values.round(4),
    "p_valor":     modelo.pvalues.values.round(4),
    "significativa": ["Sim ✅" if p < 0.05 else "Não ❌" for p in modelo.pvalues],
    "intervalo_inf": modelo.conf_int()[0].values.round(4),
    "intervalo_sup": modelo.conf_int()[1].values.round(4),
})

coef_df.to_csv(OUTPUT_RESULTADO, index=False, encoding="utf-8-sig", sep=";")

# ── RESUMO TEXTUAL ─────────────────────────────────────────────────────────────
resumo = []
resumo.append("=" * 65)
resumo.append("RESULTADO DA REGRESSÃO OLS")
resumo.append("=" * 65)
resumo.append(f"Variável alvo          : {alvo}")
resumo.append(f"Nº de observações      : {int(modelo.nobs)}")
resumo.append(f"Nº de variáveis        : {len(candidatas)}")
resumo.append(f"R²                     : {modelo.rsquared:.4f}  ({modelo.rsquared*100:.1f}% da variação explicada)")
resumo.append(f"R² ajustado            : {modelo.rsquared_adj:.4f}")
resumo.append(f"F-statistic            : {modelo.fvalue:.2f}  (p = {modelo.f_pvalue:.4f})")
resumo.append(f"AIC                    : {modelo.aic:.2f}")
resumo.append(f"BIC                    : {modelo.bic:.2f}")
resumo.append("")
resumo.append("─" * 65)
resumo.append("COEFICIENTES:")
resumo.append("─" * 65)
for _, row in coef_df.iterrows():
    sinal = "↑" if row["coeficiente"] > 0 else "↓"
    resumo.append(
        f"  {row['variavel']:40s}  β={row['coeficiente']:>12.4f}  "
        f"p={row['p_valor']:.4f}  {row['significativa']}  {sinal}"
    )
resumo.append("")
resumo.append("─" * 65)
resumo.append("VIF (multicolinearidade — ideal < 10):")
resumo.append("─" * 65)
for _, row in vif_data.iterrows():
    alerta = "⚠️ ALTO" if row["VIF"] > 10 else "✅ OK"
    resumo.append(f"  {row['variavel']:40s}  VIF = {row['VIF']:>8.2f}  {alerta}")
resumo.append("")
resumo.append("─" * 65)
resumo.append("INTERPRETAÇÃO GERAL:")
resumo.append("─" * 65)
r2 = modelo.rsquared
if r2 >= 0.85:
    qualidade = "excelente — o modelo explica muito bem os dados"
elif r2 >= 0.70:
    qualidade = "bom — o modelo tem boa capacidade explicativa"
elif r2 >= 0.50:
    qualidade = "moderado — o modelo captura parte da variação"
else:
    qualidade = "fraco — considere adicionar mais variáveis"
resumo.append(f"  R² = {r2:.4f} → ajuste {qualidade}.")
sig_count = (coef_df["p_valor"] < 0.05).sum() - 1  # desconta constante
resumo.append(f"  {sig_count} de {len(candidatas)} variáveis são estatisticamente significativas (p < 0.05).")
resumo.append("=" * 65)

resumo_str = "\n".join(resumo)
print(resumo_str)

with open(OUTPUT_RESUMO, "w", encoding="utf-8") as f:
    f.write(resumo_str)
    f.write("\n\n")
    f.write(modelo.summary().as_text())

print(f"\n📁 Coeficientes salvos em : {OUTPUT_RESULTADO}")
print(f"📁 Resumo completo em     : {OUTPUT_RESUMO}")
