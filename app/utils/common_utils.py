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
    fileType = fileurl.split('.')[-1]
    if fileType != 'npy':
        return ''
    else:
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


# 文件名获取
def getFileName(fileurl):
    filename = fileurl.split('___')[-1]
    return filename


# 文件类型获取
def getFileType(fileurl):
    if fileurl != '' and fileurl != []:
        if '.' in fileurl:
            fileType = fileurl.split('.')[-1] + '文件'
        else:
            fileType = '未知类型文件'
    else:
        fileType = ''
    return fileType


# 文件预览内容获取
def getFileContentPart(fileurl):
    if fileurl == '' or fileurl == []:
        return ''
    fileType = fileurl.split('.')[-1]
    if (fileType == 'npy'):
        data = np.load(fileurl).tolist()
        data = data[0:10]
    elif (fileType == 'txt'):
        data = ''
        with open(fileurl, 'r', encoding='utf-8') as f:
            data = []
            for i in range(10):
                data.append(f.readline().strip())
    else:
        data = fileurl
    return data


# 获取文件信息
def getFileInfo(fileurl):
    info = {}
    info['filename'] = getFileName(fileurl)
    info['filetype'] = getFileType(fileurl)
    info['fileshape'] = getFileShape(fileurl)
    info['fileContent'] = getFileContentPart(fileurl)
    return info
