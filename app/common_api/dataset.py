from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files
from app.utils.response_code import RET
from app.utils.dataset_utils import copy
from app.utils.file_utils import fileDelete
from app.models.dataset import *
from app.models.venation import *


# 数据集列表获取
@api.route('/dataset/dataset', methods=['GET'])
@jwt_required
def datasetListFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    username = get_jwt_identity()
    datasetType = info.get('datasetType')

    # 读取过滤器、设置查询项
    queryTaskName = request.args.get('taskName')
    usernameFilter = info.getlist('username[]')
    taskTypeFilter = info.getlist('taskType[]')
    sort = info.get('sort')
    if datasetType == '原始数据集':
        analyseStatusFilter = info.getlist('analyseStatus[]')
        queryList = ['id', 'username', 'taskType', 'taskName', 'desc', 'publicity', 'datetime', 'analyseStatus',
                     'annotationStatus']
    elif datasetType == '标注数据集':
        annotationStatusFilter = info.getlist('annotationStatus[]')
        queryList = ['id', 'username', 'taskType', 'taskName', 'datetime', 'analyseStatus',
                     'annotationStatus', 'annotationPublicity']
    elif datasetType == '预处理数据集':
        queryList = ['id', 'username', 'taskType', 'taskName', 'desc', 'publicity', 'datetime']

    # 设置查询条件Q
    q = Q(taskType__in=taskTypeFilter)
    if len(queryTaskName) > 0:
        q = q & Q(taskName__icontains=queryTaskName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))
    if datasetType == '原始数据集':
        q = q & Q(analyseStatus__in=analyseStatusFilter)
    elif datasetType == '标注数据集':
        q = q & Q(annotationStatus__in=annotationStatusFilter)
    elif datasetType == '预处理数据集':
        pass

    # 数据库查询
    if datasetType == '原始数据集' or datasetType == '标注数据集':
        datasetList = OriginalDataset.objects(q).scalar(*queryList).order_by(sort)
    elif datasetType == '预处理数据集':
        datasetList = PreprocessDataset.objects(q).scalar(*queryList).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': datasetList.count(), 'items': datasetList[front:end]}}


# 数据集ID列表获取
@api.route('/dataset/dataset/IDs', methods=['GET'])
@jwt_required
def datasetIDListFetch():
    # 读取基本数据
    info = request.values
    username = get_jwt_identity()
    datasetType = info.get('datasetType')

    queryList = ['id', 'taskName']
    datasetQuery=Dataset.objects(Q(username=username) & Q(datasetType=datasetType)).scalar(*queryList)
    return {'code':RET.OK,'data':{'items':datasetQuery}}


# 数据集信息列表获取
# @api.route('/dataset/dataset/info', methods=['GET'])
# @jwt_required
# def datasetInfoListFetch():
#     # 读取基本数据
#     info = request.values
#     datasetidList = info.getlist('datasetidList[]')
#     username = get_jwt_identity()
#
#     #查询数据库
#     queryList = ['id', 'username', 'taskType', 'taskName', 'desc', 'publicity', 'datetime', 'analyseStatus',
#                  'annotationStatus']
#     datasetQuery=Dataset.objects(id__in=datasetidList)
#     return {'code':RET.OK,'data':{'items':datasetQuery}}




# 数据集拷贝
@api.route('/dataset/dataset', methods=['POST'])
@jwt_required
def datasetCopy():
    # 读取数据
    info = request.json
    datasetInitType = info.get('datasetInitType')
    datasetInitID = info.get('datasetInitid')
    copyDes = info.get('copyDes')
    username = get_jwt_identity()
    # 读取原数据集
    if datasetInitType == '原始数据集':
        datasetInit = OriginalDataset.objects(id=int(datasetInitID)).first()
        venationInit = Venation.objects(ancestor=int(datasetInitID)).first()
    # 拷贝
    datasetDesID=copy(datasetInit, datasetInitType, copyDes, username, venationInit)
    return {'code': RET.OK,'data':{'datasetid':datasetDesID}}


# 数据集删除
@api.route('/dataset/dataset', methods=['DELETE'])
@jwt_required
def datasetDelete():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    datasetType = info.get('datasetType')
    username = get_jwt_identity()

    # 查找判断并删除
    if datasetType == '原始数据集':
        datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
        if datasetQuery and username == datasetQuery.username:
            fileDelete([datasetQuery.originalFile])
            datasetQuery.delete()
    elif datasetType == '预处理数据集':
        datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
        if datasetQuery and username == datasetQuery.username:
            datasetQuery.delete()

    return {'code': RET.OK}


# 任务信息修改
@api.route('dataset/dataset/ID/info', methods=['PATCH'])
@jwt_required
def taskinfoVerity():
    # 读取数据集信息
    info = request.json
    datasetID = info.get('datasetid')
    taskName = info.get('taskName')
    desc = info.get('desc')
    username = get_jwt_identity()

    # 修改任务信息
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        datasetQuery.taskName = taskName
        datasetQuery.desc = desc
        datasetQuery.save()

    return {'code': RET.OK}


# 任务类型获取
@api.route('/dataset/dataset/ID/tasktype', methods=['GET'])
@jwt_required
def tasktypeFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    username = get_jwt_identity()

    # 查找数据集
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        taskType = datasetQuery.taskType
    return {'code': RET.OK, 'data': {'taskType': taskType}}


# 按group获取vector
@api.route('/dataset/dataset/ID/group', methods=['GET'])
@jwt_required
def groupVectorsFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    group = info.get('group')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectorQuery = datasetQuery.originalData.filter(group=group)
    return {'code': RET.OK, 'data': {'vectors': vectorQuery}}
