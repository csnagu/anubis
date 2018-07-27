from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
import csv
import re

url = 'http://speedwifi.home/html/login.htm'

# Selenium settings
driver = webdriver.Chrome()

driver.get(url)
html = driver.page_source.encode('utf-8')
driver.quit()

# parse the response
soup = BeautifulSoup(html, 'html.parser')
today_down = soup.find(id='login_CurrentDownloadThroughput')
today_up = soup.find(id='login_CurrentUploadThroughput')

traff_info = list()

# 通信量を取得した日時
now_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

# 上り下りの通信量
traff_info.append(today_down.get_text())
traff_info.append(today_up.get_text())

for i, traff in enumerate(traff_info):
    # 数字のみ取得する正規表現
    regex = r'([0-9]+\.?[0-9]*)'
    traff_num = float(re.match(regex, traff).group())

    # MB表記のものをGBの単位へ変換する
    if re.search('MB', traff):
        traff_info[i] = traff_num / 1000.0
    else:
        traff_info[i] = traff_num
    traff_info[i] = round(traff_info[i], 2)

traff_info.append(round(sum(traff_info), 2))
traff_info.append(now_time)

with open('traffics.csv', 'a') as f:
    write = csv.writer(f, lineterminator='\n')
    write.writerow(traff_info)
