from app.models.dataset import TextContent
import json

# 预处理数据库与中文步骤映射表
preprocessMap = {
    '原始文本': 'originalData',
    '分词': 'cut',
    '去停用词': 'stopwords',
    '词性标注': 'postagging'
}




# 从数据库中读取向量
def getVectorsFromPreprocessDataset(dataset, preprocessChnName):
    # 获得英文名
    if preprocessChnName in preprocessMap:
        preprocessName = preprocessMap[preprocessChnName]
    else:
        preprocessName = preprocessChnName

    # 读取数据
    vectors = dataset[preprocessName]

    return vectors


# 向量回填数据库
def setVectorsToreprocessDataset(dataset, preprocessChnName, vectors):
    # 获得英文名
    if preprocessChnName in preprocessMap:
        preprocessName = preprocessMap[preprocessChnName]
    else:
        preprocessName = preprocessChnName

    # 存入数据库
    for vector in vectors:
        textContent = TextContent().from_json(json.dumps(vector))
        dataset[preprocessName].append(textContent)
    dataset.save()

    return
