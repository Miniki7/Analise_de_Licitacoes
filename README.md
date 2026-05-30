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
│   ├── raw/                            # JSONs brutos da API (um por ano)
│   │   ├── licitacoes_2015.json
│   │   ├── licitacoes_2016.json
│   │   └── ... até licitacoes_2025.json
│   │
│   ├── ipca_anual.csv                  # IPCA histórico por ano (2015–2025)
│   ├── licitacoes_final.csv            # Tabela consolidada (1 linha por item vencedor)
│   ├── licitacoes_com_ipca.csv         # Após JOIN com IPCA pelo ano
│   ├── licitacoes_deflacionadas.csv    # Com as 25 variáveis e valores reais deflacionados
│   ├── agregado_anual.csv              # Médias e totais por ano (base do dashboard)
│   ├── correlacoes.csv                 # Correlações de Pearson das 25 variáveis (Passo 6)
│   ├── significancia.csv               # Testes de significância com textos prontos (Passo 7)
│   ├── ols_resultado.csv               # Coeficientes da regressão OLS
│   ├── ols_resumo.txt                  # Resumo completo do modelo (R², VIF, F-stat)
│   ├── padrao1_desconto_anual.csv      # Índice de desconto por ano
│   ├── padrao2_itens_recorrentes.csv   # Itens recorrentes vs IPCA acumulado
│   ├── padrao3_sazonalidade.csv        # Sazonalidade por mês de publicação
│   ├── evolucao_valores.png            # Gráfico 1 — nominal vs real + IPCA
│   ├── correlacao_ipca.png             # Gráfico 2 — scatter IPCA vs crescimento
│   └── padroes_orcamentarios.png       # Gráfico 3 — desconto por ano
│
├── passo2_consolidar.py        # Consolida JSONs → CSV (1 linha por item)
├── passo3_join_ipca.py         # JOIN com IPCA pelo ano
├── passo4_deflacionar.py       # Calcula índice acumulado + todas as 25 variáveis
├── passo5_agregado_anual.py    # Agrega por ano (nominal e real)
├── passo6_correlacoes.py       # Correlações de Pearson (25 variáveis candidatas)
├── passo7_significancia.py     # Testes de significância + textos interpretativos
├── passo8_regressao_ols.py     # Regressão OLS + VIF
├── passo9_padroes.py           # Padrões: desconto, itens recorrentes, sazonalidade
├── passo10_graficos.py         # Gráficos PNG para apresentação
│
├── dashboard.html              # Dashboard interativo (lê os CSVs em tempo real)
├── requirements.txt
├── .gitignore
├── ANALISE.md                  # Guia de interpretação de cada arquivo gerado
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

### 3. Abrir o dashboard

O `dashboard.html` lê os CSVs diretamente — por isso precisa de um servidor local:

```bash
python -m http.server 8080
```

Depois acesse no navegador: **http://localhost:8080/dashboard.html**

> ⚠️ Não abra o arquivo com duplo clique — os CSVs não carregarão sem servidor.

---

## 📐 Metodologia

| Passo | Script | Descrição |
|-------|--------|-----------|
| 1 | — | Extração dos dados via API da prefeitura (2015–2025) |
| 2 | `passo2_consolidar.py` | Consolidação: 1 linha por item vencedor · extrai `mes`, `trimestre`, `diaDoAno` |
| 3 | `passo3_join_ipca.py` | JOIN com IPCA histórico (IBGE) pelo ano |
| 4 | `passo4_deflacionar.py` | Deflacionamento: índice acumulado base 2015 + **25 variáveis candidatas** |
| 5 | `passo5_agregado_anual.py` | Agregação anual: médias nominais e reais |
| 6 | `passo6_correlacoes.py` | Correlações de Pearson (mínimo 15 com \|r\| > 0.3) |
| 7 | `passo7_significancia.py` | Testes p-valor + textos prontos para o trabalho |
| 8 | `passo8_regressao_ols.py` | Regressão OLS com VIF e remoção de multicolinearidade |
| 9 | `passo9_padroes.py` | Padrões: desconto, itens recorrentes vs IPCA, sazonalidade |
| 10 | `passo10_graficos.py` | Gráficos PNG para apresentação |

---

## 📊 As 25 Variáveis Candidatas

### Grupo 1 — Diretas do JSON da API

| Nº | Variável | Origem |
|----|----------|--------|
| 1 | `valorUnitarioVencedor` | `itensVencedores` |
| 2 | `quantidade` | `itensVencedores` |
| 3 | `valorUnitarioReferencia` | `itensVencedores` |
| 4 | `valorEstimado` | raiz do JSON |
| 5 | `valorHomologado` | raiz do JSON |
| 6 | `ano` | `anoLicitacao` |
| 7 | `mes` | extraído de `dataPublicacao` |
| 8 | `ipca_decimal` | CSV de inflação |
| 9 | `ipca_percentual` | CSV de inflação |

### Grupo 2 — Derivadas (calculadas no Passo 4)

| Nº | Variável | Fórmula |
|----|----------|---------|
| 10 | `indiceAcumulado` | produto acumulado de (1 + ipca_decimal) desde 2015 |
| 11 | `valorTotalVencedorReal` | `valorTotalVencedor ÷ indiceAcumulado` |
| 12 | `valorTotalReferencia` | `valorUnitarioReferencia × quantidade` |
| 13 | `indiceDesconto` | `(valorEstimado − valorHomologado) ÷ valorEstimado` |
| 14 | `desvioUnitario` | `valorUnitarioVencedor − valorUnitarioReferencia` |
| 15 | `desvioUnitarioPerc` | `desvioUnitario ÷ valorUnitarioReferencia × 100` |
| 16 | `economiaTotal` | `valorTotalReferencia − valorTotalVencedor` |
| 17 | `economiaTotalPerc` | `economiaTotal ÷ valorTotalReferencia × 100` |
| 18 | `logValorTotalVencedor` | `log(valorTotalVencedor)` |
| 19 | `logQuantidade` | `log(quantidade)` |
| 20 | `logValorUnitarioVencedor` | `log(valorUnitarioVencedor)` |
| 21 | `logValorUnitarioRef` | `log(valorUnitarioReferencia)` |
| 22 | `trimestre` | extraído de `dataPublicacao` (1 a 4) |
| 23 | `diaDoAno` | extraído de `dataPublicacao` (1 a 365) |
| 24 | `quantidadeXipca` | `quantidade × ipca_decimal` |
| 25 | `valorRefXipca` | `valorUnitarioReferencia × ipca_decimal` |

---

## 📈 Principais Resultados

- **110.675 itens** analisados em 11 anos
- **Ticket médio real** cresceu +372% de 2015 a 2025 (inflação acumulada: 64,8%)
- **Desconto médio histórico** de 26,3% — regra: para R$ 1.000.000 estimado, gasto provável de R$ 737.000
- **2021** foi o ano de maior volume (15.445 itens · R$ 589M)
- **Julho** concentra o maior pico de publicações (12,4% do total anual)
- **2024** apresenta desconto atípico de 75,5% — causado por licitações de grande porte com estimativas acima do mercado

---

## 🔗 Fonte dos Dados

- **Licitações**: API pública da Prefeitura de Criciúma/SC
- **IPCA**: IBGE — Índice Nacional de Preços ao Consumidor Amplo (série histórica anual)

---

## 👥 Autores

Trabalho acadêmico — Análise de Dados Públicos
Criciúma/SC · 2025
