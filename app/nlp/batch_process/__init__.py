from . import batch_process


def batchProcessManage(data, taskType, model, plat, operatorOn, operatorCode):
    if (operatorOn == 'True'):
        pass
    else:
        if (taskType == '通用单文本分类'):
            data = batch_process.classificationBatch(data, model, plat)
    return data
