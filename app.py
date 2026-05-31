from flask import Flask, request
from flask_cors import CORS
import hashlib
import re
import urllib.parse
from uuid import uuid4
from datetime import datetime
import requests
import json
import time

app = Flask(__name__)
CORS(app)

CACHE_TTL = 72000
cache_dict = {}
device_id = ""
SALTS = [
    {"alg":"md5","salt":"fyZ4+p77W1U4zcWBUwefAIFhFxvADWtT1wzolCxhg9q7etmGUjXr"},
    {"alg":"md5","salt":"uSUX02HYJ1IkyLdhINEFcCf7l2"},
    {"alg":"md5","salt":"iWt97bqD/qvjIaPXB2Ja5rsBWtQtBZZmaHH2rMR41"},
    {"alg":"md5","salt":"3binT1s/5a1pu3fGsN"},
    {"alg":"md5","salt":"8YCCU+AIr7pg+yd7CkQEY16lDMwi8Rh4WNp5"},
    {"alg":"md5","salt":"DYS3StqnAEKdGddRP8CJrxUSFh"},
    {"alg":"md5","salt":"crquW+4"},
    {"alg":"md5","salt":"ryKqvW9B9hly+JAymXCIfag5Z"},
    {"alg":"md5","salt":"Hr08T/NDTX1oSJfHk90c"},
    {"alg":"md5","salt":"i"}]

def device_id_generator() -> str:
    """
    Generate a random device id.
    """
    return str(uuid4()).replace("-", "")
def get_timestamp() -> str:
    return str(int(datetime.now().timestamp() * 1000))

def l(e):
    if re.search(r"[\u0080-\uFFFF]", e):
        e = urllib.parse.unquote(urllib.parse.quote(e, encoding="utf-8"))
    return e


def b(s: str) -> str:
    s = l(s)
    return hashlib.md5(s.encode()).hexdigest()

def calculate_captcha_sign(e: dict, n: str) -> str:
    try:
        result = {"salt": n}
        for item in e:
            result["salt"] = b(result["salt"] + item["salt"])
            # print(result)
        return result["salt"]
    except Exception as e:
        print("[calculateCaptchaSign:]", e)
        return str(e)

def captcha_sign(device_id: str, timestamp: str) ->str:
    g = "YUMx5nI8ZU8Ap8pm" + "undefined" + "drive.mypikpak.com" + device_id + timestamp
    return f"1.{calculate_captcha_sign(SALTS, g)}"

def init():
    url = "https://user.mypikpak.com/v1/shield/captcha/init"
    
    timestamp = get_timestamp()

    payload = {
        "client_id": "YUMx5nI8ZU8Ap8pm",
        "action": "POST:/config/v1/basic",
        "device_id": device_id,
        "meta": {
            "captcha_sign": captcha_sign(device_id, timestamp),
            "client_version": "undefined",
            "package_name": "drive.mypikpak.com",
            "user_id": "",
            "timestamp": timestamp
        }
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "user.mypikpak.com",
        "Origin": "https://mypikpak.com",
        "Referer": "https://mypikpak.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-client-id": "YUMx5nI8ZU8Ap8pm",
        "x-client-version": "1.0.0",
        "x-device-id": device_id,
        "x-device-model": "safari/605.1.15",
        "x-device-name": "PC-Safari",
        "x-device-sign": "wdi10." + device_id + "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "x-net-work-type": "NONE",
        "x-os-version": "MacIntel",
        "x-platform-version": "1",
        "x-protocol-version": "301",
        "x-provider-name": "NONE",
        "x-sdk-version": "8.1.4"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)
    captcha_token = json.loads(response.text)['captcha_token']
    return captcha_token


def share(share_id: str, pass_code: str, captcha_token: str):
    url = "https://api-drive.mypikpak.com/drive/v1/share"
    params= {
        "limit": 100,
        "thumbnail_size": "SIZE_LARGE",
        "order": 6,
        "folders_first": "true",
        "share_id": share_id,
        "pass_code": pass_code
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "api-drive.mypikpak.com",
        "Origin": "https://mypikpak.com",
        "Referer": "https://mypikpak.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-captcha-token": captcha_token,
        "x-client-id": "YUMx5nI8ZU8Ap8pm",
        "x-device-id": device_id,
        "x-user-id": ""
    }
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.text)
    data = json.loads(response.text)

    pass_code_token = data['pass_code_token']
    file_id = data['files'][0]['id']
    return {
        "file_id": file_id,
        "pass_code_token": pass_code_token
    }

def file_info(share_id: str, file_id: str, pass_code_token: str, captcha_token: str):
    url = "https://api-drive.mypikpak.com/drive/v1/share/file_info"
    params= {
        "share_id": share_id,
        "file_id": file_id,
        "pass_code_token": pass_code_token
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "api-drive.mypikpak.com",
        "Origin": "https://mypikpak.com",
        "Referer": "https://mypikpak.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "x-captcha-token": captcha_token,
        "x-client-id": "YUMx5nI8ZU8Ap8pm",
        "x-device-id": device_id,
        "x-user-id": ""
    }
    response = requests.request("GET", url, headers=headers, params=params)

    data = json.loads(response.text)
    link = data['file_info']['medias'][0]['link']['url']
    return link

# 示例：GET 接口，可自定义鉴权、参数、解析逻辑
@app.route('/get_stream', methods=['GET'])
def get_stream():
    # 1. 接收URL参数（示例：id、token 做鉴权/区分资源）
    share_id = request.args.get('share_id', '')
    pass_code = request.args.get('pass_code', '')

    # ========== 这里替换成你的逻辑：鉴权 + 获取真实流地址 ==========
    # 示例模拟真实链接，实际在此处写爬虫/接口请求、解密、鉴权逻辑
    if not share_id or not pass_code:
        return "参数缺失", 400
    if not device_id:
        device_id = device_id_generator()

    now = time.time()
    # 命中有效缓存，直接返回
    if share_id in cache_dict:
        cache_time, link = cache_dict[share_id]
        if now - cache_time < CACHE_TTL:
            return link
    captcha_token = init()

    file = share(share_id, pass_code, captcha_token)

    real_url = file_info(share_id, file['file_id'], file['pass_code_token'], captcha_token)
    cache_dict[share_id] = (now, real_url)
    return real_url
