from __future__ import print_function
import argparse
import os
import csv
import sys


from scipy.stats import pearsonr
import numpy

def ccc(y_true, y_pred):
    true_mean = numpy.mean(y_true)
    pred_mean = numpy.mean(y_pred)
    rho,_ = pearsonr(y_pred,y_true)
    std_predictions = numpy.std(y_pred)
    std_gt = numpy.std(y_true)

    ccc = 2 * rho * std_gt * std_predictions / (
        std_predictions ** 2 + std_gt ** 2 +
        (pred_mean - true_mean) ** 2)

    return ccc

def getUtterancesArousalAndValence(readingFile, videoName, isFileValidation=True):

    arousals = []
    valences = []

    foundVideo = False
    with open(readingFile, 'rb') as csvfile:

        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        rowNumber = 0
        for row in spamreader:
            if rowNumber > 0:

                if isFileValidation:
                    video = row[3]
                    arousal = row[5]
                    valence = row[6]
                else:

                    video = row[3]
                    arousal = row[5]
                    valence = row[6]

                if video == videoName:
                    arousals.append(float(arousal))
                    valences.append(float(valence))
                    foundVideo = True

                elif foundVideo:
                    break

                else: foundVideo = False

            rowNumber = rowNumber+1

    return (arousals,valences)



def calculateCCC(validationFile, modelOutputFile):


    cccArousal = []
    cccValence = []

    lastVideo = "none"
    with open(validationFile, 'rb') as csvfile:

        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        rowNumber = 0
        for row in spamreader:
            if rowNumber > 0:

                validationVideo = row[3]
                if lastVideo == "none" or not lastVideo == validationVideo:

                    validationArousal,validationValence = getUtterancesArousalAndValence(validationFile, validationVideo)
                    modelArousal, modelValence = getUtterancesArousalAndValence(modelOutputFile, validationVideo)
                    cccArousal.append(ccc(validationArousal,modelArousal))
                    cccValence.append(ccc(validationArousal, modelArousal))

                    lastVideo = validationVideo

            rowNumber = rowNumber+1


    cccArousal = numpy.array(cccArousal)
    cccValence = numpy.array(cccValence)
    print ("CCC Arousals:", cccArousal)
    print ("CCC Valences:", cccValence)

    print ("Mean CCC Arousal:", cccArousal.mean())
    print ("Mean CCC Valence:", cccValence.mean())



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("validationFile")
    parser.add_argument("modelOutputFile")

    opt = parser.parse_args()
    if not os.path.exists(opt.validationFile):
        print("Cannot find validation File")
        sys.exit(-1)

    if not os.path.exists(opt.modelOutputFile):
        print("Cannot find modelOutput File")
        sys.exit(-1)

    calculateCCC(opt.validationFile, opt.modelOutputFile)