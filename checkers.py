import re

class Checkers():
    def extractTokensForChecker(self, checkerName, message):
        if checkerName == 'deadcode.DeadStores':
            return self.extractTokenDeadStores(message)
        if checkerName == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            return self.extractTokenTautOORCmp(message)
        #TODO: Custom errors
        raise ValueError
    def extractTokenDeadStores(self, message):
        # Value stored to '<TOKEN_1>' is never read
        #define T_ID 347
        pattern = "'(.+)'"  
        varName = re.search(pattern, message).group(0)[1:-1]
        return [{'token': 347, 'has_value': True, 'value': varName}]
    def extractTokenTautOORCmp(self, message):
        # result of comparison of constant <TOKEN_1> with expression of type '<TOKEN_NOT_USED>' is always <TOKEN_2>
        #define T_ID 347
        pattern = "(-?[0-9]+)"
        constant = re.search(pattern, message).group(0)
        compValue = 'false'
        if message[-4:] == 'true':
            compValue = 'true'
        return [{'token': 347, 'has_value': True, 'value': constant}, {'token': 347, 'has_value': True, 'value': compValue}]
    def getModelStatsForChecker(self, checkerName):
        if checkerName == 'deadcode.DeadStores':
            return self.getModelStatsDeadStores()
        if checkerName == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            return self.getModelStatsTautOORCmp()
        #TODO: Custom errors
        raise ValueError
    def getModelStatsDeadStores(self):
        return (75, 75, 10)
    def getModelStatsTautOORCmp(self):
        return (90, 90, 15)