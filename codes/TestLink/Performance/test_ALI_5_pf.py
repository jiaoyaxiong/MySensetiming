#encoding:utf-8
import base64
import sys
sys.path.append("..")
import os
import common
import requests
import uuid
import json
from requests_toolbelt import MultipartEncoder
from nose.plugins.attrib import attr
from nose import SkipTest
import testlink
import time
from prettytable import PrettyTable
from requests_toolbelt import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, wait
import shlex, subprocess




"""
First TestCase with TestLink
For Performance
约束，性能测试只有一个测试计划,build name 是float
"""




@attr(feature="test_callback_common")
@attr(runtype="abnormal")
@attr(videotype="normal")
class test_ALI_5(common.sensemediaTestBase):

    def __init__(self):
        super(test_ALI_5, self).__init__("test_ALI_5")
        common.sensemediaTestBase.setlogger(self, __name__)
        self.testid="ALI-5"
        #下文的self.tpid
        self.testplanid=""
        #建议获取最新的buildname(),下文中的self.build_name
        self.buildname=""
        #ｅｇ:"2019-01-18 14:55"
        self.timestamp=time.strftime("%Y-%m-%d %H:%m")
        self.testcasestarttime=time.time()
        self.execduration=""
        #获取TestLink　该用例的一些信息
        self.testlink_url = common.getConfig("url", "testlinkurl")
        self.testlink_key = common.getConfig("url", "testlinkkey")
        self.project_id = common.getConfig("url", "project_id")
        self.project_name = common.getConfig("url", "project_name")
        self.logger.info("project name is %s "% self.project_name)
        self.testPlanName = common.getConfig("url", "testPlanName")






    def setup(self):
        self.logger.info("test setup")
        #获取testlink连接
        self.tlc = testlink.TestlinkAPIClient(self.testlink_url, self.testlink_key)
        #获取testplane name
        tp = self.tlc.getTestPlanByName(self.project_name, self.testPlanName)
        #获取第一个testplan 的id
        self.tpid = tp[0]["id"]
        # 获取性能测试集的id
        testsuite_id =""
        top_suites = self.tlc.getFirstLevelTestSuitesForTestProject(self.project_id)
        for suite in top_suites:
            if suite["name"] == u"性能测试":
                testsuite_id = suite["id"]
        #获取该用例的版本信息,最大的那个
        versions=list()
        ids = self.tlc.getTestCasesForTestPlan(self.tpid)
        self.logger.info("ids is %s " % ids)

        for te in ids.keys():
            for te_v in ids[te]:
                if te_v['full_external_id'] == self.testid:
                    versions.append(te_v["version"])
        maxversion= int(max(versions))
        self.logger.info("version is %s " % maxversion)
        #获取最新的build name
        self.build_names = self.tlc.getBuildsForTestPlan(self.tpid)
        self.logger.info("build names  is %s " % self.build_names)
        build_list = [ float(i["name"]) for i in self.build_names ]
        self.logger.info("build_list  is %s " % build_list)
        self.build_name= max(build_list)
        self.logger.info("build name  is %s " % self.build_name)




        # 获取该用例的测试关键字
        self.concurrency = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "concurrency", "simple")["value"]
        self.logger.info("concurrency is %s " % self.concurrency)
        self.round = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "round", "simple")["value"]
        self.logger.info("round is %s " % self.round)
        self.ip = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "ip", "simple")["value"]
        self.logger.info("ip is %s " % self.ip)
        self.port = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "port", "simple")["value"]
        self.logger.info("port is %s " % self.port)
        self.url = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "url", "simple")["value"]
        self.logger.info("url is %s " % self.url)
        self.layout = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "layout", "simple")["value"]
        self.logger.info("layout is %s " % self.layout)
        self.appFunction = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "x-acs-app-function", "simple")["value"]
        self.logger.info(" x-acs-app-function is %s " % self.appFunction)
        self.files = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "files","simple")["value"]
        self.logger.info(" files is %s " % self.files)
        self.host = self.tlc.getTestCaseCustomFieldDesignValue(self.testid, maxversion, self.project_id, "host","simple")["value"]
        self.logger.info(" host is %s " % self.host)




    def test_001(self):

        moitor_pid=self.monitor_begin()
        self.collectZip(self.files)
        self.init(self.ip,self.port)
        self.qps = self.perfomanceest(self.ip,self.port,self.url,self.appFunction,self.concurrency,self.round,self.files)
        self.monitor_end(moitor_pid)

    def teardown(self):
        os.system("rm -rf testdata/*")
        self.testcaseendtime=time.time()
        execduration=int(self.testcaseendtime-self.testcasestarttime)/60
        # self.logger.info(type(self.testid),type(self.tpid),type(self.build_name),type(self.qps),type(execduration),type(self.timestamp))
        
        self.logger.info("1 is %s" % self.testid)
        self.logger.info("1 is %s" % self.tpid)
        self.logger.info("1 is %s" % self.build_name)
        self.logger.info("1 is %s" % self.qps)
        self.logger.info("1 is %s" % self.timestamp)

        notes="costtime is %s　seconds  ,qps is %s " %(self.cost_time,self.qps)


        self.result = self.tlc.reportTCResult(testcaseexternalid=self.testid, testplanid=self.tpid,
                                         buildname=str(self.build_name),
                                         status="p", notes=notes, execduration=execduration,
                                         timestamp=self.timestamp,customfields={"qps":str(self.qps)})

        self.result_id = self.result[0]["id"]

        self.upload_png_to_estlink()
        os.system("rm -rf raw_data/*")
        #upload

        #TODO 上传附件　,性能测试前需先进行次初始化

    def collectZip(self,url):
        """
        下载某个url 下面的zip包到当前文件下的testdata 文件夹里面
        如果是txt 文件则下载所列的zip包
        :param url:
        :return:
        """
        isExists = os.path.exists("testdata")
        if not isExists:
            os.mkdir("testdata")

        if url.endswith(".zip"):
            file_name = url.split("/")[-1]
            print file_name
            local_file_path = "testdata/%s" % file_name

            if os.path.exists(local_file_path):
                print("something error,there should not have file : %s " % local_file_path)
                return False

            r = requests.get(url)
            with open(local_file_path, "wb") as f:
                f.write(r.content)
        elif url.endswith(".txt"):
            # 先下载下来txt 文件
            file_name = url.split("/")[-1]
            print file_name
            local_file_path = "testdata/%s" % file_name

            if os.path.exists(local_file_path):
                print("something error,there should not have file : %s " % local_file_path)
                return False
            r = requests.get(url)
            with open(local_file_path, "wb") as f:
                f.write(r.content)

            # 删除文件里的空行
            os.system("sed -i /^$/d %s " % local_file_path)

            # 把txt 文件里的zip 包文件下载下来
            with open(local_file_path) as f:
                for x in f.readline():
                    if x.endswith(".zip"):
                        file_name = x.split("/")[-1]
                        print file_name
                        local_file_path = "testdata/%s" % file_name

                        if os.path.exists(local_file_path):
                            print("something error,there should not have file : %s " % local_file_path)
                            return False

                        r = requests.get(url)
                        with open(local_file_path, "wb") as f:
                            f.write(r.content)

        return True

    def perfomanceest(self,ip,port,url,function,concurrency,round,filename):
        """
        性能测试
        :param para:对应excel 某一行的数据,注意不要enbale 是0 的数据传过来
        :return:
        """

        invoke_server_url = "http://{}:{}{}".format(ip, port,url)
        time_start = time.time()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        file_name = filename.split("/")[-1]
        local_file_path = "testdata/%s" % file_name

        self.logger.info("Performance begin function is %s" % function)
        pool = ThreadPoolExecutor(int(concurrency))
        task_list = []
        for i in range(int(round)):
            task = pool.submit(self.ZipTask, invoke_server_url,function,file_name )
            task_list.append(task)
        wait(task_list)
        self.logger.info("Performance End function is %s" % function)
        time_end = time.time()

        num = self.hasHowMuchFile(local_file_path)
        self.logger.info(" filename %s  num is %s " % (file_name,num))
        self.cost_time = int(time_end - time_start)
        self.logger.info(" cost time is %s " % self.cost_time)
        qps = (int(num) * int(round)) / self.cost_time
        self.logger.info(" qps is %s " % qps)
        return qps


    def ZipTask(self,invoke_server_url,function,file_name):
        """
        发送zip 方式的http 请求
        :param para:
        :param job_id:
        :param last_info:
        :return:
        """
        if function != "Tracking":
            file_name = "testdata/" +file_name
            body = MultipartEncoder(
            fields={
                "files": (file_name.split("/")[-1], open(file_name, 'rb'), 'application/jpeg'),
                "mode": "sync"
            }
        )
            uuid_resq=str(uuid.uuid1())
            self.logger.info("zip task url is %s " % invoke_server_url)

            resp = requests.post(invoke_server_url, data=body,
                                 headers={
                                     'Content-Type': body.content_type,
                                     'x-acs-app-function': function,
                                     'x-acs-trace-id': uuid_resq})


            # self.logger.info("performance test with zip file , uuid is={} retcode={}, resp={}".format(uuid_resq,resp.status_code, resp.text))
            self.logger.info("performance test with zip file , uuid is={} retcode={}".format(uuid_resq,resp.status_code))

        return True


    def hasHowMuchFile(self,file):
        """
        判断zip 包里含有多少文件
        :param file:
        :return:
        """
        num_cmd = "unzip -l %s | tail -n 1 | awk '{print $2}'" % file
        num = os.popen(num_cmd).read()
        return num

    def init(self,ip,port):

        init_server_url = "http://{}:{}/initialize".format(ip, port)
        initialized = False
        self.logger.info("initialize")
        for i in range(10):
            if self.http_post_1(init_server_url)[0] == 200:
                self.logger.info("initialized")
                initialized = True
                break
            else:
                self.logger.error("waiting initialize {} times".format(i))
                time.sleep(5)

        if initialized == False:
            self.logger.error("AI not initialized")
            return False
        self.logger.info("initialize End \n")
        return True

    def http_post_1(self,url):
        try:
            resp = requests.post(url)
            return resp.status_code, resp.text
        except Exception as e:
            print(str(e))
            exit(1)


    def monitor_begin(self):
        start_sh_cmd = "sh performance.sh %s " % self.appFunction
        start_cmd = shlex.split(start_sh_cmd)
        p = subprocess.Popen(start_cmd)
        self.logger.info("monitor pid is  %s "% p.pid)
        return p.pid

    def monitor_end(self,pid):
        time.sleep(5)
        kill_cmd = "kill -2 %s " % pid
        os.system(kill_cmd)
        # 绘图需要时间，建议再延时30秒
        time.sleep(30)

    def upload_png_to_estlink(self):
        if os.path.exists("./raw_data/xiancun.png"):
            self.tlc.uploadExecutionAttachment("./raw_data/xiancun.png", self.result_id, "xiancun", "xiancun")


        if os.path.exists("./raw_data/gpu.png"):
            self.tlc.uploadExecutionAttachment("./raw_data/gpu.png", self.result_id, "gpu", "gpu")

        if os.path.exists("./raw_data/cpu_idle.png"):
            self.tlc.uploadExecutionAttachment("./raw_data/cpu_idle.png", self.result_id, "cpu_idle", "cpu_idle")

        if os.path.exists("./raw_data/memory.png"):
            self.tlc.uploadExecutionAttachment("./raw_data/memory.png", self.result_id, "memory", "memory")

    def upload_attachmens(self,file_path,id,fujian,fujianmiaoshu):

        self.tlc.uploadExecutionAttachment(file_path, self.result_id, fujian, fujianmiaoshu)
