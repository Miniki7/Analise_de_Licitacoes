# ══════════════════════════════════════════════════════════════════════════════
# PASSO 9 — Padrões para Planejamento Orçamentário
# Padrão 1: Índice de desconto por ano
# Padrão 2: Itens recorrentes vs IPCA acumulado
# Padrão 3: Sazonalidade por mês de publicação
# ══════════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np

INPUT_FILE = "data/licitacoes_deflacionadas.csv"

OUT_DESCONTO     = "data/padrao1_desconto_anual.csv"
OUT_RECORRENTES  = "data/padrao2_itens_recorrentes.csv"
OUT_SAZONALIDADE = "data/padrao3_sazonalidade.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
df["dataPublicacao"] = pd.to_datetime(df["dataPublicacao"], errors="coerce")
df["mes"] = df["dataPublicacao"].dt.month
df["nomeMes"] = df["dataPublicacao"].dt.strftime("%B")

# ════════════════════════════════════════════════════════════════════════════
# PADRÃO 1 — Índice de desconto por ano
# Trabalha no nível da licitação (uma linha por licitação, não por item)
# ════════════════════════════════════════════════════════════════════════════

# Deduplica para nível de licitação (usa primeira ocorrência de cada objeto/ano)
lic = (
    df[df["situacao"].str.upper().str.strip() == "HOMOLOGADO"]
    .dropna(subset=["valorEstimado", "valorHomologado"])
    .drop_duplicates(subset=["ano", "objeto"])
    .copy()
)

lic["indice_desconto_pct"] = (
    (lic["valorEstimado"] - lic["valorHomologado"]) / lic["valorEstimado"] * 100
).round(2)

# Remove licitações com desconto inválido (valorEstimado=0 gera -inf/+inf)
# mantém mediana/min/max confiáveis; desconto_medio_pct vem do agregado
lic_valido = lic[np.isfinite(lic["indice_desconto_pct"])].copy()

desconto_anual = (
    lic_valido.groupby("ano")
    .agg(
        qtd_licitacoes        = ("objeto",            "count"),
        desconto_mediano_pct  = ("indice_desconto_pct","median"),
        desconto_min_pct      = ("indice_desconto_pct","min"),
        desconto_max_pct      = ("indice_desconto_pct","max"),
        total_estimado        = ("valorEstimado",      "sum"),
        total_homologado      = ("valorHomologado",    "sum"),
    )
    .reset_index()
)

# desconto_medio_pct pelo agregado do ano (robusto a outliers por item)
# Fórmula: (Σ estimado - Σ homologado) / Σ estimado × 100
desconto_anual["desconto_medio_pct"] = (
    (desconto_anual["total_estimado"] - desconto_anual["total_homologado"])
    / desconto_anual["total_estimado"] * 100
).round(2)

desconto_anual["desconto_mediano_pct"] = desconto_anual["desconto_mediano_pct"].round(2)
desconto_anual["economia_total"]       = (
    desconto_anual["total_estimado"] - desconto_anual["total_homologado"]
).round(2)

# Interpretação automática
media_geral = desconto_anual["desconto_medio_pct"].mean()
desvio = desconto_anual["desconto_medio_pct"].std()
estavel = desvio < 10  # considera estável se desvio padrão < 10pp

desconto_anual.to_csv(OUT_DESCONTO, index=False, encoding="utf-8-sig", sep=";")

print("=" * 65)
print("PADRÃO 1 — ÍNDICE DE DESCONTO POR ANO")
print("=" * 65)
print(desconto_anual[["ano","qtd_licitacoes","desconto_medio_pct","desconto_mediano_pct","economia_total"]].to_string(index=False))
print(f"\n  Desconto médio geral    : {media_geral:.1f}%")
print(f"  Desvio padrão           : {desvio:.1f} pp")
print(f"  Padrão estável?         : {'✅ Sim' if estavel else '⚠️ Não — alta variação entre anos'}")
if estavel:
    exemplo = 1_000_000
    gasto_provavel = exemplo * (1 - media_geral / 100)
    print(f"\n  💡 Para orçamento estimado de R$ {exemplo:,.0f},")
    print(f"     gasto real provável: R$ {gasto_provavel:,.0f} ({100-media_geral:.1f}% do estimado)")
print(f"\n📁 Salvo em: {OUT_DESCONTO}\n")


# ════════════════════════════════════════════════════════════════════════════
# PADRÃO 2 — Itens recorrentes vs IPCA acumulado
# ════════════════════════════════════════════════════════════════════════════

# Normaliza descrição para comparação
df["descricao_norm"] = df["descricao"].str.upper().str.strip()

# Itens que aparecem em pelo menos 3 anos distintos
recorrencia = (
    df.groupby("descricao_norm")["ano"]
    .nunique()
    .reset_index()
    .rename(columns={"ano": "anos_distintos"})
)
itens_recorrentes = recorrencia[recorrencia["anos_distintos"] >= 3]["descricao_norm"].tolist()

df_rec = df[df["descricao_norm"].isin(itens_recorrentes)].copy()

# Preço médio por item por ano
preco_por_ano = (
    df_rec.groupby(["descricao_norm", "ano"])
    .agg(
        preco_medio        = ("valorUnitarioVencedor",     "mean"),
        preco_medio_real   = ("valorUnitarioVencedorReal", "mean"),
        indice_acumulado   = ("indiceAcumulado",           "first"),
        qtd_ocorrencias    = ("valorUnitarioVencedor",     "count"),
    )
    .reset_index()
)

# Para cada item: compara preço no primeiro e último ano disponível
resultado_rec = []
for item, grupo in preco_por_ano.groupby("descricao_norm"):
    grupo = grupo.sort_values("ano")
    if len(grupo) < 2:
        continue
    primeiro = grupo.iloc[0]
    ultimo   = grupo.iloc[-1]

    variacao_nominal_pct = ((ultimo["preco_medio"] / primeiro["preco_medio"]) - 1) * 100
    variacao_real_pct    = ((ultimo["preco_medio_real"] / primeiro["preco_medio_real"]) - 1) * 100
    ipca_periodo = ((ultimo["indice_acumulado"] / primeiro["indice_acumulado"]) - 1) * 100

    if variacao_real_pct > 5:
        diagnostico = "⚠️ Pressão de demanda — subiu acima do IPCA"
    elif variacao_real_pct < -5:
        diagnostico = "✅ Boa gestão — ficou abaixo do IPCA"
    else:
        diagnostico = "➡️ Neutro — acompanhou o IPCA"

    resultado_rec.append({
        "descricao":            item,
        "ano_inicial":          int(primeiro["ano"]),
        "ano_final":            int(ultimo["ano"]),
        "anos_distintos":       len(grupo),
        "preco_inicial":        round(primeiro["preco_medio"], 2),
        "preco_final":          round(ultimo["preco_medio"], 2),
        "variacao_nominal_pct": round(variacao_nominal_pct, 2),
        "ipca_periodo_pct":     round(ipca_periodo, 2),
        "variacao_real_pct":    round(variacao_real_pct, 2),
        "diagnostico":          diagnostico,
    })

rec_df = pd.DataFrame(resultado_rec).sort_values("variacao_real_pct", ascending=False)
rec_df.to_csv(OUT_RECORRENTES, index=False, encoding="utf-8-sig", sep=";")

print("=" * 65)
print("PADRÃO 2 — ITENS RECORRENTES vs IPCA")
print("=" * 65)
print(f"  Total de itens recorrentes (≥3 anos): {len(rec_df)}")
pressao  = (rec_df["variacao_real_pct"] >  5).sum()
boa_gest = (rec_df["variacao_real_pct"] < -5).sum()
neutros  = len(rec_df) - pressao - boa_gest
print(f"  ⚠️  Pressão de demanda (subiram acima do IPCA): {pressao}")
print(f"  ✅  Boa gestão (ficaram abaixo do IPCA)       : {boa_gest}")
print(f"  ➡️  Neutros (acompanharam o IPCA)             : {neutros}")
print(f"\n  Top 5 com maior pressão:")
print(rec_df.head(5)[["descricao","variacao_nominal_pct","ipca_periodo_pct","variacao_real_pct","diagnostico"]].to_string(index=False))
print(f"\n📁 Salvo em: {OUT_RECORRENTES}\n")


# ════════════════════════════════════════════════════════════════════════════
# PADRÃO 3 — Sazonalidade por mês de publicação
# ════════════════════════════════════════════════════════════════════════════

nomes_meses = {
    1:"Janeiro", 2:"Fevereiro", 3:"Março",    4:"Abril",
    5:"Maio",    6:"Junho",     7:"Julho",     8:"Agosto",
    9:"Setembro",10:"Outubro",  11:"Novembro", 12:"Dezembro"
}

sazon = (
    df.dropna(subset=["mes"])
    .groupby("mes")
    .agg(
        qtd_licitacoes     = ("objeto",             "count"),
        valor_total        = ("valorTotalVencedor",  "sum"),
        valor_medio        = ("valorTotalVencedor",  "mean"),
    )
    .reset_index()
)

sazon["nome_mes"]       = sazon["mes"].map(nomes_meses)
sazon["valor_total"]    = sazon["valor_total"].round(2)
sazon["valor_medio"]    = sazon["valor_medio"].round(2)
sazon["pct_do_total"]   = (sazon["qtd_licitacoes"] / sazon["qtd_licitacoes"].sum() * 100).round(1)

# Trimestre
sazon["trimestre"] = sazon["mes"].apply(lambda m:
    "Q1 (Jan-Mar)" if m <= 3 else
    "Q2 (Abr-Jun)" if m <= 6 else
    "Q3 (Jul-Set)" if m <= 9 else
    "Q4 (Out-Dez)"
)

sazon = sazon[["mes","nome_mes","trimestre","qtd_licitacoes","pct_do_total","valor_total","valor_medio"]]
sazon.to_csv(OUT_SAZONALIDADE, index=False, encoding="utf-8-sig", sep=";")

mes_pico = sazon.loc[sazon["qtd_licitacoes"].idxmax()]
tri_group = sazon.groupby("trimestre")["qtd_licitacoes"].sum().sort_values(ascending=False)

print("=" * 65)
print("PADRÃO 3 — SAZONALIDADE POR MÊS")
print("=" * 65)
print(sazon[["nome_mes","qtd_licitacoes","pct_do_total","valor_total"]].to_string(index=False))
print(f"\n  📌 Mês com mais licitações : {mes_pico['nome_mes']} ({int(mes_pico['qtd_licitacoes'])} — {mes_pico['pct_do_total']}%)")
print(f"\n  Por trimestre:")
for tri, qtd in tri_group.items():
    pct = qtd / sazon["qtd_licitacoes"].sum() * 100
    print(f"    {tri}: {int(qtd)} licitações ({pct:.1f}%)")

q1_pct = tri_group.get("Q1 (Jan-Mar)", 0) / sazon["qtd_licitacoes"].sum() * 100
if q1_pct > 30:
    print(f"\n  ⚠️  Concentração em Q1 detectada ({q1_pct:.1f}%) — indica pico pós-aprovação orçamentária")
else:
    print(f"\n  ✅  Distribuição relativamente equilibrada ao longo do ano")

print(f"\n📁 Salvo em: {OUT_SAZONALIDADE}")
