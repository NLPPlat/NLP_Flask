import sys
import traceback

# 储存结果
result = []

# 重写流
class __Autonomy__(object):
    def __init__(self):
        self._buff = ""

    def write(self, out_stream):
        self._buff += out_stream

    def flush(self):
        pass

# 代码执行
def codeRunUtil(code):
    code=code+"\noperator=Operator()"+"\nglobal result"+"\nresult=operator.operator()"
    current = sys.stdout
    a = __Autonomy__()
    sys.stdout = a
    try:
        exec(code)
        sys.stdout = current
        return result
    except Exception as e:
        return traceback.format_exc()
