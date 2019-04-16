import sys
import copy
sys.path.append("..\\")

from models.streams import Stream
from models.streams import Transformation
from algorithms.ITLD import Confidence
from algorithms.ITLD import ValidityThreshold

log = False

def isIncluded(a, b) :
    if len(a) < len(b) :
        return False
    for i in range(len(b)) :
        if b[i] not in a :
            return False
    return True
def LabelsIntersection(list1, list2) :
    for l1 in list1:
        if l1 in list2 :
            return True
    for l2 in list2:
        if l2 in list1 :
            return True
    return False
def GetStreamByLabel(streams, label) :
    for s in streams :
        if s.m_label == label :
            return s
    return None

coef = 1
def Matching(s1 , s2, duration) :
    if s1.m_length > 0 and s2.m_length > 0 :
        confidence, a = Confidence(s1, s2)
        confidence2, a = Confidence(s2, s1)
        threshold = ValidityThreshold(s1.m_length, s2.m_length, duration)
        if confidence > 1 - coef*threshold and confidence2 > 1 - coef*threshold:
        #if confidence > 1 - 0.2 and confidence2 > 1 - 0.2:
            if log :
                print("MATCHING TRUE." + " threshold " + str(threshold)+ " length a " + str(s1.m_length) + " length b" + str(s2.m_length)) 
                print("1 with 2 : conf =" + str(confidence))
                print("2 with 1 conf =" + str(confidence2)) 
            return True
        else :
            if log :
                print("MATCHING false." + " threshold " + str(threshold)+ " length a " + str(s1.m_length) + " length b" + str(s2.m_length)) 
                print("1 with 2 : conf =" + str(confidence))
                print("2 with 1 conf =" + str(confidence2)) 
            return False
    else : 
        return False




def prePruning(dependencies, candidate, streams, duration) :
    for new_p in dependencies :
        if new_p != candidate  :
            if isIncluded(new_p.m_labels, candidate.m_labels):
                transformation = new_p.m_transformations[new_p.m_labels.index(candidate.m_labels[0])]
                transformed = candidate.m_intersection.GetTransformation(transformation)
                inter_candidate = transformed.GetIntersection(GetStreamByLabel(streams, new_p.m_labels[0]))
                inter_new_p = new_p.m_intersection.GetIntersection(GetStreamByLabel(streams, new_p.m_labels[0]))
                if log :
                    print('Pre-pruning')
                    print('1 :' + str(new_p))
                    print('2 :' + str(candidate))
                if Matching(inter_new_p, inter_candidate, duration) :
                    if log :
                        print("Pruned")
                        print("===========")
                    return True
    return False

def GetExtension(prefix, extension, streams, duration) :
    if prefix != extension and extension.m_labels[0] == prefix.m_labels[-1] and not LabelsIntersection(prefix.m_labels[:-1], extension.m_labels[1:]) :
        
        transformed = extension.m_intersection.GetTransformation(prefix.m_transformations[-1])
        inter_extension = transformed.GetIntersection(GetStreamByLabel(streams, prefix.m_labels[0]))
        inter_prefix = prefix.m_intersection
        if Matching(inter_extension, inter_prefix, duration) :
            merged = copy.deepcopy(prefix)
            merging = True
            for i in range(1, len(extension.m_labels)) :
                transformed = extension.m_inter_storage[extension.m_labels[i]].GetTransformation(prefix.m_transformations[-1])
                confidence, intersection = Confidence(merged.m_intersection, transformed)
                validity = ValidityThreshold(transformed.m_length, merged.m_intersection.m_length, duration)
                if confidence > validity :
                    transformation = copy.deepcopy(extension.m_transformations[i])
                    transformation.m_alpha += prefix.m_transformations[-1].m_alpha
                    transformation.m_beta += prefix.m_transformations[-1].m_beta
                    merged = merged.getExtentedDependency(extension.m_labels[i], transformation, confidence, intersection)
                else : 
                    merging = False
                    break
            if merging :
                return merged

        
    return None

def MergingExtension(new_deps, streams, duration) :
    non_extendable = []
    for prefix in new_deps :
        if not prePruning(non_extendable, prefix, streams, duration) :
            current_results = [prefix]
            while len(current_results) > 0 :
                new_results = []
                for to_extend in current_results :
                    isExtended = False
                    for extension in new_deps :
                        merged = GetExtension(to_extend, extension, streams, duration)
                        if merged != None :
                            new_results.append(merged)
                            isExtended = True
                    if not isExtended :
                        non_extendable.append(to_extend)
                current_results = new_results
            non_extendable = postProcessResults(non_extendable, streams, duration)
    new_deps = copy.deepcopy(non_extendable)
    return new_deps

def postProcessResults(results, streams, duration) :
    to_remove = []
    for to_merge in results :
        for dep in results:
            if to_merge != dep and to_merge not in to_remove and dep not in to_remove :
                if isIncluded(dep.m_labels, to_merge.m_labels): 
                    transformation = dep.m_transformations[dep.m_labels.index(to_merge.m_labels[0])]
                    transformed = to_merge.m_intersection.GetTransformation(transformation)
                    inter_to_merge = transformed.GetIntersection(GetStreamByLabel(streams, dep.m_labels[0]))

                    if Matching(inter_to_merge, dep.m_intersection, duration) :
                        #extra condition if the two dependencies have equal length
                        if len(dep.m_labels) != len(to_merge.m_labels) :
                            to_remove.append(to_merge)
                            break
                        else : 
                            transformation = to_merge.m_transformations[to_merge.m_labels.index(dep.m_labels[0])]
                            transformed = dep.m_intersection.GetTransformation(transformation)
                            inter_dep = transformed.GetIntersection(GetStreamByLabel(streams, to_merge.m_labels[0]))
                            if Matching(inter_dep, to_merge.m_intersection, duration) :
                                to_remove.append(to_merge)
                                break
    for d in to_remove :
        results.remove(d)
    return results

def GetMergeable(d1, i1, d2, i2) :
    while i1 + 1 < len(d1.m_labels)   and i2 + 1 < len(d2.m_labels) :
        if d1.m_labels[i1 + 1] == d2.m_labels[i2 + 1] :
            i1 += 1
            i2 += 1
        else : 
            break 
    if len(d1.m_disjunctions) > 0 :
        for dis in d1.m_disjunctions :
            r1, ind1, r2, ind2 = GetMergeable(dis, -1, d2, copy.deepcopy(i2))
            if ind2 != i2 :
                return r1, ind1, r2, ind2
    if len(d2.m_disjunctions) > 0 :
        for dis in d2.m_disjunctions :
            r1, ind1, r2, ind2 = GetMergeable(d1, copy.deepcopy(i1), dis, -1)
            if ind1 != i1 :
                return r1, ind1, r2, ind2    
    return d1, i1, d2, i2  
def BuildDisjunctions(deps, duration) :
    for d1 in deps :
        for d2 in reversed(deps) :
            if d1 == d2 :
                break
            m1, i1, m2, i2 =  GetMergeable(d1, -1, d2, -1)
            if i1 != -1 and i2 != -1 :
                if Matching(m1.m_inter_storage[m1.m_labels[i1]], m2.m_inter_storage[m2.m_labels[i2]], duration) :
                    suffix1  = m1.getSuffixDependency(i1) 
                    m2.AddDisjunctionAtIndex(i2, suffix1)
                    deps.remove(d1)
                    return BuildDisjunctions(deps, duration)
    return deps




import networkx as nx
import matplotlib.pyplot as plt
from utils.hierarchy import hierarchy_pos

def AddEdges(d, parent_label, G) :
    for i in range(len(d.m_labels)) :
        G.add_node(str(d.id) + d.m_labels[i] + str(d.m_transformations[i]))
    for dis in d.m_disjunctions :
        G = AddEdges(dis, str(d.id) +  d.m_labels[-1] + str(d.m_transformations[-1]),  G)
    if parent_label != "" and len(d.m_labels) > 0 :
        G.add_edge(parent_label, str(d.id) +  d.m_labels[0] + str(d.m_transformations[0]) , c= str(round(d.m_confidences[0],2)))
    for i in range(1, len(d.m_labels) ) :
        G.add_edge(str(d.id) +  d.m_labels[i-1] + str(d.m_transformations[i-1]) , str(d.id) +  d.m_labels[i] + str(d.m_transformations[i]) , c= str(round(d.m_confidences[i],2)))
    
    return G

plt.ion()
def PlotDependency(d) :
    plt.clf()
    G = nx.MultiDiGraph()
    G = AddEdges(d, "", G)
    
    pos = nx.shell_layout(G)
    pos = hierarchy_pos(G, str(d.id) + d.m_labels[0] + str(d.m_transformations[0] ))
    nx.draw_networkx(G, pos, with_labels = True)
    nx.draw_networkx_edge_labels(G, pos, labels = nx.get_edge_attributes(G, "c"))



