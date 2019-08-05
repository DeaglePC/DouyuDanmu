# coding: utf-8
import signal

from douyu_chat_msg_handler import DouyuChatMsgHandler
import config


class DouyuDanmuCollector:

    def __init__(self, cfg):
        if not cfg or not isinstance(cfg, dict):
            raise TypeError

        self._rooms_cfg = cfg
        self._dys = list()

        self._init_dy()

    def _init_dy(self):
        for room, cfg in self._rooms_cfg.items():
            tmp_dy = DouyuChatMsgHandler(room)

            tmp_dy.set_save(True)
            tmp_dy.set_color(cfg["color"])

            self._dys.append(tmp_dy)

    def start(self):
        for dy in self._dys:
            dy.run()

    def stop(self):
        for dy in self._dys:
            dy.stop()


dy_dm_collector = DouyuDanmuCollector(config.COLLECTOR_ROOMS_CFG)


def signal_handler(signal, frame):
    dy_dm_collector.stop()
    print("bye...")


def main():
    signal.signal(signal.SIGINT, signal_handler)

    dy_dm_collector.start()


if __name__ == '__main__':
    main()
