from config import config
from coder import Coder
from dictionary import Dictionary
import globals
import sys
import json

import random
from six.moves import urllib
import tempfile
import tensorflow as tf
import tensorflow.keras as keras

import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.models import load_model
from keras.layers import LSTM, RepeatVector, Dense, Activation, TimeDistributed

class ModelBuilder():
    def __init__(self):
        pass
    
    def build(self, checker, startK, startBatch):
        # Initialize coder
        print("Initializing coder...")
        self.dictionary = Dictionary(checker)
        self.coder = Coder(self.dictionary)
        self.totalDictionaryLength = self.dictionary.length() + globals.firstAvailableToken

        # Load training data from file
        print("Loading training data...")
        data = []
        with open(config.cfTrainFilenameFormat.format(checker), "r") as f:
            data = f.readlines()[:51]
        random.shuffle(data)
        dataLen = len(data)
        print("Done, fetched {0} records".format(dataLen))
        if dataLen < 1:
            print("No data found")
            return
        
        # Json load
        print("Converting to objects...")
        X = []
        Y = []
        xMaxLen = 0
        yMaxLen = 0
        for record in data:
            obj = json.loads(record[:-1])
            X.append(obj['x'])
            Y.append(obj['y'])
            if len(obj['x']) > xMaxLen:
                xMaxLen = len(obj['x'])
            if len(obj['y']) > yMaxLen:
                yMaxLen = len(obj['y'])
        
        # Padding
        print("Counted input and output lengths (X = {0}, Y = {1})...".format(xMaxLen, yMaxLen))
        
        # Preparing model
        print("Preparing model...")
        batchSaveIndex = 0
        batchSaveCounter = 0
        batchSaveThreshold = 10#000
        if startK == 0 and startBatch == 0:
            model = Sequential()
            model.add(LSTM(config.cfTrainHiddenSize, input_shape=(xMaxLen, self.totalDictionaryLength)))
            model.add(RepeatVector(yMaxLen))
            for _ in range(config.cfTrainNumLayers):
                model.add(LSTM(config.cfTrainHiddenSize, return_sequences=True))
            model.add(TimeDistributed(Dense(self.totalDictionaryLength)))
            model.add(Activation('softmax'))
            model.compile(loss='categorical_crossentropy',
                        optimizer='rmsprop',
                        metrics=['accuracy'])
        else:
            modelFormat = 'checkpoint_epoch_{0}.{1}.h5'.format(startK - 1, checker)
            if startBatch > 0:
                batchSaveIndex = int(startBatch / batchSaveThreshold)
                modelFormat = 'checkpoint_epoch_b{2}.{0}.{1}.h5'.format(startK, checker, batchSaveIndex - 1)
            model = load_model(modelFormat)

        # Training model
        print("Training model...")
        for k in range(startK, config.cfTrainNoEpochs):
            i = 0
            if k == startK:
                i = startBatch
            while i < dataLen:
                end = i + config.cfTrainBatchSize
                if end > dataLen:
                    end = dataLen
                X_s = np.zeros((end - i, xMaxLen, self.totalDictionaryLength))
                Y_s = np.zeros((end - i, yMaxLen, self.totalDictionaryLength))
                for j in range(i, end):
                    valueX = X[j]
                    noZerosToPad = int((xMaxLen - len(valueX)) / 2)
                    if noZerosToPad > 0:
                        valueX = self.coder.applyPadding(valueX, noZerosToPad)
                    valueY = Y[j]
                    noZerosToPad = int((yMaxLen - len(valueY)) / 2)
                    if noZerosToPad > 0:
                        valueY = self.coder.applyPadding(valueY, noZerosToPad)
                    X_s[j - i] = self.coder.convertToOneHot(valueX, np.zeros((xMaxLen, self.totalDictionaryLength)))
                    Y_s[j - i] = self.coder.convertToOneHot(valueY, np.zeros((yMaxLen, self.totalDictionaryLength)))
                model.fit(X_s, Y_s, batch_size=config.cfTrainBatchSize, epochs=1, verbose=2)
                print("[{2}] Done batch {0}-{1}".format(i, end, k))
                i += config.cfTrainBatchSize
                batchSaveCounter += config.cfTrainBatchSize
                if batchSaveCounter >= batchSaveThreshold:
                    batchSaveCounter = 0
                    model.save('checkpoint_epoch_b{2}.{0}.{1}.h5'.format(k, checker, batchSaveIndex))
                    batchSaveIndex += 1
            model.save('checkpoint_epoch_{0}.{1}.h5'.format(k, checker))
            batchSaveIndex = 0
        print("All done, exiting...")
    
def main(checker, startK = 0, startBatch = 0):
    builder = ModelBuilder()
    builder.build(checker, startK, startBatch)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No checker name given, exiting...")
    elif sys.argv[1] not in globals.availableCheckers:
        print("No handler found for specified checker, exiting...")
    else:
        k = 0
        b = 0
        if len(sys.argv) > 2:
            k = int(sys.argv[2])
        if len(sys.argv) > 3:
            b = int(sys.argv[3])
        main(sys.argv[1], k, b)