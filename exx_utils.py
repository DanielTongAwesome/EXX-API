# -*- coding:utf-8 -*-
'''
Created on 2018.4.26
Author: Daniel Tong, 
Content: exx API utils, including http_get_request, hmacSign,
         generateParam functions for exx.
'''
import time
import json
import ssl
import hashlib
import hmac
import urllib3
import urllib.parse
import six
import random
# for time managment process
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
# account information
from exx_account import APIKey, SecretKey

# two types of request url
tradeUrl = 'https://trade.exx.com'
API_URL = 'https://api.exxvip.com/data/v1/'

# disable the insesure warning, this method will close all the notice from the urlib3 package
urllib3.disable_warnings()

# ================================================================= #
#                          Baisc functions                          #
# ================================================================= #

def http_get_request(key):
    '''
    http_get_request: only used for the API_URL
    input: key --- martket related request
        e.g: markets, tickers, ticker, depth, trades

    output: market related json data
            e.g: markets, tickers, ticker, depth, trades

    rtn type ------------------- <class 'urllib3.response.HTTPResponse'>
    rtn.data type -------------- <class 'bytes'>
    rtn.data.decode('utf-8') --- <class 'str'>
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        # API_URL + key info url 'get' information from the url
        #print(API_URL+key)
        rtn = proxy_handler.request('GET',API_URL+key)
        print(type(rtn.data.decode('utf-8')))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        return rtn_json
    # error return
    except Exception as ex:
        print(ex)
        return ex


def hmacSign(param):
    '''
    hmacSign: generate the Sign
    input: param consists of two parts, 1. accesskey 2.current time
    output: signature, the result after hashlib encryption
    '''
    # check the format is str or not
    if isinstance(SecretKey, six.text_type):
        # encode -- 'utf-8'
        secretKey = SecretKey.encode(encoding='utf-8')
    # Parse URLs into components
    # urlencode method 
    # Returns: 'accesskey=administrator&nonce=time'
    param = urllib.parse.urlencode(param).encode('utf8')
    # encryption by using the hashlib.sha512
    sign = hmac.new(secretKey, param, hashlib.sha512).hexdigest()
    return sign


def generateParam(param):
    '''
    generateParam: generate the param by using the hmacSign
    input: param, based on the trade API requirments
    output: paramString
    '''
    params = {
        'accesskey':APIKey,
        'nonce':int(time.time())*1000
    }
    params.update(param)
    desparam= sorted(dict2list(params), key=lambda d:d[0], reverse = False)
    signature = hmacSign(desparam)
    params['signature']=signature
    paramString = urllib.parse.urlencode(params)
    return paramString


def dict2list(dic:dict):
    '''
    dict2list: generate list from the given dict
    input: dictnary
    output: [(key1, value1), (key2, value2), ....] --- type = list
    '''
    keys = dic.keys()
    vals = dic.values()
    lst = [(key, val) for key, val in zip(keys, vals)]
    return lst

# ================================================================= #
#                          Martket API                              #
# ================================================================= #

def getMarkets():
    '''
    getMarkets: acquire market info
    input: no input
    output: json format market info 
    '''
    return http_get_request('markets')

def getTickers():
    '''
    getTickers: acquire all tickers info
    input: no input
    output: json format tickers
    '''
    return http_get_request('tickers')

def getTicker(currency):
    '''
    getTicker: acquire ticker info
    input: currency
    e.g: 'ensa_eth'
    output: json format info of a currency
    '''
    param={
        'currency':currency
    }
    paramString = urllib.parse.urlencode(param)
    return http_get_request('ticker?'+str(paramString))

def getDepth(currency):
    '''
    getDepth: return martket trading depth
    input: currency
    e.g: 'ensa_eth'
    output: market depth in json format
    '''
    param={
        'currency':currency
    }
    paramString = urllib.parse.urlencode(param)
    return http_get_request('depth?'+str(paramString))

def getTrades(currency):
    '''
    getTrades: return trading info
    input: currency
    e.g: 'ensa_eth'
    output: return trade information
    '''
    param={
        'currency':currency
    }
    paramString = urllib.parse.urlencode(param)
    return http_get_request('trades?'+str(paramString))


# ================================================================= #
#                            Trade API                              #
# ================================================================= #

def getBalance(param={}):
    '''
    getBalance: return the account balance
    input: no input
    output: return the account balance
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/getBalance?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
    except Exception as ex:
        print(ex)

def withdraw(amount,currency,receiveAddr,safePwd):
    '''
    withdraw: withdraw from the account
    input: amount, currency, receiveAddr, safePwd
    output: return code
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        param={
            'currency' : currency,
            'safePwd' : safePwd,
            'receiveAddr':receiveAddr,
            'amount':amount
        }
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/withdraw?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
    except Exception as ex:
        print(ex)

def withdrawRecord(currency,pageIndex=1):
    '''
    withdrawRecord: return the withdraw record
    input: currency, pageIndex (assumption is 1)
    output: withdraw record
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        param={
            'pageIndex' : pageIndex,
            'currency':currency
        }
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/getWithdrawRecord?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
    except Exception as ex:
        print(ex)

def withdrawAddress(currency):
    '''
    withdrawAddress: return the withdraw address
    input: currency
    output: the address info
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        param={
            'currency':currency
        }
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/getWithdrawAddress?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
    except Exception as ex:
        print(ex)


def buyOrSell(currency, price, amount, type):
    '''
    buyOrSell: buy or sell
    input: currency, price, amount, type
           e.g: 'ensa_eth', price(str type), amount, type = 'sell' or 'buy'
    output: success or not, return status, 100 = success
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        param = {
            'currency': currency,
            'type': type,
            'amount': amount,
            'price': price
        }
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/order?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
        return rtn_json
    except Exception as ex:
        print(ex)

def cancelOrder(param):
    '''
    cancelOrder: cancel the order
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/cancel?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
        return rtn_json
    except Exception as ex:
        print(ex)

def getOrder(param):
    '''
    getOrder: acquire the current open order
    input: none
    return: current order
    '''
    try:
        proxy_handler= urllib3.PoolManager()
        paramString = generateParam(param)
        rtn = proxy_handler.request('GET',tradeUrl+'/api/getorder?'+str(paramString))
        rtn_json = json.loads(rtn.data.decode('utf-8'))
        print(rtn_json)
        return rtn_json
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    #test markets, tickers, ticker, depth, trades
    #print((getDepth('ensa_eth')))
    tickers = getTicker('ensa_eth')
    print (tickers)
    testdic = {'a':'abc', 'b':'cdef'}
    print (dict2list(testdic))
   