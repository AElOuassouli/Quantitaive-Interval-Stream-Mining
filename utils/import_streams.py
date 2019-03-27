import sys
from os import listdir
from os.path import isfile, join
import copy
import json

sys.path.append("..\\")
from models.streams import Interval
from models.streams import Labeled_Interval
from models.streams import Stream
from models.streams import IntervalSequence


def ImportTruthJson(filePath) : 
    with open(filePath) as jsonFile :
        return json.load(jsonFile) 


def ImportIntervalList(folderPath):
    result = []
    states = []

    streams : [Stream]= ImportStreams(folderPath)

    for stream in streams :
        states.append(stream.m_label)
        for interval in stream.m_intervals :
            result.append(Labeled_Interval(interval.m_start, interval.m_end, stream.m_label))
    
    return  IntervalSequence(sorted(result, key = lambda interval: (interval.m_interval.m_start, interval.m_interval.m_end) ), states)

    

def ImportIntervalListNumFiles(folderPath, n):
    result = []
    states = []
    result = []
    states = []

    streams : [Stream]= ImportStreamsNum(folderPath, n)

    for stream in streams :
        states.append(stream.m_label)
        for interval in stream.m_intervals :
            result.append(Labeled_Interval(interval.m_start, interval.m_end, stream.m_label))
    
    return {"eventList" : sorted(result, key = lambda interval: (interval.m_interval.m_start, interval.m_interval.m_end) ),"states" : states}
    

def ImportStreams(folderPath): 
    streams : [Stream] = []
    for filename in listdir(folderPath):
        if isfile(join(folderPath, filename)):
            label = ""
            intervals = []
            file_lines = open(join(folderPath, filename), 'r').readlines()
            temp = -1 
            for line in file_lines:
                if label == "" and line.find("Name =") != -1:
                    label = line[6:]
                    label = label[:-1]
                if line.find(";") != -1:
                    if int(line[line.find(";") + 1 :]) == 1:
                        temp = int(line[: line.find(";")])
                    elif int(line[line.find(";") + 1 :]) == 2 and temp != -1:
                        intervals.append(Interval(temp,int(line[: line.find(";")])))
                        temp = -1
            stream = Stream(label, intervals, 0, True)
            streams.append(stream)
            
    return streams

def ImportStreamsNum(folderPath, n): 
    streams : [Stream] = []
    for filename in listdir(folderPath):
        if len(streams) >= n:
            break
        if isfile(join(folderPath, filename)):
            label = ""
            intervals = []
            file_lines = open(folderPath + filename, 'r').readlines()
            temp = -1 
            for line in file_lines:
                if label == "" and line.find("Name =") != -1:
                    label = line[6:]
                    label = label[:-1]
                if line.find(";") != -1:
                    if int(line[line.find(";") + 1 :]) == 1:
                        temp = int(line[: line.find(";")])
                    elif int(line[line.find(";") + 1 :]) == 2 and temp != -1:
                        intervals.append(Interval(temp,int(line[: line.find(";")])))
                        temp = -1
            stream = Stream(label, intervals, 0, True)
            streams.append(stream)
            
    return streams


def ImportIntervalListNotStream(folderPath):
    result = []
    states = []
    state = ""
    for filename in listdir(folderPath):
        if isfile(join(folderPath, filename)):
            file_lines = open(join(folderPath, filename), 'r').readlines()
            temp = -1 
            for line in file_lines:
                if state == "" and line.find("Name =") != -1:
                    state = line[6:]
                    state = state[:-1]
                    states.append(state)
                if line.find(";") != -1:
                    if int(line[line.find(";") + 1 :]) == 1:
                        temp = int(line[: line.find(";")])
                    elif int(line[line.find(";") + 1 :]) == 2 and temp != -1:
                        result.append(Labeled_Interval(temp, int(line[: line.find(";")]), state))
                        temp = -1
        state = ""
    return IntervalSequence(sorted(result, key = lambda interval: (interval.m_interval.m_start, interval.m_interval.m_end)), states)

def ImportIntervalListNumFilesNotStream(folderPath, n):
    result = []
    states = []
    state = ""
    index = 0
    for filename in listdir(folderPath):
        if index >= n :
            break
        if isfile(join(folderPath, filename)):
            file_lines = open(folderPath + filename, 'r').readlines()
            temp = -1 
            for line in file_lines:
                if state == "" and line.find("Name =") != -1:
                    state = line[6:]
                    state = state[:-1]
                    states.append(state)
                if line.find(";") != -1:
                    if int(line[line.find(";") + 1 :]) == 1:
                        temp = int(line[: line.find(";")])
                    elif int(line[line.find(";") + 1 :]) == 2 and temp != -1:
                        result.append(Labeled_Interval(temp, int(line[: line.find(";")]), state))
                        temp = -1
        state = ""
        index = index + 1
       
    return {"eventList" : sorted(result, key = lambda interval: (interval.m_interval.m_start, interval.m_interval.m_end) ),"states" : states}

        






