import sys
sys.path.append("..\\")
import math

from models.streams import Transformation
from models.streams import Interval
from models.streams import Stream


CHI_VALUE = 3.84

def Confidence(premise : Stream, conclusion : Stream):
    intersection = premise.GetIntersection(conclusion)
    return intersection.m_length / premise.m_length

def ValidityThreshold(lenA, lenB, duration):
    if lenA > 0 and duration > 0 and lenB > 0:
        return min(1, float((lenA*lenB + math.sqrt(CHI_VALUE * lenA * (duration - lenA) * lenB * (duration - lenB) /duration))/(lenA * duration)))
    else : 
        return 0 #infinite


def ConfidentAndMostSpecific(transformation, lenPremise, duration, Nodes, tmin, tmax, results):
    if  transformation.depth >= 0 :
        if transformation.confidence >= ValidityThreshold(lenPremise, transformation.length_conclusion, duration):
            isMostSpecific = True
            moreGeneral = []
            for res in results:
                if results[res].m_alpha <= transformation.m_alpha and results[res].m_beta >= transformation.m_beta:
                    isMostSpecific = False
                    break
                if results[res].m_alpha >= transformation.m_alpha and results[res].m_beta <= transformation.m_beta:
                    moreGeneral.append(str(res))
            if isMostSpecific :
                results[str(transformation)] = transformation
                for delete in moreGeneral :
                    results.pop(delete)
        else :
            if transformation.m_alpha + 1 <= tmax :
                ConfidentAndMostSpecific(Nodes[str(Transformation(transformation.m_alpha + 1 , transformation.m_beta))], lenPremise, duration, Nodes, tmin, tmax, results)
            if transformation.m_beta - 1 >= tmin :
                ConfidentAndMostSpecific(Nodes[str(Transformation(transformation.m_alpha, transformation.m_beta -1))], lenPremise, duration, Nodes, tmin, tmax,  results)
                
def Teddy(streams : [Stream], tmin : int, tmax : int, duration) :
    results = []
    for premise in streams:
        for conclusion in streams:
            if premise.m_label != conclusion.m_label  :
                duration = max(premise.m_intervals[-1].m_end, conclusion.m_intervals[-1].m_end) - min(premise.m_intervals[0].m_start, conclusion.m_intervals[0].m_start) + (tmax-tmin)
                Border = {}
                Nodes = {} # nodes deleted from Border
                Cand : [Transformation] = []
                Cand.append(Transformation(tmax, tmin))
                d = 0
                while len(Cand) != 0 :
                    #Pruning based on confidence
                    Prom : [Transformation] = []
                    k = 0
                    currentCandidate : Transformation = Cand[k]
                    
                    transformed_conclusion = conclusion.GetTransformation(currentCandidate)
                    lastConf = Confidence(premise, transformed_conclusion)
                    
                    while k < len(Cand):
                        cand_k : Transformation = Cand[k]
                        max_gain = (abs(currentCandidate.m_alpha - cand_k.m_alpha) + abs(currentCandidate.m_beta - cand_k.m_beta) )* conclusion.m_size / premise.m_length
                        boundMinConf = min(1, ValidityThreshold(premise.m_length, conclusion.m_length, duration))
                        if lastConf + max_gain >= boundMinConf : 
                            currentCandidate = Cand[k]
                            
                            transformed_conclusion = conclusion.GetTransformation(currentCandidate)
                            
                            lastConf = Confidence(premise, transformed_conclusion)
                            if lastConf >= boundMinConf :
                                Cand[k].confidence = lastConf
                                Cand[k].length_conclusion = transformed_conclusion.m_length
                                Cand[k].depth = d
                                Prom.append(Cand[k])
                        k = k+1
                    #End pruning based on confidence
                    
                    #Pruning based on dominance
                    Sigma = []
                    to_delete = []
                    for prom in Prom:
                        first_ancestor = Transformation(prom.m_alpha + 1, prom.m_beta)
                        second_ancestor = Transformation(prom.m_alpha, prom.m_beta - 1)

                        dominates_left_ancestor = False
                        dominates_right_ancestor = False
                        if str(first_ancestor) in Border.keys() :
                            left_part = 1 - prom.confidence / Border[str(first_ancestor)].confidence
                            right_part = 1 - prom.length_conclusion / Border[str(first_ancestor)].length_conclusion
                            if (left_part < right_part):
                                dominates_left_ancestor = True
                        else :                               
                            dominates_left_ancestor = True

                        if str(second_ancestor) in Border.keys() :
                            left_part = 1 - prom.confidence / Border[str(second_ancestor)].confidence
                            right_part = 1 - prom.length_conclusion / Border[str(second_ancestor)].length_conclusion
                            if (left_part < right_part):
                                dominates_right_ancestor = True
                        else :
                            dominates_right_ancestor = True
                        if dominates_left_ancestor and dominates_right_ancestor:
                            # remove ancestors from border
                            to_delete.append(str(first_ancestor))
                            to_delete.append(str(second_ancestor))
                            # adding promissing to border 
                            Border[str(prom)] = prom
                            Sigma.append(prom)
                    for delete in to_delete:
                        if delete in Border.keys() :
                            Nodes[delete] = Border[delete]
                            Border.pop(delete)        
                    # End pruning based on Dominance

                    # Candidate Generation
                    Cand_next : [Transformation] = []
                    if tmax - tmin > d and len(Sigma) > 0:
                        if str(Sigma[0]) == str(Transformation(tmax - d, tmin)):
                            Cand_next.append(Transformation(tmax - (d + 1), tmin ))
                        i = 0
                        while i < len(Sigma) - 1 :
                            prom1 = Sigma[i]
                            prom2 = Sigma[i+1]
                            if prom1.m_alpha == prom2.m_alpha - 1 and prom1.m_beta == prom2.m_beta - 1:
                                Cand_next.append(Transformation(prom1.m_alpha, prom2.m_beta))
                            i = i + 1
                        if str(Sigma[-1]) == str(Transformation(tmax, tmin + d)) :
                            Cand_next.append(Transformation(tmax, tmin + d + 1))
                    
                    Cand = Cand_next
                    # End candidate generation
                    d = d+1
                # Compute valid and significant
                
                result = {}
                for b in Border:
                    ConfidentAndMostSpecific(Border[b], premise.m_length, duration, Nodes, tmin, tmax, result)
                for res in result :
                    results.append({"premise" : premise.m_label, "conclusion" : conclusion.m_label, "transformation" : [result[res].m_alpha, result[res].m_beta], "confidence" : result[res].confidence })    
    return results