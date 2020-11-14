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
    label_names = target_name.tolist()
    # 存储
    npyURL = getFileURL('label.npy', app)
    np.save(npyURL, label)
    data['label'] = npyURL
    txtURL = getFileURL('label2id.txt', app)
    with open(txtURL, 'a', encoding='utf-8') as f:
        i = 0
        for label_name in label_names:
            f.write(label_name + ' ' + str(i) + '\n')
            i=i+1
    data['label_name'] = txtURL
    return data


def BIO_label_encoder(data, params, type):
    # 初始化
    label = []
    label_name = {}
    # 转换
    for vector in data['vectors']:
        text = vector['text1']
        bio_text = []
        for char in text:
            bio_char = [char, 'O']
            bio_text.append(bio_char)
        entities = vector['label']['entities']
        for entityGroup in entities:
            for entity in entities[entityGroup]:
                start = int(entity['start'])
                end = int(entity['end'])
                bio_text[start][1] = 'B' + '-' + entityGroup
                for i in range(start + 1, end):
                    bio_text[i][1] = 'I' + '-' + entityGroup
        label.append({'id': vector['vectorid'], 'label': bio_text})
    # 写入
    txtURL = getFileURL('BIOlabel.txt', app)
    with open(txtURL, 'a', encoding='utf-8') as f:
        for vector_label in label:
            f.write(str(vector_label['id']))
            f.write('\n')
            for bio_vector in vector_label['label']:
                f.write(bio_vector[0] + ' ' + bio_vector[1])
                f.write('\n')
    data['label'] = txtURL
    return data
