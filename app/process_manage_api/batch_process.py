from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery
from app.nlp.batch_process import *
from app.utils.vector_uitls import *
from app.utils.venation_utils import *
from app.utils.task_utils import *
from app.utils.permission_utils import *


# 某个训练模型代码运行
@api.route('/batch-process/batch-datasets/ID/code', methods=['PUT'])
@jwt_required
def batchRun():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    trainedModelID = int(info.get('trainedmodelSelect'))
    operatorOn = str(info.get('operatorOn'))
    if (operatorOn == 'Ture'):
        operatorCode = info.get('code')
    else:
        operatorCode = ''
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = FeaturesBatchDataset.objects(id=datasetID).first()
    if not writePermission(datasetQuery, username):
        return noPeimissionReturn()
    trainedmodel = TrainedModel.objects(id=trainedModelID).first()
    # 创建任务
    taskID = createTask('批处理-' + datasetQuery.taskName, '批处理', datasetQuery.id, datasetQuery.taskName,
                        username)
    batchRunManage.delay(taskID,datasetQuery, trainedmodel, operatorOn, operatorCode)
    return {'code': RET.OK}


@celery.task
def batchRunManage(taskID,dataset, trainedmodel, operatorOn, operatorCode):
    dataset.batchStatus = '处理中'
    dataset.begintime=getTime()
    dataset.save()
    taskType = dataset.taskType
    model = trainedmodel.model
    plat = trainedmodel.plat
    features = dataset.features.to_mongo().to_dict()
    vectors = json.loads(vectors_select_all(dataset.id).to_json())
    features['vectors'] = vectors
    data = batchProcessManage(features, taskType, model, plat, operatorOn, operatorCode)
    if dataset.resultDataset == -1:
        result = ResultBatchDataset(username=dataset.username, taskType=dataset.taskType,
                                    taskName=dataset.taskName, datasetType='结果数据集',
                                    desc=dataset.desc, publicity=dataset.publicity,datetime=getTime())
        result.save()
        resultID=result.id
        dataset.resultDataset = resultID
        dataset.save()
    #     创建数据脉络
        venationParent1ID = findNodeID('批处理特征集', dataset.id)
        venationParent2ID = findNodeID('训练模型对象', trainedmodel.id)
        createNode([venationParent1ID, venationParent2ID], '结果数据集', result.id)
    else:
        resultID=dataset.resultDataset
        vectors_delete_all(resultID)
    for vector in vectors:
        vector['datasetid'] = resultID
    vectors_insert(data['vectors'], '结果数据集')
    dataset.batchStatus = '处理完成'
    dataset.endtime=getTime()
    dataset.save()
    completeTask(taskID)
    return '批处理成功'
