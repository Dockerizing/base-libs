from os import path as osp
import sure
from ..dld_base import logging_init

PROJECT_DIR = osp.dirname(osp.dirname(osp.realpath(__file__)))
logging_init(osp.join(PROJECT_DIR, 'logs'))
