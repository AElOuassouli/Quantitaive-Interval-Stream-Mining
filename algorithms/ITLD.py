import sys
sys.path.append("..\\")
import math
from models.streams import Transformation
from models.streams import Interval
from models.streams import Stream

CHI_VALUE = 3.84

def Confidence(premise : Stream, conclusion : Stream): 
    intersection = premise.GetIntersection(conclusion)
    return float(intersection.m_length) / float(premise.m_length)

def ValidityThreshold(lenA, lenB, duration):
    if lenA > 0 and duration > 0 and lenB > 0:
        return float((lenA*lenB + math.sqrt(CHI_VALUE * lenA * (duration - lenA) * lenB * (duration - lenB) /duration))/(lenA * duration))
    else : 
        return 0 #infinite

def Itld(streams : [Stream], tmin, tmax, duration):
    results = []
    for premise in streams:
        for conclusion in streams:
            if premise.m_label != conclusion.m_label:
                duration = max(premise.m_intervals[-1].m_end, conclusion.m_intervals[-1].m_end) - min(premise.m_intervals[0].m_start, conclusion.m_intervals[0].m_start)+(tmax-tmin)
                thresholds = []
                expansions_impacts = []
                reductions_impacts = []
                reference = Confidence(premise, conclusion.GetTransformation(Transformation( tmin,  tmin)))
                for i in range(tmin, tmax + 1):
                    if premise.m_length * reference != 0 :
                        threshold = min(1, ValidityThreshold( premise.m_length * reference, conclusion.m_size, duration))
                    else : 
                        threshold = 1

                    thresholds.append(threshold)
                    exp_conf = Confidence(premise, conclusion.GetTransformation(Transformation(i + 1, i)))
                    exp_impact = abs(exp_conf - reference)
                    expansions_impacts.append(exp_impact) 
                    
                    red_conf =  Confidence(premise, conclusion.GetTransformation(Transformation(i, i + 1)))
                    red_impact = abs(reference - red_conf)
                    reductions_impacts.append(red_impact)

                    reference = reference - red_impact + exp_impact
                spec_exp = []
                spec_red = []

                if reductions_impacts[0] > thresholds[0] :
                    spec_red.append(tmin)
                for i in range(1, tmax - tmin + 1) :
                    if expansions_impacts[i] < thresholds[i] and expansions_impacts[i - 1] > thresholds[i - 1] :
                        spec_exp.append(tmin + i)

                for i in range(1, tmax - tmin + 1) :
                    if reductions_impacts[i] > thresholds[i] and reductions_impacts[i - 1] < thresholds[i - 1] :
                        spec_red.append(tmin + i)
                if expansions_impacts[len(expansions_impacts) - 1] > thresholds[len(thresholds) - 1] :
                    spec_exp.append(tmax)
                if len(spec_exp) == len(spec_red) : 
                    i = 0
                    while i < len(spec_red) :
                        #if statistically valid
                        specific_transformation = Transformation(spec_exp[i], spec_red[i]) 
                        transformed = conclusion.GetTransformation(specific_transformation)
                        conf = Confidence(premise, transformed)
                        validity = ValidityThreshold(premise.m_length, transformed.m_length, duration)

                        if conf > validity :
                            results.append({"premise" : premise.m_label, "conclusion" : conclusion.m_label, "transformation" : [specific_transformation.m_alpha, specific_transformation.m_beta], "confidence" : conf })   
                        i = i + 1
                elif len(spec_red) != 0 and len(spec_exp) != 0 :
                    specific_transformation = Transformation(spec_exp[-1], spec_red[0]) 
                    transformed = conclusion.GetTransformation(specific_transformation)
                    conf = Confidence(premise, transformed)
                    validity = ValidityThreshold(premise.m_length, transformed.m_length, duration)
                    if conf > validity :
                        results.append({"premise" : premise.m_label, "conclusion" : conclusion.m_label, "transformation" : [specific_transformation.m_alpha, specific_transformation.m_beta], "confidence" : conf })
    return results

