#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-22 14:36 
"""
import pickle
from pprint import pprint

import pymongo
import numpy as np

import settings


def get_color_margin(limit=20000):
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_frames_feature = db.frames_feature
        r_max = g_max = b_max = 0
        r_min = g_min = b_min = 1000
        for frame in coll_frames_feature.find().limit(limit):
            r = pickle.loads(frame['r_matrix'])
            g = pickle.loads(frame['g_matrix'])
            b = pickle.loads(frame['b_matrix'])
            if np.max(r) > r_max:
                r_max = np.max(r)
            if np.max(g) > g_max:
                g_max = np.max(g)
            if np.max(b) > b_max:
                b_max = np.max(b)
            if np.min(r) < r_min:
                r_min = np.min(r)
            if np.min(g) < g_min:
                g_min = np.min(g)
            if np.min(b) < b_min:
                b_min = np.min(b)
    return r_max, g_max, b_max, r_min, g_min, b_min


def get_tminfo_dic():
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_avs = db.avs
        tminfo_dic = {}
        for av in coll_avs.find():
            tminfo = av['tminfo']
            if tminfo not in tminfo_dic:
                tminfo_dic[tminfo] = 0
            tminfo_dic[tminfo] += av['parts_count']
            # tminfo_dic[tminfo] += 1
    return tminfo_dic


def get_av_title_and_desc():
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_avs = db.avs
        info = []
        for av in coll_avs.find():
            title = av['title']
            desc = av['desc']
            info.append([title, desc])

    return info


def predefined_class():
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_avs = db.avs
        for class_ in settings.class_predefined:
            av = coll_avs.find({"$or": [{"title": {"$regex": class_}}, {"desc": {"$regex": class_}}]},
                               {"parts_count": 1})
            count = av.count()
            num = [x['parts_count'] for x in av]
            print('|{}|{}|{}|'.format(class_, count, sum(num)))


def get_class():
    def _judge_class(string):
        for _class in settings.class_predefined[:-1]:
            if string.find(_class) != -1:
                return _class
        return '其他'

    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_avs = db.avs
        coll_parts = db.parts
        coll_parts_class = db.parts_class
        coll_parts_class.remove()
        for part in coll_parts.find({}, {'av_name': 1, 'title': 1, 'full_name': 1, '_id': 0}):
            av = coll_avs.find_one({'av_name': part['av_name']}, {'title': 1, 'desc': 1, '_id': 0})
            class_ = _judge_class(av['title'] + av['desc'] + part['title'])
            coll_parts_class.insert({'av_name': part['av_name'], 'full_name': part['full_name'], 'class': class_})


def get_class_num():
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_parts_class = db.parts_class
        nums = []
        for class_ in settings.class_predefined:
            part = coll_parts_class.find({'class': class_})
            num = part.count()
            print('|{}|{}|'.format(class_, num))
            nums.append(num)
        print('|{}|{}|'.format('合计', sum(nums)))


if __name__ == '__main__':
    # get_av_title_and_desc()
    # predefined_class()
    get_class()
    get_class_num()
