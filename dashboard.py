import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# โหลดข้อมูลจาก CSV (ปรับ path ให้เหมาะกับเครื่องคุณ)
df = pd.read_csv(r"D:\Ecosystme\enhanced_tcas_data_20250727_205010.csv", encoding='utf-8')

# สร้าง Dash App
app = dash.Dash(__name__)
app.title = "Dashboard TCAS ภาษาไทย"

# รายการคอลัมน์ทั้งหมด
columns = df.columns.tolist()

# Layout
app.layout = html.Div([
    html.H1("แดชบอร์ดข้อมูล TCAS", style={'textAlign': 'center', 'fontFamily': 'Arial'}),

    html.Div([
        html.Label('เลือกคอลัมน์ที่จะแสดงกราฟ:', style={'fontFamily': 'Arial'}),
        dcc.Dropdown(
            id='column-dropdown',
            options=[{'label': col, 'value': col} for col in columns],
            value=columns[0],
            style={'width': '50%', 'fontFamily': 'Arial'}
        ),
    ]),
    
    html.Br(),
    
    dcc.Graph(id='bar-chart'),
    
    html.Br(),
    
    dcc.Graph(id='pie-chart'),

    html.Br(),

    html.H4("ตัวอย่างตารางข้อมูล", style={'fontFamily': 'Arial'}),
    html.Div(id='data-table', style={'overflowX': 'scroll', 'fontFamily': 'Arial'})
])

# Callback สำหรับอัปเดตกราฟและตาราง
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('data-table', 'children')],
    [Input('column-dropdown', 'value')]
)
def update_dashboard(selected_column):
    value_counts = df[selected_column].value_counts().nlargest(10)

    # Bar Chart
    bar_fig = px.bar(
        x=value_counts.index, 
        y=value_counts.values,
        labels={'x': selected_column, 'y': 'จำนวน'},
        title=f'จำนวนแยกตาม {selected_column}'
    )

    # Pie Chart
    pie_fig = px.pie(
        values=value_counts.values,
        names=value_counts.index,
        title=f'สัดส่วนของ {selected_column}'
    )

    # สร้างตารางข้อมูล 10 แถวแรก
    table_html = html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), 10))
        ])
    ])

    return bar_fig, pie_fig, table_html

# รันแอป
if __name__ == '__main__':
    app.run(debug=True)

