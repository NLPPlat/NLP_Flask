import json

from manage import celery
from .data_vector import *
from app.nlp import preprocess

# 预处理类型与文本列数对应表
preprocessTypeMap = {
    '通用单文本分类': ['text1'],
    '情感分析/意图识别': ['text1'],
    '实体关系抽取': ['text1'],
    '文本关系分析': ['text1', 'text2'],
    '文本摘要': ['text1'],
    '文本排序学习': ['text1']
}


# 预处理控制层
@celery.task
def preprocessManage(dataset, preprocessIndex):
    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '执行中'
    dataset.save()

    # 步骤、参数读取
    previousProcess = dataset.preprocessStatus[preprocessIndex - 1]['preprocessName']
    curProcess = dataset.preprocessStatus[preprocessIndex]['preprocessName']
    sparkSupport = dataset.preprocessStatus[preprocessIndex]['sparkSupport']
    params = dataset.preprocessStatus[preprocessIndex]['preprocessParams']
    textType = preprocessTypeMap[dataset.taskType]

    # 控制函数调用
    previousVectors = getVectorsFromPreprocessDataset(dataset, previousProcess)
    curVectors = preprocessDistribute(previousVectors, curProcess, params, textType, sparkSupport)
    setVectorsToreprocessDataset(dataset, curProcess, curVectors)

    # 数据库状态更改
    dataset.preprocessStatus[preprocessIndex]['preprocessStatus'] = '已完成'
    dataset.save()
    return '预处理成功'


# 预处理函数分发
def preprocessDistribute(vectors, preprocessName, params, textType, sparkSupport):
    # 转换原向量
    vectorList = []
    for vector in vectors:
        vectorList.append(json.loads(vector.to_json()))

    # 分发至nlp预处理函数
    if sparkSupport:
        pass
    else:
        if preprocessName == '分词':
            curVectors = preprocess.base_methods.cut(vectorList,params,textType)

    return curVectors
