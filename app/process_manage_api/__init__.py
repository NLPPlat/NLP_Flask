from flask import Blueprint

api = Blueprint("process_manage_api", __name__)

from . import data_upload
from . import data_set
from . import annotation
from . import pre_process
from . import model_train
