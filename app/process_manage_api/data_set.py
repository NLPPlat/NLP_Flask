from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from app.utils.vector_uitls import *
from app.utils.common_utils import *
from app.utils.permission_utils import *


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
    if not writePermission(datasetQuery, username):
        return noPeimissionReturn()
    curVectors = dataCutService(vectors_select_all(datasetID))
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
