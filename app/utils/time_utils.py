import datetime


def getTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getTimeForH():
    return datetime.datetime.now().strftime("%H")

def getTimeForDay():
    return datetime.datetime.now().strftime("%d")
