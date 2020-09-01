import re
import time
from flask import request, jsonify, session,g,current_app
from ..func.token_auth import auth as http_auth
from ..models import User,Article,Comment
from . import auth
from .. import db
from ..func.redis_conn import r_db

@auth.route("")
@http_auth.login_required
def test():
    # current_app.logger.info('auth')
    return "auth"


# @auth.route('/login', methods=["POST","GET"])
# @auth.before_request
# def login():
#     if request.method == 'POST':
#         # 接受的json数据格式 {"name":"","password":""}
#         user = request.get_json()
#         username = user.get('name')
#         password = user.get('password')
#         if not all([username, password]):
#             return jsonify({"code": 1001, "error": "参数不完整"})
#         user = User.query.filter_by(name=username).first()
#         try:
#             user = User.query.filter_by(name=username).first()
#         except:
#             return jsonify({"code": 5001, 'msg': '数据库错误'})
#         if not user:
#             return jsonify({"code": 1002, 'msg': '用户不存在'})
#         if user.verify_password(password)==False or user.name != username:
#             return jsonify({"code": 1003, "error": "用户名或密码错误"})
#         session['user_id']=user.id,
#         session['username']=user.name
#         print(session.get("user_id"))
#         g.user_id = user.id
#         g.username = user.name
#         print(g.user_id,g.username)
        
#         # login_user(user)
#         # g.user = user
#         # token = login_user(user.generate_confirmation_token())
#         # # 完成登录后将token存到缓存中并设置过期时间，后面校验时如果缓存中不存在，则报错
#         # life_time = current_app.config.get("PERMANENT_SESSION_LIFETIME")
#         # token = user.get_id(life_time)   # 这里调用get_id()产生token，Flask-Login的token也是调用get_id()产生的，从而保证的二者的一致。
#         # print("-------- login, token=", token)
#         # simple_cache.set(token, 1, life_time)  # 设置cache的失效时间，在login()就可以通过判断cache中是否存在token来知道是否超时了
    
#         return jsonify({'code': 200, 'msg': '用户登录成功'})

#注销用户
@auth.route('/logout')
@http_auth.login_required
def logout():
    expiration=0
    key=current_app.config['REDIS_PREFIX']+str(g.user_id)+'_'+str(g.uuid)
    token =r_db.expire(key, expiration) # 设置修改对应key的过期时间
    return jsonify({'code': 200, 'msg': '用户登出成功'})
   



@auth.route("/users/<int:id>/pwd", methods=["POST", "GET"])
@http_auth.login_required
def change_pwd(id):
    id = g.user_id
    if id == None:
        return 'MSG'
    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        new_pwd = request.form.get("new_pwd")
        new_pwd2 = request.form.get("new_pwd2")
        password = request.form.get("old_pwd")
        if user.password != password:
            return jsonify({"msg": "密码不一致"})
        if new_pwd != new_pwd2:
            return jsonify({"msg": "两次密码不一致"})
        print(new_pwd)
        user.password = new_pwd
        db.session.add(user)
        db.session.commit()
        return 'M'


# 邮箱注册
@auth.route("/register_email", methods=["POST"])
def register_by_email():
    # 接受的数据格式{"name":"",...}
    user_data = request.get_json()
    # print(user_data)
    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")
    password2 = user_data.get("password2")
    if not all([name, password, password2, email]):
        return jsonify({'code': 1001, "msg": "参数不完整"})
    elif not re.match("\w{6,18}", name):
        return jsonify({'code': 1003, "msg": "用户名输入不合法，请重新输入"})
    elif password != password2:
        return jsonify({'code': 1003, "msg": "两次密码不一致"})
    try:
        user = User.query.filter_by(name=name).first()
        # print(user.name,user.email)
    except:
        return jsonify({"code": 5001, 'msg': '数据库查询错误'})
    if user:
        return jsonify({"code": 1004, 'msg': '用户已存在'})
    try:
        user = User.query.filter_by(email=email).first()
    except:
         return jsonify({"code": 5001, 'msg': '数据库查询错误'})
    if user:
        return jsonify({"code": 1004, 'msg': "邮箱已注册"})
    try:
        user = User(name=name, password=password, email=email)
        db.session.add(user)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'code': 5001, 'msg': "数据库错误"})
    return jsonify({'code': 200, 'msg': "注册成功"})


# 手机注册
@auth.route("/register_phone", methods=["POST"])
def register_by_phone():
    if request.method == 'POST':
        # 接受的数据格式{"name":"",...}
        user_data = request.get_json()
        # print(user_data)
        name = user_data.get("name")
        phone = user_data.get("phone")
        password = user_data.get("password")
        password2 = user_data.get("password2")
        info = ""
        if not all([name, password, password2, phone]):
            return jsonify({'code': 1, "error": "参数不完整"})
        elif not re.match("\w{6,18}", name):
            return jsonify({'code': 1, "error": "用户名输入不合法，请重新输入"})
        elif password != password2:
            return jsonify({'code': 1, "error": "两次密码不一致"})
        try:
            user = User.query.filter_by(name=name).first()
        except:
            return jsonify({"code": 2, 'msg': '数据库查询错误'})
        if user:
            return jsonify({"code": 1, 'msg': '用户已存在'})
        try:
            user = User(name, password, phone)
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'code': 2, 'msg': "数据库错误"})
        return jsonify({'code': 0, 'msg': "注册成功"})



# 显示所有用户
@auth.route('/users')
def users():
    try:
        user = db.session.query(
            User.id, User.name, User.password, User.email, User.phone, User.addtime).all()
        print(user)
    except:
        return jsonify({'code': 2, 'msg': '数据库查询错误', })
    return jsonify({'code': 0, 'msg': 'ok', 'data': user})


# 显示单个用户，用户详情页
@auth.route('/users/<int:id>')
@http_auth.login_required
def user(id):
    if id != session["user_id"]:
        return jsonify({'msg': '不是自己的资料无法访问'})
    else:
        user = User.query.filter_by(id=id).first()
        article = db.session.query(Article.id, Article.title, Article.content, Article.addtime).filter(
            Article.user_id == id).all()
        comment = db.session.query(Comment.id, Comment.comment, Comment.addtime).filter(
            Comment.user_id == id).all()
        return jsonify({"msg": "查询数据成功", "user": user, "article": article, "comment": comment})


@auth.route("/changeimg", methods=["POST"])
@http_auth.login_required
def change_img():
    try:
        print(request.headers)
        img_file = request.files.get("formData") or request.files.get("imgfile")
        uid = request.form.get("uid")
        print(img_file)
        if not img_file:
            return jsonify({"msg":"上传图片失败,请重新上传","code":"401"})
        img_path = 'app\static\img\\'+str(int(time.time()))+".png"
        print(img_path)
        with open(img_path, "wb") as f:
            f.write(img_file.read())
        change_img = img_path.split("\\").pop()
        return jsonify({"code": 201, 'msg': "上传图片成功", "data":{"uid":'',"img":change_img}})
    except:
        return jsonify({"msg":"上传图片失败","code":"401"})


@auth.route("/test",methods=["POST"])
def test1():
    data=request.get_json()
    print(data)
    return jsonify({"code":200,"msg":"ok","data":data})