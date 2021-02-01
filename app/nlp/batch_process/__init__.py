from . import batch_process
from app.models.model import *
from app.utils.codehub_utils import *



def batchProcessManage(data, taskType, trainedModelID, operatorOn, operatorCode, datasetID):
    if (operatorOn == 'True'):
        data = operatorRunUtil(operatorCode, datasetID)
    else:
        trainedmodel=TrainedModel.objects(id=int(trainedModelID)).first()
        model = trainedmodel.model
        platType = trainedmodel.platType
        if (taskType == '通用单文本分类'):
            data = batch_process.classificationBatch(data, model, platType)
    return data
