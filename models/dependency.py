import sys
import copy
sys.path.append("..\\")
from models.streams import Stream
from models.streams import Transformation

class Dependency:
    ids = 0
    def __init__(self, label : str, intersection : Stream) :
        self.id = Dependency.ids 
        Dependency.ids += 1
        self.m_labels : [str] = [label]
        self.m_transformations : [Transformation] = [Transformation(0,0)]
        self.m_confidences : [float] = [1.0]
        self.m_inter_storage = dict()
        self.m_inter_storage[label] = intersection
        self.m_intersection : Stream = intersection
        self.m_first_intersection = None
        self.m_disjunctions = []

    def setFirstIntersction(self, inter) :
        self.m_first_intersection = inter
    
    def getMergableCandidate(self, label) :
        if label in self.m_labels :
            if label == self.m_labels[-1] :
                return self.m_intersection, self.m_transformations[-1]
            elif label != self.m_labels[0] and label in self.m_inter_storage   :
                return self.m_inter_storage[label], self.m_transformations[self.m_labels.index(label)]
            else :
                return None, None
        return None, None

    def getExtentedDependency(self, label, transformation, confidence, intersection) :
        result = copy.deepcopy(self)
        result.id = Dependency.ids
        Dependency.ids += 1
        result.m_labels.append(label)
        result.m_transformations.append(transformation)
        result.m_confidences.append(confidence)
        result.m_intersection = intersection
        result.m_inter_storage[label] = intersection 
        return result
    
    def getMergedDependency(self, dep, label, confidence, intersection) :
        result = copy.deepcopy(self)
        result.id = Dependency.ids
        Dependency.ids += 1
        result.m_labels += dep.m_labels[1:] 
        result.m_transformations += dep.m_transformations[1:] 
        result.m_confidences += [confidence] + dep.m_confidences[2:]
        result.m_inter_storage[label] = intersection
        result.m_intersection = dep.m_intersection 
        return result
    
    def getPrefixDependency(self, i) :
        result = copy.deepcopy(self)
        result.m_labels = result.m_labels[:i + 1]
        result.m_transformations = result.m_transformations[:i + 1]
        result.m_confidences = result.m_confidences[:i + 1]
        result.m_intersection = self.m_inter_storage[self.m_labels[i]]
        return result

    def getSuffixDependency(self, i) :
        result = copy.deepcopy(self)
        result.id = Dependency.ids
        Dependency.ids += 1
        result.m_labels = result.m_labels[i + 1:]
        result.m_transformations = result.m_transformations[i + 1:]
        result.m_confidences = result.m_confidences[i + 1:]
        if len(result.m_labels) > 0 :
            result.m_first_intersection = self.m_inter_storage[self.m_labels[i+1]]
        else :
            result.m_first_intersection = None
        removed = True
        while removed :
            removed = False
            for key in result.m_inter_storage.keys() :
                if key not in result.m_labels :
                    del result.m_inter_storage[key]
                    removed = True
                    break 
        return result
    
    def AddDisjunctionAtIndex(self, index, dependency) :
        if index + 1 != len(self.m_labels) :
            suffix = self.getSuffixDependency(index)
            self.m_intersection = self.m_inter_storage[self.m_labels[index]]
            self.m_labels = self.m_labels[:index + 1]
            self.m_transformations = self.m_transformations[:index + 1]
            self.m_confidences = self.m_confidences[:index + 1]
            removed = True
            while removed : 
                removed = False
                for key in self.m_inter_storage.keys() :
                    if key not in self.m_labels :
                        del self.m_inter_storage[key]
                        removed = True
                        break
            self.m_disjunctions = [suffix]
        self.m_disjunctions.append(dependency)

    def __str__(self) :
        result = []
        for i in range(len(self.m_labels)) :
            result.append(self.m_labels[i] + str(self.m_transformations[i]) + str(round(self.m_confidences[i], 2)))
        if len(self.m_disjunctions) > 0 :
            result.append("Disjunctions")
            for dis in self.m_disjunctions :
                result.append(str(dis))
        return str(result)

