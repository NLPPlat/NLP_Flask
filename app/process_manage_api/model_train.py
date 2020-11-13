import copy
import numpy as np
from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from manage import celery, app
from app.models.dataset import *
from app.models.model import *
from app.nlp.model_train import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.codehub_utils import *
from app.utils.file_utils import *


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
    if datasetQuery and username == datasetQuery.username:
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
    if datasetQuery and datasetQuery.username == username:
        trainedModel = TrainedModel(username=username, baseModelID=modelSelect, modelName=modelName,
                                    modelParams=paramsFetchUtil(code), code=code, plat=modelQuery.plat)
        trainedModel.save()
        datasetQuery.model = trainedModel.id
        datasetQuery.modelStatus = '已完成'
        datasetQuery.save()
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
    trainedmodelQuery = TrainedModel.objects(id=trainedmodelID).first()
    if trainedmodelQuery and username == trainedmodelQuery.username:
        trainedmodelQuery.code = code
        print(paramsFetchUtil(code))
        trainedmodelQuery.modelParams = paramsFetchUtil(code)
        trainedmodelQuery.save()
    return {'code': RET.OK}


# 某个训练模型代码运行
@api.route('/model-train/trainedmodels/ID/model', methods=['PUT'])
@jwt_required
def trainedModelRun():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    trainedModelID = int(info.get('trainedmodelid'))
    username = get_jwt_identity()
    # 数据库查询
    trainedModelQuery = TrainedModel.objects(id=trainedModelID).first()
    if trainedModelQuery and username == trainedModelQuery.username:
        trainedModelQuery.trainStatus = '训练中'
        trainedModelQuery.save()
        trainedModelRuntask.delay(trainedModelQuery, datasetID)
    return {'code': RET.OK}


# 异步训练模型
@celery.task
def trainedModelRuntask(trainedModelQuery, datasetID):
    result, model = modelRunUtil(trainedModelQuery.code, datasetID, trainedModelQuery.id)
    if model != None:
        modelURL = getFileURL('model.h5', app)
        model.save(modelURL)
        trainedModelQuery.model = modelURL
    trainedModelQuery.result = result
    trainedModelQuery.trainStatus = '已完成'
    trainedModelQuery.save()
    print(trainedModelQuery.trainStatus)
    return '模型训练成功'
