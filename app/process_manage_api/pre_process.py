from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files

#数据集导入
@api.route('preprocess/list',methods=['POST'])
@jwt_required
def preprocessListPost():
    return {'code':200}



# 数据集列表获取
@api.route('/preprocess/list', methods=['GET'])
@jwt_required
def preprocessListGet():
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