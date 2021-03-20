from flask import jsonify, request
from app.api import bluePrint
from app import db
from datetime import datetime
from app.models import User
import requests
from config import Config
from WXBizDataCrypt import WXBizDataCrypt


# -------------------Wechat APIs--------------------------------------------------------
@bluePrint.route('/wechat/login', methods=['POST'])
def wechat_login():
    """
    This api logins a user through wechatUtils.
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
    print(r.json()['session_key'])
    openid = r.json()['openid']
    session_key = r.json()['session_key']
    # First check if the openID already exist in the DB.
    already_existed = User.query.filter(User.deleted == False).filter(
        User.openID == openid).first()
    if already_existed:
        print(already_existed)
        already_existed.sessionKey = session_key
        db.session.add(already_existed)
        db.session.commit()
    else:
        user = User()
        user.openID = openid
        user.sessionKey = session_key
        db.session.add(user)
        db.session.commit()

    return jsonify(message=code), 201


# @bluePrint.route('\wechat\updateuserinfo', methods=['POST'])
# def wechat_update_userinfo():
#     """
#     This api receives the signature and raw data from the wechat applet.
#     And calculates the signature based on the session_key that is currently stored.
#     If the calculated signature is the same as the received signature, then the user info is correct and is stored.
#     Otherwise, an error message is sent to the wechat applet and the user info is not stored.
#     """
#     appId = Config.WECHAT_APPID
#     sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='
#     encryptedData = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
#     iv = 'r7BXXKkLb8qrSNn05n0qiA=='
#
#     pc = WXBizDataCrypt(appId, sessionKey)
#
#     print pc.decrypt(encryptedData, iv)