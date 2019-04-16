import sys
import copy
from itertools import filterfalse
sys.path.append("..\\")

from models.dependency import Dependency
from models.streams import Stream
from models.streams import Transformation
from models.streams import Confidence
from models.streams import ValidityThreshold

from algorithms.utils_CTDMiner import postProcessResults
from algorithms.utils_CTDMiner import prePruning
from algorithms.utils_CTDMiner import MergingExtension
from algorithms.utils_CTDMiner import Matching
from algorithms.utils_CTDMiner import BuildDisjunctions 

from algorithms.ITLD import Itld

def CTDMinerBaseline(streams : [Stream], tmin, tmax, duration):
    final_results = []
    #building dependencies of size 1
    premises : [Dependency] = []
    for s in streams :
        premises.append(Dependency(s.m_label , s))
    while len(premises) != 0: 
        new_premises = []
        for p in premises :
            extended = False
            for c in streams :
                if c.m_label not in p.m_labels :
                    results, confidences, transformations = Itld(p.m_intersection, c, tmin, tmax, duration) 
                    for i in range(len(results)) :
                        extended = True
                        new_p = p.getExtentedDependency(c.m_label, transformations[i], confidences[i], results[i])
                        if len(new_p.m_labels) == 2 :
                            new_p.setFirstIntersction(results[i])
                        new_premises.append(new_p)
            if not extended and len(p.m_labels) > 1 :
                final_results.append(p)
        #post pruning with premise
        premises = copy.deepcopy(new_premises)
    #BuildDisjunctions(final_results, duration)
    return final_results



