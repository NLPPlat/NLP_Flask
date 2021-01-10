from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.utils.venation_utils import *
from app.utils.permission_utils import *
from app.utils.time_utils import *


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
    if not writePermission(datasetQuery, username):
        return noPeimissionReturn()
    if not namePermission(pipelineName,'管道文件'):
        return repeatNameReturn()
    # 初始化步骤数组
    preprocessIndexes = []
    preprocessIndex = preprocessID
    while preprocessIndex != 0:
        preprocessIndexes.append(preprocessIndex)
        preprocessIndex = datasetQuery.preprocessStatus[preprocessIndex]['previousProcessID']
    # 适配步骤内容
    pipeline = Pipeline(username=username, pipelineName=pipelineName, publicity=publicity,
                        taskType=datasetQuery.taskType,datetime=getTime())
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


# 某个管道预处理列表获取
@api.route('/pipeline/pipelines/ID/preprocesses', methods=['GET'])
@jwt_required
def preprocessForPipelineFetch():
    # 读取数据
    info = request.values
    pipelineID = info.get('pipelineid')
    username = get_jwt_identity()

    # 数据库查询
    pipelineQuery = Pipeline.objects(id=int(pipelineID)).first()
    if not readPermission(pipelineQuery, username):
        return noPeimissionReturn()
    return {'code': RET.OK, 'data': {'items': pipelineQuery.pipelines}}
