#BBD's Krita Script Starter Feb 2018
from krita import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from pathlib import Path

#from . import moduleExport

#usefull variable
DOCKER_NAME = 'Gestionnaire de Mot-Clef'
DOCKER_ID = 'pykrita_motclef'
SEPARATOR = '/' # le séparateur pour identifier les mots clef
OFFWORD = 'off'


docKeyWordList = [] #liste des mots clefs du document
doc = Krita.instance().activeDocument() #ID document
exportStyle = ('iterate','hide','full','moreIterate')
EXPORT_FOLDER  = str(os.path.dirname(doc.fileName())+"/export/")


def infoBox(*message):
        infoBox = QMessageBox()
        infoBox.setWindowTitle('info : ')
        thisText=str()
        if type(message) is list :
            for mot in message :
                thisText.join(mot)
        else : thisText += str(message)
        infoBox.setText(thisText)
        infoBox.exec_()

def getWordedLayers():
    nodeList=[]
    for node in doc.rootNode().findChildNodes(SEPARATOR,True,True): # get layer with Separator (so keyWords)
           nodeList.append(node)    
    return nodeList

def separateKeyWords(mot):
    start = (mot.index(SEPARATOR) + len(SEPARATOR))
    wordList = mot[start:].split(SEPARATOR)
    for i in range(len(wordList)) :
        wordList[i] = wordList[i].strip()
        if wordList[i].isspace() == True : wordList.pop(i) #delet the blank artefact due to comas
    return wordList

def getDocumentKeyWords():
    #print('ok1')
    global docKeyWordList
    newList = []
    for node in getWordedLayers():
        thisWordList = separateKeyWords(node.name())
        for word in thisWordList :
            if word not in newList and word is not OFFWORD : newList.append(word)

    docKeyWordList = newList
    docKeyWordList.sort()
    print(docKeyWordList)
    return docKeyWordList

def getSelectedNodes():
    w=Krita.instance().activeWindow()
    v=w.activeView()
    selectedNodes = v.selectedNodes()
    return selectedNodes

def exportToPNG(path):
    doc.refreshProjection()
    pngOptions = InfoObject()
    pngOptions.setProperty('compression', 9) # 0 (no compression) to 9 (max compression)
    pngOptions.setProperty('indexed', False)
    pngOptions.setProperty('interlaced', False)
    pngOptions.setProperty('saveSRGBProfile', False)
    pngOptions.setProperty('forceSRGB', True)
    pngOptions.setProperty('alpha', True)
    doc.exportImage(path,pngOptions)


class KeyWord() :
    
    listOfWords = [] #the list is sheared by all KeyWords
    
    def __init__(self,word):
        self.word = word
        self.relatedNodes = []
        self.listOfWords.append(self)      
        # widgets :
        self.widget = QWidget()
        self.solo = QRadioButton()
        self.solo.setToolTip("Make the only one visible")
        self.visible = QCheckBox()
        self.visible.setToolTip("Toogle visibility")
        self.edit = QLineEdit()
        self.writeButton = QPushButton()
        self.writeButton.setIcon(Krita.instance().icon('paintLayer'))
        self.writeButton.setToolTip("Add this keyWord to selected layers")
        self.eraseButton = QPushButton()
        self.eraseButton.setIcon(Krita.instance().icon('draw-eraser'))
        self.eraseButton.setToolTip("Remove this keyWord from selected layers")
        
        #set Layout
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.solo)
        self.layout.addWidget(self.visible)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.writeButton)
        self.layout.addWidget(self.eraseButton)
        
        #buttons Effect
        
        self.solo.clicked.connect(lambda : self.soloVisible())
        self.visible.toggled.connect(lambda : self.setVisibility())
        self.writeButton.clicked.connect(lambda : self.addWordToNode())
        self.eraseButton.clicked.connect(lambda : self.rmWordFromNode())
        self.edit.returnPressed.connect(lambda : self.changeWord(self.edit.text())) #initialisation des objet KeyWord
        self.refreshLabel()
                
    def getNodes(self) :
        global doc
        nodeList=[]
        for node in doc.rootNode().findChildNodes(SEPARATOR+self.word,True,True):
            if node not in nodeList :
                nodeList.append(node)
        self.relatedNodes = nodeList  
        return nodeList
    
    def refreshLabel(self):
        self.edit.setText(self.word)
        for node in self.getNodes() :
            if node.visible() == True:
                self.visible.setChecked(True)
    
    def setVisibility(self,visible, refresh = True, force = False):
       
        if not visible :
            visible = self.visible.isChecked()  # by default take the value of the visible checkBox
        else :
            self.visible.setChecked(visible)
        
        nodesToSet = [node for node in self.relatedNodes if node not in self.shared()]
        wordsToCheck = [word for word in self.shared('keyWord') if word.visible.isChecked == visible]
                
            
        for node in self.relatedNodes:
            node.setVisible(visible)
            
        if refresh == True :   #refresh view by default
            doc.refreshProjection()
            doc.setModified(True)
    
    def shared(self, value = 'node'):
        if value =='node' :
            communNodes = []
            for word in self.listOfWords :
                thisList = [node for node in self.relatedNodes if node in word.relatedNodes]
                communNodes.extend(thisList)
            return communNodes
        elif value =='keyWord' :
            keyWords = []
            for word in self.listOfWords :
                if self.shared('node'):
                    keyWords.append(word)
            return keyWords
                           
    def changeWord(self,newWord):
        for node in self.relatedNodes :
            node.setName(node.name().replace(self.word,newWord))
        self.word = newWord
    
    def setNew(self,newWord) :
        self.word = newWord
        self.refreshLabel()     
    
    def addWordToNode(self):
        for node in getSelectedNodes():
            if node not in self.relatedNodes :
                node.setName(f"{node.name()} {SEPARATOR}{self.word}")
                self.relatedNodes.append(node)
    
    def rmWordFromNode(self) :
        for node in getSelectedNodes():
            if node in self.relatedNodes :
                node.setName(node.name().replace(f"{SEPARATOR}{self.word}",''))
                self.relatedNodes.pop(node)    
    
    def soloVisible(self):
        for keyword in self.listOfWords :
            if keyword is not self :
                keyword.setVisibility(False,False)
        self.setVisibility(True)
        

class KeyWordDocker(DockWidget):
   
    def __init__(self) :
        super().__init__()
       
        self.Window = QDialog(self)
        
        self.setWidget(self.Window)
        self.setWindowTitle(DOCKER_NAME)
        self.Layout = QVBoxLayout()
        self.Window.setLayout(self.Layout)

        self.listLayout = QVBoxLayout()
        
        for word in getDocumentKeyWords():
            self.keyWordList.append(KeyWord(word))
            
        self.Layout.addLayout(self.listLayout)
        
        self.Window.show()

    def canvasChanged(self, canvas):
        pass

test = KeyWordDocker()