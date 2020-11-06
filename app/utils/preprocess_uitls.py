import copy
import json
import numpy as np

from app.models.dataset import *
from app.utils.vector_uitls import *


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
                                     feature=data['feature'], embedding=data['embedding'], label=data['label'],
                                     label_name=data['label_name'])
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
    if preprocessObj['label'] != '':
        if preprocessObj['label'].split('.')[-1]=='npy':
            label = np.load(preprocessObj['label'])
            preprocessObj['label'] = label.shape
        elif preprocessObj['label'].split('.')[-1]=='txt':
            pass
    if preprocessObj['feature'] != '':
        feature = np.load(preprocessObj['feature'])
        preprocessObj['feature'] = feature.shape
    return preprocessObj
