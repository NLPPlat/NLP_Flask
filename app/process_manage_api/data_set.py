from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from app import models, files

# 数据集列表获取
@api.route('/dataset/list', methods=['GET'])
def datasetListGet():
    list=models.OriginalDataset.objects()
    return {'code':200,'data':{'total':len(list),'items':list}}


@api.route('/dataset/detail',methods=['GET'])
def dataDetailGet():
    return {'code':200,'data':{'items':[{'label':'hellosddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'},{'label':'dsfe'}]}}