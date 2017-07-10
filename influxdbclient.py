# -*- coding:utf-8 -*-
"""
author:jiangxf
description:实现influx客户端


with InfluxDBClient("http://localhost:8086") as client:
    params={"db":"testdb","rp":"counters","precision":"m"}
    for item in souredata:
        i += 1
        if lastid<item[0]:
            lastid=item[0]
        lines +="%s.%s,service=%s,machine=%s,object=%s,instance=%s value=%i %s\n" % item[2].lower(),client.escape_tag(item[5]),item[1],item[3].upper(),client.escape_tag(item[4]),client.escape_tag(item[6]),item[7],client.convert_timestamp(item[8],'m')
        if i>1000:
            client.write(params,lines)
            #print lines
            lines=""
            i=0
    if len(lines)>2:
        client.write(params,lines)
        #print lines
        lines=""
    print 'ok'
"""
import time
import requests
from six import binary_type

class InfluxDBClientError(Exception):
    """Raised when an error occurs in the request."""

    def __init__(self, content, code=None):
        """Initialize the InfluxDBClientError handler."""
        if isinstance(content, type(b'')):
            content = content.decode('UTF-8', 'replace')

        if code is not None:
            message = "%s: %s" % (code, content)
        else:
            message = content

        super(InfluxDBClientError, self).__init__(
            message
        )
        self.content = content
        self.code = code


class InfluxDBServerError(Exception):
    """Raised when a server error occurs."""

    def __init__(self, content):
        """Initialize the InfluxDBServerError handler."""
        super(InfluxDBServerError, self).__init__(content)

class InfluxDBClient(object):
    def __init__(self,baseurl,username=None,password=None,retries=3,timeout=None):
        self.baseurl=baseurl
        self.session=requests.Session()
        self.retries=retries
        self.timeout=timeout
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        self.username=username
        self.password=password

    def request(self,url,method,params,data,headers,expected_response_code):
        url = "{0}/{1}".format(self.baseurl, url)
        # Try to send the request more than once by default (see #103)
        retry = True
        _try = 0
        while retry:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    auth=(self.username, self.password),
                    params=params,
                    data=data,
                    headers=headers,
                    timeout=self.timeout
                )
                break
            except requests.exceptions.ConnectionError:
                _try += 1
                if self.retries != 0:
                    retry = _try < self.retries

        else:
            raise requests.exceptions.ConnectionError

        if 500 <= response.status_code < 600:
            raise InfluxDBServerError(response.content)
        elif response.status_code == expected_response_code:
            return response
        else:
            raise InfluxDBClientError(response.content, response.status_code)

    def close(self):
        """Close http session."""
        if isinstance(self.session, requests.Session):
            self.session.close()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

    def query(self,query,params=None):
        if params is None:
            params={}
        params['q']=query
        return self.request("query",'GET',params,None,self.headers,200)
    def write(self,params,linedata):
        headers = self.headers
        headers['Content-type'] = 'application/octet-stream'
        linedata=linedata.encode('utf-8')
        self.request("write",'POST',params,linedata,headers,204)
        return True

    def convert_timestamp(self,dt, precision='s'):
        #in windows
        s=int(time.mktime(dt.timetuple()))
        #s=int(timegm(dt.utctimetuple())-28800)
        if precision == 's':
            return s
        elif precision == 'm':
            return s / 60
        elif precision == 'h':
            return s / 3600
        raise ValueError(dt)
    def get_unicode(self,data, force=False):
        """
        Try to return a text aka unicode object from the given data.
        """
        if isinstance(data, binary_type):
            return data.decode('utf-8')
        elif data is None:
            return ''
        elif force:
            return str(data)
        else:
            return data
    def escape_tag(self,value):
        try:
            mvalue=self.get_unicode(value)
            return mvalue.replace(" ","_")
        except Exception,ex:
            print ex,repr(value)
        return ""
