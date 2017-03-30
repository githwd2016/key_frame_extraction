#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-24 09:58 
"""
import pprint

import pickle

import math
import pymongo

import settings

if __name__ == '__main__':
    # with pymongo.MongoClient(settings.db_host) as conn:
    #     db = conn[settings.db_name]
    #     frames = db.frames
    #     frames_of_av = frames.find({'part_name': 'video.av1022446-1'}, {'danmus': 1, 'frame': 1})
    #     print(frames_of_av.count())


    # labels = [1, 2, 2, 3, 3, 1, 3, 5, 2, 2, 2, 3, 4]
    # cluster = []
    # temp = []
    # for i in range(len(labels)):
    #     if i == 0:
    #         temp.append(i)
    #     else:
    #         if labels[i] != labels[i - 1]:
    #             cluster.append(temp)
    #             temp = []
    #         temp.append(i)
    # cluster.append(temp)
    # pprint.pprint(cluster)

    # with open('./output/parts_sampled.txt', 'rb') as f:
    #     parts_sampled = pickle.load(f)
    # for i,j in enumerate(parts_sampled['动作']):
    #     print(i,j)

    # end = 163
    # start = 0
    # size = 20
    # n = math.floor((end - start) / size)
    # print(n)

    with pymongo.MongoClient(settings.db_host) as conn:
        db = conn[settings.db_name]
        coll_train_data = db.train_data
        coll_frames = db.frames
        frames_id = coll_train_data.find({}, {'frame_id': 1, '_id': 0})
        result = []
        for i in frames_id:
            frame_id = i['frame_id']
            result.append(frame_id)
        for i in result[0:100]:
            temp = coll_frames.find_one({'_id': i}, {'time': 1, '_id': 0})
            print(temp['time'])
