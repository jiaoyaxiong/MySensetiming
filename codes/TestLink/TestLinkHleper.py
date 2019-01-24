#encoding:utf-8
import base64
"""

api　文档：https://github.com/lczub/TestLink-API-Python-client/blob/master/doc/usage.rst
python2 与该testlink 有兼容性冲突，需修改代码

上传测试结果到testlink需要如下参数：
testcaseid | testcaseexternalid  : 对应的用例ｉｄ,注意是internal id! 或者是testcaseexternalid，　这个是在编写测试用例时由系统
                                    生成的
                                    eg：  testcaseid:14
                                         testcaseexternalid:ALI-1
                                    　　　
testplanid : 计划的ｉｄ ,一个测试计划可以有多次build,一个project 可以有多个测试计划
             eg:32
             [{'api_key': '6476031051262d339d422d50a7e3183c61c02148e2c058573c23f1fb55e4a609', 'name': u'\u963f\u91cc\u4e
             91\u6d4b\u8bd5', 'notes': u'<p>\u963f\u91cc\u4e91\u6d4b\u8bd5\u8ba1\u5212</p>', 'is_open': '1', 'active':
             '1', 'is_public': '1', 'testproject_id': '5', 'id': '32'}]

buildname : 发布的一个版本名字
　　　　　　　eg:1.0
            [{'name': '1.0', 'notes': u'<p>\u963f\u91cc\u4e91\u6d4b\u8bd5\u7248\u672c1.0</p>\n', 'testplan_id': '32',
             'closed_on_date': '', 'release_date': '2019-01-15', 'is_open': '1', 'active': '1', 'creation_ts': '2019-01-
             15 08:47:54', 'id': '1'}, {'name': '2.01', 'notes': u'<p>\u7248\u672c2.01</p>\n', 'testplan_id': '32', 'cl
             osed_on_date': '', 'release_date': '2019-01-16', 'is_open': '1', 'active': '1', 'creation_ts': '2019-01-16
              03:56:29', 'id': '2'}]



status: 测试状态,返回给testlink的状态
        ｅｇ: p f

timestamp : 用例开始执的时间
            ｅｇ:"2019-01-18 14:55"

execduration: 测试用例持续的时间
            　ｅｇ: 2.5   (2.5min)



"""



import testlink

url = 'http://172.30.1.136:80/lib/api/xmlrpc/v1/xmlrpc.php'  # testlink服务器的api地址，只需要修改IP部分
key = '6c990989fd6fabbdcf386f59d87141b2'

tlc = testlink.TestlinkAPIClient(url, key)

def get_information_test_project(tlc):
    print("Number of Projects      in TestLink: %s " % tlc.countProjects())
    print("Number of Platforms  (in TestPlans): %s " % tlc.countPlatforms())
    print("Number of Builds                   : %s " % tlc.countBuilds())
    print("Number of TestPlans                : %s " % tlc.countTestPlans())
    print("Number of TestSuites               : %s " % tlc.countTestSuites())
    print("Number of TestCases (in TestSuites): %s " % tlc.countTestCasesTS())
    print("Number of TestCases (in TestPlans) : %s " % tlc.countTestCasesTP())
    tlc.listProjects()


get_information_test_project(tlc)


# 需要自动化创建一个测试计划


# 获取某个project　的测试ｐｌａｎ

project_id =5
project_name="SenseMedia-Ali"

# 必须有两个参数
aa=tlc.getTestPlanByName(project_name,"阿里云测试")

print "test planid is %s "% aa[0]["id"]
print "aa is %s" %aa


top_suites = tlc.getFirstLevelTestSuitesForTestProject(5)
for suite in top_suites:
    print suite["id"], suite["name"]
    if suite["name"] == u"性能测试":
        print("性能测试id is %s " % suite["id"])



# 获取testsuite 对应的attachments
# base64 解码content　并写入二进制文件
# 建议通过name 来获取这个７, 可能有多个附件
att=tlc.getTestSuiteAttachments(36)
print type(att)
with open("xxx.xlsx","wb") as f:
    f.write(base64.b64decode(att["7"]["content"]))


print("attachments is %s " % att)
print("len att is %s " % len(att))
print(att["7"].keys())
print(att.keys())



# 获取测试用例的关键字

per_case=tlc.getTestCasesForTestSuite("36",False,False)

print("per is %s "% per_case)

#通过遍历可以获取测试用例的id

print tlc.getTestCase("37")

print tlc.getTestCaseCustomFieldDesignValue("ALI-4",1,5,"concurrency","simple")
print tlc.getTestCaseCustomFieldDesignValue("ALI-4",1,5,"round","simple")




#buildname 意思就是几个版本
response = tlc.getBuildsForTestPlan(aa[0]["id"])


#

print response
build_name = response[0]['name']
print "build name is %s "% build_name




#通过附件进行参数化

# tlc.getTestSuiteAttachments()


#获取测试用例id
ids=tlc.getTestCasesForTestPlan(aa[0]["id"])

print("ids is %s "% ids)

#注意testcaseid　是内部定义的一个id ,可以通过导出ｘｍｌ 格式的用例看到
#<testcase internalid="14" name="RLJL-001">

# tlc.reportTCResult(testcaseid=14, testplanid=aa[0]["id"], buildname=build_name, status="f",notes='automation make its falut')
result=tlc.reportTCResult(testcaseexternalid="ALI-1", testplanid=aa[0]["id"], buildname=build_name, status="f",notes='i am test log 999 ',execduration=2.5,timestamp="2019-01-18 14:55")
print aa[0]["id"],build_name,
print type(aa[0]["id"]),type(build_name)

# 给某次测试上传附件
file_path="/images/images/2.jpg"
file_path2="/images/images/3.png"
file_path3="/codes/PerformanceTest/qps.xlsx"

file_path5="/tmp/a.txt"

tlc.uploadExecutionAttachment(file_path,result[0]["id"],"fujian","fujian description")
tlc.uploadExecutionAttachment(file_path2,result[0]["id"],"fujian2","fujian2 description")
tlc.uploadExecutionAttachment(file_path3,result[0]["id"],"fujian3","fujian3 description")
# 上传csv文件

# 上传txt文件

tlc.uploadExecutionAttachment(file_path5,result[0]["id"],"fujian５","fujian５ description")





print("haha result is %s " % result)

print("a is %s "% aa )


# 测试结果回传给测试计划下的测试id


#测试报告自动获取
#http://172.30.1.136/lnl.php?apikey=6476031051262d339d422d50a7e3183c61c02148e2c058573c23f1fb55e4a609&tproject_id=5&tplan_id=32&type=test_report
