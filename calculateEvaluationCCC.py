from __future__ import print_function
import argparse
import os
import csv
import sys


from scipy.stats import pearsonr
import numpy
import pandas


def mse(y_true, y_pred):
    from sklearn.metrics import mean_squared_error
    return mean_squared_error(y_true,y_pred)

def f1(y_true, y_pred):
    from sklearn.metrics import f1_score
    label = [0,1,2,3,4,5,6]
    return f1_score(y_true,y_pred,labels=label,average="micro")

def ccc(y_true, y_pred):
    true_mean = numpy.mean(y_true)
    true_variance = numpy.var(y_true)
    pred_mean = numpy.mean(y_pred)
    pred_variance = numpy.var(y_pred)

    rho,_ = pearsonr(y_pred,y_true)

    std_predictions = numpy.std(y_pred)

    std_gt = numpy.std(y_true)


    ccc = 2 * rho * std_gt * std_predictions / (
        std_predictions ** 2 + std_gt ** 2 +
        (pred_mean - true_mean) ** 2)

    return ccc, rho



def calculateCCC(validationFile, modelOutputFile):


    dataY = pandas.read_csv(validationFile, header=0, sep=",")

    dataYPred = pandas.read_csv(modelOutputFile, header=0, sep=",")

    dataYArousal = dataY["arousal"]
    dataYValence = dataY["valence"]
    dataYPredArousal = dataYPred["arousal"]
    dataYPredValence = dataYPred["valence"]

    arousalCCC, acor = ccc(dataYArousal, dataYPredArousal)
    arousalmse = mse(dataYArousal, dataYPredArousal)
    valenceCCC, vcor = ccc(dataYValence, dataYPredValence)
    valencemse = mse(dataYValence, dataYPredValence)

    print ("Arousal CCC: ", arousalCCC)
    print  ("Arousal Pearson Cor: ", acor)
    print ("Arousal MSE: ", arousalmse)
    print ("Valence CCC: ", valenceCCC)
    print ("Valence cor: ", vcor)
    print ("Valence MSE: ", valencemse)


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
