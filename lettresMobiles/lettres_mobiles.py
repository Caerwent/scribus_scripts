
import scribus
import logging
import csv
import traceback
import re
import os
from pathlib import Path
import math

def loadFont(styleName, fontName, fontSize) :
    localFontName = fontName
    try :
        scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
    except Exception as e :

        localFontName= "Arial Bold"
        scribus.messageBox("Error", f"Error: {e} \n Use default font {localFontName}.")
        try :
            scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
        except Exception as e2 :
            localFontName =scribus.getFontNames()[0]
            scribus.messageBox("Error", f"Error: {e} \n Use first font {localFontName}.")
            scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
    return localFontName

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
        self.charScissors = u"\u2702" #"✂"
        self.charPencil = u"\u270e" #"🖉"
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
        self.cStyleLetterSymbols = "char_style_letter_symbols"
        # paragraph styles
        self.pStyleWordRef = "char_style_word_ref"
        self.pStyleLetterUpper = "char_style_letter_upper"
        self.pStyleLetterLower = "char_style_letter_lower"
        self.pStyleLetterScript = "char_style_letter_script"
        self.pStyleLetterSymbols = "char_style_letter_symbols"

        self.cFontRef = "Comic Sans MS Regular"
        self.cFont = "Arial Bold"
        self.cFontLetter = "Script Ecole 2 Regular"
        self.cFontSymbols = "DejaVu Sans Bold"

        self.colorIcon = "colorIcon"
        self.defaultColor = "defaultColor"
        self.color1 = "color1"
        self.color2 = "color2"
        #fonts = scribus.getFontNames()
        #scribus.messageBox("processCrosswords", f"Fonts: { [elt for elt in fonts if elt.startswith('Deja')  ] }")
        scribus.defineColorRGB(self.color1, 0, 0, 255)
        scribus.defineColorRGB(self.color2, 0, 255, 0)
        scribus.defineColorRGB(self.colorIcon, 255, 0, 0)
        scribus.defineColorRGB(self.defaultColor, 0, 0, 0)

        self.imagePath = None
        self.imageAlbumPath = None
        self.masterPage = "grille_mots_ecole"

        self.csvData = []
        self.bzh_chars = [["C'H", "C"],["CH", "Q"]]
        self.nbPlayers = 0

        self.cFontRef = loadFont(styleName=self.cStyleWordRef, fontName=self.cFontRef, fontSize=20.0)
        self.cFontLetter = loadFont(styleName=self.cStyleLetterUpper, fontName=self.cFontLetter, fontSize=26.0)
        loadFont(styleName=self.cStyleLetterLower, fontName=self.cFontLetter, fontSize=26.0)
        loadFont(styleName=self.cStyleLetterScript, fontName=self.cFontLetter, fontSize=18.0)
        self.cFontSymbols = loadFont(styleName=self.cStyleLetterSymbols, fontName=self.cFontLetter, fontSize=18.0)

        scribus.createParagraphStyle(name=self.pStyleWordRef,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWordRef)
        scribus.createParagraphStyle(name=self.pStyleLetterUpper,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterUpper)
        scribus.createParagraphStyle(name=self.pStyleLetterLower,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterLower)
        scribus.createParagraphStyle(name=self.pStyleLetterScript,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterScript)
        scribus.createParagraphStyle(name=self.pStyleLetterSymbols,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleLetterSymbols)



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




    def _check_bzh(self, word):
        formatted = word.replace(self.bzh_chars[0][0], self.bzh_chars[0][1])
        formatted = formatted.replace(self.bzh_chars[1][0], self.bzh_chars[1][1])
        return formatted

    def _uncheck_bzh(self, char)
        if char ==  self.bzh_chars[0][1] :
            return self.bzh_chars[0][0]
         if char ==  self.bzh_chars[1][1] :
            return self.bzh_chars[1][0]
        return char

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
                resp=scribus.messageBox("Langue", "Gérer les lettres pour le Breton ?",     icon=scribus.ICON_NONE, button1=scribus.BUTTON_YES,     button2=scribus.BUTTON_NO)
                self.isBZH = resp==scribus.BUTTON_YES
                # Load file contents
                with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
                    self.checkHeader( reader.fieldnames)
                    for row in reader:
                        filteredRow = [ row[key] for key in row.keys() if key in self.headers ]
                        if(self.isBZH) :
                            filteredRow[self.indexWord] = [self._check_bzh(filteredRow[self.indexWord]), filteredRow[self.indexWord]]
                        else :
                            filteredRow[self.indexWord] = [filteredRow[self.indexWord], filteredRow[self.indexWord]]
                        self.csvData.append(filteredRow)
            except Exception as e :
                scribus.messageBox("CSV", "Error processing file %s"%e)
                sys.exit(1)

    def createText(self, x, y, width, height, text, paragraphStyle, color, isVerticalAlign) :
        textbox = scribus.createText(x, y, width,height)
        scribus.setText(text, textbox)
        scribus.setTextColor( color, textbox)
        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(paragraphStyle, textbox)
        if isVerticalAlign:
            scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
        scribus.deselectAll()
        return textbox

    def drawRefWord(self, x, y, dataRow) :
        wordLen = len(dataRow[self.indexWord][self.indexWordFormatted])
        tableWidth = wordLen*self.letterCellWidth
        imgMinWidth = 2*self.letterCellWidth
        imgMaxWidth = 3.5*self.letterCellWidth
        maxWordsWidth = self.pageWidth-x-self.marginEnd
        tableHeight = (self.mode+1)*self.letterCellHeight

        #scribus.messageBox("DEBUG", f"x={x} wordLen={wordLen} letterCellWidth={self.letterCellWidth} tableWidth={tableWidth} maxWordsWidth={maxWordsWidth}")
        if maxWordsWidth-(tableWidth) < imgMinWidth :
            scribus.messageBox("Error", f"Word {dataRow[self.indexWord][self.indexWord]} is too long")
            sys.exit(1)


        imgWidth = maxWordsWidth-(tableWidth)
        if imgWidth>imgMaxWidth :
            imgWidth=imgMaxWidth

        objectlist=[]
        rect = scribus.createRect(x, y, imgWidth+tableWidth, tableHeight)
        objectlist.append(rect)
        textbox = self.createText( x=x,
                                  y=y+tableHeight-self.letterCellHeight,
                                  width=imgWidth,
                                  height=self.letterCellHeight,
                                  text=dataRow[self.indexWord][self.indexWord].capitalize(),
                                  paragraphStyle=self.pStyleWordRef,
                                  color=self.defaultColor,
                                  isVerticalAlign=True)
        objectlist.append(textbox)


        if dataRow[self.indexImage]:
            img = scribus.createImage(x, y, imgWidth, tableHeight-self.letterCellHeight)
            scribus.loadImage(dataRow[self.indexImage], img)
            self.resizeImageFrameObj(img)
            objectlist.append(img)

        letterIdx=0
        xstart = x+imgWidth
        xl=0
        for l in range(wordLen+1) :
            xl = xstart+l*self.letterCellWidth
            line = scribus.createLine(xl,y,xl,y+tableHeight)
            scribus.setLineColor(self.defaultColor, line)
            objectlist.append(line)
            for r in range(self.mode+2) :
                yl=y+r*self.letterCellHeight
                line = scribus.createLine(xl, yl, xl+self.letterCellWidth, yl)
                objectlist.append(line)
            if l==0 :
                textbox = self.createText( x=xl,
                                  y=y,
                                  width=self.letterCellWidth,
                                  height=self.letterCellHeight,
                                  text=self.charPencil,
                                  paragraphStyle=self.pStyleLetterSymbols,
                                  color=self.colorIcon,
                                  isVerticalAlign=True)
                objectlist.append(textbox)
                textbox = self.createText( x=xl,
                                  y=y+self.letterCellHeight,
                                  width=self.letterCellWidth,
                                  height=self.letterCellHeight,
                                  text=self.charScissors,
                                  paragraphStyle=self.pStyleLetterSymbols,
                                  color=self.colorIcon,
                                  isVerticalAlign=True)
                textbox = self.createText( x=xl,
                                  y=y+2*self.letterCellHeight,
                                  width=self.letterCellWidth,
                                  height=self.letterCellHeight,
                                  text=self.charScissors,
                                  paragraphStyle=self.pStyleLetterSymbols,
                                  color=self.colorIcon,
                                  isVerticalAlign=True)
                objectlist.append(textbox)
        xl = xstart+(wordLen+1)*self.letterCellWidth
        line = scribus.createLine(xl,y,xl,y+tableHeight)
        scribus.setLineColor(self.defaultColor, line)
        objectlist.append(line)
        scribus.groupObjects(objectlist)
        return tableHeight

    def drawLettersBlock(self, objsList, x, y, nbRows, nbCols, letters, color, paragraphStyle) :
        for r in range(nbRows) :
            for c in range(nbCols) :
                 newrectangle = scribus.createRect(x,y,self.letterCellWidth,self.letterCellHeight)
                 scribus.setLineColor(color, newrectangle)
                 objsList.append(newrectangle)
                 textbox = self.createText( x=x,
                                  y=y,
                                  width=self.letterCellWidth,
                                  height=self.letterCellHeight,
                                  text=letters[r*nbCols+c],
                                  paragraphStyle=paragraphStyle,
                                  color=color,
                                  isVerticalAlign=True)
                 objsList.append(textbox)

    def getBestArrangement(self, y, wordsLetters, N) :
        maxWidthSpace = self.pageWidth - self.marginStart - self.marginEnd
        maxHeightSpaces=self.pageHeight-y- self.marginTop -self.marginBottom

        wordsLen = len(wordsLetters)
        nbCols= wordsLen
        nbRows = 1

        if wordsLen*self.letterCellWidth > maxWidthSpace :
            # search optimal block size
            blocksArrangements = []
            nbCols = math.floor(maxWidthSpace/self.letterCellWidth)
            nbBlocksPerLine = 1
            run = True
            cellSurface = self.letterCellWidth*self.letterCellHeight
            while run :
                nbBlocksPerLine = nbBlocksPerLine*2
                nbCols = math.floor(maxWidthSpace/nbBlocksPerLine/self.letterCellWidth)
                nbRows = math.ceil(wordsLen/nbCols)
                nbBlocksLines = math.ceil(N/nbBlocksPerLine)

                nbBlocksLinesOnCurrentPage = nbBlocksLines
                if nbBlocksLines*self.letterCellHeight > maxHeightSpaces :
                    nbBlocksLinesOnCurrentPage = math.floor(maxHeightSpaces/(nbRows*self.letterCellHeight )

                blockSurface = nbCols*nbRows*cellSurface
                allBlocksSurface = nbHBlocks*blockSurface*nbBlocksLines
                unUsed = maxWidthSpace * nbRows*nbBlocksLines*self.letterCellHeight - allBlocksSurface
                # need to take care about margin if nbBlocksLinesOnCurrentPage != nbBlocksLines

                blocksArrangements.append([nbCols, nbRows, unUsed])
                if nbCols == 1:
                    run = False

            blocksArrangements.sort(key=lambda elt: elt[2])

            return blocksArrangements[0]

        else return [nbCols, nbRows, 0]

    def drawLettersForWords(self, y, label, wordsLetters) :
        maxHeightSpaces=self.pageHeight-y- self.marginTop -self.marginBottom
        maxWidthSpace = self.pageWidth - self.marginStart - self.marginEnd
        yOffset = self.marginTop
        xOffset = self.marginStart
        N = self.nbPlayers * self.mode
         # 1 : mot sous l'image + tableau ligne écriture, ligne collage capitales
        # 2 : mot sous l'image + tableau ligne écriture, ligne collage capitales et minuscules
        # 3 : mot sous l'image + tableau ligne écriture, ligne collage minuscules et cursif
        paragraphStyles = [self.pStyleLetterUpper]
        if self.mode == 2 :
            paragraphStyles = [self.pStyleLetterUpper, self.pStyleLetterLower]
        if self.mode == 3 :
            paragraphStyles = [self.pStyleLetterLower, self.pStyleLetterScript]

        currentColor = self.defaultColor
        objsList = []
        # for each words sequence
        for currentWordsLetters in wordsLetters :
            blockArrangement = self.getBestArrangement(yOffset, currentWordsLetters, N)
            nbBlocksPerLine = math.floor(maxWidthSpace / blockArrangement[0]*self.letterCellWidth)
            nbBlocksLines = math.floor(N/nbBlocksPerLine)
            # draw letters block for each player and each mode
            n=1
            for p in range(self.nbPlayers) :
                for m in range(self.mode) :
                    self.drawLettersBlock( objsList=objsList, x=xOffset, y=yOffset, nbRows=blockArrangement[0], nbCols=blockArrangement[1], letters=currentWordsLetters, color=currentColor, paragraphStyle=paragraphStyles[m])
                    n+=1
                    if n<nbBlocksPerLine :
                        xOffset += blockArrangement[1]*self.letterCellWidth
                    else :
                        xOffset = self.marginStart
                        yOffset += blockArrangement[0]*self.letterCellHeight

                    if maxHeightSpaces < yOffset+ blockArrangement[0]*self.letterCellHeight :
                         scribus.newPage(-1)
                        self.currentPage=self.currentPage+1
                        scribus.gotoPage(self.currentPage)
                        yOffset = self.marginTop
                        xOffset = self.marginStart

                    scribus.groupObjects(objectlist)
                    objsList = []




    def processLetters(self) :
        currentDataPage = -1

        scribus.progressReset()
        scribus.progressTotal(len(self.csvData ))
        i=0
        wordsAndLetters = []
        letters = []
        label = ""
        for data in self.csvData :
            scribus.progressSet(i)
            i+=1
            if currentDataPage==-1:
                currentDataPage = data[self.indexPage]

            if currentDataPage != data[self.indexPage] :
                 wordsAndLetters.append([label, letters])
                 letters = []
                 label = ""
                 currentDataPage = data[self.indexPage]
            label+=data[self.indexWord]
            if self.isBZH :
                letters.append([self._uncheck_bzh(x) for x in data[self.indexWordFormatted]])
            else :
                letters.append([x for x in data[self.indexWordFormatted]])

        wordsAndLetters.append([label, letters])
        scribus.progressReset()

        scribus.newPage(-1)
        self.currentPage=self.currentPage+1
        scribus.gotoPage(self.currentPage)

        yOffset = self.marginTop

        for word in wordsAndLetters :
            yOffset += self.drawLettersForWords(yOffset, word[0], word[1])


    def loadImageAlbum(self) :
        if self.imageAlbumPath != "" :
            scribus.editMasterPage(self.masterPage)
            scribus.loadImage(self.imageAlbumPath, "ImageAlbum")
            self.resizeImageFrameObj("ImageAlbum")
            scribus.closeMasterPage()

    def processWords(self) :
        scribus.selectObject("ImageAlbum")
        imageAlbum = scribus.getSelectedObject(0)
        scribus.deselectAll()
        if imageAlbum == None :
            scribus.messageBox('Error', "Objet ImageAlbum non trouvé")
            sys.exit(1)
        x, y = scribus.getPosition("ImageAlbum")
        w, h =scribus.getSize("ImageAlbum")

        y +=h
        self.imageAlbumPath =  scribus.fileDialog("Open album image file", "*.jpg *.jpeg *.png *.webp")

        self.mode = int(scribus.valueDialog('Selection du mode','1 = collage capitales\n2 = collage capitales et minuscules\n3 = collage minuscules et cursif','0'))
        self.nbPlayers = int(scribus.valueDialog("Selection du nombre d'élèves",'Saisir un nombre > 0','0'))
        if self.nbPlayers <=0 :
            scribus.messageBox('Error', "Nombre d'élèves invalide")
            sys.exit(1)
        self.loadImageAlbum()
        perPageDataList = []
        currentPageDataList = []
        currentDataPage = -1

        scribus.progressReset()
        scribus.progressTotal(len(self.csvData ))
        i=0
        for data in self.csvData :
            scribus.progressSet(i)
            i+=1
            if currentDataPage==-1:
                currentDataPage = data[self.indexPage]

            if currentDataPage != data[self.indexPage] :
                   perPageDataList.append(currentPageDataList)
                   currentPageDataList = []
                   currentDataPage = data[self.indexPage]

            currentPageDataList.append(data)
        scribus.progressReset()
        perPageDataList.append(currentPageDataList)
        perPageDataList.sort(key=lambda element: element[0][self.indexPage])

        scribus.progressReset()
        scribus.progressTotal(len(perPageDataList ))
        i=0
        for perPageData in perPageDataList :
            scribus.progressSet(i)
            i+=1
            hSpace = 10
            if len(perPageData) > 2 :
                hSpace = 3
            yOffset=hSpace
            blockHeight=0
            for data in perPageData :
                blockHeight=self.drawRefWord(x, y+yOffset, data)
                yOffset += blockHeight+hSpace
            scribus.newPage(-1, self.masterPage)
            self.currentPage=self.currentPage+1
            scribus.gotoPage(self.currentPage)
        scribus.progressReset()

    def processData(self) :
        self.processWords()
        self.processLetters()


if scribus.haveDoc():

    letters = Letters()

    action = scribus.valueDialog('Create or select CSV file ?','0 = create\n1 = select','0')

    if action=='0' :
        csvCreator = CsvCreator()
        csvCreator.createCsvFile( letters.headers)
    else :
        pageunits = scribus.getUnit()
        scribus.setUnit(scribus.UNIT_MILLIMETERS)
        letters.loadCsvDataFile()
        letters.processData()
        scribus.docChanged(1)
        scribus.setRedraw(True)
        scribus.redrawAll()
        scribus.setUnit(pageunits)
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


