from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from . import api
from app import models, files

# 数据集列表获取
@api.route('/dataset/list', methods=['GET'])
def datasetListGet():
    list=models.OriginalDataset.objects()
    print('hello world')
    return {'code':200,'data':{'total':len(list),'items':list}}

# 数据详情获取
@api.route('/dataset/detail',methods=['GET'])
def dataDetailGet():
    id=request.args.get('id')
    limit=int(request.args.get('limit'))
    page=int(request.args.get('page'))
    front=limit*(page-1)
    end=limit*page
    text=models.OriginalDataset.objects(id=id).first().text
    res=text.filter()
    return {'code':200,'data':{'items':res[front:end],'total':text.count()}}