import os
import csv

def ComputeScoresTemporal(dependencies, truth, searchSpaceSize, algorithms, matching_params) :
    results = []

    for err in matching_params :
        true_positives = []
        true_negatives = []
        false_positives = []
        false_negatives = []
        
        precision = []
        recall = []
        f1score = []
        accuracy = []

        for i in range (len(dependencies)) :
            if algorithms[i] :
                tp_r = 0
                tn_r = 0
                fp_r = 0
                fn_r = 0
                #counting false positives
                for dep in dependencies[i] :
                    found_relaxed = False
                    for tr in truth :
                        if tr["premise"] == dep["premise"] and tr["conclusion"] == dep["conclusion"] :
                            if abs( tr["transformation"][0] - dep["transformation"][0] ) <= err and  abs( tr["transformation"][1] - dep["transformation"][1] ) <= err  :
                                found_relaxed = True
                                break
                    if not found_relaxed :
                        fp_r = fp_r + 1 
                #counting false negatives and true positives
                for tr in truth :
                    found_relaxed = False
                    for dep in dependencies[i] :
                        if tr["premise"] == dep["premise"] and tr["conclusion"] == dep["conclusion"] :
                            tp_r = tp_r + 1
                            found_relaxed = True
                            break
                    if not found_relaxed : 
                        fn_r = fn_r + 1
                tn_r = searchSpaceSize - (tp_r + fn_r + fp_r)  
                    
                true_positives.append(tp_r)
                true_negatives.append(tn_r)
                false_positives.append(fp_r)
                false_negatives.append(fn_r)

                # Precision relaxed
                if tp_r + fp_r > 0 :
                    precision.append( tp_r / (tp_r + fp_r) )
                else :  
                    precision.append(0)
                # Recall relaxed
                if len(truth) != 0 and tp_r != 0 :
                    recall.append( tp_r / len(truth))
                elif len(truth) == 0 :
                    recall.append(1)
                else :
                    recall.append(0)
                # F1-Score relaxed
                if precision[-1]*recall[-1] != 0 :
                    f1score.append(  2 * (precision[-1] * recall[-1]) / (precision[-1] + recall[-1]) )
                else :
                    f1score.append(0)
                # Accuracy relaxed
                accuracy.append( (tp_r + tn_r ) / searchSpaceSize  )
        results.extend(precision)
        results.extend(recall)
        results.extend(f1score)
        results.extend(accuracy)
        

    return results

def ComputeScoresQualitatif(dependencies, truth, searchSpaceSize, algorithms) :
    # relaxed 
    #[precisions , recalls, f1scores, accuracies]
    result = []
    true_positives_relaxed = []
    true_negatives_relaxed = []
    false_positives_relaxed = []
    false_negatives_relaxed = []
    
    precision_relaxed = []
    recall_relaxed = []
    f1score_relaxed = []
    accuracy_relaxed = []

    for i in range (len(dependencies)) :
        if algorithms[i] :
            tp_r = 0
            tn_r = 0
            fp_r = 0
            fn_r = 0
            #counting false positives
            for dep in dependencies[i] :
                found_relaxed = False
                for tr in truth :
                    if tr["premise"] == dep["premise"] and tr["conclusion"] == dep["conclusion"] :
                        found_relaxed = True
                        break
                if not found_relaxed :
                    fp_r = fp_r + 1 
            #counting false negatives and true positives
            for tr in truth :
                found_relaxed = False
                for dep in dependencies[i] :
                    if tr["premise"] == dep["premise"] and tr["conclusion"] == dep["conclusion"] :
                        tp_r = tp_r + 1
                        found_relaxed = True
                        break
                if not found_relaxed : 
                    fn_r = fn_r + 1

            tn_r = searchSpaceSize - (tp_r + fn_r + fp_r)  
            
            true_positives_relaxed.append(tp_r)
            true_negatives_relaxed.append(tn_r)
            false_positives_relaxed.append(fp_r)
            false_negatives_relaxed.append(fn_r)

            # Precision relaxed
            if tp_r + fp_r > 0 :
                precision_relaxed.append( tp_r / (tp_r + fp_r) )
            else :  
                precision_relaxed.append(0)
            # Recall relaxed
            if len(truth) != 0 and tp_r != 0 :
                recall_relaxed.append( tp_r / len(truth))
            elif len(truth) == 0 :
                recall_relaxed.append(1)
            else :
                recall_relaxed.append(0)
            # F1-Score relaxed
            if precision_relaxed[-1]*recall_relaxed[-1] != 0 :
                f1score_relaxed.append(  2 * (precision_relaxed[-1] * recall_relaxed[-1]) / (precision_relaxed[-1] + recall_relaxed[-1]) )
            else :
                f1score_relaxed.append(0)
            # Accuracy relaxed
            accuracy_relaxed.append( (tp_r + tn_r ) / searchSpaceSize  )
    
      
    result.extend(precision_relaxed)
    result.extend(recall_relaxed)
    result.extend(f1score_relaxed)
    result.extend(accuracy_relaxed)
    
    return result


def ComputeScores(dependencies, truth, searchSpaceSize, algorithms, matching_params, relaxed = True) : 
    results = []
    results.extend(ComputeScoresQualitatif(dependencies, truth, searchSpaceSize, algorithms))
    if relaxed : 
        results.extend(ComputeScoresTemporal(dependencies, truth, searchSpaceSize, algorithms, matching_params))
    return results

#saves dependencies in specified folder
def saveDependencies(dependencies, test_directory, name_folder, algorithms, algorithms_labels) :
    directory = os.path.join(test_directory, name_folder)
    os.mkdir(directory)

    for i in range(len(algorithms)):
        if algorithms[i] :
            f = open(os.path.join(directory, algorithms_labels[i] + ".txt"), "w")
            for dep in dependencies[i]:
                f.write(str(dep) + "\n")
            f.close()

#append a row in a csv file
def appendLineToCsv(line, filepath) : 
    with open(filepath, "a", newline='') as csvFile :
        writer = csv.writer(csvFile)
        writer.writerow(line)

# returns [max_duration, avg_length, avg_density, avg_number]
def GetDataSetStat(streams) :
    avg_length = 0
    avg_number = 0
    tmin = streams[0].m_intervals[0].m_start
    tmax = streams[0].m_intervals[-1].m_end
    for stream in streams:
        avg_length = avg_length + stream.m_length
        avg_number = avg_number + stream.m_size
        if stream.m_intervals[0].m_start < tmin : 
            tmin = stream.m_intervals[0].m_start
        if stream.m_intervals[-1].m_end > tmax :
            tmax = stream.m_intervals[-1].m_end
        
    duration = tmax - tmin
    avg_length = avg_length / len(streams)
    avg_number = avg_number / len(streams)
    avg_density = avg_length / duration
    return [duration, avg_length, avg_density, avg_number]
