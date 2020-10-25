from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from . import api
from app.models.dataset import *
from app.utils.response_code import *
from app.utils.common_utils import *


# 某个数据集文本向量获取
@api.route('/dataset/datasets/ID/vectors', methods=['GET'])
@jwt_required
def dataVectorsFetch():
    # 读取基本数据
    info = request.values
    datasetid = request.args.get('id')

    # 分页
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    front = limit * (page - 1)
    end = limit * page

    # 数据库查询
    dataQuery = OriginalDataset.objects(id=int(datasetid)).first()
    vectors = dataQuery.originalData.filter(delete='未删除')
    return {'code': 200, 'data': {'items': vectors[front:end], 'total': vectors.count(), 'taskType': dataQuery.taskType,
                                  'groupOn': dataQuery.groupOn}}


# 某个数据集某条向量更改
@api.route('/dataset/datasets/ID/vectors/ID', methods=['PUT'])
@jwt_required
def editDataVector():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    vectorID = info.get('vectorid')
    vector = info.get('vector')
    username = get_jwt_identity()

    # 数据格式转换
    vectorDict = json.loads(vector)
    vectorDict.pop('edit')

    # 数据库修改
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.update(**vectorDict)
        vectorQuery.save()
    return {'code': 200}


# 某个数据集某条向量删除
@api.route('/dataset/datasets/ID/vectors/ID', methods=['DELETE'])
@jwt_required
def deleteDataVector():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    vectorID = info.get('vectorid')
    username = get_jwt_identity()

    # 数据库修改
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.first().delete = '已删除'
        vectorQuery.save()
    return {'code': 200}


# 某个数据集回收站向量获取
@api.route('/dataset/datasets/ID/rubbish', methods=['GET'])
@jwt_required
def dataRubbishGet():
    # 读取基本数据
    info = request.values
    datasetid = request.args.get('id')

    # 分页
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    front = limit * (page - 1)
    end = limit * page

    # 数据库查询
    dataQuery = OriginalDataset.objects(id=int(datasetid)).first()
    vectors = dataQuery.originalData.filter(delete='已删除')
    return {'code': 200, 'data': {'items': vectors[front:end], 'total': vectors.count(), 'taskType': dataQuery.taskType,
                                  'groupOn': dataQuery.groupOn}}


# 某个数据集回收站向量恢复
@api.route('/dataset/datasets/ID/rubbish/ID', methods=['DELETE'])
@jwt_required
def recycleDataVector():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    vectorID = info.get('vectorid')
    username = get_jwt_identity()

    # 数据库修改
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.first().delete = '未删除'
        vectorQuery.save()
    return {'code': 200}


# 数据集拆分
@api.route('/dataset/datasets/ID/vectors', methods=['PATCH'])
@jwt_required
def dataCut():
    # 读取基本数据
    info = request.json
    datasetID = info.get('datasetid')
    level = info.get('level')
    tool = info.get('tool')
    username = get_jwt_identity()

    # 数据库查询及修改
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        curVectors = dataCutService(datasetQuery.originalData)
        datasetQuery.originalData = []
        for curVector in curVectors:
            textContent = TextContent().from_json(json.dumps(curVector))
            datasetQuery.originalData.append(textContent)
        datasetQuery.groupOn = 'on'
        datasetQuery.save()
    return {'code': RET.OK}


# 数据集拆分服务实现
def dataCutService(previousVectors):
    curVectors = []
    id = 0
    for previousVector in previousVectors:
        sentences = sentenceCut(previousVector.text1)
        for sentence in sentences:
            curVector = {}
            curVector['id'] = id
            curVector['group'] = previousVector.id
            curVector['text1'] = sentence
            curVector['delete'] = '未删除'
            if 'title' in previousVector:
                curVector['title'] = previousVector.title
            curVectors.append(curVector)
            id = id + 1
    return curVectors
