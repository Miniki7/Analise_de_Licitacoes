import json
import os
import pandas as pd

RAW_DIR = "data/raw"
OUTPUT_FILE = "data/licitacoes_final.csv"

rows = []

for filename in sorted(os.listdir(RAW_DIR)):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        licitacoes = json.load(f)

    for lic in licitacoes:
        ano              = lic.get("anoLicitacao")
        modalidade       = lic.get("modalidade")
        data_publicacao  = lic.get("dataPublicacao")
        data_homologacao = lic.get("dataHomologacao")
        objeto           = lic.get("objeto")
        situacao         = lic.get("situacao", "")

        itens = lic.get("itensVencedores", [])
        valor_estimado = sum(i.get("valorTotalReferencia") or 0 for i in itens)

        # valorHomologado só faz sentido se a licitação foi homologada
        if situacao.strip().upper() == "HOMOLOGADO":
            valor_homologado = lic.get("valorHomologado")
            if valor_homologado is None:
                contratos = lic.get("contratos", [])
                valor_homologado = contratos[0].get("valor") if contratos else None
        else:
            valor_homologado = None

        for item in itens:
            rows.append({
                "ano":                     ano,
                "dataPublicacao":          data_publicacao,
                "dataHomologacao":         data_homologacao,
                "modalidade":              modalidade,
                "situacao":                situacao,
                "objeto":                  objeto,
                "valorEstimado":           valor_estimado,
                "valorHomologado":         valor_homologado,
                "descricao":               item.get("descricao"),
                "quantidade":              item.get("quantidade"),
                "unidadeMedida":           item.get("unidadeMedida"),
                "valorUnitarioReferencia": item.get("valorUnitarioReferencia"),
                "valorUnitarioVencedor":   item.get("valorUnitarioVencedor"),
                "valorTotalVencedor":      item.get("valorTotalVencedor"),
                "vencedor":                item.get("participanteVencedor"),
                "cnpjVencedor":            item.get("cnpjCpfVencedor"),
            })

df = pd.DataFrame(rows)

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", sep=";")

print(f"✅ Consolidado! Total de linhas: {len(df)}")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nDistribuição por situação:")
print(df["situacao"].value_counts().to_string())
print(f"\nLinhas com valorHomologado preenchido: {df['valorHomologado'].notna().sum()}")
print(f"Linhas com valorHomologado vazio:      {df['valorHomologado'].isna().sum()}")
