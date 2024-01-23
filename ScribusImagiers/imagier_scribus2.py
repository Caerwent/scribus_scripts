
import scribus
import logging
import csv
import traceback
import re


class CsvCreator(object):
    def __init__(self):
        self.imagePath = ""
        self.targetCsvFile = None
        self.validImages = [".jpg",".gif",".png",".tga"]
        self.imagesFiles = []

    def findImagesFromPath(self) :
         self.imagePath = scribus.fileDialog("Select image directory","","",False,False,True)

        for f in os.listdir(self.imagePath):
            if f.lower().endswith(valid_images):
                self.imagesFiles.append(os.path.join(path,f))

    def createCsvFile(self, headers, imageIndex) :
        inputFileName = scribus.fileDialog("Select destination CSV filet", "*.csv", "", False, True, False)
        if inputFileName != "":
            row = [""] * len(headers)
            try:
                with open(inputFileName, 'w', encoding='UTF8', newline='') as csvfile:
                    csvWriter = csv.writer(csvfile, delimiter='; ',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csvWriter.writerow(headers)
                    for image in self.imagesFiles :
                        row[imageIndex]=image
                        csvWriter.writerow(row)

             except Exception as e :
                 scribus.messageBox("processCrosswords", "Error: %s"%e)
                 logging.exception(e)
        return inputFileName

class ImagierScribus(object):
    def __init__(self):
        self.headers=[]
        self.card=None
        self.cardsize=None
        self.cardName="card"
        self.itemsInPage=0
        self.currentPage=1

        scribus.gotoPage(currentPage)
        objList = scribus.getPageItems()

        for item in objList:
            if item[1] == 12: #type 12 == group
                self.card=item[0]
                break
        if self.card==None :
            scribus.messageBox('Error', 'No card model found')
            sys.exit(1)

        self.itemsInPage=0
        self.cardsize = scribus.getSize(self.cardName)

    def initFromCardModel(self) :
        scribus.selectObject(self.cardName)
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
                    self.headers.append(text)

            elif scribus.getObjectType(element) == "ImageFrame" :
                filename = scribus.getImageFile(element)
                result = re.search('%VAR_(\w+)%', filename)
                if result != None :
                    imageHeader =result.group(1)
        if imageHeader==None :
            scribus.messageBox('Error', 'No image template found in model')
            sys.exit(1)
        self.headers.append(imageHeader)

    def checkHeader(self, header) :
        if self.headers != header :
            scribus.messageBox('Error', 'Headers from CSV file is not compatible with model card')
            sys.exit(1)

    def createCard(self, cardData, x, y) :
        scribus.copyObjects([self.cardName])
        newObjList = scribus.pasteObjects()
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
                        element
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
                except Exception as e :
                    scribus.messageBox("error", f" {e} for item {filename}")

        scribus.groupObjects()


    def createCardsList(self, data) :
        for dataItem in data :
            if self.itemsInPage >= 4 :
                self.itemsInPage = 0
                scribus.newPage(-1)
                self.currentPage=self.currentPage+1
                scribus.gotoPage(self.currentPage)
             itemsInPage = itemsInPage+1
            x=0
            y=0
            match self.itemsInPage:
                case 1:
                    x=0
                    y=0
                case 2:
                    x=self.cardsize[0]
                    y=0
                case 3 :
                    x=0
                    y=self.cardsize[1]
                case 4 :
                    x=self.cardsize[0]
                    y=self.cardsize[1]
            self.createCard( dataItem, x, y)

    def processCsvDataFile(self) :
        csvData = []
        csvfileName = scribus.fileDialog("Open CSV data file", "*.csv")
        if csvfileName != "":
            try:
                # Load file contents
                with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    line_count = 0
                    headers = None
                    for row in reader:
                        if line_count == 0:
                            headers = row
                            self.checkHeader(headers)
                            line_count += 1
                        else:
                            csvData.append(row)
                            line_count += 1
            except Exception as e :
                scribus.messageBox("CSV", "Error processing file %s"%e)
                sys.exit(1)


if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    imagier = ImagierScribus()
    imagier.initFromCardModel()

    action = scribus.valueDialog('Create or select CSV file ?','0 = create\n1 = select','0')
    if action==0 :
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


