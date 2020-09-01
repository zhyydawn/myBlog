#coding:utf-8

from collections import namedtuple
from flask import current_app, g, request,jsonify
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer \
    as Serializer, BadSignature, SignatureExpired

from app.func.error_code import AuthFailed, Forbidden
from app.func.scope import is_in_scope
from app.func.redis_conn import r_db

auth = HTTPBasicAuth()
User = namedtuple('User', ['uid', 'uuid', 'scope'])


@auth.verify_password
def verify_password(token, password):
    # token
    token = request.headers.get("token")
    user_info = verify_auth_token(token)
    if not user_info:
        return False
    else:
        # request
        g.user_id = user_info.uid
        g.uuid=user_info.uuid
        return True


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except TypeError as e:
        current_app.logger.error(e)
        raise AuthFailed(msg='token is invalid',
                         error_code=1002)
    except BadSignature:
        current_app.logger.error(BadSignature)
        raise AuthFailed(msg='token is invalid',
                         error_code=1002)
    except SignatureExpired:
        current_app.logger.error(SignatureExpired)
        raise AuthFailed(msg='token is expired',
                         error_code=1003)
    uid = data['uid']
    uuid = data['uuid']
    scope = data['scope']
    # request 视图函数
    # allow = is_in_scope(scope, request.endpoint)
    # if not allow:
    #     raise Forbidden()
    key=current_app.config['REDIS_PREFIX']+str(uid)+'_'+str(uuid)
    if token!=r_db.get(key):
        raise AuthFailed(msg='token is invalid',
                         error_code=1002)
    return User(uid, uuid, scope)
