import copy
import math

CHI_VALUE = 3.84

class Transformation : 
    def __init__(self, alpha, beta):
        self.m_alpha = alpha
        self.m_beta = beta
    
    def __eq__(self, other) :
        if self.m_alpha == other.m_alpha and self.m_beta == other.m_beta :
            return True
        else :
            return False

    def __str__(self):
        return "(" + str(self.m_alpha) + "," + str(self.m_beta) + ")"
class Interval:
    m_start : int = None
    m_end : int = None

    def __init__(self, start, end):
        if start < end :
            self.m_start = start
            self.m_end = end
        else : 
            raise NameError("Invalid interval - start: " + str(start) + " end: " + str(end))

    def __str__(self):
        return " ["+ str(self.m_start)+ "," +str(self.m_end) +")"
class Stream:
    def __init__(self, label, intervals, length, verify):
        self.m_label = label
        self.m_intervals = copy.copy(intervals)
        self.m_length = length
        self.m_size = len(self.m_intervals)
        if verify :
            self.VerifyStream()
    
    def __str__(self):
        result = self.m_label + " : "
        for interval in self.m_intervals:
            result = result + str(interval) + ","
        return result

    def AddInterval(self, interval : Interval, verify = True): 
        self.m_intervals.append(interval)
        if verify:
            self.VerifyStream()
        
    
    def VerifyStream(self):
        #sort of intervals
        self.m_intervals = sorted(self.m_intervals , key = lambda interval: interval.m_start)
        # fusion of overlapping streams
        sequence : [Interval] = []
        length = 0
        for interval in self.m_intervals:
            if len(sequence) == 0:
                sequence.append(copy.copy(interval))
                length = interval.m_end - interval.m_start
            else:
                if interval.m_start > sequence[-1].m_end :
                    sequence.append(copy.copy(interval))
                    length = length + interval.m_end - interval.m_start
                else:
                    if interval.m_end > sequence[-1].m_end:
                        length = length + interval.m_end - sequence[-1].m_end 
                        sequence[-1].m_end = interval.m_end
        self.m_intervals = sequence
        self.m_size = len(self.m_intervals)
        self.m_length = length

    # O(#Intervals)
    # self must be sorted 
    def GetTransformation(self, transformation : Transformation):
        transformed : [Interval] = []
        length = 0
        for interval in self.m_intervals:
            lowerBound = interval.m_start - transformation.m_alpha
            higherBound = interval.m_end - transformation.m_beta
            if higherBound > lowerBound:
                if len(transformed) == 0:
                    transformed.append(Interval(lowerBound, higherBound))
                    length = higherBound - lowerBound
                else:
                    if (lowerBound > transformed[-1].m_end):
                        transformed.append(Interval(lowerBound, higherBound))
                        length = length + higherBound - lowerBound
                    else :
                        if higherBound > transformed[-1].m_end:
                            length = length + higherBound - transformed[-1].m_end
                            transformed[-1].m_end = higherBound
        return Stream(self.m_label, transformed, length, False)



    #O(#Intervals)
    # streams must be sorted and non overlapping
    #computes intersection between self and stream
    def GetIntersection(self, stream):
        newLabel = self.m_label + " ^ " + stream.m_label 
        if self.m_length == 0 or stream.m_length == 0:
            return Stream(newLabel, [], 0, False)
        if self.m_intervals[0].m_start > stream.m_intervals[0].m_start :
            newStream = stream.GetIntersection(self)
            newStream.m_label = newLabel
            return copy.deepcopy(newStream)
        
        intersection : [Interval] = []
        length = 0
        index_self = 0
        index_stream = 0
        while index_self < len(self.m_intervals) and index_stream < len(stream.m_intervals):
            A : Interval = self.m_intervals[index_self]
            B : Interval = stream.m_intervals[index_stream]
            if A == B :
                intersection.append(Interval(A.m_start, A.m_end))
                length = length + A.m_end - A.m_start
                index_self = index_self + 1
                index_stream = index_stream + 1
            
            elif A.m_end <= B.m_start:
                index_self = index_self + 1
            
            else :
                if A.m_start <= B.m_start :
                    if A.m_end < B.m_end :
                        intersection.append(Interval(B.m_start, A.m_end))
                        length = length + A.m_end - B.m_start
                        index_self = index_self + 1
                    elif A.m_end > B.m_end :
                        intersection.append(Interval(B.m_start, B.m_end))
                        length = length + B.m_end - B.m_start
                        index_stream = index_stream + 1
                    else :
                        intersection.append(Interval(B.m_start, B.m_end))
                        length = length + B.m_end - B.m_start
                        index_stream = index_stream + 1
                        index_self = index_self + 1
                else :
                    if A.m_start < B.m_end :
                        if A.m_end < B.m_end :
                            intersection.append(Interval(A.m_start, A.m_end))
                            length = length +  A.m_end - A.m_start
                            index_self = index_self + 1
                        elif A.m_end > B.m_end:
                            intersection.append(Interval(A.m_start, B.m_end))
                            length = length + B.m_end - A.m_start
                            index_stream = index_stream + 1 
                        elif A:
                            intersection.append(Interval(A.m_start, B.m_end))
                            length = length + B.m_end - A.m_start
                            index_stream = index_stream + 1 
                            index_self = index_self + 1
                    else :
                        index_stream = index_stream + 1

        newLabel = self.m_label + " ^ " + stream.m_label
        return Stream(newLabel, intersection, length, False)

    def GetUnion(self, stream):
        #computes union between self and stream
        label = self.m_label + " v " + stream.m_label
        intervals = self.m_intervals + stream.m_intervals
        result = Stream(label, intervals, 0 , True)
        return result
def Confidence(premise : Stream, conclusion : Stream): 
    intersection = premise.GetIntersection(conclusion)
    return float(intersection.m_length) / float(premise.m_length) , intersection

def ValidityThreshold(lenA, lenB, duration):
    if lenA > 0 and duration > 0 and lenB > 0 and duration > lenA and duration > lenB :
        return float((lenA*lenB + math.sqrt(CHI_VALUE * lenA * (duration - lenA) * lenB * (duration - lenB) /duration))/(lenA * duration))
    else : 
        return 2 #infinite



### Unique sequence of labeled intervals

class Labeled_Interval : 
    def __init__(self, start, end, label):
        self.m_interval = Interval(start, end)
        self.m_label = label
    
    def __str__(self):
        return "{ " + self.m_label + " , " + str(self.m_interval) + "}"


class IntervalSequence : 
    def __init__(self, sequence, labels ):
        self.m_sequence = sequence
        self.m_labels = labels

    def addInterval(self, interval : Labeled_Interval) :
        self.m_sequence.append(interval)
        self.m_labels.append(interval.m_label)
        self.m_sequence = sorted(self.m_sequence , key = lambda interval: interval.m_interval.m_start)