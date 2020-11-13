import numpy as np
from tensorflow.keras.models import load_model


def classificationBatch(data, model, plat):
    if plat == 'Keras':
        features = np.load(data['feature'])
        label_name = data['label_name']
        model = load_model(model)
        results = model.predict(features)
        if len(results.shape) > 1:
            results = np.argmax(results, axis=1)
        for index, vector in enumerate(data['vectors']):
            vector['result'] = label_name[results[index]]
    return data
