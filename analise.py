"""
analise.py — Missão 1: Processamento e Cruzamento de Dados
============================================================
Desafio Técnico — Estágio em BI | Staff Telemetria (CID)

Objetivo:
    Cruzar os dados de rastreamento GPS de 5 veículos com as
    coordenadas da Base Operacional (geofence), identificando
    quais veículos e motoristas estiveram dentro do perímetro
    ao longo da semana de 02/03 a 06/03/2026.

Metodologia:
    Algoritmo Ray Casting para verificação de ponto em polígono.
    Para cada coordenada GPS (lat, lon), projeta-se um raio
    horizontal e conta-se os cruzamentos com as arestas do
    polígono da cerca. Número ímpar = ponto DENTRO.

Outputs gerados em /output:
    - dados_completos.csv      → todos os registros com status
    - sessoes.csv              → sessões dentro/fora detectadas
    - motoristas_veiculos.csv  → veículos por motorista

Autor: Lucas
Data:  21/03/2026
"""

import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────
# 1. CONFIGURAÇÕES
# ─────────────────────────────────────────
PASTA_DADOS  = Path("dados")
PASTA_OUTPUT = Path("output")
ARQUIVO_CERCA = PASTA_DADOS / "coordenadas_cerca.xlsx"
VEICULOS      = ["V-1001", "V-1002", "V-1003", "V-1004", "V-1005"]

# Garante que a pasta de output existe
PASTA_OUTPUT.mkdir(exist_ok=True)

# ─────────────────────────────────────────
# 2. ALGORITMO DE GEOFENCE (Ray Casting)
# ─────────────────────────────────────────
def ponto_dentro_do_poligono(lat: float, lon: float, poligono: list) -> bool:
    """
    Verifica se um ponto geográfico está dentro de um polígono.

    Utiliza o algoritmo Ray Casting: projeta um raio horizontal
    a partir do ponto e conta quantas vezes ele cruza as arestas
    do polígono. Número ímpar de cruzamentos = ponto DENTRO.

    Args:
        lat:      Latitude do ponto a verificar
        lon:      Longitude do ponto a verificar
        poligono: Lista de tuplas (lat, lon) representando os
                  vértices do polígono em ordem

    Returns:
        True se o ponto está dentro do polígono, False caso contrário
    """
    n      = len(poligono)
    dentro = False
    j      = n - 1

    for i in range(n):
        lat_i, lon_i = poligono[i][0], poligono[i][1]
        lat_j, lon_j = poligono[j][0], poligono[j][1]

        # Verifica se o raio horizontal cruza a aresta (i, j)
        if ((lon_i > lon) != (lon_j > lon)) and \
           (lat < (lat_j - lat_i) * (lon - lon_i) / (lon_j - lon_i) + lat_i):
            dentro = not dentro
        j = i

    return dentro

# ─────────────────────────────────────────
# 3. CARREGAR A CERCA ELETRÔNICA
# ─────────────────────────────────────────
print("=" * 55)
print("  STAFF TELEMETRIA — Análise de Geofence")
print("=" * 55)

print("\n[1/5] Carregando coordenadas da cerca...")
if not ARQUIVO_CERCA.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_CERCA}")

df_cerca = pd.read_excel(ARQUIVO_CERCA)
poligono = list(zip(df_cerca["Latitude"], df_cerca["Longitude"]))
print(f"      ✓ Cerca com {len(poligono)} vértices carregada.")

# ─────────────────────────────────────────
# 4. CARREGAR E UNIFICAR TODOS OS VEÍCULOS
# ─────────────────────────────────────────
print("\n[2/5] Carregando relatórios dos veículos...")
frames = []
for veiculo in VEICULOS:
    arquivo = PASTA_DADOS / f"relatorio_semanal_{veiculo}.xlsx"
    if not arquivo.exists():
        print(f"      ⚠ Arquivo não encontrado: {arquivo} — ignorado.")
        continue
    df_vei = pd.read_excel(arquivo)
    frames.append(df_vei)
    print(f"      ✓ {veiculo}: {len(df_vei):,} registros")

if not frames:
    raise ValueError("Nenhum arquivo de veículo foi carregado.")

df = pd.concat(frames, ignore_index=True)
df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
df = df.sort_values(["Veículo", "Data/Hora"]).reset_index(drop=True)

print(f"\n      Total: {len(df):,} registros | "
      f"{df['Veículo'].nunique()} veículos | "
      f"{df['Motorista'].nunique()} motoristas")
print(f"      Período: {df['Data/Hora'].min().strftime('%d/%m/%Y')} "
      f"a {df['Data/Hora'].max().strftime('%d/%m/%Y')}")

# ─────────────────────────────────────────
# 5. APLICAR GEOFENCE EM CADA REGISTRO
# ─────────────────────────────────────────
print("\n[3/5] Aplicando geofence (Ray Casting)...")
print("      Isso pode levar alguns segundos...")

df["dentro_da_cerca"] = df.apply(
    lambda row: ponto_dentro_do_poligono(
        row["Latitude"], row["Longitude"], poligono
    ),
    axis=1
)
df["Status"] = df["dentro_da_cerca"].map({True: "Dentro", False: "Fora"})

n_dentro = df["dentro_da_cerca"].sum()
n_fora   = (~df["dentro_da_cerca"]).sum()
pct      = (n_dentro / len(df) * 100)

print(f"      ✓ Dentro da cerca: {n_dentro:,} registros ({pct:.2f}%)")
print(f"      ✓ Fora da cerca:   {n_fora:,} registros ({100-pct:.2f}%)")

# ─────────────────────────────────────────
# 6. DETECTAR SESSÕES (GRUPOS CONTÍNUOS)
# ─────────────────────────────────────────
print("\n[4/5] Detectando sessões de permanência...")

# Uma "sessão" é um grupo contínuo de registros com o mesmo status
# por veículo — detectado através de mudanças no status anterior
df["status_anterior"] = df.groupby("Veículo")["dentro_da_cerca"].shift(1)
df["nova_sessao"]     = df["dentro_da_cerca"] != df["status_anterior"]
df["sessao_id"]       = df.groupby("Veículo")["nova_sessao"].cumsum()

sessoes = (
    df.groupby(["Veículo", "sessao_id", "Status"])
    .agg(
        Inicio    = ("Data/Hora", "min"),
        Fim       = ("Data/Hora", "max"),
        Motorista = ("Motorista", lambda x: x.mode()[0]),
        Registros = ("Data/Hora", "count"),
    )
    .reset_index()
)
sessoes["Duracao_min"] = (
    (sessoes["Fim"] - sessoes["Inicio"]).dt.total_seconds() / 60
).round(2)
sessoes["Duracao_h"] = (sessoes["Duracao_min"] / 60).round(2)

n_sessoes_dentro = len(sessoes[sessoes["Status"] == "Dentro"])
print(f"      ✓ {len(sessoes)} sessões totais identificadas")
print(f"      ✓ {n_sessoes_dentro} sessões DENTRO da cerca")

# ─────────────────────────────────────────
# 7. COLUNAS AUXILIARES
# ─────────────────────────────────────────
df["Data"]       = df["Data/Hora"].dt.strftime("%d/%m/%Y")
df["Hora"]       = df["Data/Hora"].dt.strftime("%H:%M:%S")
df["Dia_Semana"] = df["Data/Hora"].dt.day_name().map({
    "Monday":    "Segunda",
    "Tuesday":   "Terça",
    "Wednesday": "Quarta",
    "Thursday":  "Quinta",
    "Friday":    "Sexta",
    "Saturday":  "Sábado",
    "Sunday":    "Domingo",
})

# ─────────────────────────────────────────
# 8. SALVAR OUTPUTS
# ─────────────────────────────────────────
print("\n[5/5] Salvando arquivos de output...")

# Base completa com status de geofence
df_export = df[[
    "Veículo", "Data", "Dia_Semana", "Hora",
    "Latitude", "Longitude", "Motorista", "Status"
]]
df_export.to_csv(PASTA_OUTPUT / "dados_completos.csv", index=False)
print(f"      ✓ dados_completos.csv ({len(df_export):,} linhas)")

# Sessões identificadas
sessoes.to_csv(PASTA_OUTPUT / "sessoes.csv", index=False)
print(f"      ✓ sessoes.csv ({len(sessoes)} sessões)")

# Veículos por motorista
veic_real = (
    df.groupby("Motorista")["Veículo"]
    .apply(lambda x: ", ".join(sorted(x.unique())))
    .reset_index()
    .rename(columns={"Veículo": "Veículos_Operados"})
)
veic_real.to_csv(PASTA_OUTPUT / "motoristas_veiculos.csv", index=False)
print(f"      ✓ motoristas_veiculos.csv ({len(veic_real)} motoristas)")

# ─────────────────────────────────────────
# 9. RESUMO FINAL
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  RESUMO DA ANÁLISE")
print("=" * 55)

veics_na_base = sessoes[sessoes["Status"]=="Dentro"]["Veículo"].unique()
print(f"\n  Veículos que entraram na base: {', '.join(veics_na_base) or 'Nenhum'}")

for v in veics_na_base:
    s = sessoes[(sessoes["Veículo"]==v) & (sessoes["Status"]=="Dentro")]
    print(f"\n  {v}:")
    for _, row in s.iterrows():
        print(f"    • {row['Inicio'].strftime('%d/%m %H:%M')} – "
              f"{row['Fim'].strftime('%H:%M')} "
              f"({row['Duracao_min']:.1f} min) | {row['Motorista']}")

print(f"\n  Veículos que NÃO entraram na base:")
for v in VEICULOS:
    if v not in veics_na_base:
        print(f"    • {v}")

print("\n" + "=" * 55)
print("  ✅ Análise concluída! Arquivos em /output")
print("=" * 55 + "\n")