#导入flask 项目需要的库
import os,time,logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config  import config

#日志配置
# log_path是存放日志的路径
cur_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(os.path.dirname(cur_path), 'logs')
# 如果不存在这个logs文件夹，就自动创建一个
if not os.path.exists(log_path): os.mkdir(log_path)
logname = os.path.join(log_path, '%s.log'%time.strftime('%Y_%m_%d'))
# 默认日志等级的设置
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器，指明日志保存路径,每个日志的大小，保存日志的上限
file_log_handler = RotatingFileHandler(logname, maxBytes=1024 * 1024, backupCount=10)
# 设置日志的格式                   发生时间    日志等级     日志信息文件名      函数名          行数        日志信息
formatter = logging.Formatter('%(asctime)s--%(levelname)s--%(filename)s[lines:%(lineno)s]--%(funcName)s--%(message)s')
# 将日志记录器指定日志的格式
file_log_handler.setFormatter(formatter)


# 实例化数据库
db = SQLAlchemy()

# 工厂函数创建flask实例化对象
def create_app(even):
    #实例化flask对象
    app=Flask(__name__)

    #日志配置
    app.logger.addHandler(file_log_handler)

    #实例化配置文件
    app.config.from_object(config["default"])
    config["default"].init_app(app)
    
    #配置cors跨域请求伪造请求信息
    CORS(app, supports_credentials=True)
    
    #实例化数据库
    db.init_app(app)
    

    #注册主模块蓝图
    from .main import main as main_Blueprint
    app.register_blueprint(main_Blueprint,url_prefix="/main")

    #注册用户认证模块蓝图
    from .auth import auth as auth_Blueprint
    app.register_blueprint(auth_Blueprint,url_prefix="/auth")
    
    #注册验证码获取模块蓝图
    from .code import code as code_Blueprint
    app.register_blueprint(code_Blueprint,url_prefix="/code")

    return app
    