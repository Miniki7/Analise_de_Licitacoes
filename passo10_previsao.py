# ══════════════════════════════════════════════════════════════════════════════
# PASSO 11 — Previsão do modelo OLS para intervalo futuro (2026–2028)
#
# Requisito: "Fazer a previsão para o seu modelo OLS para um intervalo futuro"
#
# Estratégia:
#   1. Recarrega o modelo OLS treinado no Passo 8 (mesmas exclusões de vazamento)
#   2. Projeta as variáveis preditoras para 2026, 2027 e 2028
#      usando tendência histórica (média móvel + crescimento anual)
#   3. Gera previsão pontual + intervalo de predição 95%
#   4. Salva resultados e imprime interpretação pronta para o trabalho
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

INPUT_FILE        = "data/licitacoes_deflacionadas.csv"
INPUT_CORRELACOES = "data/correlacoes.csv"
OUTPUT_PREVISAO   = "data/previsao_2026_2028.csv"
OUTPUT_RESUMO     = "data/previsao_resumo.txt"

# IPCA projetado para anos futuros (meta Banco Central + margem)
IPCA_FUTURO = {2026: 0.0350, 2027: 0.0325, 2028: 0.0300}

# Índices acumulados históricos
INDICES_HIST = {
    2015:1.0000, 2016:1.0629, 2017:1.0943, 2018:1.1353,
    2019:1.1842, 2020:1.2377, 2021:1.3622, 2022:1.4411,
    2023:1.5077, 2024:1.5806, 2025:1.6479,
}
# Projeta índices futuros
idx = INDICES_HIST[2025]
INDICES_FUTURO = {}
for ano, ipca in IPCA_FUTURO.items():
    idx = round(idx * (1 + ipca), 4)
    INDICES_FUTURO[ano] = idx

# ── RECARREGA DADOS E RECONSTRÓI MODELO (igual ao Passo 8) ───────────────────
df   = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
corr = pd.read_csv(INPUT_CORRELACOES, sep=";", encoding="utf-8-sig")

alvo = "valorTotalVencedor"

# Recriar variáveis derivadas
df["logQuantidade"]              = np.log1p(df["quantidade"].clip(lower=0))
df["logValorUnitarioVencedor"]   = np.log1p(df["valorUnitarioVencedor"].clip(lower=0))
df["logValorUnitarioReferencia"] = np.log1p(df["valorUnitarioReferencia"].clip(lower=0))
df["logValorTotalReferencia"]    = np.log1p(df["valorTotalReferencia"].clip(lower=0))
df["indiceDesconto"] = (
    (df["valorEstimado"] - df["valorHomologado"])
    / df["valorEstimado"].replace(0, np.nan)
).fillna(0)
df["economiaItem"] = df["valorTotalReferencia"] - df["valorTotalVencedor"]
df["valorUnitarioCorrigido"] = df["valorUnitarioVencedor"] * df["indiceAcumulado"]
df["razaoVencedorReferencia"] = (
    df["valorTotalVencedor"] / df["valorTotalReferencia"].replace(0, np.nan)
).fillna(0)
df["anoNumerico"] = df["ano"].astype(int)
top_modalidades = df["modalidade"].value_counts().head(5).index
for mod in top_modalidades:
    col = "modal_" + mod.lower().replace(" ","_").replace("ã","a").replace("ô","o")[:20]
    df[col] = (df["modalidade"] == mod).astype(int)

# ── VARIÁVEIS COM VAZAMENTO DO ALVO (idêntico ao passo 8) ────────────────────
VAZAMENTO = {
    "logValorTotalVencedor",
    "valorTotalVencedorReal",
    "sqrtValorTotalVencedor",
    "valorTotal_x_ipca",
    "valorTotal_squared",
    "valorUnitario_x_qtd",
    "qtd_x_unitCorrigido",
    "unitVencedor_x_qtd_real",
    "valorUnitReal_x_qtd_ipca",
}

REMOVER = {
    "quantidade",
    "valorUnitarioVencedor",
    "valorTotalReferencia",
    "valorUnitarioReferencia",
    "valorUnitarioVencedorReal",
    "valorUnitarioReferenciaReal",
    "valorEstimadoReal",
    "valorHomologadoReal",
    "economiaItem",
    "razaoVencedorReferencia",
    "logValorUnitarioRef",
}

excluir = VAZAMENTO | REMOVER

bem_corr   = corr[corr["bem_correlacionada"] == "Sim ✅"]["variavel"].tolist()
candidatas = [v for v in bem_corr if v in df.columns and v not in excluir and v != alvo]

df_model = df[[alvo] + candidatas].dropna()
X = df_model[candidatas].copy()
Y = df_model[alvo]

# ── REMOÇÃO ITERATIVA POR VIF (limiar = 10) — idêntico ao passo 8 ─────────────
while X.shape[1] >= 2:
    vif_iter = pd.Series(
        [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
        index=X.columns
    )
    if vif_iter.max() <= 10:
        break
    X = X.drop(columns=[vif_iter.idxmax()])

candidatas_finais = X.columns.tolist()
X_const = sm.add_constant(X)
modelo  = sm.OLS(Y, X_const).fit()

print(f"✅ Modelo OLS recarregado | R² = {modelo.rsquared:.4f} | Variáveis: {len(candidatas_finais)}")
print(f"   Variáveis no modelo: {candidatas_finais}\n")

# ── PROJETAR VARIÁVEIS PARA ANOS FUTUROS ─────────────────────────────────────
agg = df.groupby("ano")[candidatas_finais].mean().reset_index().sort_values("ano")

def projetar_valor(serie_historica, anos_hist, ano_futuro):
    ultimos = list(zip(anos_hist[-3:], serie_historica[-3:]))
    x = np.array([u[0] for u in ultimos])
    y = np.array([u[1] for u in ultimos])
    if len(x) < 2 or np.std(y) == 0:
        return float(np.mean(y))
    slope, intercept = np.polyfit(x, y, 1)
    return float(intercept + slope * ano_futuro)

anos_hist  = agg["ano"].tolist()
resultados = []

for ano_fut, ipca_dec in IPCA_FUTURO.items():
    X_fut = {}
    for var in candidatas_finais:
        if var in agg.columns:
            serie = agg[var].tolist()
            val   = projetar_valor(serie, anos_hist, ano_fut)
            if var in ["ipca_decimal", "ipca_percentual"]:
                val = ipca_dec if "decimal" in var else round(ipca_dec * 100, 2)
            if var == "indiceAcumulado":
                val = INDICES_FUTURO[ano_fut]
            if var == "anoNumerico":
                val = ano_fut
            X_fut[var] = val
        else:
            X_fut[var] = 0.0

    X_fut_df    = pd.DataFrame([X_fut])[candidatas_finais]
    X_fut_const = sm.add_constant(X_fut_df, has_constant="add")

    pred   = modelo.get_prediction(X_fut_const)
    resumo = pred.summary_frame(alpha=0.05)

    pontual  = float(resumo["mean"].iloc[0])
    ic_inf   = float(resumo["obs_ci_lower"].iloc[0])
    ic_sup   = float(resumo["obs_ci_upper"].iloc[0])
    conf_inf = float(resumo["mean_ci_lower"].iloc[0])
    conf_sup = float(resumo["mean_ci_upper"].iloc[0])

    resultados.append({
        "ano":               ano_fut,
        "ipca_projetado_pct": round(ipca_dec * 100, 2),
        "indiceAcumulado":   INDICES_FUTURO[ano_fut],
        "previsao_pontual":  round(pontual, 2),
        "ic_confianca_inf":  round(conf_inf, 2),
        "ic_confianca_sup":  round(conf_sup, 2),
        "ip_predicao_inf":   round(ic_inf, 2),
        "ip_predicao_sup":   round(ic_sup, 2),
        "amplitude_ic":      round(conf_sup - conf_inf, 2),
    })
    print(f"  {ano_fut}: Previsão = R$ {pontual:,.2f}  |  IC 95%: [R$ {conf_inf:,.2f} ; R$ {conf_sup:,.2f}]")

prev_df = pd.DataFrame(resultados)
prev_df.to_csv(OUTPUT_PREVISAO, index=False, encoding="utf-8-sig", sep=";")

# ── RELATÓRIO TEXTUAL ─────────────────────────────────────────────────────────
hist_2025 = float(df[df["ano"] == 2025][alvo].mean())

linhas = []
linhas.append("=" * 65)
linhas.append("PREVISÃO OLS — INTERVALO FUTURO 2026–2028")
linhas.append("=" * 65)
linhas.append(f"Modelo base: R² = {modelo.rsquared:.4f} ({modelo.rsquared*100:.1f}% da variação explicada)")
linhas.append(f"IPCA projetado: 2026={IPCA_FUTURO[2026]*100:.1f}%  2027={IPCA_FUTURO[2027]*100:.1f}%  2028={IPCA_FUTURO[2028]*100:.1f}%")
linhas.append(f"Referência histórica — ticket médio real 2025: R$ {hist_2025:,.2f}")
linhas.append("")
linhas.append("─" * 65)
linhas.append("RESULTADOS:")
linhas.append("─" * 65)

for r in resultados:
    cresc = ((r["previsao_pontual"] / hist_2025) - 1) * 100 if hist_2025 > 0 else 0
    linhas.append(f"\n  Ano {r['ano']}:")
    linhas.append(f"    Previsão pontual         : R$ {r['previsao_pontual']:>12,.2f}")
    linhas.append(f"    IC confiança 95%         : [R$ {r['ic_confianca_inf']:>12,.2f}  ;  R$ {r['ic_confianca_sup']:>12,.2f}]")
    linhas.append(f"    IP predição 95%          : [R$ {r['ip_predicao_inf']:>12,.2f}  ;  R$ {r['ip_predicao_sup']:>12,.2f}]")
    linhas.append(f"    Variação vs 2025         : {cresc:+.1f}%")
    linhas.append(f"    IPCA projetado           : {r['ipca_projetado_pct']}%")

linhas.append("")
linhas.append("─" * 65)
linhas.append("INTERPRETAÇÃO PARA O TRABALHO:")
linhas.append("─" * 65)
p26 = resultados[0]
p28 = resultados[2]
linhas.append(f"""
  O modelo OLS (R²={modelo.rsquared:.4f}) foi utilizado para projetar o valor médio
  por item licitado nos anos de 2026 a 2028, considerando IPCA projetado
  pelo Banco Central (meta de {IPCA_FUTURO[2026]*100:.1f}% a {IPCA_FUTURO[2028]*100:.1f}% ao ano).

  Para 2026, a previsão pontual é de R$ {p26['previsao_pontual']:,.2f} por item,
  com intervalo de confiança de 95% entre R$ {p26['ic_confianca_inf']:,.2f}
  e R$ {p26['ic_confianca_sup']:,.2f}.

  Para 2028, projeta-se R$ {p28['previsao_pontual']:,.2f} por item
  (IC 95%: R$ {p28['ic_confianca_inf']:,.2f} a R$ {p28['ic_confianca_sup']:,.2f}),
  indicando tendência de {'crescimento' if p28['previsao_pontual'] > p26['previsao_pontual'] else 'queda'} real nos valores licitados.

  Diferença entre intervalo de confiança e intervalo de predição:
  - IC de confiança: incerteza sobre o VALOR MÉDIO esperado
  - IP de predição : incerteza sobre um ITEM INDIVIDUAL futuro
    (sempre mais amplo, pois inclui variabilidade individual)
""")
linhas.append("=" * 65)

resumo_str = "\n".join(linhas)
print("\n" + resumo_str)

with open(OUTPUT_RESUMO, "w", encoding="utf-8") as f:
    f.write(resumo_str)

print(f"\n📁 Previsões salvas em : {OUTPUT_PREVISAO}")
print(f"📁 Resumo salvo em    : {OUTPUT_RESUMO}")
