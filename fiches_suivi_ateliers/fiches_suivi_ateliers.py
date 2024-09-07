
import scribus
import logging
import csv
import traceback
import re
import os
from pathlib import Path

def loadFont(styleName, fontName, fontSize) :
    localFontName = fontName
    try :
        scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
    except Exception as e :
        localFontName= "Arial Regular"
        scribus.messageBox("Error", f"Error: {e} \n La font {fontName} n'a pas été trouvée, utilisation de {localFontName}.")
        try :
            scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
        except Exception as e2 :
            localFontName = result = list(filter(lambda x: x.startswith('Arial'), scribus.getFontNames()))[0]
            scribus.messageBox("Error", f"Error: {e} \n La font Arial Regular n'a pas été trouvée, utilisation de la font {localFontName}.")
            scribus.createCharStyle(name=styleName,font=localFontName, fontsize=fontSize)
    return localFontName

class FicheSuiviAtelierItem(object):
    def __init__(self, imageFilename):
        self.imageFilename = imageFilename
        self.parseFilename()

    def parseFilename(self) :
        self.name = Path(self.imageFilename).stem.replace("_"," ")


class FicheSuiviAtelier(object):
    def __init__(self):
        self.headers=[]
        self.card=None
        self.cardsize=None
        self.masterPageFirst = "Normal"
        self.masterPageOther = "pages"
        self.currentPage=1
        self.margeDroitePaire = 15
        self.margeDroiteImpaire = 5
        self.margeGauchePaire = 5
        self.margeGaucheImpaire = 15
        self.validImages = [".jpg",".gif",".png",".tga"]
        self.pointToMillimeter = 0.352777778

        scribus.editMasterPage(self.masterPageFirst)

        x,y = scribus.getPosition("objectifs")
        w,h = scribus.getSize("objectifs")
        self.pageWidth, self.pageHeight = scribus.getPageSize()
        self.topStart = y + h+5
        scribus.closeMasterPage()
        scribus.gotoPage(self.currentPage)

        self.defaultColor = "defaultColor"
        scribus.defineColorRGB(self.defaultColor, 0, 0, 0)

         # character styles
        self.cStyleWordRef = "char_style_word_ref"
        self.cStyleWordRefDate = "char_style_word_ref_date"
        # paragraph styles
        self.pStyleWordRef = "char_style_word_ref"
        self.pStyleWordRefDate = "char_style_word_ref_date"
        self.cFontRef = "Comic Sans MS Regular"

        self.cFontRef = loadFont(self.cStyleWordRef, self.cFontRef, 10.0)
        self.cFontRef = loadFont(self.cStyleWordRefDate, self.cFontRef, 12.0)

        scribus.createParagraphStyle(name=self.pStyleWordRefDate,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_LEFT, charstyle=self.cStyleWordRefDate)
        scribus.createParagraphStyle(name=self.pStyleWordRef,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyleWordRef)

        self.pageWidth, self.pageHeight = scribus.getPageSize()



    def initCardModel(self) :
        self.minCardWidth = 45
        self.cardImageHeight = 35

        self.cardWidth = (self.pageWidth - self.margeDroitePaire  - self.margeGauchePaire)/4
        #self.cardWidth = self.minCardWidth
        self.nbCardsH = 4

        if self.nameParsing :
            self.textH = 10*3
        else :
            self.textH = 10*2

        self.cardHeight = self.cardImageHeight+self.textH


    def findImagesFromPathAndCreateData(self) :
        self.imagePath = scribus.fileDialog("Select image directory","","",False,False,True)
        self.data = []
        for f in os.listdir(self.imagePath):
            for ext in self.validImages :
                if f.lower().endswith(ext):
                    self.data.append(
                        FicheSuiviAtelierItem(os.path.join(self.imagePath,f)))

        self.data.sort(key=lambda x: x.imageFilename.lower())


    def askForImageNameParsing(self) :
        resp=scribus.messageBox( "Nom des objets",  "Trouver les noms d'objets à partir du nom du fichier image ?",   icon=scribus.ICON_NONE, button1=scribus.BUTTON_YES,     button2=scribus.BUTTON_NO)
        self.nameParsing = resp==scribus.BUTTON_YES

    def resizeImageFrameObj(self, obj):
        frameW, frameH = scribus.getSize(obj)
        scribus.setScaleImageToFrame(scaletoframe=1, proportional=0, name=obj)
        fullX, fullY = scribus.getImageScale(obj)
        scribus.setScaleImageToFrame(scaletoframe=1, proportional=1, name=obj)
        scaleX, scaleY = scribus.getImageScale(obj)

        imageW = frameW * (scaleX / fullX)
        imageH = frameH * (scaleY / fullY)

        imageY = (frameH - imageH)
        imageX = (frameW - imageW) / 2.0

        scribus.setImageOffset(imageX/self.pointToMillimeter, imageY/self.pointToMillimeter, obj)

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

    def createCard(self, cardData, x, y) :

        objectlist=[]
        rect = scribus.createRect(x, y, self.cardWidth, self.cardHeight)
        objectlist.append(rect)

        img = scribus.createImage(x+0.2, y+0.2, self.cardWidth-0.4, self.cardImageHeight)
        scribus.loadImage(cardData.imageFilename, img)
        self.resizeImageFrameObj(img)
        objectlist.append(img)

        if self.nameParsing :
            textHeight = (self.cardHeight-self.cardImageHeight)/3
            textbox = self.createText( x=x,
                                  y=y+ self.cardImageHeight,
                                  width=self.cardWidth,
                                  height=textHeight,
                                  text=cardData.name,
                                  paragraphStyle=self.pStyleWordRef,
                                  color=self.defaultColor,
                                  isVerticalAlign=True)
            objectlist.append(textbox)
            textbox = self.createText( x=x,
                                  y=y+ self.cardImageHeight + textHeight,
                                  width=self.cardWidth,
                                  height=textHeight,
                                  text="Date :",
                                  paragraphStyle=self.pStyleWordRefDate,
                                  color=self.defaultColor,
                                  isVerticalAlign=False)
            objectlist.append(textbox)
            textbox = self.createText( x=x,
                                  y=y+ self.cardImageHeight + textHeight,
                                  width=self.cardWidth,
                                  height=textHeight,
                                  text="",
                                  paragraphStyle=self.pStyleWordRef,
                                  color=self.defaultColor,
                                  isVerticalAlign=False)
            objectlist.append(textbox)
        else :
            textHeight = (self.cardHeight-self.cardImageHeight)
            textbox = self.createText( x=x,
                                  y=y+ self.cardImageHeight,
                                  width=self.cardWidth,
                                  height=textHeight,
                                  text="Date :",
                                  paragraphStyle=self.pStyleWordRefDate,
                                  color=self.defaultColor,
                                  isVerticalAlign=True)
            objectlist.append(textbox)
            textbox = self.createText( x=x,
                                  y=y+ self.cardImageHeight + textHeight,
                                  width=self.cardWidth,
                                  height=textHeight,
                                  text="",
                                  paragraphStyle=self.pStyleWordRef,
                                  color=self.defaultColor,
                                  isVerticalAlign=False)
            objectlist.append(textbox)

        scribus.groupObjects(objectlist)
        scribus.deselectAll()

    def initPage(self) :
        self.marginStart = self.margeGaucheImpaire
        self.masterPage = self.masterPageFirst
        self.margeDroite = self.margeDroiteImpaire
        if (self.currentPage % 2) == 0:
            self.marginStart = self.margeGauchePaire
            self.margeDroite = self.margeDroitePaire

        if self.currentPage>1 :
            self.topStart = 0
            self.masterPage = self.masterPageOther

        self.startX=self.marginStart
        self.startY=self.topStart+5

    def createCardsList(self) :
        scribus.progressReset()
        scribus.progressTotal(len(self.data))
        i=1
        self.initPage()

        for dataItem in self.data :
            scribus.progressSet(i)
            i+=1
            #scribus.messageBox("error", f" createCardsList x={x} y={y} w={self.cardsize[0]} h={self.cardsize[1]} maxX={self.pageWidth-self.marginEnd} maxY={self.pageHeight-self.marginBottom}")
            if self.startY+self.cardHeight > self.pageHeight-5 :
                self.currentPage=self.currentPage+1
                self.initPage()
                scribus.newPage(-1, self.masterPage)
                scribus.gotoPage(self.currentPage)


            self.createCard( dataItem, self.startX, self.startY )

            if self.startX+2*self.cardWidth <= self.pageWidth-self.margeDroite :
                self.startX+=self.cardWidth
            else :
                self.startX= self.marginStart
                self.startY += self.cardHeight

        scribus.progressReset()




if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    ficheSuivi = FicheSuiviAtelier()
    ficheSuivi.findImagesFromPathAndCreateData()
    ficheSuivi.askForImageNameParsing()
    ficheSuivi.initCardModel()
    ficheSuivi.createCardsList()

    scribus.docChanged(1)
    scribus.setRedraw(True)
    scribus.redrawAll()
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


