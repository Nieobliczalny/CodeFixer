import subprocess
import sys
import json

class CxxLexer():
    def tokenize(self, code):
        cmd = './CxxLexer'
        output = self.runCmd(cmd, code).decode(sys.stdout.encoding)
        out = []
        try:
            out = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
        return out
    
    def runCmd(self, cmd, inputData):
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate(input=inputData)[0].strip()
        return proc_stdout