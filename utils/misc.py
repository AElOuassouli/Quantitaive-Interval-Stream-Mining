import os
import csv

def saveDependencies(results, alg_labels, test_directory, name_folder) :
    directory = os.path.join(test_directory, name_folder)
    os.mkdir(directory)

    for i in range(len(results)):
        f = open(os.path.join(directory, alg_labels[i] + ".txt"), "w")
        for dep in results[i]:
            f.write(str(dep) + "\n")
        f.close()

#append a row in a csv file
def appendLineToCsv(line, filepath) : 
    with open(filepath, "a", newline='') as csvFile :
        writer = csv.writer(csvFile)
        writer.writerow(line)
