import requests


def request_wechat_access_token(wechat_appid, wechat_app_secret):
    """
    This function sends a GET request to wechat server with appid and app secret to get the access token.
    """
    wechat_access_token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    payload = {
        'grant_type':  'client_credential',
        'appid': wechat_appid,
        'secret': wechat_app_secret
    }
    r = requests.get(wechat_access_token_url, params=payload)

    return r.json()
