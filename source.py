import subprocess
import sys
import getopt
import itertools

def run(*args):
    #handy function for git subprocess
    return subprocess.run(['git'] + list(args), stdout=subprocess.PIPE, universal_newlines=True)

def coNewBranch(subtaskNumber, versionNumber):
    #creates new branch off <versionNumber> with name DOCSP-<subtaskNumber>, where <subtaskNumber> is the parent Jira subtaskNumber
    process = run("checkout", "-b", "DOCSP-"+subtaskNumber, "upstream/"+versionNumber)
    print("BACKPORT BOT IS CREATING A NEW BRANCH")
    print(process.stdout)

def rebase2version(versionNumber):
    #rebases
    process = run("pull", "--rebase", "upstream", versionNumber)
    print("BACKPORT BOT IS REBASING")
    print(process.stdout)

def fetchAll():
    #fetches all branches and commits so cherry-pick can find the hash of the parent ticket commit
    process = run("fetch", "--all")
    print("BACKPORT BOT IS FETCHING ALL BRANCHES AND COMMITS")
    print(process.stdout)

def getCommitHash(parentTicketNumber):
    #returns parent ticket commit hash by rev-list of HEAD
    result = run('rev-list', 'HEAD', '--grep=DOCSP-'+parentTicketNumber)
    print("REV LIST")
    out = result.stdout.strip()
    print(out)
    return out

def cherryPick(commitHash):
    #cherry picks relevant commit via it's hash
    #commitHash = getCommitHash(parentTicketNumber)
    #test = "21ea1005690821a134d796ffddd897fe2e91cf86"
    #if commitHash != test:
    #    print("WRONG: "+commitHash)
    #    commitHash = test
    conflict = False
    process = run("cherry-pick", commitHash)
    print("BACKPORT BOT IS CHERRY PICKING "+ commitHash)
    print(process.stdout)
    if "CONFLICT" in process.stdout:
      conflict = True
      print("MERGE CONFLICT FOUND. STOPPING CHERRY-PICK.")
      process = run('cherry-pick', '--abort')
    return conflict

def commitAmend(subtaskNumber, parentTicketNumber, versionNumber):
    #replaces cherry picked commit message (this also creates a new commit with the same content as the cherry picked commit)
    newMessage = "DOCSP-"+subtaskNumber+": Backport DOCSP-"+parentTicketNumber+" to "+versionNumber
    process = run("commit", "--amend", "-m", newMessage)
    print("BACKPORT BOT IS REPLACING THE CHERRY PICKED COMMIT MESSAGE WITH: "+ newMessage)
    print(process.stdout)

def pushOrigin(subtaskNumber):
    #pushes changes to remote
    #FIX THIS LATER: get PR link and store somewhere in case someone wants to backport to a bajillion versions
    process = run("push", "origin", "DOCSP-"+subtaskNumber)
    #prLink = ""
    #for line in process.stdout:
    #    if "https" in line:
    #       prLink = line.split(":", 1)[1]
    #print("YOUR PR CAN BE FOUND AT "+prLink)
    print(process.stdout)

def main(argv):
    cmd = 'backport.py -s <subtaskNumber1> <subtaskNumber2> <subtaskNumber3> -p <parentTicketNumber> -v <v1>,<v2>,<v3>'
    subtaskNumbers = ''
    parentTicketNumber = ''
    versions = ''
    commitHash = ''

    print("GREETINGS, I AM BACKPORT BOT. I WILL ASSIST YOU IN ALL YOUR BACKPORT NEEDS TODAY")

    #get user args
    try:
        opts, args = getopt.getopt(argv,"hs:p:c:v:",["help=","subtaskNumber=","parentTicketNumber=","versions="])
    except getopt.GetoptError:
        print("I RESPOND TO THE FOLLOWING SYNTAX:")
        print(cmd)
        sys.exit(2)
    for opt, arg in opts:
        #if user needs syntax help, print the cmd syntax
        if opt in ("-h", "--help"):
            print(cmd)
            sys.exit()
        #parent Jira subtask number used to create backport branch
        elif opt in ("-s", "--subtaskNumber"):
            subtaskNumbers = arg.split(',')
        #parent Jira ticket number
        elif opt in ("-p", "--parentTicketNumber"):
            parentTicketNumber = arg
        #parse one or more versions to backport to
        elif opt in ("-v", "--versions"):
            versions = arg.split(',')
    
    if len(subtaskNumbers) != len(versions):
        print("ONE SUBSTASK FOR EACH VERSION THAT YOU WISH TO BACKPORT TO. PLEASE TRY AGAIN.")
        sys.exit(2)

    print("YOUR PARENT TICKET IS DOCSP-"+parentTicketNumber)
    run('checkout', 'master')
    fetchAll()
    commitHash = getCommitHash(parentTicketNumber)
    #for every version listed, perform the backporting process
    for (versionNumber, subtaskNumber) in zip(versions, subtaskNumbers):
        conflict = False
        print("YOUR BACKPORT SUBTASK TICKET IS DOCSP-"+subtaskNumber)
        print("YOU ARE BACKPORTING TO VERSION "+versionNumber)
        print("...")
        print()
        print("BEGINNING BACKPORT...")
        print("...")
        print()
        coNewBranch(subtaskNumber, versionNumber)
        rebase2version(versionNumber)
        conflict = cherryPick(commitHash)
        if conflict == True:
          print("\n********")
          print("MERGE CONFLICT. PLEASE PERFORM THIS BACKPORT MANUALLY AND RESOLVE ANY MERGE CONFLICTS.")
          print("********\n")
        else:
          commitAmend(subtaskNumber, parentTicketNumber, versionNumber)
          pushOrigin(subtaskNumber)
          print("BACKPORT OF DOCSP-"+parentTicketNumber+" TO " +versionNumber + " HAS BEEN PUSHED TO BRANCH DOCSP-"+subtaskNumber)

if __name__ == "__main__":
    main(sys.argv[1:])

