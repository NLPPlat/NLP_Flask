import copy
import numpy as np
from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from manage import celery, app
from app.models.dataset import *
from app.models.model import *
from app.nlp.batch_process import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.codehub_utils import *
from app.utils.file_utils import *


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
    if datasetQuery and username == datasetQuery.username:
        trainedmodel = TrainedModel.objects(id=trainedModelID).first()
        batchRunManage.delay(datasetQuery, trainedmodel, operatorOn, operatorCode)
    return {'code': RET.OK}


@celery.task
def batchRunManage(dataset, trainedmodel, operatorOn, operatorCode):
    dataset.batchStatus = '处理中'
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
                                    desc=dataset.desc, publicity=dataset.publicity)
        result.save()
        resultID=result.id
        dataset.resultDataset = resultID
        dataset.save()
    else:
        resultID=dataset.resultDataset
        vectors_delete_all(resultID)
    for vector in vectors:
        vector['datasetid'] = resultID
    vectors_insert(data['vectors'], '结果数据集')
    dataset.batchStatus = '处理完成'
    dataset.save()
    return '批处理成功'
