import os
import xlsxwriter

workbook = xlsxwriter.Workbook('../Results/Analysis.xlsx')
ch1 = workbook.add_worksheet('deadcode.DeadStores')
ch2 = workbook.add_worksheet('tautological-constant-oor-cmp')
ch3 = workbook.add_worksheet('unused-parameter')
ch4 = workbook.add_worksheet('constant-conversion')

ch1n = 1
ch2n = 1
ch3n = 1
ch4n = 1

ch1.write(0, 0, 'Filename')
ch1.write(0, 1, 'Bug ID')
ch1.write(0, 2, 'Code with bug')
ch1.write(0, 3, 'Expected fix')
ch1.write(0, 4, 'Predicted fix')
ch1.write(0, 5, 'Is compiling')
ch1.write(0, 6, 'Is bug fixed')
ch1.write(0, 7, 'Is fix == expected')
ch1.write(0, 8, 'No expected tokens')
ch1.write(0, 9, 'No predicted tokens')
ch1.write(0, 10, 'No all tokens')
ch1.write(0, 11, 'No correct tokens')

ch2.write(0, 0, 'Filename')
ch2.write(0, 1, 'Bug ID')
ch2.write(0, 2, 'Code with bug')
ch2.write(0, 3, 'Expected fix')
ch2.write(0, 4, 'Predicted fix')
ch2.write(0, 5, 'Is compiling')
ch2.write(0, 6, 'Is bug fixed')
ch2.write(0, 7, 'Is fix == expected')
ch2.write(0, 8, 'No expected tokens')
ch2.write(0, 9, 'No predicted tokens')
ch2.write(0, 10, 'No all tokens')
ch2.write(0, 11, 'No correct tokens')

ch3.write(0, 0, 'Filename')
ch3.write(0, 1, 'Bug ID')
ch3.write(0, 2, 'Code with bug')
ch3.write(0, 3, 'Expected fix')
ch3.write(0, 4, 'Predicted fix')
ch3.write(0, 5, 'Is compiling')
ch3.write(0, 6, 'Is bug fixed')
ch3.write(0, 7, 'Is fix == expected')
ch3.write(0, 8, 'No expected tokens')
ch3.write(0, 9, 'No predicted tokens')
ch3.write(0, 10, 'No all tokens')
ch3.write(0, 11, 'No correct tokens')

ch4.write(0, 0, 'Filename')
ch4.write(0, 1, 'Bug ID')
ch4.write(0, 2, 'Code with bug')
ch4.write(0, 3, 'Expected fix')
ch4.write(0, 4, 'Predicted fix')
ch4.write(0, 5, 'Is compiling')
ch4.write(0, 6, 'Is bug fixed')
ch4.write(0, 7, 'Is fix == expected')
ch4.write(0, 8, 'No expected tokens')
ch4.write(0, 9, 'No predicted tokens')
ch4.write(0, 10, 'No all tokens')
ch4.write(0, 11, 'No correct tokens')

def parseLines(lines):
    lb = -1
    le = -1
    lf = -1
    ls = -1
    for i in range(len(lines)):
        line = lines[i]
        if line == '#BUG#\n':
            lb = i
        if line == '#EXP#\n':
            le = i
        if line == '#FIX#\n':
            lf = i
        if line == '#STATS#\n':
            ls = i
    return (lb, le, lf, ls)

directory = os.fsencode('../Results/Analysis/')
for filename in os.listdir(directory):
    fullPath = os.path.join(directory, filename)
    if os.path.isfile(fullPath):
        name = os.fsdecode(os.path.basename(fullPath))[:-4].split('_')
        lines = []
        with open(fullPath) as f:
            lines = f.readlines()
        lineBug, lineExp, lineFix, lineStats = parseLines(lines)
        bug = ''.join(lines[lineBug+1:lineExp-1])
        exp = ''.join(lines[lineExp+1:lineFix-1])
        fix = ''.join(lines[lineFix+1:lineStats-1])
        isCompiling, isFixed, isExpected, noXTokens, noYTokens, noAllTokens, noCorrectTokens = lines[lineStats+1].split(',')
        ch = None
        ind = -1
        if name[2] == 'deadcode.DeadStores':
            ind = ch1n
            ch1n += 1
            ch = ch1
        elif name[2] == 'clang-diagnostic-tautological-constant-out-of-range-compare':
            ind = ch2n
            ch2n += 1
            ch = ch2
        elif name[2] == 'clang-diagnostic-unused-parameter':
            ind = ch3n
            ch3n += 1
            ch = ch3
        elif name[2] == 'clang-diagnostic-constant-conversion':
            ind = ch4n
            ch4n += 1
            ch = ch4
        ch.write(ind, 0, '{0}.cpp'.format(name[0]))
        ch.write(ind, 1, int(name[1]))
        ch.write(ind, 2, bug)
        ch.write(ind, 3, exp)
        ch.write(ind, 4, fix)
        ch.write(ind, 5, isCompiling == 'True')
        ch.write(ind, 6, isFixed == 'True')
        ch.write(ind, 7, isExpected == 'True')
        ch.write(ind, 8, int(noXTokens))
        ch.write(ind, 9, int(noYTokens))
        ch.write(ind, 10, int(noAllTokens))
        ch.write(ind, 11, int(noCorrectTokens))

workbook.close()