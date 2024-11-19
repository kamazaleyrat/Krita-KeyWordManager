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
EXPORT_FOLDER  = str(os.path.dirname(doc.fileName())+"\\export\\")

def infoBox(*message):
        infoBox = QMessageBox()
        infoBox.setWindowTitle('info : ')
        thisText=str()
        if type(message) is list :
            thisText.join(mot)
        else : thisText += str(message)
        infoBox.setText(thisText)
        infoBox.exec_()

def getKeyWordedLayers():
   
    nodeList=[]
    for node in Krita.instance().activeDocument().rootNode().findChildNodes(SEPARATOR,True,True): # get layer with Separator (so keyWords)
           nodeList.append(node)    
    return nodeList

def getLayersOf(*keyWord):
   
    nodeList=[]
    for word in keyWord :
        for node in Krita.instance().activeDocument().rootNode().findChildNodes(SEPARATOR+word,True,True):
            if node not in nodeList :
                nodeList.append(node)    
    return nodeList

def separateKeyWords(node):
    name = node.name()
    start = name.index(SEPARATOR) + len(SEPARATOR)
    wordList = name[start:].split(SEPARATOR)
    for i in range(len(wordList)) :
        wordList[i] = wordList[i].strip()
        if wordList[i].isspace() == True : wordList.pop(i) #delet the blank artefact due to comas

    return wordList

def getLayerNameOnly(node):
    name = node.name()
    end = name.index(SEPARATOR)
    name = name[:end].strip()
    return name

def getDocumentKeyWords():
    #print('ok1')
    global docKeyWordList
    newList = []
    for node in getKeyWordedLayers():
        thisWordList = separateKeyWords(node)
        for word in thisWordList :
            if word not in newList and word is not OFFWORD : newList.append(word)

    docKeyWordList = newList
    docKeyWordList.sort()
    print(docKeyWordList)
    return docKeyWordList

def modifyLayerKeyWord(layer,oldKey,newKey):
    layer.setName(layer.name().replace(oldKey,newKey))
    return layer.name()

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

class Mot():
    def __init__(self,name = 'motClef',visible = True):
        self.name = name
        self.isVisible = visible
        self.exportStyle = exportStyle[0]
        self.nodes = list()
        self.refreshNodes()

    def __str__(self):
        return str(self.name)
    def refreshNodes(self):
        self.nodes = [node for node in getLayersOf(self.name)]

class WordList():
    def __init__(self,wordsList = list()):
        self.content = list()
        if wordsList is not None :
            for mot in wordsList :
                self.addWord(mot)
                    
    def __str__(self) :
        return str(self.getAllWords())
    
    def getAllWords(self):
        thisListe = list()
        for mot in self.content :
            thisListe.append(mot.name)
        return thisListe
    
    def getAllNodes(self) :
        nodeList = []
        for word in self.content :
            thoseNodes = [node for node in word.nodes if node not in nodeList]
            nodeList.extend(thoseNodes)
        return nodeList
        
    def getThisMot(self,*name):
        for i in range(len(name)) :    
            for mot in self.content :
                if mot.name == name[i] :  return mot

    def addWord(self,word): #add 'Mot' object in the List object from a string 'name'
        print('adding '+word)
        if type(word) is str and word not in self.getAllWords() :
            self.content.append(Mot(word))

        elif type(word) is Mot and word not in self.content :
            self.content.append(word)
        else :
           print('This word is aleady in the list')

        this = self.content[-1]
        this.refreshNodes()
        return this

    def setlist(self,thisList):
        print('seting List')
        #infoBox('setup to 0')
        self.content.clear()
        for word in thisList :
                self.addWord(word)
        return True
    
class keyWordWidget() :

    #@pyqtSlot()

    def changeName(self): # change le motClef dans l'edit line et les calques
        for node in getLayersOf(self.mot.name):
            #if self.mot.name in node.name():
            modifyLayerKeyWord(node,self.mot.name,self.editLine.text())
        self.mot.name = self.editLine.text()
        self.nameLabel.setText(self.mot.name)
        self.parent.refreshList()

    def refresh(self):
        self.mot.isVisible = self.box.isChecked()
        self.nameLabel.setText(self.mot.name)
        self.editLine.setText(self.mot.name)

    def setWord(self,mot):
        self.mot = mot
        self.mot.refreshNodes()
        self.refresh()

    def addWordToNode(self): #ajouter le mot clef aux calques selectionnés
        newName = SEPARATOR+self.mot.name
        for node in getSelectedNodes():
            if newName not in node.name():
                name = node.name()
                name+=newName
                node.setName(name)
            self.mot.nodes.append(node)
                #infoBox('add in progress')
        self.parent.refreshList()

    def remWordfromNode(self):
        for node in getSelectedNodes():
            keyName = str(SEPARATOR+self.mot.name)
            if keyName in node.name():
                name = node.name().replace(keyName,'')
                node.setName(name) #enlever le mot clef aux calques selectionnés
            if node in self.mot.nodes :
                self.mot.nodes.remove(node)
        #self.parent.wordList.content.remove(self.mot)
        self.parent.refreshList()
   
    def toggleVisible(self): #rend visible ou invisible les calques avec le mot clef selon l'etat de la checkBox
        #infoBox('toggled')
        self.mot.isVisible = self.box.isChecked()
        for layer in self.mot.nodes :
            #infoBox(self.mot.nodes[0])
            layer.setVisible(self.mot.isVisible)

        Krita.instance().activeDocument().refreshProjection()
        Krita.instance().activeDocument().setModified(True)

    def __init__(self,mot,parent):

        #setup usefull properties
        self.mot = mot
        self.parent = parent
        self.nameLabel=QLabel()
        self.nameLabel.setText(self.mot.name)
        #print('init : '+name)
        # create self Layout
        self.widget = QWidget() #l'objet pricipal
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5,0,5,0)

        self.radio = QRadioButton(parent = self.parent.mainWidget)
        self.box = QCheckBox()    
        self.box.setChecked(True)
        self.editLine = QLineEdit()
        self.editLine.setText(self.mot.name)
        self.addButton = QPushButton()
        self.addButton.setIcon(Krita.instance().icon('paintLayer'))
        self.addButton.setToolTip("Add this keyWord to selected layers")
        self.removeButton = QPushButton()
        self.removeButton.setIcon(Krita.instance().icon('draw-eraser'))
        self.removeButton.setToolTip("Remove this keyWord from selected layers")


        #ajout des widget
        self.layout.addWidget(self.radio) 
        self.layout.addWidget(self.box)
        self.layout.addWidget(self.editLine)
        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.removeButton)
        self.widget.setLayout(self.layout)

        #buttons connection
        self.radio.clicked.connect(lambda : self.parent.soloVisible(self.radio,self))
        #self.box.toggled.connect(self.mot.isVisible = self.box.isChecked() )
        self.box.clicked.connect(lambda : self.parent.refreshView())
        self.box.toggled.connect(lambda : self.refresh())
        self.addButton.clicked.connect(lambda : self.addWordToNode())
        self.removeButton.clicked.connect(lambda : self.remWordfromNode())
        self.editLine.returnPressed.connect(lambda : self.changeName()) #initialisation des objet KeyWord
       
       
        # version Simple :
        self.simple = QWidget()
        simplelayout = QHBoxLayout()
        simplelayout.setContentsMargins(5,0,5,0)
        simplebox = QCheckBox()
        simplebox.setChecked(True)
        simplebox.setText(self.mot.name)
        simpleRadbutton =QRadioButton()


        #ajout des widget
        simplelayout.addWidget(simplebox)
        simplelayout.addWidget(simpleRadbutton)
        self.simple.setLayout(simplelayout)

    def __str__(self):
        return str(self.mot.name)

class HardWordWidget(keyWordWidget) : #keyWordWidget who can't be modified = jls_extract_def()
    def __init__(self,mot,parent):
        keyWordWidget.__init__(self,mot,parent)
        super().__init__(mot,parent)
        self.box.setText(self.mot.name)
        self.editLine.setVisible(False)
        self.radio.setVisible(False)
        self.box.toggled.connect(lambda : self.toggleVisible())

class ExportWidget() :

    def modifyExportStyle(self) :
        actualStyle = exportStyle.index(self.mot.exportStyle)
        if actualStyle+1 < len(exportStyle) : 
            self.mot.exportStyle  = exportStyle[actualStyle+1]
        else : 
            self.mot.exportStyle = exportStyle[0]
        self.setExportIcon()

    def setExportIcon(self):
        
        if self.mot.exportStyle == exportStyle[0] : 
            self.button.setIcon(Krita.instance().icon('addblankframe'))
            self.button.setToolTip("Get his one version")
        elif self.mot.exportStyle == exportStyle[1] : 
            self.button.setIcon(Krita.instance().icon('deletekeyframe'))
            self.button.setToolTip("Hide layer for all other versions")
        elif self.mot.exportStyle == exportStyle[2] : 
            self.button.setIcon(Krita.instance().icon('auto-key-on'))
            self.button.setToolTip("Show layer for all other versions")
        elif self.mot.exportStyle == exportStyle[3] : 
            self.button.setIcon(Krita.instance().icon('addduplicateframe'))
            self.button.setToolTip("Make an other full iteration with this one visible")      
    def getName(self) : 
        return self.mot.name
    def getExportStyle(self) :
        return self.mot.exportStyle
    def __init__(self,mot,parent) :
        self.parent = parent
        self.mot = mot
        self.layout = QHBoxLayout()
        self.label = QLabel(self.mot.name)
        self.button = QPushButton()
        self.setExportIcon()
        self.button.clicked.connect(lambda : self.modifyExportStyle())
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)

class ExportBox():
   
    def __init__(self) :
        
        #super.__init__()

        self.keyWordList = WordList(getDocumentKeyWords())
        self.listOfWidgetWords = list()      
        
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
        tableauChoix = ['Nom','Exporter','Masquer']


        for i in range(len(self.keyWordList.content)):
           self.listOfWidgetWords.append(ExportWidget(self.keyWordList.content[i],self.choixLayout))
           self.choixLayout.addLayout(self.listOfWidgetWords[-1].layout)
        
                
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
        show = [word.getName() for word in self.listOfWidgetWords if word.getExportStyle() == exportStyle[0]]
        hide = [word.getName() for word in self.listOfWidgetWords if word.getExportStyle() == exportStyle[1]]
        full = [word.getName() for word in self.listOfWidgetWords if word.getExportStyle() == exportStyle[2]]
        more = [word.getName() for word in self.listOfWidgetWords if word.getExportStyle() == exportStyle[3]]
         
        if self.onlyKeyedCheckBox.isChecked() ==True :
            for node in doc.rootNode().findChildNodes('',True,True):
                node.setVisible(True)
        #make all the layer Visible if the checkBox is checked

        for node in getLayersOf(*hide,OFFWORD) : #hide the off and hide layer
            node.setVisible(False)
 
        for node in getLayersOf(*full) : #make the full layer visible
            node.setVisible(True)
        
        doc.setBatchmode(True) #shut up damn png option
          
        if os.path.exists(self.folderLine.text()) == False :
                os.mkdir(self.folderLine.text())
                          
        # for each other key words, make an png export
        for mot in show :    
           
            folderPath = str(self.folderLine.text()+'\\')
            path = str(folderPath+doc.name()+"_"+mot+".png")   #make the specific name path for the export
            
            for node in getLayersOf(mot) : #make layers visible 
                node.setVisible(True)
            
            exportToPNG(path) #Export, of course
    
            for moreMot in more : # Make an other Iteration for the "more" Layers
                
                morePath = str(folderPath+doc.name()+"_"+mot+"_"+moreMot+".png") 
                for node in getLayersOf(moreMot) :
                        node.setVisible(True)
                exportToPNG(morePath)
                for node in getLayersOf(moreMot) : #make layers visible 
                    node.setVisible(False)
                
            for node in getLayersOf(mot) : 
                node.setVisible(False) #hide layers to let the other alone

        doc.setBatchmode(False) #ok you can talk again if you want

        infoBox('Export is done !')
        self.window.accept()
   
    def canvasChanged(self, canvas):
        pass

class LayerBox():

    def refreshView(self):

        showWord = [word for word in self.wordList.content if word.isVisible == True]
        showNodes = []

        for word in showWord :
            newNode = [node for node in word.nodes if node not in showNodes]
            if newNode :
                 showNodes.extend(newNode)
        
        for node in self.wordList.getAllNodes():
            if node in showNodes:
                node.setVisible(True)
            else : node.setVisible(False)

        Krita.instance().activeDocument().refreshProjection()
        Krita.instance().activeDocument().setModified(True)
    
    def refreshList(self, view = False) :

        try : self.wordList.setlist(getDocumentKeyWords())
        
        except :
            print('not setting list now')
            return False
        
        A = len(self.wordList.content)
        B = len(self.WordWidgetList)
        widgetWords = self.getWidgetsWords(self.WordWidgetList)
            
        for word in self.wordList.content : 
            word.nodes = getLayersOf(word.name)
            if word.name == OFFWORD : continue
            
            elif word not in widgetWords and A>B:
                self.addKeyWordWidget(word)
            
            elif word not in widgetWords and A<=B:
                thisWidget = self.getWidgetOf(word,wordIn = False)[0]
                thisWidget.setWord(word)
                thisWidget.widget.setVisible(True)
            
            else :
                thisWidget = self.getWidgetOf(word)[0]
                thisWidget.widget.setVisible(True)

        
      #  for widget in self.getWidgetOf(*self.wordList.content,wordIn = False):
       #     widget.widget.setVisible(False)
            
            
        if view :
            self.refreshView()

                
    def old_refreshList(self,view = False):
        #infoBox('refreshing')
        print("refreshing...")

        # get the '//keyword' in document layers (if ther is document)
        
        try : self.wordList.setlist(getDocumentKeyWords())

        except :
            print('notWorking')
            return False
       
        # Check if the number of EXISTANTs WIDGET  fit the numers of keywords in the list
        A,B = len(self.WordWidgetList), len(self.wordList.content)
        if A < B : #if not enought, create more :
            for i in range(B-A):
                self.addKeyWordWidget(self.wordList.content[A+i])

        #To refresh : hide all then show how much it's needed and write the good name on them
        alreadyNamedWidget = [widget for widget in self.WordWidgetList if widget.mot in self.wordList.content]
        for wordWidget in alreadyNamedWidget :
            wordWidget.widget.setVisible(True)


        for wordWidget in self.WordWidgetList :
            pass

        for i in range(len(self.wordList.content)) :
            #infoBox(self.wordList.content[i])
            
            self.WordWidgetList[i].widget.setVisible(True)
            self.WordWidgetList[i].setWord(self.wordList.content[i],getLayersOf(self.wordList.content[i].name))
        print('refresh List is ok')
        
        if view == True : 
            self.refreshView()
            print('Refreshing View is Ok')

        return True
    
    def getWidgetsWords(self, widgetList ) :
        widgetsWords = list() 
        for widget in widgetList :
            widgetsWords.append(widget.mot)
        return widgetsWords
    
    def getWidgetOf(self,*words, wordIn = True):
        thosesWidgets = []
        restWidgets = []
        for widget in self.WordWidgetList :
            if widget.mot in words and widget not in thosesWidgets:
                thosesWidgets.append(widget)
            else : 
                
                restWidgets.append(widget)

        
        if not thosesWidgets and wordIn == True :
            return False 
        
        elif wordIn == False : return restWidgets
        
        elif wordIn == True : return thosesWidgets

    def __init__(self):
       
        super().__init__()
        self.WordWidgetList = [] # objects list for keyWordWidgets widget
        self.wordList = WordList() # object for listing words
       
        # Main Windows Layout
        self.mainWidget = QWidget()
        layoutWindow = QVBoxLayout()
        #title
        label = QLabel("Mots clefs :")
        layoutWindow.addWidget(label)
        
        #key Word List Layout
        self.ListWidget = QGroupBox()
        self.ListLayout = QVBoxLayout()
        self.ListWidget.setLayout(self.ListLayout)
        layoutWindow.addWidget(self.ListWidget)
        self.mainWidget.setLayout(layoutWindow)

        # ligne pour le mot 'off' (calques ignorés à l'export)
        offWord = self.wordList.addWord('off')
        self.offKey  = HardWordWidget(offWord,self)
        self.offKey.box.setToolTip("'/Off' layers will be automatically hided at the export")
        layoutWindow.addWidget(self.offKey.widget)
        
        # Ligne nouveaux motClef
        newKeyLine = QLineEdit()
        newKeyLine.setText("motClef")
        layoutWindow.addWidget(newKeyLine)

        actualiseButton = QPushButton("Actualiser Mot Clef")
        actualiseButton.setIcon(Krita.instance().icon('view-refresh'))
        layoutWindow.addWidget(actualiseButton)

        #Buttons Effect
        actualiseButton.clicked.connect(lambda : self.refreshList(True))
        #   actualiseButton.setFocusPolicy(ClickFocus)
        newKeyLine.returnPressed.connect(lambda : self.newkeyFromLine(newKeyLine.text()))
        newKeyLine.textChanged.connect(lambda :newKeyLine.setFocus(False) )

        self.refreshList()
        

    def soloVisible(self,this,wordWidget):
        
        self.offKey.box.setChecked(False)
        self.offKey.mot.isVisible=False
        
        if this.isChecked() == True :
            for widget in self.WordWidgetList :
                    widget.mot.isVisible = False
                    widget.box.setChecked(False)
                    widget.radio.setDown(False)
            wordWidget.box.setChecked(True)
            wordWidget.mot.isVisible = True
       
        self.refreshView()

    def newkeyFromLine(self,lineText):
        listOfMot = lineText.split(',')
        for i in range(len(listOfMot)):
           # infoBox(":"+listOfMot[i].strip()+"!")
            self.addKeyWordWidget(self.wordList.addWord(listOfMot[i].strip())).addWordToNode()
    
        self.refreshList()
        return True
    
    def addKeyWordWidget(self,keyWord):
        self.WordWidgetList.append(keyWordWidget(keyWord,self))
        thisWidget = self.WordWidgetList[-1]
        self.ListLayout.addWidget(thisWidget.widget)
        return thisWidget
   
class KeyWordDocker(DockWidget):

    def __init__(self):
        super().__init__()
         # object for listing words

        #fenêtre principale

        self.TotalWindow = QDialog(self)
        self.setWidget(self.TotalWindow)
        self.setWindowTitle(DOCKER_NAME)
        self.setWindowTitle(DOCKER_NAME)
        self.TotalLayout = QVBoxLayout()
        self.TotalWindow.setLayout(self.TotalLayout)

        #layer and export Box Layout
        self.layerBox = LayerBox().mainWidget
       
        # Main Windows Layout
        self.mainWidget = QWidget()
        self.TotalLayout.addWidget(self.layerBox)
        #self.TotalLayout.addWidget(self.exportWindow)
       
        self.exportButton = QPushButton("Exporter")
        #self.exportButton.setFocusPolicy(None)
        self.TotalLayout.addWidget(self.exportButton)
        #Buttons Effect
        self.exportButton.clicked.connect(lambda : ExportBox().window.show())    
    
    def switchWindow(self):
        if self.layerBox.isVisible() == True:
            self.layerBox.setVisible(False)
            self.exportWindow.setVisible(True)
            self.exportButton.setText("Layer Manager")
        elif self.exportWindow.isVisible() == True:
            self.exportWindow.setVisible(False)
            self.layerBox.setVisible(True)
            self.exportButton.setText("Export Manager")
        else :
            pass

    def canvasChanged(self, canvas):
        pass
        
test = KeyWordDocker()
