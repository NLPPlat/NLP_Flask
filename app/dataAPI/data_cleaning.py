import json

from app.models.model import *
from app.models.dataset import *
from app.utils.common_utils import *
from app.utils.global_utils import *
from app.utils.vector_uitls import *


def getCleaningData():
    vectors = json.loads(vectors_select_all(int(getDataset())).to_json())
    return vectors
