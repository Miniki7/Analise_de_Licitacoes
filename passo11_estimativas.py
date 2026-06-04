# ══════════════════════════════════════════════════════════════════════════════
# PASSO 12 — Estimativa Pontual e Intervalar
#
# Aplica os dois tipos de estimativa sobre a variável alvo valorTotalVencedor:
#
# ESTIMATIVA PONTUAL
#   → Usa a média amostral como estimador do parâmetro populacional
#   → Calculada para o total e segmentada por ano
#
# ESTIMATIVA INTERVALAR
#   → Intervalo de Confiança (IC) para a média
#   → Usa t de Student quando n < 30, distribuição normal (z) quando n >= 30
#   → Aplica FPC quando n/N > 5% E a linha não é o TOTAL
#     (quando ano=="TOTAL", n == N → FPC zeraria o erro padrão → não aplicar)
#   → Calculado com 90%, 95% e 99% de confiança
#
# Saídas:
#   data/estimativas_pontual.csv    — estimativa pontual por ano
#   data/estimativas_intervalar.csv — IC por ano e nível de confiança
#   data/estimativas_resumo.txt     — interpretação completa para o trabalho
# ══════════════════════════════════════════════════════════════════════════════

import math
import numpy as np
import pandas as pd
from scipy.stats import norm, t as t_dist

INPUT_FILE = "data/licitacoes_deflacionadas.csv"

OUT_PONTUAL     = "data/estimativas_pontual.csv"
OUT_INTERVALAR  = "data/estimativas_intervalar.csv"
OUT_RESUMO      = "data/estimativas_resumo.txt"

ALVO       = "valorTotalVencedor"
CONFIANCAS = [0.90, 0.95, 0.99]


# ── FUNÇÃO DE INTERVALO DE CONFIANÇA ─────────────────────────────────────────

def intervalo_confianca_media(media_amostral, desvio_amostral, n,
                               confianca=0.95, populacao_finita=False, N=None):
    """
    Calcula o intervalo de confiança para a média populacional.

    Parâmetros:
        media_amostral  : média calculada na amostra
        desvio_amostral : desvio padrão amostral (ddof=1)
        n               : tamanho da amostra
        confianca       : nível de confiança (ex: 0.95)
        populacao_finita: aplica FPC quando True
        N               : tamanho da população (obrigatório se populacao_finita=True)

    Retorna dict com todos os componentes do cálculo.
    """
    if n <= 1:
        raise ValueError("n deve ser maior que 1")
    if desvio_amostral < 0:
        raise ValueError("O desvio padrão amostral não pode ser negativo")
    if not (0 < confianca < 1):
        raise ValueError("A confiança deve estar entre 0 e 1. Ex: 0.95")

    alpha = 1 - confianca
    gl    = n - 1

    # Escolhe distribuição conforme tamanho amostral
    if n < 30:
        metodo        = "t de Student"
        valor_critico = t_dist.ppf(1 - alpha / 2, df=gl)
    else:
        metodo        = "normal (z)"
        valor_critico = norm.ppf(1 - alpha / 2)

    erro_padrao = desvio_amostral / math.sqrt(n)
    fpc = 1.0

    # Fator de Correção de População Finita
    # Só aplica quando a amostra é uma parte da população (n < N)
    # Quando n == N (caso TOTAL), FPC seria 0 — não aplicar
    if populacao_finita:
        if N is None:
            raise ValueError("Informe N quando a população for finita")
        if N <= 1:
            raise ValueError("N deve ser maior que 1")
        if n > N:
            raise ValueError("n não pode ser maior que N")
        fpc = math.sqrt((N - n) / (N - 1)) if N > 1 else 1.0
        erro_padrao *= fpc

    margem_erro = valor_critico * erro_padrao

    return {
        "metodo":                    metodo,
        "graus_de_liberdade":        gl,
        "valor_critico":             round(valor_critico, 6),
        "erro_padrao":               round(erro_padrao, 4),
        "fator_correcao_pop_finita": round(fpc, 6),
        "margem_erro":               round(margem_erro, 4),
        "limite_inferior":           round(media_amostral - margem_erro, 4),
        "limite_superior":           round(media_amostral + margem_erro, 4),
    }


# ── CARREGAR DADOS ────────────────────────────────────────────────────────────
print("── Carregando dados ──")
df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
df_valido = df[df[ALVO].notna() & (df[ALVO] > 0)].copy()

N_populacao = len(df_valido)
print(f"  Registros válidos (população): {N_populacao:,}".replace(",", "."))


# ════════════════════════════════════════════════════════════════════════════
# PARTE 1 — ESTIMATIVA PONTUAL
# Estimador: média amostral ( x̄ ) como estimativa do parâmetro µ
# ════════════════════════════════════════════════════════════════════════════
print("\n── Estimativa Pontual ──")

rows_pontual = []

# Total geral
media_geral   = df_valido[ALVO].mean()
mediana_geral = df_valido[ALVO].median()
desvio_geral  = df_valido[ALVO].std(ddof=1)
cv_geral      = (desvio_geral / media_geral * 100) if media_geral > 0 else 0

rows_pontual.append({
    "ano":                        "TOTAL",
    "n_amostral":                 N_populacao,
    "estimativa_pontual_media":   round(media_geral, 4),
    "estimativa_pontual_mediana": round(mediana_geral, 4),
    "desvio_padrao":              round(desvio_geral, 4),
    "coef_variacao_pct":          round(cv_geral, 2),
    "observacao":                 "Média amostral como estimador pontual de µ",
})

# Por ano
for ano in sorted(df_valido["ano"].dropna().unique().astype(int)):
    sub = df_valido[df_valido["ano"] == ano][ALVO]
    n_a = len(sub)
    if n_a < 2:
        continue
    media_a   = sub.mean()
    mediana_a = sub.median()
    desvio_a  = sub.std(ddof=1)
    cv_a      = (desvio_a / media_a * 100) if media_a > 0 else 0

    rows_pontual.append({
        "ano":                        ano,
        "n_amostral":                 n_a,
        "estimativa_pontual_media":   round(media_a, 4),
        "estimativa_pontual_mediana": round(mediana_a, 4),
        "desvio_padrao":              round(desvio_a, 4),
        "coef_variacao_pct":          round(cv_a, 2),
        "observacao":                 "t de Student" if n_a < 30 else "normal (z)",
    })
    print(f"  {ano}: µ̂ = R$ {media_a:>10,.2f}  (n={n_a:,})".replace(",", "."))

df_pontual = pd.DataFrame(rows_pontual)
df_pontual.to_csv(OUT_PONTUAL, index=False, encoding="utf-8-sig", sep=";")
print(f"\n  Estimativa pontual geral: R$ {media_geral:,.2f}".replace(",", "."))


# ════════════════════════════════════════════════════════════════════════════
# PARTE 2 — ESTIMATIVA INTERVALAR
# IC para a média com 90%, 95% e 99% de confiança
#
# Regra do FPC:
#   - ano == "TOTAL": n == N → NÃO aplica FPC (zeraria o erro padrão)
#   - ano específico: aplica FPC quando n/N > 5%
# ════════════════════════════════════════════════════════════════════════════
print("\n── Estimativa Intervalar ──")

rows_intervalar = []

for ano in ["TOTAL"] + sorted(df_valido["ano"].dropna().unique().astype(int).tolist()):
    if ano == "TOTAL":
        sub = df_valido[ALVO]
    else:
        sub = df_valido[df_valido["ano"] == ano][ALVO]

    n_a = len(sub)
    if n_a < 2:
        continue
    media_a  = sub.mean()
    desvio_a = sub.std(ddof=1)

    # TOTAL cobre toda a população → FPC zeraria o erro padrão → não aplica
    # Anos específicos: aplica FPC apenas quando n > 5% de N
    eh_total = (ano == "TOTAL")
    usar_fpc = (not eh_total) and ((n_a / N_populacao) > 0.05)
    N_ref    = N_populacao if usar_fpc else None

    for conf in CONFIANCAS:
        ic = intervalo_confianca_media(
            media_amostral   = media_a,
            desvio_amostral  = desvio_a,
            n                = n_a,
            confianca        = conf,
            populacao_finita = usar_fpc,
            N                = N_ref,
        )

        rows_intervalar.append({
            "ano":                ano,
            "confianca_pct":      int(conf * 100),
            "n_amostral":         n_a,
            "estimativa_pontual": round(media_a, 4),
            "metodo":             ic["metodo"],
            "valor_critico":      ic["valor_critico"],
            "erro_padrao":        ic["erro_padrao"],
            "fpc_aplicado":       "Sim" if usar_fpc else "Não",
            "fpc_valor":          ic["fator_correcao_pop_finita"],
            "margem_erro":        ic["margem_erro"],
            "ic_inferior":        max(0, ic["limite_inferior"]),
            "ic_superior":        ic["limite_superior"],
            "amplitude_ic":       round(ic["limite_superior"] - max(0, ic["limite_inferior"]), 4),
        })

df_intervalar = pd.DataFrame(rows_intervalar)
df_intervalar.to_csv(OUT_INTERVALAR, index=False, encoding="utf-8-sig", sep=";")

# Exibe IC 95% por ano no terminal
ic95 = df_intervalar[df_intervalar["confianca_pct"] == 95]
print(f"\n  {'Ano':<8} {'n':>7} {'Pontual':>12} {'IC 95% inferior':>16} {'IC 95% superior':>16} {'Método'}")
print("  " + "─" * 70)
for _, row in ic95.iterrows():
    print(f"  {str(row['ano']):<8} {int(row['n_amostral']):>7,} "
          f"R${row['estimativa_pontual']:>10,.0f} "
          f"R${row['ic_inferior']:>13,.0f} "
          f"R${row['ic_superior']:>13,.0f}  {row['metodo']}".replace(",", "."))


# ── RESUMO TEXTUAL ────────────────────────────────────────────────────────────
ic_total_90 = df_intervalar[(df_intervalar["ano"] == "TOTAL") & (df_intervalar["confianca_pct"] == 90)].iloc[0]
ic_total_95 = df_intervalar[(df_intervalar["ano"] == "TOTAL") & (df_intervalar["confianca_pct"] == 95)].iloc[0]
ic_total_99 = df_intervalar[(df_intervalar["ano"] == "TOTAL") & (df_intervalar["confianca_pct"] == 99)].iloc[0]

linhas = []
linhas.append("=" * 65)
linhas.append("ESTIMATIVA PONTUAL E INTERVALAR — valorTotalVencedor")
linhas.append("=" * 65)
linhas.append(f"\nVariável analisada : {ALVO}")
linhas.append(f"Tamanho da população (N): {N_populacao:,}".replace(",", "."))
linhas.append("")
linhas.append("─" * 65)
linhas.append("1. ESTIMATIVA PONTUAL")
linhas.append("─" * 65)
linhas.append(f"""
  A estimativa pontual usa a média amostral (x̄) como estimador
  do parâmetro populacional µ (valor médio verdadeiro de todos
  os itens licitados).

  Estimativa pontual geral (2015–2025):
    x̄  = R$ {media_geral:,.2f}
    Md = R$ {mediana_geral:,.2f}  (mediana — menos sensível a outliers)
    s  = R$ {desvio_geral:,.2f}  (desvio padrão amostral)
    CV = {cv_geral:.1f}%  (coeficiente de variação — indica alta dispersão)

  Interpretação:
  O CV de {cv_geral:.0f}% indica que a base é altamente heterogênea —
  itens de poucos reais convivem com contratos de centenas de
  milhares. A mediana é uma estimativa pontual mais robusta
  para planejamento neste caso.
""".replace(",", "."))

linhas.append("─" * 65)
linhas.append("2. ESTIMATIVA INTERVALAR")
linhas.append("─" * 65)
linhas.append(f"""
  O intervalo de confiança (IC) fornece uma faixa de valores
  dentro da qual o parâmetro µ está com determinada probabilidade.

  Como n = {N_populacao:,} > 30, usa-se a distribuição normal (z).

  Para o TOTAL (2015–2025), os dados cobrem toda a população —
  o FPC não é aplicado, pois com n = N o fator seria zero.
  O IC reflete a variabilidade interna da série histórica.

  Para anos individuais, o FPC é aplicado quando n/N > 5%,
  reduzindo o erro padrão proporcionalmente ao peso da amostra.

  Resultados para a base completa:

  IC 90%  (z = {ic_total_90['valor_critico']:.4f}):
    [R$ {ic_total_90['ic_inferior']:>12,.2f}  ;  R$ {ic_total_90['ic_superior']:>12,.2f}]
    Margem de erro: R$ {ic_total_90['margem_erro']:,.2f}

  IC 95%  (z = {ic_total_95['valor_critico']:.4f}):
    [R$ {ic_total_95['ic_inferior']:>12,.2f}  ;  R$ {ic_total_95['ic_superior']:>12,.2f}]
    Margem de erro: R$ {ic_total_95['margem_erro']:,.2f}

  IC 99%  (z = {ic_total_99['valor_critico']:.4f}):
    [R$ {ic_total_99['ic_inferior']:>12,.2f}  ;  R$ {ic_total_99['ic_superior']:>12,.2f}]
    Margem de erro: R$ {ic_total_99['margem_erro']:,.2f}

  Interpretação do IC 95%:
  Com 95% de confiança, o valor médio real por item licitado
  pela Prefeitura de Criciúma está entre
  R$ {ic_total_95['ic_inferior']:,.2f} e R$ {ic_total_95['ic_superior']:,.2f}.
  Isso significa que se repetíssemos a coleta de dados 100 vezes,
  em 95 delas o verdadeiro µ estaria dentro deste intervalo.
""".replace(",", "."))

linhas.append("─" * 65)
linhas.append("3. DIFERENÇA ENTRE ESTIMATIVA PONTUAL E INTERVALAR")
linhas.append("─" * 65)
linhas.append(f"""
  Estimativa PONTUAL:
    → Fornece um único valor: x̄ = R$ {media_geral:,.2f}
    → Vantagem: simples e direta
    → Desvantagem: não informa a incerteza do estimador

  Estimativa INTERVALAR (IC 95%):
    → Fornece uma faixa: [R$ {ic_total_95['ic_inferior']:,.2f} ; R$ {ic_total_95['ic_superior']:,.2f}]
    → Vantagem: quantifica a incerteza da estimativa
    → Desvantagem: mais complexa de comunicar

  Para planejamento orçamentário, recomenda-se usar o
  LIMITE SUPERIOR do IC 95% como valor de referência conservador,
  garantindo cobertura mesmo nos cenários acima da média.
""".replace(",", "."))

linhas.append("=" * 65)
resumo_str = "\n".join(linhas)
print("\n" + resumo_str)

with open(OUT_RESUMO, "w", encoding="utf-8") as f:
    f.write(resumo_str)

print(f"\n📁 Estimativa pontual   : {OUT_PONTUAL}")
print(f"📁 Estimativa intervalar: {OUT_INTERVALAR}")
print(f"📁 Resumo               : {OUT_RESUMO}")
