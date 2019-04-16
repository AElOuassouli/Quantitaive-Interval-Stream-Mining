import sys
sys.path.append("..\\")
import math

from models.streams import Transformation
from models.streams import Interval
from models.streams import Stream
from models.streams import Confidence
from models.streams import ValidityThreshold

def Itld(premise : Stream, conclusion : Stream, tmin, tmax, duration):
    if premise.m_length == 0 or conclusion.m_length == 0 :
        return [], [], [], []
    results = []
    transformations = []
    confidences = []
    thresholds = []
    expansions_impacts = []
    reductions_impacts = []
                
    reference , a = Confidence(premise, conclusion.GetTransformation(Transformation( tmin,  tmin)))

    for i in range(tmin, tmax + 1):
        if premise.m_length * reference != 0 :
            threshold = min(1, ValidityThreshold( premise.m_length * reference, conclusion.m_size, duration))
        else : 
            threshold = 1
        thresholds.append(threshold)
        exp_conf , a = Confidence(premise, conclusion.GetTransformation(Transformation(i + 1, i)))
        exp_impact = abs(exp_conf - reference)
        expansions_impacts.append(exp_impact) 
        red_conf , a =  Confidence(premise, conclusion.GetTransformation(Transformation(i, i + 1)))
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
            conf , intersection = Confidence(premise, transformed)
            validity = ValidityThreshold(premise.m_length, intersection.m_length, duration)
            if conf > validity :
                results.append(intersection)
                transformations.append(specific_transformation)
                confidences.append(conf)
            i = i + 1
    elif len(spec_red) != 0 and len(spec_exp) != 0 :
        #if statistically valid
        specific_transformation = Transformation(spec_exp[-1], spec_red[0]) 
        transformed = conclusion.GetTransformation(specific_transformation)
        conf, intersection = Confidence(premise, transformed)
        validity = ValidityThreshold(premise.m_length, transformed.m_length, duration)
        if conf > validity :
            results.append(intersection)
            transformations.append(specific_transformation)
            confidences.append(conf)

    return results, confidences, transformations

