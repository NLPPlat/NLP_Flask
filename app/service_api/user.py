from flask import request, render_template, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt
from werkzeug.security import generate_password_hash, check_password_hash

from . import api
from app import jwt
from app.utils.permission_utils import *
from app.utils.response_code import *


# 注册
@api.route('/user', methods=["POST"])
def register():
    userinfo = request.json
    username = userinfo.get("username")
    user = User.objects(username=username)
    if not user:
        name = userinfo.get("name")
        introduction = userinfo.get("introduction")
        password = userinfo.get("password")
        password_hash = generate_password_hash(password)
        avatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
        user = User(username=username, name=name, introduction=introduction, password=password_hash,
                    avatar=avatar, status='正常')
        user.save()
        wallet = Wallet(username=username)
        wallet.save()
        return jsonify({"code": RET.OK, "message": "register_success"})
    else:
        return jsonify({"code": 400, "message": "user_already_exists"})


# 登录
@api.route('/token', methods=['POST'])
def login():
    userInfo = request.json
    username = userInfo.get('username')
    password = userInfo.get('password')
    user = User.objects(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(
            {"code": RET.OK, "message": "login_success", "data": {"token": access_token, "username": username}})
    else:
        return jsonify({"code": 400, "message": "login_fail"})


# 获取用户信息
@api.route('/user', methods=['GET'])
@jwt_required
def getInfo():
    user = User.objects(username=get_jwt_identity()).first()
    return jsonify({"code": RET.OK, "data": {
        "username": user.username,
        "roles": user.roles,
        "avatar": user.avatar
    }})


# 获取用户全部信息
@api.route('/user/infos', methods=['GET'])
@jwt_required
def getAllInfo():
    user = User.objects(username=get_jwt_identity()).first()
    return jsonify({"code": RET.OK, "data": {
        'username': user.username,
        'datetime': user.datetime,
        'name': user.name,
        'introduction': user.introduction,
        'email': user.email,
        'phone': user.phone
    }})


# 用户信息修改
@api.route('/user/infos', methods=['PATCH'])
@jwt_required
def modifyInfo():
    info = request.json
    username = info.get('username')
    realUsername = get_jwt_identity()
    if not userinfoWritePermission(username, realUsername):
        return noPeimissionReturn()
    user = User.objects(username=username).first()
    for key in info:
        if key != 'username' and key != 'password':
            user[key] = info.get(key)
    user.save()
    return {'code': RET.OK}


# 登出用户token集合
blacklist = set()
max_token_count = 50  # 暂设50


# 在一个受JWT保护的endpoint被访问时调用，检查token是否被撤回/加入黑名单
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    token = decrypted_token["jti"]
    return token in blacklist


# 检查登出用户token集合blacklist的大小，大于max_token_count则开始清除最早的token
def check_blacklist_size():
    if len(blacklist) > max_token_count:  # 暂设50
        print(blacklist.pop())


# 登出
@api.route('/token', methods=['DELETE'])
@jwt_required
def logout():
    token = get_raw_jwt()["jti"]
    blacklist.add(token)
    check_blacklist_size()
    return jsonify({'code': 200, 'message': 'logout_success'})
