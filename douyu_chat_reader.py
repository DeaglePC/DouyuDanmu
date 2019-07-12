# coding: utf-8
"""
连接斗鱼弹幕服务器
"""

import socket
import threading
import time
import struct


class DouyuChatReader(object):

    def __init__(self, room_id=None):
        self._room_id = room_id

        self._conn = None
        self._stop_lock = threading.Lock()

        self._recv_thread = None
        self._is_stop = False

    HEART_INTERVAL = 35
    HEADER_SIZE = 12  # 4 + 4 + 2 + 1 + 1

    def _connect_chat_server(self):
        host = socket.gethostbyname("openbarrage.douyutv.com")
        port = 8601

        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect((host, port))
        print("连接弹幕服务器成功...")

    @staticmethod
    def _pack_header(msg):
        if not isinstance(msg, str):
            raise TypeError("消息类型必须为str")

        msg = msg.encode("utf-8")
        data_length = len(msg) + 8
        msg_type = 689  # client msg type

        msg_head = (
                int.to_bytes(data_length, 4, "little")  # 消息长度
                + int.to_bytes(data_length, 4, "little")  # 消息长度
                + struct.pack("h", msg_type)  # 消息类型
                + b'\x00\x00'  # 加密字段 保留字段
        )

        return msg_head + msg

    def _send_req_msg(self, msg):
        if not isinstance(msg, str):
            raise TypeError("消息类型必须为str")

        msg = self._pack_header(msg)
        sent = 0
        while sent < len(msg):
            tn = self._conn.send(msg[sent:])
            sent = sent + tn

    def _logout(self):
        msg = "type@=logout/"
        self._send_req_msg(msg)

    def _login(self):
        msg = "type@=loginreq/roomid@={}/\0".format(self._room_id)
        self._send_req_msg(msg)

    def _join_group(self):
        msg = "type@=joingroup/rid@={}/gid@=-9999/\0".format(self._room_id)
        self._send_req_msg(msg)

    def _recv_target_num(self, num):
        """
        从弹幕服务器接收num字节的数据
        :param num:
        :return:
        """
        if not isinstance(num, int):
            raise TypeError

        res = bytearray()
        while len(res) < num and not self.is_stop():
            try:
                res += self._conn.recv(num - len(res))
            except socket.timeout:
                continue
        return res

    def _recv_douyu_msg(self):
        data_len = self._recv_target_num(4)
        data_len = int.from_bytes(data_len, "little")

        msg_data = self._recv_target_num(data_len)
        msg_data = msg_data[8:]  # 头部取完4个字节, 还剩8个字节

        return msg_data

    def _recv_data(self):
        self._conn.settimeout(1)

        last_keep = int(time.time())
        while not self.is_stop():
            self._handle_recv_data(self._recv_douyu_msg())

            # 最多一秒recv就会超时，每隔35秒发一次心跳就好
            if int(time.time()) - last_keep >= self.HEART_INTERVAL:
                self._send_heartbeat()
                last_keep = int(time.time())

    def _handle_recv_data(self, data):
        pass

    def _send_heartbeat(self):
        msg = "type@=keeplive/tick@=" + str(int(time.time())) + "/\0"
        self._send_req_msg(msg)

    def _is_ready(self):
        if self._room_id is not None:
            return True
        return False

    def run(self):
        if not self._is_ready():
            return

        self._set_is_stop(False)

        self._connect_chat_server()
        self._login()
        self._join_group()

        self._recv_thread = threading.Thread(target=DouyuChatReader._recv_data, args=(self,))
        self._recv_thread.start()

    def is_stop(self):
        self._stop_lock.acquire()
        res = self._is_stop
        self._stop_lock.release()

        return res

    def _set_is_stop(self, is_stop):
        self._stop_lock.acquire()
        self._is_stop = is_stop
        self._stop_lock.release()

    def stop(self):
        if self._recv_thread is None:
            return

        if not self._recv_thread.is_alive():
            return

        self._set_is_stop(True)

        self._recv_thread.join()

        self._logout()

        self._conn.close()
        print("退出弹幕服务器...")

    def set_room(self, room_id):
        if not isinstance(room_id, int):
            raise ValueError("房间号应该是数字！")

        self._room_id = room_id
