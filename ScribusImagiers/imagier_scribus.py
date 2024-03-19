
import scribus
import logging
import csv
import traceback
import re
import os
from pathlib import Path


class CsvCreator(object):
    def __init__(self):
        self.imagePath = ""
        self.targetCsvFile = None
        self.validImages = [".jpg",".gif",".png",".tga"]
        self.imagesFiles = []

    def findImagesFromPath(self) :
        self.imagePath = scribus.fileDialog("Select image directory","","",False,False,True)
        self.imagesFiles = []
        for f in os.listdir(self.imagePath):
            for ext in self.validImages :
                if f.lower().endswith(ext):
                    self.imagesFiles.append(os.path.join(self.imagePath,f))

    def createCsvFile(self, headers, imageIndex) :
        self.findImagesFromPath()
        inputFileName = scribus.fileDialog('Save as CSV file',  "*.csv", 'flashcards.csv', issave=True)
        if inputFileName != "":

            indexUpper = None
            indexFR = None
            for header in headers :
                if header.isupper() :
                    indexUpper = headers.index(header)
                elif "FR" in header :
                    indexFR = headers.index(header)

            try:
                with open(inputFileName, 'w', encoding='UTF8', newline='') as csvfile:
                    csvWriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                    csvWriter.writerow(headers)
                    scribus.progressReset()
                    scribus.progressTotal(len(self.imagesFiles))
                    i=1
                    for image in self.imagesFiles :
                        scribus.progressSet(i)
                        i+=1
                        filebasename =Path(image).stem.replace("-"," ").replace("_"," ").lower()
                        row = [filebasename] * len(headers)
                        if indexUpper != None :
                            row[indexUpper] = filebasename.upper()
                        if indexFR != None :
                            row[indexFR] = " "

                        row[imageIndex]=image
                        csvWriter.writerow(row)
                    scribus.progressReset()

            except Exception as e :
                scribus.messageBox("processCrosswords", "Error: %s"%e)
                logging.exception(e)
                scribus.progressReset()
        scribus.messageBox("processCrosswords",f"File created : {os.path.abspath(inputFileName)}")
        return inputFileName

class ImagierScribus(object):
    def __init__(self):
        self.headers=[]
        self.card=None
        self.cardsize=None
        self.cardName="card"
        self.currentPage=1

        scribus.gotoPage(self.currentPage)
        objList = scribus.getPageItems()

        for item in objList:
            if item[1] == 12: #type 12 == group
                self.card=item[0]
                break
        if self.card==None :
            scribus.messageBox('Error', 'No card model found')
            sys.exit(1)

        self.cardsize = scribus.getSize(self.cardName)
        self.marginTop, self.marginStart, self.marginEnd, self.marginBottom = scribus.getPageMargins()
        self.pageWidth, self.pageHeight = scribus.getPageSize()

    def initFromCardModel(self) :
        scribus.deselectAll()
        newObjList=scribus.duplicateObjects([self.cardName])
        scribus.selectObject(newObjList[0])
        scribus.unGroupObject()
        childObjectCount = scribus.selectionCount()
        imageHeader = None
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
                    if text not in self.headers :
                        self.headers.append(text)

            elif scribus.getObjectType(element) == "ImageFrame" :
                filename = scribus.getImageFile(element)
                result = re.search('%VAR_(\w+)%', filename)
                if result != None :
                    imageHeader =result.group(1)
        objName=scribus.groupObjects()
        scribus.deleteObject(objName)
        scribus.deselectAll()
        if imageHeader==None :
            scribus.messageBox('Warning', 'No image template found in model')
        else :
            self.headers.append(imageHeader)

    def checkHeader(self, headers) :
        for header in self.headers :
            if header not in headers :
                scribus.messageBox('Error', f"Header {header} from CSV file is not found in model card {self.headers}")
                sys.exit(1)

    def resizeImageFrameObj(self, obj):
        frameW, frameH = scribus.getSize(obj)
        scribus.setScaleImageToFrame(scaletoframe=1, proportional=0, name=obj)
        fullX, fullY = scribus.getImageScale(obj)
        scribus.setScaleImageToFrame(scaletoframe=1, proportional=1, name=obj)
        scaleX, scaleY = scribus.getImageScale(obj)

        imageW = frameW * (scaleX / fullX)
        imageH = frameH * (scaleY / fullY)

        imageY = (frameH - imageH) / 2.0
        imageX = (frameW - imageW) / 2.0

        scribus.setImageOffset(imageX, imageY, obj)

    def createCard(self, cardData, x, y) :

        newObjList=scribus.duplicateObjects([self.cardName])
        scribus.selectObject(newObjList[0])
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
                        index = self.headers.index(text)
                        if index >= 0:
                            textLength = scribus.getTextLength(element)
                            scribus.insertText(cardData[index], -1, element)
                            scribus.selectText(0,textLength,element)
                            scribus.deleteText(element)
                    except Exception as e :
                        scribus.messageBox("error", f" {e} for item {text}")

            elif scribus.getObjectType(element) == "ImageFrame" :
                filename = scribus.getImageFile(element)
                result = re.search('%VAR_(\w+)%', filename)
                if result != None :
                    filename = result.group(1)
                    try:
                        index = self.headers.index(filename)
                        if index >= 0:
                            scribus.loadImage(cardData[index], element)
                            self.resizeImageFrameObj(element)
                    except Exception as e :
                        scribus.messageBox("error", f" {e} for item {filename}")

        scribus.groupObjects()
        scribus.deselectAll()


    def createCardsList(self, data) :
        scribus.progressReset()
        scribus.progressTotal(len(data))
        i=1
        x=self.marginStart
        y=self.marginTop

        for dataItem in data :
            scribus.progressSet(i)
            i+=1
            #scribus.messageBox("error", f" createCardsList x={x} y={y} w={self.cardsize[0]} h={self.cardsize[1]} maxX={self.pageWidth-self.marginEnd} maxY={self.pageHeight-self.marginBottom}")
            if y+self.cardsize[1] > self.pageHeight-self.marginBottom :
                x= self.marginStart
                y=self.marginTop
                scribus.newPage(-1)
                self.currentPage=self.currentPage+1
                scribus.gotoPage(self.currentPage)

            self.createCard( dataItem, x, y)

            if x+2*self.cardsize[0] <= self.pageWidth-self.marginEnd :
                x+=self.cardsize[0]
            else :
                x= self.marginStart
                y += self.cardsize[1]

        scribus.progressReset()
        scribus.deleteObject(self.cardName)

    def processCsvDataFile(self) :
        csvData = []
        csvfileName = scribus.fileDialog("Open CSV data file", "*.csv")
        if csvfileName != "":
            try:
                # Load file contents
                with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                    self.checkHeader( reader.fieldnames)
                    for row in reader:
                        filteredRow = [ row[key] for key in row.keys() if key in self.headers ]
                        csvData.append(filteredRow)
                self.createCardsList(csvData)
            except Exception as e :
                scribus.messageBox("CSV", "Error processing file %s"%e)
                sys.exit(1)


if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    imagier = ImagierScribus()
    imagier.initFromCardModel()

    action = scribus.valueDialog('Create or select CSV file ?','0 = create\n1 = select','0')

    if action=='0' :
        csvCreator = CsvCreator()
        csvCreator.createCsvFile( imagier.headers, len(imagier.headers)-1)
    else :
        imagier.processCsvDataFile()
        scribus.docChanged(1)
        scribus.setRedraw(True)
        scribus.redrawAll()
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


