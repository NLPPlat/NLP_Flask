import copy
import json
import numpy as np

from app.models.dataset import *
from app.models.pipeline import *
from app.utils.vector_uitls import *
from app.utils.common_utils import *

from app.nlp.preprocess import *


# 从数据库中读取向量
def getDataFromPreprocessDataset(dataset, preprocessIndex):
    # 读取数据
    preprocessObj = dataset.data.filter(id=preprocessIndex).first().to_mongo().to_dict()
    vectors = json.loads(vectors_select_all_preprocess(dataset.id, preprocessIndex).to_json())
    # 复制原数据
    newData = copy.deepcopy(preprocessObj)
    newData['vectors'] = vectors
    return newData


# 向量回填数据库
def setDataToPreprocessDataset(dataset, preprocessIndex, preprocessName, preprocessType, data):
    # 存入数据库
    preprocessObj = PreprocessObject(id=preprocessIndex, preprocessName=preprocessName, preprocessType=preprocessType,
                                     feature=data['feature'], embedding=data['embedding'],
                                     embedding_matrix=data['embedding_matrix'], label=data['label'],
                                     label_id=data['label_id'])
    for vector in data['vectors']:
        vector['preprocessid'] = preprocessIndex
    vectors_insert(data['vectors'], '预处理数据集')
    dataset.data.append(preprocessObj)
    dataset.save()
    return


# 返回前端的预处理数据
def getDataForFront(dataset, preprocessID):
    # 读取数据
    preprocessObj = dataset.data.filter(id=preprocessID).first().to_mongo().to_dict()
    preprocessObj['label'] = getFileInfo(preprocessObj['label'])
    preprocessObj['label_id'] = getFileInfo(preprocessObj['label_id'])
    preprocessObj['feature'] = getFileInfo(preprocessObj['feature'])
    preprocessObj['embedding'] = getFileInfo(preprocessObj['embedding'])
    preprocessObj['embedding_matrix'] = getFileInfo(preprocessObj['embedding_matrix'])
    preprocessObj['vocabs'] = getFileInfo(preprocessObj['vocabs'])
    return preprocessObj


# 处理pipeline
def dealPipeline(vectors, pipelineID):
    pipeline = Pipeline.objects(id=pipelineID).first()
    pipelines = pipeline.pipelines
    data = {'vectors': vectors, 'label_id': '', 'label': '', 'embedding': '', 'embedding_matrix': '', 'feature': ''}
    for vector in data['vectors']:
        if 'text1' in vector:
            vector['originalText1'] = vector['text1']
        if 'text2' in vector:
            vector['originalText2'] = vector['text2']
    for preprocess in pipelines:
        data = preprocessManage(preprocess.preprocessType, preprocess.preprocessName, data, preprocess.preprocessParams,
                                pipeline.taskType, -1, -1, preprocess.pipeline)

    return data
