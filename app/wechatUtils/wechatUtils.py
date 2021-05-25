import requests
from config import Config

def get_wechat_access_token():
    wechat_access_token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    payload = {
        'grant_type':  'client_credential',
        'appid': Config.WECHAT_APPID,
        'secret': Config.WECHAT_APP_SECRET
    }
    r = requests.get(wechat_access_token_url, params=payload)

    return r.json()