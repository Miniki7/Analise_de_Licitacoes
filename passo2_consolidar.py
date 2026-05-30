import json
import os
import pandas as pd

RAW_DIR = "data/raw"
OUTPUT_FILE = "data/licitacoes_final.csv"
""" 

Como rodar na sua máquina:

    Salva o arquivo passo2_consolidar.py na raiz do projeto (mesma pasta onde está a pasta data/)
    Abre o terminal nessa pasta e roda:

    python passo2_consolidar.py


O que o script faz:

    Lê todos os .json dentro de data/raw/
    Para cada licitação, percorre a lista itensVencedores e cria uma linha por item
    Junta tudo num único DataFrame com as colunas: ano, dataPublicacao, modalidade, valorEstimado, valorHomologado, descricao, valorTotalVencedor, valorUnitarioVencedor, valorUnitarioReferencia, quantidade
    Salva em data/licitacoes_final.csv

Ao final ele imprime quantas linhas foram geradas — se aparecer 20.000+ é porque funcionou direitinho. Qualquer erro que aparecer no terminal, me manda aqui!


RODEI RETORNOU



PS C:\GitHub\Analise_de_Licitacoes> python data/passo2_consolidar.py
✅ Consolidado! Total de linhas: 110675
📁 Arquivo salvo em: data/licitacoes_final.csv

Amostra:
    ano dataPublicacao         modalidade  valorEstimado  valorHomologado                                                     descricao  valorTotalVencedor  valorUnitarioVencedor  valorUnitarioReferencia  quantidade
0  2015     2015-05-14            Convite            NaN              NaN                                                       MEDALHA             16500.0                   2.75                      3.0      6000.0
1  2015     2015-05-26  Pregão presencial            NaN              NaN  Tabuleiro e Dama Gigante medindo 4x4 de Nylon, contendo 32 p             44500.0                8900.00                   9000.0         5.0
2  2015     2015-08-05  Pregão presencial            NaN              NaN                                                 KIT'S PROJETO             44578.0                  14.38                     17.0      3100.0
PS C:\GitHub\Analise_de_Licitacoes> 





Olhando o JSON, o campo valorHomologado existe sim na raiz da licitação — aparece no segundo exemplo que você mandou ("valorHomologado": 108102.21). O primeiro exemplo que você tinha mandado antes simplesmente não tinha esse campo porque era uma licitação mais simples/antiga.
Então o script precisa:

Tentar pegar valorHomologado direto da raiz
Se não existir, cair para contratos[0].valor como fallback
Executou um comando, leu um arquivoExecutou um comando, leu um arquivoO script agora tem a lógica correta:

Primeiro tenta valorHomologado direto na raiz da licitação
Se não existir (como nas licitações mais antigas/simples), usa contratos[0].valor como fallback

Ao rodar, ele também vai imprimir quantas linhas ficaram com o campo preenchido vs. vazio, então você consegue ver se ainda tem algum caso não coberto.
 
 No caso A correção acima é do caso 3
 
 """
rows = []

for filename in sorted(os.listdir(RAW_DIR)):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        licitacoes = json.load(f)

    for lic in licitacoes:
        ano = lic.get("anoLicitacao")
        modalidade = lic.get("modalidade")
        data_publicacao = lic.get("dataPublicacao")
        valor_estimado = lic.get("valorEstimado")
        valor_homologado = lic.get("valorHomologado")

        itens = lic.get("itensVencedores", [])

        for item in itens:
            rows.append({
                "ano": ano,
                "dataPublicacao": data_publicacao,
                "modalidade": modalidade,
                "valorEstimado": valor_estimado,
                "valorHomologado": valor_homologado,
                "descricao": item.get("descricao"),
                "valorTotalVencedor": item.get("valorTotalVencedor"),
                "valorUnitarioVencedor": item.get("valorUnitarioVencedor"),
                "valorUnitarioReferencia": item.get("valorUnitarioReferencia"),
                "quantidade": item.get("quantidade"),
            })

df = pd.DataFrame(rows)

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"✅ Consolidado! Total de linhas: {len(df)}")
print(f"📁 Arquivo salvo em: {OUTPUT_FILE}")
print(f"\nAmostra:")
print(df.head(3).to_string())
