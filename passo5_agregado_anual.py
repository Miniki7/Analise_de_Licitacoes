import pandas as pd

INPUT_FILE  = "data/licitacoes_deflacionadas.csv"
OUTPUT_FILE = "data/agregado_anual.csv"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

agregado = df.groupby("ano").agg(
    qtd_itens            = ("valorTotalVencedor",     "count"),
    valor_total_nominal  = ("valorTotalVencedor",     "sum"),
    valor_medio_nominal  = ("valorTotalVencedor",     "mean"),
    valor_total_real     = ("valorTotalVencedorReal", "sum"),
    valor_medio_real     = ("valorTotalVencedorReal", "mean"),
    ipca_percentual      = ("ipca_percentual",        "first"),
    indiceAcumulado      = ("indiceAcumulado",        "first"),
).reset_index()

# Arredonda
for col in ["valor_total_nominal","valor_medio_nominal","valor_total_real","valor_medio_real"]:
    agregado[col] = agregado[col].round(2)

agregado.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

print(f"✅ Agregação concluída!")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\n{agregado.to_string(index=False)}")
