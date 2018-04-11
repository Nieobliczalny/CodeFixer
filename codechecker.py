import config

import subprocess

class CodeChecker():
    def check(self, clean = False):
        makeClean = ''
        if clean:
            makeClean = ' && make clean'
        cmd = 'CodeChecker check -b "cd ' + config.repo + makeClean + ' && make" -o ' + config.tmpDir
        self.runCmd(cmd)
    
    def store(self, tag):
        cmd = 'CodeChecker store ' + config.tmpDir + ' -n ' + config.ccRunName + ' --tag ' + tag
        self.runCmd(cmd)
    
    def runCmd(self, cmd):
        command = '. ' + config.codeCheckerPath + config.codeCheckerRelativeVenv + ' && cd ' + config.codeCheckerPath + config.codeCheckerRelativeBinPath + ' && ./' + cmd
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout

cc = CodeChecker()
#cc.check(True)
#cc.store("0000000")