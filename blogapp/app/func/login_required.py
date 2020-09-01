from functools import wraps
from flask import session, jsonify, g
from ..models import User
from .. import db

# 自定义普通用户登录控制
def login_required(func):
    @wraps(func)  # 保留源信息，本质是endpoint装饰，否则修改函数名很危险
    def inner(*args, **kwargs):  # 接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
        user_id = session.get("user_id")
        username = session.get("username")
        session_data=[user_id,username]
        print(session_data)  # 表单接手网页中登录信息，存入到session中，判断用户是否登录
        if not user_id:
            return jsonify({"msg": "请登录"})
        
        return func(*args, **kwargs)  # 登录成功就执行传过来的函数
    return inner


# 自定义管理员控制
def admin_requir(func):
    @wraps(func)  # 保留源信息，本质是endpoint装饰，否则修改函数名很危险
    def inner(*args, **kwargs):  # 接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
        user_id = session.get("user_id")
        username = session.get("username")  # 表单接手网页中登录信息，存入到session中，判断用户是否登录
        if not user_id:
            return jsonify({"msg": "请登录"})
        try:
            user = db.session.query(User.level).filter_by(id=user_id).first()
        except:
            return jsonify({"msg": "数据库错误"})
        if user.level == 2:
            return func(*args, **kwargs)  # 登录成功就执行传过来的函数
        else:
            return jsonify({"msg": "非法访问，没有权限"})
    return inner

    # 自定义超级管理员控制


def super_requir(func):
    @wraps(func)  # 保留源信息，本质是endpoint装饰，否则修改函数名很危险
    def inner(*args, **kwargs):  # 接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
        user_id = session.get("user_id")
        username = session.get("username")  # 表单接手网页中登录信息，存入到session中，判断用户是否登录
        if not user_id:
            return jsonify({"msg": "请登录"})
        try:
            user = db.session.query(User.level).filter_by(id=user_id).first()
        except:
            return jsonify({"msg": "数据库错误"})
        if user.level == 3:
            return func(*args, **kwargs)  # 登录成功就执行传过来的函数
        else:
            return jsonify({"msg": "非法访问，没有权限"})
    return inner
