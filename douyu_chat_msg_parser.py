# coding: utf-8
"""
解析从弹幕服务器拿到的数据
"""


class DouyuChatMsgFormatTool:
    """
    原始消息解析
    """

    special_char_map = {"/": "@S", "@": "@A"}

    r_special_char_map = {v: k for k, v in special_char_map.items()}

    item_separator = "/"
    kv_separator = "@="

    item_separator_b = b"/"
    kv_separator_b = b"@="

    @classmethod
    def _serialize_str(cls, str_):
        res_str = ""
        for char in str_:
            res_str += cls.special_char_map.get(char, char)
        return res_str

    @classmethod
    def serialize(cls, data_dict):
        """
        dict to douyu msg data format
        :param data_dict:
        :return:
        """
        if not isinstance(data_dict, dict):
            raise TypeError("data must be dict")

        return cls.item_separator.join(
            [
                cls.kv_separator.join([cls._serialize_str(k), cls._serialize_str(v)])
                for k, v in data_dict.items()
            ]
        )

    @classmethod
    def _deserialize_str(cls, mate_str):
        if not isinstance(mate_str, str):
            raise TypeError

        for k, v in cls.r_special_char_map.items():
            mate_str = mate_str.replace(k, v)

        return mate_str

    @classmethod
    def deserialize(cls, mate_data):
        """
        douyu msg data to dict
        :param mate_data:
        :return:
        """
        if not isinstance(mate_data, bytes) and not isinstance(mate_data, bytearray):
            raise TypeError("源数据必须是bytes")

        data_bytes = bytearray(mate_data)
        data_items = data_bytes.split(cls.item_separator_b)

        res_dict = dict()
        for item in data_items:
            if item == b'\x00':
                break

            kv = item.split(cls.kv_separator_b)
            if len(kv) != 2:
                return None

            try:
                k = kv[0].decode("utf-8")
                v = kv[1].decode("utf-8")
            except UnicodeDecodeError as err:
                print(err)
                print(kv)
                continue
            res_dict[cls._deserialize_str(k)] = cls._deserialize_str(v)

        return res_dict


def test():
    tmp_dict = {
        "type": "joi@=ngroup/123",
        "rid": "123",
        "gid": "-9999",
    }
    ss = DouyuChatMsgFormatTool.serialize(tmp_dict)
    print(ss)
    dd = DouyuChatMsgFormatTool.deserialize(bytes(ss, encoding='utf-8'))
    print(dd)
    print("----------------")
    ss = b'type@=chatmsg/rid@=606118/ct@=2/uid@=167151232/nn@=\xe8\x8d\x89\xe9\x99\x8d/txt@=\xe6\x89\xab\xe7\xa0\x81\xe9\xa2\x86\xe5\xa5\x96\xe5\x93\x81/cid@=8c87c8c2faf54bf5e664150000000000/ic@=avanew@Sface@S201709@S20@S19@S52c4bcc6e3b410d369e3a9ccae276337/level@=4/sahf@=0/bnn@=/bl@=0/brid@=0/hc@=/el@=/lk@=/urlev@=4/\x00'

    dd = DouyuChatMsgFormatTool.deserialize(ss)
    import json
    dd = json.dumps(dd, ensure_ascii=False)
    print(dd)


if __name__ == '__main__':
    test()
