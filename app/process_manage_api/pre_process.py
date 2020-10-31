from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from manage import celery
from app.nlp import preprocess
from app.models.dataset import *
from app.models.operator import *
from app.utils.vector_uitls import *
from app.utils.response_code import *
from app.utils.codehub_utils import *
from app.utils.preprocess_uitls import *

# 预处理类型与文本列数对应表
preprocessTypeMap = {
    '通用单文本分类': ['text1'],
    '情感分析/意图识别': ['text1'],
    '实体关系抽取': ['text1'],
    '文本关系分析': ['text1', 'text2'],
    '文本摘要': ['text1'],
    '文本排序学习': ['text1']
}


# 某个数据集预处理列表获取
@api.route('/pre-process/datasets/ID/preprocesses', methods=['GET'])
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


# 某个数据集新增预处理步骤
@api.route('/pre-process/datasets/ID/preprocesses', methods=['POST'])
@jwt_required
def preprocessAdd():
    # 读取数据
    info = request.json
    datasetID = info.get('datasetid')
    preprocessAdd = info.get('preprocessAdd')
    previousProcessID = int(info.get('previousProcessID'))
    sparkSupport = info.get('sparkSupport')
    preprocessParams = info.get('preprocessParams')
    username = get_jwt_identity()

    # 数据库查询并修改
    datasetQuery = PreprocessDataset.objects(id=int(datasetID)).first()
    if datasetQuery and username == datasetQuery.username:
        previousID = datasetQuery.preprocessStatus[-1]['id']
        datasetQuery.preprocessStatus.append(
            {'id': previousID + 1, 'preprocessName': preprocessAdd[1], 'preprocessType': preprocessAdd[0],
             'previousProcessID': previousProcessID, 'sparkSupport': sparkSupport, 'preprocessStatus': '未开始',
             'preprocessParams': preprocessParams})
        datasetQuery.save()
    return {'code': RET.OK}


# 某个数据集某个预处理向量查看
@api.route('/pre-process/datasets/ID/preprocesses/ID/data', methods=['GET'])
@jwt_required
def preprocessDataFetch():
    # 读取数据
    info = request.values
    datasetID = int(info.get('datasetid'))
    preprocessID = int(info.get('preprocessid'))
    username = get_jwt_identity()

    # 分页
    limit = int(info.get('limit'))
    page = int(info.get('page'))

    # 读取数据库
    datasetQuery = PreprocessDataset.objects(id=datasetID).first()
    if datasetQuery and username == datasetQuery.username:
        count, vectors = vectors_select_divide_preprocess(datasetID, preprocessID, limit, page)
    return {'code': RET.OK, 'data': {'items': vectors, 'total': count}}


# 某个数据集执行某个预处理步骤
@api.route('/pre-process/datasets/ID/preprocesses/ID/status', methods=['PUT'])
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
        preprocessManage.delay(datasetQuery, preprocessIndex)
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
    previousData = getDataFromPreprocessDataset(dataset, previousProcessIndex)
    if preprocessType == '自定义算子':
        code = Operator.objects(operatorName=preprocessName).first().code
        curVectors = operatorRunUtil(code, dataset.id)
    else:
        curData = preprocessDistribute(previousData, preprocessName, params, textType, preprocessType, sparkSupport)
    setDataToPreprocessDataset(dataset, preprocessIndex, preprocessName, preprocessType, curData)

    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '已完成'
    dataset.save()
    return '预处理成功'


# 预处理函数分发
def preprocessDistribute(data, preprocessName, params, textType, preprocessType, sparkSupport):
    # 分发至nlp预处理函数
    if sparkSupport:
        if preprocessName == '分词':
            curData = preprocess.base_methods.cut_spark(data, params, textType, 'local[4]')
        elif preprocessName == '词性标注':
            curData = preprocess.base_methods.postagging_spark(data, params, textType, 'local[4]')
        elif preprocessName == '去停用词':
            stopwordsList = [line.strip() for line in open(r'e:/hit_stopwords.txt', encoding='UTF-8').readlines()]
            curData = preprocess.base_methods.stopwords_spark(data, {'tool': stopwordsList, 'from': '分词'}, textType,
                                                              'local[4]')

    else:
        if preprocessName == '分词':
            curData = preprocess.base_methods.cut(data, params, textType)
        elif preprocessName == '词性标注':
            curData = preprocess.base_methods.postagging(data, params, textType)
        elif preprocessName == '去停用词':
            stopwordsList = [line.strip() for line in open(r'e:/hit_stopwords.txt', encoding='UTF-8').readlines()]
            curData = preprocess.base_methods.stopwords(data, {'tool': stopwordsList, 'from': '分词'},
                                                        textType)
        elif preprocessName == 'Word2vec':
            curData = preprocess.vector_models.Word2vec(data, params, textType)
        elif preprocessName == 'EmbeddingMatrix':
            curData = preprocess.features_construction.EmbeddingMatrix(data, params, textType)
        elif preprocessName == '单标签':
            curData = preprocess.label_encoder.single_label_encoder(data, params, textType)

    return curData

