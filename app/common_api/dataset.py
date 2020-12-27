from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.dataset import *
from app.models.venation import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.dataset_utils import *
from app.utils.file_utils import *
from app.utils.task_utils import *
from app.utils.permission_utils import *


# 数据集列表获取
@api.route('/dataset/datasets', methods=['GET'])
@jwt_required
def datasetListFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    username = get_jwt_identity()
    datasetType = info.get('datasetType')

    # 获得用户信息
    user = User.objects(username=username).first()
    roles = user.roles

    # 设置通用查询条件Q
    taskTypeFilter = info.getlist('taskType[]')
    usernameFilter = info.getlist('username[]')
    queryTaskName = request.args.get('taskName')
    sort = info.get('sort')
    q = Q(taskType__in=taskTypeFilter)
    if len(queryTaskName) > 0:
        q = q & Q(taskName__icontains=queryTaskName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        if 'admin' in roles:
            pass
        else:
            q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        if 'admin' in roles:
            q = q & Q(username__ne=username)
        else:
            q = q & (Q(username__ne=username) & Q(publicity='公开'))

    # 设置独立查询条件
    analyseStatusFilter = ['解析完成']
    if datasetType == '训练数据集' or datasetType == '批处理数据集':
        analyseStatusFilter = info.getlist('analyseStatus[]')
    elif datasetType == '标注数据集':
        annotationStatusFilter = info.getlist('annotationStatus[]')
        q = q & Q(annotationStatus__in=annotationStatusFilter)
    elif datasetType == '预处理数据集':
        pass
    elif datasetType == '特征数据集':
        trainStatusFilter = info.getlist('trainStatus[]')
        q = q & Q(trainStatus__in=trainStatusFilter)
    elif datasetType == '批处理特征集':
        batchStatusFilter = info.getlist('batchStatus[]')
        q = q & Q(batchStatus__in=batchStatusFilter)
    q = q & Q(analyseStatus__in=analyseStatusFilter)

    # 数据库查询
    if datasetType == '训练数据集' or datasetType == '标注数据集':
        datasetList = OriginalDataset.objects(q).order_by(sort)
    elif datasetType == '批处理数据集':
        datasetList = OriginalBatchDataset.objects(q).order_by(sort)
    elif datasetType == '预处理数据集':
        datasetList = PreprocessDataset.objects(q).order_by(sort)
    elif datasetType == '特征数据集':
        datasetList = FeaturesDataset.objects(q).order_by(sort)
    elif datasetType == '批处理特征集':
        datasetList = FeaturesBatchDataset.objects(q).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page
    return {'code': RET.OK, 'data': {'total': datasetList.count(), 'items': datasetList[front:end]}}


# 数据集创建（拷贝）
@api.route('/dataset/datasets', methods=['POST'])
@jwt_required
def datasetCopy():
    # 读取数据
    info = request.json
    datasetInitType = info.get('datasetInitType')
    datasetInitID = info.get('datasetInitid')
    copyDes = info.get('copyDes')
    username = get_jwt_identity()
    params = {}
    if 'params' in info:
        params = info.get('params')

    # 读取数据集信息
    datasetInit = Dataset.objects(id=int(datasetInitID)).first()
    if not datasetReadPermission(datasetInit, username):
        return noPeimissionReturn()
    datasetDesID = copyManage(datasetInit, copyDes, username, params)
    return {'code': RET.OK, 'data': {'datasetDesID': datasetDesID}}


# 某个数据集信息获取
@api.route('/dataset/datasets/ID', methods=['GET'])
@jwt_required
def datasetInfoFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    username = get_jwt_identity()

    # 查找数据集
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetReadPermission(datasetQuery, username):
        return noPeimissionReturn()
    dataResult = datasetQuery.to_mongo().to_dict()
    return {'code': RET.OK, 'data': dataResult}


# 某个数据集信息更新
@api.route('dataset/datasets/ID', methods=['PUT'])
@jwt_required
def datasetInfoUpdate():
    # 读取数据集信息
    info = request.json
    datasetID = info.get('datasetid')
    infos = info.get('infos')
    username = get_jwt_identity()

    # 查找数据集
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetWritePermission(datasetQuery, username):
        return noPeimissionReturn()
    for key in infos:
        datasetQuery[key] = infos[key]
        datasetQuery.save()
    return {'code': RET.OK}


# 某个数据集名称、描述信息更新
@api.route('dataset/datasets/ID', methods=['PATCH'])
@jwt_required
def datasetInfoVerity():
    # 读取数据集信息
    info = request.json
    datasetID = info.get('datasetid')
    taskName = info.get('taskName')
    desc = info.get('desc')
    username = get_jwt_identity()

    # 修改任务信息
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetWritePermission(datasetQuery, username):
        return noPeimissionReturn()
    datasetQuery.taskName = taskName
    datasetQuery.desc = desc
    datasetQuery.save()
    return {'code': RET.OK}


# 某个数据集删除
@api.route('/dataset/datasets/ID', methods=['DELETE'])
@jwt_required
def datasetDelete():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    datasetType = info.get('datasetType')
    username = get_jwt_identity()

    # 查找判断并删除
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetWritePermission(datasetQuery, username):
        return noPeimissionReturn()
    datasetQuery.delete()
    return {'code': RET.OK}


# 某个数据集向量获取
@api.route('/dataset/datasets/ID/vectors', methods=['GET'])
@jwt_required
def datasetVectorsFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    deleted = info.get('deleted')
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetReadPermission(datasetQuery, username):
        return noPeimissionReturn()
    count, vectors = vectors_select_divide(datasetID, deleted, limit, page, datasetQuery.datasetType)
    return {'code': RET.OK, 'data': {'items': vectors, 'total': count}}


# 某个数据集某条向量获取
@api.route('/dataset/datasets/ID/vector/ID', methods=['GET'])
@jwt_required
def datasetVectorFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    vectorID = int(info.get('vectorid'))
    username = get_jwt_identity()

    # 数据查询
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetReadPermission(datasetQuery, username):
        return noPeimissionReturn()
    vector = vectors_select_one(datasetID, vectorID)
    return {'code': RET.OK, 'data': {'vector': vector}}


# 某个数据集某条向量更新
@api.route('/dataset/datasets/ID/vectors/ID', methods=['PUT'])
@jwt_required
def datasetVectorUpdate():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    vectorID = int(info.get('vectorid'))
    vector = info.get('vector')
    username = get_jwt_identity()

    # 数据格式转换
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if not datasetWritePermission(datasetQuery, username):
        return noPeimissionReturn()
    vectorDict = json.loads(vector)
    if 'edit' in vectorDict:
        vectorDict.pop('edit')
    # 数据库修改
    vector_update(datasetID, vectorID, vectorDict)
    return {'code': RET.OK}


# 某个数据集某个group的vectors获取
@api.route('/dataset/datasets/ID/group/vectors', methods=['GET'])
@jwt_required
def groupVectorsFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    group = int(info.get('group'))
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if not datasetReadPermission(datasetQuery, username):
        return noPeimissionReturn()
    count, vectors = vectors_select(datasetID, {'group': group, 'deleted': '未删除'})
    return {'code': RET.OK, 'data': {'vectors': vectors, 'count': count}}


# 某个数据集某个group的vectors更新
@api.route('/dataset/datasets/ID/group/vectors', methods=['PUT'])
@jwt_required
def groupVectorsUpdate():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    group = info.get('group')
    vectors = info.get('vectors')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if datasetQuery and (username == datasetQuery.username or (
            'annotationPublicity' in datasetQuery and datasetQuery.annotationPublicity == '允许')):
        for vector in vectors:
            vector_update(datasetID, vector['vectorid'], vector)
        return {'code': RET.OK, 'data': {'vectors': vectors}}
    else:
        return {'code': RET.FORBBIDEN, 'message': error_map[RET.FORBBIDEN]}


# 某个数据集总量信息获取
@api.route('/dataset/datasets/ID/totalInfo', methods=['GET'])
@jwt_required
def datasetTotalInfoFetch():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    type = int(info.get('totalType'))
    username = get_jwt_identity()

    # 数据查询
    datasetQuery = OriginalDataset.objects(id=int(datasetID)).first()
    if not datasetReadPermission(datasetQuery, username):
        return noPeimissionReturn()
    if type == 0:
        min = vectors_select_first(datasetID).vectorid
        max = vectors_select_last(datasetID).vectorid
    else:
        min = vectors_select_first(datasetID).group
        max = vectors_select_last(datasetID).group
    return {'code': RET.OK, 'data': {'max': max, 'min': min}}


# 部分数据集信息获取
@api.route('/dataset/datasets/IDs/info', methods=['GET'])
@jwt_required
def datasetIDListFetch():
    # 读取基本数据
    info = request.values
    username = get_jwt_identity()
    datasetType = info.get('datasetType')

    queryList = ['id', 'taskName']
    datasetQuery = Dataset.objects(Q(username=username) & Q(datasetType=datasetType)).scalar(*queryList)
    return {'code': RET.OK, 'data': {'items': datasetQuery}}
