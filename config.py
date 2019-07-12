# coding:utf-8
import os

ROOMS = {
    "qz": 9418,
    "dsm": 606118,
    "xj": 74751,
    "yz": 71415,
    "lx": 52319,
}

# 每几条数据写入数据库一次
SAVE_CONFIG = {
    74751: 10,
    606118: 10,
    9418: 5,
    52319: 3,
}

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://user:pw@localhost/db")
DB_NAME = "db"
