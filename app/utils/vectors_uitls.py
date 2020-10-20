from app.models.dataset import *
import json
from app import db

# 预处理数据库与中文步骤映射表
preprocessMap = {
    '原始文本': 'originalData',
    '分词': 'cut',
    '去停用词': 'stopwords',
    '词性标注': 'postagging'
}


# 从数据库中读取向量
def getVectorsFromPreprocessDataset(dataset, preprocessIndex):

    # 读取数据
    vectorsQuery = dataset.data.filter(id=preprocessIndex).first()
    vectors=vectorsQuery.data

    # 转换原向量
    vectorList = []
    for vector in vectors:
        vectorList.append(vector.copy())

    return vectorList


# 向量回填数据库
def setVectorsToPreprocessDataset(dataset, preprocessIndex, vectors):
    # 存入数据库
    preprocessObj=PreprocessObject(id=preprocessIndex)
    preprocessObj.data=[]
    for vector in vectors:
        textContent = TextContent().from_json(json.dumps(vector))
        preprocessObj.data.append(textContent)
    dataset.data.append(preprocessObj)
    dataset.save()

    return
