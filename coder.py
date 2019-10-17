from cxxlexer import CxxLexer
import globals
import numpy as np

class Coder():
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.lexer = CxxLexer()
        #define T_CHARACTER_LITERAL 256
        #define T_STRING_LITERAL 257
        #define T_NUMBER 346
        #define T_ID 347
        #define T_ESCAPED 348
        self.valuedTokens = [256, 257, 346, 347, 348]
    def encode(self, code, checkerData = [], unkList = [], reverse = True):
        # Coding process:
        # Tokenize
        tokens = self.tokenize(code)
        # Insert checker data at the end
        if len(checkerData) > 0:
            #define T_SOS 349
            tokens.append({'token': 349, 'has_value': False})
            tokens = tokens + checkerData
        # Replace tokens not in dictionary with UNKs
        (newTokens, unkList) = self.convertToUnks(tokens, unkList)
        # Convert to numeric list
        numList = self.convertToNumList(newTokens)
        # Reverse input
        if reverse:
            numList = numList[::-1]
        return (numList, unkList)
    def decode(self, numList, unkList, reverse = False):
        # Decoding process:
        # Reverse input
        if reverse:
            numList = numList[::-1]
        # Convert to token list
        tokens = self.convertFromNumList(numList)
        # Replace UNKs with proper tokens
        tokens = self.convertFromUnks(tokens, unkList)
        # If checker data exists - remove it
        tokenSosIndex = -1
        for i in range(len(tokens)):
            #define T_SOS 349
            if tokens[i]['token'] == '349':
                tokenSosIndex = i
                break
        if tokenSosIndex != -1:
            tokens = tokens[:tokenSosIndex]
        # Detokenize
        code = self.detokenize(tokens)
        return code
    def tokenize(self, code):
        return self.lexer.tokenize(code)
    def detokenize(self, tokens):
        return self.lexer.detokenize(tokens)
    def convertToUnks(self, tokens, unks = []):
        newTokens = []
        unkList = []
        unkData = []
        if len(unks) > 0:
            for unk in unks:
                unkList.append(unk['value'])
                unkData.append(unk)
        for token in tokens:
            token['token'] = int(token['token'])
            if token['token'] in self.valuedTokens:
                if self.dictionary.contains(token['value']):
                    token['value'] = self.dictionary.index(str(token['value']))
                    newTokens.append(token)
                else:
                    if token['value'] not in unkList:
                        unkList.append(token['value'])
                        unkData.append({'token': token['token'], 'value': token['value']})
                    #define T_UNK 351
                    newToken = {'token': 351, 'has_value': True, 'value': self.dictionary.index(str(unkList.index(token['value'])))}
                    newTokens.append(newToken)
            else:
                if not token['has_value']:
                    token['value'] = self.dictionary.index(globals.emptyValue)
                newTokens.append(token)
        return (newTokens, unkData)
    def convertFromUnks(self, tokens, unkList):
        newTokens = []
        for token in tokens:
            #define T_UNK 351
            if token['token'] == 351:
                unkNo = int(self.dictionary.get(token['value']))
                newToken = {'token': str(unkList[unkNo]['token']), 'has_value': True, 'value': str(unkList[unkNo]['value'])}
                newTokens.append(newToken)
            elif token['token'] in self.valuedTokens:
                token['token'] = str(token['token'])
                token['value'] = str(self.dictionary.get(token['value']))
                newTokens.append(token)
            else:
                token['token'] = str(token['token'])
                if not token['has_value'] and 'value' in token:
                    del token['value']
                newTokens.append(token)
        return newTokens
    def convertToNumList(self, tokens):
        numList = []
        for token in tokens:
            numList.append(token['token'])
            numList.append(token['value'] + 352) #Last known token is 351, so we start from 352
        return numList
    def convertFromNumList(self, numList):
        tokens = []
        numListLen = len(numList)
        noValueLabelIndex = self.dictionary.index(globals.emptyValue)
        i = 0
        while i < numListLen:
            numList[i + 1] -= 352
            token = {'token': numList[i], 'value': numList[i + 1]}
            if numList[i + 1] == noValueLabelIndex:
                token['has_value'] = False
            else:
                token['has_value'] = True
            tokens.append(token)
            i += 2
        return tokens
    def convertToOneHot(self, numList, outputArray):
        i = 0
        for num in numList:
            outputArray[i][num] = 1
            i += 1
        return outputArray
    def convertFromOneHot(self, oneHotList):
        numList = []
        for oneHot in oneHotList:
            numList.append(np.argmax(oneHot, 0))
        return numList
    def applyPadding(self, numList, noElements):
        noValueLabelIndex = self.dictionary.index(globals.emptyValue) + 352
        newValue = numList + [0, noValueLabelIndex] * noElements
        return newValue
    def removePadding(self, numList):
        paddingIndex = -1
        i = 0
        numListLen = len(numList)
        while i < numListLen:
            if numList[i] == 0:
                paddingIndex = i
                break
            i += 2
        return numList[:paddingIndex]