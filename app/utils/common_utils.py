import re
import numpy as np


# 分句
def sentenceCut(para):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    return para.split("\n")


# 文件形状获取
def getFileShape(fileurl):
    if fileurl == '' or fileurl == []:
        return ''
    matrix = np.load(fileurl)
    return matrix.shape


# 文件内容获取
def getFileContent(fileurl):
    if fileurl == '' or fileurl == []:
        return ''
    fileType = fileurl.split('.')[-1]
    if (fileType == 'npy'):
        data = np.load(fileurl)
    else:
        data = fileurl
    return data
