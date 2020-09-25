import csv


def csvReader(file):
    text = csv.DictReader(file)
    i = 0
    textList=[]
    for row in text:
        row['id'] = i
        i = i + 1
        textList.append(row)
    return textList
