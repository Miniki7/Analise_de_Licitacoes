import pandas as pd

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

# Adiciona coluna do índice acumulado
df["indiceAcumulado"] = df["ano"].map(indices)

# Deflaciona os valores monetários
df["valorTotalVencedorReal"]      = (df["valorTotalVencedor"]      / df["indiceAcumulado"]).round(2)
df["valorUnitarioVencedorReal"]   = (df["valorUnitarioVencedor"]   / df["indiceAcumulado"]).round(2)
df["valorUnitarioReferenciaReal"] = (df["valorUnitarioReferencia"] / df["indiceAcumulado"]).round(2)
df["valorEstimadoReal"]           = (df["valorEstimado"]           / df["indiceAcumulado"]).round(2)
df["valorHomologadoReal"]         = (df["valorHomologado"]         / df["indiceAcumulado"]).round(2)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

print(f"✅ Deflacionamento concluído! Total de linhas: {len(df)}")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nVerificação dos índices aplicados:")
print(df.groupby("ano")["indiceAcumulado"].first().to_string())
print(f"\nExemplo — mesmo item em anos diferentes (primeiros 5 registros):")
print(df[["ano","descricao","valorTotalVencedor","indiceAcumulado","valorTotalVencedorReal"]].head(5).to_string())
