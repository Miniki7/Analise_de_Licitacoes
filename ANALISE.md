# 📋 Guia de Interpretação das Análises

Este documento explica como ler e interpretar cada arquivo gerado pelo projeto.

---

## 1. `licitacoes_deflacionadas.csv` — Base principal

Cada linha representa **um item vencedor** de uma licitação.

| Coluna | Descrição |
|--------|-----------|
| `ano` | Ano da licitação |
| `modalidade` | Tipo de licitação (Pregão, Convite, etc.) |
| `situacao` | Status: Homologado, Cancelado, etc. |
| `valorEstimado` | Soma de valorTotalReferencia dos itens |
| `valorHomologado` | Valor final pago (só quando Homologado) |
| `valorTotalVencedor` | Valor total do item vencedor |
| `valorUnitarioVencedor` | Preço unitário pago |
| `valorUnitarioReferencia` | Preço de referência do edital |
| `indiceAcumulado` | Fator de correção pela inflação (base 2015 = 1.0) |
| `valorTotalVencedorReal` | Valor deflacionado em poder de compra de 2015 |

---

## 2. `agregado_anual.csv` — Evolução temporal

| Coluna | Como interpretar |
|--------|-----------------|
| `valor_medio_nominal` | Ticket médio em valores correntes do ano |
| `valor_medio_real` | Ticket médio em reais de 2015 — **use este para comparar entre anos** |
| `ipca_percentual` | Inflação oficial do ano |

> Se `valor_medio_real` **cresce** ao longo dos anos → os itens estão ficando mais caros acima da inflação.  
> Se `valor_medio_real` **cai** → a prefeitura está comprando mais barato em termos reais.

---

## 3. `correlacoes.csv` — Correlações de Pearson

| Coluna | Descrição |
|--------|-----------|
| `correlacao_r` | De -1 a +1. Quanto mais próximo de ±1, mais forte a relação |
| `p_valor` | < 0.05 = correlação real; ≥ 0.05 = pode ser coincidência |
| `bem_correlacionada` | Sim se \|r\| > 0.3 — critério mínimo do trabalho |
| `forca` | Forte (≥0.70), Moderada (0.40–0.70), Fraca-moderada (0.30–0.40) |

> **Requisito do trabalho**: mínimo de 15 variáveis com \|r\| > 0.3.

---

## 4. `ols_resultado.csv` — Regressão OLS

| Coluna | Como interpretar |
|--------|-----------------|
| `coeficiente` | Quanto o alvo muda para cada +1 unidade na variável |
| `p_valor` | < 0.05 = variável estatisticamente significativa no modelo |
| `intervalo_inf / sup` | Intervalo de confiança 95% do coeficiente |

**No arquivo `ols_resumo.txt`** os indicadores-chave são:

```
R²          → % da variação do valorTotalVencedor explicada pelo modelo
              Ideal: acima de 0.70 para dados de licitações
R² ajustado → R² penalizado pelo número de variáveis (use este)
F-statistic → Se p < 0.05, o modelo como um todo é significativo
VIF         → < 10 = sem multicolinearidade problemática
```

---

## 5. `padrao1_desconto_anual.csv` — Índice de desconto

```
indice_desconto = ((valorEstimado - valorHomologado) / valorEstimado) × 100
```

- Desconto alto → boa competitividade nas licitações
- Desconto estável ao longo dos anos → padrão confiável para orçamentos futuros
- **Regra prática**: se a média for 35%, para R$ 1.000.000 estimado, planejar R$ 650.000 de gasto real

---

## 6. `padrao2_itens_recorrentes.csv` — Itens vs IPCA

| Diagnóstico | Significado |
|-------------|-------------|
| ⚠️ Pressão de demanda | Preço subiu acima do IPCA acumulado |
| ✅ Boa gestão | Preço subiu menos que o IPCA |
| ➡️ Neutro | Variação próxima ao IPCA |

> `variacao_real_pct` é a métrica principal: positivo = ficou mais caro em termos reais.

---

## 7. `padrao3_sazonalidade.csv` — Sazonalidade

- Concentração em **Q1 (jan–mar)** indica pico pós-aprovação orçamentária
- Concentração em **Q4 (out–dez)** indica corrida para gastar saldo antes do fim do exercício
- Distribuição equilibrada → boa gestão do planejamento anual

---

## 8. Gráficos

| Arquivo | O que mostra |
|---------|-------------|
| `evolucao_valores.png` | Linha nominal (azul) vs real (laranja) + barras de IPCA |
| `correlacao_ipca.png` | Dispersão IPCA × crescimento nominal com r e p-valor |
| `padroes_orcamentarios.png` | Desconto por ano com média histórica tracejada |

---

## ⚠️ Limitações da Análise

1. **Heterogeneidade dos itens**: a base mistura itens de R$ 5 a R$ 500.000 — o valor médio pode ser influenciado por outliers
2. **valorEstimado calculado**: quando não disponível diretamente, foi estimado pela soma de valorTotalReferencia
3. **IPCA geral vs setorial**: o IPCA usado é o índice geral; insumos específicos (obras, saúde) têm índices próprios
4. **Itens recorrentes**: a comparação de preços entre anos assume descrições idênticas, o que pode não refletir mudanças de especificação
