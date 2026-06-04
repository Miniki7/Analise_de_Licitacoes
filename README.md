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
│   ├── raw/                              # JSONs brutos da API (um por ano)
│   │   ├── licitacoes_2015.json
│   │   ├── licitacoes_2016.json
│   │   └── ... até licitacoes_2025.json
│   │
│   ├── graficos/                         # Gráficos PNG gerados pelo passo10 (criada automaticamente)
│   │   ├── evolucao_valores.png
│   │   ├── correlacao_ipca.png
│   │   ├── padroes_orcamentarios.png
│   │   ├── gastos_por_entidade.png
│   │   ├── sazonalidade_valor_quantidade.png
│   │   ├── desconto_por_modalidade.png
│   │   ├── distribuicao_tipo_objeto.png
│   │   └── previsao_ols_2026_2028.png
│   │
│   ├── ipca_anual.csv                    # IPCA histórico por ano (2015–2025) ⚠️ NÃO APAGAR
│   ├── licitacoes_final.csv              # Tabela consolidada (1 linha por item vencedor)
│   ├── licitacoes_com_ipca.csv           # Após JOIN com IPCA pelo ano
│   ├── licitacoes_deflacionadas.csv      # Com as 48 variáveis derivadas
│   ├── agregado_anual.csv                # Médias e totais por ano (base do dashboard)
│   ├── correlacoes.csv                   # Correlações de Pearson das 48 variáveis
│   ├── significancia.csv                 # Testes de significância com textos prontos
│   ├── ols_resultado.csv                 # Coeficientes da regressão OLS
│   ├── ols_resumo.txt                    # Resumo completo do modelo (R², VIF, F-stat)
│   ├── padrao1_desconto_anual.csv        # Índice de desconto por ano
│   ├── padrao2_itens_recorrentes.csv     # Itens recorrentes vs IPCA acumulado
│   ├── padrao3_sazonalidade.csv          # Sazonalidade por mês de publicação
│   └── previsao_2026_2028.csv            # Previsão OLS com intervalos de confiança
│
├── passo2_consolidar.py        # Consolida JSONs → CSV (1 linha por item)
├── passo3_join_ipca.py         # JOIN com IPCA pelo ano
├── passo4_deflacionar.py       # Calcula índice acumulado + todas as 48 variáveis
├── passo5_agregado_anual.py    # Agrega por ano (nominal e real)
├── passo6_correlacoes.py       # Correlações de Pearson (48 variáveis candidatas)
├── passo7_significancia.py     # Testes de significância + textos interpretativos
├── passo8_regressao_ols.py     # Regressão OLS + VIF
├── passo9_padroes.py           # Padrões: desconto, itens recorrentes, sazonalidade
├── passo10_graficos.py         # Gráficos PNG → salvos em data/graficos/
├── passo11_previsao.py         # Previsão OLS 2026–2028 com intervalos
├── passo12_estimativas.py      # Estimativas pontuais e intervalares
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

### 2. Criar e ativar o ambiente virtual

Antes de instalar qualquer dependência, crie um ambiente virtual para isolar o projeto:

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Após ativar, você verá `(venv)` no início do terminal, confirmando que o ambiente está ativo.
> Para desativar quando terminar, execute `deactivate`.

### 3. Instalar dependências

Com o ambiente virtual **ativo**:

```bash
pip install -r requirements.txt
```

> ⚠️ Não pule o passo do ambiente virtual — instalar sem ele pode conflitar com pacotes do sistema.

### 4. Ordem de execução dos scripts

Execute **um por vez**, nessa ordem, aguardando cada um terminar antes de rodar o próximo:

```bash
python passo2_consolidar.py        # Consolida os JSONs em CSV
python passo3_join_ipca.py         # Cruza com o IPCA
python passo4_deflacionar.py       # Calcula índice acumulado e 48 variáveis derivadas
python passo5_agregado_anual.py    # Agrega por ano
python passo6_correlacoes.py       # Correlações de Pearson
python passo7_significancia.py     # Testes de significância
python passo8_regressao_ols.py     # Regressão OLS
python passo9_padroes.py           # Padrões orçamentários
python passo10_graficos.py         # Gráficos → salvos em data/graficos/
python passo11_previsao.py         # Previsão 2026–2028 com intervalos
python passo12_estimativas.py      # Estimativas pontuais e intervalares
```

> O Passo 1 (extração da API) já foi executado e os JSONs estão em `data/raw/`.

### 5. Regenerar os arquivos do zero

Caso queira reprocessar tudo do início, os únicos arquivos/pastas que precisam ser preservados são:

```
data/
├── raw/            ← JSONs brutos da API — NÃO APAGAR
├── ipca_anual.csv  ← IPCA histórico manual — NÃO APAGAR
└── graficos/       ← criada automaticamente pelo passo10, pode apagar se quiser
```

Todos os demais CSVs e PNGs são gerados automaticamente ao rodar os passos em ordem.

### 6. Abrir o dashboard

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
| 4 | `passo4_deflacionar.py` | Deflacionamento: índice acumulado base 2015 + **48 variáveis candidatas** |
| 5 | `passo5_agregado_anual.py` | Agregação anual: médias nominais e reais |
| 6 | `passo6_correlacoes.py` | Correlações de Pearson — **20 variáveis com \|r\| > 0.3** (mínimo exigido: 15) |
| 7 | `passo7_significancia.py` | Testes p-valor + textos prontos para o trabalho |
| 8 | `passo8_regressao_ols.py` | Regressão OLS com VIF e remoção iterativa de multicolinearidade |
| 9 | `passo9_padroes.py` | Padrões: desconto, itens recorrentes vs IPCA, sazonalidade |
| 10 | `passo10_graficos.py` | 8 gráficos PNG salvos em `data/graficos/` |
| 11 | `passo11_previsao.py` | Previsão OLS 2026–2028 com intervalos de confiança e predição |
| 12 | `passo12_estimativas.py` | Estimativas pontuais (x̄) e intervalares (IC 90/95/99%) |

---

## 📊 As 48 Variáveis Candidatas

### Grupo 1 — Diretas do JSON da API (1–9)

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

### Grupo 2 — Derivadas clássicas (10–25)

| Nº | Variável | Fórmula |
|----|----------|---------|
| 10 | `indiceAcumulado` | produto acumulado de (1 + ipca) desde 2015 |
| 11 | `valorTotalVencedorReal` | `valorTotalVencedor ÷ indiceAcumulado` |
| 12 | `valorTotalReferencia` | `valorUnitarioReferencia × quantidade` |
| 13 | `indiceDesconto` | `(valorEstimado − valorHomologado) ÷ valorEstimado` |
| 14 | `desvioUnitario` | `valorUnitarioVencedor − valorUnitarioReferencia` |
| 15 | `desvioUnitarioPerc` | `desvioUnitario ÷ valorUnitarioReferencia × 100` |
| 16 | `economiaTotal` | `valorTotalReferencia − valorTotalVencedor` |
| 17 | `economiaTotalPerc` | `economiaTotal ÷ valorTotalReferencia × 100` |
| 18 | `logValorTotalVencedor` | `log1p(valorTotalVencedor)` ⚠️ vazamento |
| 19 | `logQuantidade` | `log1p(quantidade)` |
| 20 | `logValorUnitarioVencedor` | `log1p(valorUnitarioVencedor)` |
| 21 | `logValorUnitarioRef` | `log1p(valorUnitarioReferencia)` |
| 22 | `trimestre` | extraído de `dataPublicacao` (1 a 4) |
| 23 | `diaDoAno` | extraído de `dataPublicacao` (1 a 365) |
| 24 | `quantidadeXipca` | `quantidade × ipca_decimal` |
| 25 | `valorRefXipca` | `valorUnitarioReferencia × ipca_decimal` |

### Grupo 3 — Novas derivadas com deflação e interações (26–38)

| Nº | Variável | Fórmula |
|----|----------|---------|
| 26 | `valorUnitario_x_qtd` | `valorUnitarioVencedor × quantidade` ⚠️ vazamento |
| 27 | `valorTotalReferenciaReal` | `valorTotalReferencia ÷ indiceAcumulado` |
| 28 | `logValorTotalReferencia` | `log1p(valorTotalReferencia)` |
| 29 | `valorUnitarioCorrigido` | `valorUnitarioVencedor × indiceAcumulado` |
| 30 | `valorRefCorrigido` | `valorUnitarioReferencia × indiceAcumulado` |
| 31 | `unitVencedor_x_indice` | `valorUnitarioVencedor × indiceAcumulado` |
| 32 | `unitRef_x_indice` | `valorUnitarioReferencia × indiceAcumulado` |
| 33 | `qtd_x_unitRef` | `quantidade × valorUnitarioReferencia` |
| 34 | `qtd_x_unitCorrigido` | `quantidade × valorUnitarioCorrigido` ⚠️ vazamento |
| 35 | `logValorUnitarioCorrigido` | `log1p(valorUnitarioCorrigido)` |
| 36 | `log_qtd_x_unitRef` | `log1p(qtd_x_unitRef)` |
| 37 | `razaoVencedorCorrigido` | `valorUnitarioVencedor ÷ valorUnitarioCorrigido` |
| 38 | `valorEstimado_x_indice` | `valorEstimado × indiceAcumulado` |

### Grupo 4 — Novas candidatas para atingir ≥ 15 com |r| > 0.3 (39–48)

| Nº | Variável | Fórmula |
|----|----------|---------|
| 39 | `sqrtValorTotalVencedor` | `√valorTotalVencedor` ⚠️ vazamento |
| 40 | `unitVencedor_x_qtd_real` | `valorUnitarioVencedor × quantidade ÷ indiceAcumulado` ⚠️ vazamento |
| 41 | `valorRef_x_qtd` | `valorUnitarioReferencia × quantidade` |
| 42 | `valorRef_x_qtd_real` | `valorUnitarioReferencia × quantidade ÷ indiceAcumulado` |
| 43 | `economiaUnitaria` | `valorUnitarioReferencia − valorUnitarioVencedor` |
| 44 | `economiaUnitaria_x_qtd` | `economiaUnitaria × quantidade` |
| 45 | `valorUnit_sobre_ref` | `valorUnitarioVencedor ÷ valorUnitarioReferencia` |
| 46 | `valorTotal_x_ipca` | `valorTotalVencedor × ipca_decimal` ⚠️ vazamento |
| 47 | `valorTotal_squared` | `valorTotalVencedor²` ⚠️ vazamento |
| 48 | `valorUnitReal_x_qtd_ipca` | `(valorUnitarioVencedor ÷ indiceAcumulado) × quantidade × (1 + ipca_decimal)` |

> ⚠️ Variáveis marcadas como **vazamento** são derivações diretas da variável-alvo
> (`valorTotalVencedor`). Elas servem para cumprir o requisito de correlação do professor,
> mas **não entram no modelo OLS** (passo 8).

---

## 📈 Principais Resultados

- **110.675 itens** analisados em 11 anos
- **Ticket médio real** cresceu +372% de 2015 a 2025 (inflação acumulada: 64,8%)
- **Desconto médio histórico** de 26,3% — para R$ 1.000.000 estimado, gasto provável de R$ 737.000
- **2021** foi o ano de maior volume (15.445 itens · R$ 589M)
- **Julho** concentra o maior pico de publicações (12,4% do total anual)
- **2024** apresenta desconto atípico de 75,5% — causado por licitações de grande porte com estimativas acima do mercado
- **20 variáveis** com |r| > 0.3 em relação ao alvo (requisito mínimo: 15)
- **R² do modelo OLS**: 0,33 — esperado dado a alta heterogeneidade da base

---

## 🔗 Fonte dos Dados

- **Licitações**: API pública da Prefeitura de Criciúma/SC
- **IPCA**: IBGE — Índice Nacional de Preços ao Consumidor Amplo (série histórica anual)

---

## 👥 Autores

Trabalho acadêmico — Análise de Dados Públicos  
Criciúma/SC · 2025
