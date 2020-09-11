from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from app import models



# 注册
@api.route('/user', methods=['POST'])
def register():
    return


# 登录
@api.route('/token', methods=['POST'])
def login():
    userInfo = request.json
    username = userInfo.get('username')
    password = userInfo.get('password')
    user = models.User.objects(username=username, password=password)
    if user:
        access_token = create_access_token(identity=username)
        return {'code': 200, 'data': {'token': access_token}}
    else:
        return {'code': 400, 'message': '用户名或密码错误！'}


# 获取用户信息
@api.route('/user', methods=['GET'])
@jwt_required
def getInfo():
    user = models.User.objects(username=get_jwt_identity()).first()
    return {'code': 200, 'data': {
        'datetime': user.datetime,
        'roles': user.roles,
        'introduction': user.introduction,
        'avatar': user.avatar,
        'name': user.name
    }}


# 登出
@api.route('/token', methods=['DELETE'])
def logout():
    return {'code': 200, 'data': 'success'}
