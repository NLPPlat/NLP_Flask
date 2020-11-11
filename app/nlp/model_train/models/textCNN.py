import tensorflow as tf
import gensim
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
from tensorflow.keras.layers import *
from tensorflow.keras import Model
from app.dataAPI.model_train import *
from app.dataAPI.utils import *
import matplotlib.pyplot as plt


class TrainModel():
    # 构建TextCNN模型
    def TextCNN_model_2(self, x_train_padded_seqs, y_train, x_test_padded_seqs, y_test, embedding_matrix):
        # 模型结构：词嵌入-卷积池化*3-拼接-全连接-dropout-全连接
        embedding_matrix_x,embedding_matrix_y=embedding_matrix.shape
        feature_x,feature_y=x_train_padded_seqs.shape
        main_input = Input(shape=(feature_y,), dtype='float64')
        # 词嵌入（使用预训练的词向量）
        embedder = Embedding(embedding_matrix_x, embedding_matrix_y, input_length=feature_y, weights=[embedding_matrix], trainable=False)
        embed = embedder(main_input)
        # 词窗大小分别为3,4,5
        cnn1 = Conv1D(256, 3, padding='same', strides=1, activation='relu')(embed)
        cnn1 = MaxPooling1D(pool_size=15)(cnn1)
        cnn2 = Conv1D(256, 4, padding='same', strides=1, activation='relu')(embed)
        cnn2 = MaxPooling1D(pool_size=14)(cnn2)
        cnn3 = Conv1D(256, 5, padding='same', strides=1, activation='relu')(embed)
        cnn3 = MaxPooling1D(pool_size=13)(cnn3)
        # 合并三个模型的输出向量
        cnn = concatenate([cnn1, cnn2, cnn3], axis=-1)
        flat = Flatten()(cnn)
        drop = Dropout(0.2)(flat)
        main_output = Dense(10, activation='softmax')(drop)
        model = Model(inputs=main_input, outputs=main_output)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        history = model.fit(x_train_padded_seqs, y_train, batch_size=1000, epochs=5,validation_split=0.35,verbose=2)
        showHistory(history)
        showEvaluation(model, x_test_padded_seqs, y_test)
        return model

    def train(self):
        data = getAllData()
        x = data['feature']
        embedding_matrix = data['embedding_matrix']
        y = data['label']
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
        y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
        model=self.TextCNN_model_2(x_train, y_train, x_test, y_test, embedding_matrix)
        return model

    def hyperparameters(self):
        return
