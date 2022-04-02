import re
import subprocess
import sys
import getopt
import yaml
import glob
import string
import os

rst_procedure_template = ""

def run(*args):
    #handy function for git subprocess
    return subprocess.run(['git'] + list(args), stdout=subprocess.PIPE, universal_newlines=True)

def coNewBranch(ticketNumber):
    #creates new branch off <versionNumber> with name DOCSP-<subtaskNumber>, where <subtaskNumber> is the parent Jira subtaskNumber
    process = run("checkout", "-b", "DOCSP-"+ticketNumber, "upstream/master")
    print(process.stdout)

def commitWMessage(ticketNumber):
    #replaces cherry picked commit message (this also creates a new commit with the same content as the cherry picked commit)
    newMessage = "DOCSP-"+ticketNumber+" TODO"
    process = run("commit", "-m", newMessage)
    print(process.stdout)

def pushOrigin(ticketNumber):
    #pushes changes to remote
    #FIX THIS LATER: get PR link and store somewhere in case someone wants to backport to a bajillion versions
    process = run("push", "origin", "DOCSP-"+ticketNumber)
    #prLink = ""
    #for line in process.stdout:
    #    if "https" in line:
    #       prLink = line.split(":", 1)[1]
    #print("YOUR PR CAN BE FOUND AT "+prLink)
    print(process.stdout)

#4
def openFile(fname):
    with open(fname, 'r') as file:
        yamlFile = yaml.safe_load_all(file.read())
        return yamlFile

def printYAMLfile(yamlFileObj):
    for data in yamlFileObj:
        print(data)

def findStepByRef(yamlFileObj, ref2find):
    step2inheritFrom = ""
    yamlFileList = steps2list(yamlFileObj)
    stepsWRefs = [step for step in yamlFileList if 'ref' in step]
    for data in stepsWRefs:
        if ref2find == data.get('ref'):
            step2inheritFrom = data
    return step2inheritFrom

#5.1
def steps2list(yamlFileObj):
    return list(yamlFileObj)

''' 
def getSingleStep(yamlFileList, stepNum):
    yamlFileStepList = steps2list(yamlFileStepObj)
    #print(type(yamlFileObj))
    return yamlFileStepList[stepNum]
'''

#5
def yamlContent2RSTContent(yamlFileObj):
    #convert loaded YAML obj to list 
    yamlAsMarkup = ""
    #5.1
    yamlFileList = steps2list(yamlFileObj)
    #print(yamlFileList)
    for step in yamlFileList:
        #print(type(step))
        #print(step)
        #print()
        #5.2
        stepMarkup = constructStepUsingProcedureMarkup(step)
        yamlAsMarkup = yamlAsMarkup + stepMarkup
    return yamlAsMarkup

def yamlContent2RSTProcedure(yamlFileObj):
    #convert loaded YAML obj to list 
    yamlAsMarkup =  ".. procedure::" +"\n" +  "   "+ ":style: normal" + "\n\n"
    #5.1
    yamlFileList = steps2list(yamlFileObj)
    #print(yamlFileList)
    for step in yamlFileList:
        #print(type(step))
        #print(step)
        #print()
        #5.2
        stepMarkup = constructStepUsingProcedureMarkup(step)
        yamlAsMarkup = yamlAsMarkup + stepMarkup
    return yamlAsMarkup

def constructStepAsMarkup(singleStepObj):
    #print(singleStepObj)
    rst = ""
    #assumption: all steps have a stepNum
    stepNum = singleStepObj.get('stepnum')
    #assumption: all steps have a ref
    ref = singleStepObj.get('ref')
    title = ""
    #assumption: not all steps have a title 
    # if no title, inherits
    if 'title' not in singleStepObj:
        inherit = singleStepObj.get('inherit')
        inheritFileName = inherit.get('file')
        inheritFileStepRef = inherit.get('ref')
        inheritFileYAMLObj = openFile(inheritFileName)
        stepObj2InheritFrom = findStepByRef(inheritFileYAMLObj, inheritFileStepRef)
        title = stepObj2InheritFrom.get('title')
        content = stepObj2InheritFrom.get('content') 
        formattedContent = reindent(content, 2)
        rst = str(stepNum) + ". " + title + "\n "+formattedContent+"\n"
        #print(type(inheritFile))
        #printYAMLfile(inheritFile)
    else:
        #if title, get it
        title = singleStepObj.get('title')
    
        #if there is no content, 
        #rst step is literally just the stpeNum concatenated to the title
        if 'content' not in singleStepObj:
            
            '''
            the step as an rst string consists of:
            its stepNum,
            followed by a ". "
            then the title (which is the actual instruction)
            '''
            rst = str(stepNum) + ". " + title + "\n\n"
        #if there is content...
        
        else:
            #massage the content and add tabs and such
            content = singleStepObj.get('content') 
            
            #splitContent = parseSubstepsFromContent(content) 
            formattedContent = reindent(content, 2)
            
            '''
            the step as an rst string consists of:
            its stepNum,
            followed by a ". "
            then the title
            then the content (description, substeps, whatever)
            '''
            rst = str(stepNum) + ". " + title + "\n\n "+formattedContent+"\n"
        
    return rst

def indentBy3():
    return "   "

def checkContent(content):
    s = re.split(r'(\n)',content)
    newList = []
    while("" in s):
        s.remove("")
    for i in s:
        match = re.search(r'^\D', i)
        if match:
            #print(match.group() + " :LINE: " + i)
            rep = '.. step:: \n\n   '
            n = re.sub(r'^\D\.', rep , i)
            newList.append(n)

        else:
            #print(None)
            newList.append(i)
    procStart = ".. procedure::" +"\n" +  "   "+ ":style: normal" + "\n\n"
    newList = procStart + ' '.join(newList)
    return(newList)

def constructStepUsingProcedureMarkup(singleStepObj):
    #print(singleStepObj)
    rst = ""
    #assumption: all steps have a stepNum
    #stepNum = singleStepObj.get('stepnum')
    #assumption: all steps have a ref
    #ref = singleStepObj.get('ref')
    title = ""
    #assumption: not all steps have a title 
    # if no title, inherits
    if 'title' not in singleStepObj:
        inherit = singleStepObj.get('inherit')
        inheritFileName = inherit.get('file')
        inheritFileStepRef = inherit.get('ref')
        inheritFileYAMLObj = openFile(inheritFileName)
        stepObj2InheritFrom = findStepByRef(inheritFileYAMLObj, inheritFileStepRef)
        title = stepObj2InheritFrom.get('title')
        content = stepObj2InheritFrom.get('content') 
        checkedContent = checkContent(content)
        print(checkedContent)
        formattedContent = reindent(checkedContent, 2)
        rst = rst +  "   "+ ".. step:: " + title + "\n "+formattedContent+"\n"
        #print(type(inheritFile))
        #printYAMLfile(inheritFile)
    else:
        #if title, get it
        title = singleStepObj.get('title')
    
        #if there is no content, 
        #rst step is literally just the stpeNum concatenated to the title
        if 'content' not in singleStepObj:
            
            '''
            the step as an rst string consists of:
            its stepNum,
            followed by a ". "
            then the title (which is the actual instruction)
            '''
            rst = rst +  "   "+".. step:: " + title  + "\n\n"
        #if there is content...
        
        else:
            #massage the content and add tabs and such
            content = singleStepObj.get('content') 
            
            #splitContent = parseSubstepsFromContent(content) 
            formattedContent = reindent(content, 2)
            
            '''
            the step as an rst string consists of:
            its stepNum,
            followed by a ". "
            then the title
            then the content (description, substeps, whatever)
            '''
            rst = rst + "   " +".. step:: " + title + "\n\n "+formattedContent+"\n"
        
    return rst

def remspace(my_str):
    if len(my_str) < 2: # returns ' ' unchanged
        return my_str
    if my_str[-1] == '\n':
        if my_str[-2] == ' ':
            return my_str[:-2] + '\n'
    if my_str[-1] == ' ':
        return my_str[:-1]
    return my_str

def reindent(s, numSpaces):
    #split on and keep \n
    s = re.split(r'(\n)',s)   
    s = [remspace(line) for line in s]
    while("" in s):
        s.remove("")
    #s = [(numSpaces * ' ') + line for line in s]
    #print(s)
    #print()
    s = [(numSpaces * ' ') + line for line in s]
    s = " ".join(s)
    return s

#todo: figure out why substeps aren't indented at the same level
def parseSubstepsFromContent(content):
    #split on any single letter or digit (specified by \w)
    #IF that character is not directly preceded by another char, digit, etc.
    #this negative look behind account for the end of the content i.e. a word, period and maybe newline
    #Splits incorrectly if this is not included

    #splitContent = re.split(r"(?<!\w)(\w\.\s)", content)
    #splitContent = re.split(r"(?<!\w)([#\w\d]\.\s)", content)
    splitContent = re.split(r"(\n)", content)
    print(splitContent)
    #then remove any whitespace
    while("" in splitContent):
        splitContent.remove("")
    #iterates through splitContent list, finds substep markers ("a. ", "b. ", etc.)
    #if found, adds \t at front per RST conventions
    
    for s in splitContent:
        #if re.match(r"\w\.\s",s):
        if re.match(r"\n",s):
            s = "\t" + s
            print(s)
        else:
            print(s)
        
    #return updated content list as a joined string
    #print(splitContent)
    return ' '.join(splitContent)

def createRSTStepFile(rstFileName, content):
     f = open(rstFileName, 'w+')
     f.write(content)

#2
def getListOStepFiles():
    return glob.glob(r"steps-*.yaml")

#1
def createStepDir():
    if not os.path.exists('steps'):
        os.makedirs('steps')

#3
#TODO rename properly - add rst extension and test
def renameStepFile(stepFileName):
    return ((stepFileName.split('-', 1))[1]).split(".",1)[0]

def main():
    #1: create steps/ if it doesn't exist
    createStepDir()
    #2: get list of step files
    listOStepFiles = getListOStepFiles()
    for f in listOStepFiles:
        newFileName = "steps/" + renameStepFile(f) + ".rst"
        print()
        print(newFileName)
        print()
        yamlFileObj = openFile(f)
        #CONSTRUCTION BELOW#
        yamlFileAsRST = yamlContent2RSTProcedure(yamlFileObj)
        print(yamlFileAsRST)

        '''CONSTRUCTION SAFETY ZONE###
        yamlFileAsRST = yamlContent2RSTContent(yamlFileObj)
        #print(yamlFileAsRST)
        createRSTStepFile(newFileName,yamlFileAsRST)
        ##CONSTRUCTION SAFETY ZONE'''
if __name__ == "__main__":
    main()
