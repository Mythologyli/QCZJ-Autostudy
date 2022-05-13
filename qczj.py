# Copyright 2022.1 by WuliAPO
# Copyright © cjlu.online . All rights reserved.

# modified by @Dimlitter 2022/3/1 
# personal profile: https://github.com/Dimlitter
import json
import random
import time
import requests
from requests import RequestException
import datetime


class YouthLearning:
    """
    · self.session : 统一的session管理
    · 支持每日签到与阅读文章
    · 每周观看网课
    """

    def __init__(self, nid, card_no, open_id, nickname, push_key, email=''):
        self.nid = nid
        self.cardNo = card_no
        self.openid = open_id
        self.nickname = nickname
        self.email = email

        self.push_url = "https://push.akashic.cc/%s/" % push_key

        self.sleep_time = random.randint(5, 10)
        self.session = requests.session()

        self.headers = {
            'Host': 'qczj.h5yunban.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K11AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3185 MMWEBSDK/20220105 Mobile '
                          'Safari/537.36 WEBISODE/4365 MicroMessenger/8.0.19.2080(0x2800133D) Process/toolsmp '
                          'WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',

            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json;charset=UTF-8',

            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
        }

    # 获取 AccessToken
    def get_access_token(self, openid, nickname):
        headers = {
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
        }

        temp_headers = self.headers
        temp_headers.update(headers)
        time_stamp = str(int(time.time()))  # 获取时间戳

        url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback?callback=https%3A%2F" \
              "%2Fqczj.h5yunban.com%2Fqczj-youth-learning%2Findex.php&scope=snsapi_userinfo&appid=wx56b888a1409a2920" \
              "&openid=" + openid + "&nickname=" + nickname + "&headimg=&time=" + time_stamp + \
              "&source=common&sign=&t=" + time_stamp

        res = self.session.get(url, headers=temp_headers)

        access_token = res.text[45:81]  # 比较懒，直接截取字符串了
        print("获取到 AccessToken:", access_token)
        return access_token

    # 获取当前最新的课程代号
    def get_current_course(self, access_token):
        headers = {
            'Referer': 'https://qczj.h5yunban.com/qczj-youth-learning/signUp.php?rom=1',
        }
        headers.update(self.headers)
        url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current?accessToken=" + \
              access_token

        res = self.session.get(url)
        res_json = json.loads(res.text)

        if res_json["status"] == 200:  # 验证正常
            print("获取到最新课程代号:", res_json["result"]["id"])
            return res_json["result"]["id"]
        else:
            print("获取最新课程失败！退出程序")
            self.push("获取最新课程失败！退出程序")
            print(res.text)
            exit(0)

    # 签到并获取签到记录
    def get_join(self, access_token, current_course, nid, card_no):
        headers = {
            'Content-Length': '80',
            'Origin': 'https://qczj.h5yunban.com',
            'Referer': 'https://qczj.h5yunban.com/qczj-youth-learning/signUp.php?rom=1',
        }
        headers.update(self.headers)
        data = {
            "course": current_course,  # 大学习期次的代码，如C0046，本脚本已经帮你获取啦
            "subOrg": None,
            "nid": nid,  # 团组织编号，形如N003************
            "cardNo": card_no  # 打卡昵称
        }

        url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join?accessToken=" + access_token
        res = self.session.post(url, json=data, headers=headers)  # 特别注意，此处应选择 json 格式发送 data 数据

        print("签到结果:", res.text)
        res_json = json.loads(res.text)
        if res_json["status"] == 200:  # 验证正常
            print("似乎签到成功了")
            return True
        else:
            print("签到失败！")
            self.push("签到失败！")
            exit(0)

    def check(self, access_token):
        headers1 = {
            'Content-Length': '2',
            'Origin': 'https://qczj.h5yunban.com',
            'Referer': 'https://qczj.h5yunban.com/qczj-youth-learning/mine.php',
        }
        url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/sign-in?accessToken=' + access_token
        data = {
            # 'accessToken': access_token,
        }
        try:
            res = self.session.post(url, json=data, headers=headers1)
        except RequestException as e:
            print("网络错误，请检查网络")
            print("尝试重新签到,等待15s")
            time.sleep(15)
            try:
                res = self.session.post(url, json=data, headers=headers1)
            except RequestException:
                print("签到失败！")
                self.push("签到失败！")
                return False

        res = json.loads(res.text)
        if res["status"] == 200:
            print("访问成功")
            if not res['result']:
                print("今天已经签到过了")
            else:
                print("今天签到成功！")
        else:
            print("访问失败")
            self.push("访问失败")

        url2 = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/sign-in/records?accessToken=' + \
               access_token + '&date=' + datetime.datetime.now().strftime('%Y-%m')
        headers2 = {
            'Referer': 'https://qczj.h5yunban.com/qczj-youth-learning/mine.php',
        }

        headers2.update(self.headers)

        try:
            res2 = self.session.get(url2, headers=headers2)
            if res2.status_code == 200:
                print("签到记录存在！")
                print(res2.text)
            else:
                print("签到记录失败")
                self.push("签到记录失败")
        except RequestException:
            print("网络错误，不影响签到")

    def read(self, access_token):
        headers = {
            'Referer': 'https://qczj.h5yunban.com/qczj-youth-learning/learn.php',
            'Content-Length': '2',
            'Origin': 'https://qczj.h5yunban.com',
        }
        headers.update(self.headers)
        numbers = [random.randint(470017, 470026) for i in range(4)]
        for number in numbers:
            number = str(number)
            url = 'https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/study?accessToken=' + \
                  access_token + '&id=' + 'C00' + number
            time.sleep(8)

            # 传的data居然是空的
            data = {
                # 'accessToken': access_token,
                # 'id': 'C00'+ number,
            }

            try:
                res = self.session.post(url, json=data, headers=headers).json()
                if res['status'] == 200:
                    print("文章" + 'C00' + number + "学习成功")
                    print(res)
                else:
                    print("文章" + 'C00' + number + "学习失败")
                    print(res)
            except RequestException:
                print("网络错误,尝试重新学习,等待15s")
                time.sleep(15)
                try:
                    res = self.session.post(url, json=data).json()
                    if res['status'] == 200:
                        print("文章" + 'C00' + number + "重新学习成功")
                except RequestException:
                    print("重新学习失败，退出")
                    self.push("重新学习失败，退出")
                    break

    def push(self, message):
        if message != "":
            requests.post(self.push_url,
                          params={'title': '青年大学习脚本通知', 'description': '详细信息: ' + f"\n{message}"})
            if self.email != '':
                requests.post(self.push_url, params={'email': self.email, 'title': '青年大学习脚本通知',
                                                     'description': '详细信息: ' + f"\n{message}"})

            print("推送完成！")

    def run(self):
        access_token = self.get_access_token(self.openid, self.nickname)

        time.sleep(self.sleep_time)
        current_course = self.get_current_course(access_token)

        # 添加随机执行
        sequence = [1, 2, 3]
        random.shuffle(sequence)
        order = {1: '看视频', 2: '签到', 3: '阅读文章'}
        result = ''
        for i in sequence:
            result = result + order[i] + '------>'
        print("本次学习的顺序为：", result, "完成")

        for i in sequence:
            if i == 1:  # 看视频
                time.sleep(self.sleep_time)
                print("今天是星期", datetime.datetime.now().weekday() + 1)
                # if datetime.datetime.now().weekday() == 0:
                #     time.sleep(self.sleep_time)
                #     self.get_join(access_token, current_course, self.nid, self.cardNo)
                # else:
                #     print("今天不是周一，不看视频")

                time.sleep(self.sleep_time)
                self.get_join(access_token, current_course, self.nid, self.cardNo)

            if i == 2:  # 签到
                time.sleep(self.sleep_time)
                self.check(access_token)
            if i == 3:  # 阅读
                time.sleep(self.sleep_time)
                self.read(access_token)

        self.push("今天学习完成！")
