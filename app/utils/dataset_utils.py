import json

from app.models.dataset import *
from app.models.venation import *
from app.utils.vector_uitls import *


# 数据集拷贝
def copy(datasetInit, datasetInitType, copyDes, username, venationInit):
    if datasetInitType == '原始数据集' and copyDes == '原始数据集':
        datasetDes = OriginalDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName, datasetType='原始数据集',
                                     desc=datasetInit.desc, publicity=datasetInit.publicity,
                                     originalFile=datasetInit.originalFile,
                                     analyseStatus=datasetInit.analyseStatus,
                                     annotationStatus=datasetInit.annotationStatus,
                                     annotationFormat=datasetInit.annotationFormat)
        datasetDes.ancestor = datasetDes.id
        vectors=json.loads(vectors_select_all_original(datasetInit.id).to_json())
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
        vectors_insert(vectors)
        datasetNodeDes = DatasetNode(parent=-1, id=datasetDes.id, username=datasetDes.username,
                                     taskName=datasetDes.taskName, taskType=datasetDes.taskType,
                                     datetime=datasetDes.datetime)
        venationDes = Venation(ancestor=datasetDes.id, originalDataset=[datasetNodeDes])
        venationDes.save()


    elif datasetInitType == '原始数据集' and copyDes == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName, datasetType='预处理数据集',
                                       desc=datasetInit.desc, publicity=datasetInit.publicity,
                                       annotationFormat=datasetInit.annotationFormat)
        preprocessObj = PreprocessObject(id=0, preprocessName='原始数据', preprocessType='无')
        datasetDes.data.append(preprocessObj)
        datasetDes.ancestor = datasetInit.ancestor
        vectors=json.loads(vectors_select_all_original(datasetInit.id).to_json())
        for vector in vectors[:]:
            if vector['deleted']=='已删除':
                vectors.remove(vector)
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
            vector['preprocessid']=0
        vectors_insert(vectors,'预处理数据集')
        datasetNodeDes = DatasetNode(parent=datasetInit.id, id=datasetDes.id, username=datasetDes.username,
                                     taskName=datasetDes.taskName, taskType=datasetDes.taskType,
                                     datetime=datasetDes.datetime)
        venationInit.preprocessDataset.append(datasetNodeDes)

    datasetDes.save()
    venationInit.save()
    return datasetDes.id
