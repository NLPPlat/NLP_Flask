from app.utils.preprocess_uitls import *
from app.utils.global_utils import *


def getPreprocessData(id=-1):
    datasetQuery = PreprocessDataset.objects(id=int(getDataset())).first()
    data = getDataFromPreprocessDataset(datasetQuery, id)
    return data
