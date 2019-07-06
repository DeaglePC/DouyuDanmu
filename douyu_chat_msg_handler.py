# coding: utf-8
"""
弹幕数据自定义处理
"""
import time

from pymongo import MongoClient

from douyu_chat_reader import DouyuChatReader
from douyu_chat_msg_parser import DouyuChatMsgFormatTool
import config


def format_date(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000))


class MsgType:
    CHAT_MSG = 1
    GIFT = 2
    UNKNOWN = -1

    MSG = {
        "chatmsg": CHAT_MSG,
        "dgb": GIFT,
        "unknown": UNKNOWN,
    }

    MSG_CODE = {v: k for k, v in MSG.items()}

    @classmethod
    def name(cls, msg_code):
        return cls.MSG_CODE.get(msg_code, "unknown")

    @classmethod
    def code(cls, msg_name):
        return cls.MSG.get(msg_name, cls.UNKNOWN)


class DouyuChatMsgHandler(DouyuChatReader):

    def __init__(self, room_id=None):
        super().__init__(room_id)

        try:
            self._db = MongoClient(config.MONGODB_URI)[config.DB_NAME]
        except Exception as err:
            print(err)
            self._db = None

        self._collection_name = self._get_coll_name(room_id) if room_id else None

        self._need_save = False
        self._save_buf = list()

    @property
    def need_save(self):
        return self._need_save

    def set_save(self, need_save):
        if isinstance(need_save, bool):
            self._need_save = need_save

    @staticmethod
    def _get_coll_name(id_):
        return "dy_" + str(id_)

    @staticmethod
    def _format_chat_msg(res_data):
        """
        弹幕文字信息，自定义格式
        :param res_data:
        :return:
        """
        return {
            "content": res_data.get("txt", ""),
            "uid": res_data.get("uid", ""),
            "username": res_data.get("nn", ""),
            "level": int(res_data.get("level", "")),
            "time": format_date(int(res_data.get("cst"))) if res_data.get("cst") else "",
        }

    @staticmethod
    def _display_chat_data(data_dict):
        print(
            "[{}] {} ({}): {}".format(
                data_dict["time"], data_dict["username"], data_dict["level"], data_dict["content"]
            )
        )

    def _save_data(self, data_dict):
        if not self._db:
            return

        if not self._collection_name:
            print("unknown collection name")
            return

        self._save_buf.append(data_dict)

        if len(self._save_buf) == config.SAVE_CONFIG.get(self._room_id, 1):
            col = self._db[self._collection_name]
            col.insert_many(self._save_buf)
            self._save_buf.clear()

    def _handle_chat_msg(self, res_data):
        chat_msg_dict = self._format_chat_msg(res_data)
        self._display_chat_data(chat_msg_dict)
        self._save_data(chat_msg_dict) if self.need_save else None

    @staticmethod
    def _display_gift_msg(res_data):
        print(res_data)
        print(
            "{}({}) 送出{}个{}, {}连击".format(
                res_data.get("nn", ""),
                res_data.get("level", ""),
                res_data.get("gfcnt", ""),
                res_data.get("gfid", ""),
                res_data.get("hits", ""),
            )
        )

    def _handle_gift_msg(self, res_data):
        self._display_gift_msg(res_data)

    def _handle_recv_data(self, data):
        # print(data)
        res_data = DouyuChatMsgFormatTool.deserialize(data)
        if not res_data:
            return

        msg_type = res_data.get("type")
        if not msg_type:
            return

        msg_type = MsgType.code(msg_type)

        if msg_type == MsgType.CHAT_MSG:
            self._handle_chat_msg(res_data)
        elif msg_type == MsgType.GIFT:
            # self._handle_gift_msg(res_data)
            pass
        # more type deal...

    def set_room(self, room_id):
        super().set_room(room_id)
        self._collection_name = self._get_coll_name(room_id)
