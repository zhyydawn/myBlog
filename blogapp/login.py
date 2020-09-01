#-*-coding:utf8;-*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, ValidationError
from flask import Flask,request,jsonify,render_template,redirect,url_for,flash,g,session
import re
import json
from functools import wraps
from datetime import datetime
import time
from flask_sqlalchemy import SQLAlchemy#pyhton3 必须用这种方式导入
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)


DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'test'
 
app.config['SQLALCHEMY_DATABASE_URI'] = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '123456'
app.config['JSON_AS_ASCII']=False

db = SQLAlchemy(app)



#创建表单

class RegistForm(FlaskForm):
    """会员注册表单"""
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={  # 附加选项
            "class": "form-control input-lg",
            "placeholder": "请输入昵称！",
            "autofocus": ""
            # "required": "required"  # 添加强制属性，H5会在前端验证
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
           # Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱！"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机号码！"),
            Regexp("^1[3|4|5|7|8][0-9]{9}$", message="手机号码格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机号码！"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )
    re_pwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请再次输入密码！"),
            EqualTo('pwd', message="两次密码输入不一致！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请再次输入密码！"
        }
    )
    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    # 昵称验证
    def validate_name(self, field):
        name = field.data
        if User.query.filter_by(name=name).count() == 1:
            raise ValidationError("昵称已经存在！")

    def validate_email(self, field):
        email = field.data
        if User.query.filter_by(email=email).count() == 1:
            raise ValidationError("邮箱已经存在！")

    def validate_phone(self, field):
        phone = field.data
        if User.query.filter_by(phone=phone).count() == 1:
            raise ValidationError("手机号码已经存在！")


class ArticleForm(FlaskForm):
    """发表文章表单"""
    title = StringField(
        label="标题",
        validators=[
            DataRequired("请输入标题！")
        ],
        description="文章标题")
    content = StringField(
        label="内容",
        validators=[
            DataRequired("请输入内容！")
            ],
        description="内容" )
   
    submit = SubmitField(
        '发表',
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    # 昵称验证
    def validate_name(self, field):
        name = field.data
        if User.query.filter_by(name=name).count() == 1:
            raise ValidationError("文章标题不能重复！")


#评论表单
class CommentsForm(FlaskForm):
    """评论表单"""
    comment = StringField(
        label="comment",
        validators=[DataRequired("评论:")]
        )
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    comment= StringField('comment',validators=[DataRequired()])
    submit = SubmitField('Submit')



# 定义ORM  
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(50), unique=True)  # 昵称
    password = db.Column(db.String(50))  # 密码
    email = db.Column(db.String(50), unique=True)  # 邮箱
    phone = db.Column(db.String(50), unique=True)  # 手机号码
    info = db.Column(db.String(200))  # 个性简介
    #fav = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 注册时间
    #uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    #userlogs = db.relationship('Userlog', backref='user')  # 会员日志外键关系关联
    comments = db.relationship('Comment', backref='user')  # 评论外键关系关联
    articles = db.relationship('Article', backref='user')  # 电影收藏外键关系关联
    
    def __init__(self, name,password,phone,email,info):
        self.name = name
        self.password = password
        self.email = email
        self.phone= phone
        self.info = info
        #self.addtime = addtime
    def __repr__(self):
        return "<User %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)  # 验证密码是否正确，返回True和False
  
 # 会员登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员编号
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __init__(self,ip):
        self.ip=ip
    def __repr__(self):
        return "<Userlog %r>" % self.id




# 文章
class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(100),unique=True)  # 内容
    content =db.Column(db.String(10000))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
  
    def __repr__(self):
        return "<Article %r>" % self.title
   
# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    comment = db.Column(db.String(1000))  # 内容
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    
       
    def __repr__(self):
        return "<Comment %r>" % self.id

#自定义登录控制 
def login_requir(func):
    @wraps(func)#保留源信息，本质是endpoint装饰，否则修改函数名很危险
    def inner(*args,**kwargs):#接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
        user_id=session.get("user_id")
        username=session.get("username")#表单接手网页中登录信息，存入到session中，判断用户是否登录
        if not user_id:
           return redirect('/login') #没有登录就跳转到登录路由下
        g.user_id=user_id
        g.username=username
        return func(*args,**kwargs)#登录成功就执行传过来的函数
    return inner

 
        
        
# 初始化创建表格、插入数据
@app.before_first_request
def create_db():
    pass
# Recreate database each time for demo
    # db.drop_all()
    # db.create_all()

    # admin = User('admin', "123456","121123456789",'admin@example.com',"None")
    # db.session.add(admin)
    # users = [User('guest1',"123456","18112345678",'guest1@example.com',"test user"),
    # User('guest2',"123456","13112341234",'guest2@example.com',"test user2")]
    # db.session.add_all(users)
    # db.session.commit()



 # code-- 0，成功-- 1,参数错误 -- 2，数据库错误--
'''
## 登录
# @app.route('/login',methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if not all([username,password]):
#             flash ('参数不完整')
#             return jsonify({"error":"参数不完整"})
#         user = User.query.filter_by(name=username).first()
#         if not user:
#             return "fail"
#         if user.password!=password or user.name!=username:
#             return jsonify({"error":"用户名或密码错误"})
#         session["user_id"]= user.id
#         session["username"]=user.name
#         #return "ok"
#         return redirect(url_for("get_articles"))
     
#     return render_template('login_1.html')
'''

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.get_json()
        #print(user)
        username=user.get('name')
        password=user.get('password') 
        if not all([username,password]):
            # flash ('参数不完整')
            return jsonify({"code":1,"error":"参数不完整"})
        try:
            user = User.query.filter_by(name=username).first()
            #print(user)
        except:
            return jsonify({"code":2,'msg':'数据库错误'})
        if not user:
            return jsonify({"code":1,'msg':'用户不存在'})
        if user.password!=password or user.name!=username:
            return jsonify({"code":1,"error":"用户名或密码错误"})
        session["user_id"]= user.id
        session["username"]=user.name
        return jsonify({'code':0,'msg':'ok'})
    
     
@app.route("/logout")
def logout():
    session["user_id"]=None
    return redirect(url_for("login"))
   
@app.route("/users/<int:id>/pwd",methods=["POST","GET"])
@login_requir
def change_pwd(id):
    id=g.user_id    
    if id==None:
        return redirect(url_for("login"))
    user=User.query.filter_by(id=id).first()
    if request.method=="POST":
        new_pwd=request.form.get("new_pwd")
        new_pwd2=request.form.get("new_pwd2")
        password=request.form.get("old_pwd")
        if user.password!=password:
            return jsonify({"msg":"密码不一致"})
        if new_pwd!=new_pwd2:
            return jsonify({"msg":"两次密码不一致"}) 
        print(new_pwd)
        user.password=new_pwd
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("changePwd.html",user=user)
  
'''
# 定义登录视图
@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()  # 导入登录表单
    if form.validate_on_submit():  # 验证是否有提交表单
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = data["name"]
        session["user_id"] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("home.user"))
    return render_template("home/login.html", form=form)

'''

# #注册
# @app.route("/register",methods=["POST","GET"])
# def register():
#     if request.method=='POST':
#         name=request.form.get("username")
#         phone=request.form.get("phone")
#         email=request.form.get("email")
#         password=request.form.get("password")
#         password2=request.form.get("password2")
#         info=""
    
#         if not all([name,password,password2,phone,email]):
#             flash("参数不完整")
#             return jsonify({"error":"参数不完整"})
#         elif not re.match("\w{6,18}",name):
#             return jsonify({"error":"用户名输入不合法，请重新输入"})
#         elif password!=password2:
#             flash("密码不一致")
#             return jsonify({"error":"两次密码不一致"})
#         user = User(name,password,phone,email,info)
#         db.session.add(user)
#         db.session.commit()
    
#         #return jsonify({"ok":"注册成功"}) 
#         return redirect(url_for("login")) 
#     return render_template("register_1.html")

#注册
@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=='POST':
        user_data=request.get_json()
        print(user_data)
        name=user_data.get("name")
        phone=user_data.get("phone")
        email=user_data.get("email")
        password=user_data.get("password")
        password2=user_data.get("password2")
        info=""    
        if not all([name,password,password2,phone,email]):
            return jsonify({'code':1,"error":"参数不完整"})
        elif not re.match("\w{6,18}",name):
            return jsonify({'code':1,"error":"用户名输入不合法，请重新输入"})
        elif password!=password2:
            return jsonify({'code':1,"error":"两次密码不一致"})
        try:
            user = User.query.filter_by(name=name).first()
        except:
            return jsonify({"code":2,'msg':'数据库查询错误'})
        if user:
             return jsonify({"code":1,'msg':'用户已存在'})
        try:
            user = User(name,password,phone,email,info)
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'code':2,'msg':"数据库错误"})
        return jsonify({'code':0,'msg':"注册成功"})
    
@app.route("/base",methods=["POST","GET"])
def base():
    user_id=session.get("user_id",default=0)
    if user_id==0:
        render_template("default.html")
    return render_template("base.html",user_id=user_id)
    
#显示所有用户
@app.route('/users')
def users():
    try:
        user=db.session.query(User.id,User.name,User.password,User.email,User.phone).all()
        print(user)
        # user = db.session.query(User.id,User.name,User.password,User.email,User.phone,User.addtime).first()
        # print(dict(user))
        # users={'id':{0},'name': {1},'password':{2},'email':{3},'phone':{4},'addtime':{5}}.format(user.id,user.name,user.password, user.email,user.phone,user.addtime)
        # print(users)
    except:
        return jsonify({'code':2,'msg':'数据库查询错误',})
    return jsonify({'code':0,'msg':'ok','data':user})


# 显示单个用户，用户详情页
@app.route('/users/<int:id>')
@login_requir
def user(id):
    if id==None:
        return render_template(url_for("login"))
        
    if id==g.user_id:
        user = User.query.filter_by(id=id).first()
        article=db.session.query(Article.id,Article.title,Article.content,Article.addtime).filter(Article.user_id==id).all()
        comment=db.session.query(Comment.id,Comment.comment,Comment.addtime).filter(Comment.user_id==id).all()
        #return "{0}: {1}".format(user.name, user.email)
    else:
        return render_template("login.html")
    return render_template("user.html",user=user,article=article,comment=comment)

#显示所有文章，文章主页        
@app.route('/articles',methods=["GET","POST"])
def get_articles():
    user_id=session.get("user_id")
    arc_data = db.session.query(Article.id,Article.title,Article.content,Article.addtime,User.name).join(User).all()
    return render_template("index.html",arc_data=arc_data,user_id=user_id)
    
# 文章详情页   
@app.route("/articles/<int:id>",methods=["POST","GET"])
def show_article(id):
    form=CommentsForm()
    
    article_id=id
    article=Article.query.filter_by(id=id).first()
    # return jsonify({"code":"400","msg":"保存失败"})
    comments=Comment.query.filter_by(article_id=id).all()
    comments=[(comm.id,comm.user_id,comm.comment,comm.addtime) for comm in comments]
    if request.method =="POST":
         if session.get("user_id") is None:
             return redirect(url_for("login"))
    #if form.validate_on_submit():
         comment=form.data.get("comment")
         print(comment)
         com=Comment(
         	comment=comment,
         	user_id=session.get("user_id"),
         	article_id=article_id,
         addtime=datetime.now())
        	#time.strftime('%Y-%m-%d %H:%M:%S' , time.localtime(time.time())))    
         try:
             db.session.add(com)
             db.session.commit()
           # return jsonify({"cod":200,"msg":"保存成功"}) 
         except:
             db.session.rollback()
         print(com)
         return redirect(url_for("show_article",id=id))
    #测试
    #a=article
    #return "{0}: {1},{2},{3},".format(a.id,a.title,a.content,a.addtime)
    
    return render_template("articleInfo.html",article=article,comments=comments,form=form,username="")
    
    
# 显示当前用户发表的所有文章
@app.route("/users/<user_id>/articles",methods=["GET","POST"])
@login_requir
def write_article(user_id):
    #user_id=g.user_id
    if not user_id:
        return render_template(url_for("login"))
    username=User.query.filter_by(id=user_id).first()
    if request.method =="POST":
        title=request.form.get("title")
        content=request.form.get("content")
        #print(title,content)
        
        #c_time=time.strftime('%Y-%m-%d %H:%M:%S' , time.localtime(time.time()))
        article=Article(
        	user_id=user_id,
        	title=title,
        	content=content,
        addtime=datetime.now())
        db.session.add(article)
        db.session.commit()
 
    articles=Article.query.filter_by(user_id=user_id).all()
    #print(type(articles))
    articles=[(arc.id,arc.title,arc.content,arc.addtime) for arc in articles]
    return render_template("article.html",username=username,articles=articles)

      
 #显示当前用户发表文章详情   
@app.route("/users/articles/<int:id>",methods=["POST","GET"])
@login_requir
def show__user_article(id):
    user_id=g.user_id
    article=Article.query.filter_by(id=id,user_id=user_id).first() 
    
    #测试
    #a=article
    #return "{0}: {1},{2},{3},".format(a.id,a.title,a.content,a.addtime)
    
    return render_template("userArticle.html",article=article)
    
      
#发表评论    
@app.route("/users/<int:user_id>/comments",methods=["GET"])   
@login_requir 
def show_comment(user_id):
    user_id=g.user_id
    user=User.query.filter_by(id=user_id).first()
    comments=Comment.query.filter_by(user_id=user_id).all()
    comments=[(comm.id,comm.article_id,comm.comment,comm.addtime) for comm in comments]
    return render_template("userComment.html",username=user.name,comments=comments)
    

@app.route("/comments",methods=["GET"]) 
def show_comments():
    #user_id=g.user_id
    #username=User.query.filter_by(id=user_id).first()
    # return jsonify({"code":"400","msg":"保存失败"})
    comments=Comment.query.all()
    comments=[(comm.id,comm.comment,comm.addtime) for comm in comments]
    return render_template("comment.html",username="",comments=comments)
 
 
 
 
@app.route("/tests",methods=["GET"]) 
@login_requir
def tests():
    article_id=8
    user_id=g.user_id
    comment_id=1
    u=User.query.filter_by(id=user_id).first()
    a=Article.query.filter_by(id=article_id).first()
    c=Comment.query.filter_by(id=comment_id).first()
    s=User.query.join(Article).filter(Article.id==article_id).first()
    return {"t":[{u.id:u.name},{a.id:a.title},{c.id:c.comment},s.name]}
    
  
  
@app.route("/json")
def test():
    datas=request.data
    print(datas)
    data=db.session.query(User.id,User.name,User.email,Article.id,Article.title,Article.content,Article.addtime).join(Article).filter(User.id==Article.user_id).all()
    return render_template("vuepost.html",data=datas)  



  
@app.route("/test")
def test1():
    return render_template("login_register.html")
  
@app.route("/")
def indextst():
    return '''
    <h1>博客系统开发<h1>
    '''
    
    
if __name__=="__main__":
    app.run(debug=True)
