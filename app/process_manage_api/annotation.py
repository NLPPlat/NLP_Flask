from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files
from app.models.dataset import *


# 标注任务配置
@api.route('/annotation/config', methods=['POST'])
@jwt_required
def annotationConfig():
    taskInfo = request.json
    taskID = taskInfo.get("id")
    username = get_jwt_identity()
    taskQuery = OriginalDataset.objects(id=int(taskID)).first()
    if taskQuery and username == taskQuery.username:
        taskType = taskQuery.taskType
        if taskType == '实体关系抽取':
            entityTags = taskInfo.get('entityTags')
            relationTags = taskInfo.get('relationTags')
            taskQuery.annotationFormat = {'entityTags': entityTags, 'relationTags': relationTags}
        elif taskType == '文本关系分析':
            textTags = taskInfo.get('textTags')
            text1Tags = taskInfo.get('text1Tags')
            text2Tags = taskInfo.get('text2Tags')
            taskQuery.annotationFormat = {'textTags': textTags, 'text1Tags': text1Tags, 'text2Tags': text2Tags}
        elif taskType == '文本排序学习' or taskType == '文本摘要':
            annotationConfig = taskInfo.get('annotationFormat')
            taskQuery.annotationFormat = annotationConfig
        elif taskType == '通用单文本分类':
            textTags = taskInfo.get('textTags')
            taskQuery.annotationFormat = textTags
        taskQuery.annotationStatus = '标注中'
        taskQuery.annotationPublicity = taskInfo.get('annotationPublicity')
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
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        pass
    return {'code': 200, 'data': {'annotationFormat': datasetQuery.annotationFormat}}


# 数据向量获取
@api.route('/annotation/detail/vector', methods=['GET'])
@jwt_required
def getDataVector():
    getInfo = request.values
    datasetID = getInfo.get("datasetid")
    vectorID = getInfo.get('vectorid')
    username = get_jwt_identity()
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
    return {'code': 200, 'data': {'vector': vectorQuery.first()}}


# 标注上传
@api.route('/annotation/detail/tags', methods=['POST'])
@jwt_required
def uplaodAnnotationTags():
    # 读取基本数据
    info = request.json
    datasetID = info.get("datasetid")
    username = get_jwt_identity()

    # 分类处理
    # 查询
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        if datasetQuery.taskType == '文本排序学习' and datasetQuery.annotationFormat == '列表标注' or datasetQuery.taskType == '文本摘要' and datasetQuery.annotationFormat == '抽取式':
            vectors = info.get('vectors')
            for item in vectors:
                vectorQuery = datasetQuery.originalData.filter(id=int(item['id']))
                vectorQuery.first().label = item['label']
                vectorQuery.save()
        else:
            # 读取数据
            vectorID = info.get('vectorid')
            label = info.get('label')
            labelDict = {'label': label}
            # 更新字段
            vectorQuery = datasetQuery.originalData.filter(id=int(vectorID))
            vectorQuery.update(**labelDict)
            vectorQuery.save()

    return {'code': 200}
