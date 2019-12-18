from __future__ import print_function
import time
import schedule
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import mongodb
import linenotify

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


# 修改為你的權杖內容
token = ''
startmsg = '股價起始執行時間:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
linenotify.lineNotifyMessage(token, msg=startmsg)


def job():
    # 執行時間測試，確認時間有在執行  若想確認是否有跑排程    打開以下註記
    # linenotify.lineNotifyMessage(token, msg='執行時間:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data = mongodb.show_user_stock_fountion()
    for i in data:
        stock = i['stock']
        bs = i['bs']
        price = i['price']
        url = 'https://tw.stock.yahoo.com/q/q?s=' + stock
        list_req = requests.get(url)
        soup = BeautifulSoup(list_req.content, "html.parser")
        getstock = soup.findAll('b')[1].text  # 裡面所有文字內容
        if float(getstock):
            if bs == '<':
                if float(getstock) < price:
                    get = stock + '(可買進)的價格：' + getstock
                    linenotify.lineNotifyMessage(token, get)

            else:
                if float(getstock) > price:
                    get = stock + '(可賣出)的價格：' + getstock
                    linenotify.lineNotifyMessage(token, get)
        else:
            linenotify.lineNotifyMessage(token, msg='抓取有問題異常')


# 判斷一到五  台股開放時間範圍時間 開放時間早上九點-下午一點半
start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:00', '%Y-%m-%d%H:%M')
end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '13:30', '%Y-%m-%d%H:%M')
now_time = datetime.datetime.now()
weekday = datetime.datetime.now().weekday()
if weekday >= 0 and weekday <= 4:
    if now_time > start_time and now_time < end_time:
        second_5_j = schedule.every(10).seconds.do(job)

# 無窮迴圈
while True:
    schedule.run_pending()
    time.sleep(1)