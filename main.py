# 載入LineBot所需要的套件
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb
import re
import time
import schedule
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import linenotify


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('')
# Channel Secret
handler = WebhookHandler('')
# Your User Id
line_bot_api.push_message('', TextSendMessage(text='你可以開始了'))

# 修改為你的權杖內容
token = ''
startmsg = '股價起始執行時間:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
linenotify.lineNotifyMessage(token, msg=startmsg)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id  
    usespeak = str(event.message.text)  
    if re.match('[0-9]{4}[<>][0-9]', usespeak):   
        mongodb.write_user_stock_fountion(stock=usespeak[0:4], bs=usespeak[4:5], price=usespeak[5:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak[0:4] + '已經儲存成功'))
        return 0
    elif re.match('刪除[0-9]{4}', usespeak):   
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak + '已經刪除成功'))
        return 0

def job():
    #執行時間測試，確認時間有在執行  若想確認是否有跑排程    打開以下註記
    #linenotify.lineNotifyMessage(token, msg='執行時間:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
# 主程式
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

