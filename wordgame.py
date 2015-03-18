## Author: Krzysztof Oblak
## Date: 28/11/2014

from random import randrange
from flask import *
##from threading import Thread
from itertools import islice
import linecache
import time
import natsort

app = Flask(__name__)
a = "words.txt"
b = "containers.txt"
c = "score.txt"
baseWord = ""
inputList = [""]*7
flagList = [""]*7
processedList = []
resultList = [False]*7
index = 0
valid = True
startTime = -1.0
endTime = -2.0
resultTime = -3.0

def getHighScore():
    temp = []
    with open(c, 'r') as infile:
        lines_gen = islice(infile, 10)
        for line in lines_gen:
            temp.append(line)
    return temp

def fileLength():
    with open(b) as file:
        for i, l in enumerate(file):
            pass
    return i + 1

def getWord():
    lineNum = randrange(fileLength())
    source = linecache.getline(b,lineNum)
    return source.strip()

def checkLetters(inp,bs):
    index = session['index']
    flagList = session['fList']
    inList = sorted(inp)
    bsList = sorted(bs)

    for elem in inList:
        if elem in bsList:
            bsList.remove(elem)
        else:
            flagList[index] = "No letter '" + elem + "' in word " + bs + " or used too many times"
            session['fList'] = flagList
            return False
    session['fList'] = flagList
    return True

def checkWord(wordInput,flagInput,base):
    datafile = open(a)
    resultList = session['rList']
    index = session['index']
    flagList = session['fList']
    for line in datafile:
        if wordInput in line.upper().strip() and len(wordInput) == len(line.upper().strip()) and checkLetters(wordInput,base) == True and wordInput != base and flagInput == "":
            resultList[index] = True
            flagList[index] = "Correct"
            session['fList'] = flagList
        if wordInput == base:
            flagList[index] = "Duplicate of the source word"
            session['fList'] = flagList
    datafile.close()
    session['index'] = index+1
    session['rList'] = resultList

def startGame():
    session['base'] = getWord()
    session['sTime'] = round(time.time(),3)

def storeInput(a,b,c,d,e,f,g):
    inputList = [""]*7
    inputList[0] = a.strip()
    inputList[1] = b.strip()
    inputList[2] = c.strip()
    inputList[3] = d.strip()
    inputList[4] = e.strip()
    inputList[5] = f.strip()
    inputList[6] = g.strip()
    session['inList'] = inputList

def processInput():
    inputList = session['inList']
    flagList = session['fList']
    baseWord = session['base']
    valid = session['valid']
    resultTime = -3
    startTime = session['sTime']
    endTime = session['eTime']

    for x in range(0,7):
        for y in range(x,7):
            if x == y:
                pass
            else:
                if inputList[x].upper() == inputList[y].upper():
                    flagList[y] = "Duplicate of " + inputList[x]
                    session['fList'] = flagList

    for x in range(0,7):
        checkWord(inputList[x].upper(),flagList[x],baseWord.upper())

    flagList = session['fList']

    for x in range(0,7):
        if flagList[x] == "":
            flagList[x] = "Not in dictionary"

    for x in range(0,7):
        if flagList[x] == "Correct" and valid == True:
            valid = True;
        else:
            valid = False

    if valid == True:
        resultTime = endTime - startTime
        session['rTime'] = round(resultTime,3)
    else:
        resultTime = -1
        session['rTime'] = resultTime

    session['fList'] = flagList
    session['index'] = index
    session['valid'] = valid
    session['sTime'] = startTime
    session['eTime'] = endTime

def getRank(nm,tm):
    rank = -1
    query = str(tm)+"^DA&^*"+nm
    with open(c) as search:
        for i,line in enumerate(search):
            line = line.strip()  # remove '\n' at end of line
            if query == line:
                val = str(i+1)
                if val.endswith('1') and val != "11":
                    return val+'st'
                elif val.endswith('2') and val != "12":
                    return val+'nd'
                elif val.endswith('3') and val != "13":
                    return val+'rd'
                else:
                    return val+'th'
            else:
                pass
    return str(rank)

def storeScore():
    with open(c,'a') as file:
        file.write(str(session['rTime'])+"^DA&^*"+session['name']+"\n")
    file = open(c, "r")
    toSort = file.read()
    listToSort = toSort.splitlines()
    sortedList = natsort.natsorted(listToSort, key=lambda y: y.lower())
    # now write the output file
    with open(c, 'w') as file:
        for elem in sortedList:
            file.write(elem+"\n")
    file.close()

@app.route("/")
def display_intro():
    session['base'] = ''
    return render_template("intro.html",the_title="WordGame")

@app.route("/game")
def display_home():
    if session['base'] == '':
        startGame()
    baseWord = session['base']
    return render_template("home.html",the_title="WordGame", the_source_word=baseWord)

@app.route("/result", methods=['POST'])
def display_result():
    all_ok = True
    if request.form["first"].strip() == '' or request.form["second"].strip() == '' or \
       request.form["third"].strip() == '' or request.form["fourth"].strip() == '' or \
       request.form["fifth"].strip() == '' or request.form["sixth"].strip() == '' or \
       request.form["seventh"].strip() == '':
        all_ok = False
        flash("Missing word input.")
    if all_ok:
        session['index'] = 0
        session['eTime'] = round(time.time(),3)
        session['valid'] = True
        session['fList'] = [""]*7
        session['rList'] = [False]*7
        storeInput(request.form["first"],request.form["second"],
                   request.form["third"],request.form["fourth"],
                   request.form["fifth"],request.form["sixth"],
                   request.form["seventh"])
        processInput()
        inputList = session['inList']
        flagList = session['fList']
        resultTime = session['rTime']
        baseWord = session['base']
        session['base']=''
        return render_template("result.html",stored_input_flags=zip(inputList,flagList),time_result=resultTime,base=baseWord)
    else:
        return redirect(url_for('display_home'))

@app.route("/scores", methods=['POST'])
def display_score():
    session['name'] = request.form['name']
    if session['rTime'] != -1:
        storeScore()
        times = []
        names = []
        top = getHighScore()
        for elem in top:
            temp = elem.split('^DA&^*')
            times.append(temp[0])
            names.append(temp[1])
        
        rank = getRank(session['name'],session['rTime'])
        session['rTime'] = -1
        return render_template("highscore.html",top_ten = zip(times,names), the_rank=rank)
    else:
        return display_top()
@app.route("/topscores")
def display_top():
    times = []
    names = []
    top = getHighScore()
    for elem in top:
        temp = elem.split('^DA&^*')
        times.append(temp[0])
        names.append(temp[1])
    return render_template("highscore.html",top_ten = zip(times,names),the_rank=str(-1))

@app.route("/about")
def display_about():
    return render_template("about.html",the_title="WordGame")
app.secret_key = 'IGI&AD^DAD6*AUIA14819Duiad&^DA&^*6768'
if __name__ == '__main__':
    app.run(host='0.0.0.0')
