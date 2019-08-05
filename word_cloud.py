# coding: utf-8
import os
from datetime import date, datetime, timedelta

from PIL import Image
from pymongo import MongoClient
from wordcloud import WordCloud, ImageColorGenerator
import jieba
import matplotlib.pyplot as plt
import numpy as np

import config
from douyu_chat_msg_handler import DouyuChatMsgHandler, TIME_FORMAT


def get_wordcloud_img_name(room):
    return "_".join([str(room), datetime.now().strftime("%Y%m%d%H%M%S")])


class DanmuCloud:
    BK_IMG_PATH = "./res/kn2.jpg"
    FONT_PATH = "./res/SIMYOU.TTF"
    WD_IMG_PATH = "./wordcloud_images"

    def __init__(self):
        self._db = MongoClient(config.MONGODB_URI)[config.DB_NAME]

        self._bk_image = np.array(Image.open(self.BK_IMG_PATH))
        self._wd = WordCloud(
            font_path=self.FONT_PATH,
            background_color="white",
            collocations=False,
            mask=self._bk_image
        )

    def _get_col(self, room):
        return self._db[DouyuChatMsgHandler.get_coll_name(room)]

    @staticmethod
    def _get_date_filter(dm_date):
        if dm_date and not isinstance(dm_date, date):
            raise TypeError

        start_date = datetime(dm_date.year, dm_date.month, dm_date.day)
        end_date = start_date + timedelta(days=1)

        return {
            "$gte": start_date.strftime(TIME_FORMAT),
            "$lt": end_date.strftime(TIME_FORMAT),
        }

    def read_danmu(self, room, dm_date=None):
        """
        读取指定房间的弹幕
        :param room: 房间id
        :param dm_date: 哪天的, 默认全部
        :return:
        """
        if dm_date and not isinstance(dm_date, date):
            raise TypeError

        col = self._get_col(room)
        proj = {"_id": 0, "content": 1}

        return col.find({"time": self._get_date_filter(dm_date)}, proj) if dm_date \
            else col.find(projection=proj)

    @staticmethod
    def get_split_words(res_data):
        txt_list = list()

        for item in res_data:
            jb = jieba.cut(item["content"])
            txt_list += [_item for _item in jb]

        return txt_list

    def generate_pic(self, room, dm_date=None):
        res_data = self.read_danmu(room, dm_date)
        words = self.get_split_words(res_data)
        if not words:
            return
        print("words: {}".format(len(words)))

        wordcloud = self._wd.generate(" ".join(words))

        image_colors = ImageColorGenerator(self._bk_image)
        plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
        plt.axis("off")
        plt.savefig(os.path.join(self.WD_IMG_PATH, get_wordcloud_img_name(room)))
        plt.show()


def main():
    c = DanmuCloud()
    c.generate_pic(
        606118,
        date(2019, 8, 4),
    )


if __name__ == '__main__':
    main()
