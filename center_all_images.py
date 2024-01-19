 
#!/usr/bin/python
# align_image_in_frame.py
# This version 2014.04.19
"""
This script will align an image inside a frame to one of 9 possible positions:
Top left, top center, top right; middle left, middle center, middle right;
or bottom left, bottom center, bottom right.

USAGE
Select one or more image frames. Run the script, which asks for your alignment
choice. Possible legitimate entries are:
TL	TC	TR
ML	MC	MR
BL	BC	BR

and lowercase entries are also legitimate.

Note
There is minimal error checking, in particular no checking for frame type.

"""

import scribus
import logging

def resizeImageFrameObj(obj):
    frameW, frameH = scribus.getSize(obj)
    saveScaleX, saveScaleY = scribus.getImageScale(obj)
    scribus.setScaleImageToFrame(1, 0, obj)
    fullScaleX, fullScaleY = scribus.getImageScale(obj)
    scribus.setScaleImageToFrame(0, 0, obj)
    scribus.setImageScale(saveScaleX, saveScaleY, obj)
    imageW = frameW * (saveScaleX / fullScaleX)
    imageH = frameH * (saveScaleY / fullScaleY)

    imageY = (frameH - imageH) / 2.0
    imageX = (frameW - imageW) / 2.0
    scribus.setImageOffset(imageX, imageY, obj)

if scribus.haveDoc():
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
                   resizeImageFrameObj(obj)
                except Exception as e:
                    scribus.messageBox('Error:', f'exception {e}')
                    logging.exception(e)
            elif item[1] == 12: #type 12 == group
                scribus.selectObject(item[0])
                scribus.unGroupObject(item[0])
                childObjectCount = scribus.selectionCount()
                for x in range(0, childObjectCount):
                    obj = scribus.getSelectedObject(x)
                    if scribus.getObjectType(obj) == "ImageFrame" :
                         resizeImageFrameObj(obj)
                scribus.groupObjects()
        page += 1
    scribus.setUnit(restore_units)
    scribus.docChanged(1)
    scribus.setRedraw(True)
    scribus.redrawAll()
else:
    scribus.messageBox('Error', 'No document open')
    sys.exit(1)


