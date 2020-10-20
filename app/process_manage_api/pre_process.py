from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json

from manage import celery
from . import api
from app.utils.response_code import RET
from app import models, files
from app.models.dataset import *
from app.models.operator import *
from app.utils.vectors_uitls import *
from app.nlp import preprocess
from app.utils.code_run_utils import codeRunUtil

# 预处理类型与文本列数对应表
preprocessTypeMap = {
    '通用单文本分类': ['text1'],
    '情感分析/意图识别': ['text1'],
    '实体关系抽取': ['text1'],
    '文本关系分析': ['text1', 'text2'],
    '文本摘要': ['text1'],
    '文本排序学习': ['text1']
}


# 预处理状态获取
@api.route('/pre-process/preprocess', methods=['GET'])
@jwt_required
def preprocessStatusFetch():
    # 读取数据
    info = request.values
    datasetID = info.get('datasetid')
    username = get_jwt_identity()

    # 数据库查询
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        pass
    return {'code': RET.OK, 'data': {'items': datasetQuery.preprocessStatus}}


# 新增预处理步骤
@api.route('/pre-process/preprocess/id', methods=['POST'])
@jwt_required
def preprocessAdd():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessAdd = info.get('preprocessAdd')
    previousProcessID=int(info.get('previousProcessID'))
    sparkSupport = info.get('sparkSupport')
    preprocessParams = info.get('preprocessParams')
    username = get_jwt_identity()

    # 数据库查询并修改
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        print(datasetQuery.preprocessStatus)
        previousID=datasetQuery.preprocessStatus[-1]['id']
        datasetQuery.preprocessStatus.append({'id':previousID+1,'preprocessName':preprocessAdd[1],'preprocessType':preprocessAdd[0],'previousProcessID':previousProcessID,'sparkSupport':sparkSupport,'preprocessStatus':'未开始','preprocessParams':preprocessParams})
        datasetQuery.save()
    return {'code':RET.OK}


# 预处理结果数据获取
@api.route('/pre-process/preprocess/ID/data', methods=['GET'])
@jwt_required
def preprocessDataFetch():
    # 读取数据
    info = request.values
    datasetID = info.get('datasetid')
    preprocessID=int(info.get('preprocessid'))
    username = get_jwt_identity()

    # 分页
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    front = limit * (page - 1)
    end = limit * page

    # 读取数据库
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        vectors = getVectorsFromPreprocessDataset(datasetQuery, preprocessID)
    return {'code':RET.OK,'data':{'items': vectors[front:end], 'total': len(vectors)}}


# 执行预处理步骤
@api.route('/pre-process/preprocess/id', methods=['PUT'])
@jwt_required
def preprocessDeal():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessIndex = info.get('preprocessIndex')
    username = get_jwt_identity()

    # 数据库查询修改、异步处理任务
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        preprocessManage.delay(datasetQuery,preprocessIndex)
    return {'code': RET.OK}


# 预处理控制层
@celery.task
def preprocessManage(dataset, preprocessIndex):
    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '执行中'
    dataset.save()

    # 步骤、参数读取
    previousProcessIndex = dataset.preprocessStatus[preprocessIndex]['previousProcessID']
    preprocessName = dataset.preprocessStatus[preprocessIndex]['preprocessName']
    preprocessType = dataset.preprocessStatus[preprocessIndex]['preprocessType']
    sparkSupport = dataset.preprocessStatus[preprocessIndex]['sparkSupport']
    params = dataset.preprocessStatus[preprocessIndex]['preprocessParams']
    textType = preprocessTypeMap[dataset.taskType]

    # 控制函数调用
    previousVectors = getVectorsFromPreprocessDataset(dataset, previousProcessIndex)
    if preprocessType=='自定义算子':
        code=Operator.objects(operatorName=preprocessName).first().code
        curVectors=codeRunUtil(code,dataset.id)
    else:
        curVectors = preprocessDistribute(previousVectors, preprocessName, params, textType, preprocessType,sparkSupport)
    setVectorsToPreprocessDataset(dataset, preprocessIndex, curVectors)

    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '已完成'
    dataset.save()
    return '预处理成功'


# 预处理函数分发
def preprocessDistribute(vectors, preprocessName, params, textType, preprocessType,sparkSupport):

    # 分发至nlp预处理函数
    if sparkSupport:
        if preprocessName == '分词':
            curVectors = preprocess.base_methods.cut_spark(vectors, {'tool': 'jieba'}, textType,'local[4]')
        elif preprocessName =='词性标注':
            curVectors = preprocess.base_methods.postagging_spark(vectors, {'tool': 'jieba'}, textType,'local[4]')
        elif preprocessName=='去停用词':
            stopwordsList = [line.strip() for line in open(r'e:/hit_stopwords.txt', encoding='UTF-8').readlines()]
            curVectors = preprocess.base_methods.stopwords_spark(vectors, {'tool':stopwordsList,'from': '分词'}, textType,'local[4]')

    else:
        if preprocessName == '分词':
            curVectors = preprocess.base_methods.cut(vectors,{'tool':'jieba'},textType)
        elif preprocessName == '词性标注':
            curVectors = preprocess.base_methods.postagging(vectors, {'tool': 'jieba'}, textType)
        elif preprocessName == '去停用词':
            stopwordsList = [line.strip() for line in open(r'e:/hit_stopwords.txt', encoding='UTF-8').readlines()]
            curVectors = preprocess.base_methods.stopwords(vectors, {'tool': stopwordsList, 'from': '分词'},
                                                                 textType)

    return curVectors