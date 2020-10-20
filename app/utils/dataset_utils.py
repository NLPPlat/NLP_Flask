from app.models.dataset import *
from app.models.venation import *


# 数据集拷贝
def copy(datasetInit, datasetInitType, copyDes, username, venationInit):
    if datasetInitType == '原始数据集' and copyDes == '原始数据集':
        datasetDes = OriginalDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName, datasetType='原始数据集',
                                     desc=datasetInit.desc, publicity=datasetInit.publicity,
                                     originalFile=datasetInit.originalFile, originalData=datasetInit.originalData,
                                     analyseStatus=datasetInit.analyseStatus,
                                     annotationStatus=datasetInit.annotationStatus,
                                     annotationFormat=datasetInit.annotationFormat)
        datasetDes.ancestor = datasetDes.id
        datasetNodeDes = DatasetNode(parent=-1, id=datasetDes.id, username=datasetDes.username,
                                     taskName=datasetDes.taskName, taskType=datasetDes.taskType,
                                     datetime=datasetDes.datetime)
        venationDes = Venation(ancestor=datasetDes.id, originalDataset=[datasetNodeDes])
        venationDes.save()


    elif datasetInitType == '原始数据集' and copyDes == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName, datasetType='预处理数据集',
                                       desc=datasetInit.desc, publicity=datasetInit.publicity)
        preprocessObj = PreprocessObject(id=0, type='vectors', data=datasetInit.originalData)
        datasetDes.data.append(preprocessObj)
        datasetDes.ancestor = datasetInit.ancestor
        datasetNodeDes = DatasetNode(parent=datasetInit.id, id=datasetDes.id, username=datasetDes.username,
                                     taskName=datasetDes.taskName, taskType=datasetDes.taskType,
                                     datetime=datasetDes.datetime)
        venationInit.preprocessDataset.append(datasetNodeDes)

    datasetDes.save()
    venationInit.save()
    return datasetDes.id
