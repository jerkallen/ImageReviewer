import urllib
import requests
import json
import os
import mimetypes



FEISHU_MSG_APIKEY = 'MFE4_LiXianglong_HDEV6_Final_01'

class Feishu:
    '''
    - 用于使用OpenAPI发送飞书信息
    - 开发部门WxP/MFE42
    '''

    def __init__(self, APIKEY=None) -> None:
        self.IP = 'https://feishu.wxp.prod.dservice.uaes.com:8443'
        self.APIKEY = APIKEY if APIKEY is not None else FEISHU_MSG_APIKEY  # APIKEY 限部门内部使用
        self.CHAT_ID = {
            "MFE4": "oc_18623c08a21247f0770ede48ec7f972f",
            "MOE4": "oc_6e8102e0772aee14cb0c90567beb173e",
            "MFE4工程师": "oc_b04d7c1542f219b67b1ef81eb485e649",
            "工艺监控预警": "oc_ad71da861d14a6f8fb0c08435878653f",
            "DLL AGV问题收集与培训": "oc_f8db1a6aa6ab442d687335e002c0b9bd",
            "视觉筛选": "oc_721a60adaacd102a727f155fc5ec0c64"
        }

    def _get_imgkey(self, attachment_path):
        ''' - 上传图片文件，获取imageKey'''
        url = f'{self.IP}/api/v1/feishu/getImageKey?imageType=message'
        with open(attachment_path, 'rb') as f:
            body = {"file": f.read()}
        response = requests.post(url=url, files=body, headers={
                                 "APIKEY": self.APIKEY})
        return json.loads(response.text)

    def get_groupid(self):
        ''' - 获取机器人所以在群的信息，如chat_id '''
        url = f'{self.IP}/api/v1/feishu/chatId'
        response = requests.get(url=url, data='', headers={
                                "APIKEY": self.APIKEY})
        r = json.loads(response.text)
        if r['code'] == 0:
            for group in json.loads(r['result'])['items']:
                print(group)
            return json.loads(r['result'])['items']
        else:
            return json.loads(response.text)

    def creat_group(self, data):
        ''' 
        - 建立群聊
        '''
        url = f'{self.IP}/api/v1/feishu/createChat'
        pass

    def send_msg(self, data):
        ''' 
        - 发送飞书信息，形式包括文本、图片、富文本、消息卡片 
        - ### 消息模板说明:
        - 文本消息：
        msg = {
            "msgType": "text",
            "userIds": ["xianglong.li"],
            "content": {"text":"测试文本消息"}
            }

        - 图片消息：
        msg = {
            "msgType": "image",
            "userIds": ["xianglong.li"],
            "content": {"image_key":"img_v2_d1a6dd93-db60-4b55-8662-b713dc99104g"}
            }

        - 富文本消息：
        msg = {
            "msgType": "post",
            "userIds": ["xianglong.li"],
            "content": {
                "post":{
                    "zh_cn": {
                        "title": "我是一个标题",
                        "content": [
                            [{
                                "tag": "text",
                                "text": "文本信息"
                            },
                            {
                                "tag": "a",
                                "href": "http://www.feishu.cn",
                                "text": "链接"
                            },
                            {
                                "tag": "img",
                                "image_key": "img_v2_d1a6dd93-db60-4b55-8662-b713dc99104g",
                                "text": "示例图片"
                            }
                            ]
                        ]
                    }
                }
            }
            }

        - 卡片消息：
        msg = {
            "card": {
                "type": "template",
                "data": {
                "template_id": "ctp_AAfvKkz1EGkE",
                "template_variable": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                        "tag": "markdown",
                        "content": "这里是卡片文本，支持使用markdown标签设置文本格式。例如：\n*斜体* \n**粗体**\n~~删除线~~\n[文字链接](https://www.feishu.cn)\n<at id=all></at>\n<font color='red'> 彩色文本 </font>"
                        }
                    ],
                    "header": {
                        "template": "blue",
                        "title": {
                        "content": "当班总产量信息",
                        "tag": "plain_text"
                        }
                    }
                    }
                }
            },
            "content": {},
            "msgType": "interactive",
            "userIds": [
                "xianglong.li"
            ]
            }
        '''

        url = f'{self.IP}/api/v1/feishu/postMessage'
        body = bytes(json.dumps(data), 'utf-8')
        response = requests.post(url=url, data=body, headers={
                                 "APIKEY": self.APIKEY, "content-type": 'application/json', "Host":'feishu.wxp.prod.dservice.uaes.com'})
        return json.loads(response.text)

    def send_group_msg(self, data):
        ''' 
        - 发送飞书群信息，形式包括文本、图片、富文本、消息卡片 
        - ### 消息模板说明:
        - 文本消息：
        msg = {
            "msgType": "text",
            "receiveId": "oc_fac410843464a8eb1411b9edbac4207a",
            "content": {"text":"测试文本消息"}
            }

        - 图片消息：
        msg = {
            "msgType": "image",
            "receiveId": "oc_fac410843464a8eb1411b9edbac4207a",
            "content": {"image_key":"img_v2_d1a6dd93-db60-4b55-8662-b713dc99104g"}
            }

        - 富文本消息：
        msg = {
            "msgType": "post",
            "receiveId": "oc_fac410843464a8eb1411b9edbac4207a",
            "content": {
                    "zh_cn": {
                        "title": "我是一个标题",
                        "content": [
                            [{
                                "tag": "text",
                                "text": "文本信息"
                            },
                            {
                                "tag": "a",
                                "href": "http://www.feishu.cn",
                                "text": "链接"
                            },
                            {
                                "tag": "img",
                                "image_key": "img_v2_d1a6dd93-db60-4b55-8662-b713dc99104g",
                                "text": "示例图片"
                            }
                            ]
                        ]
                    }
            }
            }

        - 卡片消息：
        msg = {
            "card": {
                "type": "template",
                "data": {
                "template_id": "ctp_AAfvKkz1EGkE",
                "template_variable": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                        "tag": "markdown",
                        "content": "这里是卡片文本，支持使用markdown标签设置文本格式。例如：\n*斜体* \n**粗体**\n~~删除线~~\n[文字链接](https://www.feishu.cn)\n<at id=all></at>\n<font color='red'> 彩色文本 </font>"
                        }
                    ],
                    "header": {
                        "template": "blue",
                        "title": {
                        "content": "当班总产量信息",
                        "tag": "plain_text"
                        }
                    }
                    }
                }
            },
            "content": {},
            "msgType": "interactive",
            "receiveId": "oc_fac410843464a8eb1411b9edbac4207a"
            }
        '''

        url = f'{self.IP}/api/v1/feishu/postChatMessage'
        body = bytes(json.dumps(data), 'utf-8')
        response = requests.post(url=url, data=body, headers={
                                 "APIKEY": self.APIKEY, "content-type": 'application/json', "Host":'feishu.wxp.prod.dservice.uaes.com'})

        return json.loads(response.text)

if __name__ == "__main__":
    feishu = Feishu()
    chat_id =  'oc_fac410843464a8eb1411b9edbac4207a'
    imgurl = feishu._get_imgkey("static/test_img.png")
    img_id = imgurl['result']
    test_msg = {
            "msgType": "post",
            "receiveId": chat_id,
            "content": {
                    "zh_cn": {
                        "title": "【图片审查系统】测试消息",
                        "content": 
                        [
                            [{
                                "tag": "text",
                                "text": "【图片审查系统】测试消息\n发送时间: xxxx"
                            },
                            {
                                "tag": "img",
                                "image_key": img_id,
                                "text": "示例图片"
                            }
                            ]
                        ]
                    }
            }
            }

    result = feishu.send_group_msg(test_msg)
    print(result)
    pass