from app.models.dataset import *


def copy(datasetInit, datasetInitType, copyDes, username):
    if datasetInitType == '原始数据集' and copyDes == '原始数据集':
        datasetDes = OriginalDataset(username=username, taskType=datasetInit.taskType,
                                     taskName=datasetInit.taskName,
                                     desc=datasetInit.desc, publicity=datasetInit.publicity,
                                     originalFile=datasetInit.originalFile, originalData=datasetInit.originalData,
                                     analyseStatus=datasetInit.analyseStatus,
                                     annotationStatus=datasetInit.annotationStatus,
                                     annotationFormat=datasetInit.annotationFormat)

    elif datasetInitType == '原始数据集' and copyDes == '预处理数据集':
        datasetDes = PreprocessDataset(username=username, taskType=datasetInit.taskType,
                                       taskName=datasetInit.taskName,
                                       desc=datasetInit.desc, publicity=datasetInit.publicity,
                                       originalData=datasetInit.originalData)
    datasetDes.save()
    return
