#encoding:utf-8
import sys
sys.path.append("..")
import common
import os
import requests
import uuid
import json
from requests_toolbelt import MultipartEncoder
import random


"""
仅上传单个图片
测试目的：
测试步骤：
1，事件、物体、场景三个大类，每个类随机选择5个小类，每个小类随机选择5张图片，测试是否能检测出正确的tag
预期结果：
1.所有的都可以检测出正确的tag
"""


class test_viedo_normal_002(common.sensemediaTestBase):

    def __init__(self):
        super(test_viedo_normal_002, self).__init__("test_viedo_normal_001")
        common.sensemediaTestBase.setlogger(self,__name__)
        self.url=common.getConfig("url","video_tag_common")
        self.logger.info("testcase is %s " % self.testid)
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("url is %s" % self.url)

    def setup(self):
        pass

    def test_002(self):

        #找出目录下所有的图片文件及路劲
        pic_ad=common.getConfig("address","local_image")
        pic_ad_imagetag = os.path.join(pic_ad,"imgtag_benchmark")
        self.logger.info("local image address is %s " % pic_ad_imagetag)
        cls=os.listdir(pic_ad_imagetag)
        abspa=map(lambda x:os.path.join(pic_ad_imagetag,x),cls)
        self.logger.info("abspath is %s " % abspa)

        test_image_=list()

        for x in abspa:
            a=random.sample(os.listdir(x),5)
            # self.logger.info("a is %s " % a)
            a_abs=map(lambda y:os.path.join(x,y),a)
            for z in a_abs:
                b=random.sample(os.listdir(z),5)
                # self.logger.info("b is %s " % b)
                b_abs=map(lambda y:os.path.join(z,y),b)
                test_image_.extend(b_abs)
        # self.logger.info("test_image is %s " % test_image_)
        self.logger.info("first image is %s " % test_image_[0])
        http_image_add=map(lambda x:"http://127.0.0.1:90/"+"/".join(x.split("/")[3:]),test_image_)
        self.logger.info(" http image address is %s " % http_image_add[0])



        #仅测验一张数据

        self.uuid = uuid.uuid1()
        pic_tag=http_image_add[0].split("/")[-2]

        jsonstr=json.dumps([{"url":http_image_add[0] ,"id":"2"}])

        self.postdata = {
            "srcUris":jsonstr
        }

# "http://127.0.0.1:90/2.jpg"
#http_image_add[0]
        # body = MultipartEncoder(
        #     fields={
        #         'srcUris': '[{"url":"http://127.0.0.1:90/2.jpg","id":"2"}]'
        #     }
        # )

        body = MultipartEncoder(
            fields={
                'srcUris': json.dumps([{"url":http_image_add[0],"id":str(random.choice(range(10)))}])
            }
        )



        self.headers = {'content-type':body.content_type,
                        'x-acs-app-function': 'Filter',
                        "x-acs-trace-id": self.uuid}

        # self.headers = {'content-type': 'multipart/form-data',
        #                 'x-acs-app-function': 'Filter',
        #                 "x-acs-trace-id": self.uuid}

        self.logger.info("test beginning!,uuid is %s" % self.uuid)

        r = requests.post(self.url, data=body, headers=self.headers)

        self.logger.info("!!!!!!!!!!!!!!!!!!!!")
        self.logger.info(r.headers)

        self.logger.info(r.text)
        # self.logger.info(r.request.headers)
        # self.logger.info(r.request.body)
        #self.logger.info(r.json)

        dict=json.loads(r.text)
        self.logger.info("pic tag is %s " % pic_tag)
        try:
            succ=dict.get("succ_results")[0]
            self.logger.info("succ_results is %s " % succ)

            res = succ.get("results")
            self.logger.info("res is %s " % res)

            tag = succ.get("results")[0].get("tags")[0].get("tag")
            self.logger.info(" http image address is %s " % http_image_add[0])
            self.logger.info("pic tag is %s " % pic_tag)
            self.logger.info("ai tag is %s " % tag)

            tag = tag.encode("utf-8")
            if tag == pic_tag:
                self.logger.info("very good!")
        except Exception as e:
            self.logger.error("not get tag")
            assert False

        if r.status_code <> requests.codes.ok:
            self.logger.error("status code is %s" % r.status_code)
            assert False
        pass



    def teardown(self):
        self.logger.info("test teardown")
