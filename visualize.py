import csv
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

app = dash.Dash()

traffics = []
date = []
with open("traffics.csv", "r") as f:
    for x in csv.reader(f, delimiter=','):
        traffics.append(float(x[2]))
        date.append(x[-1])

current_date_traffic = []
one_day_traffics = []
one_day_traffics_date = []
for i in range(len(date)):
    # 文字列から日付型へ変換
    # 年月日のみを取得する
    current_date = datetime.datetime.strptime(date[i], "%Y/%m/%d %H:%M:%S")
    if i == len(date)-1:
        # yesterday = current_date - datetime.timedelta(days=1)
        # one_day_traffics_date.append(yesterday.date())
        one_day_traffics_date.append(current_date.date())
        one_day_traffics.append(traffics[-1])
        # one_day_traffics.append(0)
        break

    # 日付のみを取得し、1日分のデータ通信量を求める
    # 一日のスタートはAM02:00からとする（L01の仕様っぽい）
    day_time = datetime.time(2, 0, 0, 0)
    if current_date.hour != day_time.hour:
        current_date_traffic.append(traffics[i])
    else:
        one_day_traffics.append(max(current_date_traffic))
        # １日の通信量はAM02:00にリセットされるので日付を１日戻す
        today = current_date - datetime.timedelta(days=1)
        one_day_traffics_date.append(today.date())
        current_date_traffic = []

latest_three_days_traffic = 0
if len(one_day_traffics) >= 3:
    latest_three_days_traffic = sum(one_day_traffics[-3:])
else:
    latest_three_days_traffic = sum(one_day_traffics)
latest_three_days_traffic = round(latest_three_days_traffic, 3)
datetime = [datetime.datetime.strptime(x, "%Y/%m/%d %H:%M:%S").strftime('%d日 %H時') for x in date]

app.layout = html.Div(children=[
    html.H1('通信量'),

    html.H2('直近3日間の通信量：{} GB'.format(latest_three_days_traffic)),
    dcc.Graph(
        id='per_hour',
        figure={
            'data':[
                {'x':datetime, 'y':traffics}
            ]
        }
    ),

    dcc.Graph(
        id='per_day',
        figure={
            'data':[
                {'x': one_day_traffics_date, 'y': one_day_traffics}
            ],
            'layout':go.Layout(
                xaxis={'tickformat': '%_m/%-d', 'dtick': 'D'}
            )
        }
    )
])

app.run_server()
