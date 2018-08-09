from datetime import datetime
from selenium import webdriver
import csv
import os
import re

url = 'http://speedwifi.home/html/login.htm'

# Selenium settings
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', chrome_options=options)

driver.get(url)
today_down = driver.find_element_by_id('login_CurrentDownloadThroughput').text
today_up = driver.find_element_by_id('login_CurrentUploadThroughput').text
driver.quit()

traff_info = []

# date of get traffics e.g.) 2018/05/25 20:03:23
now_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
traff_info.append(today_down)
traff_info.append(today_up)

# log
cwd = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(cwd, 'log.csv')
with open(csv_path, 'a') as f:
    write = csv.writer(f, lineterminator='\n')
    write.writerow(traff_info)

for i, traff in enumerate(traff_info):
    # regex for get figures only
    regex = r'([0-9]+\.?[0-9]*)'
    traff_num = float(re.match(regex, traff).group())

    # convert MB to GB
    if re.search('KB', traff):
        traff_info[i] = traff_num / 1000000.0
    else if re.search('MB', traff):
        traff_info[i] = traff_num / 1000.0
    else:
        traff_info[i] = traff_num
    traff_info[i] = round(traff_info[i], 2)

traff_info.append(round(sum(traff_info), 2))
traff_info.append(now_time)

cwd = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(cwd, 'traffics.csv')
with open(csv_path, 'a') as f:
    write = csv.writer(f, lineterminator='\n')
    write.writerow(traff_info)
