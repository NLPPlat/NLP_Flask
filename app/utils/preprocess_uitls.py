import copy
import json

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
                                     matrix=data['matrix'], url=data['url'], label=data['label'],
                                     label_name=data['label_name'])
    for vector in data['vectors']:
        vector['preprocessid'] = preprocessIndex
    vectors_insert(data['vectors'], '预处理数据集')
    dataset.data.append(preprocessObj)
    dataset.save()
    return
