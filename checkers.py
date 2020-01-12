import re

class Checkers():
    def extractTokensForChecker(self, checkerName, message):
        if checkerName == 'deadcode.DeadStores':
            return self.extractTokenDeadStores(message)
        if checkerName == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            return self.extractTokenTautOORCmp(message)
        if checkerName == 'clang-diagnostic-unused-parameter':
            return self.extractTokenUnusedParam(message)
        if checkerName == 'clang-diagnostic-constant-conversion':
            return self.extractTokenConstConv(message)
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
    def extractTokenUnusedParam(self, message):
        # unused parameter '<TOKEN_1>'
        #define T_ID 347
        pattern = "'(.+)'"  
        varName = re.search(pattern, message).group(0)[1:-1]
        return [{'token': 347, 'has_value': True, 'value': varName}]
    def extractTokenConstConv(self, message):
        # implicit conversion from '<TOKEN_NOT_USED>' to '<TOKEN_1>' changes value from <TOKEN_2> to <TOKEN_NOT_USED>
        #define T_ID 347
        pattern = "to '([a-zA-Z0-9_ ]+)'"
        newType = re.search(pattern, message).group(1)
        pattern = "from (-?[0-9]+)"
        constant = re.search(pattern, message).group(1)
        return [{'token': 347, 'has_value': True, 'value': constant}, {'token': 347, 'has_value': True, 'value': newType}]
    def getModelStatsForChecker(self, checkerName):
        if checkerName == 'deadcode.DeadStores':
            return self.getModelStatsDeadStores()
        if checkerName == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            return self.getModelStatsTautOORCmp()
        if checkerName == 'clang-diagnostic-unused-parameter':
            return self.getModelStatsUnusedParams()
        if checkerName == 'clang-diagnostic-constant-conversion':
            return self.getModelStatsConstConv()
        #TODO: Custom errors
        raise ValueError
    def getModelStatsDeadStores(self):
        return (75, 75, 10)
    def getModelStatsTautOORCmp(self):
        return (90, 90, 15)
    def getModelStatsUnusedParams(self):
        return (90, 100, 15)
    def getModelStatsConstConv(self):
        return (90, 95, 15)