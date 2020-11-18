import json

from manage import celery
from app.models.dataset import *
from app.models.venation import *
from app.utils.vector_uitls import *
from app.utils.common_utils import *
from app.utils.preprocess_uitls import *
from app.utils.venation_utils import *
from app.utils.time_utils import *
from app.utils.task_utils import *


# 数据集拷贝
@celery.task
def copy(taskID,datasetInit, datasetInitType, copyDes, username, venationInit, params={}):
    if datasetInitType == '原始数据集' and copyDes == '原始数据集':
        datasetDes = OriginalDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName, datasetType='原始数据集',
                                     desc=datasetInit.desc, publicity=datasetInit.publicity,
                                     originalFile=datasetInit.originalFile,
                                     analyseStatus=datasetInit.analyseStatus,
                                     annotationStatus=datasetInit.annotationStatus,
                                     annotationFormat=datasetInit.annotationFormat,
                                     datetime=getTime())
        datasetDes.ancestor = datasetDes.id
        vectors = json.loads(vectors_select_all(datasetInit.id).to_json())
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
        vectors_insert(vectors)


    elif datasetInitType == '原始数据集' and copyDes == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName, datasetType='预处理数据集',
                                       desc=datasetInit.desc, publicity=datasetInit.publicity,
                                       annotationFormat=datasetInit.annotationFormat, datetime=getTime())
        preprocessObj = PreprocessObject(id=0, preprocessName='原始数据', preprocessType='无')
        datasetDes.data.append(preprocessObj)
        datasetDes.ancestor = datasetInit.ancestor
        vectors = json.loads(vectors_select_all(datasetInit.id).to_json())
        for vector in vectors[:]:
            if vector['deleted'] == '已删除':
                vectors.remove(vector)
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
            vector['preprocessid'] = 0
        vectors_insert(vectors, '预处理数据集')
        venationParentID = findNodeID('训练数据集', datasetInit.id)
        createNode([venationParentID], '预处理数据集', datasetDes.id)



    elif datasetInitType == '预处理数据集' and copyDes == '特征数据集':
        datasetDes = FeaturesDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName, datasetType='特征数据集',
                                     desc=datasetInit.desc, publicity=datasetInit.publicity, trainStatus='未开始',
                                     datetime=getTime())
        for preprocess in datasetInit.data:
            if preprocess.id == int(params['preprocessid']):
                features = FeaturesObject(label=preprocess.label, label_name=preprocess.label_name,
                                          feature=preprocess.feature, vectors=preprocess.vectors,
                                          embedding=preprocess.embedding,
                                          embedding_matrix=preprocess.embedding_matrix)
                datasetDes.features = features
                datasetDes.featuresShape = getFileShape(features.feature)
                break
        train = FeaturesObject(label_name=datasetDes.features.label_name)
        test = FeaturesObject(label_name=datasetDes.features.label_name)
        datasetDes.train = train
        datasetDes.test = test
        venationParentID = findNodeID('预处理数据集', datasetInit.id)
        createNode([venationParentID], '特征数据集', datasetDes.id)

    elif datasetInitType == '批处理数据集' and copyDes == '批处理特征集':
        datasetDes = FeaturesBatchDataset(username=username, taskType=datasetInit.taskType,
                                          taskName=datasetInit.taskName, datasetType='批处理特征集',
                                          desc=datasetInit.desc, publicity=datasetInit.publicity, batchStatus='未开始',
                                          datetime=getTime())
        vectors = json.loads(vectors_select_all(datasetInit.id).to_json())
        for vector in vectors[:]:
            if vector['deleted'] == '已删除':
                vectors.remove(vector)
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
        data = dealPipeline(vectors, int(params['pipeline']))
        features = FeaturesBatchObject(label=data['label'], label_name=data['label_name'],
                                       embedding_matrix=data['embedding_matrix'], embedding=data['embedding'],
                                       feature=data['feature'])
        vectors_insert(data['vectors'], '批处理特征集')
        datasetDes.features = features
        venationParent1ID = findNodeID('批处理数据集', datasetInit.id)
        venationParent2ID = findNodeID('预处理管道对象', int(params['pipeline']))
        createNode([venationParent1ID, venationParent2ID], '批处理特征集', datasetDes.id)
    datasetDes.save()
    completeTask(taskID)
    # venationInit.save()
    return '拷贝成功'
