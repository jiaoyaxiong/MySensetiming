# encoding=utf-8

import os
import sys
import json
import time
import uuid
import requests
from prettytable import PrettyTable
from requests_toolbelt import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, wait

reload(sys)
sys.setdefaultencoding('utf-8')


def http_post_with_file(url, file, param_dict):
    try:
        file_name = file.split('/')[-1]
        files = {'files': (file_name, open(file, 'rb'), 'application/jpeg')}

        if param_dict.has_key('jobId'):
            job_id = param_dict['jobId']
        else:
            job_id = ""

        if param_dict.has_key('last'):
            last = param_dict['last']
        else:
            last = False

        data = {'mode': param_dict["mode"], 'layout': param_dict["layout"], 'jobId': job_id, 'last': last}

        resp = requests.post(url, files=files, data={'param': json.dumps(data)},
                             headers={'x-acs-app-function': param_dict["function"],
                                      'x-acs-trace-id': str(uuid.uuid1())})

        if param_dict["debug"] == 'True':
            print("http_post_with_file, retcode={}, resp={}".format(resp.status_code, resp.text))
        else:
            print("http_post_with_file, retcode={}".format(resp.status_code))

        return resp.status_code
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


def http_post(url, headers={}):
    try:
        resp = requests.post(url, headers=headers)
        return resp.status_code, resp.text
    except Exception as e:
        print(str(e))
        exit(1)


def my_task(server_url, zip_file, param_dict):
    http_post_with_file(server_url, zip_file, param_dict)


def init_params_value(key, params_value):
    value = os.environ.get(key)
    if value:
        params_value[key] = value
    else:
        print("wrong {}: {}".format(key, value))
        exit(1)


def select_dataset(param_dict):
    function = param_dict["function"]
    dataset = param_dict["dataset"]
    layout = param_dict["layout"]

    dataset_meta = {}
    if function in ['OCR']:
        if layout == "IDCard":
            if dataset == "50":
                dataset_meta["dataset"] = "dataset/dataset_idcard_50.zip"
                dataset_meta["num"] = 50
            else:
                dataset_meta["dataset"] = "dataset/dataset_idcard_200.zip"
                dataset_meta["num"] = 200
        elif layout == "BankCard":
            if dataset == "50":
                dataset_meta["dataset"] = "dataset/dataset_bankcard_50.zip"
                dataset_meta["num"] = 50
            else:
                dataset_meta["dataset"] = "dataset/dataset_bankcard_200.zip"
                dataset_meta["num"] = 200
        elif layout == "Vehicle" or layout == "Driver":
            if dataset == "50":
                dataset_meta["dataset"] = "dataset/dataset_vehicle_50.zip"
                dataset_meta["num"] = 50
            else:
                dataset_meta["dataset"] = "dataset/dataset_vehicle_200.zip"
                dataset_meta["num"] = 200
        else:
            print("layout not supported")
            exit(1)
    elif function in ['FilterCelebrity', 'CelebrityAttrDetect', 'FeatureCompare', 'FeatureExtract']:
        if dataset == "50":
            dataset_meta["dataset"] = "dataset/dataset_celebrity_50.zip"
            dataset_meta["num"] = 50
        else:
            dataset_meta["dataset"] = "dataset/dataset_celebrity_200.zip"
            dataset_meta["num"] = 200
    elif function in ['Tracking']:
        dataset_meta["dataset"] = "dataset/dataset_tracking_200"
        dataset_meta["num"] = 200
    else:
        if dataset == "50":
            dataset_meta["dataset"] = "dataset/dataset_50.zip"
            dataset_meta["num"] = 50
        else:
            dataset_meta["dataset"] = "dataset/dataset_200.zip"
            dataset_meta["num"] = 200

    print("dataset meta: {}".format(dataset_meta))
    return dataset_meta


if __name__ == '__main__':
    #读取Excel 文件，设置环境变量，每次读取一行，

    workspace = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(workspace)

    # 获取变量参数
    params_key = ['ip', 'port', 'round', 'dataset', 'concurrency', 'function', 'mode', 'layout', 'debug']
    params_value = {}

    for key in params_key:
        init_params_value(key, params_value)

    # server url
    init_server_url = "http://{}:{}/initialize".format(params_value["ip"], params_value["port"])

    initialized = False
    print("======================  initialize  =====================")
    for i in range(10):
        if http_post(init_server_url)[0] == 200:
            print("initialized")
            initialized = True
            break
        else:
            print("waiting initialize {} times".format(i))
            time.sleep(5)

    if initialized == False:
        print("AI not initialized")
        exit(1)
    print("======================  initialize End  =====================\n")

    invoke_server_url = "http://{}:{}/invoke".format(params_value["ip"], params_value["port"])

    # dataset
    zip_file = select_dataset(params_value)

    # execute
    time_start = time.time()
    if params_value["function"] == "Tracking":
        # TrackStart
        print("======================  TrackStart  ======================")
        headers = {'x-acs-trace-id': str(uuid.uuid1()), 'x-acs-app-function': 'TrackStart',
                   'Content-Type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"}
        code, text = http_post(invoke_server_url, headers)
        if code == 200:
            print("TrackStart: {}".format(text))
            job_id = json.loads(text)["result"]["jobId"]
        else:
            print("TrackStart failed, code={}, msg={}".format(code, text))
            exit(1)
        print("======================  TrackStart End ======================\n")

        # Tracking
        params_value["jobId"] = job_id
        params_value["round"] = 10
        params_value["concurrency"] = 1
        params_value["function"] = "Tracking"
        print("======================  Tracking  ======================")
        pool = ThreadPoolExecutor(params_value["concurrency"])
        task_list = []
        for i in range(params_value["round"]):
            if i == (params_value["round"] - 1):
                params_value["last"] = True
            else:
                params_value["last"] = False
            task = pool.submit(my_task, invoke_server_url, "{}_{}.zip".format(zip_file["dataset"], i), params_value)
            task_list.append(task)
        wait(task_list)
        print("======================  Tracking End  ======================\n")

        # TrackEnd
        print("======================  TrackEnd  =====================")
        headers = {'x-acs-trace-id': str(uuid.uuid1()), 'x-acs-app-function': 'TrackEnd'}
        body = {'jobId': job_id}
        code, text = http_post_with_body(invoke_server_url, headers, body)
        if code == 200:
            print("TrackEnd: ", text)
        else:
            print("TrackEnd failed, code={}, msg={}".format(code, text))
            exit(1)
        print("======================  TrackEnd End =====================\n")
    else:
        print("======================  Performance  ======================")
        pool = ThreadPoolExecutor(int(params_value['concurrency']))
        task_list = []
        for i in range(int(params_value["round"])):
            task = pool.submit(my_task, invoke_server_url, zip_file["dataset"], params_value)
            task_list.append(task)
        wait(task_list)
        print("======================  Performance End ======================\n")
    time_end = time.time()

    x = PrettyTable(["function", "dataset", "concurreny", "total", "cost(s)", "qps", "avg(ms)"])
    row_0 = params_value["function"]
    row_1 = zip_file["dataset"]
    row_2 = params_value["concurrency"]
    row_3 = zip_file["num"] * int(params_value["round"])
    row_4 = time_end - time_start
    row_5 = row_3 / row_4
    row_6 = 1 / row_5
    x.add_row([row_0, row_1, row_2, row_3, row_4, row_5, row_6])
    print(x)
