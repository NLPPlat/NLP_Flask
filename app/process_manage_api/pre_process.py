from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app.utils.response_code import RET
from app.utils.preprocess import preprocessManage
from app import models, files
from app.models.dataset import *


# 预处理状态获取
@api.route('/pre-process/preprocess', methods=['GET'])
@jwt_required
def preprocessStatusFetch():
    # 读取数据
    info = request.values
    datasetID = info.get('datasetid')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        pass
    return {'code': RET.OK, 'data': {'items': datasetQuery.preprocessStatus}}


# 新增预处理步骤
@api.route('/pre-process/preprocess/id', methods=['POST'])
@jwt_required
def preprocessAdd():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessAdd = info.get('preprocessAdd')
    previousProcessID=int(info.get('previousProcessID'))
    sparkSupport = info.get('sparkSupport')
    preprocessParams = info.get('preprocessParams')
    username = get_jwt_identity()

    # 数据库查询并修改
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        print(datasetQuery.preprocessStatus)
        previousID=datasetQuery.preprocessStatus[-1]['id']
        datasetQuery.preprocessStatus.append({'id':previousID+1,'preprocessName':preprocessAdd[1],'preprocessType':preprocessAdd[0],'previousProcessID':previousProcessID,'sparkSupport':sparkSupport,'preprocessStatus':'未开始','preprocessParams':preprocessParams})
        datasetQuery.save()
    return {'code':RET.OK}


# 执行预处理步骤
@api.route('/pre-process/preprocess/id', methods=['PUT'])
@jwt_required
def preprocessDeal():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessIndex = info.get('preprocessIndex')
    username = get_jwt_identity()

    # 数据库查询修改、异步处理任务
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        preprocessManage.delay(datasetQuery,preprocessIndex)
    return {'code': RET.OK}