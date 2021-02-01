from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.utils.permission_utils import *


# 用户获取
@api.route('/user/users', methods=['GET'])
@jwt_required
def usersFetch():
    # 读取基本数据
    info = request.values
    queryUserName = info.get('username')
    userStatusFilter = info.getlist('userStatus[]')
    sort = info.get('sort')
    username = get_jwt_identity()

    if not adminPermission(username):
        return noPeimissionReturn()

    # 设置查询条件Q
    q = Q(status__in=userStatusFilter)
    q = q & Q(roles=['editor'])
    if len(queryUserName) > 0:
        q = q & Q(username__icontains=queryUserName)

    # 数据库查询
    usersList = User.objects(q).order_by(sort)

    # 分页
    type = info.get('type')
    if type == 'part':
        limit = int(info.get('limit'))
        page = int(info.get('page'))
        front = limit * (page - 1)
        end = limit * page
        return {'code': RET.OK, 'data': {'total': usersList.count(), 'items': usersList[front:end]}}
    else:
        return {'code': RET.OK, 'data': {'total': usersList.count(), 'items': usersList}}
