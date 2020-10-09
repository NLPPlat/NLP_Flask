from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from . import api
from app import models, files
from app.utils.response_code import RET

#数据集拷贝
@api.route('/dataset/dataset', methods=['POST'])
@jwt_required
def datasetCopy():
    # 读取数据
    info=request.json
    datasetInitType=info.get('datasetInitType')
    datasetInitID=info.get('datasetInitid')
    copyDes=info.get('copyDes')
    # 读取原数据集
    if datasetInitType=='原始数据集':
        datasetInit=models.OriginalDataset.objects(id=int(datasetInitID)).first()
    # 拷贝判断
    if datasetInitType=='原始数据集' and copyDes=='原始数据集':
        datasetDes=models.OriginalDataset()
    return {'code':RET.OK}