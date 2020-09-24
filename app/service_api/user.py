from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from . import api
from app import models,jwt
# from manage import jwt


# 注册
@api.route('/user', methods=["POST"])
def register():
    userinfo = request.json
    username = userinfo.get("username")
    user = models.User.objects(username=username)
    if not user:
        name = userinfo.get("name")
        introduction = userinfo.get("introduction")
        password = userinfo.get("password")
        password_hash = generate_password_hash(password)
        user = models.User(username=username, name=name, introduction=introduction, password=password_hash)
        user.save()
        return jsonify({"code": 200, "message": "register_success"})
    else:
        return jsonify({"code": 400, "message": "user_already_exists"})


# 登录
@api.route('/token', methods=['POST'])
def login():
    userInfo = request.json
    username = userInfo.get('username')
    password = userInfo.get('password')
    user = models.User.objects(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"code": 200, "message": "login_success", "data": {"token": access_token}})
    else:
        return jsonify({"code": 400, "message": "login_fail"})


# 获取用户信息
@api.route('/user', methods=['GET'])
@jwt_required
def getInfo():
    user = models.User.objects(username=get_jwt_identity()).first()
    return jsonify({"code": 200, "data": {
        "datetime": user.datetime,
        "roles": user.roles,
        "introduction": user.introduction,
        "avatar": user.avatar,
        "name": user.name
    }})


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
        blacklist.pop()


# 登出
@api.route('/token', methods=['DELETE'])
@jwt_required
def logout():
    token = get_raw_jwt()["jti"]
    blacklist.add(token)
    check_blacklist_size()
    return jsonify({'code': 200, 'message': 'logout_success'})

