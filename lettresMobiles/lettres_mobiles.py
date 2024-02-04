
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

    def createCsvFile(self, headers) :
        self.findImagesFromPath()
        inputFileName = scribus.fileDialog('Save as CSV file',  "*.csv", 'lettresMobiles.csv', issave=True)
        if inputFileName != "":
            try:
                with open(inputFileName, 'w', encoding='UTF8', newline='') as csvfile:
                    csvWriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)

                    scribus.progressReset()
                    scribus.progressTotal(len(self.imagesFiles))
                    csvWriter.writerow(headers)
                    i=1
                    for image in self.imagesFiles :
                        scribus.progressSet(i)
                        i+=1
                        filebasename =Path(image).stem.replace("-"," ").replace("_"," ").lower()
                        row = ["",filebasename,image]
                        csvWriter.writerow(row)
                    scribus.progressReset()

            except Exception as e :
                scribus.messageBox("processCrosswords", "Error: %s"%e)
                logging.exception(e)
                scribus.progressReset()
        scribus.messageBox("processCrosswords",f"File created : {os.path.abspath(inputFileName)}")
        return inputFileName

class Letters(object):
    def __init__(self):
        self.headers=[]

        self.currentPage=1

        self.headers = ["Page", "Mot", "Image"]
        self.indexPage=0
        self.indexWord=1
        self.indexImage=2
        self.indexWordFormatted = 0

        scribus.gotoPage(self.currentPage)

        self.letterCellWidth = 15
        self.letterCellHeight = 12
        self.charScissors = "✂"
        self.charPencil = "🖉"
        self.hasScript = False
        self.isBZH = True

        # 1 : mot sous l'image + tableau ligne écriture, ligne collage capitales
        # 2 : mot sous l'image + tableau ligne écriture, ligne collage capitales et minuscules
        # 3 : mot sous l'image + tableau ligne écriture, ligne collage minuscules et cursif
        self.mode=1

        # character styles
        self.cStyleWordRef = "char_style_word_ref"
        self.cStyleLetterUpper = "char_style_letter_upper"
        self.cStyleLetterLower = "char_style_letter_lower"
        self.cStyleLetterScript = "char_style_letter_script"
        # paragraph styles
        self.pStyleWordRef = "char_style_word_ref"
        self.pStyleLetterUpper = "char_style_letter_upper"
        self.pStyleLetterLower = "char_style_letter_lower"
        self.pStyleLetterScript = "char_style_letter_script"

        self.cFontRef = "Comic Sans MS"
        self.cFont = "Arial Bold"
        self.cFontLetter = "ScriptEcole2"

        self.colorIcon = "colorIcon"
        self.defaultColor = "defaultColor"
        self.colorH = "color1"
        self.colorV = "color2"

        scribus.defineColorRGB(self.color1, 0, 0, 255)
        scribus.defineColorRGB(self.color2, 0, 255, 0)
        scribus.defineColorRGB(self.colorIcon, 255, 0, 0)
        scribus.defineColorRGB(self.defaultColor, 0, 0, 0)

        self.imagePath = None

        self.csvData = []
        self.bzh_chars = [["C'H", "C"],["CH", "Q"]]

        scribus.createCharStyle(name=self.cStyleWordRef,font=self.cFontRef, fontsize=20.0)
        scribus.createCharStyle(name=self.cStyleLetterUpper,font=self.cFontLetter, fontsize=26.0)
        scribus.createCharStyle(name=self.cStyleLetterLower,font=self.cFontLetter, fontsize=26.0)
        scribus.createCharStyle(name=self.cStyleLetterScript,font=self.cFontLetter, fontsize=18.0)

        scribus.createParagraphStyle(name=self.pStyleWordRef,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWordRef)
        scribus.createParagraphStyle(name=self.pStyleLetterUpper,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterUpper)
        scribus.createParagraphStyle(name=self.pStyleLetterLower,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterLower)
        scribus.createParagraphStyle(name=self.pStyleLetterScript,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterScript)



        self.marginTop, self.marginStart, self.marginEnd, self.marginBottom = scribus.getPageMargins()
        self.pageWidth, self.pageHeight = scribus.getPageSize()


        #selectedWordFont=scribus.itemDialog("Font", "Choose a Font", scribus.getFontNames())
        #scribus.messageBox("processCrosswords", "Fonts: %s"%scribus.getFontNames())
        #if wordFont != None :
        #    self.cFontWord=wordFont
        #try :
        #    scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSize)
        #except Exception as e :
        #    scribus.messageBox("processCrosswords", "Error: %s \n Use default font."%e)
        #    self.cFontWord = "DejaVu Sans Condensed Bold"
        #    try :
        #        scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSize)
        #    except Exception as e2 :
        #        self.cFontWord =scribus.getFontNames()[0]
        #        scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSi




    def _check_bzh(word):
        formatted = word.replace(self.bzh_chars[0][0], self.bzh_chars[0][1])
        formatted = formatted.replace(self.bzh_chars[1][0], self.bzh_chars[1][1])
        return formatted

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

    def checkHeader(self, headers) :
        for header in self.headers :
            if header not in headers :
                scribus.messageBox('Error', f"Header {header} from CSV file is not compatible {self.headers}")
                sys.exit(1)

    def loadCsvDataFile(self) :
        self.csvData = []
        csvfileName = scribus.fileDialog("Open CSV data file", "*.csv")
        if csvfileName != "":
            try:
                # Load file contents
                with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                    self.checkHeader( reader.fieldnames)
                    for row in reader:
                        filteredRow = [ row[key] for key in row.keys() if key in self.headers ]
                        if(self.isBZH) :
                            filteredRow[self.indexWord] = [self._check_bzh(filteredRow[self.indexWord]), filteredRow[self.indexWord]]
                        else
                            filteredRow[self.indexWord] = [filteredRow[self.indexWord], filteredRow[self.indexWord]]
                        self.csvData.append(filteredRow)
            except Exception as e :
                scribus.messageBox("CSV", "Error processing file %s"%e)
                sys.exit(1)


    def drawRefWord(self, x, y, dataRow) :
        wordLen = dataRow[self.indexWord][self.indexWordFormatted]
        tableWidth = wordLen*self.letterCellWidth
        imgMinWidth = 2*self.letterCellWidth
        imgMaxWidth = 3.5*self.letterCellWidth
        maxWordsWidth = self.pageWidth-x-self.marginEnd
        tableHeight = (self.mode+1)*self.letterCellHeight

        if maxWordsWidth-(tableWidth) > imgMinWidth :
            scribus.messageBox("Error", f"Word {dataRow[self.indexWord][self.indexWord]} is too long")
            sys.exit(1)


        imgWidth = maxWordsWidth-(tableWidth)
        if imgWidth>imgMaxWidth :
            imgWidth=imgMaxWidth

        objectlist=[]
        rect = scribus.createRect(x, y, imgWidth+tableWidth, tableHeight)
        objectlist.append(rect)
        textbox = scribus.createText(x, y+tableHeight-self.letterCellHeight, imgWidth, self.letterCellHeight)
        objectlist.append(textbox)
        scribus.setText(dataRow[self.indexWord][self.indexWord])
        scribus.setTextColor( self.defaultColor, textbox)
        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(self.pStyleWordRef, textbox)
        scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
        scribus.deselectAll()

        img = scribus.createImage(x, y, imgWidth, tableHeight-self.letterCellHeight)

        if self.imagePath !=None :
            scribus.loadImage(os.path.join(self.imagePath,imgFile), img)
        else :
            scribus.loadImage(imgFile, img)

        self.resizeImageFrameObj(img)

        scribus.groupObjects(objectlist)

    def processData(self) :
        self.mode = scribus.valueDialog('Selection du mode','1 = collage capitales\n2 = collage capitales et minuscules\n3 = collage minuscules et cursif','0')



if scribus.haveDoc():

    letters = Letters()

    action = scribus.valueDialog('Create or select CSV file ?','0 = create\n1 = select','0')

    if action=='0' :
        csvCreator = CsvCreator()
        csvCreator.createCsvFile( letters.headers)
    else :
        pageunits = scribus.getUnit()
        scribus.setUnits(scribus.UNIT_MILLIMETERS)
        letters.loadCsvDataFile()
        scribus.docChanged(1)
        scribus.setRedraw(True)
        scribus.redrawAll()
        scribus.setUnit(pageunits)
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


