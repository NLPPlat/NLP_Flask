from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.models.dataset import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.common_utils import *


# 某个数据集某条向量更新
@api.route('/dataset/datasets/ID/vectors/ID', methods=['PUT'])
@jwt_required
def editDataVector():
    # 读取基本数据
    info = request.values
    datasetID = int(info.get("datasetid"))
    vectorID = int(info.get('vectorid'))
    vector = info.get('vector')
    username = get_jwt_identity()

    # 数据格式转换
    vectorDict = json.loads(vector)
    if 'edit' in vectorDict:
        vectorDict.pop('edit')

    # 数据库修改
    vector_update(datasetID, vectorID, vectorDict)
    return {'code': 200}


# 数据集拆分
@api.route('/dataset/datasets/ID/vectors', methods=['PATCH'])
@jwt_required
def dataCut():
    # 读取基本数据
    info = request.json
    datasetID = int(info.get('datasetid'))
    level = info.get('level')
    tool = info.get('tool')
    username = get_jwt_identity()

    # 数据库查询及修改
    datasetQuery = OriginalDataset.objects(id=datasetID).first()
    if datasetQuery and username == datasetQuery.username:
        curVectors = dataCutService(vectors_select_all_original(datasetID))
        vectors_delete_all(datasetID)
        vectors_insert(curVectors)
        datasetQuery.groupOn = 'on'
        datasetQuery.save()
    return {'code': RET.OK}


# 数据集拆分服务实现
def dataCutService(previousVectors):
    curVectors = []
    id = 0
    for previousVector in previousVectors:
        sentences = sentenceCut(previousVector.text1)
        for sentence in sentences:
            curVector = {}
            curVector['vectorid'] = id
            curVector['datasetid'] = previousVector.datasetid
            curVector['group'] = previousVector.vectorid
            curVector['text1'] = sentence
            curVector['deleted'] = previousVector.deleted
            if 'title' in previousVector:
                curVector['title'] = previousVector.title
            curVectors.append(curVector)
            id = id + 1
    return curVectors
