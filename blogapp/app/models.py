
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from .import db
import time

# 定义ORM
# 定义用户模型


class User(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(50), unique=True)  # 昵称
    password_hash = db.Column(db.String(128))  # 密码hash值
    email = db.Column(db.String(50), unique=True)  # 邮箱
    phone = db.Column(db.String(50), unique=True)  # 手机号码
    birth_date = db.Column(db.Date)  # 生日
    school = db.Column(db.String(50))  # 学校
    comp = db.Column(db.String(50))  # 公司
    info = db.Column(db.String(200))  # 个性简介
    level = db.Column(db.Integer, default=1)
    fav = db.Column(db.String(255))  # 头像
    addtime = db.Column(db.DateTime, index=True, default=time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))  # 注册时间
    # confirmed = db.Column(db.Boolean, default=False) #token检验状态
    # uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    # userlogs = db.relationship('Userlog', backref='user')  # 会员日志外键关系关联
    comments = db.relationship('Comment', backref='user')  # 评论外键关系关联
    articles = db.relationship('Article', backref='user')  # 电影收藏外键关系关联

    def __repr__(self):
        return "<User %r>" % self.name

    # 加载用户的回调函数  flask_login的设置
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(int(user_id))
    
    # def generate_confirmation_token(self, expiration=current_app.config["PERMANENT_SESSION_LIFETIME"]):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': self.id})
    # def confirm(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     return True

    #通过property装饰器把函数设置为属性
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 生成密码哈希值，保存到数据库password_hsah变量中
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码是否正确，返回True和False
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

 # 会员登录日志


class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员编号
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))  # 登录时间

    def __init__(self, ip):
        self.ip = ip

    def __repr__(self):
        return "<Userlog %r>" % self.id


# 文章
class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(100), unique=True)  # 标题
    content = db.Column(db.String(10000))  # 内容
    article_type = db.Column(db.String(50), default="web技术")  # 文章类型
    article_dianzan = db.Column(db.Integer, default=0)  # 点赞
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))  # 添加时间

    def __repr__(self):
        return "<Article %r>" % self.title

# 文章图片


class ArticleImg(db.Model):
    __tablename__ = "arc_img"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    img_path = db.Column(db.String(100), unique=True)  # 图片路径
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属文章
    addtime = db.Column(db.DateTime, index=True, default=time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))  # 添加时间

# 评论


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    comment = db.Column(db.String(1000))  # 内容
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())))  # 添加时间

    def __repr__(self):
        return "<Comment %r>" % self.id
