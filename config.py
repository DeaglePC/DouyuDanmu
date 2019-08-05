# coding:utf-8
import os
from colorama import init, Fore

init(autoreset=True)

COLLECTOR_ROOMS_CFG = {
    9418: {
        "name": "qz",
        "save_rate": 5,
        "color": Fore.GREEN,
    },
    606118: {
        "name": "dsm",
        "save_rate": 10,
        "color": Fore.YELLOW,
    },
    74751: {
        "name": "xj",
        "save_rate": 10,
        "color": Fore.BLUE,
    },
    71415: {
        "name": "yz",
        "save_rate": 10,
        "color": Fore.CYAN,
    },
}

ROOMS = {
    "qz": 9418,
    "dsm": 606118,
    "xj": 74751,
    "yz": 71415,
    "lx": 52319,
    "6079602": 6079602,
    "by": 252802,
}

# 每几条数据写入数据库一次
SAVE_CONFIG = {
    74751: 10,
    606118: 10,
    9418: 5,
    52319: 3,
}

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://ddyy:123@localhost/danmu")
DB_NAME = "danmu"
