from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.dataset import *
from app.utils.vector_uitls import *
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
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        return {'code': RET.OK, 'data': {'annotationFormat': datasetQuery.annotationFormat}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集标注任务配置创建
@api.route('/annotation/datasets/ID/annotation/config', methods=['POST'])
@jwt_required
def annotationConfig():
    # 读取基本数据
    info = request.json
    datasetID = info.get("id")
    annotationFormat = info.get('annotationFormat')
    annotationPublicity = info.get('annotationPublicity')
    username = get_jwt_identity()

    # 数据库写入
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        datasetQuery.annotationFormat = annotationFormat
        datasetQuery.annotationStatus = '标注中'
        datasetQuery.annotationPublicity = annotationPublicity
        if annotationPublicity == '允许':
            datasetQuery.publicity = '公开'
        datasetQuery.save()
        return {'code': RET.OK}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集标注状态更新
@api.route('annotation/datasets/ID/annotation/status', methods=['PUT'])
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
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集标注进度获取
@api.route('annotation/datasets/ID/annotation/progress', methods=['GET'])
@jwt_required
def fetchAnnotationProgress():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    username = get_jwt_identity()

    # 查询数量
    datasetQuery = OriginalDataset.objects(id=datasetID).first()
    if datasetQuery and (username == datasetQuery.username or datasetQuery.publicity == '公开'):
        nolabelCount, nolabelVectors = vectors_select(datasetID, {'label': '', 'deleted': '未删除'})
        allCount, allVectors = vectors_select(datasetID, {'deleted': '未删除'})
        return {'code': RET.OK, 'data': {'nolabelCount': nolabelCount, 'allCount': allCount}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}
