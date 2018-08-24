import csv
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

app = dash.Dash()

def get_traffic_and_date(filename):
    traffic = []
    date = []
    with open(filename, "r") as f:
        for x in csv.reader(f, delimiter=','):
            traffic.append(float(x[2]))
            date.append(x[-1])
    return traffic, date

traffic, date = get_traffic_and_date('traffics.csv')

current_date_traffic = []
one_day_traffics = []
one_day_traffics_date = []
for i in range(len(date)):
    # 文字列から日付型へ変換
    # 年月日のみを取得する
    current_date = datetime.datetime.strptime(date[i], "%Y/%m/%d %H:%M:%S")
    if i == len(date)-1:
        if current_date.hour != 0:
            one_day_traffics_date.append(current_date.date())
        else:
            one_day_traffics_date.append(datetime.datetime.strptime(date[i-1], "%Y/%m/%d %H:%M:%S").date())
        one_day_traffics.append(traffic[-1])
        break

    # 日付のみを取得し、1日分のデータ通信量を求める
    # 一日のスタートはAM02:00からとする（L01の仕様っぽい）
    day_time = datetime.time(4, 0, 0, 0)
    if current_date.hour != day_time.hour:
        current_date_traffic.append(traffic[i])
    else:
        one_day_traffics.append(max(current_date_traffic))
        # １日の通信量はAM02:00にリセットされるので日付を１日戻す
        today = current_date - datetime.timedelta(days=1)
        one_day_traffics_date.append(today.date())
        current_date_traffic = []

three_days_traffic_from_the_day_before = sum(one_day_traffics)
latest_three_days_traffic = sum(one_day_traffics)

if len(one_day_traffics) >= 4:
    three_days_traffic_from_the_day_before = sum(one_day_traffics[-4:-1])
if len(one_day_traffics) >= 3:
    latest_three_days_traffic = sum(one_day_traffics[-3:])

three_days_traffic_from_the_day_before = round(three_days_traffic_from_the_day_before, 3)
latest_three_days_traffic = round(latest_three_days_traffic, 3)
datetime = [datetime.datetime.strptime(x, "%Y/%m/%d %H:%M:%S").strftime('%d日 %H時') for x in date]

app.layout = html.Div(children=[
    html.H1('通信量'),

    html.Div('直近3日間の通信量：{} GB'.format(latest_three_days_traffic)),
    html.Div('前日から3日間の通信量：{} GB'.format(three_days_traffic_from_the_day_before)),

    html.Div([
        html.Label('表示するグラフの選択'),
        dcc.Dropdown(
            id='change-graph',
            options=[
                {'label':'hourly graph', 'value':'hourly'},
                {'label':'daily graph', 'value':'daily'}
            ],
            value='hourly'
        )
    ],
    style={'width':'50%'}),

    dcc.Graph(id='traffic-graph')
])

@app.callback(
    dash.dependencies.Output('traffic-graph', 'figure'),
    [dash.dependencies.Input('change-graph', 'value')])
def update_graph(selected_graph):
    if selected_graph == 'hourly':
        return {
            'data':[
                {'x':datetime, 'y':traffic}
            ]
        }
    if selected_graph == 'daily':
        return {
            'data':[
                {'x': one_day_traffics_date, 'y': one_day_traffics}
            ],
            'layout':go.Layout(
                xaxis={'tickformat': '%_m/%-d', 'dtick': 'D'}
            )
        }

if __name__ == '__main__':
    app.run_server()
