import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# โหลดข้อมูลจาก CSV (ปรับ path ให้เหมาะกับเครื่องคุณ)
df = pd.read_csv(r"D:\Ecosystme\enhanced_tcas_data_20250727_205010.csv", encoding='utf-8')

# สร้าง Dash App
app = dash.Dash(__name__)
app.title = "TCAS Cyberpunk Dashboard"

columns = df.columns.tolist()

# Cyberpunk Color Palette
CYBERPUNK_COLORS = {
    'primary_bg': '#0a0a0a',
    'secondary_bg': '#1a1a2e',
    'card_bg': 'rgba(22, 22, 50, 0.9)',
    'neon_cyan': '#00ffff',
    'neon_pink': '#ff0080',
    'neon_purple': '#8a2be2',
    'neon_green': '#39ff14',
    'neon_orange': '#ff6600',
    'text_primary': '#ffffff',
    'text_secondary': '#cccccc',
    'accent': '#ff00ff'
}

# สไตล์หลักของแอป - ใช้ style inline เพื่อให้แน่ใจว่าทำงาน
main_bg_style = {
    'background': f'radial-gradient(circle at 20% 20%, {CYBERPUNK_COLORS["neon_purple"]}22 0%, transparent 50%), radial-gradient(circle at 80% 80%, {CYBERPUNK_COLORS["neon_cyan"]}22 0%, transparent 50%), linear-gradient(135deg, {CYBERPUNK_COLORS["primary_bg"]} 0%, {CYBERPUNK_COLORS["secondary_bg"]} 100%)',
    'minHeight': '100vh',
    'padding': '20px',
    'fontFamily': '"Courier New", monospace',
    'color': CYBERPUNK_COLORS['text_primary'],
    'fontSize': '14px'
}

# สไตล์ของ Card แบบ Cyberpunk
def get_card_style(border_color=CYBERPUNK_COLORS["neon_cyan"]):
    return {
        'background': f'linear-gradient(135deg, {CYBERPUNK_COLORS["card_bg"]}, rgba(138, 43, 226, 0.1))',
        'border': f'3px solid {border_color}',
        'borderRadius': '15px',
        'padding': '25px',
        'margin': '20px',
        'boxShadow': f'0 0 25px {border_color}50, inset 0 0 25px rgba(138, 43, 226, 0.1)',
        'fontFamily': '"Courier New", monospace',
        'position': 'relative',
        'overflow': 'hidden',
        'transition': 'all 0.3s ease'
    }

# Header style แบบ Cyberpunk เข้ม
header_style = {
    'background': f'linear-gradient(45deg, {CYBERPUNK_COLORS["neon_pink"]}, {CYBERPUNK_COLORS["neon_purple"]}, {CYBERPUNK_COLORS["neon_cyan"]})',
    'backgroundSize': '400% 400%',
    'textAlign': 'center',
    'padding': '40px',
    'margin': '0 0 40px 0',
    'borderRadius': '20px',
    'boxShadow': f'0 0 40px {CYBERPUNK_COLORS["neon_pink"]}80, 0 0 60px {CYBERPUNK_COLORS["neon_cyan"]}50',
    'border': f'3px solid {CYBERPUNK_COLORS["neon_cyan"]}',
    'position': 'relative'
}

# Title style
title_style = {
    'color': '#000000',  # สีดำเพื่อให้เด่นบน gradient
    'margin': '0',
    'fontFamily': '"Courier New", monospace',
    'fontWeight': 'bold',
    'fontSize': '2.5rem',
    'textShadow': '2px 2px 4px rgba(0,0,0,0.8)',
    'letterSpacing': '3px',
    'textTransform': 'uppercase'
}

# Dropdown style
dropdown_style = {
    'backgroundColor': CYBERPUNK_COLORS['secondary_bg'],
    'color': CYBERPUNK_COLORS['text_primary'],
    'border': f'2px solid {CYBERPUNK_COLORS["neon_green"]}',
    'borderRadius': '8px',
    'padding': '10px',
    'fontFamily': '"Courier New", monospace',
    'fontSize': '14px'
}

# Layout
app.layout = html.Div(
    style=main_bg_style,
    children=[
        # Header
        html.Div([
            html.H1(
                "⚡ TCAS CYBER DASHBOARD ⚡", 
                style=title_style
            ),
            html.P(
                "// DATA VISUALIZATION MATRIX //", 
                style={
                    'color': '#000000',
                    'fontSize': '1.2rem',
                    'margin': '10px 0 0 0',
                    'fontFamily': '"Courier New", monospace',
                    'letterSpacing': '2px',
                    'fontWeight': 'bold'
                }
            )
        ], style=header_style),

        # Main Content
        html.Div([
            # Control Panel
            html.Div([
                html.Label(
                    '>> SELECT DATA COLUMN:', 
                    style={
                        'fontWeight': 'bold',
                        'color': CYBERPUNK_COLORS['neon_green'],
                        'fontSize': '1.2rem',
                        'marginBottom': '15px',
                        'display': 'block',
                        'textTransform': 'uppercase',
                        'letterSpacing': '1px',
                        'textShadow': f'0 0 10px {CYBERPUNK_COLORS["neon_green"]}'
                    }
                ),
                dcc.Dropdown(
                    id='column-dropdown',
                    options=[{'label': f'◉ {col}', 'value': col} for col in columns],
                    value=columns[0],
                    style=dropdown_style
                )
            ], style=get_card_style(CYBERPUNK_COLORS["neon_green"])),
            
            # Charts Container
            html.Div([
                # Bar Chart
                html.Div([
                    html.H3("📊 BAR CHART", style={
                        'color': CYBERPUNK_COLORS['neon_cyan'],
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'textShadow': f'0 0 10px {CYBERPUNK_COLORS["neon_cyan"]}'
                    }),
                    dcc.Graph(id='bar-chart', style={'backgroundColor': 'transparent'})
                ], style={**get_card_style(CYBERPUNK_COLORS["neon_cyan"]), 'width': '48%', 'display': 'inline-block'}),

                # Pie Chart
                html.Div([
                    html.H3("🥧 PIE CHART", style={
                        'color': CYBERPUNK_COLORS['neon_pink'],
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'textShadow': f'0 0 10px {CYBERPUNK_COLORS["neon_pink"]}'
                    }),
                    dcc.Graph(id='pie-chart', style={'backgroundColor': 'transparent'})
                ], style={**get_card_style(CYBERPUNK_COLORS["neon_pink"]), 'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),

            # Data Table
            html.Div([
                html.H3(
                    "⚡ DATA MATRIX PREVIEW ⚡", 
                    style={
                        'marginBottom': '20px',
                        'color': CYBERPUNK_COLORS['neon_purple'],
                        'textAlign': 'center',
                        'fontSize': '1.5rem',
                        'textTransform': 'uppercase',
                        'letterSpacing': '2px',
                        'textShadow': f'0 0 15px {CYBERPUNK_COLORS["neon_purple"]}'
                    }
                ),
                html.Div(id='data-table', style={'overflowX': 'auto'})
            ], style=get_card_style(CYBERPUNK_COLORS["neon_purple"])),
        ], style={'maxWidth': '1400px', 'margin': '0 auto'})
    ]
)

# Callback สำหรับอัปเดตกราฟและตาราง
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('data-table', 'children')],
    [Input('column-dropdown', 'value')]
)
def update_dashboard(selected_column):
    value_counts = df[selected_column].value_counts().nlargest(10)

    # Cyberpunk color sequence
    cyber_colors = [
        CYBERPUNK_COLORS['neon_cyan'], 
        CYBERPUNK_COLORS['neon_pink'], 
        CYBERPUNK_COLORS['neon_purple'], 
        CYBERPUNK_COLORS['neon_green'],
        CYBERPUNK_COLORS['neon_orange'],
        '#ff1493',  # Deep pink
        '#00ff7f',  # Spring green
        '#ff4500',  # Orange red
        '#9400d3',  # Violet
        '#00bfff'   # Deep sky blue
    ]

    # Bar Chart with Enhanced Cyberpunk styling
    bar_fig = go.Figure()
    
    for i, (category, count) in enumerate(value_counts.items()):
        bar_fig.add_trace(go.Bar(
            x=[category],
            y=[count],
            name=str(category),
            marker=dict(
                color=cyber_colors[i % len(cyber_colors)],
                line=dict(color='white', width=2)
            ),
            hovertemplate=f'<b>{category}</b><br>Count: {count}<extra></extra>'
        ))
    
    bar_fig.update_layout(
        title=dict(
            text=f'⚡ DATA COUNT: {selected_column.upper()} ⚡',
            font=dict(
                color='white', 
                size=20, 
                family="Courier New"
            ),
            x=0.5
        ),
        plot_bgcolor='rgba(10,10,10,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white', 
            family="Courier New"
        ),
        xaxis=dict(
            gridcolor='rgba(0,255,255,0.3)',
            title=dict(
                text=selected_column.upper(), 
                font=dict(
                    color=CYBERPUNK_COLORS['neon_green'],
                    family="Courier New",
                    size=14
                )
            ),
            tickfont=dict(color='white', size=12)
        ),
        yaxis=dict(
            gridcolor='rgba(255,0,128,0.3)',
            title=dict(
                text='COUNT', 
                font=dict(
                    color=CYBERPUNK_COLORS['neon_pink'],
                    family="Courier New",
                    size=14
                )
            ),
            tickfont=dict(color='white', size=12)
        ),
        margin=dict(l=60, r=40, t=80, b=60),
        showlegend=False
    )

    # Pie Chart with Enhanced Cyberpunk styling
    pie_fig = go.Figure(data=[
        go.Pie(
            labels=value_counts.index,
            values=value_counts.values,
            marker=dict(
                colors=cyber_colors[:len(value_counts)],
                line=dict(color='white', width=3)
            ),
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}<extra></extra>',
            textfont=dict(
                color='white', 
                family="Courier New",
                size=12
            ),
            textinfo='label+percent'
        )
    ])
    
    pie_fig.update_layout(
        title=dict(
            text=f'⚡ DATA DISTRIBUTION: {selected_column.upper()} ⚡',
            font=dict(
                color='white', 
                size=20, 
                family="Courier New"
            ),
            x=0.5
        ),
        plot_bgcolor='rgba(10,10,10,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white', 
            family="Courier New"
        ),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # สร้างตารางข้อมูล 10 แถวแรก แบบ Cyberpunk สุดเข้ม
    table_rows = []
    for i in range(min(len(df), 10)):
        row_cells = []
        for col in df.columns:
            cell_style = {
                'padding': '15px',
                'border': f'1px solid {CYBERPUNK_COLORS["neon_cyan"]}',
                'backgroundColor': f'rgba(22, 22, 50, {0.8 if i % 2 == 0 else 0.6})',
                'color': 'white',
                'fontFamily': '"Courier New", monospace',
                'textAlign': 'center',
                'fontSize': '13px'
            }
            row_cells.append(html.Td(str(df.iloc[i][col]), style=cell_style))
        table_rows.append(html.Tr(row_cells))

    table_html = html.Table([
        html.Thead(
            html.Tr([
                html.Th(
                    f'◉ {col}', 
                    style={
                        'padding': '20px',
                        'background': f'linear-gradient(45deg, {CYBERPUNK_COLORS["neon_cyan"]}, {CYBERPUNK_COLORS["neon_purple"]})',
                        'color': 'black',
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                        'fontFamily': '"Courier New", monospace',
                        'textTransform': 'uppercase',
                        'letterSpacing': '1px',
                        'border': f'2px solid {CYBERPUNK_COLORS["neon_cyan"]}',
                        'fontSize': '14px'
                    }
                ) for col in df.columns
            ])
        ),
        html.Tbody(table_rows)
    ], 
    style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'border': f'3px solid {CYBERPUNK_COLORS["neon_cyan"]}',
        'borderRadius': '10px',
        'overflow': 'hidden',
        'boxShadow': f'0 0 20px {CYBERPUNK_COLORS["neon_cyan"]}50'
    })

    return bar_fig, pie_fig, table_html

# รันแอป
if __name__ == '__main__':
    app.run(debug=True, port=8051)  # เปลี่ยน port เพื่อ clear cache