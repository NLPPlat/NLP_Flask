from app.models.dataset import *
from app.utils.preprocess_uitls import *
from app.utils.global_utils import *


def getPreprocessData(preprocessID):
    datasetQuery=PreprocessDataset.objects(id=int(getDataset())).first()
    data=getDataFromPreprocessDataset(datasetQuery, preprocessID)
    return data