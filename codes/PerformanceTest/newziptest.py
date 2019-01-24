# encoding:utf-8
import os
import sys
import json
import time
import uuid
import requests
from prettytable import PrettyTable
from requests_toolbelt import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, wait
import xlrd
import xlwt
from xlutils.copy import copy
import shlex, subprocess
import datetime
from ftplib import FTP

reload(sys)
sys.setdefaultencoding('utf-8')
"""
约束条件：
    1：Tracking 测试多少轮，则txt 文件所指的zip 包里面有多少个zip 文件
    2：提供的zip 包第一层目录就是图片文件，不允许有文件夹，否则会判断图片数目出错
    3：多线程的多个请求uuid使用的是一样的
"""

ftp_url="ftp://172.20.20.225"
ftp_user="sensemedia"
ftp_passwprd="S@nsemedia2019"

def readExcelData(address):
    """
    读取excel performance settings 页面的 数据，每一行的数据变成一个list，多个list构成一个list返回
    :param address:Excel 地址
    :return: [[],[],...] or False
    """
    testPara=list()
    workbook = xlrd.open_workbook(address)
    sheet = workbook.sheet_by_name('performance settings')
    #校验第一行的字段与规定是否相同
    first_row=sheet.row_values(0)
    if first_row != [u'id', u'enable', u'modules', u'ip', u'port', u'round', u'concurrency', u'url', u'layout', u'x-acs-app-function', u'files', u'HOST']:
        print("!!!!!! Excel first row should is [u'id', u'enable', u'modules', u'ip', u'port', u'round', u'concurrency', u'url', u'layout', u'x-acs-app-function', u'files', u'HOST']")
        print("!!!!!! but Excel first row    is %s" %first_row )
        return False
    for i in range(1,sheet.nrows):
        testPara.append(sheet.row_values(i))

    # TODO(增加校验第二个sheet页是否合法)
    return testPara


def writeExcelData(address,para):
    """
    在performance test 页面里面新一行写入性能测试记录
    仅写入一行数据
    :param address: Excel地址
    :param para: 需要累加写入Excel 的数据
    :return:  True/False
    """

    wb = xlrd.open_workbook(address)
    newb = copy(wb)
    sheet = newb.get_sheet(1)
    if sheet.name != "performance test":
        print("!!!!!! not find sheet : performance test")
        return False
    #获取sheet页有多少行数据
    length= len(sheet.rows)
    # 往新行写入数据
    for i in range(len(para)):
        # print "nidayenidaye"
        # print i
        # print para
        # print type(para)
        # print para[i]
        sheet.write(length,i,para[i])
    #保存数据
    newb.save(address)
    return True

def postZipRequest(paras):
    """
    根据参数发送http请求
    :param paras:
    :return:
    """

def collectZip(url):
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
        file_name=url.split("/")[-1]
        print file_name
        local_file_path="testdata/%s" % file_name

        if os.path.exists(local_file_path):
            print("something error,there should not have file : %s " % local_file_path)
            return False

        r = requests.get(url)
        with open(local_file_path,"wb") as f :
            f.write(r.content)
    elif url.endswith(".txt"):
        #先下载下来txt 文件
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
        os.system("sed -i /^$/d %s "% local_file_path)



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


def collectAllZip(paras):
    """
    下载所有的测试zip 到当前文件下的testdata 文件夹里面,
    :param paras:[[],[]]  第十行是zip 地址
    :return:
    """
    ziplist=[]

    #url 去重
    for x in paras:
        #TODO(如果function是Tacking 的话该如何处理)
        ziplist.append(x[10].encode("utf-8"))
    ziplist = list(set(ziplist))

    for x in ziplist:
        if not collectZip(x):
            print("collectzip fail:%s "% x)
            return False
    return True


def send_zip_requests(para):
    """
    根据参数发送zip 请求
    :param para: [[],[]]
           eg:[[1.0, 1.0, u'video_tag', u'172.20.20.225', 21000.0, u'\u6d4b\u8bd5\u591a\u5c11\u8f6e', u'\u5e76\u53d1\u7ebf\u7a0b\u6570', u'/invoke', u'IDCard', u'VideoTag', u'http://172.20.20.225:8000/images/common/crush.zip', u'172.20.20.225\uff0c\n\u63cf\u8ff0\u4e3b\u673a\u7684\u786c\u4ef6\u914d\u7f6e\uff0ccpu\u578b\u53f7\u3001GPU\u578b\u53f7\uff1b\n\u63cf\u8ff0\u4e3b\u673a\u7684\u8f6f\u4ef6\u914d\u7f6e\n\u53ef\u4ee5\u5355\u72ec\u52a0\u4e00\u4e2aCSV\uff0c\u91cc\u9762\u7f57\u5217\u4e86HOST\u7684\u914d\u7f6e\u4fe1\u606f\n']]
    :return:
    """
    pass

def http_post_1(url):
    try:
        resp = requests.post(url)
        return resp.status_code, resp.text
    except Exception as e:
        print(str(e))
        exit(1)

def init(para):
    """
    做initialize and Tracking
    :param para:对应excel 某一行的数据,注意不要enbale 是0 的数据传过来
    :return:true or False
    """
    init_server_url = "http://{}:{}/initialize".format(para[3].encode("utf-8"), int(para[4]))
    initialized = False
    print("initialize")
    for i in range(10):
        if http_post_1(init_server_url)[0] == 200:
            print("initialized")
            initialized = True
            break
        else:
            print("waiting initialize {} times".format(i))
            time.sleep(5)

    if initialized == False:
        print("AI not initialized")
        return False
    print("initialize End \n")
    return True

def http_post(url, headers={}):
    try:
        resp = requests.post(url, headers=headers)
        return resp.status_code, resp.text
    except Exception as e:
        print(str(e))
        exit(1)

def http_post_with_body(url, headers, body):
    try:
        payload = "{}{}{}".format(
            "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"param\"\r\n\r\n{\"jobId\":\"",
            body["jobId"],
            "\",\"attribute\":true, \"last\": true,\"feature\":true}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--")

        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'x-acs-trace-id': "dfafdasfdadsfadsfdasdfdasfdsafda",
            'x-acs-app-function': "TrackEnd"
        }

        resp = requests.post(url, data=payload, headers=headers)
        return resp.status_code, resp.text
    except Exception as e:
        print(str(e))
        exit(1)

def zipTask(para,job_id=None,last_info=None):
    """
    发送zip 方式的http 请求
    :param para:
    :param job_id:
    :param last_info:
    :return:
    """
    invoke_server_url = "http://{}:{}/invoke".format(para[3].encode("utf-8"), int(para[4]))
    function = para[9].encode("utf-8")

    if function != "Tracking":
        file_name = "testdata/"+para[10].encode("utf-8").split("/")[-1]
        files = {'files': (file_name.split("/")[-1], open(file_name, 'rb'), 'application/zip')}
    else:

        file_name = para[10].encode("utf-8").split("/")[-1]
        print file_name
        local_file_path = "testdata/%s" % file_name





        #读取第一行的数据并删除第一行数据
        with open(local_file_path) as f:

            file_name ="testdata/"+f.readline().split("/")[-1]
            files = {'files': (file_name.split("/")[-1], open(file_name, 'rb'), 'application/jpeg')}
        #删除文件第一行
        os.system("sed -i 1d %s"% local_file_path)

    body = MultipartEncoder(
        fields={
            "files":(file_name.split("/")[-1], open(file_name,'rb'), 'application/jpeg'),
            "mode" : "sync",
            'layout': para[8].encode("utf-8"),
            'jobId': job_id, 'last': last_info

        }
    )


    resp = requests.post(invoke_server_url,  data=body,
                             headers={
                                     'Content-Type': body.content_type,
                                      'x-acs-app-function': function,
                                      'x-acs-trace-id': para[-1]})


    print("performance test with zip file , retcode={}, resp={}".format(resp.status_code, resp.text))
    return resp.status_code


def hasHowMuchFile(file):
    """
    判断zip 包里含有多少文件
    :param file:
    :return:
    """
    num_cmd= "unzip -l %s | tail -n 1 | awk '{print $2}'" % file
    num=os.popen(num_cmd).read()
    return num





def perfomanceTest(para):
    """
    性能测试
    :param para:对应excel 某一行的数据,注意不要enbale 是0 的数据传过来
    :return:
    """
    date=time.strftime("%Y%m%d")
    uuid_haha=str(uuid.uuid1())
    para.append(uuid_haha)



    invoke_server_url = "http://{}:{}/initialize".format(para[3].encode("utf-8"), int(para[4]))
    time_start = time.time()
    start_time= time.strftime("%Y-%m-%d %H:%M:%S")
    #TODO(判断function 是否非法)
    #TODO(触发监控)
    dir_name_sh = uuid_haha+para[9].encode("utf-8")
    start_sh_cmd = "sh performance.sh %s" % dir_name_sh
    start_cmd=shlex.split(start_sh_cmd)
    p=subprocess.Popen(start_cmd)
    print("monitor pid is %s "% p.pid)



    if para[9] == u"Tracking":
        # TrackStart
        print("TrackStart")
        headers = {'x-acs-trace-id': str(uuid.uuid1()), 'x-acs-app-function': 'TrackStart',
                   'Content-Type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"}
        code, text = http_post(invoke_server_url, headers)
        if code == 200:
            print("TrackStart: {}".format(text))
            job_id = json.loads(text)["result"]["jobId"]
        else:
            print("TrackStart failed, code={}, msg={}".format(code, text))
            exit(1)
        print("TrackStart End \n")

        # Tracking
        jobId = job_id

        # 为什么Tracking 的 concurrency 是 1
        # params_value["round"] = 10
        # params_value["concurrency"] = 1
        print("Tracking")

        #判断约束条件1
        file_name = para[10].encode("utf-8").split("/")[-1]
        print file_name
        local_file_path = "testdata/%s" % file_name
        with open(local_file_path) as f:
            a = len(f.readlines())
            if a != int(para[5]):
                print("error! Tracking round %s must equal txt rows %s" % (int(para[5]).encode("utf-8"),a))
                return False
        pool = ThreadPoolExecutor(int(para[6].encode("utf-8")))
        task_list = []
        for i in range(int(para[5].encode("utf-8"))):
            if i == (int(para[5].encode("utf-8") - 1)):
                last_info = True
            else:
                last_info = False
            #TODO(job id 是zipTask 新增加的参数)
            #TODO(如果是Tracking 的话，对应的URL下面的zip包怎么安排（存放成txt,txt 里面放置url!!!）)
            task = pool.submit(zipTask, para,job_id)
            task_list.append(task)
        wait(task_list)
        print("Tracking End\n")

        # TrackEnd
        print("TrackEnd")
        headers = {'x-acs-trace-id': str(uuid.uuid1()), 'x-acs-app-function': 'TrackEnd'}
        body = {'jobId': job_id}
        code, text = http_post_with_body(invoke_server_url, headers, body)
        if code == 200:
            print("TrackEnd: ", text)
        else:
            print("TrackEnd failed, code={}, msg={}".format(code, text))
            exit(1)
        print("TrackEnd End\n")
    else:
        print("Performance begin function is %s" % para[9].encode("utf-8"))
        pool = ThreadPoolExecutor(int(para[6]))
        task_list = []
        for i in range(int(para[5])):
            task = pool.submit(zipTask,para,)
            task_list.append(task)
        wait(task_list)
        print("Performance End function is %s " % para[9].encode("utf-8"))
    time_end = time.time()

    end_time= time.strftime("%Y-%m-%d %H:%M:%S")
    file_name = para[10].encode("utf-8").split("/")[-1]
    print file_name
    local_file_path = "testdata/%s" % file_name
    num=hasHowMuchFile(local_file_path)
    print("file num is %s "% num)
    cost_time =int(time_end-time_start)
    print("cost time is %s " %cost_time )

    hostipcmd="ifconfig eth0 |grep \"inet addr\" | awk '{print $2 }' | awk -F: '{print $2}'"
    hostip=os.popen(hostipcmd).read()

    round=int(para[5])
    qps=(int(num)*round)/cost_time
    print("qps is %s " % qps)


    #TODO(触发绘图) 延时5秒绘图
    time.sleep(5)
    kill_cmd="kill -2 %s " % p.pid
    os.system(kill_cmd)

    #绘图需要时间，建议再延时10秒
    time.sleep(10)
    # 上传文件到ftp
    upLoadToFtp()
    time.sleep(5)

    cpu_cmd= "cat /proc/cpuinfo  | grep -i 'model name'|sort|uniq "
    gpu_cmd ="nvidia-smi -q | grep \"Product Name\" "
    docker_version_cmd="docker --version"
    cpu=os.popen(cpu_cmd).read().strip()
    gpu=os.popen(gpu_cmd).read().strip()
    docker_version=os.popen(docker_version_cmd).read().strip()

    string_host_info=cpu+"\n"+gpu+"\n"+docker_version

    write_data=hostip,int(para[0]),date,start_time,end_time,para[2].encode("utf-8"),int(para[5]),int(para[6]),para[8].encode("utf-8"),qps,int(num)*round,cost_time, \
               para[10].encode("utf-8"),invoke_server_url,uuid_haha,get_min_max("raw_data/%s%s/mem.txt"%(uuid_haha,para[9].encode("utf-8"))),get_min_max("raw_data/%s%s/xiancun.txt"%(uuid_haha,para[9].encode("utf-8"))),\
               get_min_max("raw_data/%s%s/cpu_idle.txt"%(uuid_haha,para[9].encode("utf-8"))),get_min_max("raw_data/%s%s/GPU.txt"%(uuid_haha,para[9].encode("utf-8"))),"ftp://172.20.20.225/performance_data/%s%s"%(uuid_haha,para[9].encode("utf-8")),string_host_info
    print("!!!!!!!!!!!!!!!!!!")
    print(write_data)

    # 清空本地raw_data

    os.system("rm -rf raw_data/*")

    return write_data


#TODO(原始数据上传到ftp上面)
def upLoadToFtp():
    """
    上传文件到ftp
    :param :
    :return:
    """
    os.system("sh uploadfile.sh")



def get_min_max(file):
    """
    获取文件的最大最小值及delta 值
    :param file:
    :return:
    """
    with open(file) as f:
        a=f.readlines()
    b=list()
    for x in a:
        b.append(float(x.replace("\n","").replace("%","")))
    data = "%s(%s:%s)"%(max(b)-min(b),min(b),max(b))
    return data



if __name__ == "__main__" :

    workspace = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(workspace)
    os.system("rm -rf testdata/*")
    os.system("rm -rf raw_data/*")
    read_results = readExcelData("qps.xlsx")
    print read_results
    if not read_results:
        print("read Excel Fail ")
        sys.exit(1)

    if not collectAllZip(read_results):
        print("collect allzip Fail ")
        sys.exit(1)

    init(read_results[0])
    a=perfomanceTest(read_results[0])
    writeExcelData("qps.xlsx",a)


    os.system("rm -rf testdata/*")





    pass