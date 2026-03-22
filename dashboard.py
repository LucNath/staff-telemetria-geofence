# dashboard.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# ─────────────────────────────────────────
# 1. DADOS
# ─────────────────────────────────────────
df       = pd.read_csv("output/dados_completos.csv")
sessoes  = pd.read_csv("output/sessoes.csv")
veic_mot = pd.read_csv("output/motoristas_veiculos.csv")

sessoes["Inicio"]      = pd.to_datetime(sessoes["Inicio"])
sessoes["Fim"]         = pd.to_datetime(sessoes["Fim"])
sessoes["Duracao_min"] = sessoes["Duracao_min"].round(1)

VEICULOS   = sorted(df["Veículo"].unique())
MOTORISTAS = sorted(df["Motorista"].unique())

# ─────────────────────────────────────────
# 2. PALETA
# ─────────────────────────────────────────
AZUL_ESC  = "#0D2B5E"
AZUL_MED  = "#1A4A8A"
AZUL_CLR  = "#EAF1FB"
VERDE_MED = "#2E7D32"
VERDE_CLR = "#E8F5E9"
CINZA_900 = "#1C1C1C"
CINZA_600 = "#4A4A4A"
CINZA_300 = "#C8CDD4"
CINZA_100 = "#F2F4F7"
BRANCO    = "#FFFFFF"
LARANJA   = "#BF360C"

COR_MOT = {
    "Ana Costa":       "#1A4A8A",
    "Carlos Silva":    "#4A235A",
    "João Souza":      "#004D40",
    "Marcos Oliveira": "#BF360C",
    "Pedro Santos":    "#4E342E",
}

LAYOUT_BASE = dict(
    font=dict(family="Arial", size=12, color=CINZA_900),
    plot_bgcolor=BRANCO,
    paper_bgcolor=BRANCO,
)

def lm(t=24, b=48, l=48, r=24):
    return {**LAYOUT_BASE, "margin": dict(t=t, b=b, l=l, r=r)}

XAXIS = {"showgrid": False, "linecolor": CINZA_300, "linewidth": 1,
         "ticks": "outside", "tickcolor": CINZA_300}
YAXIS = {"showgrid": True, "gridcolor": "#EEF0F3", "linecolor": CINZA_300,
         "linewidth": 1, "zeroline": False}

# ─────────────────────────────────────────
# 3. COMPONENTES
# ─────────────────────────────────────────
def card(children, style_extra=None):
    s = {"backgroundColor": BRANCO, "borderRadius": "6px",
         "padding": "20px 24px", "border": f"1px solid {CINZA_300}"}
    if style_extra:
        s.update(style_extra)
    return html.Div(children=children, style=s)

def kpi(label, valor, cor_val=AZUL_MED, bg=AZUL_CLR, borda=AZUL_MED):
    return html.Div(style={
        "backgroundColor": bg, "borderRadius": "6px",
        "padding": "16px 20px", "flex": "1", "minWidth": "140px",
        "border": f"1px solid {CINZA_300}",
        "borderTop": f"3px solid {borda}",
    }, children=[
        html.P(label.upper(), style={
            "fontSize": "10px", "color": CINZA_600, "margin": "0 0 8px 0",
            "letterSpacing": "0.8px", "fontWeight": "600",
        }),
        html.H3(valor, style={
            "fontSize": "24px", "color": cor_val,
            "margin": 0, "fontWeight": "700",
        }),
    ])

def secao(texto):
    return html.Div(style={
        "borderLeft": f"3px solid {AZUL_MED}",
        "paddingLeft": "10px", "marginBottom": "16px",
    }, children=[
        html.H3(texto, style={
            "fontSize": "12px", "color": AZUL_ESC, "margin": 0,
            "fontWeight": "700", "textTransform": "uppercase",
            "letterSpacing": "0.6px",
        })
    ])

def dropdown(id_, options, placeholder):
    return dcc.Dropdown(
        id=id_,
        options=[{"label": o, "value": o} for o in options],
        placeholder=placeholder,
        multi=True, clearable=True,
        style={"fontSize": "13px"},
    )

def tabela(dataframe, rename=None):
    df_t = dataframe.rename(columns=rename) if rename else dataframe.copy()
    th = {"padding": "10px 14px", "fontSize": "11px", "fontWeight": "700",
          "color": BRANCO, "backgroundColor": AZUL_ESC,
          "textTransform": "uppercase", "letterSpacing": "0.5px",
          "textAlign": "left", "border": "none"}
    def td(i):
        return {"padding": "10px 14px", "fontSize": "13px", "color": CINZA_900,
                "borderBottom": f"1px solid {CINZA_100}",
                "backgroundColor": BRANCO if i % 2 == 0 else CINZA_100}
    return html.Table(
        style={"width": "100%", "borderCollapse": "collapse"},
        children=[
            html.Thead(html.Tr([html.Th(c, style=th) for c in df_t.columns])),
            html.Tbody([
                html.Tr([html.Td(str(v), style=td(i)) for v in row])
                for i, row in enumerate(df_t.values)
            ]),
        ]
    )

# ─────────────────────────────────────────
# 4. APP
# ─────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Staff Telemetria — CID"

TAB_STYLE = {"fontWeight": "600", "fontSize": "13px", "color": CINZA_600,
             "padding": "12px 20px", "backgroundColor": BRANCO}
TAB_SEL   = {**TAB_STYLE, "color": AZUL_MED,
             "borderTop": f"2px solid {AZUL_MED}", "borderBottom": "none"}

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif",
           "backgroundColor": CINZA_100, "minHeight": "100vh"},
    children=[
        html.Div(style={
            "backgroundColor": AZUL_ESC, "padding": "0 48px",
            "display": "flex", "alignItems": "center",
            "justifyContent": "space-between", "height": "64px",
            "borderBottom": f"3px solid {AZUL_MED}",
        }, children=[
            html.Div([
                html.Span("STAFF TELEMETRIA", style={
                    "color": BRANCO, "fontSize": "15px",
                    "fontWeight": "800", "letterSpacing": "1.5px",
                }),
                html.Span("  |  Centro de Inteligência de Dados", style={
                    "color": "#90B4E0", "fontSize": "13px",
                }),
            ]),
            html.Span("Semana 02/03 – 06/03/2026  •  5 veículos  •  27.567 registros GPS",
                      style={"color": "#90B4E0", "fontSize": "11px"}),
        ]),
        html.Div(style={"padding": "28px 48px"}, children=[
            dcc.Tabs(id="abas", value="veiculos",
                     style={"marginBottom": "24px",
                            "borderBottom": f"1px solid {CINZA_300}"},
                     children=[
                         dcc.Tab(label="🚛  Visão Veículo",    value="veiculos",
                                 style=TAB_STYLE, selected_style=TAB_SEL),
                         dcc.Tab(label="👤  Visão Motorista",  value="motoristas",
                                 style=TAB_STYLE, selected_style=TAB_SEL),
                         dcc.Tab(label="📍  Eventos na Cerca", value="eventos",
                                 style=TAB_STYLE, selected_style=TAB_SEL),
                     ]),
            html.Div(id="conteudo"),
        ]),
    ]
)

# ─────────────────────────────────────────
# 5. CALLBACKS
# ─────────────────────────────────────────
@app.callback(Output("conteudo","children"), Input("abas","value"))
def trocar_aba(aba):
    if aba == "veiculos":   return layout_veiculos()
    if aba == "motoristas": return layout_motoristas()
    if aba == "eventos":    return layout_eventos()

# ── ABA VEÍCULOS ──────────────────────────
def layout_veiculos():
    return html.Div([
        card(html.Div([
            html.P("Filtrar veículos:", style={"fontSize":"12px","color":CINZA_600,
                                               "marginBottom":"8px","fontWeight":"600"}),
            dropdown("filtro-veiculo", VEICULOS, "Todos os veículos"),
        ]), {"marginBottom":"20px","padding":"16px 24px"}),
        html.Div(id="kpis-veiculo",
                 style={"display":"flex","gap":"14px","marginBottom":"20px","flexWrap":"wrap"}),
        html.Div(style={"display":"grid","gridTemplateColumns":"3fr 2fr",
                        "gap":"16px","marginBottom":"20px"}, children=[
            card(html.Div([
                secao("Tempo fora (h) e dentro (min) da base por veículo"),
                dcc.Graph(id="graf-bar-veiculo",
                          config={"displayModeBar":False}, style={"height":"320px"}),
            ])),
            card(html.Div([
                secao("Distribuição de registros GPS"),
                dcc.Graph(id="graf-pie-veiculo",
                          config={"displayModeBar":False}, style={"height":"320px"}),
            ])),
        ]),
        card(html.Div([
            secao("Sessões dentro da Base Operacional"),
            html.Div(id="tabela-sessoes-veiculo", style={"marginTop":"12px"}),
        ])),
    ])

@app.callback(
    Output("kpis-veiculo","children"),
    Output("graf-bar-veiculo","figure"),
    Output("graf-pie-veiculo","figure"),
    Output("tabela-sessoes-veiculo","children"),
    Input("filtro-veiculo","value"),
)
def atualizar_veiculos(filtro):
    df_f  = df[df["Veículo"].isin(filtro)]          if filtro else df.copy()
    ses_f = sessoes[sessoes["Veículo"].isin(filtro)] if filtro else sessoes.copy()

    # Resumo de duração por veículo/status
    res = ses_f.groupby(["Veículo","Status"])["Duracao_min"].sum().reset_index()
    res["Duracao_h"] = (res["Duracao_min"]/60).round(1)

    na_base = ses_f[ses_f["Status"]=="Dentro"]["Veículo"].nunique()

    kpis = [
        kpi("Veículos",      str(df_f["Veículo"].nunique())),
        kpi("Na base",       str(na_base), cor_val=VERDE_MED, bg=VERDE_CLR, borda=VERDE_MED),
        kpi("Registros GPS", f"{len(df_f):,}".replace(",",".")),
        kpi("Período",       "5 dias"),
    ]

    # Garante todos os veículos em ambos os status
    todos_veic = sorted(df_f["Veículo"].unique())
    base_veic  = pd.DataFrame({"Veículo": todos_veic})

    res_fora = (res[res["Status"]=="Fora"]
                .merge(base_veic, on="Veículo", how="right")
                .fillna({"Duracao_h": 0, "Duracao_min": 0}))
    res_dentro = (res[res["Status"]=="Dentro"]
                  .merge(base_veic, on="Veículo", how="right")
                  .fillna({"Duracao_h": 0, "Duracao_min": 0}))

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Fora (h)",
        x=res_fora["Veículo"],
        y=res_fora["Duracao_h"],
        marker_color=AZUL_MED, width=0.35,
        text=res_fora["Duracao_h"].apply(lambda v: f"{v:.0f}h" if v > 0 else ""),
        textposition="outside", textfont=dict(size=11, color=CINZA_600),
        hovertemplate="<b>%{x}</b><br>Fora: %{y:.1f}h<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name="Dentro (min)",
        x=res_dentro["Veículo"],
        y=res_dentro["Duracao_min"],
        marker_color=VERDE_MED, width=0.35,
        text=res_dentro["Duracao_min"].apply(lambda v: f"{v:.0f} min" if v > 0 else ""),
        textposition="inside", textfont=dict(size=10, color=BRANCO),
        hovertemplate="<b>%{x}</b><br>Dentro: %{y:.1f} min<extra></extra>",
        yaxis="y2",
    ))
    fig_bar.update_layout(
        **lm(t=24, b=48, l=56, r=60),
        barmode="group", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
        xaxis={**XAXIS, "title": None},
        yaxis={**YAXIS, "title": "Horas (Fora)",
               "title_font": dict(color=AZUL_MED),
               "tickfont": dict(color=AZUL_MED)},
        yaxis2=dict(
            title="Minutos (Dentro)", overlaying="y", side="right",
            showgrid=False, zeroline=False,
            title_font=dict(color=VERDE_MED),
            tickfont=dict(color=VERDE_MED),
        ),
    )

    contagem = df_f.groupby("Veículo").size().reset_index(name="Registros")
    fig_pie = go.Figure(go.Pie(
        labels=contagem["Veículo"], values=contagem["Registros"],
        hole=0.55, textinfo="percent+label", textfont=dict(size=12),
        marker=dict(colors=[AZUL_MED, VERDE_MED, LARANJA, "#4A235A", "#004D40"],
                    line=dict(color=BRANCO, width=2)),
    ))
    fig_pie.update_layout(
        **lm(t=8, b=8, l=8, r=8),
        showlegend=False,
        annotations=[dict(text="GPS", x=0.5, y=0.5, font_size=13,
                          font_color=CINZA_600, showarrow=False)],
    )

    sess_d = ses_f[ses_f["Status"]=="Dentro"][
        ["Veículo","Inicio","Fim","Duracao_min","Motorista"]].copy()
    sess_d["Inicio"]      = sess_d["Inicio"].dt.strftime("%d/%m/%Y %H:%M")
    sess_d["Fim"]         = sess_d["Fim"].dt.strftime("%d/%m/%Y %H:%M")
    sess_d["Duracao_min"] = sess_d["Duracao_min"].apply(lambda v: f"{v} min")
    tbl = tabela(sess_d, {"Veículo":"Veículo","Inicio":"Entrada","Fim":"Saída",
                           "Duracao_min":"Duração","Motorista":"Motorista"})
    return kpis, fig_bar, fig_pie, tbl


# ── ABA MOTORISTAS ────────────────────────
def layout_motoristas():
    return html.Div([
        card(html.Div([
            html.P("Filtrar motoristas:", style={"fontSize":"12px","color":CINZA_600,
                                                  "marginBottom":"8px","fontWeight":"600"}),
            dropdown("filtro-motorista", MOTORISTAS, "Todos os motoristas"),
        ]), {"marginBottom":"20px","padding":"16px 24px"}),
        html.Div(id="kpis-motorista",
                 style={"display":"flex","gap":"14px","marginBottom":"20px","flexWrap":"wrap"}),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr",
                        "gap":"16px","marginBottom":"20px"}, children=[
            card(html.Div([
                secao("Tempo dentro da base por motorista (min)"),
                dcc.Graph(id="graf-bar-mot", config={"displayModeBar":False},
                          style={"height":"300px"}),
            ])),
            card(html.Div([
                secao("Tempo total operado (horas)"),
                dcc.Graph(id="graf-stack-mot", config={"displayModeBar":False},
                          style={"height":"300px"}),
            ])),
        ]),
        card(html.Div([
            secao("Veículos operados por motorista"),
            html.Div(id="tabela-motoristas", style={"marginTop":"12px"}),
        ])),
    ])

@app.callback(
    Output("kpis-motorista","children"),
    Output("graf-bar-mot","figure"),
    Output("graf-stack-mot","figure"),
    Output("tabela-motoristas","children"),
    Input("filtro-motorista","value"),
)
def atualizar_motoristas(filtro):
    df_f  = df[df["Motorista"].isin(filtro)]          if filtro else df.copy()
    ses_f = sessoes[sessoes["Motorista"].isin(filtro)] if filtro else sessoes.copy()
    vpm_f = veic_mot[veic_mot["Motorista"].isin(filtro)] if filtro else veic_mot.copy()

    res = ses_f.groupby(["Motorista","Status"])["Duracao_min"].sum().reset_index()
    res["Duracao_h"] = (res["Duracao_min"]/60).round(1)

    res_dentro = res[res["Status"]=="Dentro"]
    na_base  = res_dentro["Motorista"].nunique()
    top_mot  = res_dentro.loc[res_dentro["Duracao_min"].idxmax(),"Motorista"] if len(res_dentro) else "—"
    top_min  = int(res_dentro["Duracao_min"].max()) if len(res_dentro) else 0

    kpis = [
        kpi("Motoristas",        str(df_f["Motorista"].nunique())),
        kpi("Estiveram na base", str(na_base), cor_val=VERDE_MED, bg=VERDE_CLR, borda=VERDE_MED),
        kpi("Maior tempo na base", f"{top_mot} — {top_min} min"),
    ]

    # Barras horizontais — tempo dentro
    fig_bar = go.Figure(go.Bar(
        x=res_dentro["Duracao_min"],
        y=res_dentro["Motorista"],
        orientation="h",
        marker_color=[COR_MOT.get(m, AZUL_MED) for m in res_dentro["Motorista"]],
        text=res_dentro["Duracao_min"].apply(lambda v: f"{v:.1f} min"),
        textposition="outside", textfont=dict(size=11, color=CINZA_600),
    ))
    fig_bar.update_layout(
        **lm(t=24, b=48, l=140, r=80),
        xaxis={**XAXIS, "title": "Minutos"},
        yaxis={**YAXIS, "showgrid": False, "title": None, "autorange": "reversed"},
        showlegend=False,
    )

    # Barras empilhadas — usa merge seguro em vez de reindex
    todos_mot = sorted(df_f["Motorista"].unique())
    base_mot  = pd.DataFrame({"Motorista": todos_mot})

    fig_stack = go.Figure()
    for status, cor in {"Fora": AZUL_MED, "Dentro": VERDE_MED}.items():
        d = (res[res["Status"]==status][["Motorista","Duracao_h"]]
             .merge(base_mot, on="Motorista", how="right")
             .fillna({"Duracao_h": 0})
             .sort_values("Motorista"))
        fig_stack.add_trace(go.Bar(
            name=status,
            x=d["Motorista"],
            y=d["Duracao_h"],
            marker_color=cor,
            text=d["Duracao_h"].apply(lambda v: f"{v:.0f}h" if v > 0 else ""),
            textposition="inside", textfont=dict(size=11, color=BRANCO),
        ))
    fig_stack.update_layout(
        **lm(t=24, b=48, l=48, r=24),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
        xaxis={**XAXIS, "title": None},
        yaxis={**YAXIS, "title": "Horas"},
    )

    tbl = tabela(vpm_f, {"Motorista":"Motorista","Veículos_Operados":"Veículos Operados"})
    return kpis, fig_bar, fig_stack, tbl


# ── ABA EVENTOS ───────────────────────────
def layout_eventos():
    return html.Div([
        card(html.Div([
            html.P("Filtrar por motorista:", style={"fontSize":"12px","color":CINZA_600,
                                                     "marginBottom":"8px","fontWeight":"600"}),
            dropdown("filtro-eventos-mot", MOTORISTAS, "Todos os motoristas"),
        ]), {"marginBottom":"20px","padding":"16px 24px"}),
        html.Div(id="kpis-eventos",
                 style={"display":"flex","gap":"14px","marginBottom":"20px","flexWrap":"wrap"}),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr",
                        "gap":"16px","marginBottom":"20px"}, children=[
            card(html.Div([
                secao("Linha do tempo — entradas na base"),
                dcc.Graph(id="graf-gantt", config={"displayModeBar":False},
                          style={"height":"300px"}),
            ])),
            card(html.Div([
                secao("Duração de cada sessão (minutos)"),
                dcc.Graph(id="graf-dur", config={"displayModeBar":False},
                          style={"height":"300px"}),
            ])),
        ]),
        card(html.Div([
            secao("Detalhamento das sessões"),
            html.Div(id="tabela-eventos", style={"marginTop":"12px"}),
        ])),
    ])

@app.callback(
    Output("kpis-eventos","children"),
    Output("graf-gantt","figure"),
    Output("graf-dur","figure"),
    Output("tabela-eventos","children"),
    Input("filtro-eventos-mot","value"),
)
def atualizar_eventos(filtro):
    ses_f = sessoes[sessoes["Motorista"].isin(filtro)] if filtro else sessoes.copy()
    sd    = ses_f[ses_f["Status"]=="Dentro"].copy().reset_index(drop=True)
    sd["Label"] = sd.apply(
        lambda r: f"{r['Motorista']}  •  {r['Inicio'].strftime('%d/%m  %H:%M')} – {r['Fim'].strftime('%H:%M')}",
        axis=1
    )

    kpis = [
        kpi("Entradas na cerca",   str(len(sd))),
        kpi("Veículo envolvido",   "V-1002"),
        kpi("Dias com ocorrência", "2 dias"),
        kpi("Motoristas na base",  "Ana Costa / Marcos Oliveira"),
    ]

    if len(sd) == 0:
        fig_vazio = go.Figure()
        fig_vazio.update_layout(**lm())
        return kpis, fig_vazio, fig_vazio, html.P("Nenhuma sessão encontrada.")

    fig_gantt = go.Figure()
    for mot, cor in COR_MOT.items():
        d = sd[sd["Motorista"]==mot]
        if len(d):
            fig_gantt.add_trace(go.Bar(
                name=mot,
                x=d["Duracao_min"],
                y=d["Label"],
                orientation="h",
                marker_color=cor, marker_line_width=0,
                text=d["Duracao_min"].apply(lambda v: f"{v:.1f} min"),
                textposition="inside",
                textfont=dict(size=11, color=BRANCO),
                customdata=d[["Inicio","Fim","Veículo"]].values,
                hovertemplate=(
                    "<b>%{customdata[2]}</b><br>"
                    "Entrada: %{customdata[0]|%d/%m %H:%M}<br>"
                    "Saída: %{customdata[1]|%d/%m %H:%M}<br>"
                    "Duração: %{x:.1f} min<extra></extra>"
                ),
            ))
    fig_gantt.update_layout(
        **lm(t=24, b=24, l=260, r=40),
        barmode="group", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
        xaxis={**XAXIS, "title": "Duração (minutos)"},
        yaxis={**YAXIS, "showgrid": False, "title": None, "autorange": "reversed"},
    )

    fig_dur = go.Figure()
    for mot, cor in COR_MOT.items():
        d = sd[sd["Motorista"]==mot]
        if len(d):
            fig_dur.add_trace(go.Bar(
                name=mot, x=d["Label"], y=d["Duracao_min"],
                marker_color=cor, width=0.5, marker_line_width=0,
                text=d["Duracao_min"].apply(lambda v: f"{v:.1f} min"),
                textposition="outside", textfont=dict(size=11, color=CINZA_600),
            ))
    fig_dur.update_layout(
        **lm(t=24, b=80, l=48, r=24),
        barmode="group", showlegend=False,
        xaxis={**XAXIS, "title": None, "tickangle": -15},
        yaxis={**YAXIS, "title": "Minutos"},
    )

    tbl_d = ses_f[ses_f["Status"]=="Dentro"][
        ["Veículo","Inicio","Fim","Duracao_min","Motorista"]].copy()
    tbl_d["Inicio"]      = tbl_d["Inicio"].dt.strftime("%d/%m/%Y %H:%M")
    tbl_d["Fim"]         = tbl_d["Fim"].dt.strftime("%d/%m/%Y %H:%M")
    tbl_d["Duracao_min"] = tbl_d["Duracao_min"].apply(lambda v: f"{v} min")
    tbl = tabela(tbl_d, {"Veículo":"Veículo","Inicio":"Entrada","Fim":"Saída",
                          "Duracao_min":"Duração","Motorista":"Motorista"})
    return kpis, fig_gantt, fig_dur, tbl


# ─────────────────────────────────────────
# 6. RODAR
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)