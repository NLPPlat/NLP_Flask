import os
import uuid
import csv
import json
import xlrd
import docx
from chardet.universaldetector import UniversalDetector


# 文件删除
def fileDelete(paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
    return


# 文件路径获取
def getFileURL(filename, app):
    UUIDFileName = str(uuid.uuid1()) + '_' + filename
    fileurl = os.path.join(app.config['UPLOAD_FOLDER'], UUIDFileName)
    return fileurl


# 文件读取
def fileReader(fileurl):
    # 检测编码集
    detector = UniversalDetector()
    fileDetector = open(fileurl, 'rb')
    for line in fileDetector:
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    fileDetector.close()

    # 获取文件类型，分发函数
    fileType = fileurl.split(".")[-1]
    if fileType == 'csv':
        vectors = csvReader(fileurl, detector.result['encoding'])
    elif fileType == 'tsv':
        vectors = tsvReader(fileurl, detector.result['encoding'])
    elif fileType == 'json':
        vectors = jsonReader(fileurl, detector.result['encoding'])
    elif fileType == 'txt':
        vectors = txtReader(fileurl, detector.result['encoding'])
    elif fileType == 'xls' or fileType == 'xlsx':
        vectors = xlsReader(fileurl, detector.result['encoding'])
    elif fileType == 'doc' or fileType == 'docx':
        vectors = docReader(fileurl, detector.result['encoding'])
    return vectors


# 读取csv文件
def csvReader(fileurl, encoding):
    with open(fileurl, 'r', encoding=encoding) as file:
        data = csv.DictReader(file)
        i = 0
        vectors = []
        for vector in data:
            vector['id'] = i
            vector['delete'] = '未删除'
            i = i + 1
            vectors.append(vector)
    return vectors


# 读取tsv文件
def tsvReader(fileurl, encoding):
    with open(fileurl, 'r', encoding=encoding) as file:
        csv.register_dialect('tsv', delimiter='\t')
        data = csv.DictReader(file, dialect='tsv')
        csv.unregister_dialect('tsv')
        i = 0
        vectors = []
        for vector in data:
            vector['id'] = i
            vector['delete'] = '未删除'
            i = i + 1
            vectors.append(vector)
    return vectors


# 读取xls文件
def xlsReader(fileurl, encoding):
    book = xlrd.open_workbook(fileurl)
    table = book.sheet_by_index(0)
    row_Num = table.nrows
    col_Num = table.ncols
    key = table.row_values(0)
    j = 1
    vectors = []
    for i in range(row_Num - 1):
        vector = {}
        values = table.row_values(j)
        for x in range(col_Num):
            vector[key[x]] = values[x]
        j += 1
        vector["id"] = i
        vector['delete'] = '未删除'
        vectors.append(vector)
    return vectors


# 读取json文件
def jsonReader(fileurl, encoding):
    with open(fileurl, 'r', encoding=encoding) as file:
        data = json.load(file)
        i = 0
        vectors = []
        for vector in data:
            vector['id'] = i
            vector['delete'] = '未删除'
            i = i + 1
            vectors.append(vector)
    return vectors


# 读取txt文件
def txtReader(fileurl, encoding):
    with open(fileurl, 'r', encoding=encoding) as file:
        data = [k.strip() for k in file.readlines()]
        vectors = []
        for i, content in enumerate(data):
            if not content.isspace() and len(content) > 0:
                vector = {}
                vector['delete'] = '未删除'
                vector['id'] = i
                vector['text1'] = content
                vectors.append(vector)
    return vectors


# 读取doc文件
def docReader(fileurl, encoding):
    document = docx.Document(fileurl)
    vectors = []
    i = 0
    for para in document.paragraphs:
        content = para.text
        if not content.isspace() and len(content) > 0:
            vector = {}
            vector['delete'] = '未删除'
            vector['id'] = i
            vector['text1'] = content
            i = i + 1
            vectors.append(vector)
    return vectors
