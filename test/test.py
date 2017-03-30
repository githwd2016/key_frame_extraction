#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-22 15:04 
"""
import random
from pprint import pprint
import pickle

import numpy as np
import math

import pymongo
import time

from sklearn.metrics import euclidean_distances

import settings
from src.extract_key_frame import get_key_frame, insert_data
from src.util import Frame, Extractor


def f1(r, g, b):
    _acos = math.acos((r - g + r - b) / (2 * math.sqrt((r - g) * (r - g) + (r - b) * (g - b))))
    h = _acos if b <= g else 2 * math.pi - _acos
    return h / (2 * math.pi) * 360


def f2(r, g, b):
    v = max(r, g, b)
    diff = v - min(r, g, b)
    if v == r:
        h = 60 * (g - b) / diff
    elif v == g:
        h = 60 * (b - r) / diff + 120
    else:
        h = 60 * (r - g) / diff + 240
    if h < 0:
        h += 360
    return h


if __name__ == '__main__':
    # test two methods of calculating hsv
    # for i in range(10):
    #     r = random.randint(0, 255)
    #     g = random.randint(0, 255)
    #     b = random.randint(0, 255)
    #     f1_ = f1(r, g, b)
    #     f2_ = f2(r, g, b)
    #     print("f1:{} f2:{} diff:{}".format(f1_, f2_, abs(f1_ - f2_)))
    # # deep combine
    # a = np.array([[1, 2], [3, 4]])
    # b = np.array([[1, 2], [3, 4]])
    # c = np.array([[1, 2], [3, 4]])
    # d = np.dstack((a, b, c))
    # print(d)
    # # cumsum
    # a = np.array([1, 2, 3, 4, 5, 6])
    # print(np.cumsum(a))
    # # one frame test
    start = time.clock()
    part_name = 'video.av2668065-3'
    result = get_key_frame(part_name)
    # insert_data(result)
    end = time.clock()
    print('total time: {}s'.format(end - start))
