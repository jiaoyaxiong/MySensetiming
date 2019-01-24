#encoding:utf-8
import sys
sys.path.append("..")
import common
import os
import requests
import uuid
import json
from requests_toolbelt import MultipartEncoder





class test_viedo_normal_001(common.sensemediaTestBase):

    def __init__(self):
        super(test_viedo_normal_001, self).__init__("test_viedo_normal_001")
        common.sensemediaTestBase.setlogger(self,__name__)
        self.url=common.getConfig("url","video_tag_common")
        self.logger.info("testcase is %s " % self.testid)
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("url is %s" % self.url)

    def setup(self):
        pass

    def test_001(self):
        self.uuid = uuid.uuid1()


        jsonstr=json.dumps([{"url": "http://127.0.0.1:90/2.jpg","id":"2"}])

        self.postdata = {
            "srcUris":jsonstr
        }

        body = MultipartEncoder(
            fields={
                'files': ("xxx", open("3.zip", 'rb'), 'application/jpeg'),
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

        self.logger.info(r.text)
        # self.logger.info(r.request.headers)
        # self.logger.info(r.request.body)
        self.logger.info(r.json)

        if r.status_code <> requests.codes.ok:
            self.logger.error("status code is %s" % r.status_code)
            assert False
        pass



    def teardown(self):
        self.logger.info("test teardown")
