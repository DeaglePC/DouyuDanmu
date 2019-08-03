# coding: utf-8
import signal

from douyu_chat_msg_handler import DouyuChatMsgHandler
import config


class DouyuDanmuCollector:

    def __init__(self, rooms):
        if not rooms:
            return

        self._rooms = rooms
        self._dys = list()

        self._init_dy()

    def _init_dy(self):
        for room in self._rooms:
            tmp_dy = DouyuChatMsgHandler(room)
            tmp_dy.set_save(True)
            self._dys.append(tmp_dy)

    def start(self):
        for dy in self._dys:
            dy.run()

    def stop(self):
        for dy in self._dys:
            dy.stop()


dy_dm_collector = DouyuDanmuCollector([v for k, v in config.ROOMS.items()])


def signal_handler(signal, frame):
    dy_dm_collector.stop()
    print("bye...")


def main():
    signal.signal(signal.SIGINT, signal_handler)

    dy_dm_collector.start()


if __name__ == '__main__':
    main()
