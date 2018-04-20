import config

import subprocess
import sys
import json

class CodeChecker():
    def __init__(self, repo = None):
        if repo is None:
            self.repo = config.repo
        else:
            self.repo = repo
    
    def check(self, clean = False):
        makeClean = ''
        if clean:
            makeClean = ' && make clean'
        cmd = 'CodeChecker check -b "cd ' + self.repo + makeClean + ' && make" -o ' + config.tmpDir
        self.runCmd(cmd)
    
    def store(self, tag):
        cmd = 'CodeChecker store ' + config.tmpDir + ' -n ' + config.ccRunName + ' --tag ' + tag
        self.runCmd(cmd)
    
    def diffResolved(self, baseRun, newRun):
        cmd = 'CodeChecker cmd diff -b ' + baseRun + ' -n ' + newRun + ' --resolved -o json'
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        output = stdoutData.split('\n', 1)[1]
        out = []
        try:
            out = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
        return out
    
    def runCmd(self, cmd):
        command = '. ' + config.codeCheckerPath + config.codeCheckerRelativeVenv + ' && cd ' + config.codeCheckerPath + config.codeCheckerRelativeBinPath + ' && ./' + cmd
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

#cc = CodeChecker()
#cc.check(True)
#cc.store("0000000")
#print(cc.diffResolved('example', '/tmp/cctmp'))