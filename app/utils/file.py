import csv


def csvReader(file):
    text = csv.DictReader(file)
    i = 0
    textList = []
    for row in text:
        row['id'] = i
        row['delete'] = '未删除'
        if 'label' not in row:
            row['label']=''
        i = i + 1
        textList.append(row)
    return textList
