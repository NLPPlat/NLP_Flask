import numpy as np
from sklearn import preprocessing

from manage import app
from app.utils.file_utils import *


def single_label_encoder(data, params, type):
    # 初始化
    label = []
    label_name = {}
    # 转换
    for vector in data['vectors']:
        label.append(vector['label'])
    encoder = preprocessing.LabelEncoder()
    encoder.fit(label)
    label = encoder.transform(label)
    # 获得标签排序
    target_name = encoder.classes_
    # 存储
    npyURL = getFileURL('label.npy', app)
    np.save(npyURL, label)
    data['label'] = npyURL
    data['label_name'] = target_name.tolist()
    return data
