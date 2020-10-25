from app.utils.global_utils import *
from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from mongoengine import Q
import json
from app import models, files
from app.utils.response_code import RET
from app.utils.dataset_utils import copy
from app.utils.file_utils import fileDelete
from app.models.dataset import *
from app.models.venation import *
from app.utils.vectors_uitls import getDataFromPreprocessDataset


def getPreprocessData(preprocessID):
    datasetQuery=PreprocessDataset.objects(id=int(getDataset())).first()
    vectors=getDataFromPreprocessDataset(datasetQuery, preprocessID)
    return vectors