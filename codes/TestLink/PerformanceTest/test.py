
import uuid
from requests_toolbelt import MultipartEncoder
import json,requests,os

print os.getcwd()
invoke_server_url="http://172.20.20.224:50100/invoke"
body=MultipartEncoder(
        fields={
            "files":("dataset_celebrity_200.zip", open("testdata/dataset_celebrity_200.zip", 'rb'), 'application/jpeg'),
            "mode" : "sync",
            'layout': "xxx",
            'jobId': "xxx",
            'last': "xxx"
        }
    )


resp = requests.post(invoke_server_url, data=body,
                             headers={
                                     'Content-Type': body.content_type,
                                      'x-acs-app-function': "FilterCelebrity",
                                      'x-acs-trace-id': str(uuid.uuid1())})

print resp.text
