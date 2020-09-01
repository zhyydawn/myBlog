import re
import time
from redis import StrictRedis
from flask import current_app, request, jsonify, session,g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, \
    BadSignature
from ..models import User
from . import auth
from .. import db
from ..func.redis_conn import r_db

            
@auth.route('/get_token', methods=['POST'])
def get_token():
    # 获取用户登录信息,生产token令牌
    user_data =request.get_json()
    username=user_data.get("name")
    password=user_data.get("password")
    uuid=user_data.get("uuid")
    if not all([username, password]):
        return jsonify({"code": 1001, "error": "参数不完整"})
    user = User.query.filter_by(name=username).first()
    try:
        user = User.query.filter_by(name=username).first()
    except:
        return jsonify({"code": 5001, 'msg': '数据库错误'})
    if not user:
        return jsonify({"code": 1002, 'msg': '用户不存在'})
    if user.verify_password(password)==False or user.name != username:
        return jsonify({"code": 1003, "error": "用户名或密码错误"})
    # Token
    expiration = current_app.config['TOKEN_EXPIRATION']
    token = generate_auth_token(user.id,uuid,None,expiration)
    t = {
        'token': token.decode('ascii')
    }
    name=current_app.config["REDIS_PREFIX"]+str(user.id)+"_"+str(uuid)
    r_db.setex(name=name,value=token,time = expiration)
    return jsonify(code=200,msg="获取token成功",t=t)


@auth.route('/secret', methods=['POST'])
def get_token_info():
    """获取令牌信息"""
    token=request.headers.get("token")
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, return_header=True)
    except SignatureExpired:
        return jsonify(msg='token is expired', error_code=1003)
    except BadSignature:
        return jsonify(msg='token is invalid', error_code=1002)

    r = {
        'scope': data[0]['scope'],
        'create_at': data[1]['iat'],
        'expire_in': data[1]['exp'],
        'uid': data[0]['uid'],
        'uuid':data[0]['uuid']
    }
    return jsonify(r)


def generate_auth_token(uid, uuid, scope=None,
                        expiration=7200):
    """生成令牌"""
    s = Serializer(current_app.config['SECRET_KEY'],
                   expires_in=expiration)
    return s.dumps({
        'uid': uid,
        'uuid': uuid,
        'scope':scope
    })
