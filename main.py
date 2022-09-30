import sys
import tabula
import pandas as pd

from PyQt6.QtCore  import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from lib_shopware6_api import *
from my_shop_config import ConfShopware6ApiBase
from googletrans import Translator

from language import *

class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
        return None

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
    
    def getHeaderKeys(self):
        return self._data.keys()
    
    def setHeaderData(self, col, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data.rename(columns={self._data.columns[col]:value}, inplace=True)
            return True
        return False


    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def getData(self):
        return self._data
    
    def removeRow(self, row, reset_index=True):
        if row in self._data.index:
            self._data.drop(index=row, inplace=True)
            if reset_index:
                self._data.reset_index(drop=True, inplace=True)
            # print(f"removed row {row}")
        else:
            print(f"no row {row}")
            print(f"index is: {self._data.index}")


class TableImport(QTableView):

    def __init__(self, parent = None):
    
        QTableView.__init__(self, parent)
    
    def contextMenuEvent(self, event):
        # print("triggered")
        menu = QMenu()
        delRow = menu.addAction("Delete selected Rows")
        delRow.triggered.connect(self.removeRowParameter)
        menu.exec(self.mapToGlobal(event.pos()))
    
    def removeRowParameter(self):
        for index in sorted(self.selectionModel().selectedRows()):
            # print('Row %d is selected' % index.row())
            self.model().removeRow(index.row(), False)
        self.model()._data.reset_index(drop=True, inplace=True)
    
    def dragEnterEvent(self, event):
        print("dragEnterEvent")
        event.accept()

    def dragMoveEvent(self, event):
        print("dragMoveEvent")
        event.accept()

    def dropEvent(self, event):
        print("dropEnterEvent")


class Ui_MainWindow(object):
    def __init__(self, MainWindow: QMainWindow, language: Language = Language.English):
        QDir.addSearchPath('icons', os.path.dirname(os.path.realpath(__file__))+r"\resources")
        self.language = Language.German
        self.MainWindow = MainWindow
        self.selectedFrameIndex = 0
        self.frameList = []
    
    def setupUi(self):
        self.MainWindow.setWindowTitle(self.language.WindowTitle)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()
        # Create Status Bar
        self.statusbar = self.MainWindow.statusBar()
        self.tableCountLabel = QLabel(f"{self.language.Tablecount}: 0")
        self.statusbar.setFont(QFont('Times', 11))
        self.statusbar.addPermanentWidget(self.tableCountLabel)

        #Create Tab Group
        self.tabGroup = QTabWidget(self.MainWindow)
        self.tabGroup.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabGroup.setDocumentMode(False)
        self.tabGroup.setTabsClosable(False)
        self.tabGroup.setTabBarAutoHide(False)
        self.MainWindow.setCentralWidget(self.tabGroup)
        self.tabGroup.setFont(QFont('Times', 13))
        # Create Tabs
        # Import Data Tab
        self.tab_Table = QWidget()
        self.tabGroup.addTab(self.tab_Table, self.language.Tabs.data)
        self.tableVLayout =  QVBoxLayout(self.tab_Table)
        # self.searchBar = QLineEdit(self.tab_Table)
        # self.searchBar.setMaximumWidth(500)
        # self.tableVLayout.addWidget(self.searchBar)
        self.importTable = TableImport(self.tab_Table)
        self.tableVLayout.addWidget(self.importTable)



        # Product Overview Tab
        self.tab_Products = QWidget()
        self.tabGroup.addTab(self.tab_Products, self.language.Tabs.products)

        # Product Detail Tab
        self.tab_Detail = QWidget()
        self.tabGroup.addTab(self.tab_Detail, self.language.Tabs.detail)
        self.tabGroup.setTabEnabled(2, False)


    
    def _createActions(self):
        # File Actions
        self.openAction = QAction(QIcon("icons:file-open.png"), "&"+self.language.Actions.openAction, self.MainWindow)
        # Table actions
        self.newAction  = QAction(QIcon("icons:add-row.png"), "&"+self.language.Actions.newAction, self.MainWindow)
        self.deleteAction = QAction(QIcon("icons:delete-row.png"), "&"+self.language.Actions.deleteAction, self.MainWindow)
        self.removeTableAction = QAction(QIcon("icons:remove-table.png"), "&"+self.language.Actions.removeTableAction, self.MainWindow)
        self.saveAction = QAction(QIcon("icons:table-save.png"), "&"+self.language.Actions.saveAction, self.MainWindow)
        self.saveAllAction = QAction(QIcon("icons:table-save-all.png"), "&"+self.language.Actions.saveAllAction, self.MainWindow)
        self.backAction = QAction(QIcon("icons:back.png"), "&"+self.language.Actions.backAction, self.MainWindow)
        self.nextAction = QAction(QIcon("icons:next.png"), "&"+self.language.Actions.nextAction, self.MainWindow)
        # Shopware Actions
        self.translateAction = QAction(QIcon("icons:translate.png"), "&"+self.language.Actions.translateAction, self.MainWindow)
        self.uploadAction = QAction(QIcon("icons:upload.png"), "&"+self.language.Actions.uploadAction, self.MainWindow)
        # Exit Action
        self.exitAction = QAction("&Exit", self.MainWindow)
        # Help Action
        self.helpAction = QAction(QIcon("icons:help.png"), "&"+self.language.Actions.helpAction, self.MainWindow)
        self.changeLanguageAction = QAction(QIcon("icons:change-language.png"), "&"+self.language.Actions.changeLanguageAction, self.MainWindow)
        #Shortcuts
        self.openAction.setShortcut("Ctrl+O")
        self.newAction.setShortcut("Ctrl+N")
        self.deleteAction.setShortcut(QKeySequence.StandardKey.Delete)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAllAction.setShortcut("Ctrl+Shift+S")
        self.uploadAction.setShortcut("Ctrl+U")
        # Hints
        self.openAction.setToolTip(self.language.Hints.openHint)
        self.newAction.setToolTip(self.language.Hints.newHint)
        self.deleteAction.setToolTip(self.language.Hints.deleteHint)
        self.removeTableAction.setToolTip(self.language.Hints.removeTableHint)
        self.newAction.setToolTip(self.language.Hints.nextHint)
        self.backAction.setToolTip(self.language.Hints.backHint)
        self.saveAction.setToolTip(self.language.Hints.saveHint)
        self.saveAllAction.setToolTip(self.language.Hints.saveAllHint)
        self.uploadAction.setToolTip(self.language.Hints.uploadHint)

    def _createMenuBar(self):
        menuBar = self.MainWindow.menuBar()
        # File Menu
        self.fileMenu = QMenu("&"+self.language.Menu.file, self.MainWindow)
        menuBar.addMenu(self.fileMenu)
        self.fileMenu.addActions([self.openAction, self.fileMenu.addSeparator(), self.exitAction])
        # Table Menu
        self.tableMenu = QMenu("&"+self.language.Menu.table, self.MainWindow)
        menuBar.addMenu(self.tableMenu)
        self.tableMenu.addActions([self.newAction, self.deleteAction, self.removeTableAction, self.saveAction, self.saveAllAction, self.backAction, self.nextAction, self.translateAction, self.uploadAction])
        # Help Menu
        self.helpMenu = QMenu("&"+self.language.Menu.help, self.MainWindow)
        menuBar.addMenu(self.helpMenu)
        self.helpMenu.addActions([self.helpAction, self.changeLanguageAction])
    
    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.MainWindow.addToolBar("File")
        fileToolBar.addAction(self.openAction)
        # Table toolbar
        self.tableToolBar = QToolBar("Table", self.MainWindow)
        self.MainWindow.addToolBar(self.tableToolBar)
        self.tableToolBar.addActions([self.newAction, self.deleteAction, self.removeTableAction, self.backAction])
        self.tableSpinBox = QSpinBox()
        self.tableSpinBox.setMaximum(0)
        self.tableSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.tableSpinBox.setToolTip(self.language.Hints.currentTableHint)
        self.tableToolBar.addWidget(self.tableSpinBox)
        self.tableToolBar.addActions([self.nextAction,self.saveAction, self.saveAllAction])
        # Shopware upload
        self.uploadToolBar = QToolBar("Upload", self.MainWindow)
        self.MainWindow.addToolBar(self.uploadToolBar)
        self.uploadToolBar.addAction(self.translateAction)
        self.translationLanguageComboBox = QComboBox() 
        self.translationLanguageComboBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.translationLanguageComboBox.addItems((lan.name for lan in TranslationLanguages))
        self.translationLanguageComboBox.setCurrentIndex(0)
        self.uploadToolBar.addWidget(self.translationLanguageComboBox)
        self.uploadToolBar.addAction(self.uploadAction)
    
    def _connectActions(self):
        # Connect File actions
        # File Actions
        self.openAction.triggered.connect(self.openFile)
        # Table actions
        self.newAction
        self.deleteAction
        self.removeTableAction
        self.saveAction
        self.saveAllAction
        self.backAction
        self.nextAction
        # Shopware Actions
        self.translateAction
        self.uploadAction
        # Exit Action
        self.exitAction
        # Help Action
        self.helpAction
        self.changeLanguageAction.triggered.connect(self.retranslateUi)
    
    def openFile(self):
        fname = QFileDialog.getOpenFileName(self.MainWindow, 'Open file', 'c:\\',"Data Files(*.pdf *.csv *.xls*)")[0]
        if not fname:
            return
        try:
            if fname.endswith(".pdf"):
                frames = tabula.read_pdf(fname, pages='all')
            elif fname.endswith('.csv'):
                frames = [pd.read_csv(fname)]
            elif fname.lower().endswith('.xlsx'):
                frames = [pd.read_excel(fname)]
            else:
                self.statusbar.showMessage(self.language.InvalidFile, 5000)

        except:
            self.statusbar.showMessage(self.language.fileError, 5000)
        else:
            if not frames:
                self.statusbar.showMessage(self.language.noFrames, 5000)
            else:
                frameLength = len(frames)
                self.statusbar.showMessage(self.language.framesFound+str(frameLength), 5000)
                self.tableCountLabel.setText(self.language.Tablecount+":"+str(frameLength))
                self.tableSpinBox.setMaximum(frameLength-1)
                self.selectedFrameIndex = 0
                self.frameList = list(map(PandasModel, frames))
                self.importTable.setModel(self.frameList[self.selectedFrameIndex])


    


    
    
    def retranslateUi(self):
        _translate = QCoreApplication.translate
        newLanguage, ok = QInputDialog.getItem(self.MainWindow, self.language.Actions.changeLanguageAction, self.language.Hints.changeLanguageHint, ["English", "German"])
        if newLanguage == "English":
            self.language = Language.English
        elif newLanguage == "German":
            self.language = Language.German
        # Retranslate MenuBar
        self.fileMenu.setTitle(self.language.Menu.file)
        self.tableMenu.setTitle(self.language.Menu.table)
        self.helpMenu.setTitle(self.language.Menu.help)

        # File Actions
        self.openAction.setText(self.language.Actions.openAction)
        # Table actions
        self.newAction.setText(self.language.Actions.newAction)
        self.deleteAction.setText(self.language.Actions.deleteAction)
        self.removeTableAction.setText(self.language.Actions.removeTableAction)
        self.backAction.setText(self.language.Actions.backAction)
        self.newAction.setText(self.language.Actions.nextAction)
        self.saveAction.setText(self.language.Actions.saveAction)
        self.saveAllAction.setText(self.language.Actions.saveAllAction)
        # Shopware Actions
        self.translateAction.setText(self.language.Actions.translateAction)
        self.uploadAction.setText(self.language.Actions.uploadAction)
        # Help Action
        self.helpAction.setText(self.language.Actions.helpAction)
        self.changeLanguageAction.setText(self.language.Actions.changeLanguageAction)
        # Hints
        self.openAction.setToolTip(self.language.Hints.openHint)
        self.newAction.setToolTip(self.language.Hints.newHint)
        self.deleteAction.setToolTip(self.language.Hints.deleteHint)
        self.removeTableAction.setToolTip(self.language.Hints.removeTableHint)
        self.backAction.setToolTip(self.language.Hints.backHint)
        self.tableSpinBox.setToolTip(self.language.Hints.currentTableHint)
        self.nextAction.setToolTip(self.language.Hints.nextHint)
        self.saveAction.setToolTip(self.language.Hints.saveHint)
        self.saveAllAction.setToolTip(self.language.Hints.saveAllHint)
        self.uploadAction.setToolTip(self.language.Hints.uploadHint)

















if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow(MainWindow, Language.German())
    ui.setupUi()
    MainWindow.showMaximized()
    sys.exit(app.exec())