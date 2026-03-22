# gerar_relatorio.py
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

# ─────────────────────────────────────────
# 1. DADOS
# ─────────────────────────────────────────
df       = pd.read_csv("output/dados_completos.csv")
sessoes  = pd.read_csv("output/sessoes.csv")
veic_mot = pd.read_csv("output/motoristas_veiculos.csv")

sessoes["Inicio"]      = pd.to_datetime(sessoes["Inicio"])
sessoes["Fim"]         = pd.to_datetime(sessoes["Fim"])
sessoes["Duracao_min"] = sessoes["Duracao_min"].round(1)
sess_dentro = sessoes[sessoes["Status"] == "Dentro"].copy()

resumo_vei = (sessoes.groupby(["Veículo","Status"])["Duracao_min"]
              .sum().reset_index())
resumo_vei["Duracao_h"] = (resumo_vei["Duracao_min"]/60).round(2)

resumo_mot = (sessoes.groupby(["Motorista","Status"])["Duracao_min"]
              .sum().reset_index())
resumo_mot["Duracao_h"] = (resumo_mot["Duracao_min"]/60).round(2)

# ─────────────────────────────────────────
# 2. CORES E ESTILOS
# ─────────────────────────────────────────
AZUL       = colors.HexColor("#1565C0")
AZUL_CLR   = colors.HexColor("#E3F0FF")
VERDE      = colors.HexColor("#2E7D32")
VERDE_CLR  = colors.HexColor("#E8F5E9")
CINZA      = colors.HexColor("#F5F5F5")
CINZA_ESC  = colors.HexColor("#555555")
BRANCO     = colors.white
PRETO      = colors.black

def estilo(nome, **kwargs):
    return ParagraphStyle(nome, **kwargs)

titulo_doc = estilo("TituloDoc", fontSize=20, textColor=BRANCO,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
subtit_doc = estilo("SubtitDoc", fontSize=11, textColor=colors.HexColor("#90CAF9"),
                    fontName="Helvetica", alignment=TA_CENTER)
titulo_sec = estilo("TituloSec", fontSize=13, textColor=AZUL,
                    fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=6)
corpo      = estilo("Corpo", fontSize=10, textColor=CINZA_ESC,
                    fontName="Helvetica", spaceAfter=4, leading=14)
rodape_sty = estilo("Rodape", fontSize=8, textColor=CINZA_ESC,
                    fontName="Helvetica", alignment=TA_CENTER)

def th_style(cor_header=None):
    cor = cor_header or AZUL
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), cor),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BRANCO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BRANCO, CINZA]),
        ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
        ("ALIGN",         (0, 1), (0, -1), "LEFT"),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ])

def kpi_table(items):
    cells = [[
        Paragraph(
            f"<b>{v}</b><br/><font size=8 color='#555555'>{l}</font>",
            ParagraphStyle("kpi", fontSize=14, fontName="Helvetica-Bold",
                           alignment=TA_CENTER, textColor=PRETO)
        ) for l, v, _ in items
    ]]
    col_w = [4.3*cm] * len(items)
    t = Table(cells, colWidths=col_w, rowHeights=[1.4*cm])
    cmds = [
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0, BRANCO),
    ]
    for i, (_, _, cor) in enumerate(items):
        cmds.append(("BACKGROUND", (i, 0), (i, 0), cor))
    t.setStyle(TableStyle(cmds))
    return t

# ─────────────────────────────────────────
# 3. DOCUMENTO
# ─────────────────────────────────────────
W, H    = A4
MARGEM  = 1.8*cm
LARG    = W - 2*MARGEM
elementos = []

output_path = "output/relatorio_geofence.pdf"
doc = SimpleDocTemplate(
    output_path, pagesize=A4,
    leftMargin=MARGEM, rightMargin=MARGEM,
    topMargin=MARGEM, bottomMargin=MARGEM,
)

# ── CAPA ─────────────────────────────────
capa_data = [
    [Paragraph("Staff Telemetria", titulo_doc)],
    [Paragraph("Centro de Inteligência de Dados", titulo_doc)],
    [Paragraph("Relatório de Análise de Frota — Geofence", subtit_doc)],
    [Paragraph("02/03/2026 – 06/03/2026", subtit_doc)],
]
t_capa = Table(capa_data, colWidths=[LARG])
t_capa.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, -1), AZUL),
    ("TOPPADDING",    (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ("LEFTPADDING",   (0, 0), (-1, -1), 16),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
]))
elementos.append(t_capa)
elementos.append(Spacer(1, 0.4*cm))
elementos.append(Paragraph(
    f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
    rodape_sty))
elementos.append(HRFlowable(width=LARG, thickness=0.5, color=AZUL))
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 1: CONTEXTO ─────────────────────
elementos.append(Paragraph("1. Contexto e Metodologia", titulo_sec))
elementos.append(Paragraph(
    "Esta análise tem como objetivo cruzar os dados de rastreamento GPS de uma frota de "
    "<b>5 veículos</b> (V-1001 a V-1005) com as coordenadas da <b>Base Operacional</b>, "
    "identificando quais veículos e motoristas estiveram dentro do perímetro (geofence) "
    "ao longo de uma semana comercial.", corpo))
elementos.append(Paragraph(
    "Para determinar se um ponto GPS está dentro do polígono da cerca, foi utilizado o "
    "algoritmo de <b>Ray Casting</b>: projeta-se um raio horizontal a partir do ponto e "
    "conta-se os cruzamentos com as arestas do polígono — número ímpar indica ponto interno.",
    corpo))
elementos.append(Spacer(1, 0.3*cm))
elementos.append(kpi_table([
    ("Total de registros GPS", "27.567", AZUL_CLR),
    ("Veículos monitorados",   "5",      CINZA),
    ("Motoristas na semana",   "5",      CINZA),
    ("Dias monitorados",       "5 dias", CINZA),
]))
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 2: CERCA ELETRÔNICA ─────────────
elementos.append(HRFlowable(width=LARG, thickness=0.3, color=colors.HexColor("#DDDDDD")))
elementos.append(Paragraph("2. Cerca Eletrônica (Geofence)", titulo_sec))
elementos.append(Paragraph(
    "A Base Operacional é definida por um polígono de <b>8 vértices</b> (coordenadas lat/lon). "
    "Todos os registros GPS foram classificados como <b>Dentro</b> ou <b>Fora</b> deste perímetro.",
    corpo))

cerca_data = [["Ponto", "Latitude", "Longitude"],
              ["P1", "-3.735743", "-38.507709"],
              ["P2", "-3.731888", "-38.507923"],
              ["P3", "-3.730368", "-38.505628"],
              ["P4", "-3.730775", "-38.501851"],
              ["P5", "-3.733965", "-38.501186"],
              ["P6", "-3.737370", "-38.501894"],
              ["P7", "-3.737220", "-38.505349"],
              ["P8", "-3.735743", "-38.507709"]]
t_cerca = Table(cerca_data, colWidths=[2*cm, 4*cm, 4*cm])
t_cerca.setStyle(th_style())
elementos.append(t_cerca)
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 3: RESULTADOS POR VEÍCULO ───────
elementos.append(HRFlowable(width=LARG, thickness=0.3, color=colors.HexColor("#DDDDDD")))

vei_rows = [["Veículo", "Dentro (min)", "Fora (h)", "Registros GPS", "Status"]]
veiculos_info = {
    "V-1001": (0,    105.8, 8390),
    "V-1002": (61.1, 105.7, 8005),
    "V-1003": (0,    105.7, 404),
    "V-1004": (0,    106.6, 7085),
    "V-1005": (0,    106.1, 3683),
}
for v, (dentro, fora, regs) in veiculos_info.items():
    status = "✓ Entrou na base" if dentro > 0 else "Somente fora"
    vei_rows.append([v, str(dentro) if dentro > 0 else "0",
                     f"{fora}h", str(regs), status])

t_vei = Table(vei_rows, colWidths=[2.5*cm, 3.5*cm, 3*cm, 3*cm, 4*cm])
ts_vei = th_style()
ts_vei.add("TEXTCOLOR", (4, 2), (4, 2), VERDE)
ts_vei.add("FONTNAME",  (4, 2), (4, 2), "Helvetica-Bold")
t_vei.setStyle(ts_vei)

elementos.append(KeepTogether([
    Paragraph("3. Análise por Veículo", titulo_sec),
    Paragraph(
        "Dos 5 veículos monitorados, apenas o <b>V-1002</b> registrou presença dentro da "
        "cerca eletrônica durante a semana, com <b>3 sessões</b> totalizando <b>61 minutos</b> na base.",
        corpo),
    Spacer(1, 0.2*cm),
    t_vei,
]))
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 4: SESSÕES NA CERCA ─────────────
elementos.append(HRFlowable(width=LARG, thickness=0.3, color=colors.HexColor("#DDDDDD")))

sess_rows = [["#", "Veículo", "Data", "Entrada", "Saída", "Duração (min)", "Motorista"]]
for i, row in enumerate(sess_dentro.itertuples(), 1):
    sess_rows.append([
        str(i), row.Veículo,
        row.Inicio.strftime("%d/%m/%Y"),
        row.Inicio.strftime("%H:%M"),
        row.Fim.strftime("%H:%M"),
        str(row.Duracao_min),
        row.Motorista,
    ])

t_sess = Table(sess_rows, colWidths=[0.8*cm, 2*cm, 2.5*cm, 2*cm, 2*cm, 3*cm, 3.7*cm])
t_sess.setStyle(th_style(VERDE))

elementos.append(KeepTogether([
    Paragraph("4. Sessões dentro da Base Operacional", titulo_sec),
    Paragraph(
        "Foram detectadas <b>3 sessões</b> de entrada na Base, todas pelo veículo V-1002, "
        "em dois dias distintos e com dois motoristas diferentes.", corpo),
    Spacer(1, 0.2*cm),
    t_sess,
]))
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 5: ANÁLISE POR MOTORISTA ────────
elementos.append(HRFlowable(width=LARG, thickness=0.3, color=colors.HexColor("#DDDDDD")))

mot_rows = [["Motorista", "Dentro (min)", "Fora (h)", "Veículos Operados"]]
motoristas_info = {
    "Ana Costa":       (51.3, 236.5),
    "Carlos Silva":    (0,    160.2),
    "João Souza":      (0,    27.3),
    "Marcos Oliveira": (9.8,  105.8),
    "Pedro Santos":    (0,    0),
}
for mot, (dentro, fora) in motoristas_info.items():
    veics = veic_mot[veic_mot["Motorista"]==mot]["Veículos_Operados"].values
    veics_str = veics[0] if len(veics) > 0 else "—"
    mot_rows.append([
        mot,
        str(dentro) if dentro > 0 else "0",
        f"{fora}h" if fora > 0 else "0h",
        veics_str,
    ])

t_mot = Table(mot_rows, colWidths=[4*cm, 2.5*cm, 2.5*cm, 7*cm])
ts_mot = th_style()
for i, (mot, (dentro, _)) in enumerate(motoristas_info.items(), 1):
    if dentro > 0:
        ts_mot.add("TEXTCOLOR", (1, i), (1, i), VERDE)
        ts_mot.add("FONTNAME",  (1, i), (1, i), "Helvetica-Bold")
t_mot.setStyle(ts_mot)

elementos.append(KeepTogether([
    Paragraph("5. Análise por Motorista", titulo_sec),
    Paragraph(
        "A frota opera com <b>rotatividade de motoristas</b> — o mesmo veículo pode ser conduzido "
        "por motoristas diferentes a cada dia. Dos 5 motoristas, <b>Ana Costa</b> e "
        "<b>Marcos Oliveira</b> registraram presença dentro da cerca.", corpo),
    Spacer(1, 0.2*cm),
    t_mot,
]))
elementos.append(Spacer(1, 0.4*cm))

# ── SEÇÃO 6: CONCLUSÕES ───────────────────
conclusoes = [
    "O <b>V-1002</b> foi o único veículo a registrar presença na Base Operacional durante a semana monitorada.",
    "Foram identificadas <b>3 sessões</b> de entrada na cerca, com duração total de <b>61 minutos</b>.",
    "A <b>Ana Costa</b> foi a motorista com maior tempo na base (51,3 min em 2 sessões na terça-feira).",
    "O <b>Marcos Oliveira</b> registrou uma sessão de 9,8 minutos na quarta-feira.",
    "Os demais veículos (V-1001, V-1003, V-1004, V-1005) <b>não passaram pela Base</b> em nenhum momento.",
]

elementos.append(KeepTogether([
    HRFlowable(width=LARG, thickness=0.3, color=colors.HexColor("#DDDDDD")),
    Paragraph("6. Conclusões", titulo_sec),
    *[Paragraph(f"• {c}", corpo) for c in conclusoes],
    Spacer(1, 0.4*cm),
    HRFlowable(width=LARG, thickness=0.5, color=AZUL),
    Spacer(1, 0.2*cm),
    Paragraph(
        f"Staff Telemetria — Centro de Inteligência de Dados  |  "
        f"Análise gerada via Python (pandas + reportlab)  |  "
        f"{datetime.now().strftime('%d/%m/%Y')}",
        rodape_sty),
]))

# ─────────────────────────────────────────
# 4. GERAR PDF
# ─────────────────────────────────────────
doc.build(elementos)
print(f"✅ PDF gerado: {output_path}")