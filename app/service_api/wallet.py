from flask import request, render_template, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt
from werkzeug.security import generate_password_hash, check_password_hash

from . import api
from app import jwt
from app.utils.permission_utils import *
from app.utils.response_code import *


# 获取某个人余额
@api.route('/wallet/users/ID/money', methods=["GET"])
@jwt_required
def getMoney():
    # 读取基本数据
    info = request.values
    username = info.get('username')
    print(username)
    realUsername = get_jwt_identity()
    if not userinfoWritePermission(username, realUsername):
        return noPeimissionReturn()

    # 数据库查询
    wallet = Wallet.objects(username=username).first()
    return {'code': RET.OK, 'data': {'money': wallet.money}}
