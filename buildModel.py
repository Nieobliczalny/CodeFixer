from config import config
from coder import Coder
from dictionary import Dictionary
import globals
import sys
import json

import random
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, RepeatVector, Dense, Activation, TimeDistributed

class ModelBuilder():
    def __init__(self):
        pass
    
    def build(self, checker):
        # Initialize coder
        print("Initializing coder...")
        self.dictionary = Dictionary(checker)
        self.coder = Coder(self.dictionary)
        self.totalDictionaryLength = self.dictionary.length() + globals.firstAvailableToken

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

        # Training model
        print("Training model...")
        for k in range(config.cfTrainNoEpochs):
            i = 0
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
                print("Done batch {0}-{1}".format(i, end))
                i += config.cfTrainBatchSize
            model.save_weights('checkpoint_epoch_{0}.{1}.hdf5'.format(k, checker))
        print("All done, exiting...")
    
def main(checker):
    builder = ModelBuilder()
    builder.build(checker)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No checker name given, exiting...")
    elif sys.argv[1] not in globals.availableCheckers:
        print("No handler found for specified checker, exiting...")
    else:
        main(sys.argv[1])