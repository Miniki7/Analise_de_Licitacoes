import pandas as pd

LICITACOES_FILE = "data/licitacoes_final.csv"
IPCA_FILE       = "data/ipca_anual.csv"
OUTPUT_FILE     = "data/licitacoes_com_ipca.csv"
""" 
OS DADOS DE INFLAÇÂO FORAM RETITADOS DE
https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html?t=series-historicas&utm_source=landing&utm_medium=explica&utm_campaign=inflacao#plano-real-ano


 """
# Carrega os dois arquivos
df   = pd.read_csv(LICITACOES_FILE, sep=";", encoding="utf-8-sig")
ipca = pd.read_csv(IPCA_FILE,       sep=";", encoding="utf-8-sig")

# Garante que ano é inteiro nos dois lados
df["ano"]   = df["ano"].astype(int)
ipca["ano"] = ipca["ano"].astype(int)

# JOIN pelo ano
df_final = df.merge(ipca, on="ano", how="left")

# Salva
df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

print(f"✅ Join concluído! Total de linhas: {len(df_final)}")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nLinhas sem IPCA (anos fora do range): {df_final['ipca_percentual'].isna().sum()}")
print(f"\nIPCA por ano na base:")
print(df_final.groupby("ano")["ipca_percentual"].first().to_string())
