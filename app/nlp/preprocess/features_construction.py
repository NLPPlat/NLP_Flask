import numpy as np
import gensim
import tensorflow.compat.v1 as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from bson.binary import Binary
import pickle

from manage import app
from app.utils.file_utils import *


def get_index(sentences, word_index):
    sequences = []
    for sentence in sentences:
        sequence = []
        for word in sentence:
            try:
                sequence.append(word_index[word])
            except KeyError:
                pass
        sequences.append(sequence)
    return sequences


# 序列化
def padSequence(data, params, type):
    # 初始化
    model = gensim.models.KeyedVectors.load_word2vec_format(data['embedding'])
    vocab_list = list(model.wv.vocab.keys())
    word_index = {" ": 0}
    # word_vector = {}
    embedding_matrix = np.zeros((len(vocab_list) + 1, model.vector_size))

    # 填充
    for i in range(len(vocab_list)):
        word = vocab_list[i]
        word_index[word] = i + 1
        # word_vector[word] = model.wv[word]
        embedding_matrix[i + 1] = model.wv[word]

    # 序列化
    sentences = []
    if 'text1' in type:
        for vector in data['vectors']:
            sentences.append(vector['text1'])
    X_data = get_index(sentences, word_index)
    maxlen = int(params["maxlen"])
    X_pad = pad_sequences(X_data, maxlen=maxlen, padding="post", truncating="post")
    feature = np.array(X_pad)

    # 保存
    embeddingMatrixURL = getFileURL('embedding_matrix.npy', app)
    featureURL = getFileURL('feature.npy', app)
    np.save(embeddingMatrixURL, embedding_matrix)
    np.save(featureURL, feature)
    data['embedding_matrix'] = embeddingMatrixURL
    data['feature'] = featureURL
    return data


# 特征矩阵生成
def EmbeddingMatrix(data, params, type):
    # 读取句子
    sentences = []
    for vector in data['vectors']:
        if 'text1' in type:
            sentences.append(vector['text1'])

    # 处理为三维矩阵
    model = gensim.models.KeyedVectors.load_word2vec_format(data['embedding'])
    vocab_list = list(model.wv.vocab.keys())
    word_index = {word: index for index, word in enumerate(vocab_list)}
    X_data = get_index(sentences, word_index)
    maxlen = int(params["maxlen"])
    X_pad = pad_sequences(X_data, maxlen=maxlen, padding="post", truncating="post")
    embedding_matrix = np.zeros((len(vocab_list) + 1, model.vector_size))
    for index, word in enumerate(vocab_list):
        embedding_matrix[index + 1] = model.wv[word]
    with tf.Session() as sess:
        matrix = tf.nn.embedding_lookup(embedding_matrix, X_pad).eval(session=sess)

    # 处理为二维矩阵
    features = []
    for i, basevec in enumerate(matrix):
        exist = (basevec != 0)
        den = basevec.sum(axis=0)
        num = exist.sum(axis=0)
        features.append((den / num).tolist())
    featureMatrix = np.array(features)

    # 保存
    npyURL = getFileURL('feature.npy', app)
    np.save(npyURL, featureMatrix)
    data['feature'] = npyURL
    return data
