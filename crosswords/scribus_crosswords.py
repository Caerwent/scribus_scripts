import scribus
import os
import logging
import traceback
import re
import control
import calculate
from control import Genxword
from calculate import Crossword

Letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U" ,"V", "W", "X", "Y", "Z" ]
currentPage=1


def inputOksol(text):
    resp=scribus.messageBox( "Are you happy with this solution?",  text,   icon=scribus.ICON_NONE, button1=scribus.BUTTON_YES,     button2=scribus.BUTTON_NO)
    return resp==scribus.BUTTON_YES

def inputIncrSize():
    resp=scribus.messageBox("crosswaord", "And increase the grid size? ",     icon=scribus.ICON_NONE, button1=scribus.BUTTON_YES,     button2=scribus.BUTTON_NO)
    return resp==scribus.BUTTON_YES


class GridCreator(object):
    def __init__(self, rows, cols, grid, wordlist, isBZH, empty='=', wordFont=None, wordFontSize=18.0):
        self.isBZH = isBZH
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.wordlist = wordlist
        self.empty = empty
        # character styles
        self.cStyleIndex = "char_style_index"
        self.cStyleWord = "char_style_word"
        self.cStyleWordIndex = "char_style_wordIndex"
        self.cStyleWordTitle = "char_style_wordTitle"
        # paragraph styles
        self.pStyleIndex = "par_style_index"
        self.pStyleWord = "par_style_word"
        self.pStyleWordTitle = "par_style_wordTitle"
        self.pStyleWordIndex = "par_style_wordIndex"

        self.cFont = "Arial Bold"
        self.cFontWord = "Arial Bold"

        self.colorH = "colorH"
        self.colorV = "colorV"
        self.imagePath = None
        self.pointToMillimeter = 0.352777778

        scribus.createCharStyle(name=self.cStyleIndex,font=self.cFont, fontsize=18.0)
        scribus.createCharStyle(name=self.cStyleWordIndex,font=self.cFont, fontsize=14.0)
        scribus.createCharStyle(name=self.cStyleWordTitle,font=self.cFont, fontsize=24.0)

        scribus.createParagraphStyle(name=self.pStyleIndex,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleIndex)
        scribus.createParagraphStyle(name=self.pStyleWordTitle,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWordTitle)
        scribus.createParagraphStyle(name=self.pStyleWordIndex,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWordIndex)

        scribus.defineColorRGB(self.colorH, 0, 0, 255)
        scribus.defineColorRGB(self.colorV, 255, 0, 0)

        #selectedWordFont=scribus.itemDialog("Font", "Choose a Font", scribus.getFontNames())
        #scribus.messageBox("processCrosswords", "Fonts: %s"%scribus.getFontNames())
        if wordFont != None :
            self.cFontWord=wordFont

        try :
            scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSize)
        except Exception as e :
            scribus.messageBox("processCrosswords", "Error: %s \n Use default font."%e)
            self.cFontWord = "DejaVu Sans Condensed Bold"
            try :
                scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSize)
            except Exception as e2 :
                self.cFontWord =scribus.getFontNames()[0]
                scribus.createCharStyle(name=self.cStyleWord,font=self.cFontWord, fontsize=wordFontSize)
        	
        scribus.createParagraphStyle(name=self.pStyleWord,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWord)

        path = scribus.fileDialog("Select image directory","","",False,False,True)
        if path != "":
            self.imagePath = path

        #self.cellType = Dialogs.itemDialog('Cell type', 'Select empty cells type', ['hashes', 'waves'])
        self.cellType = scribus.valueDialog('Select empty cells type','0 = hashes\n1 = waves','0')

    def getModelTopOffset(self) :
        if "ecole" in scribus.masterPageNames() :
            scribus.editMasterPage("ecole")

            scribus.selectObject("TexteCompetence")
            textBottom = scribus.getSelectedObject(0)
            scribus.deselectAll()
            if textBottom != None :
                x, y = scribus.getPosition("TexteCompetence")
                w, h =scribus.getSize("TexteCompetence")

            scribus.closeMasterPage()
            scribus.gotoPage(1)
            return y+h+10
        else :
            return 0

    def order_number_words(self):
        self.wordlist.sort(key=itemgetter(calculate.IDX_ROW, calculate.IDX_COL))
        count, icount = 1, 1
        for word in self.wordlist:
            word.append(count)
            if icount < len(self.wordlist):
                if word[IDX_ROW] == self.wordlist[icount][calculate.IDX_ROW] and word[calculate.IDX_COL] == self.wordlist[icount][calculate.IDX_COL]:
                    pass
                else:
                    count += 1
            icount += 1

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

        scribus.setImageOffset(imageX/self.pointToMillimeter, imageY/self.pointToMillimeter, obj)

    def createWordView(self, x, y, width, word, row, col, orientation, imgFile) :
        objectlist=[]
        height = 25
        newrectangle = scribus.createRect(x,y,width,height)
        img = scribus.createImage(x+1, y+1, height-2, height-2)

        if self.imagePath !=None :
            scribus.loadImage(os.path.join(self.imagePath,imgFile), img)
        else :
            scribus.loadImage(imgFile, img)

        self.resizeImageFrameObj(img)
        #scribus.setScaleImageToFrame(scaletoframe=1, proportional=1, name=img)

        textbox=scribus.createText(x+height+1, y+1, width-height-2, height-2)
        coord='\n'+Letters[row]+str(col+1)
        scribus.setText(word, textbox)
        if orientation==1 :
            scribus.setTextColor(self.colorV, textbox)
        else :
            scribus.setTextColor(self.colorH, textbox)
        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(self.pStyleWordIndex, textbox)
        scribus.deselectAll()

        textlen = scribus.getTextLength(textbox)
        scribus.insertText(coord,-1,textbox)
        scribus.selectText(textlen-3, 3, textbox)
        scribus.setStyle(self.pStyleWord, textbox)
        scribus.deselectAll()



        objectlist.append(newrectangle)
        objectlist.append(img)
        objectlist.append(textbox)
        scribus.groupObjects(objectlist)
        return height

    def addWordsList(self, startY, wordsList, isHorizontal) :
        y=startY
        wordMargin = 10
        marginH, marginL, marginR, marginB = scribus.getPageMargins()
        pageWidth, pageHeight = scribus.getPageSize()
        wordWidth = (pageWidth-marginR-marginL)/2-wordMargin
        isLeft = True
        direction = 0 if isHorizontal else 1
        #filteredWords = filter(lambda word: word[calculate.IDX_DIR]==direction, wordsList)
        filteredWords = [ word for word in wordsList if word[calculate.IDX_DIR]==direction ]
        #random.shuffle(filteredWords)

        scribus.progressReset()
        scribus.progressTotal(len(filteredWords))
        i=1
        for word in filteredWords:
            scribus.progressSet(i)
            i+=1
            fheight = self.createWordView(
                int(marginL) if isLeft else int(marginL)+wordWidth+wordMargin,
                int(y),
                wordWidth,
                word[calculate.IDX_WORD_ORIG],
                word[calculate.IDX_ROW],
                word[calculate.IDX_COL],
                word[calculate.IDX_DIR],
                word[calculate.IDX_IMG])
            isLeft = not isLeft
            if isLeft:
                y += fheight+wordMargin
        scribus.progressReset()
        return y

    def draw_cell_waves(self, group, lineCount, x, y, width, height) :
        yOffset = height/(lineCount+1)
        yOffsetDem = yOffset/2
        xOffset = width / 4
        xOffsetDem=xOffset/2
        # x, y, x1Control, y1Control, x2Control, y2Control
        P1 = [x, y+yOffset, x, y+yOffset, x, y+yOffset]
        P2 =  [x+xOffset, y, x+xOffset-xOffsetDem, y, x+2*xOffset, y]
        P3 =  [x+3*xOffset, y+2*yOffset, x+2*xOffset, y+2*yOffset, x+4*xOffset-xOffsetDem, y+2*yOffset]
        P4 =  [x+4*xOffset, y+yOffset, x+4*xOffset, y+yOffset, x+4*xOffset, y+yOffset]
        line = scribus.createBezierLine([x+2*xOffset, y, x+2*xOffset, y, x+2*xOffset, y,
                                         x+3*xOffset, y+yOffset, x+3*xOffset-xOffsetDem, y+yOffset, x+3*xOffset+xOffsetDem, y+yOffset,
                                         x+4*xOffset, y, x+4*xOffset, y, x+4*xOffset, y] )
        scribus.setLineColor("Black", line)
        group.append(line)
        for i in range(lineCount) :
            line = scribus.createBezierLine([P1[0], P1[1]+i*yOffset, P1[2], P1[3]+i*yOffset, P1[4], P1[5]+i*yOffset,
                                             P2[0], P2[1]+i*yOffset, P2[2], P2[3]+i*yOffset, P2[4], P2[5]+i*yOffset,
                                             P3[0], P3[1]+i*yOffset, P3[2], P3[3]+i*yOffset, P3[4], P3[5]+i*yOffset,
                                             P4[0], P4[1]+i*yOffset, P4[2], P4[3]+i*yOffset, P4[4], P4[5]+i*yOffset])
            scribus.setLineColor("Black", line)
            group.append(line)

        line = scribus.createBezierLine([x, y+(lineCount+1)*yOffset, x, y+(lineCount+1)*yOffset, x, y+(lineCount+1)*yOffset,
                                         x+xOffset, y+lineCount*yOffset, x+xOffsetDem, y+lineCount*yOffset, x+2*xOffset-xOffsetDem, y+lineCount*yOffset,
                                         x+2*xOffset, y+(lineCount+1)*yOffset, x+2*xOffset, y+(lineCount+1)*yOffset, x+2*xOffset, y+(lineCount+1)*yOffset] )
        scribus.setLineColor("Black", line)
        group.append(line)

    def draw_cell_hashes(self, group, x, y, width, height) :
        yOffset = height/4
        xOffset = width/4

        line = scribus.createLine(x, y+height, x+width, y)
        scribus.setLineColor("Black", line)
        group.append(line)

        for i in range(3) :
            line = scribus.createLine(x,y+(i+1)*yOffset, x+(i+1)*xOffset, y)
            scribus.setLineColor("Black", line)
            group.append(line)
            line = scribus.createLine(x+width,y+height-(i+1)*yOffset, x+width-(i+1)*xOffset, y+height)
            scribus.setLineColor("Black", line)
            group.append(line)

    def draw_grid(self, color="Black"):
        global Letters
        global currentPage

        pageWidth, pageHeight = scribus.getPageSize()
        marginH, marginL, marginR, marginB = scribus.getPageMargins()
        modelTopOffset = self.getModelTopOffset()

        gridMarginH = marginH
        if modelTopOffset!= 0 :
            gridMarginH = modelTopOffset

        x = int(marginL)
        y = int(gridMarginH)

        xStep = int( (pageWidth -marginR -marginL) / (self.cols+1))
        yStep = int( (pageHeight - marginB - gridMarginH) / (self.rows+1))
        maxX = x+(self.cols+1)*xStep
        if yStep > xStep:
            yStep = xStep

        maxY = y+(self.rows+1)*yStep

        scribus.progressTotal(self.cols+1)
        scribus.progressReset()
        objectlist=[]

        for i in range(self.cols):
            scribus.progressSet(i+1)
            textbox=scribus.createText((i+1)*xStep+x, y, xStep, yStep)
            objectlist.append(textbox)
            scribus.setText(str(i+1), textbox)
            scribus.setTextColor(self.colorV, textbox)
            scribus.deselectAll()
            scribus.selectObject(textbox)
            scribus.setParagraphStyle(self.pStyleIndex, textbox)
            scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
            scribus.deselectAll()

        scribus.groupObjects(objectlist)

        objectlist=[]

        scribus.progressReset()
        scribus.progressTotal(self.rows+1)
        for i in range(self.rows):
            scribus.progressSet(i+1)
            textbox=scribus.createText(x, (i+1)*yStep+y, xStep, yStep)
            objectlist.append(textbox)
            scribus.setText(Letters[i], textbox)
            scribus.setTextColor(self.colorH, textbox)
            scribus.deselectAll()
            scribus.selectObject(textbox)
            scribus.setParagraphStyle(self.pStyleIndex, textbox)
            scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
            scribus.deselectAll()
        scribus.groupObjects(objectlist)

        objectlist=[]
        scribus.progressReset()
        scribus.progressTotal(self.rows*self.cols+1)
        i=1
        for r in range(self.rows):
            for c in range(self.cols):
                scribus.progressSet(i)
                i+=1
                if self.grid[r][c] == self.empty:
                    if self.cellType == 1 :
                        self.draw_cell_waves(objectlist, 3, (c+1)*xStep+x, (r+1)*yStep+y, xStep, yStep)
                    else :
                        self.draw_cell_hashes(objectlist, (c+1)*xStep+x, (r+1)*yStep+y, xStep, yStep)
        scribus.groupObjects(objectlist)

        objectlist=[]
        scribus.progressReset()
        scribus.progressTotal(self.cols+1)
        for c in range(self.cols+1):
            scribus.progressSet(c+1)
            line = scribus.createLine((c+1)*xStep+x,y+yStep,(c+1)*xStep+x,maxY)
            scribus.setLineColor(color, line)
            objectlist.append(line)

        scribus.progressReset()
        scribus.progressTotal(self.rows+1)
        for r in range(self.rows+1):
            scribus.progressSet(r+1)
            line = scribus.createLine(x+xStep, (r+1)*yStep+y,maxX, (r+1)*yStep+y)
            scribus.setLineColor(color, line)
            objectlist.append(line)
        scribus.progressReset()
        scribus.groupObjects(objectlist)

        scribus.newPage(-1)
        currentPage=currentPage+1
        scribus.gotoPage(currentPage)


        textbox=scribus.createText(marginL, marginH, pageWidth-marginL-marginR, 10)

        scribus.setText( "A-BLAEN →" if self.isBZH else "HORIZONTALEMENT →", textbox)
        scribus.setTextColor(self.colorH, textbox)
        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(self.pStyleWordTitle, textbox)
        scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
        scribus.deselectAll()

        y=self.addWordsList(marginH+15, self.wordlist, True)
        textbox=scribus.createText(marginL, marginH+y+15, pageWidth-marginL-marginR, 10)
        scribus.setText("A-BLOM ↓" if self.isBZH else "VERTICALEMENT ↓" , textbox)
        scribus.setTextColor(self.colorV, textbox)
        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(self.pStyleWordTitle, textbox)
        scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
        scribus.deselectAll()
        self.addWordsList(marginH+y+15+10+15, self.wordlist, False)






def processCrosswords():
    """opens a csv file, reads it in and returns a 2 dimensional list with the data"""
    inputFileName = scribus.fileDialog("words list :: open file", "*.txt")
    if inputFileName != "":
        try:
            # Load file contents
            gen = Genxword(False)

            with open(inputFileName, newline='', encoding='utf-8') as inputfile:
                gen.wlist(inputfile)
                gen.grid_size()
                calc = gen.gengrid(inputOksol, inputIncrSize)
                if gen.wordFont!=None :
                    scribus.messageBox("Font", "Font : %s"%{gen.wordFont})
                exporter = GridCreator(calc.best_rows, calc.best_cols, calc.best_grid, calc.best_wordlist, gen.isBZH, calc.empty, gen.wordFont)
                exporter.draw_grid()

        except Exception as e :
            scribus.messageBox("processCrosswords", "Error: %s"%e)
            logging.exception(e)
            return False

        return True

    else:
        return False

if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    #scribus.createCharStyle("keychar", "DejaVu Sans Condensed Bold", 14.0,'','Black',1.0,'',0,0,0,0,0,0,0,0,0,1,1,-50)
    #scribus.createParagraphStyle("name", linespacingmode, linespacing, alignment, leftmargin, rightmargin, gapbefore, gapafter, firstindent, hasdropcap, dropcaplines, dropcapoffset, "charstyle")
    #scribus.createParagraphStyle(INDICE_STYLE,1,7.0,1,0,0,0,0,0,0,0,0,"keychar")

    #scribus.createCharStyle("wordchar", "DejaVu Sans Condensed Bold", 14.0,'','Black',1.0,'',0,0,0,0,0,0,0,0,0,1,1,-50)
    #scribus.createParagraphStyle(WORD_STYLE,1,7.0,1,0,0,0,0,0,0,0,0,"wordchar")

    currentPage=1
    scribus.gotoPage(currentPage)

    if(processCrosswords()) :
        scribus.docChanged(1)
        scribus.setRedraw(True)
        scribus.redrawAll()



else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)
