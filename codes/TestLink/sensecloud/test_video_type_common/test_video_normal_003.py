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
用例名字：test_video_normal_003
测试目的：https--MP4-普通电影
预置条件：1，测试桩已启动（接收callback 的post 请求）
         2,私有云已启动
         3,视频文件:  已经放到当前目录
测试步骤：1，构造请求发送https--MP4-普通电影视频给私有云分析
         2，检查响应,记录响应结果
预期结果：1，响应状态码200
         2，应答结果检查：
         3，callback ... 通过requestid 查询结果是否完成
         4，超时机制（(视频时长×(功能1超时倍数+功能2超时倍数+...+功能n超时倍数)*整体超时倍数) = 超时时长）

content-type:application/json

"""
#@SkipTest
@attr(feature="test_video_transports_common")
@attr(runtype="normal")
@attr(videotype="normal")
class test_video_normal_003(common.sensemediaTestBase):

    def __init__(self):
        super(test_video_normal_003, self).__init__("test_video_normal_003")
        common.sensemediaTestBase.setlogger(self, __name__)

        #超时时间(任务需在自指定时间内完成，否则置为失败),检测间隔为test_interval
        self.expire = 300
        self.test_interval = 5

        #请求url
        self.url = common.getConfig("url", "cloud_url")
        self.logger.info("testcase is %s " % self.testid)
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("request url is %s" % self.url)

        # get_res_url(通过此url 查询任务状态)
        self.res_url = common.getConfig("url", "res_url")

        # request url
        self.file = ""
        # TODO
        self.video_url = "https://172.20.14.63:6554/hebing/politician_17g.mp4"

        # self.video_url = "https://172.20.14.63:6554/zuixiao.mp4"



        self.stream = ""
        self.frame_extract_interval = ""
        self.modules = ""
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = ""

        # 请求体
        self.body = {
            "url": self.video_url,
            "callback": self.callback,
            "token": self.token,
            "modules": "filter_politician"

        }
        # 请求头
        self.headers = {'content-type': 'application/json'}


        #期望使用的modules
        self.expect_modules=["filter_politician",]
        #probability 最低限度
        self.probability_low=0
        #probability 最高限度
        self.probability_high=1

    def setup(self):
        self.logger.info("test setup")

    def test_001(self):

        self.logger.info("now to send request,body is  %s!" % self.body )

        # 发送request请求
        r = requests.post(self.url, data=json.dumps(self.body), headers=self.headers)

        self.logger.info(r.text)

        # 检查http 状态码
        if r.status_code == requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r.status_code)
            assert False
        self.logger.info("status code is %s" % r.status_code)

        if r.json().get("http_code") == 500:
            self.logger.error("status code is %s,not as expected" % r.status_code)
            assert False

        if r.json().get("error_msg") != "File is too large":
            self.logger.error("error_msg should be Request stream is invalid ")
            assert False

        if r.json().get("http_code") != 400:
            assert False

        if r.json().get("error_code") != 1010102:
            assert False

        if r.json().get("status") != "error":
            assert False


    def teardown(self):
        self.logger.info("test teardown")





"""
{
  "content": [
    {
      "isFinished": 1,
      "updateTime": "2018-12-03T16:21:02.000+0000",
      "createTime": "2018-12-03T16:21:02.000+0000",
      "result": "{\"result_urls\":[\"http://172.20.23.43/sensemedia/video/result/1DpuFyjvhoLy1R9ksaWXCJPpIm3.json\",\"http://172.20.23.43/sensemedia/video/result/1DpuG0QnL1exc0KPartoQOlUNGX.json\"]}",
      "taskId": "afcd13d5-b386-422c-ad99-5da99cef54b7",
      "requestId": "0608aaf4-0fff-48c4-8408-e656bb151c8e",
      "id": 75
    },
    {
      "isFinished": 1,
      "updateTime": "2018-12-03T15:40:11.000+0000",
      "createTime": "2018-12-03T15:40:11.000+0000",
      "result": "image dispatch error",
      "taskId": "afcd13d5-b386-422c-ad99-5da99cef54b7",
      "requestId": "0608aaf4-0fff-48c4-8408-e656bb151c8e",
      "id": 51
    }
  ],
  "size": 2
}

"""