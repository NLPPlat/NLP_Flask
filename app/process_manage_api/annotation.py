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


# 某个数据集标注进度查询
@api.route('annotation/datasets/ID/progress', methods=['GET'])
@jwt_required
def fetchAnnotationProgress():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    username = get_jwt_identity()

    # 查询数量
    datasetQuery = OriginalDataset.objects(id=datasetID).first()
    if datasetQuery and username == datasetQuery.username:
        nolabelCount,nolabelVectors=vectors_select(datasetID,{'label':'','deleted':'未删除'})
        allCount,allVectors=vectors_select(datasetID,{'deleted':'未删除'})
    return {'code': RET.OK, 'data': {'nolabelCount': nolabelCount, 'allCount': allCount}}
