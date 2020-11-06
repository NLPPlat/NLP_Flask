import base64
from io import BytesIO
import numpy as np

from app.models.dataset import *
from app.models.model import *
from app.utils.global_utils import *


def getFeatures():
    data = {}
    datasetQuery = FeaturesDataset.objects(id=int(getDataset())).first()
    trainURL = datasetQuery.train.feature
    testURL = datasetQuery.test.feature
    trainLabel = datasetQuery.features.label
    testLabel = datasetQuery.test.label
    label_name = datasetQuery.features.label_name
    data['x_train'] = np.load(trainURL)
    data['x_test'] = np.load(testURL)
    data['y_train'] = np.load(trainLabel)
    data['y_test'] = np.load(testLabel)
    data['label_name'] = label_name
    return data


def saveFig(fig, name):
    sio = BytesIO()
    fig.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    trainModelQuery = TrainedModel.objects(id=getTrainedModel()).first()
    trainModelQuery.figs[name] = src
    trainModelQuery.save()
    return
