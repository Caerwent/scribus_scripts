
import scribus
import logging
import traceback
import re
import os
from pathlib import Path


class Anniversaire(object):
    def __init__(self):

        self.vowels = "aeiouyhàâäéèêëîïôöùûüÿ"
        self.ages="3456"
        self.pointToMillimeter = 0.352777778
        self.name = scribus.valueDialog("Saisie du nom","Entrez le prénom de l'élève.","")
        self.age = scribus.valueDialog("Saisie de l'âge",'Entrez son âge (3, 4, 5 ou 6).','3')
        if not (self.age in self.ages) :
            scribus.messageBox('Erreur', "L'âge doit être 3, 4, 5 ou 6.")
            sys.exit(1)
        currentPage=1
        scribus.gotoPage(currentPage)

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
    def replaceText(self, textFrame, varName, text) :
        textLen = len(text)
        varLen = len(varName)
        index = 0
        try:
            while index >= 0 :
                textInFrame = scribus.getAllText(textFrame)
                index = textInFrame.find(varName)

                if index>= 0 :
                    #insert new text
                    scribus.insertText(text, index, textFrame)
                    #remove variable
                    scribus.selectText(index+textLen,varLen,textFrame)
                    scribus.deleteText(textFrame)
                    #reset selection
                    scribus.selectText(0,0,textFrame)
        except Exception as e :
            scribus.messageBox("error", f" {e} for item {text}")

    def replaceNameAndAge(self) :
        objList = scribus.getPageItems()
        frName = "de "+self.name
        if self.name[0].lower() in self.vowels :
           frName = "d'"+self.name
        for item in objList:
            itemName = item[0]

            if scribus.getObjectType(itemName) == "TextFrame" :
                self.replaceText(itemName, "%PRENOM%", self.name)
                self.replaceText(itemName, "%PRENOM_FR%", frName)
                self.replaceText(itemName, "%A%", self.age)
                if self.age in "26" :
                    self.replaceText(itemName, "%B%", "V")
                    self.replaceText(itemName, "%b%", "v")
                else :
                    self.replaceText(itemName, "%B%", "B")
                    self.replaceText(itemName, "%b%", "b")

    def setAgeImage(self) :
        imageAlbum = scribus.selectObject("ImageAge")
        imageAlbum = scribus.getSelectedObject(0)
        scribus.deselectAll()
        if imageAlbum == None :
            scribus.messageBox('Erreur', "Objet ImageAge non trouvé")
            sys.exit(1)
        imagePath = self.age+".jpg"

        p = os.path.dirname( scribus.getDocName() )

        scribus.loadImage(os.path.join(p,imagePath), imageAlbum)
        self.resizeImageFrameObj(imageAlbum)

if scribus.haveDoc():

    restore_units = scribus.getUnit()   # since there is an issue with units other than points,

    anniversaire = Anniversaire()
    anniversaire.replaceNameAndAge()
    anniversaire.setAgeImage()

    scribus.docChanged(1)
    scribus.setRedraw(True)
    scribus.redrawAll()
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


