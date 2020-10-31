from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.operator import *
from app.utils.response_code import *
from app.utils.codehub_utils import *


# 算子列表获取
@api.route('/operator/operators', methods=['GET'])
@jwt_required
def operatorsFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    queryOperatorName = info.get('operatorName')
    username = get_jwt_identity()

    # 读取过滤器、设置查询项
    usernameFilter = info.getlist('username[]')
    operatorTypeFilter = info.getlist('operatorType[]')
    sort = info.get('sort')

    # 设置查询条件Q
    q = Q(operatorType__in=operatorTypeFilter)
    if len(queryOperatorName) > 0:
        q = q & Q(taskName__icontains=queryOperatorName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))

    # 数据库查询
    operatorsList = Operator.objects(q).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': operatorsList.count(), 'items': operatorsList[front:end]}}


# 算子保存
@api.route('/operator/operators/ID', methods=['POST'])
@jwt_required
def operatorUpload():
    # 读取基本数据
    info = request.json
    code = info.get('code')
    publicity = info.get('publicity')
    operatorID = info.get('operatorid')
    operatorType = info.get('operatorType')
    operatorName = info.get('operatorName')
    username = get_jwt_identity()

    if (int(operatorID) == -1):
        operator = Operator(operatorType=operatorType, operatorName=operatorName, username=username,
                            publicity=publicity, code=code)
        operator.save()
    else:
        operatorQuery = Operator.objects(id=int(operatorID)).first()
        if operatorQuery and username == operatorQuery.username:
            operatorQuery.operatorType = operatorType
            operatorQuery.operatorName = operatorName
            operatorQuery.publicity = publicity
            operatorQuery.code = code
            operatorQuery.save()
    return {'code': RET.OK}


# 算子获取
@api.route('/operator/operators/ID', methods=['GET'])
@jwt_required
def operatorFetch():
    # 读取基本数据
    info = request.values
    operatorID = info.get('operatorid')
    username = get_jwt_identity()

    # 数据库读取
    operatorQuery = Operator.objects(id=int(operatorID)).first()
    if operatorQuery and username == operatorQuery.username:
        data = operatorQuery
    return {'code': RET.OK, 'data': data}


# 算子调试
@api.route('/operator/operators/ID/code', methods=['GET'])
@jwt_required
def codeRun():
    # 读取基本数据
    info = request.values
    code = info.get('code')
    datasetID = info.get('datasetid')

    # 运行代码
    result = operatorRunUtil(code, datasetID)
    return {'code': RET.OK, 'data': str(result)}
