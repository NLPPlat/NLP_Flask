from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.operator import *
from app.models.model import *
from app.utils.response_code import *
from app.utils.codehub_utils import *


# 模型列表获取
@api.route('/model/models', methods=['GET'])
@jwt_required
def modelssFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    queryModelName = info.get('modelName')
    username = get_jwt_identity()

    # 读取过滤器、设置查询项
    usernameFilter = info.getlist('username[]')
    sort = info.get('sort')

    # 设置查询条件Q
    q = Q()
    if len(queryModelName) > 0:
        q = q & Q(taskName__icontains=queryModelName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))
    # 数据库查询
    modelsList = Model.objects(q).order_by(sort)
    # 分页
    front = limit * (page - 1)
    end = limit * page
    return {'code': RET.OK, 'data': {'total': modelsList.count(), 'items': modelsList[front:end]}}


# 模型保存
@api.route('/model/models/ID', methods=['POST'])
@jwt_required
def modelUpload():
    # 读取基本数据
    info = request.json
    code = info.get('code')
    publicity = info.get('publicity')
    modelID = info.get('modelid')
    modelName = info.get('modelName')
    username = get_jwt_identity()

    if (int(modelID) == -1):
        model = Model(modelName=modelName, username=username,
                      publicity=publicity, code=code)
        model.save()
    else:
        operatorQuery = Operator.objects(id=int(modelID)).first()
        if operatorQuery and username == operatorQuery.username:
            operatorQuery.operatorName = modelName
            operatorQuery.publicity = publicity
            operatorQuery.code = code
            operatorQuery.save()
    return {'code': RET.OK}
