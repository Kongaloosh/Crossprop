#######################################################################
# Copyright (C) 2017 Shangtong Zhang(zhangshangtong.cpp@gmail.com)    #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################

from __future__ import print_function
import numpy as np
from functools import partial
from multiprocessing import Pool, Process
import pickle
from CrosspropLearner import *
from BackpropLearner import *
from GEOFF import *

fr = open('YAD.bin', 'rb')
totalTrainX, totalTestX, totalTrainY, totalTestY = pickle.load(fr)
totalTrainX = np.concatenate((totalTrainX, np.ones((totalTrainX.shape[0], 1))), 1)
totalTestX = np.concatenate((totalTestX, np.ones((totalTestX.shape[0], 1))), 1)
fr.close()
trainIndices = np.arange(totalTrainX.shape[0])
testIndices = np.arange(totalTestX.shape[0])

runs = 30
epochs = 200
# labels = ['Backprop', 'Crossprop', 'CrosspropV2']
# labels = ['Backprop', 'Crossprop']
labels = ['Backprop-Adam']
# labels = ['CrosspropV2']

def test(learner, testX, testY):
    error = 0.0
    for i in range(testX.shape[0]):
        error += 0.5 * np.power(learner.predict(testX[i, :]) - testY[i], 2)
    return error


def trainUnitWrapper(args):
    return trainUnit(*args)

def trainUnit(stepSize, hiddenUnits, nSample, startRun, endRun, trainErrors, testErrors):
    nTestExamples = 500
    nTrainExamples = nSample - nTestExamples
    random = np.random.RandomState()
    for run in range(startRun, endRun):
        random.shuffle(trainIndices)
        sampledTraining = trainIndices[: nTrainExamples]
        trainX = totalTrainX[sampledTraining, :]
        trainY = totalTrainY[sampledTraining]
        random.shuffle(testIndices)
        sampledTesting = testIndices[: nTestExamples]
        testX = totalTestX[sampledTesting, :]
        testY = totalTestY[sampledTesting]

        dims = [90, hiddenUnits]
        cp = CrossPropLearner(stepSize, list(dims))
        bp = BackpropLearner(stepSize, list(dims))
        bpAdam = BackpropLearner(stepSize, list(dims), gradient='adam')
        # learners = [bp, cp, cpv2]
        # learners = [bp, cp]
        learners = [bpAdam]

        for ind in range(len(labels)):
            print('Run', run, labels[ind], stepSize, hiddenUnits, nSample)
            for ep in range(epochs):
                # print('Run', run, labels[ind], 'Epoch', ep)
                indices = np.arange(trainX.shape[0])
                for i in indices:
                    learners[ind].predict(trainX[i, :])
                    trainErrors[ind, run, ep] += learners[ind].learn(trainY[i])
                testErrors[ind, run, ep] = test(learners[ind], testX, testY)
                # print(testErrors[ind, run, ep])
    return [trainErrors, testErrors]


def train(stepSize, hiddenUnits, nSample):
    trainErrors = np.zeros((len(labels), runs, epochs))
    testErrors = np.zeros(trainErrors.shape)

    nThreads = 6
    step = runs // nThreads
    startRun = []
    endRun = []
    for i in range(nThreads):
        startRun.append(i * step)
        endRun.append((i + 1) * step)
    endRun[-1] = runs
    args = []
    for i in range(len(startRun)):
        args.append((stepSize, hiddenUnits, nSample, startRun[i], endRun[i], trainErrors, testErrors))
        # trainUnit(stepSize, hiddenUnits, nSample, startRun[i], endRun[i], trainErrors, testErrors)
    results = Pool(nThreads).map(trainUnitWrapper, args)
    for trError, teError in results:
        trainErrors += trError
        testErrors += teError

    fw = open('data/YAD_adam_' + str(hiddenUnits) + '_' + str(stepSize) + '_' + str(nSample) + '.bin', 'wb')
    pickle.dump({'errors': [trainErrors, testErrors],
                 'stepSize': stepSize,
                 'hiddenUnits': hiddenUnits}, fw)
    fw.close()


samples = [6500, 9500, 12500]
hiddenUnits = [100, 300, 500, 700, 900, 1000, 2000]
stepSizes = np.power(2., np.arange(-17, -11))

for step in stepSizes:
    train(step, 100, 6500)
