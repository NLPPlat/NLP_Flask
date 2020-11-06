from gensim.models import word2vec as wc

from manage import app
from app.utils.file_utils import getFileURL


def Word2vec(data, params, type):
    sentences = []
    for vector in data['vectors']:
        if 'text1' in type:
            sentences.append(vector['text1'])
        if 'text2' in type:
            sentences.append(vector['text2'])
    if (params['max_vocab_size'] == 'None'):
        params['max_vocab_size'] = None
    else:
        params['max_vocab_size'] = int(params['max_vocab_size'])
    if (params['trim_rule'] == 'None'):
        params['trim_rule'] = None
    else:
        params['trim_rule'] = int(params['trim_rule'])
    model = wc.Word2Vec(sentences, size=int(params['size']), alpha=int(params['alpha']), window=int(params['window']),
                        min_count=int(params['min_count']), max_vocab_size=params['max_vocab_size'],
                        sample=int(params['sample']), seed=int(params['seed']), workers=int(params['workers']),
                        min_alpha=int(params['min_alpha']), sg=int(params['sg']), hs=int(params['hs']),
                        negative=int(params['negative']), cbow_mean=int(params['cbow_mean']),
                        hashfxn=hash, iter=int(params['iter']),
                        trim_rule=params['trim_rule'], sorted_vocab=int(params['sorted_vocab']),
                        batch_words=int(params['batch_words']))
    modelURL=getFileURL('word2vec.txt', app)
    model.wv.save_word2vec_format(modelURL, binary=False)
    data['embedding']=modelURL
    return data
