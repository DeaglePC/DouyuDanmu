# coding: utf-8
import asyncio

from douyu_chat_msg_handler import DouyuChatMsgHandler
import config


class DouyuDanmuCollector:

    def __init__(self, cfg):
        if not cfg or not isinstance(cfg, dict):
            raise TypeError

        self.__rooms_cfg = cfg
        self.__dys = list()

        self.__init_dy()

    def __init_dy(self):
        for room, cfg in self.__rooms_cfg.items():
            tmp_dy = DouyuChatMsgHandler(room)

            tmp_dy.set_save(True)
            tmp_dy.set_color(cfg["color"])

            self.__dys.append(tmp_dy)

    async def start(self):
        funcs = [dy.run() for dy in self.__dys]
        print(funcs)
        await asyncio.gather(*funcs)


dy_dm_collector = DouyuDanmuCollector(config.COLLECTOR_ROOMS_CFG)


async def main():
    await dy_dm_collector.start()


if __name__ == '__main__':
    asyncio.run(main())
