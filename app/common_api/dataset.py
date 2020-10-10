from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files
from app.utils.response_code import RET
from app.utils.dataset import copy
from app.models.dataset import *


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
        queryList = ['id', 'username', 'taskType', 'taskName', 'publicity', 'datetime', 'analyseStatus',
                     'annotationStatus']
    elif datasetType == '标注数据集':
        annotationStatusFilter = info.getlist('annotationStatus[]')
        queryList = ['id', 'username', 'taskType', 'taskName', 'publicity', 'datetime', 'analyseStatus',
                     'annotationStatus']
    elif datasetType == '预处理数据集':
        queryList = ['id', 'username', 'taskType', 'taskName', 'publicity', 'datetime']

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
    if datasetType == '原始数据集' or datasetType=='标注数据集':
        datasetList = OriginalDataset.objects(q).scalar(*queryList).order_by(sort)
    elif datasetType == '预处理数据集':
        datasetList = PreprocessDataset.objects(q).scalar(*queryList).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': datasetList.count(), 'items': datasetList[front:end]}}


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
    # 拷贝
    copy(datasetInit, datasetInitType, copyDes, username)
    return {'code': RET.OK}
