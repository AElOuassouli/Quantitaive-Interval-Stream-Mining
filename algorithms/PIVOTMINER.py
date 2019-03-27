
#implementation of PivotMiner 
# [Hassani2016] A Geometric approach for mining sequantial patterns in interval based data streams

from sklearn.cluster import DBSCAN
import numpy as np
from sklearn import metrics
import copy
import time


import sys
sys.path.append("..\\")
from models.streams import Delta
from models.streams import Transformation 


def Count(eventList, state, delta):
    result = 0
    for event in eventList:
        if event.m_label == state:
            result = result + 1
    return result

def Transform(origin, target, eventList, delta):
    result = []
    index_t = 0
    for i in range(0, len(eventList)):
        if eventList[i].m_label == origin:
            in_window = False
            for j in range(index_t, len(eventList)):
                if eventList[j].m_label == target :
                    
                    input()
                    if abs(eventList[i].m_interval.m_start - eventList[j].m_interval.m_start) <= delta and abs(eventList[i].m_interval.m_end - eventList[j].m_interval.m_end) <= delta : 
                        newDelta = Delta(eventList[i], eventList[j])
                        result.append(newDelta.getCordinates())
                        if not in_window :
                            in_window = True
                            index_t = j
                    elif in_window or (eventList[i].m_interval.m_start < eventList[j].m_interval.m_start and eventList[i].m_interval.m_end < eventList[j].m_interval.m_end) :
                        break
                    else :
                        index_t = j
                    
    return result

def PivotMiner(eventList, states, minSupport, tmax, eps, min_samples, plot, prefix):
    counts = {}
    deltas = {}

    ## Origin Transformation O(n²)
    index_t = 0
    for i in range(0, len(eventList)) :
        if eventList[i].m_label not in counts.keys() : 
            counts[eventList[i].m_label] = 1
        else :    
            counts[eventList[i].m_label] = counts[eventList[i].m_label] + 1
        for j in range(index_t, len(eventList)):
            if eventList[i].m_label != eventList[j].m_label :
                if abs(eventList[i].m_interval.m_start - eventList[j].m_interval.m_start) <= tmax and abs(eventList[i].m_interval.m_end - eventList[j].m_interval.m_end) <= tmax : 
                    if eventList[i].m_label not in deltas.keys() :
                        deltas[eventList[i].m_label] = {}
                    if eventList[j].m_label not in deltas[eventList[i].m_label].keys():
                        deltas[eventList[i].m_label][eventList[j].m_label] = []
                    
                    newDelta = Delta(eventList[i], eventList[j])
                    deltas[eventList[i].m_label][eventList[j].m_label].append(newDelta.getCordinates())


    ## Clusturing
    if len(deltas) == 0 :
        return []
    clusters = {}
    for origin in states:
        for target in states:
            if target != origin:
                if target in clusters.keys() and origin in clusters[target].keys():
                    if origin not in clusters.keys() :
                        clusters[origin] = {}
                    clusters[origin][target] = copy.copy(clusters[target][origin])
                    clusters[origin][target]["isMirror"] = True
                elif origin in deltas.keys() and target in deltas[origin].keys():
                    db = DBSCAN(eps=eps, min_samples=minSupport*counts[origin]).fit(deltas[origin][target])
                    labels = db.labels_
                    if origin not in clusters.keys() :
                        clusters[origin] = {}
                    clusters[origin][target] = {"clust" : labels, "isMirror" : False}
     ## Base Patterns extraction
    basePatterns = []
    for origin in states:
        if origin in clusters.keys() :
            for target in states:
                if target in clusters[origin].keys() and origin != target :
                    if not clusters[origin][target]["isMirror"]:
                        sum_start = {}
                        sum_end = {}
                        num_delta = {}
                        index = 0
                        for label in clusters[origin][target]["clust"]:
                            if label != -1: # -1 is noise
                                if label in sum_start:
                                    sum_start[label] = sum_start[label] + deltas[origin][target][index][0]
                                    sum_end[label] = sum_end[label] + deltas[origin][target][index][1]
                                    num_delta[label] = num_delta[label] + 1
                                else :
                                    sum_start[label] =  deltas[origin][target][index][0]
                                    sum_end[label] = deltas[origin][target][index][1]
                                    num_delta[label] = 1
                            index = index + 1
                        labels = set(clusters[origin][target]["clust"])
                        for label in labels :
                            if label != -1 :
                                if num_delta[label] / counts[origin] > minSupport and  sum_start[label] / num_delta[label] >= 0 and sum_end[label] / num_delta[label] >= 0 :
                                    newBP = {}
                                    newBP["premise"] = origin
                                    newBP["conclusion"] = target
                                    newBP['transformation'] =  [ sum_start[label] / num_delta[label] , sum_end[label] / num_delta[label] ]   
                                    newBP['support'] = num_delta[label]
                                    basePatterns.append(newBP)
                                    
                    else :
                        sum_start = {}
                        sum_end = {}
                        num_delta = {}
                        index = 0
                        for label in clusters[target][origin]["clust"]:
                            if label != -1: # -1 is noise
                                if label in sum_start:
                                    sum_start[label] = sum_start[label] + deltas[target][origin][index][0]
                                    sum_end[label] = sum_end[label] + deltas[target][origin][index][1]
                                    num_delta[label] = num_delta[label] + 1
                                else :
                                    sum_start[label] =  deltas[target][origin][index][0]
                                    sum_end[label] = deltas[target][origin][index][1]
                                    num_delta[label] = 1
                            index = index + 1
                        labels = set(clusters[target][origin]["clust"])
                        for label in labels :
                            if label != -1 :
                                if num_delta[label] / counts[target] > minSupport and  sum_start[label] / num_delta[label] <= 0 and sum_end[label] / num_delta[label] <= 0  :
                                    newBP = {}
                                    newBP["premise"] = origin
                                    newBP["conclusion"] = target
                                    newBP['transformation'] = [-1 * sum_start[label] / num_delta[label] , -1 * sum_end[label] / num_delta[label] ]
                                    newBP['support'] = num_delta[label]
                                    basePatterns.append(newBP)
    return basePatterns  

 
