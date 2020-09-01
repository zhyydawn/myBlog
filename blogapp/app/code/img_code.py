# import time
from flask import Flask,jsonify,current_app,request, make_response
from ..func.captcha import Captcha
from io import BytesIO
from . import code
from ..func.redis_conn import r_db



# @code.router("/get_img_code")
# def get_img_code(img_code_id):
#     """
#     获取图片验证码
#     ：params img_code_id: 图片验证码编号
#     ：return: 验证码图片
#     """
#     #获取前端数据
#     #生产图片验证码
#     #保存图片验证码到redis
#     #发送验证码给前端
    

@code.route('/')
def index():
    return 'common index'


@code.route('/get_img_code')
def graph_captcha():
    img_code_id=request.args.get("img_code_id")
    if not img_code_id:
        return jsonify(code=1002,msg='参数不合法')
    text, image = Captcha.gene_graph_captcha()
    try:
        r_db.setex(img_code_id,300,text)
    except Exception  as e:
        current_app.logger.error(e)
        return jsonify(code=5001,msg='数据库错误')   
        
    # out = BytesIO()
    # image.save(out, 'png')
    # out.seek(0)
    # resp = make_response(out.read())
    # resp.content_type = 'image/png'
    # return resp 
    code_img=image.save('app\static\code_img\\'+str(img_code_id)+'.png')
    code_img_path='app\static\code_img\\'+str(img_code_id)+'.png'
    return jsonify(code=200,msg="获取图片验证码成功",code_img=code_img_path)