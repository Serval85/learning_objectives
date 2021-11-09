# -*- coding: utf-8 -*-
# !/usr/bin/env python
import http.client


def api_get(method, uri):
    conn.request(method, uri)
    result = conn.getresponse()
    return result


conn = http.client.HTTPConnection('127.0.0.1', 10001)

res = api_get('GET', '/api/get')
print(res.status, res.read().decode())

res = api_get('GET', '/api/download')
print(res.status, res.read().decode())

res = api_get('DELETE', '/api/delete')
print(res.status, res.reason)
