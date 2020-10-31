import numpy as np
from sklearn.model_selection import *

from app.models.dataset import *
from app.utils.global_utils import *

def getFeaturesData():
    datasetQuery=FeaturesDataset.objects(id=int(getDataset())).first()
    data=datasetQuery.features
    return data.to_mongo().to_dict()