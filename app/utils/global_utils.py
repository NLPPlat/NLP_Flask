datasetid = -1
trainedModelID = -1


def setDataset(x):
    global datasetid
    datasetid = x


def getDataset():
    global datasetid
    return datasetid


def setTrainedModel(x):
    global trainedModelID
    trainedModelID = x


def getTrainedModel():
    global trainedModelID
    return trainedModelID
