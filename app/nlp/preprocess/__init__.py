from . import base_methods
from . import vector_models
from . import features_construction
from . import label_encoder

from app.models.operator import *
from app.utils.codehub_utils import *

# 预处理类型与文本列数对应表
preprocessTypeMap = {
    '通用单文本分类': ['text1'],
    '情感分析/意图识别': ['text1'],
    '实体关系抽取': ['text1'],
    '文本关系分析': ['text1', 'text2'],
    '文本匹配': ['text1'],
    '文本摘要': ['text1'],
    '文本排序学习': ['text1']
}


def preprocessManage(preprocessType, preprocessName, data, params, taskType, datasetID=-1, master=-1, pipeline=-1):
    if pipeline != -1:
        for key in pipeline:
            data[key] = pipeline[key]
    else:
        type = preprocessTypeMap[taskType]
        if preprocessType == '基本预处理':
            if preprocessName == '分词':
                data = cut(data, params, type, master=-1)
            elif preprocessName == '词性标注':
                data = postagging(data, params, type, master=-1)
            elif preprocessName == '去停用词':
                data = stopwords(data, params, type, master=-1)

        elif preprocessType == '向量模型':
            if preprocessName == 'Word2vec':
                data = vector_models.Word2vec(data, params, type)

        elif preprocessType == '特征生成':
            if preprocessName == '序列化':
                data = features_construction.padSequence(data, params, type)
            elif preprocessName == 'EmbeddingMatrix':
                data = features_construction.EmbeddingMatrix(data, params, type)

        elif preprocessType == '标签映射':
            if preprocessName == '单标签数值映射':
                data = label_encoder.single_label_encoder(data, params, type)
            elif preprocessName == '序列BIO':
                data = label_encoder.BIO_label_encoder(data, params, type)

        elif preprocessType == '自定义算子':
            code = Operator.objects(operatorName=preprocessName).first().code
            data = operatorRunUtil(code, datasetID)

    return data


def cut(data, params, type, master=-1):
    if master == -1:
        data = base_methods.cut(data, params, type)
    else:
        data = base_methods.cut_spark(data, params, type, master)
    return data


def postagging(data, params, type, master=-1):
    if master == -1:
        data = base_methods.postagging(data, params, type)
    else:
        data = base_methods.postagging_spark(data, params, type, master)
    return data


def stopwords(data, params, type, master=-1):
    stopwordsList = [line.strip() for line in open(r'e:/hit_stopwords.txt', encoding='UTF-8').readlines()]
    if master == -1:
        data = base_methods.stopwords(data, {'tool': stopwordsList, 'from': '分词'}, type)
    else:
        data = base_methods.stopwords_spark(data, {'tool': stopwordsList, 'from': '分词'}, type, master)
    return data
