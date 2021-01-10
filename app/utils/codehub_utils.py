import sys
import traceback
from app.utils.global_utils import *

# 储存结果
codehub_result = None
# 储存模型
codehub_model = None
# 储存超参数列表
codehub_params = None

codeForOperator = '''
operator=Operator()
global codehub_result
codehub_result=operator.operator()
'''

codeForModel = '''
trainmodel=TrainModel()
global codehub_model
codehub_model=trainmodel.train()
'''

codeForParams = '''
trainmodel=TrainModel()
global codehub_params
codehub_params=trainmodel.hyperparameters()
'''


# 重写流
class __Autonomy__(object):
    def __init__(self):
        self._buff = ""

    def write(self, out_stream):
        self._buff += out_stream

    def flush(self):
        pass


def codeReplace(code):
    return code.replace('\t', '    ')


# 算子执行
def operatorRunUtil(code, datasetIDForUse):
    setDataset(datasetIDForUse)
    code = code + codeForOperator
    code = codeReplace(code)
    current = sys.stdout
    a = __Autonomy__()
    sys.stdout = a
    try:
        exec(code, globals())
        sys.stdout = current
        return codehub_result
    except Exception as e:
        sys.stdout = current
        return traceback.format_exc()


# 模型执行
def modelRunUtil(code, datasetIDForUse, trainedModelForUse):
    setDataset(datasetIDForUse)
    setTrainedModel(trainedModelForUse)
    code = code + codeForModel
    code = codeReplace(code)
    current = sys.stdout
    a = __Autonomy__()
    sys.stdout = a
    try:
        exec(code, globals())
        sys.stdout = current
        return a._buff, codehub_model
    except Exception as e:
        sys.stdout = current
        return a._buff + traceback.format_exc(), codehub_model


# 超参数读取
def paramsFetchUtil(code):
    code = code + codeForParams
    code = codeReplace(code)
    current = sys.stdout
    a = __Autonomy__()
    sys.stdout = a
    try:
        exec(code, globals())
        sys.stdout = current
        return codehub_params
    except Exception as e:
        sys.stdout = current
        return traceback.format_exc()
