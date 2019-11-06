# coding: utf-8
"""
连接斗鱼弹幕服务器
"""

import socket
import time
import struct
import asyncio

BUFFER_LIMIT = 2 ** 20


class DouyuChatReader(object):

    def __init__(self, room_id=None):
        self._room_id = room_id

        self._writer = None
        self._reader = None
        self._is_stop = False

    HEART_INTERVAL = 35
    HEADER_SIZE = 12  # 4 + 4 + 2 + 1 + 1

    async def _connect_chat_server(self):
        host = socket.gethostbyname("openbarrage.douyutv.com")
        port = 8601

        self._reader, self._writer = await asyncio.open_connection(host, port, limit=BUFFER_LIMIT)
        print(f"[{self._room_id}] 连接弹幕服务器成功...")

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

    async def _send_req_msg(self, msg):
        if not isinstance(msg, str):
            raise TypeError("消息类型必须为str")

        msg = self._pack_header(msg)
        self._writer.write(msg)
        await self._writer.drain()

    async def _logout(self):
        msg = "type@=logout/"
        await self._send_req_msg(msg)

    async def _login(self):
        msg = "type@=loginreq/roomid@={}/\0".format(self._room_id)
        await self._send_req_msg(msg)

    async def _join_group(self):
        msg = "type@=joingroup/rid@={}/gid@=-9999/\0".format(self._room_id)
        await self._send_req_msg(msg)

    async def _recv_douyu_msg(self):
        data_len = await self._reader.read(4)
        data_len = int.from_bytes(data_len, "little")

        msg_data = await self._reader.read(data_len)
        msg_data = msg_data[8:]  # 头部取完4个字节, 还剩8个字节

        return msg_data

    async def _recv_data(self):
        last_keep = int(time.time())
        while not self.is_stop():
            self._handle_recv_data(await self._recv_douyu_msg())

            # 每隔35秒发一次心跳就好
            if int(time.time()) - last_keep >= self.HEART_INTERVAL:
                await self._send_heartbeat()
                last_keep = int(time.time())

    def _handle_recv_data(self, data):
        pass

    async def _send_heartbeat(self):
        msg = "type@=keeplive/tick@=" + str(int(time.time())) + "/\0"
        await self._send_req_msg(msg)

    def _is_ready(self):
        if self._room_id is not None:
            return True
        return False

    async def run(self):
        if not self._is_ready():
            return

        while True:
            try:
                self._set_is_stop(False)
                await self._connect_chat_server()
                await self._login()
                await self._join_group()
                await self._recv_data()
            except ConnectionResetError as err:
                print(err)

    def is_stop(self):
        return self._is_stop

    def _set_is_stop(self, is_stop):
        self._is_stop = is_stop

    # async def stop(self):
    #     self._set_is_stop(True)
    #     await self._logout()
    #
    #     self._writer.close()
    #     await self._writer.wait_closed()
    #
    #     print(f"[{self._room_id}] 退出弹幕服务器...")

    def set_room(self, room_id):
        if not isinstance(room_id, int):
            raise ValueError("房间号应该是数字！")

        self._room_id = room_id
