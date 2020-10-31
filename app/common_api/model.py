from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.model import *
from app.utils.response_code import *



# 某个人的模型列表获取
@api.route('/model/models', methods=['GET'])
@jwt_required
def modelsForUserFetch():
    # 读取基本数据
    username = get_jwt_identity()

    # 数据库查询
    modelQuery = Model.objects(username=username)
    return {'code': RET.OK, 'data': {'items': modelQuery}}

# 某个模型信息获取
@api.route('/model/models/ID', methods=['GET'])
@jwt_required
def modelFetch():
    # 读取基本数据
    info = request.values
    modelID = info.get('modelid')
    username = get_jwt_identity()

    # 数据库读取
    modelQuery = Model.objects(id=int(modelID)).first()
    if modelQuery and username == modelQuery.username:
        data = modelQuery
    return {'code': RET.OK, 'data': data}

# 某个训练模型信息获取
@api.route('/model/trainedmodels/ID', methods=['GET'])
@jwt_required
def trainedmodelFetch():
    # 读取基本数据
    info = request.values
    trainedmodelID= int(info.get('trainedmodelid'))
    username = get_jwt_identity()

    # 数据库读取
    trainedmodelQuery = TrainedModel.objects(id=trainedmodelID).first()
    if trainedmodelQuery and username == trainedmodelQuery.username:
        data = trainedmodelQuery
    return {'code': RET.OK, 'data': data}

