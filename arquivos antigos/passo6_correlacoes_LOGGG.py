import pandas as pd
import numpy as np
from scipy import stats

INPUT_FILE  = "data/licitacoes_deflacionadas.csv"
OUTPUT_FILE = "data/correlacoes.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
""" 

O problema aqui é clássico: a base tem itens de R$ 5 até R$ 500.000 misturados, o que cria uma distribuição extremamente assimétrica que "esmaga" as correlações. A solução é rodar as correlações em escala logarítmica — ou seja, usar log(valorTotalVencedor) como alvo em vez do valor bruto.Editou um arquivo, executou um comando, leu um arquivoEditou um arquivo, executou um comando, leu um arquivoSubstitui o arquivo. A mudança principal foi usar log(valorTotalVencedor) como alvo das correlações em vez do valor bruto. Isso resolve o problema porque:

Com o valor bruto, um único item de R$ 500.000 distorce toda a correlação
Em escala log, a distância entre R$ 100 e R$ 1.000 é igual à distância entre R$ 1.000 e R$ 10.000 — muito mais justo para Pearson



 """
# ── VARIÁVEL ALVO ──────────────────────────────────────────────────────────────
# Usamos log(valorTotalVencedor) nas correlações para lidar com a distribuição
# extremamente assimétrica da base (itens de R$ 5 a R$ 500.000 misturados).
# A correlação de Pearson funciona muito melhor em escala logarítmica nesses casos.
alvo_original = "valorTotalVencedor"
df["logAlvo"] = np.log1p(df[alvo_original].clip(lower=0))
alvo = "logAlvo"

# ── AS 25 VARIÁVEIS CANDIDATAS ─────────────────────────────────────────────────
candidatas = [
    "valorUnitarioVencedor",    # 1
    "quantidade",               # 2
    "valorUnitarioReferencia",  # 3
    "valorEstimado",            # 4
    "valorHomologado",          # 5
    "ano",                      # 6
    "mes",                      # 7
    "ipca_decimal",             # 8
    "ipca_percentual",          # 9
    "indiceAcumulado",          # 10
    "valorTotalVencedorReal",   # 11
    "valorTotalReferencia",     # 12
    "indiceDesconto",           # 13
    "desvioUnitario",           # 14
    "desvioUnitarioPerc",       # 15
    "economiaTotal",            # 16
    "economiaTotalPerc",        # 17
    "logValorTotalVencedor",    # 18  (= log do alvo original — correlação perfeita esperada)
    "logQuantidade",            # 19
    "logValorUnitarioVencedor", # 20
    "logValorUnitarioRef",      # 21
    "trimestre",                # 22
    "diaDoAno",                 # 23
    "quantidadeXipca",          # 24
    "valorRefXipca",            # 25
]

faltando = [v for v in candidatas if v not in df.columns]
if faltando:
    print(f"⚠️  Variáveis faltando no CSV: {faltando}")

candidatas = [v for v in candidatas if v in df.columns]

# ── CALCULAR CORRELAÇÕES ───────────────────────────────────────────────────────
resultados = []
alvo_serie = df[alvo].dropna()

for i, var in enumerate(candidatas, 1):
    serie = df[var].dropna()
    idx_comum = alvo_serie.index.intersection(serie.index)
    if len(idx_comum) < 30:
        resultados.append({"numero": i, "variavel": var, "correlacao_r": None,
                           "p_valor": None, "significativa": "N/A — poucos dados",
                           "bem_correlacionada": "N/A", "forca": "N/A", "direcao": "N/A"})
        continue
    x = alvo_serie.loc[idx_comum]
    y = serie.loc[idx_comum]
    if y.std() == 0:
        resultados.append({"numero": i, "variavel": var, "correlacao_r": 0.0,
                           "p_valor": 1.0, "significativa": "Não ❌ (variância zero)",
                           "bem_correlacionada": "Não ❌", "forca": "Nenhuma", "direcao": "N/A"})
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
print(f"   (correlações medidas em relação a log(valorTotalVencedor))")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{'='*65}")
print(f"  Total de variáveis testadas  : {len(resultado_df)}")
print(f"  Bem correlacionadas (|r|>0.3): {len(bem_corr)}  "
      f"{'✅ REQUISITO ATINGIDO' if len(bem_corr) >= 15 else '❌ ABAIXO DE 15'}")
print(f"{'='*65}")
print(f"\n📊 RANKING POR FORÇA DE CORRELAÇÃO:")
print(resultado_df_sorted[["numero","variavel","correlacao_r","p_valor","forca","significativa","bem_correlacionada"]].to_string(index=False))
