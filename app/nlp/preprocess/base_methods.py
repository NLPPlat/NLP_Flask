import jieba

def cut(vectors,params,textType):
    for vector in vectors:
        if 'text1' in textType:
            vector['text1']=jieba.lcut(vector['text1'])
        if 'text2' in textType:
            vector['text2']=jieba.lcut(vector['text2'])
    return vectors