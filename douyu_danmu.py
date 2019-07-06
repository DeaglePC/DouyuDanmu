# coding: utf-8
"""
调用入口
"""
import signal
import sys

from douyu_chat_msg_handler import DouyuChatMsgHandler

dy = DouyuChatMsgHandler()


def signal_handler(signal, frame):
    dy.stop()
    print("bye...")
    # raise KeyboardInterrupt


def main():
    signal.signal(signal.SIGINT, signal_handler)

    need_save = False

    if len(sys.argv) == 2:
        room_id = int(sys.argv[1])
    elif len(sys.argv) == 3:
        room_id = int(sys.argv[1])
        if sys.argv[2] == "--save":
            need_save = True
        else:
            print("unknown param!")
            return
    else:
        print("你还是输入一个房间号吧！")
        return

    dy.set_room(room_id)
    dy.set_save(need_save)
    dy.run()


if __name__ == '__main__':
    main()
