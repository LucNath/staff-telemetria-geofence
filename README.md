# Staff Telemetria — Análise de Frota com Geofence

> **Desafio Técnico — Estágio em BI | Centro de Inteligência de Dados (CID)**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green)
![Plotly Dash](https://img.shields.io/badge/Plotly%20Dash-4.x-purple)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## 📋 Descrição

Análise de dados de rastreamento GPS de uma frota de **5 veículos** ao longo
de uma semana comercial (02/03 a 06/03/2026), cruzando as posições com
uma **cerca eletrônica (geofence)** que delimita a Base Operacional.

O projeto está dividido em duas missões conforme o desafio técnico:

| Missão       | Descrição                                            | Entregável                   |
| ------------ | ---------------------------------------------------- | ---------------------------- |
| **Missão 1** | Processamento e cruzamento de dados GPS com geofence | `analise.py` + CSVs + Excel  |
| **Missão 2** | Criação de dashboards interativos de BI              | `dashboard.py` (Plotly Dash) |

---

## 📁 Estrutura do Projeto

```
staff_telemetria/
│
├── dados/                              ← Arquivos brutos recebidos
│   ├── relatorio_semanal_V-1001.xlsx
│   ├── relatorio_semanal_V-1002.xlsx
│   ├── relatorio_semanal_V-1003.xlsx
│   ├── relatorio_semanal_V-1004.xlsx
│   ├── relatorio_semanal_V-1005.xlsx
│   └── coordenadas_cerca.xlsx
│
├── output/                             ← Arquivos gerados pela análise
│   ├── dados_completos.csv             ← 27.567 registros com status GPS
│   ├── sessoes.csv                     ← Sessões dentro/fora detectadas
│   ├── motoristas_veiculos.csv         ← Veículos operados por motorista
│   ├── base_consolidada_staff_telemetria.xlsx  ← Excel final (5 abas)
│   └── relatorio_geofence.pdf          ← Relatório analítico completo
│
├── analise.py          ← Missão 1: processamento e geofence (Ray Casting)
├── dashboard.py        ← Missão 2: dashboards interativos (Plotly Dash)
├── gerar_excel.py      ← Gera o Excel consolidado de entrega
├── gerar_relatorio.py  ← Gera o relatório PDF
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- Os arquivos `.xlsx` na pasta `dados/`

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install pandas openpyxl plotly dash reportlab
```

### 3. Rodar a análise — Missão 1

```bash
python analise.py
```

Processa os dados GPS, aplica o geofence e gera os arquivos em `/output`.

### 4. Rodar o dashboard — Missão 2

```bash
python dashboard.py
```

Acesse em: **http://127.0.0.1:8050**

O dashboard possui 3 abas:

- **Visão Veículo** — comportamento da frota na semana
- **Visão Motorista** — tempo na base por colaborador
- **Eventos na Cerca** — linha do tempo das entradas

### 5. Gerar o Excel consolidado

```bash
python gerar_excel.py
```

### 6. Gerar o relatório PDF

```bash
python gerar_relatorio.py
```

---

## 🧠 Metodologia — Geofence (Ray Casting)

Para verificar se cada coordenada GPS está dentro do polígono da Base
Operacional, foi implementado o algoritmo de **Ray Casting**:

```
Ponto P (lat, lon)
        │
        ▼
Projeta raio horizontal →→→→→→→→
        │
        ▼
Conta cruzamentos com arestas do polígono
        │
        ├── Ímpar  → DENTRO da cerca ✅
        └── Par    → FORA da cerca  ❌
```

A implementação está em `analise.py` na função `ponto_dentro_do_poligono()`.

---

## 📊 Resultados Principais

| Métrica                            | Valor                   |
| ---------------------------------- | ----------------------- |
| Total de registros GPS processados | **27.567**              |
| Veículos monitorados               | **5** (V-1001 a V-1005) |
| Motoristas na semana               | **5**                   |
| Período monitorado                 | **02/03 a 06/03/2026**  |
| Veículos que entraram na base      | **1** (V-1002)          |
| Sessões dentro da cerca            | **3**                   |
| Tempo total na base                | **61 minutos**          |

### Sessões detectadas dentro da Base Operacional

| #   | Data                | Entrada | Saída | Duração  | Motorista       |
| --- | ------------------- | ------- | ----- | -------- | --------------- |
| 1   | 03/03/2026 (Terça)  | 10:36   | 11:23 | 47,5 min | Ana Costa       |
| 2   | 03/03/2026 (Terça)  | 11:26   | 11:30 | 3,8 min  | Ana Costa       |
| 3   | 04/03/2026 (Quarta) | 11:41   | 11:51 | 9,8 min  | Marcos Oliveira |

### Veículos que **não** passaram pela base

V-1001 • V-1003 • V-1004 • V-1005 permaneceram 100% do tempo fora da cerca.

---

## 🛠️ Tecnologias Utilizadas

| Biblioteca  | Uso                               |
| ----------- | --------------------------------- |
| `pandas`    | Manipulação e análise de dados    |
| `openpyxl`  | Leitura/escrita de arquivos Excel |
| `plotly`    | Criação dos gráficos interativos  |
| `dash`      | Framework do dashboard web        |
| `reportlab` | Geração do relatório PDF          |

---

_Staff Telemetria — Centro de Inteligência de Dados (CID) • 2026_
