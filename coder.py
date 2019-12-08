from cxxlexer import CxxLexer
import globals
import numpy as np
import re

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
        self.patToken = re.compile("^T_([0-9]+)$")
        self.patUnk = re.compile("^UNK_([0-9]+)$")
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
            if reverse:
                tokens = tokens[:tokenSosIndex]
            else:
                tokens = tokens[tokenSosIndex + 1:]
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
                    newToken = {'token': 351, 'has_value': True, 'value': self.dictionary.index("UNK_{0}".format(unkList.index(token['value'])))}
                    newTokens.append(newToken)
            else:
                value = "T_{0}".format(token['token'])
                if self.dictionary.contains(value):
                    token['value'] = self.dictionary.index(value)
                    newTokens.append(token)
                else:
                    if value not in unkList:
                        unkList.append(value)
                        unkData.append({'token': token['token'], 'value': value})
                    #define T_UNK 351
                    newToken = {'token': 351, 'has_value': True, 'value': self.dictionary.index("UNK_{0}".format(unkList.index(value)))}
                    newTokens.append(newToken)
        return (newTokens, unkData)
    def convertFromUnks(self, tokens, unkList):
        newTokens = []
        for token in tokens:
            #define T_UNK 351
            if token['token'] == 351:
                try:
                    unkNo = token['value']
                    newToken = {'token': str(unkList[unkNo]['token']), 'has_value': True, 'value': str(unkList[unkNo]['value'])}
                    newTokens.append(newToken)
                except ValueError:
                    pass # Ignore invalid tokens
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
            numList.append(token['value'])
        return numList
    def convertFromNumList(self, numList):
        tokens = []
        numListLen = len(numList)
        i = 0
        while i < numListLen:
            value = str(self.dictionary.get(numList[i]))
            match = self.patToken.match(value)
            if match:
                tokens.append({'token': int(match.group(1)), 'has_value': False})
            else:
                match = self.patUnk.match(value)
                if match:
                    tokens.append({'token': 351, 'value': int(match.group(1)), 'has_value': True})
                else:
                    # Ignore specific token ID, since all values tokens are processed the same
                    tokens.append({'token': 347, 'value': numList[i], 'has_value': True})
            i += 1
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
        newValue = numList + [0] * noElements
        return newValue
    def removePadding(self, numList):
        paddingIndex = -1
        i = 0
        numListLen = len(numList)
        while i < numListLen:
            if numList[i] == 0:
                paddingIndex = i
                break
            i += 1
        return numList[:paddingIndex]