# encoding:utf-8
import sys

sys.path.append("..")
import common
import os
import requests
import time
import uuid
import json
from requests_toolbelt import MultipartEncoder
from nose.plugins.attrib import attr
from nose import SkipTest

"""

# setup 和 teardown 均需要先删除相应的 人 库 标签 ，防止干扰测试


本地方式新增人物　全流程覆盖测试接口


１，新增一个子库：　朋友圈美女　　　　　　　　　　
２，搜索子库　是否存在　　　　　　　　
３，修改子库名：　朋友圈美女　朋友圈大美女
４，搜索子库　是否存在　　　　　　　　　　　　　　　　　
５，删除　朋友圈大美女　子库　
６，搜索子库是否存在　　　　　　　　　　　　　　　　
７，新增一个子库：　朋友圈美女　　　　　　　　　　
８，增加标签　　绝色美女　　　　　　　　　　　　　　　
９，查询标签　绝色美女　　　　　　　　　　　　　　　　　　
10，修改标签　　绝色美女　绝色大美女　
11 ,查询标签　绝色大美女是否存在　　　　　　　　
12，删除标签　绝色大美女　　　　　　　　　　　　　　　　　　　
13，查询标签　　绝色大美女
14，新增标签　绝色美女
15，搜索标签　　绝色美女　
16，朋友圈美女图片两张　入库　　　李欣萌　　　　　　　　　　　　　　
17，搜索图片接口确认能收到　　　　　　　　　　　　　　
18，删除美女图片一张　
19，搜索图片接口确认能收到　　　
20，人物搜索接口，可以搜索到李欣萌　　　　　　　
21，主库添加人物到　子库　　朋友圈美女　　　　　
22，搜索　李欣萌
23，　修改李欣萌　为　李萌新
24，搜索　李萌新
25，　使用Ｆilter 分析李萌新的　视频，　必须分析出来
26，删除　李萌新
27，搜索　李萌新
28，使用Ｆilter 分析李萌新的　视频，　分析不出来李萌新　　　
29，　删除　子库　朋友圈美女
30，　删除　标签　绝色美女
31，　确认图片已删除
32，　确认子库已删除
33，　确认标签已删除
34，　确认人物已删除

"""


@attr(feature="test_logic")
@attr(runtype="normal")
@attr(videotype="normal")
class test_logic_002(common.sensemediaTestBase):

    def __init__(self):
        super(test_logic_002, self).__init__("test_logic_002")
        common.sensemediaTestBase.setlogger(self, __name__)

        # 超时时间(任务需在自指定时间内完成，否则置为失败),检测间隔为test_interval
        self.expire = 300
        self.test_interval = 5

        # 请求url
        self.url = common.getConfig("url", "cloud_url")
        self.baseurl = common.getConfig("url", "base_url")
        self.logger.info("testcase is %s " % self.testid)
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("request url is %s" % self.url)
        self.logger.info("base url is %s" % self.baseurl)

        # get_res_url(通过此url 查询任务状态)
        self.res_url = common.getConfig("url", "res_url")

        # request url
        # self.file =("renmingdemingyi.avi", open('/codes/sensecloud/test_video_type_common/renmingdemingyi.avi', 'rb'), "video/mpeg4")
        # TODO
        self.video_url = "https://172.20.14.63:6554/renmingdemingyi.avi"
        self.stream = "rtsp://172.20.14.63:8081/bucunzai.ts"
        self.frame_extract_interval = ""
        self.modules = ""
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = ""

        # 请求体
        self.body = {
            "stream": self.video_url,
            "callback": self.callback,
            "token": self.token,
            "modules": "filter_star",
            "db_name": ""
        }
        # 请求头
        self.headers = {'content-type': 'application/json'}
        self.json_headers = {'content-type': 'application/json'}

        # 期望使用的modules
        self.expect_modules = ["filter_star", ]
        # probability 最低限度
        self.probability_low = 0
        # probability 最高限度
        self.probability_high = 1

    def setup(self):
        self.logger.info("test setup")

        # 删人
        self.logger.info("---setup，删除　李萌新 李欣萌")
        data_26 = {"name": "李萌新,李欣萌,李萌新1,天子娇女"}
        url_26 = self.baseurl + "/sensemedia/face_in/v2/persons"
        r_26 = requests.delete(url_26, params=data_26)
        self.logger.info("req url is %s" % r_26.url)
        self.logger.info(r_26.text)

        # 删库
        self.logger.info("---setup  删除　朋友圈大美女　朋友圈美女 子库")
        data_5 = {"name": "朋友圈大美女,朋友圈美女"}

        url_5 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_5 = requests.delete(url_5, params=data_5, headers=self.json_headers)
        self.logger.info(r_5.text)
        self.logger.info(r_5.url)
        self.logger.info("status code is %s" % r_5.status_code)

        # 删标签
        self.logger.info("---setup  删除标签　绝色大美女 绝色美女")
        data_12 = {"name": "绝色大美女,绝色美女"}

        url_12 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_12 = requests.delete(url_12, params=data_12, headers=self.json_headers)
        self.logger.info(r_12.url)
        self.logger.info(r_12.text)

    def test_001(self):

        # 1,新增一个子库：　朋友圈美女
        self.logger.info("---step1  make a new lib 朋友圈美女")
        url_1 = self.baseurl + "/sensemedia/face_in/v2/parts"
        data_1 = {"name": "朋友圈美女", "db_name": "明星"}
        r_1 = requests.post(url_1, data=json.dumps(data_1), headers={'content-type': 'application/json'})

        self.logger.info(r_1.text)

        # 检查http 状态码
        if r_1.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_1.status_code)
            assert False
        self.logger.info("status code is %s" % r_1.status_code)

        # 2 搜索子库　是否存在
        self.logger.info("---step2  搜索子库　是否存在 朋友圈美女")

        url_2 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_2 = requests.get(url_2, headers=self.json_headers)
        self.logger.info(r_2.text)

        # 检查http 状态码
        if r_2.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_2.status_code)
            assert False
        self.logger.info("status code is %s" % r_2.status_code)

        if "朋友圈美女" not in r_2.text.encode("utf-8"):
            self.logger.error("not find　子库　朋友圈美女")
            assert False

        # ３，修改子库名：　朋友圈美女　朋友圈大美女

        self.logger.info("---step3  修改子库名：　朋友圈美女　朋友圈大美女")
        data_3 = {"parts": [{"origin_part": "朋友圈美女", "part": "朋友圈大美女"}]}

        url_3 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_3 = requests.put(url_3, data=json.dumps(data_3), headers=self.json_headers)
        self.logger.info(r_3.text)

        # 检查http 状态码
        if r_3.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_3.status_code)
            assert False
        self.logger.info("status code is %s" % r_3.status_code)

        # TODO 判断响应体其他字段

        # 4,搜索子库　是否存在　　　　
        self.logger.info("---step4  搜索子库　是否存在 朋友圈大美女")

        url_4 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_4 = requests.get(url_4, headers=self.json_headers)
        self.logger.info(r_4.text)

        # 检查http 状态码
        if r_4.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_4.status_code)
            assert False
        self.logger.info("status code is %s" % r_4.status_code)

        if "朋友圈大美女" not in r_4.text.encode("utf-8"):
            self.logger.error("not find　子库　朋友圈大美女")
            assert False

        if "朋友圈美女" in r_4.text.encode("utf-8"):
            self.logger.error("find　子库　朋友圈美女，not as expected")
            assert False

        # 5,删除　朋友圈大美女　子库

        self.logger.info("---step5  删除　朋友圈大美女　子库")
        data_5 = {"name": "朋友圈大美女"}

        url_5 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_5 = requests.delete(url_5, params=data_5, headers=self.json_headers)
        self.logger.info(r_5.text)

        # 检查http 状态码
        if r_5.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_5.status_code)
            assert False
        self.logger.info("status code is %s" % r_5.status_code)

        # 6, 搜索子库是否存在

        self.logger.info("---step6  搜索子库　是否存在 朋友圈大美女 朋友圈美女　")

        url_6 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_6 = requests.get(url_6, headers=self.json_headers)
        self.logger.info(r_6.text)

        # 检查http 状态码
        if r_6.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_6.status_code)
            assert False
        self.logger.info("status code is %s" % r_6.status_code)

        if "朋友圈大美女" in r_6.text.encode("utf-8"):
            self.logger.error("find　子库　朋友圈大美女, not as expected !")
            assert False

        if "朋友圈美女" in r_6.text.encode("utf-8"):
            self.logger.error("find　子库　朋友圈美女，not as expected ! ")
            assert False

        # 7,新增一个子库：　朋友圈美女

        self.logger.info("---step7  make a new lib 朋友圈美女")
        url_7 = self.baseurl + "/sensemedia/face_in/v2/parts"
        data_7 = {"name": "朋友圈美女", "db_name": "明星"}
        r_7 = requests.post(url_7, data=json.dumps(data_7), headers=self.json_headers)
        self.logger.info(r_7.text)

        # 检查http 状态码
        if r_7.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_7.status_code)
            assert False
        self.logger.info("status code is %s" % r_7.status_code)

        # 8,增加标签　　绝色美女

        self.logger.info("---step8  add a label 绝色美女　")
        url_8 = self.baseurl + "/sensemedia/face_in/v2/labels"
        data_8 = {"name": "绝色美女"}
        r_8 = requests.post(url_8, params=data_8, headers=self.json_headers)
        self.logger.info(r_8.text)

        # 检查http 状态码
        if r_8.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_8.status_code)
            assert False
        self.logger.info("status code is %s" % r_8.status_code)

        # 9,查询标签　绝色美女

        self.logger.info("---step9  搜索标签　绝色美女　")

        url_9 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_9 = requests.get(url_9, headers=self.json_headers)
        self.logger.info(r_9.text)

        # 检查http 状态码
        if r_9.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_9.status_code)
            assert False
        self.logger.info("status code is %s" % r_9.status_code)

        if "绝色美女" not in r_9.text.encode("utf-8"):
            self.logger.error("not find　标签　绝色美女, not as expected !")
            assert False

        # 10,修改标签　　绝色美女　绝色大美女　

        self.logger.info("---step10  修改标签：　绝色美女　绝色大美女")
        data_10 = {"labels": [{"origin_label": "绝色美女", "label": "绝色大美女"}]}

        url_10 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_10 = requests.put(url_10, data=json.dumps(data_10), headers=self.json_headers)
        self.logger.info(r_10.text)

        # 检查http 状态码
        if r_10.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_10.status_code)
            assert False
        self.logger.info("status code is %s" % r_10.status_code)

        # 11, 搜索标签　绝色大美女是否存在

        self.logger.info("---step11  查询标签　　绝色大美女　")

        url_11 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_11 = requests.get(url_11, headers=self.json_headers)
        self.logger.info(r_11.text)

        # 检查http 状态码
        if r_11.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_11.status_code)
            assert False
        self.logger.info("status code is %s" % r_11.status_code)

        if "绝色美女" in r_11.text.encode("utf-8"):
            self.logger.error(" find　标签　绝色美女, not as expected !")
            assert False

        if "绝色大美女" not in r_11.text.encode("utf-8"):
            self.logger.error(" not find　标签　绝色大美女, not as expected !")
            assert False

        # 12，删除标签　绝色大美女

        self.logger.info("---step12  删除标签　绝色大美女")
        data_12 = {"name": "绝色大美女"}

        url_12 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_12 = requests.delete(url_12, params=data_12, headers=self.json_headers)
        self.logger.info(r_12.text)

        # 检查http 状态码
        if r_12.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_12.status_code)
            assert False
        self.logger.info("status code is %s" % r_12.status_code)

        # １3，查询标签　　绝色大美女

        self.logger.info("---step13  查询标签　　绝色大美女　")

        url_13 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_13 = requests.get(url_13, headers=self.json_headers)
        self.logger.info(r_13.text)

        # 检查http 状态码
        if r_13.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_13.status_code)
            assert False
        self.logger.info("status code is %s" % r_13.status_code)

        if "绝色美女" in r_13.text.encode("utf-8"):
            self.logger.error(" find　标签　绝色美女, not as expected !")
            assert False

        if "绝色大美女" in r_13.text.encode("utf-8"):
            self.logger.error(" find　标签　绝色大美女, not as expected !")
            assert False

        # １4，新增标签　绝色美女

        self.logger.info("---step14  add a label 绝色美女　")
        url_14 = self.baseurl + "/sensemedia/face_in/v2/labels"
        data_14 = {"name": "绝色美女"}
        r_14 = requests.post(url_14, params=data_14, headers=self.json_headers)
        self.logger.info(r_14.text)

        # 检查http 状态码
        if r_14.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_14.status_code)
            assert False
        self.logger.info("status code is %s" % r_14.status_code)

        # １5，搜索标签　　绝色美女

        self.logger.info("---step15  查询标签　　绝色美女　")

        url_15 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_15 = requests.get(url_15, headers=self.json_headers)
        self.logger.info(r_15.text)

        # 检查http 状态码
        if r_15.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_15.status_code)
            assert False
        self.logger.info("status code is %s" % r_15.status_code)

        if "绝色美女" not in r_15.text.encode("utf-8"):
            self.logger.error(" not find　标签　绝色美女, not as expected !")
            assert False

        if "绝色大美女" in r_15.text.encode("utf-8"):
            self.logger.error("  find　标签　绝色大美女, not as expected !")
            assert False

        # 16，朋友圈美女图片两张　入库　　　李欣萌　　

        self.logger.info("---step16  朋友圈美女图片两张　入库　　　李欣萌　")

        url_16 = self.baseurl + "/sensemedia/face_in/v2/persons?db_name=明星"
        self.file = ("李欣梦.zip", open('/codes/sensecloud/test_logic/李欣梦.zip', 'rb'), "application/zip")
        # 请求体
        self.body = {
            "comment": "新增1个名单",
            "figures": [
                {
                    "name": "李欣萌",
                    "label": "绝色美女",
                    "url": [
                        "http://172.20.14.63:90/lixingmeng.png",
                        "http://172.20.14.63:90/lixingmeng1.png"
                    ]
                }
            ]
        }

        r_16 = requests.post(url_16, data=json.dumps(self.body), headers=self.json_headers)
        self.logger.info(r_16.text)

        # 检查http 状态码
        if r_16.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_16.status_code)
            assert False
        self.logger.info("status code is %s" % r_16.status_code)

        # 17，搜索图片接口确认能收到

        self.logger.info("---step17  搜索图片接口确认能收到　")

        url_17 = self.baseurl + "/sensemedia/face_in/v2/features"

        payload = {'person_name': '李欣萌'}
        r_17 = requests.get(url_17, params=payload, headers=self.json_headers)
        self.logger.info(r_17.url)
        self.logger.info(r_17.text)

        # 检查http 状态码
        if r_17.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_17.status_code)
            assert False
        self.logger.info("status code is %s" % r_17.status_code)

        if "lixingmeng1.png" not in r_17.text.encode("utf-8"):
            self.logger.error("not find lixingmeng1.png, not as expected ！")
            assert False

        id = ""

        # TODO()获取lixingmeng1.png 的id ,给下一步删除
        for x in r_17.json().get("results"):
            if x["imageName"].encode("utf-8") == "lixingmeng1.png":
                id = x["id"]

        if len(str(id)) < 0:
            self.logger.error("id len is 0 ,not as expect!")
            assert False
        self.logger.info("lixingmeng1.png id  is %s" % id)

        # # 18，删除美女图片一张　lixingmeng1.png

        self.logger.info("---step18  删除美女图片一张　lixingmeng1.png")
        data_18 = {"id": id}
        url_18 = self.baseurl + "/sensemedia/face_in/v2/features"
        r_18 = requests.delete(url_18, params=data_18)
        self.logger.info("18 req url is %s" % r_18.url)
        self.logger.info(r_18.text)

        # 检查http 状态码
        if r_18.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_18.status_code)
            assert False
        self.logger.info("status code is %s" % r_18.status_code)

        # 19，搜索图片接口确认能收到　lixingpeng.png

        self.logger.info("---step19  搜索图片接口确认能收到　lixingpeng.png  ")

        url_19 = self.baseurl + "/sensemedia/face_in/v2/features"

        payload = {'person_name': '李欣萌'}
        r_19 = requests.get(url_19, params=payload, headers=self.json_headers)
        self.logger.info(r_19.text)

        # 检查http 状态码
        if r_19.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_19.status_code)
            assert False
        self.logger.info("status code is %s" % r_19.status_code)

        if "lixingmeng.png" not in r_19.text.encode("utf-8"):
            self.logger.error("not find lixingmeng1.png, not as expected ！")
            assert False

        # 20，人物搜索接口，可以搜索到李欣萌

        self.logger.info("---step20  人物搜索接口，可以搜索到李欣萌 ")

        url_20 = self.baseurl + "/sensemedia/face_in/v2/persons"

        payload = {'name': '李欣萌'}
        r_20 = requests.get(url_20, params=payload)
        self.logger.info(r_20.url)
        self.logger.info(r_20.text)

        # 检查http 状态码
        if r_20.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_20.status_code)
            assert False
        self.logger.info("status code is %s" % r_20.status_code)

        if "李欣萌" not in r_20.text.encode("utf-8"):
            self.logger.error("not find 李欣萌, not as expected ！")
            assert False

        # 21，主库添加人物李欣萌到　子库　 朋友圈美女

        self.logger.info("---step21  主库添加人物李欣萌到　子库　 朋友圈美女　")
        url_21 = self.baseurl + "/sensemedia/face_in/v2/persons/copy"
        data_21 = {"part": "朋友圈美女", "persons": ["李欣萌"]}
        r_21 = requests.post(url_21, data=json.dumps(data_21), headers=self.json_headers)
        self.logger.info(r_21.url)
        self.logger.info(r_21.text)

        # 检查http 状态码
        if r_21.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_21.status_code)
            assert False
        self.logger.info("status code is %s" % r_21.status_code)

        # 22，搜索人物 子库　李欣萌

        self.logger.info("---step22  人物搜索接口，可以搜索到李欣萌 ")

        url_22 = self.baseurl + "/sensemedia/face_in/v2/persons"

        payload = {'name': '李欣萌', "db_name": "朋友圈美女"}
        r_22 = requests.get(url_22, params=payload)
        self.logger.info(r_22.url)
        self.logger.info(r_22.text)

        # 检查http 状态码
        if r_22.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_22.status_code)
            assert False
        self.logger.info("status code is %s" % r_22.status_code)

        if "李欣萌" not in r_22.text.encode("utf-8"):
            self.logger.error("not find 李欣萌, not as expected ！")
            assert False

        # 23，　修改李欣萌　为　李萌新

        self.logger.info("---step23  修改李欣萌　为　李萌新")
        data_23 = {"persons": [{"origin_name": "李欣萌", "name": "李萌新"}]}

        url_23 = self.baseurl + "/sensemedia/face_in/v2/persons"
        r_23 = requests.put(url_23, data=json.dumps(data_23), headers=self.json_headers)
        self.logger.info(r_23.url)
        self.logger.info(r_23.text)

        # 检查http 状态码
        if r_23.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_23.status_code)
            assert False
        self.logger.info("status code is %s" % r_23.status_code)

        # 24，搜索　李萌新

        self.logger.info("---step24  人物搜索接口，可以搜索到李萌新 ")

        url_24 = self.baseurl + "/sensemedia/face_in/v2/persons"

        payload = {'name': '李萌新', "db_name": "朋友圈美女"}
        r_24 = requests.get(url_24, params=payload, )
        self.logger.info(r_24.text)

        # 检查http 状态码
        if r_24.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_24.status_code)
            assert False
        self.logger.info("status code is %s" % r_24.status_code)

        if "李萌新" not in r_24.text.encode("utf-8"):
            self.logger.error("not find 李萌新, not as expected ！")
            assert False

        # 25，　使用Ｆilter分析李萌新的　视频，　必须分析出来

        self.logger.info("---step25，　使用Ｆilter分析李萌新的视频，两分钟内必须分析出来 ")
        self.video_url = "https://172.20.14.63:6554/lixingmeng.mp4"
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = "朋友圈美女"

        # 请求体
        self.body = {
            "url": self.video_url,
            "callback": self.callback,
            "token": self.token,
            "modules": "filter_star",
            "db_name": "朋友圈美女"
        }
        # 请求头
        self.headers = {'content-type': 'application/json'}

        # 发送request请求
        r = requests.post(self.url, data=json.dumps(self.body), headers=self.headers)
        self.logger.info(r.url)
        self.logger.info(r.text)

        # 检查http 状态码
        if r.status_code != requests.codes.ok:
            self.logger.error("status code is %s" % r.status_code)
            assert False
        r_body = r.json()
        self.logger.info("response body_json is %s" % r_body)
        resp_id = r_body.get("request_id")
        if not isinstance(resp_id, basestring):
            self.logger.error("resp_id %s is not sting " % resp_id)
            assert False

        # sleep 120 and get results
        self.logger.info("now sleep 120 seconds ")
        time.sleep(120);

        # get results
        r = requests.get(self.res_url + resp_id + "/results")
        self.logger.info("single results reponse is %s " % r.text)
        res_res_url = json.loads(r.json().get("content")[0].get("result")).get("result_urls")[0]
        r_json = requests.get(res_res_url).json()
        self.logger.info("r_json reponse is %s " % r_json)

        # 判断李萌新是否在不在结果中
        if repr(u"李萌新") not in str(r_json):
            self.logger.error("not find 李萌新，not as expected !")
            assert False

        # 26，删除　李萌新
        self.logger.info("---step26，删除　李萌新")
        data_26 = {"name": "李萌新"}
        url_26 = self.baseurl + "/sensemedia/face_in/v2/persons"
        r_26 = requests.delete(url_26, params=data_26)
        self.logger.info("26 req url is %s" % r_26.url)
        self.logger.info(r_26.text)

        # 检查http 状态码
        if r_26.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_26.status_code)
            assert False
        self.logger.info("status code is %s" % r_26.status_code)

        # 27，搜索　李萌新

        self.logger.info("---step27  人物搜索接口，搜索不到李萌新 ")

        url_27 = self.baseurl + "/sensemedia/face_in/v2/persons"

        payload = {'name': '李萌新', "db_name": "朋友圈美女"}
        r_27 = requests.get(url_27, params=payload)
        self.logger.info("url is %s" % r_27.url)

        self.logger.info(r_27.text)

        # 检查http 状态码
        if r_27.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_27.status_code)
            assert False
        self.logger.info("status code is %s" % r_27.status_code)

        if "李萌新" in r_27.text.encode("utf-8"):
            self.logger.error("find 李萌新, not as expected ！")
            assert False

        # 28，使用Ｆilter分析李萌新的　视频，　分析不出来李萌新　　　

        self.logger.info("---step28，使用Ｆilter分析李萌新的　视频，　分析不出来李萌新　 ")
        self.video_url = "https://172.20.14.63:6554/lixingmeng.mp4"
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = "朋友圈美女"

        # 请求体
        self.body = {
            "url": self.video_url,
            "callback": self.callback,
            "token": self.token,
            "modules": "filter_star",
            "db_name": "朋友圈美女"
        }
        # 请求头
        self.headers = {'content-type': 'application/json'}

        # 发送request请求
        r = requests.post(self.url, data=json.dumps(self.body), headers=self.headers)

        self.logger.info(r.text)

        # 检查http 状态码
        if r.status_code == requests.codes.ok:
            self.logger.error("status code is %s" % r.status_code)
            assert False
        r_body = r.json()
        self.logger.info("response body_json is %s" % r_body)

        # 29，　删除　子库　朋友圈美女

        self.logger.info("---step27  删除　朋友圈美女　子库")
        data_27 = {"name": "朋友圈美女"}

        url_27 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_27 = requests.delete(url_27, params=data_27, headers=self.json_headers)
        self.logger.info(r_27.text)

        # 检查http 状态码
        if r_27.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_27.status_code)
            assert False
        self.logger.info("status code is %s" % r_27.status_code)

        # 30，　删除　标签　绝色美女

        self.logger.info("---step30  删除标签　绝色美女")
        data_30 = {"name": "绝色美女"}

        url_30 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_30 = requests.delete(url_30, params=data_30, headers=self.json_headers)
        self.logger.info(r_30.text)

        # 检查http 状态码
        if r_30.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_30.status_code)
            assert False
        self.logger.info("status code is %s" % r_30.status_code)

        # 31，　确认图片已删除

        self.logger.info("---step31 　确认图片已删除  ")

        url_31 = self.baseurl + "/sensemedia/face_in/v2/features"

        payload = {'person_name': '李欣萌'}
        r_31 = requests.get(url_31, params=payload, headers=self.json_headers)
        self.logger.info(r_31.text)

        # 检查http 状态码
        if r_31.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_31.status_code)
            assert False
        self.logger.info("status code is %s" % r_31.status_code)

        if "lixingmeng.png" in r_31.text.encode("utf-8") or "lixingmeng1.png" in r_31.text.encode("utf-8"):
            self.logger.error(" find lixingmeng.png, not as expected ！")
            assert False

        # 32，　确认子库已删除

        self.logger.info("---step32  搜索子库　是否存在 朋友圈大美女 朋友圈美女　")

        url_32 = self.baseurl + "/sensemedia/face_in/v2/parts"
        r_32 = requests.get(url_32, headers=self.json_headers)
        self.logger.info(r_32.text)

        # 检查http 状态码
        if r_32.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_32.status_code)
            assert False
        self.logger.info("status code is %s" % r_32.status_code)

        if "朋友圈大美女" in r_32.text.encode("utf-8"):
            self.logger.error("find　子库　朋友圈大美女")
            assert False

        if "朋友圈美女" in r_32.text.encode("utf-8"):
            self.logger.error("find　子库　朋友圈美女，not as expected")
            assert False

        # 33，　确认标签已删除

        self.logger.info("---step33  搜索标签　绝色美女　")

        url_33 = self.baseurl + "/sensemedia/face_in/v2/labels"
        r_33 = requests.get(url_33, headers=self.json_headers)
        self.logger.info(r_33.text)

        # 检查http 状态码
        if r_33.status_code != requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_33.status_code)
            assert False
        self.logger.info("status code is %s" % r_33.status_code)

        if "绝色美女" in r_33.text.encode("utf-8") or "绝色大美女" in r_33.text.encode("utf-8"):
            self.logger.error("find　标签　绝色美女, not as expected !")
            assert False

        # 34，　确认人物已删除

        self.logger.info("---step34  人物搜索接口，确认人物已删除 ")

        url_34 = self.baseurl + "/sensemedia/face_in/v2/persons "

        payload = {'name': '李欣萌，李萌新', }
        r_34 = requests.get(url_34, params=payload, headers=self.json_headers)
        self.logger.info(r_34.text)

        # 检查http 状态码
        if r_34.status_code == requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r_34.status_code)
            assert False
        self.logger.info("status code is %s" % r_34.status_code)

        if "李欣萌" in r_34.text.encode("utf-8") or "李萌新" in r_34.text.encode("utf-8"):
            self.logger.error(" find 李欣萌 or　李萌新　, not as expected ！")
            assert False

    def teardown(self):
        self.logger.info("test teardown")