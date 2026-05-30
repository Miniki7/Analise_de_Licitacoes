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

        # valorEstimado = soma dos valorTotalReferencia dos itens
        valor_estimado = sum(i.get("valorTotalReferencia") or 0 for i in itens)

        # valorHomologado: só preenche se a licitação foi homologada
        if situacao.strip().upper() == "HOMOLOGADO":
            valor_homologado = lic.get("valorHomologado")
            if valor_homologado is None:
                contratos = lic.get("contratos", [])
                valor_homologado = contratos[0].get("valor") if contratos else None
        else:
            valor_homologado = None

        # mes e trimestre e diaDoAno extraídos de dataPublicacao
        try:
            dt = pd.to_datetime(data_publicacao)
            mes       = dt.month
            trimestre = (dt.month - 1) // 3 + 1
            dia_do_ano = dt.day_of_year
        except Exception:
            mes = trimestre = dia_do_ano = None

        for item in itens:
            qtd        = item.get("quantidade") or 0
            unit_ref   = item.get("valorUnitarioReferencia") or 0
            unit_venc  = item.get("valorUnitarioVencedor") or 0
            total_ref  = item.get("valorTotalReferencia") or (unit_ref * qtd)
            total_venc = item.get("valorTotalVencedor") or 0

            rows.append({
                # ── Grupo 1 — diretas ──────────────────────────────────
                "valorUnitarioVencedor":    unit_venc,
                "quantidade":               qtd,
                "valorUnitarioReferencia":  unit_ref,
                "valorEstimado":            valor_estimado,
                "valorHomologado":          valor_homologado,
                "ano":                      ano,
                "mes":                      mes,        # var 7
                # ── Metadados extras ───────────────────────────────────
                "trimestre":                trimestre,  # var 22 (calculada)
                "diaDoAno":                 dia_do_ano, # var 23 (calculada)
                "dataPublicacao":           data_publicacao,
                "dataHomologacao":          data_homologacao,
                "modalidade":               modalidade,
                "situacao":                 situacao,
                "objeto":                   objeto,
                # ── Direto dos itens ───────────────────────────────────
                "valorTotalReferencia":     total_ref,  # var 12 base
                "valorTotalVencedor":       total_venc,
                "descricao":                item.get("descricao"),
                "unidadeMedida":            item.get("unidadeMedida"),
                "vencedor":                 item.get("participanteVencedor"),
                "cnpjVencedor":             item.get("cnpjCpfVencedor"),
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
print(f"\nColunas geradas: {list(df.columns)}")
print(f"\nAmostra:")
print(df.head(3).to_string())
