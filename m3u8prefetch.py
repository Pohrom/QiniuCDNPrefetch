#coding=utf-8

import os
import sys
import qiniu
from qiniu.http import ResponseInfo
import m3u8
import json
import requests

accessKey = "<Your Access Key>"
secretKey = "<Your Secret Key>"

class QiNiuCDN(object):

    def __init__(self, auth):
        self.auth = auth
        self.USER_AGENT = 'QiniuPython'
        self.CONTENT_TYPE = 'application/json'
        self.headers = {'User-Agent': self.USER_AGENT,'Content-Type': self.CONTENT_TYPE}

    def __return_wrapper(self, resp):
        if resp.status_code != 200 or resp.headers.get('X-Reqid') is None:
            return None, ResponseInfo(resp)
        ret = resp.json() if resp.text != '' else {}
        return ret, ResponseInfo(resp)

    def __post(self, url, data):
        try:
            r = requests.post(url, data=data, auth=qiniu.auth.RequestsAuth(self.auth), 
            headers=self.headers, timeout=qiniu.config.get_default('connection_timeout'))
        except Exception as e:
            return None, ResponseInfo(None, e)
        return self.__return_wrapper(r)

    def prefetch(self, urls):
        url = 'http://fusion.qiniuapi.com/v2/tune/prefetch'
        ret, info = self.__post(url, json.dumps({"urls":urls}))
        return ret, info


def prefetch(urls):
    auth = qiniu.Auth(accessKey, secretKey)
    cdn = QiNiuCDN(auth)
    retData, respInfo = cdn.prefetch(urls)
    if respInfo.status_code == 200:
        return "Prefetch success!"
    elif respInfo.status_code == 400031:
        return "invalid url"
    elif respInfo.status_code == 400032:
        return "invalid host"
    elif respInfo.status_code == 400033:
        return "prefetch url limit error"
    elif respInfo.status_code == 400036:
        return "invalid request id"
    elif respInfo.status_code == 400037:
        return "url has existed"
    elif respInfo.status_code == 500000:
        return "internal error"
    else:
        return "Error: " + respInfo.error

def get_fileUrls_in_m3u8(filePath):
    f = open(filePath)
    f.read()

def main():
    files =  os.listdir('.\\m3u8files')
    paths = map(lambda x:'.\\m3u8files\\' + x,files)
    objs = map(lambda x:m3u8.load(x),paths)
    urls = map(lambda x:x.segments.uri,objs)
    fixed_urls = map(lambda x:map(lambda y:"http://qiniu.cdn.vekwu.com/" + y,x),urls)
    print "Result: " + prefetch(fixed_urls[0])

if __name__ == "__main__":
    main()