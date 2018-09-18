#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for
import urllib.request
import json
import sys, os
import configparser
import requests

 
#BASE_URL = "http://sso.dev.u-tokyo.mintsys.jp:8050"
CONTENTS_DB = "page_contents.ini"

servers = None
UserList = {}
VersionList = {}
 
def dict_print2(elements, spc, debug=False):
    '''
    辞書を再帰的にたどって表示する。インデント幅はspcで文字で指定する。
    '''

    spc += "  "

    dictionary = ""
    inventory_id = None
    inventory_name = None
    for item in elements:
        if type(elements[item]) is dict:
            ret = dict_print(elements[item], spc, debug)
            for item in ret:
                dictionary += item

        elif type(elements[item]) is list:
            list_elements = elements[item]
            for list_item in list_elements:
                if type(list_item) is dict:
                    ret = dict_print(list_item, spc, debug)
                    for item in ret:
                        dictionary += item
                else:
                    if debug is True:
                        print("%s | %s"%(spc, list_item))
        else:

            if debug is True:
                print("%s | %20s : %s"%(spc, item, elements[item]))
            dictionary += "%s | %20s : %s"%(spc, item, elements[item])


    return dictionary

#値の検証とuidの取得
def validate(token):
    req = urllib.request.Request(
        url=BASE_URL + "/sso/json/sessions/" + token + "?_action=validate",
        headers={"Content-Type" : "application/json"},
        data="".encode()
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())
 
def getMaxIdle(token):
    '''
    MaxIdleの検証
    '''

    req = urllib.request.Request(
        url=BASE_URL + "/sso/json/sessions?_action=getMaxIdle&tokenId=" + token,
        headers={"Content-Type" : "application/json"},
        data="".encode()
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def sso_logout(token):
    '''
    logout処理
    '''

    req = urllib.request.Request(
        url=BASE_URL + "/sso/json/sessions/" + token + "?_action=logout",
        headers={"Content-Type" : "application/json"},
        data="".encode()
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def read_db():
    '''
    コンテンツDBの読み込み
    @retval DBのリスト
    '''

    parser = configparser.ConfigParser()

    inifilename = CONTENTS_DB
    if os.path.exists(inifilename) is True:
        parser.read(inifilename)

    global servers
    global UserList
    global VersionList
    if parser.has_section("Servers") is True:
        if parser.has_option("Servers", "servers") is True:
            servers = parser.get("Servers", "servers").split()

    for item in servers:
        print("server : %s"%item)
        if parser.has_section(item) is True:
            UserList[item] = {}
            VersionList[item] = {}
            usernames = userids = tokenlist = None
            if parser.has_option(item, "username") is True:
                usernames = parser.get(item, "username").split(",")
            if parser.has_option(item, "userid") is True:
                userids = parser.get(item, "userid").split()
            if parser.has_option(item, "token") is True:
                tokenlist = parser.get(item, "token").split()
            if usernames is not None and userids is not None and tokenlist is not None:
                for i in range(len(usernames)):
                    UserList[item][usernames[i]] = userids[i] + ":" + tokenlist[i]
            version = "3.0"
            if parser.has_option(item, "version") is True:
                version = parser.get(item, "version")
            VersionList[item]["version"] = version

    return servers, UserList, VersionList

def InventoryAPI(token, weburl, headers=None, method="get", invdata=None):
    '''
    Inventory Reference API Get method
    @param token(64character barer type token)
    @param weburl(URL for API access)
    @param invdata(body for access by json)
    @retval (json = dict) There is None if error has occured.
    '''

    # parameter
    if headers is None:
        headers = {'Content-Language':'ja'}
    #    headers = {'Authorization': 'Bearer ' + token,
    #               'Content-Type': 'application/json',
    #               'Accept': 'application/json'}

    # http request
    session = requests.Session()
    session.trust_env = False
    session.headers['Content-Language'] = 'ja'

    if method == "get":
        if headers is None:
            print("session.get(%s)"%weburl)
            res = session.get(weburl)
        else:
            res = session.get(weburl, json=invdata, headers=headers)
    elif method == "post":
        res = session.post(weburl, json=invdata, headers=headers)
    elif method == "delete":
        res = session.delete(weburl, json=invdata, headers=headers)
    #print res

    print('headers : ' + str(res.headers))
    print('headers : ' + str(headers))
    if str(res.status_code) != "200":
        print("error   : ")
        print('status  : ' + str(res.status_code))
        print('body    : ' + res.text)
        print('-------------------------------------------------------------------')
        print('url     : ' + weburl)
        return False, res.text

    return True, res

def dict_print(elements, spc, htmlspc, debug=False):
    '''
    \u8f9e\u66f8\u3092\u518d\u5e30\u7684\u306b\u8868\u793a\u3059\u308b
    '''

    spc += "　"
    htmlspc += "&nbsp;&nbsp;"

    dictionary = []
    inventory_id = None
    inventory_name = None
    for item in elements:
        if type(elements[item]) is dict:
            ret = dict_print(elements[item], spc, htmlspc, debug)
            print("%s%20s {"%(spc, item))
            dictionary.append("%s%20s {<BR>"%(htmlspc, item))
            for item in ret:
                dictionary.append(item)
            print("%s}"%(spc))
            dictionary.append("%s }<BR>"%(htmlspc, item))

        elif type(elements[item]) is list:
            list_elements = elements[item]
            print("%s%20s ["%(spc, item))
            dictionary.append("%s%20s [<BR>"%(htmlspc, item))
            for list_item in list_elements:
                if type(list_item) is dict:
                    ret = dict_print(list_item, spc, htmlspc, debug)
                    print("%s {"%spc)
                    dictionary.append("%s {<BR>"%htmlspc)
                    for item in ret:
                        dictionary.append(item)
                    print("%s}"%(spc))
                    dictionary.append("%s}<BR>"%(htmlspc))
                elif type(list_item) is list:
                    ret = dict_print(list_item, spc, htmlspc, debug)
                    print("%s%20s ["%(spc, item))
                    dictionary.append("%s%20s [<BR>"%(htmlspc, item))
                    for item in ret:
                        dictionary.append(item)
                    print("%s]"%(spc))
                    dictionary.append("%s]<BR>"%(htmlspc))
                else:
                    print("%s%s"%(spc, list_item))
                    dictionary.append("%s%s%s<BR>"%(spc, htmlspc, list_item))
                    if debug is True:
                        print("%s | %s"%(spc, list_item))
            print("%s]"%(spc))
            dictionary.append("%s]<BR>"%(htmlspc))
        else:

            if item == "preferred_name" or item == "software_tool_name":
                inventory_name = elements[item].split("@")[0]
            elif item == "descriptor_id":
                inventory_id = elements[item].split("/")[-1]
            elif item == "prediction_model_id":
                inventory_id = elements[item].split("/")[-1]
            elif item == "software_tool_id":
                inventory_id = elements[item].split("/")[-1]

            print("%s%20s : %s"%(spc, item, elements[item]))
            dictionary.append("%s%20s : %s<BR>"%(htmlspc, item, elements[item]))

    return dictionary

app = Flask(__name__)
 
# パラメータ
param_len = len(sys.argv)
#print("paramlen = %d / params = %s"%(param_len, sys.argv))

#if param_len == 3:
#    BASE_URL = sys.argv[1]
#    docserver = sys.argv[2]
#    print("set BASE_URL to %s"%BASE_URL)
#    print("set document server name to %s"%docserver)
#else:
#    print("not define BASE_URL for sso server or document server name. exit")
#    sys.exit(1)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
@app.route("/")
def index():

    servers, UserList, VersionList = read_db()
    return render_template('api-top.html', servers=servers, UserList=UserList)

    #return "提供できるページがありません role for workflow(%s)/role for inventory(%s)"%(role_wf, role_in)

@app.route("/gpdb-api-v1", methods=['GET', 'POST'])
def gpdb_api_v1():
    '''
    GPDB API V1
    '''

    server = endpoint_path = ""
    for item in request.form:
        print("key = %s / value = %s"%(item, request.form[item]))
        if item == "token":
            userid = request.form[item]
        elif item == "siteurl":
            server = request.form[item]
        elif item == "api-url":
            apiurl = request.form[item]
        elif item == "endpoint_path":
            endpoint_path = request.form[item]
    
    token = ""
    weburl = server + "/gpdb-api/v1/" + endpoint_path

    ret, res = InventoryAPI(token, weburl)

    result = "URL = %s<P>"%weburl
    result += "<HR>"
    if ret is True:
        result += res.text
    else:
        result += res

    return "%s"%result

@app.route("/gpdb-api-v2", methods=['GET', 'POST'])
def gpdb_api_v2():
    '''
    GPDB API V2
    '''

    server = endpoint_path = ""
    for item in request.form:
        print("key = %s / value = %s"%(item, request.form[item]))
        if item == "token":
            userid = request.form[item]
        elif item == "siteurl":
            server = request.form[item]
        elif item == "api-url":
            apiurl = request.form[item]
        elif item == "endpoint_path":
            endpoint_path = request.form[item]

    token = ""
    weburl = server + "/gpdb-api/v2/" + endpoint_path

    ret, res = InventoryAPI(token, weburl)

    if ret is True:
        if str(res.status_code) != "200":
            return("何かしらエラーが発生しました(status code = %s)"%res.status_code)
        else:
            print("successfully API access!")

    result = "URL = %s<P>"%weburl
    result += "<HR>"
    if ret is True:
        #result_list = dict_print(res.json(), "", "")
        #for item in result_list:
        #    result += item
        #result += "<HR>"
        #result += str(res.json())
        result += json.dumps(res.json(), ensure_ascii=False, indent=2).replace(" ", "&nbsp;").replace("\n", "<BR>")

    else:
        result += res

    return "%s"%result

@app.route("/inventory-api-ref", methods=['GET', 'POST'])
def inventory_api_ref():
    '''
    参照系API
    '''

    servers, UserList, VersionList = read_db()
    server = useid = apiurl = None
    for item in request.form:
        print("key = %s / value = %s"%(item, request.form[item]))
        if item == "token":
            userid = request.form[item]
        elif item == "siteurl":
            server = request.form[item]
        elif item == "api-url":
            apiurl = request.form[item]

    print("UserList = %s"%UserList)
    if (userid in UserList[server]) is False:
        return "指定されたサイト(%s)は指定されたユーザー(%s)を持っていません"%(server, userid)

    print("token = %s"%UserList[server][userid].split(":")[1])
    token = UserList[server][userid].split(":")[1]

    weburl = server + "/inventory-api/v3/" + apiurl
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    ret, res = InventoryAPI(token, weburl, headers)

    if ret is True:
        #res = res.json()
        #ret = dict_print(res, "")
        #result = "URL = %s<P>"%weburl
        #result += "userid = %s<P>"%userid
        #result += "token = %s<P>"%token
        #result += "<HR>"
        #result += json.dumps(res, indent=2)
        #result += "<HR>"
        #for item in ret:
        #    result += item + "<BR>"
        result += json.dumps(res.json(), ensure_ascii=False, indent=2).replace(" ", "&nbsp;").replace("\n", "<BR>")
    else:
        result = res

    return "%s"%result

@app.route("/inventory-api-upd", methods=['GET', 'POST'])
def inventory_api_upd():
    '''
    更新系API
    '''

    for item in request.form:
        print("key = %s / value = %s"%(item, request.form[item]))

    return "method %s"%request.method

app.debug = True
app.run(host='192.168.1.55')
