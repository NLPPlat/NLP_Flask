import csv
import os


def fileDelete(paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
    return

def csvReader(file):
    text = csv.DictReader(file)
    i = 0
    textList = []
    for row in text:
        row['id'] = i
        row['delete'] = '未删除'
        i = i + 1
        textList.append(row)
    return textList
