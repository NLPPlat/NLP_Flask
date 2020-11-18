import tensorflow as tf
import gensim
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
from tensorflow.keras.layers import *
from tensorflow.keras import Model
from tensorflow import keras
from app.dataAPI.model_train import *
from app.dataAPI.utils import *
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.layers import Embedding
from tensorflow.keras.callbacks import Callback,EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import GlobalAveragePooling1D
from tensorflow.keras.datasets import imdb


class TrainModel():
    # 构建TextCNN模型
    def TextCNN_model_2(self, x_train_padded_seqs, y_train, x_test_padded_seqs, y_test, embedding_matrix):
        # 模型结构：词嵌入-卷积池化*3-拼接-全连接-dropout-全连接
        embedding_matrix_x, embedding_matrix_y = embedding_matrix.shape
        feature_x, feature_y = x_train_padded_seqs.shape
        main_input = Input(shape=(feature_y,), dtype='float64')
        # 词嵌入（使用预训练的词向量）
        model = Sequential()
        adam = Adam(lr=1e-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
        # 我们从一个有效的嵌入层（embedding layer）开始，它将我们的词汇索引（vocab indices ）映射到词向量的维度上.
        model.add(Embedding(embedding_matrix_x, embedding_matrix_y, input_length=feature_y, weights=[embedding_matrix],
                             trainable=True))
        # 我们增加 GlobalAveragePooling1D, 这将平均计算文档中所有词汇的的词嵌入
        model.add(GlobalAveragePooling1D())
        # 我们投射到单个单位的输出层上，并用sigmoid压缩它
        model.add(Dense(10, activation='softmax'))
        model.compile(loss='binary_crossentropy',
                      optimizer=adam,
                      metrics=['accuracy'])
        history = model.fit(x_train_padded_seqs, y_train, batch_size=1000, epochs=20, validation_split=0.2, verbose=2)
        showHistory(history)
        showEvaluation(model, x_test_padded_seqs, y_test)
        return model

    def train(self):
        data = getAllData()
        x = data['feature']
        embedding_matrix = data['embedding_matrix']
        y = data['label']
        x, y = doShuffle(x, y)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
        y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
        model = self.TextCNN_model_2(x_train, y_train, x_test, y_test, embedding_matrix)
        return model

    def hyperparameters(self):
        return
