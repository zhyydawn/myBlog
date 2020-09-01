import re
from ronglian_sms_sdk import SmsSDK #导入云通讯
from flask import session,jsonify,g,request,current_app
from  ..models import User
from .. import db
from code import code
from ..func.redis_conn import r_db

#云通讯配置
accId = '容联云通讯分配的主账号ID'
accToken = '容联云通讯分配的主账号TOKEN'
appId = '容联云通讯分配的应用ID'
 
def send_message():
    sdk = SmsSDK(accId, accToken, appId)
    tid = '容联云通讯创建的模板ID'
    mobile = '手机号1,手机号2'
    datas = ('变量1', '变量2')
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)
    return resp

#获取手机验证码
@code.route("/sms_code", methods=["POST"])
def send_sms_code():
    json_data = request.get_json()
    phone = json_data.get("phone") #接受前端手机号
    image_code = json_data.get("image_code") #接受前端验证码
    image_code_id = json_data.get("image_code_id") #接受前端验证码id

    if not all([phone, image_code, image_code_id]):
        return jsonify(errno=1002, errmsg="参数不全")

    if not re.match("^1[35789][0-9]{9}$",phone):
        return jsonify(errno=1002, errmsg="手机号不正确")

    try:
        real_image_code = r_db.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=5001,errmsg="数据库查询错误")

    if not real_image_code:
        return jsonify(errno=5005,errmsg="验证码已经过期")

    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=1002,errmsg="验证码输入错误")
    try:
        user = User.query.filter_by(phone=phone).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=5001,errmsg="数据库查询错误")

    if user:
        return jsonify(errno=5001,errmsg="该手机号已经被注册")

    # 后端自己生成验证码
    # result = random.randint(0, 999999)
    # sms_code = "%06d" % result
    # print("短信验证码是：{}".format(sms_code))

    # 调用第三方去发送短信
    sms_code=send_message(1,phone,image_code_id)
    if sms_code != 0:
        return jsonify(errno=172001, errmsg="发送短信失败")

    try:
        #       key:手机号    value:验证码  有效期
        r_db.set("SMS_" + phone, sms_code, 300)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=5001, errmsg="手机验证码保存失败")

    return jsonify(errno=200, errmsg="发送成功")