from sklearn import preprocessing


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
    # 构造映射
    target_name = encoder.classes_
    target = encoder.transform(target_name)
    for index in range(len(target)):
        label_name[target[index]] = target_name[index]
    # 存储
    data['label'] = label
    data['label_name'] = label_name
    return data
