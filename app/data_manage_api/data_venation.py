from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app.utils.response_code import RET
from app.utils.file_utils import fileDelete
from app.models.dataset import *
from app.models.venation import *


# 数据脉络获取
@api.route('/venation', methods=['GET'])
@jwt_required
def datasetListFetch():
    # 读取基本数据
    info = request.values
    datasetID = info.get('datasetid')
    username = get_jwt_identity()

    # 查询数据库，寻找脉络
    datasetQuery = Dataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        # 读取基本数据
        ancestor = datasetQuery.ancestor
        datasetType = datasetQuery.datasetType
        venation = Venation.objects(ancestor=ancestor).first()

        # 查找节点脉络
        if datasetType == '原始数据集':
            originalDatasetNodes = getDatasetNodes(datasetID, '原始数据集', venation)
            preprocessDatasetNodes = getChildrenNodes(datasetID,'预处理数据集',venation)
        if datasetType == '预处理数据集':
            preprocessDatasetNodes=getDatasetNodes(datasetID, '预处理数据集', venation)
            originalDatasetNodes=getDatasetNodes(preprocessDatasetNodes[0].parent,'原始数据集',venation)

        # 写入脉络
        partOfVenation = {'原始数据集': [], '预处理数据集': []}
        partOfVenation['原始数据集']=originalDatasetNodes
        partOfVenation['预处理数据集']=preprocessDatasetNodes

    return {'code': RET.OK,'data':{'venation':partOfVenation}}


# 获取节点
def getDatasetNodes(datasetID, datasetType, venation):
    if datasetType == '原始数据集':
        return venation.originalDataset.filter(id=datasetID)
    elif datasetType == '预处理数据集':
        return venation.preprocessDataset.filter(id=datasetID)
    return

# 获取子节点
def getChildrenNodes(parentID, datasetType, venation):
    if datasetType =='预处理数据集':
        return venation.preprocessDataset.filter(parent=parentID)
    return
