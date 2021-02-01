import json

from app.models.model import *
from app.models.dataset import *
from app.utils.common_utils import *
from app.utils.global_utils import *
from app.utils.vector_uitls import *


def getBatchData():
    datasetQuery = FeaturesBatchDataset.objects(id=int(getDataset())).first()
    data = datasetQuery.features
    data.to_mongo().to_dict()
    vectors = json.loads(vectors_select_all(int(getDataset())).to_json())
    data['vectors'] = vectors
    if type == 0:
        data['feature'] = getFileContent(data['feature'])
        data['label'] = getFileContent(data['label'])
        data['embedding_matrix'] = getFileContent(data['embedding_matrix'])
    return data.to_mongo().to_dict()

def getTrainedModel(modelName):
    model = TrainedModel.objects(modelName=modelName).first()
    return model.model
