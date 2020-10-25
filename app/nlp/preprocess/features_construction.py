import numpy as np
import gensim
import tensorflow.compat.v1 as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from bson.binary import Binary
import pickle

# 序列化
def get_index(sentences,word_index):
    sequences=[]
    for sentence in sentences:
        sequence = []
        for word in sentence:
            try:
                sequence.append(word_index[word])
            except KeyError:
                pass
        sequences.append(sequence)
    return sequences


def EmbeddingMatrix(data, params, type):
    # 读取句子
    sentences=[]
    for vector in data['vectors']:
        if 'text1' in type:
            sentences.append(vector['text1'])

    # 处理为三维embedding矩阵
    print(data['url'])
    model = gensim.models.KeyedVectors.load_word2vec_format(data['url'])
    vocab_list = list(model.wv.vocab.keys())
    word_index = {word: index for index, word in enumerate(vocab_list)}
    X_data = get_index(sentences,word_index)
    maxlen = int(params["padding"])
    X_pad = pad_sequences(X_data, maxlen=maxlen,padding="post",truncating="post")
    embedding_matrix = np.zeros((len(vocab_list) + 1, model.vector_size))
    for index, word in enumerate(vocab_list):
        embedding_matrix[index + 1] = model.wv[word]
    with tf.Session() as sess:
        matrix = tf.nn.embedding_lookup(embedding_matrix, X_pad).eval(session=sess)
    data['matrix']=Binary(pickle.dumps(matrix, protocol=-1), subtype=128)
    return data