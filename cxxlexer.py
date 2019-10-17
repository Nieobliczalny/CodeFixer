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
        proc_stdout = process.communicate(input=inputData.encode())[0].strip()
        return proc_stdout
    
    def detokenize(self, tokens):
        code = []
        specials = ['asm', 'auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'const', 'const_cast', 'continue', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'operator', 'private', 'protected', 'public', 'register', 'reinterpret_cast', 'return', 'short', 'signed', 'sizeof', 'static', 'static_cast', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while', '::', '...', '<<', '>>', '==', '!=', '<=', '>=', '&&', '||', '++', '--', '->*', '->', '.*', '+=', '-=', '*=', '/=', '%=', '^=', '&=', '|=', '>>=', '<<=']
        for token in tokens:
            tokenId = int(token['token'])
            if tokenId < 256:
                code.append(chr(tokenId))
            elif tokenId > 257 and tokenId < 346:
                code.append(specials[tokenId - 258])
            elif tokenId < 352:
                code.append(token['value'])
            else:
                # Unknown / invalid token, ignore it
                code.append('')
        return "".join(code)