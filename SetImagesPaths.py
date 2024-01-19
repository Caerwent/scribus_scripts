## Resets the default path for all %VAR images
## Default is on C:\, obviously can be changed
## Make sure to add the remainder of the path in the CSV file!!!

## contribution from jvr14115, https://github.com/berteh/ScribusGenerator/issues/102
## run from within Scribus > Script > run Script

import os
import scribus
import logging
from tkinter import Tk
from tkinter.filedialog import askdirectory

if scribus.haveDoc():
    #path = askdirectory(title='Select Folder') # shows dialog box and return the path
    path = scribus.fileDialog("Select Directory","","",False,False,True)
    restore_units = scribus.getUnit()   # since there is an issue with units other than points,
    scribus.setUnit(0)			# we switch to points then restore later.

    page = 1
    pagenum = scribus.pageCount()
    while (page <= pagenum):
        scribus.gotoPage(page)
        objList = scribus.getPageItems()
        for item in objList:
            if item[1] == 2: #type 2 == image
                obj=item[0]
                try:
                    imgFilename=scribus.getImageFile(obj)
                    imgFilename=os.path.join(path,os.path.basename(imgFilename))
                    scribus.loadImage(imgFilename,obj)
                    scribus.setScaleImageToFrame(scaletoframe=1, proportional=1, name=obj)
                except Exception as e:
                    scribus.messageBox('Error:', f'exception {e}')
                    logging.exception(e)
            elif item[1] == 12: #type 12 == group
                scribus.selectObject(item[0])
                scribus.unGroupObject(item[0])
                childObjectCount = scribus.selectionCount()
                for x in range(0, childObjectCount):
                    element = scribus.getSelectedObject(x)
                    if scribus.getObjectType(element) == "ImageFrame" :
                        imgFilename=scribus.getImageFile(element)
                        imgFilename=os.path.join(path,os.path.basename(imgFilename))
                        scribus.loadImage(imgFilename,element)
                        scribus.setScaleImageToFrame(1, 1, element)
                scribus.groupObjects()
        page += 1
    scribus.docChanged(1)
    scribus.setRedraw(True)
    scribus.redrawAll()
    scribus.setUnit(restore_units)
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)



