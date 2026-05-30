# ══════════════════════════════════════════════════════════════════════════════
# PASSO 7 — Teste de Significância (p-valor)
#
# NOTA: O cálculo do p-valor já é realizado automaticamente no Passo 6
# (passo6_correlacoes.py), onde scipy.stats.pearsonr retorna r e p juntos.
# Este arquivo existe para documentar e apresentar os resultados de forma
# isolada, filtrando e interpretando o que foi gerado no passo anterior.
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd

INPUT_FILE  = "data/correlacoes.csv"        # gerado no passo 6
OUTPUT_FILE = "data/significancia.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

# ── CLASSIFICAÇÃO POR P-VALOR ──────────────────────────────────────────────────
df["interpretacao_p"] = df["p_valor"].apply(lambda p:
    "Muito forte (p < 0.001)" if p < 0.001 else
    "Forte (p < 0.01)"        if p < 0.010 else
    "Moderada (p < 0.05)"     if p < 0.050 else
    "Não significativa (p ≥ 0.05)"
)

# ── TEXTO DE INTERPRETAÇÃO AUTOMÁTICO ─────────────────────────────────────────
def gerar_texto(row):
    r   = row["correlacao_r"]
    p   = row["p_valor"]
    var = row["variavel"]

    if p >= 0.05:
        return (
            f"A correlação entre '{var}' e 'valorTotalVencedor' foi de "
            f"r = {r} (p = {p}), indicando que NÃO há evidência estatística "
            f"suficiente para afirmar que essa relação é real — pode ser coincidência."
        )

    abs_r = abs(r)
    if abs_r >= 0.70:
        forca = "forte"
    elif abs_r >= 0.40:
        forca = "moderada"
    else:
        forca = "fraca-moderada"

    direcao = "positiva" if r > 0 else "negativa"

    sentidos = {
        "quantidade":               "itens com maior quantidade tendem a ter maior valor total",
        "valorUnitarioVencedor":    "o preço unitário é o principal determinante do valor total pago",
        "valorTotalReferencia":     "licitações com maior referência resultam em maior valor pago",
        "indiceDesconto":           "maiores descontos estão associados a menores valores finais",
        "economiaItem":             "maior economia gerada está associada a menor valor pago",
        "razaoVencedorReferencia":  "quanto mais próximo da referência, maior o valor homologado",
        "anoNumerico":              "os valores tendem a crescer ao longo dos anos",
        "ipca_percentual":          "os valores das licitações acompanham a inflação anual",
        "indiceAcumulado":          "a inflação acumulada influencia os valores pagos ao longo do tempo",
    }
    sentido = sentidos.get(var, f"há uma relação {direcao} entre '{var}' e o valor total vencedor")

    return (
        f"A correlação entre '{var}' e 'valorTotalVencedor' foi de "
        f"r = {r} (p = {p}), indicando correlação {forca} e estatisticamente "
        f"significativa. Ou seja, {sentido}."
    )

df["texto_interpretacao"] = df.apply(gerar_texto, axis=1)

# ── SALVAR ─────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

# ── RELATÓRIO NO TERMINAL ──────────────────────────────────────────────────────
sig  = df[df["p_valor"] <  0.05]
nsig = df[df["p_valor"] >= 0.05]

print(f"✅ Análise de significância concluída!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{'='*65}")
print(f"  Variáveis significativas   (p < 0.05) : {len(sig)}")
print(f"  Variáveis NÃO significativas (p ≥ 0.05): {len(nsig)}")
print(f"{'='*65}")
print(f"\n📌 VARIÁVEIS SIGNIFICATIVAS — textos prontos para o trabalho:\n")
for _, row in sig.sort_values("correlacao_r", key=abs, ascending=False).iterrows():
    print(f"  [{row['interpretacao_p']}]")
    print(f"  {row['texto_interpretacao']}")
    print()

if len(nsig) > 0:
    print(f"⚠️  VARIÁVEIS NÃO SIGNIFICATIVAS (não usar no modelo):")
    for _, row in nsig.iterrows():
        print(f"  - {row['variavel']} (r = {row['correlacao_r']}, p = {row['p_valor']})")
