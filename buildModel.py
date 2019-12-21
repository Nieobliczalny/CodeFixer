from config import config
from coder import Coder
from dictionary import Dictionary
import globals
import sys
import json
import gc

import random
from six.moves import urllib
import tempfile
import tensorflow as tf
tf.keras.backend.clear_session()

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LSTM, RepeatVector, Dense, Activation, TimeDistributed

class ModelBuilder():
    '''
    def datagen(self, batchSize, xMaxLen, yMaxLen):
        while self.ObjInd < self.ObjMax:
            end = batchSize
            if end + self.ObjInd > self.ObjMax:
                end = self.ObjMax - self.ObjInd
            x = np.zeros((end, xMaxLen, self.totalDictionaryLength))
            y = np.zeros((end, yMaxLen, self.totalDictionaryLength))
            for j in range(self.ObjInd, self.ObjInd + end):
                valueX = self.X[j]
                noZerosToPad = xMaxLen - len(valueX)
                if noZerosToPad > 0:
                    valueX = self.coder.applyPadding(valueX, noZerosToPad)
                valueY = self.Y[j]
                noZerosToPad = yMaxLen - len(valueY)
                if noZerosToPad > 0:
                    valueY = self.coder.applyPadding(valueY, noZerosToPad)
                self.coder.convertToOneHot(valueX, x[j - self.ObjInd])
                self.coder.convertToOneHot(valueY, y[j - self.ObjInd])
            self.ObjInd += end
            #some code here to load and manipulate data into x and y. Mostly numpy functions
            yield x,y
    '''
    
    def build(self, checker, startK, startBatch):
        # Initialize coder
        print("Initializing coder...")
        self.dictionary = Dictionary(checker)
        self.coder = Coder(self.dictionary)
        self.totalDictionaryLength = self.dictionary.length()# + globals.firstAvailableToken

        # Load training data from file
        print("Loading training data...")
        data = []
        with open(config.cfTrainFilenameFormat.format(checker), "r") as f:
            data = f.readlines()
        random.shuffle(data)
        dataLen = len(data)
        print("Done, fetched {0} records".format(dataLen))
        if dataLen < 1:
            print("No data found")
            return
        
        # Json load
        print("Converting to objects...")
        self.X = []
        self.Y = []
        self.ObjInd = 0
        self.ObjMax = dataLen
        xMaxLen = 0
        yMaxLen = 0
        for record in data:
            obj = json.loads(record[:-1])
            self.X.append(obj['x'])
            self.Y.append(obj['y'])
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
        batchSaveThreshold = 10000
        
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
        '''
        print("Converting data...")
        X_s = np.zeros((dataLen, xMaxLen, self.totalDictionaryLength))
        Y_s = np.zeros((dataLen, yMaxLen, self.totalDictionaryLength))
        for j in range(dataLen):
            valueX = X[j]
            noZerosToPad = xMaxLen - len(valueX)
            if noZerosToPad > 0:
                valueX = self.coder.applyPadding(valueX, noZerosToPad)
            valueY = Y[j]
            noZerosToPad = yMaxLen - len(valueY)
            if noZerosToPad > 0:
                valueY = self.coder.applyPadding(valueY, noZerosToPad)
            self.coder.convertToOneHot(valueX, X_s[j])
            self.coder.convertToOneHot(valueY, Y_s[j])
        '''
        # Training model
        '''
        print("Training...")
        for k in range(startK, config.cfTrainNoEpochs):
            #model.fit(X_s, Y_s, epochs=1)#, validation_split=0.2)
            model.fit(self.datagen(config.cfTrainBatchSize, xMaxLen, yMaxLen), epochs=1, steps_per_epoch=103)#, validation_split=0.2)
            model.save('checkpoint_epoch_{0}.{1}.h5'.format(k, checker))
        '''
        #"""
        print("Training model...")
        for k in range(startK, config.cfTrainNoEpochs):
            i = 0
            model.reset_metrics()
            if k == startK:
                i = startBatch
            while i < dataLen:
                end = i + config.cfTrainBatchSize
                if end > dataLen:
                    end = dataLen
                #'''
                X_s = np.zeros((end - i, xMaxLen, self.totalDictionaryLength))
                Y_s = np.zeros((end - i, yMaxLen, self.totalDictionaryLength))
                for j in range(i, end):
                    valueX = self.X[j]
                    noZerosToPad = xMaxLen - len(valueX)#int((xMaxLen - len(valueX)) / 2)
                    if noZerosToPad > 0:
                        valueX = self.coder.applyPadding(valueX, noZerosToPad)
                    valueY = self.Y[j]
                    noZerosToPad = yMaxLen - len(valueY)#int((yMaxLen - len(valueY)) / 2)
                    if noZerosToPad > 0:
                        valueY = self.coder.applyPadding(valueY, noZerosToPad)
                    zerosX = np.zeros((xMaxLen, self.totalDictionaryLength))
                    zerosY = np.zeros((yMaxLen, self.totalDictionaryLength))
                    X_s[j - i] = self.coder.convertToOneHot(valueX, zerosX)
                    Y_s[j - i] = self.coder.convertToOneHot(valueY, zerosY)
                result = model.train_on_batch(X_s, Y_s, reset_metrics=False)
                #'''
                #result = model.train_on_batch(X_s[i:end], Y_s[i:end])
                #del X_s
                #del Y_s
                print("[{2}] Done batch {0}-{1} (loss: {3:.3f}, accuracy: {4:.3f})".format(i, end, k, result[0], result[1]))
                i += config.cfTrainBatchSize
                batchSaveCounter += config.cfTrainBatchSize
                if batchSaveCounter >= batchSaveThreshold:
                    batchSaveCounter = 0
                    model.save('checkpoint_epoch_b{2}.{0}.{1}.h5'.format(k, checker, batchSaveIndex))
                    batchSaveIndex += 1
            model.save('checkpoint_epoch_{0}.{1}.h5'.format(k, checker))
            batchSaveIndex = 0
            batchSaveCounter = 0
        #"""
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