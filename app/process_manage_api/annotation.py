from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.dataset import *
from app.utils.response_code import *


# 某个数据集标注任务配置获取
@api.route('/annotation/datasets/ID/annotation/config', methods=['GET'])
@jwt_required
def getTags():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    username = get_jwt_identity()

    # 读取数据库
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        pass
    return {'code': 200, 'data': {'annotationFormat': datasetQuery.annotationFormat}}


# 某个数据集标注任务配置
@api.route('/annotation/datasets/ID/annotation/config', methods=['POST'])
@jwt_required
def annotationConfig():
    # 读取基本数据
    info = request.json
    datasetID = info.get("id")
    annotationFormat=info.get('annotationFormat')
    annotationPublicity=info.get('annotationPublicity')
    username = get_jwt_identity()

    # 数据库写入
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        datasetQuery.annotationFormat=annotationFormat
        # taskType = taskQuery.taskType
        # if taskType == '实体关系抽取':
        #     entityTags = info.get('entityTags')
        #     relationTags = info.get('relationTags')
        #     taskQuery.annotationFormat = {'entityTags': entityTags, 'relationTags': relationTags}
        # elif taskType == '文本关系分析':
        #     textTags = info.get('textTags')
        #     text1Tags = info.get('text1Tags')
        #     text2Tags = info.get('text2Tags')
        #     taskQuery.annotationFormat = {'textTags': textTags, 'text1Tags': text1Tags, 'text2Tags': text2Tags}
        # elif taskType == '文本排序学习' or taskType == '文本摘要' or taskType == '情感分析/意图识别':
        #     annotationConfig = info.get('annotationFormat')
        #     taskQuery.annotationFormat = annotationConfig
        # elif taskType == '通用单文本分类':
        #     textTags = info.get('textTags')
        #     taskQuery.annotationFormat = textTags
        datasetQuery.annotationStatus = '标注中'
        datasetQuery.annotationPublicity = annotationPublicity
        datasetQuery.save()
        return {'code': 200, 'message': '任务配置成功'}
    else:
        return {'code': 400, 'message': '未找到该数据集'}


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
        if datasetQuery.taskType == '文本排序学习' or datasetQuery.taskType == '文本摘要' and datasetQuery.annotationFormat['type'] == '抽取式' or datasetQuery.taskType == '情感分析/意图识别' and \
                datasetQuery.annotationFormat['type'] == '句子级':
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


# 获取标注状态
@api.route('annotation/status/ID', methods=['GET'])
@jwt_required
def fetchAnnotationStatus():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    username = get_jwt_identity()

    # 查询状态
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        status = datasetQuery.annotationStatus
    return {'code': RET.OK, 'data': {'annotationStatus': status}}


# 更新标注状态
@api.route('annotation/status/ID', methods=['POST'])
@jwt_required
def completeAnnotationStatus():
    # 读取基本数据
    info = request.json
    datasetID = info.get("datasetid")
    username = get_jwt_identity()

    # 查询状态
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        datasetQuery.annotationStatus = '标注完成'
        datasetQuery.save()
    return {'code': RET.OK}


# 标注进度查询
@api.route('annotation/progress/ID', methods=['GET'])
@jwt_required
def fetchAnnotationProgress():
    # 读取基本数据
    info = request.values
    datasetID = info.get("datasetid")
    username = get_jwt_identity()

    # 查询数量
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        nolabelQuery = datasetQuery.originalData.filter(label='')
        allQuery = datasetQuery.originalData.filter()
    return {'code': RET.OK, 'data': {'nolabelCount': len(nolabelQuery), 'allCount': len(allQuery)}}
