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


# 数据集拷贝管理
def copyManage(datasetInit, datasetDesType, username, params={}):
    # 创建任务
    taskID = createTask('数据集拷贝-' + datasetInit.taskName, '数据集拷贝', datasetInit.id, datasetInit.taskName,
                        username)
    # 分发数据集信息拷贝
    if datasetInit.datasetType == datasetDesType:
        datasetDes = copyMyself(datasetInit, username, params)
    else:
        datasetDes = copyFromOther(datasetInit, datasetDesType, username, params)
    # 数据脉络注册
    venationRegister(datasetInit, datasetDes, params)
    # 异步执行数据拷贝
    copyVectors.delay(taskID, datasetInit, datasetDes, params)
    return datasetDes.id


# 数据脉络注册
def venationRegister(datasetInit, datasetDes, params):
    # 自拷贝数据脉络节点创建
    if datasetInit.datasetType == datasetDes.datasetType:
        venationBrotherID = findNodeID(datasetInit.datasetType, datasetInit.id)
        createNode(findParents(venationBrotherID), datasetDes.datasetType, datasetDes.id)
    # 他拷贝数据脉络节点创建
    else:
        venationParentID = findNodeID(datasetInit.datasetType, datasetInit.id)
        if datasetDes.datasetType == '批处理特征集':
            venationParent2ID = findNodeID('预处理管道对象', int(params['pipeline']))
            createNode([venationParentID, venationParent2ID], datasetDes.datasetType, datasetDes.id)
        else:
            createNode([venationParentID], datasetDes.datasetType, datasetDes.id)
    return


# 自拷贝（相同数据类型拷贝）
def copyMyself(datasetInit, username, params):
    # 按类别拷贝
    if datasetInit.datasetType == '训练数据集':
        datasetDes = OriginalDataset(username=username, taskType=datasetInit.taskType, taskName=datasetInit.taskName,
                                     datasetType=datasetInit.datasetType, desc=datasetInit.desc,
                                     publicity=datasetInit.publicity, originalFile=datasetInit.originalFile,
                                     analyseStatus='解析中',
                                     annotationStatus=datasetInit.annotationStatus,
                                     annotationFormat=datasetInit.annotationFormat, datetime=getTime())
    elif datasetInit.datasetType == '批处理数据集':
        datasetDes = OriginalBatchDataset(username=username, taskType=datasetInit.taskType,
                                          taskName=datasetInit.taskName,
                                          datasetType=datasetInit.datasetType, desc=datasetInit.desc,
                                          publicity=datasetInit.publicity, originalFile=datasetInit.originalFile,
                                          analyseStatus='解析中', datetime=getTime())
    elif datasetInit.datasetType == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName,
                                       datasetType=datasetInit.datasetType, desc=datasetInit.desc,
                                       data=datasetInit.data, publicity=datasetInit.publicity, analyseStatus='解析中',
                                       preprocessStatus=datasetInit.preprocessStatus, datetime=getTime())
    datasetDes.save()
    return datasetDes


# 他拷贝（不同数据类型拷贝）
def copyFromOther(datasetInit, datasetDesType, username, params):
    # 按类别拷贝
    if datasetInit.datasetType == '训练数据集' and datasetDesType == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName, datasetType=datasetDesType,
                                       desc=datasetInit.desc, publicity=datasetInit.publicity,
                                       annotationFormat=datasetInit.annotationFormat, datetime=getTime(),
                                       analyseStatus='解析中')
        preprocessObj = PreprocessObject(id=0, preprocessName='原始数据', preprocessType='无')
        datasetDes.data.append(preprocessObj)

    if datasetInit.datasetType == '预处理数据集' and datasetDesType == '特征数据集':
        datasetDes = FeaturesDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName, datasetType=datasetDesType,
                                     desc=datasetInit.desc, publicity=datasetInit.publicity, trainStatus='未开始',
                                     datetime=getTime(), analyseStatus='解析中')

    if datasetInit.datasetType == '批处理数据集' and datasetDesType == '批处理特征集':
        datasetDes = FeaturesBatchDataset(username=username, taskType=datasetInit.taskType,
                                          taskName=datasetInit.taskName, datasetType=datasetDesType,
                                          desc=datasetInit.desc, publicity=datasetInit.publicity, batchStatus='未开始',
                                          datetime=getTime(), analyseStatus='解析中')
    datasetDes.save()
    return datasetDes


# 拷贝向量
@celery.task
def copyVectors(taskID, datasetInit, datasetDes, params):
    vectors = json.loads(vectors_select_all(datasetInit.id).to_json())

    # 按类别拷贝
    if datasetDes.datasetType == '训练数据集' or datasetDes.datasetType == '批处理数据集':
        for vector in vectors:
            vector['datasetid'] = datasetDes.id
        vectors_insert(vectors, datasetDes.datasetType)

    elif datasetDes.datasetType == '预处理数据集':
        for vector in vectors[:]:
            if vector['deleted'] == '已删除':
                vectors.remove(vector)
        for vector in vectors:
            if datasetInit.datasetType == '训练数据集':
                vector['preprocessid'] = 0
            vector['datasetid'] = datasetDes.id
        vectors_insert(vectors, '预处理数据集')

    elif datasetDes.datasetType == '特征数据集':
        if 'preprocessid' not in params:
            params['preprocessid'] = datasetInit.data[-1].id
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

    elif datasetDes.datasetType == '批处理特征集':
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

    datasetDes.analyseStatus = '解析完成'
    datasetDes.save()
    completeTask(taskID)
    return '拷贝成功！'
