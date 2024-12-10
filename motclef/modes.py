from krita import *
from PyQt5.QtWidgets import *
doc = Krita.instance().activeDocument()


def exportToPNG(path):
    path +='.png'
    doc = Krita.instance().activeDocument()
    doc.refreshProjection()
    pngOptions = InfoObject()
    pngOptions.setProperty('compression', 0) # 0 (no compression) to 9 (max compression)
    pngOptions.setProperty('indexed', False)
    pngOptions.setProperty('interlaced', False)
    pngOptions.setProperty('saveSRGBProfile', False)
    pngOptions.setProperty('forceSRGB', True)
    pngOptions.setProperty('alpha', True)
    doc.exportImage(path,pngOptions)

def exportToJpg(path) :
    path +='.jpg'
    doc = Krita.instance().activeDocument()
    doc.refreshProjection()
    pngOptions = InfoObject()
    pngOptions.setProperty('compression', 9) # 0 (no compression) to 9 (max compression)
    pngOptions.setProperty('indexed', False)
    pngOptions.setProperty('interlaced', False)
    pngOptions.setProperty('saveSRGBProfile', False)
    pngOptions.setProperty('forceSRGB', True)
    pngOptions.setProperty('alpha', True)
    doc.exportImage(path,pngOptions)

print( Krita.instance().readSetting('','ExportConfiguration-image/png','Not found!') )

for i in range(3) :
    path = str(doc.fileName().split('.')[0])+"_"+str(i)
    exportToPNG(path)
    print( Krita.instance().readSetting('','ExportConfiguration-image/png','Not found!') )
    doc.setBatchmode(True)

print( Krita.instance().readSetting('','ExportConfiguration-image/png','Not found!') )

doc.setBatchmode(False)