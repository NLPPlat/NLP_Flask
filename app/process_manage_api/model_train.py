from flask import request, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery, app
from app.nlp.model_train import *
from app.utils.codehub_utils import *
from app.utils.file_utils import *
from app.utils.venation_utils import *
from app.utils.task_utils import *
from app.utils.permission_utils import *


# 某个数据集特征修改
@api.route('/model-train/datasets/ID/features', methods=['PATCH'])
@jwt_required
def featuresSplit():
    # 读取数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    stratify = info.get('stratify')
    trainRate = float(info.get('trainRate'))
    skip = info.get('skip')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = FeaturesDataset.objects(id=datasetID).first()
    if not writePermission(datasetQuery, username):
        return noPeimissionReturn()
    if skip == '不跳过':
        features_split.features_split(datasetQuery, stratify, trainRate)
        featuresUpdate(datasetQuery)
        datasetQuery.trainRate = trainRate
        datasetQuery.splitStratify = stratify
    datasetQuery.splitStatus = '已完成'
    datasetQuery.save()
    return {'code': RET.OK}


def featuresUpdate(dataset):
    x_train = np.load(dataset.train.feature)
    x_test = np.load(dataset.test.feature)
    dataset.trainShape = x_train.shape
    dataset.testShape = x_test.shape
    return


# 某个数据集模型修改
@api.route('/model-train/datasets/ID/model', methods=['PUT'])
@jwt_required
def modelUpdate():
    # 读取数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    modelSelect = int(info.get('modelSelect'))
    modelName = info.get('modelName')
    code = info.get('code')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = FeaturesDataset.objects(id=datasetID).first()
    modelQuery = BaseModel.objects(id=modelSelect).first()
    if not writePermission(datasetQuery, username):
        return noPeimissionReturn()
    trainedModel = TrainedModel(username=username, baseModelID=modelSelect, baseDatasetID=datasetID,
                                modelName=modelName,
                                modelParams=paramsFetchUtil(code), code=code, platType=modelQuery.platType)
    trainedModel.save()
    datasetQuery.model = trainedModel.id
    datasetQuery.modelStatus = '已完成'
    datasetQuery.save()
    #     创建数据脉络
    venationParent1ID = findNodeID('特征数据集', datasetID)
    createNode([venationParent1ID], '训练模型对象', trainedModel.id)
    return {'code': RET.OK}


# 某个训练模型代码修改
@api.route('/model-train/trainedmodels/ID/code', methods=['PUT'])
@jwt_required
def codeUpdate():
    # 读取基本数据
    info = request.json
    trainedmodelID = int(info.get('trainedmodelid'))
    code = info.get('code')
    username = get_jwt_identity()

    # 数据库读取
    trainedModelQuery = TrainedModel.objects(id=trainedmodelID).first()
    if not writePermission(trainedModelQuery, username):
        return noPeimissionReturn()
    trainedModelQuery.code = code
    trainedModelQuery.modelParams = paramsFetchUtil(code)
    trainedModelQuery.save()
    return {'code': RET.OK}


# 某个训练模型下载
@api.route('/model-train/trainedmodels/ID/model', methods=['GET'])
@jwt_required
def trainedModelDownload():
    # 读取数据
    info = request.values
    trainedModelID = int(info.get('trainedmodelid'))
    username = get_jwt_identity()

    # 文件导出
    trainedModel = TrainedModel.objects(id=trainedModelID).first()
    if not readPermission(trainedModel, username):
        return noPeimissionReturn()
    url = trainedModel.model
    response = make_response(send_file(url))
    response.headers['content-disposition'] = url.split('___')[-1]
    response.headers['Access-Control-Expose-Headers'] = 'content-disposition'
    return response


# 某个训练模型代码运行
@api.route('/model-train/trainedmodels/ID/model', methods=['PUT'])
@jwt_required
def trainedModelRun():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    trainedModelID = int(info.get('trainedmodelid'))
    modelParams = info.get('modelParams')
    username = get_jwt_identity()

    # 数据库查询
    trainedModelQuery = TrainedModel.objects(id=trainedModelID).first()
    if not writePermission(trainedModelQuery, username):
        return noPeimissionReturn()
    datasetQuery = FeaturesDataset.objects(id=datasetID).first()
    datasetQuery.trainStatus = '训练中'
    trainedModelQuery.trainStatus = '训练中'
    trainedModelQuery.modelParams = modelParams
    trainedModelQuery.datetime = getTime()
    trainedModelQuery.save()
    datasetQuery.save()
    # 创建任务
    taskID = createTask('模型训练-' + trainedModelQuery.modelName, '模型训练', trainedModelQuery.id,
                        trainedModelQuery.modelName,
                        username)
    trainedModelRuntask.delay(taskID, trainedModelQuery, datasetQuery)
    return {'code': RET.OK}


# 异步训练模型
@celery.task
def trainedModelRuntask(taskID, trainedModelQuery, datasetQuery):
    result, model = modelRunUtil(trainedModelQuery.code, datasetQuery.id, trainedModelQuery.id)
    if model != None:
        modelURL = getFileURL('model.h5', app)
        model.save(modelURL)
        trainedModelQuery.model = modelURL
    trainedModelQuery.result = result
    trainedModelQuery.trainStatus = '已完成'
    datasetQuery.trainStatus = '已完成'
    trainedModelQuery.endtime = getTime()
    trainedModelQuery.save()
    datasetQuery.save()
    completeTask(taskID)
    return '模型训练成功'
