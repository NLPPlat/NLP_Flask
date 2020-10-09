from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files


# 数据集列表获取
@api.route('/dataset/list', methods=['GET'])
@jwt_required
def datasetListGet():
    # 分页
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    front = limit * (page - 1)
    end = limit * page
    # 数据库查询
    usernameFilter = request.args.getlist('username[]')
    taskTypeFilter = request.args.getlist('taskType[]')
    statusFilter = request.args.getlist('status[]')
    sort = request.args.get('sort')
    username = get_jwt_identity()
    taskName = request.args.get('taskName')
    queryList = ['id', 'username', 'taskType', 'taskName', 'publicity', 'datetime', 'status']
    q = Q(taskType__in=taskTypeFilter) & Q(status__in=statusFilter)
    if len(taskName) > 0:
        q = q & Q(taskName__icontains=taskName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))
    datasetList = models.OriginalDataset.objects(q).scalar(*queryList).order_by(sort)
    # 返回
    return {'code': 200, 'data': {'total': datasetList.count(), 'items': datasetList[front:end]}}


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
    data = models.OriginalDataset.objects(id=id).first()
    res = data.text.filter(delete='未删除')
    return {'code': 200, 'data': {'items': res[front:end], 'total': res.count(), 'taskType': data.taskType}}


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
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.text.filter(id=int(vectorID))
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
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.text.filter(id=int(vectorID))
        vectorQuery.first().delete='已删除'
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
    data = models.OriginalDataset.objects(id=id).first()
    res = data.text.filter(delete='已删除')
    return {'code': 200, 'data': {'items': res[front:end], 'total': res.count(), 'taskType': data.taskType}}

# 数据向量删除
@api.route('/dataset/rubbish/vector', methods=['DELETE'])
@jwt_required
def recycleDataVector():
    deleteInfo = request.values
    datasetID = deleteInfo.get("datasetid")
    vectorID = deleteInfo.get('vectorid')
    username = get_jwt_identity()
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.text.filter(id=int(vectorID))
        vectorQuery.first().delete='未删除'
        vectorQuery.save()
    return {'code': 200}

#数据集拷贝
@api.route('/dataset/copy', methods=['POST'])
@jwt_required
def copyDataSet():
    postInfo=request.json
    copyID=postInfo.get('copyid')
    copyType=postInfo.get('copyType')
    username=get_jwt_identity()
    if copyType=='原始数据集':
        pass
    elif copyType=='预处理数据集':
        pass
    return {'code':200}