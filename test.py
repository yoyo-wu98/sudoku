# coding:utf-8
# python3.6

from utils.structure import *
# from utils.analytics import *
from utils.solver import *

if __name__ == '__main__':
    test_datas = open('./data/test_demo.txt', 'r')
    test_datas = test_datas.readlines()
    for test_data in test_datas:
        s = Structure(test_data)
        print(s.data)
        print(s.display())