from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.model import *
from app.utils.permission_utils import *


# 模型列表获取
@api.route('/model/models', methods=['GET'])
@jwt_required
def modelsFetch():
    # 读取基本数据
    info = request.values
    queryModelName = info.get('modelName')
    usernameFilter = info.getlist('username[]')
    platTypeFilter = info.getlist('platType[]')
    sort = info.get('sort')
    username = get_jwt_identity()

    # 获得用户信息
    user = User.objects(username=username).first()
    roles = user.roles

    # 设置查询条件Q
    q = Q(platType__in=platTypeFilter)
    if len(queryModelName) > 0:
        q = q & Q(modelName__icontains=queryModelName)
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
    modelsList = BaseModel.objects(q).order_by(sort)

    # 分页
    type = info.get('type')
    if type == 'part':
        limit = int(info.get('limit'))
        page = int(info.get('page'))
        front = limit * (page - 1)
        end = limit * page
        return {'code': RET.OK, 'data': {'total': modelsList.count(), 'items': modelsList[front:end]}}
    else:
        return {'code': RET.OK, 'data': {'total': modelsList.count(), 'items': modelsList}}


# 训练模型列表获取
@api.route('/model/trainedmodels', methods=['GET'])
@jwt_required
def trainedmodelsFetch():
    # 读取基本数据
    info = request.values
    queryModelName = info.get('modelName')
    usernameFilter = info.getlist('username[]')
    platTypeFilter = info.getlist('platType[]')
    sort = info.get('sort')
    username = get_jwt_identity()

    # 获得用户信息
    user = User.objects(username=username).first()
    roles = user.roles

    # 设置查询条件Q
    q = Q(platType__in=platTypeFilter)
    if len(queryModelName) > 0:
        q = q & Q(modelName__icontains=queryModelName)
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
    modelsList = TrainedModel.objects(q).order_by(sort)

    type = info.get('type')
    if type == 'part':
        limit = int(info.get('limit'))
        page = int(info.get('page'))
        front = limit * (page - 1)
        end = limit * page
        return {'code': RET.OK, 'data': {'total': modelsList.count(), 'items': modelsList[front:end]}}
    else:
        return {'code': RET.OK, 'data': {'total': modelsList.count(), 'items': modelsList}}


# 某个模型信息获取
@api.route('/model/models/ID', methods=['GET'])
@jwt_required
def modelFetch():
    # 读取基本数据
    info = request.values
    modelID = info.get('modelid')
    username = get_jwt_identity()

    # 数据库读取
    modelQuery = BaseModel.objects(id=int(modelID)).first()
    if not readPermission(modelQuery, username):
        return noPeimissionReturn()
    data = modelQuery
    return {'code': RET.OK, 'data': data}


# 某个训练模型信息获取
@api.route('/model/trainedmodels/ID', methods=['GET'])
@jwt_required
def trainedmodelFetch():
    # 读取基本数据
    info = request.values
    trainedmodelID = int(info.get('trainedmodelid'))
    username = get_jwt_identity()

    # 数据库读取
    trainedmodelQuery = TrainedModel.objects(id=trainedmodelID).first()
    if not readPermission(trainedmodelQuery, username):
        return noPeimissionReturn()
    data = trainedmodelQuery
    return {'code': RET.OK, 'data': data}
