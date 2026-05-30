# 📊 Análise de Licitações Públicas — Criciúma/SC (2015–2025)

Projeto de análise estatística dos dados de licitações públicas do município de Criciúma/SC,
com foco em identificar padrões de variação de preços, correlação com inflação (IPCA) e
construção de um modelo preditivo via regressão OLS.

---

## 🎯 Objetivo

Investigar se os valores homologados nas licitações públicas de Criciúma acompanham,
superam ou ficam abaixo da inflação ao longo de 2015 a 2025, e identificar padrões
úteis para o planejamento orçamentário futuro.

---

## 🗂️ Estrutura do Projeto

```
projeto/
│
├── data/
│   ├── raw/                          # JSONs brutos da API (um por ano)
│   │   ├── licitacoes_2015.json
│   │   ├── licitacoes_2016.json
│   │   └── ... até licitacoes_2025.json
│   │
│   ├── ipca_anual.csv                # IPCA histórico por ano (2015–2025)
│   ├── licitacoes_final.csv          # Tabela consolidada (1 linha por item)
│   ├── licitacoes_com_ipca.csv       # Após JOIN com IPCA
│   ├── licitacoes_deflacionadas.csv  # Com índice acumulado e valores reais
│   ├── agregado_anual.csv            # Médias e totais por ano
│   ├── correlacoes.csv               # Correlações de Pearson (Passo 6)
│   ├── significancia.csv             # Testes de significância (Passo 7)
│   ├── ols_resultado.csv             # Coeficientes da regressão OLS
│   ├── ols_resumo.txt                # Resumo completo do modelo OLS
│   ├── padrao1_desconto_anual.csv    # Índice de desconto por ano
│   ├── padrao2_itens_recorrentes.csv # Itens recorrentes vs IPCA
│   ├── padrao3_sazonalidade.csv      # Sazonalidade por mês
│   ├── evolucao_valores.png          # Gráfico 1
│   ├── correlacao_ipca.png           # Gráfico 2
│   └── padroes_orcamentarios.png     # Gráfico 3
│
├── passo2_consolidar.py
├── passo3_join_ipca.py
├── passo4_deflacionar.py
├── passo5_agregado_anual.py
├── passo6_correlacoes.py
├── passo7_significancia.py
├── passo8_regressao_ols.py
├── passo9_padroes.py
├── passo10_graficos.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Como Executar

### 1. Pré-requisitos
- Python 3.9 ou superior
- Instalar dependências:

```bash
pip install -r requirements.txt
```

### 2. Ordem de execução dos scripts

> ⚠️ Os scripts dependem uns dos outros — execute **nessa ordem**.

```bash
python passo2_consolidar.py        # Consolida os JSONs em CSV
python passo3_join_ipca.py         # Cruza com o IPCA
python passo4_deflacionar.py       # Calcula índice acumulado e valores reais
python passo5_agregado_anual.py    # Agrega por ano
python passo6_correlacoes.py       # Correlações de Pearson
python passo7_significancia.py     # Testes de significância
python passo8_regressao_ols.py     # Regressão OLS
python passo9_padroes.py           # Padrões orçamentários
python passo10_graficos.py         # Gráficos para apresentação
```

> O Passo 1 (extração da API) já foi executado e os JSONs estão em `data/raw/`.

---

## 📐 Metodologia

| Passo | Descrição |
|-------|-----------|
| 1 | Extração dos dados via API da prefeitura (2015–2025) |
| 2 | Consolidação: 1 linha por item vencedor |
| 3 | JOIN com IPCA histórico (IBGE) pelo ano |
| 4 | Deflacionamento: índice acumulado base 2015 |
| 5 | Agregação anual: médias nominais e reais |
| 6 | Correlações de Pearson (25 variáveis candidatas) |
| 7 | Testes de significância estatística (p-valor < 0.05) |
| 8 | Regressão OLS com variáveis bem correlacionadas |
| 9 | Padrões: desconto, itens recorrentes, sazonalidade |
| 10 | Visualizações para apresentação |

---

## 📊 Principais Resultados Esperados

- **Evolução real dos preços**: comparação nominal vs deflacionado ao longo de 10 anos
- **Índice de desconto**: % médio de economia gerada nas licitações por ano
- **Modelo OLS**: R² e coeficientes das variáveis preditoras do valor total
- **Sazonalidade**: concentração de licitações em determinados meses
- **Itens sob pressão**: insumos cujo preço superou o IPCA acumulado

---

## 🔗 Fonte dos Dados

- **Licitações**: API pública da Prefeitura de Criciúma/SC
- **IPCA**: IBGE — Índice Nacional de Preços ao Consumidor Amplo (série histórica anual)

---

## 👥 Autores

Trabalho acadêmico — Análise de Dados Públicos  
Criciúma/SC · 2025
