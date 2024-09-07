
import scribus
import logging
import csv
import traceback
import re
import os
from pathlib import Path
import math
import random

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


class EtiquettePolice(object):
    #a = 3 étiquettes capitales rouge-noir
    #b = 3 étiquettes capitales noires
    #c = 3 étiquettes minuscules en script
    #d = 3 étiquettes minuscules cursives

    def __init__(self, letterCode):
        self.fontName="Comic Sans MS Regular"
        self.isUpper = False
        self.hasFirstLetterColored = False
        self.fontsize = 20.0
        match letterCode:
            case "a":
                self.isUpper=True
                self.hasFirstLetterColored = True
            case "b":
                self.isUpper=True
            case "c":
                self.fontName="Liberation Serif Regular"
            case "d":
                self.fontName="Belle Allure GS Gras"
                self.fontsize = 18.0

         # paragraph styles
        self.cStyle = "char_style_"+letterCode
        self.pStyle = "paragraph_label_style_"+letterCode
        self.textColor = "textColor"
        self.firstCharColor = "firstCharColor"
        scribus.defineColorRGB(self.textColor, 0, 0, 0)
        scribus.defineColorRGB(self.firstCharColor, 255, 0, 0)
        self.fontName= loadFont(self.cStyle, self.fontName, self.fontsize)
        scribus.createParagraphStyle(name=self.pStyle ,  linespacingmode=1,linespacing=0,alignment=scribus.ALIGN_CENTERED, charstyle=self.cStyle)

    def createText(self, x, y, width, height, text) :
        textbox = scribus.createText(x, y, width,height)
        if self.isUpper :
            scribus.setText(text.upper(), textbox)
        else :
            scribus.setText(text, textbox)
        scribus.setTextColor( self.textColor, textbox)

        if self.hasFirstLetterColored :
            scribus.selectText(0, 1, textbox)
            scribus.setTextColor( self.firstCharColor, textbox)

        scribus.deselectAll()
        scribus.selectObject(textbox)
        scribus.setParagraphStyle(self.pStyle, textbox)
        scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED,textbox)
        scribus.deselectAll()
        return textbox


class Etiquette(object):
    def __init__(self, label, code, width, height):
        self.label=label
        #scribus.messageBox("DEBUG", f"Etiquette label={label} code={code}")
        self.police=EtiquettePolice(code)
        self.width = width
        self.height = height


    def draw(self, x, y) :
        objectlist=[]
        rect = scribus.createRect(x, y, self.width, self.height)
        objectlist.append(rect)
        textbox = self.police.createText(x, y, self.width, self.height, self.label)
        objectlist.append(textbox)
        scribus.groupObjects(objectlist)

class EtiquettesList(object):
    def __init__(self):
        self.currentPage=1
        scribus.gotoPage(self.currentPage)
        scribus.editMasterPage(scribus.masterPageNames()[0])
        scribus.setMargins(5, 5, 5, 5)
        scribus.closeMasterPage()

        scribus.setMargins(5, 5, 5, 5)
        self.pageWidth, self.pageHeight = scribus.getPageSize()

        self.itemWidth = (self.pageWidth-10.0)/3
        self.itemHeight = (self.pageHeight-10.0)/18


    def loadCsvDataFile(self) :
        self.etiquettes = []
        csvfileName = scribus.fileDialog("Open CSV data file", "*.csv")
        if csvfileName != "":
            try:
                # Load file contents
                with open(csvfileName, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, fieldnames=["label", "code"], delimiter=';', quoting=csv.QUOTE_NONE)
                    for row in reader:
                        label = row["label"]
                        code = row["code"]

                        for codeLetter in code :
                            self.etiquettes.append(Etiquette(label, codeLetter, self.itemWidth, self.itemHeight))

            except Exception as e :
                scribus.messageBox("CSV", "Error processing file %s"%e)
                sys.exit(1)

    def draw(self) :
        scribus.progressReset()
        scribus.progressTotal(len(self.etiquettes ))
        i=0
        currentHeight = 5
        for etiquette in self.etiquettes :
            scribus.progressSet(i)
            i+=1

            if round(currentHeight+self.itemHeight,2) > round(self.pageHeight-5,2) :
                scribus.newPage(-1)
                self.currentPage=self.currentPage+1
                scribus.gotoPage(self.currentPage)
                currentHeight = 5
            etiquette.draw(5.0, currentHeight)
            etiquette.draw(5.0+self.itemWidth, currentHeight)
            etiquette.draw(5.0+2*self.itemWidth, currentHeight)
            currentHeight = currentHeight+self.itemHeight
        scribus.progressReset()


#if scribus.newDocument(scribus.PAPER_A4, (5, 5, 5, 5), scribus.PORTRAIT, 1, scribus.UNIT_MILLIMETERS, scribus.NOFACINGPAGES, scribus.FIRSTPAGERIGHT,1) :
if scribus.haveDoc():

    pageunits = scribus.getUnit()
    scribus.setUnit(scribus.UNIT_MILLIMETERS)
    etiquettes = EtiquettesList()
    etiquettes.loadCsvDataFile()
    etiquettes.draw()
    scribus.docChanged(1)
    scribus.setRedraw(True)
    scribus.redrawAll()
    scribus.setUnit(pageunits)
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


