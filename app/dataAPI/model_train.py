import base64
from io import BytesIO

from app.models.dataset import *
from app.models.model import *
from app.utils.global_utils import *
from app.utils.common_utils import *


# 获得训练数据
def getAllData(type=0):
    datasetQuery = FeaturesDataset.objects(id=int(getDataset())).first()
    data = datasetQuery.features
    data.to_mongo().to_dict()
    if type == 0:
        data['feature'] = getFileContent(data['feature'])
        data['label'] = getFileContent(data['label'])
        data['embedding_matrix'] = getFileContent(data['embedding_matrix'])
    return data.to_mongo().to_dict()


# 获得训练集和测试集
def getTrainAndTest():
    data = {}
    datasetQuery = FeaturesDataset.objects(id=int(getDataset())).first()
    trainURL = datasetQuery.train.feature
    testURL = datasetQuery.test.feature
    trainLabel = datasetQuery.features.label
    testLabel = datasetQuery.test.label
    label_id = datasetQuery.features.label_id
    data['x_train'] = np.load(trainURL)
    data['x_test'] = np.load(testURL)
    data['y_train'] = np.load(trainLabel)
    data['y_test'] = np.load(testLabel)
    data['label_id'] = label_id
    return data


def getParams():
    trainedModelID = getTrainedModel()
    trainedModel = TrainedModel.objects(id=trainedModelID).first()
    return trainedModel.modelParams


# 展示图片
def saveFig(fig, name):
    sio = BytesIO()
    fig.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    trainModelQuery = TrainedModel.objects(id=getTrainedModel()).first()
    trainModelQuery.figs[name] = src
    trainModelQuery.save()
    return


# 展示学习曲线
def showHistory(history):
    import matplotlib.pyplot as plt
    # 绘制accuracy曲线
    fig1 = plt.figure()
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    saveFig(fig1, 'accuracy曲线')
    # 绘制loss曲线
    fig2 = plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    saveFig(fig2, 'loss曲线')
    return


# 展示评价指标
def showEvaluation(model, x_test, y_test):
    from sklearn import metrics

    y_predict = model.predict(x_test)
    if len(y_predict.shape) > 1:
        y_predict = np.argmax(y_predict, axis=1)
    if len(y_test.shape) > 1:
        y_test = np.argmax(y_test, axis=1)
    accuracy = metrics.accuracy_score(y_test, y_predict)
    precision = metrics.precision_score(y_test, y_predict, average='weighted')
    recall = metrics.recall_score(y_test, y_predict, average='weighted')
    f1 = metrics.f1_score(y_test, y_predict, average='weighted')
    evaluation = {'accuracy': round(accuracy, 4), 'precision': round(precision, 4), 'recall': round(recall, 4),
                  'f1': round(f1, 4)}
    trainModelQuery = TrainedModel.objects(id=getTrainedModel()).first()
    trainModelQuery.evaluation = evaluation
    trainModelQuery.save()
    return


# 数据集shuffle
def doShuffle(x, y):
    indices = np.arange(x.shape[0])
    np.random.shuffle(indices)
    x = x[indices]
    y = y[indices]
    return x, y
