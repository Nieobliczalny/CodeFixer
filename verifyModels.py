from config import config
from ccdatabase import CCDatabase
from codechecker import CodeChecker
from coder import Coder
from checkers import Checkers
from dictionary import Dictionary
from extractCode import CodeExtractor
from gitprovider import GitProvider
from posixdiffer import POSIXDiffer
import globals
import os
import re
import sqlite3
from collections import deque
import concurrent.futures

from tensorflow.keras.models import load_model
import tensorflow.keras

import numpy as np

#Checkout before use!

def convertFilePathToRepoRelativePath(path):
    return os.path.relpath(path, config.getRepoDir())

def findMatchingDefine(code, value):
    patValue = '({0})'
    patName = '[ \t]([0-9a-zA-Z_]+)[ \t]'
    for line in code:
        if line[:7] == '#define':
            if re.search(patValue.format(value), line):
                return re.search(patName, line).group(1)
    return None

def fixDeadStore(code, bugData):
    if bugData.getLine() == 1:
        return ["\n"] + code[1:]
    elif bugData.getLine() == len(code):
        return code[:-1] + ["\n"]
    else:
        return code[0:(bugData.getLine() - 1)] + ["\n"] + code[bugData.getLine():]

def findTautOORCmp(code, bugData):
    tokens = checkers.extractTokensForChecker('clang-diagnostic-tautological-constant-out-of-range-compare', bugData.getMessage())
    line = code[bugData.getLine() - 1]
    pat = "\([^\(]*{0}\)".format(tokens[0]['value'])
    match = re.search(pat, line)
    if match is None:
        pat = "\([^\(]*{0}\)".format(findMatchingDefine(code, tokens[0]['value']))
        match = re.search(pat, line)
    match = match.group(0)
    newLine = line.replace(match, '({0})'.format(tokens[1]['value']))
    return code[0:(bugData.getLine() - 1)] + [newLine] + code[bugData.getLine():]

def fixUnusedParam(code, bugData):
    newLine = '// codechecker_intentional [clang-diagnostic-unused-parameter] Suppress\n'
    return code[0:(bugData.getLine() - 1)] + [newLine] + code[(bugData.getLine() - 1):]

def fixConstConv(code, bugData):
    line = code[bugData.getLine() - 1]
    if line.count('=') > 5:
        newLine = '// codechecker_intentional [clang-diagnostic-constant-conversion] Suppress\n{0}'.format(line)
    else:
        tokens = checkers.extractTokensForChecker('clang-diagnostic-constant-conversion', bugData.getMessage())
        line = code[bugData.getLine() - 1]
        newLine = line.replace(tokens[0]['value'], '({0}){1}'.format(tokens[1]['value'], tokens[0]['value']))
        if line == newLine:
            tokens[0]['value'] = findMatchingDefine(code, tokens[0]['value'])
            if tokens[0]['value'] is not None:
                newLine = line.replace(tokens[0]['value'], '({0}){1}'.format(tokens[1]['value'], tokens[0]['value']))
        if line == newLine:
            s = re.search('= (.*);', line)
            expr = s.group(1)
            newLine = line.replace(expr, '({0})({1})'.format(tokens[1]['value'], expr))
    return code[0:(bugData.getLine() - 1)] + [newLine] + code[bugData.getLine():]

def fix(code, bugData):
    if bugData.getChecker() == 'deadcode.DeadStores':
        return fixDeadStore(code, bugData)
    if bugData.getChecker() == 'clang-diagnostic-tautological-constant-out-of-range-compare':
        return findTautOORCmp(code, bugData)
    if bugData.getChecker() == 'clang-diagnostic-unused-parameter':
        return fixUnusedParam(code, bugData)
    if bugData.getChecker() == 'clang-diagnostic-constant-conversion':
        return fixConstConv(code, bugData)
    return None

ccdb = CCDatabase(config.getCcDbFile())
db = sqlite3.connect('../Results/db.sqlite')
cursor = db.cursor()
cursor.execute('SELECT * FROM bugs')
dataFromDb = cursor.fetchall()
bugs = []
bugsPerFile = {}
BUG_NOT_PROCESSED = 0
vcs = GitProvider(config.getRepoDir())
checkers = Checkers()
currentCommit = vcs.getAllVersions(config.getBranch())[0]
bugDataList = {}
fileContents = {}
codechecker = CodeChecker(config.getRepoDir())

if len(dataFromDb) > 0:
    print("Skipping steps 1-2, DB already filled with data")
    for bug in dataFromDb:
        if bug[2] not in bugsPerFile:
            bugsPerFile[bug[2]] = []
        if bug[3] == BUG_NOT_PROCESSED:
            bugDataList[bug[0]] = ccdb.getNotResolvedBugData(bug[0])
            bugsPerFile[bug[2]].append(bug[0])
else:
    # 1.
    print("Step 1")
    lists = ['../Results/ID_checker1.txt', '../Results/ID_checker2.txt', '../Results/ID_checker3.txt', '../Results/ID_checker4.txt']
    checkersCount = len(globals.availableCheckers)
    for i in range(checkersCount):
        with open(lists[i], 'rt') as f:
            lines = f.readlines()
            ids = [int(x[:-1]) for x in lines]
            for id in ids:
                bugs.append([id, globals.availableCheckers[i]])

    # 2.
    print("Step 2")
    for bug in bugs:
        bugData = ccdb.getNotResolvedBugData(bug[0])
        if bugData is not None:
            bug.append(convertFilePathToRepoRelativePath(bugData.getFile()))
            cursor.execute('INSERT INTO bugs (id, checker, file) VALUES ({0}, "{1}", "{2}")'.format(bug[0], bug[1], bug[2]))
            if bug[2] not in bugsPerFile:
                bugsPerFile[bug[2]] = []
            bugDataList[bug[0]] = bugData
            bugsPerFile[bug[2]].append(bug[0])

    db.commit()
    cursor.close()

# 3., 4., 5.
model1 = load_model(config.cfModelFilenameFormat.format('deadcode.DeadStores'))
model2 = load_model(config.cfModelFilenameFormat.format('clang-diagnostic-tautological-constant-out-of-range-compare'))
model3 = load_model(config.cfModelFilenameFormat.format('clang-diagnostic-unused-parameter'))
model4 = load_model(config.cfModelFilenameFormat.format('clang-diagnostic-constant-conversion'))
dictionary1 = Dictionary('deadcode.DeadStores')
dictionary2 = Dictionary('clang-diagnostic-tautological-constant-out-of-range-compare')
dictionary3 = Dictionary('clang-diagnostic-unused-parameter')
dictionary4 = Dictionary('clang-diagnostic-constant-conversion')
coder1 = Coder(dictionary1)
coder2 = Coder(dictionary2)
coder3 = Coder(dictionary3)
coder4 = Coder(dictionary4)
totalDictionaryLength1 = dictionary1.length()
totalDictionaryLength2 = dictionary2.length()
totalDictionaryLength3 = dictionary3.length()
totalDictionaryLength4 = dictionary4.length()

def ProcessBugsInFile(fileName):
    # 5.1.
    # 5.2.
    for bug in bugsPerFile[fileName]:
        bugData = bugDataList[bug]
        cleanFn = fileName[:-4]
        fn = '../Results/Analysis/{0}_{1}_{2}.txt'.format(cleanFn, bug, bugData.getChecker())
        repoFn = os.fsdecode(os.path.join(os.fsencode(config.getRepoDir()), os.fsencode(fileName)))
        if os.path.isfile(fn):
            continue
        model = None
        if bugData.getChecker() == 'deadcode.DeadStores':
            model = model1
            coder = coder1
            totalDictionaryLength = totalDictionaryLength1
        if bugData.getChecker() == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            model = model2
            coder = coder2
            totalDictionaryLength = totalDictionaryLength2
        if bugData.getChecker() == 'clang-diagnostic-unused-parameter':
            model = model3
            coder = coder3
            totalDictionaryLength = totalDictionaryLength3
        if bugData.getChecker() == 'clang-diagnostic-constant-conversion':
            model = model4
            coder = coder4
            totalDictionaryLength = totalDictionaryLength4
        MODEL_X_MAX_LEN = model.get_layer(index = 0).input_shape[1]

        # 5.2.1.
        fullCodeWithBug = fileContents[fileName]
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromText(fullCodeWithBug)
        extractor.extractBugCode()
        bugCodeFragment = extractor.getBugCodeFragment()

        # 5.2.2.
        fullCodeWithoutBug = ''.join(fix(extractor.code, bugData))
        diff = POSIXDiffer().diff(fullCodeWithBug, fullCodeWithoutBug)
        extractor.loadDiff(diff)
        try:
            extractor.extractFixCode()
        except ValueError as ve:
            print("Unable to generate expected fix for bug #{0} ({1}), checker = {2}".format(bug, fileName, bugData.getChecker()))
            continue
        expectedFixCodeFragment = extractor.getFixCodeFragment()

        # 5.2.3.
        checkerInfo = checkers.extractTokensForChecker(bugData.getChecker(), bugData.getMessage())
        encodedBugData, initialUnkList = coder.encode(bugCodeFragment, checkerData = checkerInfo)
        noZerosToPad = MODEL_X_MAX_LEN - len(encodedBugData)
        if noZerosToPad > 0:
            encodedBugData = coder.applyPadding(encodedBugData, noZerosToPad)
        X = np.zeros((1, MODEL_X_MAX_LEN, totalDictionaryLength))
        X[0] = coder.convertToOneHot(encodedBugData, np.zeros((MODEL_X_MAX_LEN, totalDictionaryLength)))
        Y = coder.convertFromOneHot(model.predict(X)[0])
        while (Y[-1] == 0):
            Y.pop()
        fixCodeFragment = coder.decode(Y, initialUnkList)

        # 5.2.4.
        isCompiling = False
        f1 = os.fsdecode(os.path.join(os.fsencode(config.getRepoDir()), os.fsencode(cleanFn)))
        f2 = os.fsdecode(os.path.join(os.fsencode(config.getRepoDir()), os.fsencode('{0}.o'.format(cleanFn))))
        if os.path.isfile(f1):
            os.remove(f1)
        if os.path.isfile(f2):
            os.remove(f2)
        extractor.loadCodeFromText(fullCodeWithBug)
        extractor.applyFix(fixCodeFragment)
        with open(repoFn, 'wt') as f:
            f.writelines(extractor.code)
        log = codechecker.runCmd('CodeChecker check -e all -b "cd {0} && make {1}" -o /tmp/codefixer_{1}'.format(config.getRepoDir(), cleanFn))
        if os.path.isfile(f1):
            isCompiling = True

        # 5.2.5.
        isFixed = False
        ids = []
        if isCompiling:
            resolved = codechecker.diffResolved(config.getCcRunName(), '/tmp/codefixer_{0}'.format(cleanFn), ccdb)
            for bugInfo in resolved:
                ids.append(bugInfo['reportId'])
            if bug in ids:
                isFixed = True

        # 5.2.6.
        isExpected = False
        if fixCodeFragment == expectedFixCodeFragment:
            isExpected = True

        # 5.2.7.
        encodedExpFix, finalUnkList = coder.encode(expectedFixCodeFragment, unkList = initialUnkList, reverse = False)
        noXTokens = len(encodedExpFix)
        noYTokens = len(Y)
        noAllTokens = max(noXTokens, noYTokens)
        noCorrectTokens = 0
        #print(encodedExpFix)
        #print(Y)
        for i in range(min(noXTokens, noYTokens)):
            if encodedExpFix[i] == Y[i]:
                noCorrectTokens += 1

        # 5.2.8.
        with open(fn, 'wt') as f:
            f.write('#BUG#\n{0}\n#EXP#\n{1}\n#FIX#\n{2}\n#STATS#\n{3},{4},{5},{6},{7},{8},{9}\n{10}\n{11}'.format(bugCodeFragment, expectedFixCodeFragment, fixCodeFragment, isCompiling, isFixed, isExpected, noXTokens, noYTokens, noAllTokens, noCorrectTokens, log, ids))

        # 5.2.9.
        with open(repoFn, 'wt') as f:
            f.write(fileContents[fileName])

        # 5.2.10.
        # Not used due to multithreading issues, will be done on file-by-file basis after closing pool
    # 5.3.
    return fileName

print("Step 3")
files = sorted(list(bugsPerFile.keys()))
threads = []
'''
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    while len(files) > 0:
        fileName = files.pop()
        fileContents[fileName] = vcs.getFileContents(fileName, currentCommit)
        threads.append(executor.submit(ProcessBugsInFile, fileName))
    for future in concurrent.futures.as_completed(threads):
        data = future.result()
        # 5.2.10.
        print(data)'''
        
while len(files) > 0:
    fileName = files.pop()
    #cursor = db.cursor()
    filteredBugs = []
    for bug in bugsPerFile[fileName]:
        bugData = bugDataList[bug]
        cleanFn = fileName[:-4]
        fn = '../Results/AnalysisCopy/{0}_{1}_{2}.txt'.format(cleanFn, bug, bugData.getChecker())
        repoFn = os.fsdecode(os.path.join(os.fsencode(config.getRepoDir()), os.fsencode(fileName)))
        if not os.path.isfile(fn):
            filteredBugs.append(bug)
        #else:
            #cursor.execute('UPDATE bugs SET status={0} WHERE id={1}'.format(BUG_PROCESSED, bug))

    if len(filteredBugs) > 0:
        bugsPerFile[fileName] = filteredBugs
        fileContents[fileName] = vcs.getFileContents(fileName, currentCommit)
        print(ProcessBugsInFile(fileName))
    else:
        print(fileName)
    #db.commit()
    #cursor.close()

# 6.
print("Step 6")