import tabula
import pandas as pd
import sys

from PyQt6.QtCore  import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from lib_shopware6_api import *
from my_shop_config import ConfShopware6ApiBase
from googletrans import Translator

from language import *


class Ui_MainWindow(object):
    def __init__(self):
        QDir.addSearchPath('icons', os.path.dirname(os.path.realpath(__file__))+r"\resources")
    
    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setWindowTitle(language.WindowTitle)
        self._createActions(MainWindow)
        self._createMenuBar(MainWindow)
        self._createToolBars(MainWindow)
    
    def _createActions(self, MainWindow):
        # File Actions
        self.openAction = QAction(QIcon("icons:file-open.png"), "&"+language.Actions.openAction, MainWindow)
        # Table actions
        self.newAction  = QAction(QIcon("icons:add-row.png"), "&"+language.Actions.newAction, MainWindow)
        self.deleteAction = QAction(QIcon("icons:delete-row.png"), "&"+language.Actions.deleteAction, MainWindow)
        self.saveAction = QAction(QIcon("icons:table-save.png"), "&"+language.Actions.saveAction, MainWindow)
        self.saveAllAction = QAction(QIcon("icons:table-save-all.png"), "&"+language.Actions.saveAllAction, MainWindow)
        # Shopware Actions
        self.translateAction = QAction(QIcon("icons:translate.png"), "&"+language.Actions.translateAction, MainWindow)
        self.uploadAction = QAction(QIcon("icons:upload.png"), "&"+language.Actions.uploadAction, MainWindow)
        # Exit Action
        self.exitAction = QAction("&Exit", MainWindow)
        # Help Action
        self.helpAction = QAction(QIcon("icons:help.png"), "&"+language.Actions.helpAction, MainWindow)
        self.changeLanguageAction = QAction(QIcon("icons:change-language.png"), "&"+language.Actions.changeLanguageAction, MainWindow)
        #Shortcuts
        self.openAction.setShortcut("Ctrl+O")
        self.newAction.setShortcut("Ctrl+N")
        self.deleteAction.setShortcut(QKeySequence.StandardKey.Delete)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAllAction.setShortcut("Ctrl+Shift+S")
        self.uploadAction.setShortcut("Ctrl+U")
        # Hints
        self.openAction.setToolTip(language.Hints.openHint)
        self.newAction.setToolTip(language.Hints.newHint)
        self.deleteAction.setToolTip(language.Hints.deleteHint)
        self.saveAction.setToolTip(language.Hints.saveHint)
        self.saveAllAction.setToolTip(language.Hints.saveAllHint)
        self.uploadAction.setToolTip(language.Hints.uploadHint)

    def _createMenuBar(self, MainWindow: QMainWindow):
        menuBar = MainWindow.menuBar()
        # File Menu
        fileMenu = QMenu("&"+language.Menu.file, MainWindow)
        menuBar.addMenu(fileMenu)
        fileMenu.addActions([self.openAction, fileMenu.addSeparator(), self.exitAction])
        # Table Menu
        tableMenu = QMenu("&"+language.Menu.table, MainWindow)
        menuBar.addMenu(tableMenu)
        tableMenu.addActions([self.newAction, self.deleteAction, self.saveAction, self.saveAllAction, self.translateAction, self.uploadAction])
        # Help Menu
        helpMenu = QMenu("&"+language.Menu.help, MainWindow)
        menuBar.addMenu(helpMenu)
        helpMenu.addActions([self.helpAction, self.changeLanguageAction])
    
    def _createToolBars(self, MainWindow: QMainWindow):
        # File toolbar
        fileToolBar = MainWindow.addToolBar("File")
        fileToolBar.addAction(self.openAction)
        # Table toolbar
        self.tableToolBar = QToolBar("Table", MainWindow)
        MainWindow.addToolBar(self.tableToolBar)
        self.tableToolBar.addActions([self.newAction, self.deleteAction, self.saveAction, self.saveAllAction])
        # Shopware upload
        self.uploadToolBar = QToolBar("Upload", MainWindow)
        MainWindow.addToolBar(self.uploadToolBar)
        self.uploadToolBar.addAction(self.translateAction)
        self.translationLanguageComboBox = QComboBox() 
        self.translationLanguageComboBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.translationLanguageComboBox.addItems((lan.name for lan in TranslationLanguages))
        self.translationLanguageComboBox.setCurrentIndex(0)
        self.uploadToolBar.addWidget(self.translationLanguageComboBox)
        self.uploadToolBar.addAction(self.uploadAction)


    
    
    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
















if __name__ == "__main__":
    language = Language.German()
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec())