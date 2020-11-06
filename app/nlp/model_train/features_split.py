import numpy as np
from sklearn.model_selection import train_test_split

from manage import app
from app.utils.file_utils import getFileURL


def features_split(dataset, stratify, rate):
    featuresURL = dataset.features.feature
    labelURL = dataset.features.label
    x = np.load(featuresURL)
    y = np.load(labelURL)
    if stratify == 'None':
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=1 - rate, stratify=None)
    elif stratify == 'x':
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=1 - rate, stratify=x)
    else:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=1 - rate, stratify=y)
    dataset.train.feature = x_train_url = getFileURL('x_train.npy', app)
    dataset.test.feature = x_test_url = getFileURL('x_test.npy', app)
    dataset.train.label = y_train_url = getFileURL('y_train.npy', app)
    dataset.test.label = y_test_url = getFileURL('y_test.npy', app)
    np.save(x_train_url, x_train)
    np.save(x_test_url, x_test)
    np.save(y_train_url, y_train)
    np.save(y_test_url, y_test)
    return
