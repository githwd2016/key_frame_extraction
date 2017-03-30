#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-24 10:43 
"""
import pprint
import random

import pickle
import pymongo
import time

import settings
from src.util import Frame, Extractor

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='../output/extract.log',
                    filemode='w')


def get_key_frame(part_name):
    result = []
    with pymongo.MongoClient(settings.db_host) as conn:
        db = conn[settings.db_name]
        frames = db.frames
        frames_of_av = frames.find({'part_name': part_name}, {'danmus': 1, 'frame': 1})
    print(frames_of_av.count())
    logging.info('frames num: {}'.format(frames_of_av.count()))
    t1 = time.clock()
    av_list = []
    for frame in frames_of_av:
        temp = Frame(frame['danmus'], frame['frame'], frame['_id'])
        av_list.append(temp)

    t2 = time.clock()
    extractor = Extractor(av_list)
    model = extractor.train(preference_weight=2)

    t3 = time.clock()
    indices = model.cluster_centers_indices_
    # print('index: ' + str(indices.shape))
    # print('iter: ' + str(model.n_iter_))
    labels = model.labels_
    clusters = []
    temp = []
    for i in range(len(labels)):
        if i == 0:
            temp.append(i)
        else:
            if labels[i] != labels[i - 1]:
                clusters.append(temp)
                temp = []
            temp.append(i)
    clusters.append(temp)

    t4 = time.clock()
    length = len(clusters)
    for cluster in clusters[length // 4: -length // 4]:
        data_temp = {'danmus': []}
        for frame_index in cluster:
            danmu = av_list[frame_index].get_danmus_text(5, 20)
            data_temp['danmus'].extend(danmu)
        if data_temp['danmus']:
            key_frame_index = cluster[len(cluster) // 2]
            data_temp['frame_id'] = av_list[key_frame_index].id
            data_temp['part_name'] = part_name
            data_temp['r_matrix'] = pickle.dumps(av_list[key_frame_index].r_matrix)
            data_temp['g_matrix'] = pickle.dumps(av_list[key_frame_index].g_matrix)
            data_temp['b_matrix'] = pickle.dumps(av_list[key_frame_index].b_matrix)
            result.append(data_temp)

    t5 = time.clock()
    # print('get av list: {}s'.format(t2 - t1))
    print('train: {}s'.format(t3 - t2))
    # print('get clusters: {}s'.format(t4 - t3))
    # print('get key frame: {}s'.format(t5 - t4))
    return result


def sample(size=50):
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_parts_class = db.parts_class
        result = {}
        for class_ in settings.class_predefined:
            parts = coll_parts_class.find({'class': class_}, {'full_name': 1, '_id': 0})
            part = [x['full_name'] for x in parts]
            slice_ = random.sample(part, size)
            result[class_] = slice_
        return result


def insert_data(datas):
    with pymongo.MongoClient(settings.db_host) as client:
        db = client[settings.db_name]
        coll_train_data_ = db.train_data
        for data in datas:
            coll_train_data_.insert(data)


if __name__ == '__main__':
    # parts_sampled = sample()
    # with open('../output/parts_sampled.txt', 'wb') as f:
    #     pickle.dump(parts_sampled, f)

    # with pymongo.MongoClient(settings.db_host) as client:
    #     db = client[settings.db_name]
    #     coll_train_data = db.train_data
    #     coll_train_data.remove()

    with open('../output/parts_sampled.txt', 'rb') as f:
        parts_sampled = pickle.load(f)
    # pprint.pprint(parts_sampled)
    for class_name in parts_sampled:
        if class_name != '动作':
            print(class_name)
            logging.info(class_name)
            part = parts_sampled[class_name]
            for i, part_name in enumerate(part):
                print('{} begin'.format(part_name))
                logging.info('{} begin'.format(part_name))
                data = get_key_frame(part_name)
                print('insert...')
                logging.info('insert...')
                insert_data(data)
                print('{} finished({}/{})'.format(part_name, i + 1, len(part)))
                logging.info('{} finished({}/{})'.format(part_name, i + 1, len(part)))
