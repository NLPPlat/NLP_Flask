from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files


# 标注集列表获取
@api.route('/annotation/list', methods=['GET'])
@jwt_required
def annotationListGet():
    # 分页
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    front = limit * (page - 1)
    end = limit * page
    # 数据库查询
    usernameFilter = request.args.getlist('username[]')
    taskTypeFilter = request.args.getlist('taskType[]')
    annotationStatusFilter = request.args.getlist('annotationStatus[]')
    sort = request.args.get('sort')
    username = get_jwt_identity()
    taskName = request.args.get('taskName')
    queryList = ['id', 'username', 'taskType', 'taskName', 'publicity', 'datetime', 'status', 'annotationStatus']
    q = Q(taskType__in=taskTypeFilter) & Q(annotationStatus__in=annotationStatusFilter)
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


# 标注任务配置
@api.route('/annotation/config', methods=['POST'])
@jwt_required
def annotationConfig():
    taskInfo = request.json
    taskID = taskInfo.get("id")
    username = get_jwt_identity()
    taskQuery = models.OriginalDataset.objects(id=int(taskID)).first()
    if taskQuery and username == taskQuery.username:
        taskType = taskQuery.taskType
        if taskType == '实体关系抽取':
            entityTags = taskInfo.get('entityTags')
            relationTags = taskInfo.get('relationTags')
            taskQuery.annotationFormat = {'entityTags': entityTags, 'relationTags': relationTags}
            taskQuery.annotationStatus = '标注中'
            taskQuery.save()
        return {'code': 200, 'message': '任务配置成功'}
    else:
        return {'code': 400, 'message': '未找到该数据集'}


# 标注tags获取
@api.route('/annotation/config', methods=['GET'])
@jwt_required
def getTags():
    getInfo = request.values
    datasetID = getInfo.get("datasetid")
    username = get_jwt_identity()
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        pass
    return {'code': 200,'data':{'annotationFormat':datasetQuery.annotationFormat}}

# 数据向量获取
@api.route('/annotation/detail/vector', methods=['GET'])
@jwt_required
def getDataVector():
    getInfo = request.values
    datasetID = getInfo.get("datasetid")
    vectorID = getInfo.get('vectorid')
    username = get_jwt_identity()
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.text.filter(id=int(vectorID))
    return {'code': 200, 'data': {'vector': vectorQuery.first()}}

#标注上传
@api.route('/annotation/detail/tags', methods=['POST'])
@jwt_required
def uplaodAnnotationTags():
    postInfo = request.json
    datasetID =postInfo.get("datasetid")
    vectorID = postInfo.get('vectorid')
    label=postInfo.get('label')
    labelDict={'label':label}
    username = get_jwt_identity()
    datasetQuery = models.OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.text.filter(id=int(vectorID))
        vectorQuery.update(**labelDict)
        vectorQuery.save()
    return {'code':200}

