# coding:utf-8
# python3.6

from .structure import *

# TODO: history save and retrace - use solver's data and data_origin
# TODO: predict point's possible number and add checkpoint
class Predictor():
    point = None
    point_index = 0
    value = None