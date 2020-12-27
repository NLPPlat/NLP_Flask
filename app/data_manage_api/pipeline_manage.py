from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q

from . import api
from app.models.dataset import *
from app.models.pipeline import *
from app.utils.response_code import *
from app.utils.venation_utils import *


# 管道列表获取
@api.route('/pipeline/pipelines', methods=['GET'])
@jwt_required
def pipelinesFetch():
    # 读取基本数据
    info = request.values
    limit = int(info.get('limit'))
    page = int(info.get('page'))
    queryPipelineName = info.get('pipelineName')
    username = get_jwt_identity()

    # 读取过滤器、设置查询项
    usernameFilter = info.getlist('username[]')
    taskTypeFilter = info.getlist('taskType[]')
    sort = info.get('sort')

    # 设置查询条件Q
    q = Q(taskType__in=taskTypeFilter)
    if len(queryPipelineName) > 0:
        q = q & Q(pipelineName__icontains=queryPipelineName)
    if '自己' in usernameFilter and '他人' in usernameFilter:
        q = q & (Q(username=username) | Q(publicity='公开'))
    elif '自己' in usernameFilter:
        q = q & Q(username=username)
    else:
        q = q & (Q(username__ne=username) | Q(publicity='公开'))

    # 数据库查询
    pipelinesList = Pipeline.objects(q).order_by(sort)

    # 分页
    front = limit * (page - 1)
    end = limit * page

    return {'code': RET.OK, 'data': {'total': pipelinesList.count(), 'items': pipelinesList[front:end]}}


# 管道创建
@api.route('/pipeline/pipelines', methods=['POST'])
@jwt_required
def pipelineConstruction():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    publicity = info.get('publicity')
    pipelineName = info.get('pipelineName')
    username = get_jwt_identity()

    # 填充管道
    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    if datasetQuery and username == datasetQuery.username:
        # 初始化步骤数组
        preprocessIndexes = []
        preprocessIndex = preprocessID
        while preprocessIndex != 0:
            preprocessIndexes.append(preprocessIndex)
            preprocessIndex = datasetQuery.preprocessStatus[preprocessIndex]['previousProcessID']
        # 适配步骤内容
        pipeline = Pipeline(username=username, pipelineName=pipelineName, publicity=publicity,
                            taskType=datasetQuery.taskType)
        preprocessPreviousObj = {'label_id': '', 'embedding': ''}
        while len(preprocessIndexes) > 0:
            preprocessIndex = preprocessIndexes.pop(-1)
            preprocessObj = datasetQuery.data.filter(id=preprocessIndex).first().to_mongo().to_dict()
            preprocessStatusObj = datasetQuery.preprocessStatus[preprocessIndex]
            pipelineObj = PipelineObject(preprocessType=preprocessStatusObj['preprocessType'],
                                         preprocessName=preprocessStatusObj['preprocessName'],
                                         preprocessParams=preprocessStatusObj['preprocessParams'],
                                         sparkSupport=preprocessStatusObj['sparkSupport'])
            if preprocessPreviousObj['label_id'] != preprocessObj['label_id']:
                pipelineObj.pipeline = {'label_id': preprocessObj['label_id']}
            if preprocessPreviousObj['embedding'] != preprocessObj['embedding']:
                pipelineObj.pipeline = {'embedding': preprocessObj['embedding']}
            preprocessPreviousObj = preprocessObj
            pipeline.pipelines.append(pipelineObj)
        pipeline.save()
        # 创建数据脉络节点
        venationParentID = findNodeID('预处理数据集', datasetID)
        createNode([venationParentID], '预处理管道对象', pipeline.id)

    return {'code': RET.OK}
