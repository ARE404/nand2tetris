from asyncore import file_dispatcher
from nis import match
import sys

fileName = str(sys.argv[1])
fileNameWithoutSuffix = fileName.removesuffix(".vm")
outfileName = fileNameWithoutSuffix + ".asm"

class command:
    commandContent = None
    commandType = None
    argNum = 0
    arg1 = None
    arg2 = None
    op = None

    def __init__(self) -> None:
        pass

    def __init__(self, cmdcontent, argNum, arg1, arg2) -> None:
        self.commandContent = cmdcontent
        self.op = cmdcontent[0]
        self.argNum = argNum
        self.arg1 = arg1
        self.arg2 = arg2

# main
def VMtranslator():
    parsedCmdList = parser()
    codewriter(parsedCmdList)
    
# open a .vm file and parse into a list include every command's type and argvs
def parser():
    # open file
    infile = open(fileName)

    cmdlist = []
    # for every line in infile
    for line in infile:
        parsedcmd = parseline(line)
        if parsedcmd is not None:
            cmdlist.append(parsedcmd)
        
    return cmdlist

# parse a line of vm language, produce a command class obj
def parseline(l):
    # empty line
    if l == "\n":
        return None

    # remove around whitespace
    l = l.strip()

    # individual comment
    if l[0] == "/":
        return None

    # remove inline comment
    l = l.partition("//")[0]
    l.strip()

    # split into componets
    l = l.split()

    # judge command type
    if len(l) == 0:
        return None
    elif len(l) == 1:
        cmd = command(l, 0, None, None)
        op = l[0]
        if op == "add" or op == "sub" or op == "neg":
            cmd.commandType = "C_ARITHMETIC"
        elif op == "eq" or op == "gt" or op == "lt":
            cmd.commandType = "C_COMPARISON"
        elif op == "and" or op == "or" or op == "not":
            cmd.commandType = "C_LOGICAL"
    elif len(l) == 2:
        cmd = command(l, 1, l[1], None)
    elif len(l) == 3:
        cmd = command(l, 2, l[1], l[2])
        op = l[0]
        if op == "push":
            cmd.commandType = "C_PUSH"
        elif op == "pop":
            cmd.commandType = "C_POP"

    return cmd 
    
# translate and write parsed commands into file
def codewriter(cmdList):
    translatedCmd = ""
    # for each cmd in cmdList
    for cmd in cmdList:
        # translate cmd
        assembleCodeList = translate(cmd)
        for ac in assembleCodeList:
            translatedCmd += ac
        translatedCmd += "\n"
    translatedCmd = addEnd(translatedCmd)
    with open(outfileName, "w") as f:
        f.write(translatedCmd)
    pass

# translate a cmd obj into mutiple lines assemble code
def translate(cmd):
    res = []

    if cmd.commandType == "C_ARITHMETIC":
        res = transArithmetic(cmd)
    elif cmd.commandType == "C_LOGICAL":
        res = transLogical(cmd)
    elif cmd.commandType in ["C_PUSH", "C_POP"]:
        res = transPushPop(cmd)

    return res

# translate arithmetic type command into assembly code
def transArithmetic(cmd):
    res = []
    if cmd.op in ["add", "sub"]:
        res.append("@SP\n")
        res.append("M=M-1\n")
        res.append("A=M\n")
        res.append("D=M\n")
        res.append("@SP\n")
        res.append("A=M-1\n")
        if cmd.op == "add":
            res.append("D=M+D\n")
        elif cmd.op == "sub":
            res.append("D=M-D\n")
        res.append("M=D\n")
    elif cmd.op == "neg":
        res.append("@SP\n")
        res.append("A=M-1\n")
        res.append("M=-M\n")
    return res

# translate logical command into assembly code
def transLogical(cmd):
    res = []
    res.append("@SP\n")
    res.append("M=M-1\n")
    res.append("A=M\n")
    res.append("D=M\n")
    res.append("A=A-1\n")
    res.append("D=D-M\n")
    res.append("M=-1\n")
    if cmd.op == "eq":
        res.append("@EQUAL\n")
        res.append("D;JEQ\n")
        res.append("@SP\n")
        res.append("A=M-1\n")
        res.append("M=0\n")
        res.append("(EQUAL)\n")
    elif cmd.op == "gt":
        res.append("@GT\n")
        res.append("D;JGT\n")
        res.append("@SP\n")
        res.append("A=M-1\n")
        res.append("M=0\n")
        res.append("(GT)\n")
    elif cmd.op == "lt":
        res.append("@LT\n")
        res.append("D;JLT\n")
        res.append("@SP\n")
        res.append("A=M-1\n")
        res.append("M=0\n")
        res.append("(LT)\n")
    return res

# translate push or pop command into assembly code
def transPushPop(cmd):
    res = []
    if cmd.op == "push":
        if cmd.arg1 in ["local", "argument", "this", "that", "temp"]:
            res.append("@" + cmd.arg2 + "\n")
            res.append("D=A\n")
            if cmd.arg1 == "local":
                res.append("@LCL\n")
            elif cmd.arg1 == "argument":
                res.append("@ARG\n")
            elif cmd.arg1 == "this":
                res.append("@THIS\n")
            elif cmd.arg1 == "that":
                res.append("@THAT\n")
            elif cmd.arg1 == "temp":
                res.append("@TEMP\n")
            res.append("A=M+D\n")
            res.append("D=M\n")
        elif cmd.arg1 == "constant":
            res.append("@" + cmd.arg2 + "\n")
            res.append("D=A\n")
        elif cmd.arg1 == "static":
            res.append("@" + fileNameWithoutSuffix + "." + cmd.arg2 + "\n")
            res.append("D=M\n")
        # push into stack
        res.append("@SP\n")
        res.append("A=M\n")
        res.append("M=D\n")
        res.append("@SP\n")
        res.append("M=M+1\n")

    elif cmd.op == "pop":
        if cmd.arg1 in ["local", "argument", "this", "that", "temp"]:
            if cmd.arg1 == "local":
                res.append("@LCL\n")
            elif cmd.arg1 == "argument":
                res.append("@ARG\n")
            elif cmd.arg1 == "this":
                res.append("@THIS\n")
            elif cmd.arg1 == "that":
                res.append("@THAT\n")
            elif cmd.arg1 == "temp":
                res.append("@TEMP\n")
            res.append("D=M\n")
            res.append("@" + cmd.arg2 + "\n")
            res.append("D=D+A\n")
            res.append("@R13\n")
            res.append("M=D\n")
            # pop out
            res.append("@SP\n")
            res.append("M=M-1\n")
            res.append("A=M\n")
            res.append("D=M\n")

            res.append("@R13\n")
            res.append("A=M\n")
            res.append("M=D\n")
        elif cmd.arg1 == "static":
            res.append("@SP\n")
            res.append("M=M-1\n")
            res.append("A=M\n")
            res.append("D=M\n")
            res.append("@" + fileNameWithoutSuffix + "." + cmd.arg2 + "\n")
            res.append("M=D\n")
    return res

# add an infinite loop at the end
def addEnd(res):
    res += "@END"
    res += "0;JMP"
    return res

VMtranslator()