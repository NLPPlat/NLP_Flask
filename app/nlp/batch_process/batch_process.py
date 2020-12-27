import numpy as np
from tensorflow.keras.models import load_model


def classificationBatch(data, model, plat):
    if plat == 'Keras':
        features = np.load(data['feature'])
        label_id = {}
        with open(data['label_id'], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                value, key = line.split()
                label_id[int(key)] = value
        model = load_model(model)
        results = model.predict(features)
        if len(results.shape) > 1:
            results = np.argmax(results, axis=1)
        for index, vector in enumerate(data['vectors']):
            vector['result'] = label_id[results[index]]
    return data
