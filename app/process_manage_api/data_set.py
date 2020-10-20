from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files
from app.models.dataset import *
from app.utils.response_code import RET
from app.utils.data_process_utils import sentenceCut


# 数据详情获取
@api.route('/dataset/detail', methods=['GET'])
@jwt_required
def dataDetailGet():
    # 分页
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    front = limit * (page - 1)
    end = limit * page
    # 数据库查询
    id = request.args.get('id')
    data = OriginalDataset.objects(id=int(id)).first()
    res = data.originalData.filter(delete='未删除')
    return {'code': 200, 'data': {'items': res[front:end], 'total': res.count(), 'taskType': data.taskType,'groupOn':data.groupOn}}


# 数据向量更改
@api.route('/dataset/detail/vector', methods=['PUT'])
@jwt_required
def editDataVector():
    putInfo = request.values
    datasetID = putInfo.get("datasetid")
    vectorID = putInfo.get('vectorid')
    vector = putInfo.get('vector')
    vectorDict = json.loads(vector)
    vectorDict.pop('edit')
    username = get_jwt_identity()
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.update(**vectorDict)
        vectorQuery.save()
    return {'code': 200}


# 数据向量删除
@api.route('/dataset/detail/vector', methods=['DELETE'])
@jwt_required
def deleteDataVector():
    deleteInfo = request.values
    datasetID = deleteInfo.get("datasetid")
    vectorID = deleteInfo.get('vectorid')
    username = get_jwt_identity()
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.first().delete = '已删除'
        vectorQuery.save()
    return {'code': 200}


# 回收站详情获取
@api.route('/dataset/rubbish', methods=['GET'])
@jwt_required
def dataRubbishGet():
    # 分页
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    front = limit * (page - 1)
    end = limit * page
    # 数据库查询
    id = request.args.get('id')
    data = OriginalDataset.objects(id=id).first()
    res = data.originalData.filter(delete='已删除')
    return {'code': 200, 'data': {'items': res[front:end], 'total': res.count(), 'taskType': data.taskType,'groupOn':data.groupOn}}


# 数据向量删除
@api.route('/dataset/rubbish/vector', methods=['DELETE'])
@jwt_required
def recycleDataVector():
    deleteInfo = request.values
    datasetID = deleteInfo.get("datasetid")
    vectorID = deleteInfo.get('vectorid')
    username = get_jwt_identity()
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
        vectorQuery.first().delete = '未删除'
        vectorQuery.save()
    return {'code': 200}


# 数据集拷贝
@api.route('/dataset/copy', methods=['POST'])
@jwt_required
def copyDataSet():
    postInfo = request.json
    copyID = postInfo.get('copyid')
    copyType = postInfo.get('copyType')
    username = get_jwt_identity()
    if copyType == '原始数据集':
        pass
    elif copyType == '预处理数据集':
        pass
    return {'code': 200}


# 数据集拆分
@api.route('/dataset/dataset/ID/vectors', methods=['PUT'])
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
        curVectors=dataCutService(datasetQuery.originalData)
        datasetQuery.originalData=[]
        for curVector in curVectors:
            textContent = TextContent().from_json(json.dumps(curVector))
            datasetQuery.originalData.append(textContent)
        datasetQuery.groupOn='on'
        datasetQuery.save()
    return {'code': RET.OK}


# 数据集拆分服务实现
def dataCutService(previousVectors):
    curVectors=[]
    id=0
    for previousVector in previousVectors:
        sentences=sentenceCut(previousVector.text1)
        for sentence in sentences:
            curVector={}
            curVector['id']=id
            curVector['group']=previousVector.id
            curVector['text1']=sentence
            curVector['delete']='未删除'
            if 'title' in previousVector:
                curVector['title']=previousVector.title
            curVectors.append(curVector)
            id=id+1
    return curVectors




