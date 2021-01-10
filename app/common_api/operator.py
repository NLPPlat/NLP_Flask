from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.operator import *
from app.models.user import *
from app.utils.response_code import *


# 算子列表获取
@api.route('/operator/operators', methods=['GET'])
@jwt_required
def operatorsFetch():
    # 读取基本数据
    info = request.values
    queryOperatorName = info.get('operatorName')
    usernameFilter = info.getlist('username[]')
    operatorTypeFilter = info.getlist('operatorType[]')
    sort = info.get('sort')
    username = get_jwt_identity()


    # 获得用户信息
    user = User.objects(username=username).first()
    roles = user.roles

    # 设置查询条件Q
    q = Q(operatorType__in=operatorTypeFilter)
    if len(queryOperatorName) > 0:
        q = q & Q(taskName__icontains=queryOperatorName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        if 'admin' in roles:
            pass
        else:
            q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        if 'admin' in roles:
            q = q & Q(username__ne=username)
        else:
            q = q & (Q(username__ne=username) & Q(publicity='公开'))

    # 数据库查询
    operatorsList = Operator.objects(q).order_by(sort)

    # 分页
    type = info.get('type')
    if type == 'part':
        limit = int(info.get('limit'))
        page = int(info.get('page'))
        front = limit * (page - 1)
        end = limit * page
        return {'code': RET.OK, 'data': {'total': operatorsList.count(), 'items': operatorsList[front:end]}}
    else:
        return {'code': RET.OK, 'data': {'total': operatorsList.count(), 'items': operatorsList}}
