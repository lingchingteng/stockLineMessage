# -*- coding: utf-8 -*-
from pymongo import MongoClient
import urllib.parse
import datetime

Authdb = 'mydb'


def constructor():
    client = MongoClient("")
    db = client[Authdb]
    return db


# ----------------------------儲存使用者的股票--------------------------
def write_user_stock_fountion(stock, bs, price):
    db = constructor()
    collect = db['mystock']
    collect.insert({"stock": stock,
                    "data": 'care_stock',
                    "bs": bs,
                    "price": float(price),
                    "date_info": datetime.datetime.utcnow()
                    })


# ----------------------------殺掉使用者的股票--------------------------
def delete_user_stock_fountion(stock):
    db = constructor()
    collect = db['mystock']
    collect.remove({"stock": stock})


# ----------------------------秀出使用者的股票--------------------------
def show_user_stock_fountion():
    db = constructor()
    collect = db['mystock']
    cel = list(collect.find({"data": 'care_stock'}))
    return cel



