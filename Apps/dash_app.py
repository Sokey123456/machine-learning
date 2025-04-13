# dash_app.py
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# データ生成（同じ内容）
n_days = 64
n_terms = 31
dates = pd.date_range('2023-01-01', periods=n_days)
terms = np.arange(1, n_terms + 1)

x = np.tile(dates, n_terms)
y = np.repeat(terms, n_days)
base = np.sqrt(y) + 0.1 * np.sin(pd.factorize(x)[0] / 5) + np.random.normal(0, 0.05, size=len(x))
rate = 1.5 + (base - base.min()) / (base.max() - base.min()) * 3.0

df = pd.DataFrame({'date': x, 'term': y, 'rate': rate})
df['term'] = pd.Categorical(df['term'], categories=terms, ordered=True)
z_grid = df.pivot(index='term', columns='date', values='rate')

# Dash アプリ定義
def create_dash_app():
    app = Dash(__name__)
    app.layout = html.Div(    
        style={
           "backgroundColor": "#111111",   # ← ダーク背景
            "color": "white",               # ← テキストの色
            "minHeight": "100vh",              # ← 画面いっぱいに
            "padding": "20px"
        },
        children=[
            html.H2("3D Yield Curve: Click to Explore Cross Sections"),
            dcc.Graph(id='curve-graph', style={'height': '700px'}),
            html.Div(id='clicked-info', style={'margin': '20px', 'fontWeight': 'bold'}),
        ])

    @app.callback(
        Output('curve-graph', 'figure'),
        Output('clicked-info', 'children'),
        Input('curve-graph', 'clickData')
    )
    def update_graph(clickData):
        if clickData and 'points' in clickData:
            pt = clickData['points'][0]
            clicked_date = pd.to_datetime(pt['x'])
            clicked_term = int(pt['y'])
        else:
            clicked_date = dates[len(dates)//2]
            clicked_term = terms[len(terms)//2]

        rate_at_term = z_grid.loc[clicked_term, :]
        rate_at_date = z_grid[clicked_date]

        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "scene",  "colspan": 2}, None], [{"type": "xy"}, {"type": "xy"}]],
            column_widths=[0.5, 0.5],
            row_heights=[0.7, 0.3],
            horizontal_spacing=0.05,
            vertical_spacing=0.05,
            subplot_titles=(
                "3D Yield Surface",
                "",
                f"Term vs Rate @ {clicked_date.date()}",
                f"Date vs Rate @ {clicked_term}Y"
            )
        )

        fig.add_trace(go.Surface(
            z=z_grid.values,
            x=z_grid.columns,
            y=z_grid.index,
            colorscale='jet',
            showscale=True,
            name='Yield Surface',
            colorbar=dict(
                x=-0.2,
                len=0.75,
                title='Rate (%)'
            )
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=[clicked_date],
            y=[clicked_term],
            z=[z_grid.loc[clicked_term, clicked_date]],
            mode='markers',
            marker=dict(size=2, color='red'),
            name='Clicked Point'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=terms,
            y=rate_at_date.values,
            mode='lines+markers',
            name='YZ Projection',
            line=dict(color='blue'),
            marker=dict(color='blue')
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=dates,
            y=rate_at_term.values,
            mode='lines+markers',
            name='XZ Projection',
            line=dict(color='black'),
            marker=dict(color='black')
        ), row=2, col=2)

        fig.add_trace(go.Scatter3d(
            x=dates,
            y=[clicked_term] * len(dates),
            z=z_grid.loc[clicked_term, :].values,
            mode='lines',
            line=dict(color='black', width=10),
            name='XZ Section Line'
        ), row=1, col=1)

        fig.add_trace(go.Scatter3d(
            x=[clicked_date] * len(terms),
            y=terms,
            z=z_grid.loc[:, clicked_date].values,
            mode='lines',
            line=dict(color='blue', width=10),
            name='YZ Section Line'
        ), row=1, col=1)

        fig.update_layout(
            hovermode='x unified',
            height=700,
            scene=dict(uirevision='3d-scene')
        )

        info = f"Clicked Point → Date: {clicked_date.date()}, Term: {clicked_term}Y"
        return fig, info

    return app

def run_dash_server():
    app = create_dash_app()
    app.run_server(host="127.0.0.1", debug=False, use_reloader=False, port=8050)
    
