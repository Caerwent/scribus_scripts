
import scribus
import logging
import csv
import traceback
import re


headers=[]
card=None
cardsize=None
cardName="card"
itemsInPage=0
currentPage=1

def initCard():
    global card
    global cardsize
    global itemsInPage
    global currentPage
    currentPage=1
    scribus.gotoPage(currentPage)
    objList = scribus.getPageItems()
    card = None

    for item in objList:
        if item[1] == 12: #type 12 == group
            card=item[0]
            break
    if card==None :
        scribus.messageBox('Error', 'No card found')
        sys.exit(1)

    itemsInPage=0
    cardsize = scribus.getSize(cardName)
    scribus.copyObjects([cardName])

def addNewCard(csvLine) :
    global itemsInPage
    global currentPage

    if itemsInPage >= 4 :
        itemsInPage = 0
        scribus.newPage(-1)
        currentPage=currentPage+1
        scribus.gotoPage(currentPage)

    newObjList = scribus.pasteObjects()
    scribus.selectObject(newObjList[0])
    itemsInPage = itemsInPage+1
    x=0
    y=0
    match itemsInPage:
        case 1:
            x=0
            y=0
        case 2:
            x=cardsize[0]
            y=0
        case 3 :
            x=0
            y=cardsize[1]
        case 4 :
            x=cardsize[0]
            y=cardsize[1]

    scribus.moveObjectAbs(x, y, newObjList[0])

    scribus.unGroupObject()
    childObjectCount = scribus.selectionCount()
    for x in range(0, childObjectCount):
        element = scribus.getSelectedObject(x)
        if scribus.getObjectType(element) == "TextFrame" :
            contents = scribus.getAllText(element)
            text = ""
            for elt in contents:
                text = text +elt
            result = re.search('%VAR_(\w+)%', text)

            if result != None :
                text = result.group(1)

            try:
                index = headers.index(text)
                if index >= 0:
                    textLength = scribus.getTextLength(element)
                    scribus.insertText(csvLine[index], -1, element)
                    scribus.selectText(0,textLength,element)
                    scribus.deleteText(element)
                    element
            except ValueError:
                scribus.messageBox("error", f"That item does not exist {text}")
        elif scribus.getObjectType(element) == "ImageFrame" :
            filename = scribus.getImageFile(element)
            result = re.search('%VAR_(\w+)%', filename)
            if result != None :
                filename = result.group(1)
            try:
                index = headers.index(filename)
                if index >= 0:
                    scribus.loadImage(csvLine[index], element)
            except ValueError:
                 scribus.messageBox("Error", f"That item does not exist {filename}")
    scribus.groupObjects()


def processCSVdata():
    global headers
    """opens a csv file, reads it in and returns a 2 dimensional list with the data"""
    csvfileName = scribus.fileDialog("csv data :: open file", "*.csv")
    if csvfileName != "":
        try:
             # reader = csv.reader(file(csvfile))

            # Load file contents
            with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headersInit = False
                initCard()
                for row in reader:
                    if(headersInit==True):
                        rowlist=[]
                        for col in row:
                            rowlist.append(col)
                        addNewCard(rowlist)
                    else :
                        headers=[]
                        for col in row:
                            headers.append(col)
                        headersInit = True
        except Exception as e :
            scribus.messageBox("CSV", "Error processing file %s"%e)
            return False

        scribus.deleteObject(cardName)
        return True

    else:
        return False



if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    if(processCSVdata()) :
        scribus.docChanged(1)
        scribus.setRedraw(True)
        scribus.redrawAll()



else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


