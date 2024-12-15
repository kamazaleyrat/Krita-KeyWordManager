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
            if word not in newList and word != OFFWORD : newList.append(word)

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
        self.listOfWords.append(self) # push himself in the list of words
        self.exportStyle = exportStyle[0]
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
        self.visible.toggled.connect(lambda : self.setVisibility(self.visible.isChecked()))
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
        self.getNodes()
        if self.relatedNodes == [] : self.remove()
        else : 
            for node in self.relatedNodes :
                if node.visible() == True:
                    self.visible.setChecked(True)
    
    def setVisibility(self,visible, refresh = True):
        if visible != self.visible.isChecked():
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
    
    def remove(self) : 
        #self.listOfWords.remove(self)
        self.widget.setParent(None)

    def rmWordFromNode(self) :
        for node in getSelectedNodes():
            if node in self.relatedNodes :
                node.setName(node.name().replace(f"{SEPARATOR}{self.word}",''))
                self.relatedNodes.remove(node)    
        if self.getNodes() == [] : self.remove()
            
    def soloVisible(self):
        for keyword in self.listOfWords :
            if keyword is not self :
                keyword.setVisibility(False,False)
                keyword.solo.setChecked(False)
        self.setVisibility(True)
        self.solo.setChecked(True)

class LockWord(KeyWord) : 

    def __init__(self,word):
        super().__init__(word)
        self.visible.setText(self.word)
        self.solo.setVisible(False)
        self.edit.setVisible(False)

    def rmWordFromNode(self) :
        for node in getSelectedNodes():
            if node in self.relatedNodes :
                node.setName(node.name().replace(f"{SEPARATOR}{self.word}",''))
                self.relatedNodes.remove(node)

class ExportWidget(KeyWord) :
    listOfWords = [] 
    def __init__(self,word) :
        #super().__init__()
        self.word = word
        self.relatedNodes = []
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.exportStyle = exportStyle[0]
        self.label = QLabel(self.word)
        self.button = QPushButton()
        self.setExportIcon()
        self.button.clicked.connect(lambda : self.modifyExportStyle())
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        
        self.getNodes()
    def setVisibility(self,visible):
        for node in self.relatedNodes:
            node.setVisible(visible)
   
    def soloVisible(self):
        for keyword in self.listOfWords :
            if keyword is not self and keyword.exportStyle != exportStyle[2]:
                keyword.setVisibility(False,False)
        self.setVisibility(True)      
    def modifyExportStyle(self) :
        actualStyle = exportStyle.index(self.exportStyle)
        if actualStyle+1 < len(exportStyle) : 
            self.exportStyle  = exportStyle[actualStyle+1]
        else : 
            self.exportStyle = exportStyle[0]
        self.setExportIcon()
        
    def setExportIcon(self):
        if self.exportStyle == exportStyle[0] : 
            self.button.setIcon(Krita.instance().icon('addblankframe'))
            self.button.setToolTip("Get his one version")
        elif self.exportStyle == exportStyle[1] : 
            self.button.setIcon(Krita.instance().icon('deletekeyframe'))
            self.button.setToolTip("Hide layer for all other versions")
        elif self.exportStyle == exportStyle[2] : 
            self.button.setIcon(Krita.instance().icon('auto-key-on'))
            self.button.setToolTip("Show layer for all other versions")
        elif self.exportStyle == exportStyle[3] : 
            self.button.setIcon(Krita.instance().icon('addduplicateframe'))
            self.button.setToolTip("Make an other full iteration with this one visible")      
    def getExportStyle(self) :
        return self.exportStyle
   
class ExportBox():
   
    def __init__(self) :

        self.keyWords = []
        self.window = QDialog()
        exportLayer = QVBoxLayout()
        self.window.setLayout(exportLayer)
        exportTitle = QLabel("Versionning PNG exports by Key Words")
        exportLayer.addWidget(exportTitle)
      
        #Layer list
        choixGroupe = QGroupBox()
        self.choixLayout = QVBoxLayout()
        choixGroupe.setLayout(self.choixLayout)
        exportLayer.addWidget(choixGroupe)

        keyWordList = getDocumentKeyWords()
        infoBox(keyWordList)
        for i in range(len(keyWordList)):
            self.keyWords.append(ExportWidget(keyWordList[i]))
            self.choixLayout.addWidget(self.keyWords[-1].widget)
                
        # only keyed layer checkBox
        self.onlyKeyedCheckBox = QCheckBox()
        self.onlyKeyedCheckBox.setText("Show all other layers")
        self.onlyKeyedCheckBox.setToolTip("If checked : make all layers without keyword visible. \n If not : let them as they are.")
        self.onlyKeyedCheckBox.setChecked(False)
        exportLayer.addWidget(self.onlyKeyedCheckBox)


        #folderBox for export path :
        folderLayout = QVBoxLayout()
        folderLabel = QLabel("Export folder :")
        folderLayout.addWidget(folderLabel)
        folderLineLayout = QHBoxLayout()
        self.folderLine = QLineEdit()
        self.folderLine.setText(EXPORT_FOLDER)
        folderButton = QPushButton()
        
        def changeExportFolder(text):
            global EXPORT_FOLDER
            EXPORT_FOLDER = text
            
        folderButton.clicked.connect(lambda : self.folderLine.setText(self.getExportPath()))
        self.folderLine.textChanged.connect(lambda : changeExportFolder(self.folderLine.text()))
        folderButton.setIcon(Krita.instance().icon('document-open'))
        folderLineLayout.addWidget(self.folderLine)
        folderLineLayout.addWidget(folderButton)
        folderLayout.addLayout(folderLineLayout)
        exportLayer.addLayout(folderLayout)

        # confirmBox
        buttonCancel = QPushButton("Annuler")
        buttonExport = QPushButton("Exporter")
        
        confirmLayout = QHBoxLayout()
        confirmLayout.addWidget(buttonCancel)
        confirmLayout.addWidget(buttonExport)

        buttonExport.clicked.connect(lambda : self.exportByChoice())
        buttonCancel.clicked.connect(lambda : self.window.reject())

        exportLayer.addLayout(confirmLayout)
    def getExportPath(self) :
        # first get the actual doc path 
        #wdir = os.path.dirname(doc.fileName())
        fileDialog = QFileDialog()
        fileDialog.setDirectory(EXPORT_FOLDER)
        fileDialog.setFileMode(QFileDialog.Directory)
        if fileDialog.exec_() :
            folderName = fileDialog.selectedFiles()
            if folderName == None : return EXPORT_FOLDER
            
            return folderName[0]      
    def makeVersionOf(*keyWord):
        pass
    def exportByChoice(self):
        show = [word for word in self.keyWords if word.exportStyle == exportStyle[0]]
        hide = [word for word in self.keyWords if word.exportStyle == exportStyle[1]]
        full = [word for word in self.keyWords if word.exportStyle == exportStyle[2]]
        more = [word for word in self.keyWords if word.exportStyle == exportStyle[3]]
         
        if self.onlyKeyedCheckBox.isChecked() ==True :
            for node in doc.rootNode().findChildNodes('',True,True):
                node.setVisible(True)
        #make all the layer Visible if the checkBox is checked
        KeyWord(OFFWORD).setVisibility(False)
        for keyWord in hide : #hide the off and hide layer
            keyWord.setVisibility(False)
 
        for keyWord in full : #make the full layer visible
            infoBox(keyWord.word)
            keyWord.setVisibility(True)
        
        doc.setBatchmode(True) #shut up damn png option
          

        if os.path.exists(self.folderLine.text()) == False :
                os.mkdir(self.folderLine.text())
                          

        for keyWord in show :    
            folderPath = str(self.folderLine.text()+'\\')
            path = str(folderPath+doc.name()+"_"+keyWord.word+".png")   #make the specific name path for the export
            
            keyWord.soloVisible()
            #infoBox(keyWord.relatedNodes)
            exportToPNG(path) #Export, of course
            
            for moreKeyWord in more : # Make an other Iteration for the "more" Layers
                morePath = str(folderPath+doc.name()+"_"+keyWord.word+"_"+moreKeyWord.word+".png") #change path
                moreKeyWord.setVisibility(True) 
                exportToPNG(morePath)
                moreKeyWord.setVisibility(False) 
                
             
            keyWord.setVisibility(False) #hide layers to let the other alone

        doc.setBatchmode(False) #ok you can talk again if you want

        infoBox('Export is done !')
        self.window.accept() 
    def canvasChanged(self, canvas):
        pass

class KeyWordDocker(DockWidget):
    

    def __init__(self) :
        super().__init__()
       
        self.Window = QDialog(self)
        self.setWidget(self.Window)
        self.setWindowTitle(DOCKER_NAME)
        self.Layout = QVBoxLayout()
        self.Window.setLayout(self.Layout)

        self.listLayout = QVBoxLayout()
        
        #list of words : 
        for word in getDocumentKeyWords():
            self.listLayout.addWidget(KeyWord(word).widget)
        self.listLayout.addWidget(LockWord(OFFWORD).widget)

        self.Layout.addLayout(self.listLayout)

        # create the new word Line : 
        self.newWord = QLineEdit("new Words, separate, by comas")
        self.newWord.returnPressed.connect(lambda : self.newkeyFromLine(self.newWord.text()))
        self.Layout.addWidget(self.newWord)
        #create the refresh Button
        self.refreshButton = QPushButton('Refresh')
        self.Layout.addWidget(self.refreshButton)
        self.refreshButton.clicked.connect(lambda : self.refreshList())

        #Create Export Button 
        self.exportButton = QPushButton("Export")
        self.Layout.addWidget(self.exportButton)

        self.exportButton.clicked.connect(lambda : ExportBox().window.show())

        self.Window.show()

    def refreshList(self) :
        for i in reversed(range(self.listLayout.count())) :
            word = self.listLayout.itemAt(i).widget()
            word.setParent(None)
        for word in getDocumentKeyWords():
            self.listLayout.addWidget(KeyWord(word).widget)
        self.listLayout.addWidget(LockWord(OFFWORD).widget)
    
    def newkeyFromLine(self,lineText):
        listOfMot = lineText.split(',')
        for i in range(len(listOfMot)):
            newWord = KeyWord(listOfMot[i].strip())
            newWord.addWordToNode()
        
        self.refreshList()
        return True
    
    def canvasChanged(self, canvas):
        pass
    
test = KeyWordDocker()
