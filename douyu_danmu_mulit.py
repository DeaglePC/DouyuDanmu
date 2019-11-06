# coding: utf-8
import asyncio
import signal
import functools
from concurrent.futures import CancelledError
import sys

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
        await asyncio.gather(*funcs)


dy_dm_collector = DouyuDanmuCollector(config.COLLECTOR_ROOMS_CFG)


def ask_exit(signame, loop):
    print("got signal %s: exit" % signame)
    for task in asyncio.Task.all_tasks():
        task.cancel()

    sys.exit(1)


async def main():
    loop = asyncio.get_running_loop()

    for signame in {'SIGINT', 'SIGTERM'}:
        try:
            loop.add_signal_handler(
                getattr(signal, signame),
                functools.partial(ask_exit, signame, loop)
            )
        except NotImplementedError:
            continue

    await dy_dm_collector.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except CancelledError as err:
        print(err)
