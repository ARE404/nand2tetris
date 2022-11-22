import enum
import sys
# these three dictionaries store the translations of the 3 parts
# of a c-instruction
comp = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
    }

dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
    }

jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
    }

# table of symbols used in assembly code, initialized to include
# standard ones
table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    }
# add R0-R15 into table
for i in range(16):
    table["R" + str(i)] = i


def assembler():
    preprocess()
    labelAssembler()
    basicAssembler()

# remove emptylines and comments
def preprocess():
    # open file
    infile = open(sys.argv[1] + ".asm")
    outfile = open(sys.argv[1] + "_0.tmp", "w")
    for line in infile:
        pline = processLine(line)
        if pline is not None and len(pline) != 0:
            outfile.write(pline)

# process a line, return nothing if its empty, cut comments
def processLine(l):
    # remove whole line comment and empty line
    if l == "\n" or l[0:2] == "//":
        return ""

    # remove inline comment
    for i, c in enumerate(l):
        if c == "/":
            l = l[:i] + "\n"
            break
    
    # remove whitespaces
    l = l.replace(" ", "")
    return l

# labelAssembler, deal with labels
def labelAssembler():
    # open file
    infile = open(sys.argv[1] + "_0.tmp")
    # load symbols
    # load label
    loadLabel(infile)
    # load variable
    infile = open(sys.argv[1] + "_0.tmp")
    loadVar(infile)
    # replace symbols
    infile = open(sys.argv[1] + "_0.tmp")
    outfile = open(sys.argv[1] + "_1.tmp", "w")
    transSymbols(infile, outfile)

# get the symbol part from a line if there is
def getSymbol(l):
    s = ""
    if len(l) > 1 and l[0] == "@" and l[1].isalpha():
        for c in l[1:]:
            if c.isalpha():
                s += c
    return s

# go through file, load all jump label into table
def loadLabel(infile):
    index = 0
    for line in infile:
        if len(line) != 0 and line[0] == "(":
            label = ""
            for c in line[1:]:
                if c == ")":
                    break
                label += c
            table[label] = index
        else:
            index += 1

def loadVar(infile):
    # point to next avaliable variable address
    varAddressPointer = 16
    for line in infile:
        s = getSymbol(line)
        if len(s) != 0:
            if s in table.keys():
                continue
            else:
                table[s] = varAddressPointer 
                varAddressPointer += 1

def transSymbols(infile, outfile):
    for line in infile:
        if line[0] == "(":
            continue
        s = getSymbol(line)
        if len(s) != 0:
            line = "@" + str(table[s]) + "\n"
        outfile.write(line)
        
# basic assembler, don't consider label, deal with comments and translation
def basicAssembler():
    # open file
    infile = open(sys.argv[1] + "_1.tmp")
    outfile = open(sys.argv[1] + ".hack", "w")

    for line in infile:
        if len(line) != 0:
            # translate
            tline = translate(line[:-1])
            # write processed lines into outfile
            outfile.write(tline)

# translate a line, from A\C instrucion into binary
def translate(l):
    s = ""

    # A instruction @a
    if l[0] == "@":
        s = "0" + f'{int(l[1:]):015b}' + "\n"
        return s

    # C instruction 111a cccc ccdd djjj
    s = "111"

    desClip = ""
    compClip = ""
    jmpClip = ""

    # split desClip
    if "=" in l:
        desSplit = l.split("=")
        desClip = desSplit[0]
        l = desSplit[1]

    # split jmpClip
    if ";" in l:
        jmpSplit = l.split(";")
        jmpClip = jmpSplit[1]
        l = jmpSplit[0]

    # compClip
    compClip = l
    s += comp[compClip]    

    if desClip == "":
        s += "000"
    else:
        s += dest[desClip]

    if jmpClip == "":
        s += "000"
    else:
        s += jump[jmpClip]
    
    return s + "\n"

assembler()