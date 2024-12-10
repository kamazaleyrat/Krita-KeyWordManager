from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSlot
from krita import  *

# add label to test notifier
newLayout = QVBoxLayout()
newLabel = QLabel('new label')
newLayout.addWidget(newLabel)

# hook up notifier object to watch for configuration changes
# https://api.kde.org/krita/html/classNotifier.html
appNotifier  = Krita.instance().notifier()
appNotifier.setActive(True)

# create dialog  and show it
newDialog = QDialog() 
newDialog.setLayout(newLayout)
newDialog.show() # show the dialog

def viewClosedEvent(closedView):
    newLabel.setText('view closed')
    print(closedView);

def viewOpenedEvent(openedView):
    newLabel.setText('view opened')
    print(openedView);
def changeDoc():
        newLabel.setText('Doc changed')
appNotifier.viewClosed.connect(viewClosedEvent)
appNotifier.viewCreated.connect(viewOpenedEvent)
mainWindow = Krita.instance().activeWindow()
mainWindow.activeViewChanged.connect(changeDoc)