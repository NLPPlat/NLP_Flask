import csv

def csvReader(file):
    reader = csv.DictReader(file)
    print(reader)
    for row in reader:
        print(row)
    return 'list'