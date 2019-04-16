import sys
import copy
sys.path.append("..\\")
import math

from models.streams import Transformation
from models.streams import Interval
from models.streams import Stream
from models.streams import Confidence
from models.streams import ValidityThreshold

class Candidate :
    def __init__(self, transformation) :
        self.m_confidence = None
        self.m_intersection = None
        self.m_length_conclusion = None
        self.m_depth = None
        self.m_transformation = transformation

    def __eq__(self, other) :
        if self.m_transformation == other.m_transformation :
            return True
        else :
            return False
    def __str__(self):
        result = str(self.m_transformation)
        result += " " + str(self.m_confidence)
        if self.m_intersection != None :
            result += " " + str(len(self.m_intersection.m_intervals))
        return result



def ConfidentAndMostSpecific(candidate : Candidate, lenPremise, duration, deleted_from_border, tmin, tmax, results):
    if  candidate.m_depth >= 0 :
        if candidate.m_confidence >= ValidityThreshold(lenPremise, candidate.m_length_conclusion, duration):
            isMostSpecific = True
            moreGeneral = []
            for res in results:
                if results[str(res)].m_transformation.m_alpha <= candidate.m_transformation.m_alpha and results[str(res)].m_transformation.m_beta >= candidate.m_transformation.m_beta:
                    isMostSpecific = False
                    break
                if results[str(res)].m_transformation.m_alpha >= candidate.m_transformation.m_alpha and results[str(res)].m_transformation.m_beta <= candidate.m_transformation.m_beta:
                    moreGeneral.append(str(res))
            if isMostSpecific :
                results[str(candidate)] = candidate
                for delete in moreGeneral :
                    results.pop(delete)
        else :
            if candidate.m_transformation.m_alpha + 1 <= tmax :
                ConfidentAndMostSpecific(deleted_from_border[str(Transformation(candidate.m_transformation.m_alpha + 1 , candidate.m_transformation.m_beta))], lenPremise, duration, deleted_from_border, tmin, tmax, results)
            if candidate.m_transformation.m_beta - 1 >= tmin :
                ConfidentAndMostSpecific(deleted_from_border[str(Transformation(candidate.m_transformation.m_alpha, candidate.m_transformation.m_beta -1))], lenPremise, duration, deleted_from_border, tmin, tmax,  results)
                

def MaxGain(cand1, cand2, conclusion_size, premise_length) :
    return (abs(cand1.m_alpha - cand2.m_alpha) + abs(cand1.m_beta - cand2.m_beta)) * conclusion_size / premise_length

def BoundMinConf(premise_length, conclusion_length, duration) :
    return min(1, ValidityThreshold(premise_length, conclusion_length, duration))


def Teddy(premise : Stream, conclusion : Stream, tmin : int, tmax : int, duration : int) :
    
    Border = {}
    deleted_from_border = {} # nodes deleted from Border
    Cand : [Candidate] = []
    Cand.append(Candidate(Transformation(tmax, tmin)))
    d = 0
    while len(Cand) != 0:
        #Pruning based on confidence
        Prom : [Candidate] = []
        k = 0
        currentCandidate = Cand[k]
        transformed_conclusion = conclusion.GetTransformation(currentCandidate.m_transformation)
        lastConf, intersection = Confidence(premise, transformed_conclusion)
        
        currentCandidate.m_confidence = copy.deepcopy(lastConf)
        currentCandidate.m_intersection = copy.deepcopy(intersection)          
       
        while k < len(Cand):
            cand_k = Cand[k]
            
            max_gain = MaxGain(currentCandidate.m_transformation, cand_k.m_transformation, conclusion.m_size, premise.m_length)
            boundMinConf = BoundMinConf(premise.m_length, conclusion.m_length, duration)
            
            if lastConf + max_gain >= boundMinConf : 
                currentCandidate = Cand[k]
                transformed_conclusion = conclusion.GetTransformation(currentCandidate.m_transformation)
                lastConf, intersection = Confidence(premise, transformed_conclusion)
                currentCandidate.m_confidence = copy.deepcopy(lastConf)
                currentCandidate.m_intersection = copy.deepcopy(intersection)          
                if lastConf >= boundMinConf :
                    Cand[k].m_confidence = copy.deepcopy(lastConf)
                    Cand[k].m_length_conclusion = transformed_conclusion.m_length
                    Cand[k].m_depth = d
                    Cand[k].m_intersection = copy.deepcopy(intersection)
                    Prom.append(Cand[k])
            k = k+1
        #End pruning based on confidence
       
        #Pruning based on dominance
        Sigma = []
        to_delete = []
        for prom in Prom:
            first_ancestor = Transformation(prom.m_transformation.m_alpha + 1, prom.m_transformation.m_beta)
            second_ancestor = Transformation(prom.m_transformation.m_alpha, prom.m_transformation.m_beta - 1)
            dominates_left_ancestor = False
            dominates_right_ancestor = False
            if str(first_ancestor) in Border.keys() :
                left_part = 1 - prom.m_confidence / Border[str(first_ancestor)].m_confidence
                right_part = 1 - prom.m_length_conclusion / Border[str(first_ancestor)].m_length_conclusion
                if (left_part < right_part):
                    dominates_left_ancestor = True
            else :                               
                dominates_left_ancestor = True

            if str(second_ancestor) in Border.keys() :
                left_part = 1 - prom.m_confidence / Border[str(second_ancestor)].m_confidence
                right_part = 1 - prom.m_length_conclusion / Border[str(second_ancestor)].m_length_conclusion
                if (left_part < right_part):
                    dominates_right_ancestor = True
            else :
                dominates_right_ancestor = True
            if dominates_left_ancestor and dominates_right_ancestor:
                # remove ancestors from border
                to_delete.append(str(first_ancestor))
                to_delete.append(str(second_ancestor))
                # adding promissing to border 
                Border[str(prom.m_transformation)] = prom
                Sigma.append(prom)
        for delete in to_delete:
            if delete in Border.keys() :
                deleted_from_border[delete] = Border[delete]
                Border.pop(delete)        
        # End pruning based on Dominance


        # Candidate Generation
        Cand_next : [Candidate] = []
        if tmax - tmin > d and len(Sigma) > 0:
            if Sigma[0].m_transformation == Transformation(tmax - d, tmin):
                Cand_next.append(Candidate(Transformation(tmax - (d + 1), tmin )))
            i = 0
            while i < len(Sigma) - 1 :
                prom1 = Sigma[i]
                prom2 = Sigma[i+1]
                if prom1.m_transformation.m_alpha == prom2.m_transformation.m_alpha - 1 and prom1.m_transformation.m_beta == prom2.m_transformation.m_beta - 1:
                    Cand_next.append(Candidate(Transformation(prom1.m_transformation.m_alpha, prom2.m_transformation.m_beta)))
                i = i + 1
            if Sigma[-1].m_transformation == Transformation(tmax, tmin + d) :
                Cand_next.append(Candidate(Transformation(tmax, tmin + d + 1)))
                    
        Cand = Cand_next
        # End candidate generation
        d = d+1
    # Compute valid and significant            
    result = {}
    for b in Border:
        ConfidentAndMostSpecific(Border[b], premise.m_length, duration, deleted_from_border, tmin, tmax, result)
    
    results = [] #intersections
    confidences = [] #confidences
    transformations = [] #transformations
    for res in result :
        results.append(result[res].m_intersection )
        confidences.append(result[res].m_confidence)
        transformations.append(result[res].m_transformation)
    return results, confidences, transformations