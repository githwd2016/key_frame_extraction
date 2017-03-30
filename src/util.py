#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: winton 
@time: 2017-03-22 14:59 
"""
import base64
import io
import math

import time
from pprint import pprint
import multiprocessing

from PIL import Image
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.metrics import euclidean_distances

from src import slaves


class ColorUnit(object):
    def __init__(self, r, g, b):
        # self.r = r
        # self.g = g
        # self.b = b
        max_ = max(r, g, b)
        diff = max_ - min(r, g, b)
        self.v = max_ / 255
        self.s = diff / max_ if max_ != 0 else 0
        if diff == 0:
            h = 0
        else:
            if max_ == r:
                h = 60.0 * (g - b) / diff
            elif max_ == g:
                h = 60.0 * (b - r) / diff + 120.0
            else:
                h = 60.0 * (r - g) / diff + 240.0
        if h < 0:
            h += 360
        self.h = h
        self.w = self._quantization_value()

    def _quantization_value(self):
        if 0 <= self.s <= 1:
            if self.s <= 0.2:
                s = 0
            elif self.s <= 0.7:
                s = 1
            else:
                s = 2
        else:
            raise ValueError()
        if 0 <= self.v <= 1:
            if self.v <= 0.2:
                v = 0
            elif self.v <= 0.7:
                v = 1
            else:
                v = 2
        else:
            raise ValueError()
        if 0 <= self.h <= 360:
            if 21 <= self.h <= 40:
                h = 1
            elif 41 <= self.h <= 75:
                h = 2
            elif 76 <= self.h <= 155:
                h = 3
            elif 156 <= self.h <= 190:
                h = 4
            elif 191 <= self.h <= 270:
                h = 5
            elif 271 <= self.h <= 295:
                h = 6
            elif 296 <= self.h <= 315:
                h = 7
            else:
                h = 0
        else:
            raise ValueError('illegal value:{}'.format(self.h))
        return 9 * h + 3 * s + v


class Frame(object):
    def __init__(self, danmus, frame, id=None):
        self.id = id
        self.danmus = danmus
        self.image = Image.open(io.BytesIO(frame))
        r, g, b = self.image.split()
        self.r_matrix = np.array(r, dtype=np.int32)
        self.g_matrix = np.array(g, dtype=np.int32)
        self.b_matrix = np.array(b, dtype=np.int32)

    def get_danmus_text(self, lower, upper):
        text = []
        for danmu in self.danmus:
            if lower < len(danmu['text']) < upper:
                text.append({'text': danmu['text']})
        return text

    def show_img(self):
        self.image.show()

    def save_img(self, dir):
        self.image.save(dir)


class Extractor(object):
    def __init__(self, av, length=200, width=200, jobs=20):
        # t1 = time.clock()
        count = len(av)
        wg = slaves.Workgroup(jobs, self._task)
        context = (av, length, width)
        result = wg.work(context, 0, count)
        self.x = []
        finished = 0
        while finished < jobs:
            r = result.get()
            if r is None:
                finished += 1
            else:
                self.x.append(r)
        wg.wait()
        self.x.sort(key=lambda x: x[0])
        # t2 = time.clock()
        # print('extract time:{}s'.format(t2 - t1))

    def train(self, damping=0.8, max_iter=1000, convergence_iter=30, preference_weight=1, verbose=False):
        feature = np.array([i[1] for i in self.x])
        if preference_weight != 1:
            similarity = -euclidean_distances(feature, squared=True)
            preference = preference_weight * np.median(similarity)
        else:
            preference = None
        ap = AffinityPropagation(damping, max_iter, convergence_iter,
                                 preference=preference, verbose=verbose)
        ap = ap.fit(feature)
        return ap

    def _task(self, id, queue, context, start, end):
        def cumulative_histogram_vector(color):
            count = np.zeros(72, np.int32)
            for unit in color:
                count[unit.w] += 1
            return np.cumsum(count)

        frames = context[0]
        length = context[1]
        width = context[2]
        index = 0
        for frame in frames[start:end]:
            temp = []
            for i in range(length):
                for j in range(width):
                    temp.append(ColorUnit(frame.r_matrix[i][j], frame.g_matrix[i][j], frame.b_matrix[i][j]))
            queue.put((index + start, cumulative_histogram_vector(temp)))
            index += 1
        queue.put(None)
        print('{}: Success from {} to {}.'.format(id, start, end))
