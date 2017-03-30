#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-23 16:26 
"""
import multiprocessing
import os
import pprint
from collections import Iterable, Iterator

import pickle

import pymongo

import settings
from src.util import Frame

if __name__ == '__main__':
    with open('./output/labels.txt', 'rb') as f:
        labels = pickle.load(f)
    with open('./output/cluster.txt', 'rb') as f:
        clusters = pickle.load(f)
    with pymongo.MongoClient(settings.db_host) as conn:
        db = conn[settings.db_name]
        frames = db.frames
        frames_of_av = frames.find({'part_name': 'video.av1022446-1'}, {'frame': 1})
    av_list = []
    for frame in frames_of_av:
        temp = Frame(None, frame['frame'])
        av_list.append(temp)
    print('get data')
    dir = './output' + '/damping=0.8 preference=2*median center=36'
    os.mkdir(dir)
    for index, l in enumerate(clusters):
        for i in l:
            path = os.path.join(dir, str(index) + '_' + str(i) + '.png')
            av_list[i].save_img(path)
