import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

def str2date(date):
    return datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S")

df = pd.read_csv('traffics.csv', names=('down', 'up', 'updown', 'date'))

current_date_traffic = []
one_day_traffic = []
one_day_traffic_date = []
for index, row in df.iterrows():
    # 文字列から日付型へ変換
    # 年月日のみを取得する
    current_date = str2date(row['date'])

    if index == len(df) - 1:
        if current_date.hour != 0:
            one_day_traffic_date.append(current_date.date())
        else:
            one_day_traffic_date.append(str2date(df.at[index-1, 'date']).date())
        one_day_traffic.append(row['updown'])
        break
    
    # 日付のみを取得し、1日分のデータ通信量を求める
    # 一日のスタートはAM04:00からとする（L01の仕様っぽい）
    day_time = datetime.time(4, 0, 0, 0)
    if current_date.hour != day_time.hour:
        current_date_traffic.append(row['updown'])
    else:
        one_day_traffic.append(max(current_date_traffic))
        # １日の通信量はAM02:00にリセットされるので日付を１日戻す
        today = current_date - datetime.timedelta(days=1)
        one_day_traffic_date.append(today.date())
        current_date_traffic = []

three_days_traffic_from_the_day_before = sum(one_day_traffic[-4:-1])
latest_3days = sum(one_day_traffic[-3:])

three_days_traffic_from_the_day_before = round(three_days_traffic_from_the_day_before, 3)
latest_3days = round(latest_3days, 3)
datetime = [str2date(x).strftime('%d日 %H時') for x in df['date']]

# 描画
app = dash.Dash()

app.layout = html.Div(children=[
    html.H1('通信量'),

    html.Div('直近3日間の通信量：{} GB'.format(latest_3days)),
    html.Div('前日から3日間の通信量：{} GB'.format(three_days_traffic_from_the_day_before)),

    html.Div([
        html.Label('表示するグラフの選択'),
        dcc.Dropdown(
            id='change-graph',
            options=[
                {'label':'Daily', 'value':'daily'},
                {'label':'Three Days', 'value':'three'},
                {'label':'Week', 'value':'week'}
            ],
            value='daily'
        )
    ],
    style={'width':'35%'}),

    dcc.Graph(id='traffic-graph')
])

@app.callback(
    dash.dependencies.Output('traffic-graph', 'figure'),
    [dash.dependencies.Input('change-graph', 'value')])

def update_graph(selected_graph):
    if selected_graph == 'daily':
        return {
            'data':[
                {'x': one_day_traffic_date, 'y': one_day_traffic}
            ],
            'layout':go.Layout(
                xaxis={'tickformat': '%_m/%-d', 'dtick': 'D'}
            )
        }
    elif selected_graph == 'three':
        return {
            'data':[
                {'x': one_day_traffic_date[-3:], 'y': one_day_traffic[-3:]}
            ],
            'layout':go.Layout(xaxis={'tickformat': '%_m/%-d', 'dtick': 'D'})
        }
    elif selected_graph == 'week':
        return {
            'data':[
                {'x': one_day_traffic_date[-7:], 'y': one_day_traffic[-7:]}
            ],
            'layout':go.Layout(xaxis={'tickformat': '%_m/%-d', 'dtick': 'D'})
        }

if __name__ == '__main__':
    app.run_server()
