
# Wechat Class
class wechat:
    def __new__()


@bluePrint.route('/wechat/login', methods=['POST'])
def wechat_login():
    """
    This api logins a user through wechat.
    """
    code = request.json['code']

    wechat_code2session_url = 'https://api.weixin.qq.com/sns/jscode2session'
    payload = {
        'appid': Config.WECHAT_APPID,
        'secret': Config.WECHAT_APP_SECRET,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(wechat_code2session_url, params=payload)
    print(r.url)
    print(r.json())
    print('now text')
    print(r.text)

    return jsonify(message=code), 201