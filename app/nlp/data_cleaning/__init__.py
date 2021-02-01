from app.utils.codehub_utils import *


def dataCleaningManage(datasetID, vectors, code):
    vectors = operatorRunUtil(code, datasetID)
    return vectors
