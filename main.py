from cProfile import label
import sys
import tabula
import pandas as pd
import typing

from PyQt6.QtCore  import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from lib_shopware6_api import *
from my_shop_config import ConfShopware6ApiBase
from googletrans import Translator

from language import *

class EditableHeaderView(QHeaderView):
 
    def __init__(self,orientation, Mainwindow: QMainWindow, parent=None):
        super(EditableHeaderView, self).__init__(orientation,parent)
        # This block sets up the edit line by making setting the parent
        # to the Headers Viewport.
        self.MainWindow = Mainwindow
        self.combo = QComboBox(parent=self.viewport())  #Create
        # self.line.setAlignment(Qt.AlignmentFlag.AlignTop) # Set the Alignment
        self.combo.setHidden(True) # Hide it till its needed
        # This is needed because I am having a werid issue that I believe has
        # to do with it losing focus after editing is done.
        self.combo.blockSignals(True)
        self.sectionedit = 0
        # Connects to double click
        self.sectionDoubleClicked.connect(self.editHeader)
        self.combo.currentTextChanged.connect(self.TextChanged)
    
    def editHeader(self,section):
        # This block sets up the geometry for the line edit
        edit_geometry = self.combo.geometry()
        edit_geometry.setWidth(self.sectionSize(section))
        edit_geometry.moveLeft(self.sectionViewportPosition(section))
        self.combo.setGeometry(edit_geometry)

        sectionMenu = []
        # create menu options
        for lan in self.MainWindow.language.ImportSelection:
            if lan.name not in self.model().columns():
                sectionMenu.append(lan.name)
        if self.model().headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) in sectionMenu:
            self.combo.clear()
            self.combo.addItems(sectionMenu)
            self.combo.setCurrentIndex(sectionMenu.index(self.model().headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)))
        else:
            self.combo.clear()
            sectionMenu.insert(0, self.model().headerData(section, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole))
            self.combo.addItems(sectionMenu)
            self.combo.setCurrentIndex(0)
        self.combo.setHidden(False) # Make it visiable
        self.combo.blockSignals(False) # Let it send signals
        self.combo.setFocus()
        self.sectionedit = section
 
    def TextChanged(self):
        # This block signals needs to happen first otherwise I have lose focus
        # problems again when there are no rows
        self.combo.blockSignals(True)
        self.combo.setHidden(True)
        oldName = self.model().headerData(self.sectionedit, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        newName = str(self.combo.currentText())
        if newName:
            self.model().setHeaderData(self.sectionedit, Qt.Orientation.Horizontal, str(self.combo.currentText()),Qt.ItemDataRole.EditRole)
            if self.MainWindow.continuosMode:
                for table in self.MainWindow.frameList[self.MainWindow.selectedFrameIndex:]:
                    if oldName in table.getHeaderKeys():
                        table.setHeaderData(list(table.getHeaderKeys()).index(oldName), Qt.Orientation.Horizontal, newName, Qt.ItemDataRole.EditRole)

        self.setCurrentIndex(QModelIndex())
        #apply change to all table columns with same name
    
class ProductTableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, index=0):
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
    
    def setHeaderData(self, col,orientation, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data.rename(columns={self._data.columns[col]:value}, inplace=True)
            return True
        return False

    def columns(self):
        return self._data.columns

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        if index.row() < self.rowCount():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def supportedDropActions(self) -> bool:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction
    
    def relocateRow(self, row_source, row_target) -> None:
        row_a, row_b = max(row_source, row_target), min(row_source, row_target)
        self.beginMoveRows(QModelIndex(), row_a, row_a, QModelIndex(), row_b)
        copyRow = self._data.iloc[row_source]
        self._data.drop(index=row_source, inplace=True)
        self._data.loc[row_target+0.5] = copyRow
        self._data.sort_index(inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.endMoveRows()
    
    def removeRow(self, row, reset_index=True):
        if row in self._data.index:
            self._data.drop(index=row, inplace=True)
            if reset_index:
                self._data.reset_index(drop=True, inplace=True)
            # print(f"removed row {row}")
        else:
            print(f"no row {row}")
            print(f"index is: {self._data.index}")
    
    def removeRowsList(self, rows: typing.List[QModelIndex]):
        for index in sorted(rows):
            self.removeRow(index.row(), False)
        self._data.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()
    
    def newRow(self):
        if self.rowCount():
            self._data.loc[self._data.iloc[-1].name + 1,:] = ""
        else:
            self._data.loc[0] = ""
        self.layoutChanged.emit()


class ImportTableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, index=0):
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
    
    def setHeaderData(self, col,orientation, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data.rename(columns={self._data.columns[col]:value}, inplace=True)
            return True
        return False

    def columns(self):
        return self._data.columns

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        if index.row() < self.rowCount():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def supportedDropActions(self) -> bool:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction
    
    def relocateRow(self, row_source, row_target) -> None:
        row_a, row_b = max(row_source, row_target), min(row_source, row_target)
        self.beginMoveRows(QModelIndex(), row_a, row_a, QModelIndex(), row_b)
        copyRow = self._data.iloc[row_source]
        self._data.drop(index=row_source, inplace=True)
        self._data.loc[row_target+0.5] = copyRow
        self._data.sort_index(inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.endMoveRows()
    
    def removeRow(self, row, reset_index=True):
        if row in self._data.index:
            self._data.drop(index=row, inplace=True)
            if reset_index:
                self._data.reset_index(drop=True, inplace=True)
            # print(f"removed row {row}")
        else:
            print(f"no row {row}")
            print(f"index is: {self._data.index}")
    
    def removeRowsList(self, rows: typing.List[QModelIndex]):
        for index in sorted(rows):
            self.removeRow(index.row(), False)
        self._data.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()
    
    def newRow(self):
        if self.rowCount():
            self._data.loc[self._data.iloc[-1].name + 1,:] = ""
        else:
            self._data.loc[0] = ""
        self.layoutChanged.emit()
    
    def getHeaderKeys(self):
        return self._data.keys()


class TableImport(QTableView):
    class DropmarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            """Draw a line across the entire row rather than just the column we're hovering over."""
            if element == self.PrimitiveElement.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)

    def __init__(self, MainWindow, parent = None):
        QTableView.__init__(self, parent)
        self.MainWindow = MainWindow
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setDragEnabled(True)
        self.setStyle(self.DropmarkerStyle())
        self.setHorizontalHeader(EditableHeaderView(orientation=Qt.Orientation.Horizontal, Mainwindow=self.MainWindow))
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
    
    def contextMenuEvent(self, event):
        menu = QMenu()
        delRow = menu.addAction("Delete selected Rows")
        delRow.triggered.connect(self.removeSelectedRows)
        menu.exec(self.mapToGlobal(event.pos()))
    
    def removeSelectedRows(self):
        self.model().removeRowsList(self.selectionModel().selectedRows()) if self.model() else None
    
    def dropEvent(self, event):
        if (event.source() is not self or
            (event.dropAction() != Qt.DropAction.CopyAction and
             self.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove)):
            super().dropEvent(event)

        selection = self.selectedIndexes()
        from_index = selection[0].row() if selection else -1
        to_index = self.indexAt(event.position().toPoint()).row()
        if (0 <= from_index < self.model().rowCount() and
            0 <= to_index < self.model().rowCount() and
            from_index != to_index):
            self.model().relocateRow(from_index, to_index)
            event.accept()
        super().dropEvent(event)
        self.setCurrentIndex(self.model().index(to_index+1, 0))

class TableProducts(QTableView):
    class DropmarkerStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            """Draw a line across the entire row rather than just the column we're hovering over."""
            if element == self.PrimitiveElement.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)

    def __init__(self, MainWindow, parent = None):
        QTableView.__init__(self, parent)
        self.MainWindow = MainWindow
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setDragEnabled(True)
        self.setStyle(self.DropmarkerStyle())
        self.setHorizontalHeader(EditableHeaderView(orientation=Qt.Orientation.Horizontal, Mainwindow=self.MainWindow))
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
    
    def contextMenuEvent(self, event):
        menu = QMenu()
        delRow = menu.addAction("Delete selected Rows")
        delRow.triggered.connect(self.removeSelectedRows)
        menu.exec(self.mapToGlobal(event.pos()))
    
    def removeSelectedRows(self):
        self.model().removeRowsList(self.selectionModel().selectedRows()) if self.model() else None
    
    def dropEvent(self, event):
        if (event.source() is not self or
            (event.dropAction() != Qt.DropAction.CopyAction and
             self.dragDropMode() != QAbstractItemView.DragDropMode.InternalMove)):
            super().dropEvent(event)

        selection = self.selectedIndexes()
        from_index = selection[0].row() if selection else -1
        to_index = self.indexAt(event.position().toPoint()).row()
        if (0 <= from_index < self.model().rowCount() and
            0 <= to_index < self.model().rowCount() and
            from_index != to_index):
            self.model().relocateRow(from_index, to_index)
            event.accept()
        super().dropEvent(event)
        self.setCurrentIndex(self.model().index(to_index+1, 0))


class Ui_MainWindow(object):
    def __init__(self, MainWindow: QMainWindow, language: Language = Language.English):
        QDir.addSearchPath('icons', os.path.dirname(os.path.realpath(__file__))+r"\resources")
        self.language = Language.German
        self.MainWindow = MainWindow
        self.selectedFrameIndex = 0
        self.frameList = []
        self.continuosMode = False
    
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
        self.importTable = TableImport(self, self.tab_Table)
        self.tableVLayout.addWidget(self.importTable)

        # Product Overview Tab
        self.tab_Products = QWidget()
        self.tabGroup.addTab(self.tab_Products, self.language.Tabs.products)
        self.productLayout = QVBoxLayout(self.tab_Products)
        self.searchBar = QLineEdit(self.tab_Table)
        self.searchBar.setMaximumWidth(500)
        self.productLayout.addWidget(self.searchBar)
        self.productItemsLayout = QHBoxLayout()
        self.productLayout.addLayout(self.productItemsLayout)
        self.productTable = TableProducts(self, self.tab_Products)
        self.productItemsLayout.addWidget(self.productTable)
        self.productListLayout = QVBoxLayout()
        self.productItemsLayout.addLayout(self.productListLayout)
        self.variantLabel = QLabel(self.language.Label.variantsLabel)
        self.variantsList = QListWidget()
        self.variantsList.setMaximumWidth(300)
        self.categoryLabel = QLabel(self.language.Label.categoryLabel)
        self.categoryList = QListWidget()
        self.categoryList.setMaximumWidth(300)
        self.productListLayout.addWidget(self.variantLabel)
        self.productListLayout.addWidget(self.variantsList)
        self.productListLayout.addWidget(self.categoryLabel)
        self.productListLayout.addWidget(self.categoryList)
        



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
        self.continuosAction = QAction(QIcon("icons:continuos-mode-dark.png"), "&"+self.language.Actions.continuosModeAction, self.MainWindow)
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
        self.newAction.setToolTip(self.language.Hints.newHint)
        self.backAction.setToolTip(self.language.Hints.backHint)
        self.nextAction.setToolTip(self.language.Hints.nextHint)
        self.continuosAction.setToolTip(self.language.Hints.continuosModeHintOff)
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
        self.tableMenu.addActions([self.newAction, self.deleteAction, self.removeTableAction, self.saveAction, self.saveAllAction, self.backAction, self.nextAction, self.continuosAction, self.translateAction, self.uploadAction])
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
        self.tableSpinBox.valueChanged.connect(self.spinBoxValueChanged)
        self.tableToolBar.addWidget(self.tableSpinBox)
        self.tableToolBar.addActions([self.nextAction,self.saveAction, self.saveAllAction, self.continuosAction])
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
        self.newAction.triggered.connect(self.newRow)
        self.deleteAction.triggered.connect(self.removeRow)
        self.removeTableAction.triggered.connect(self.deleteTable)
        self.backAction.triggered.connect(self.previous_table)
        self.nextAction.triggered.connect(self.next_table)
        self.continuosAction.triggered.connect(self.togglecontinuosMode)
        self.saveAction
        self.saveAllAction
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
                self.frameList = list(map(ImportTableModel, frames))
                self.importTable.setModel(self.frameList[self.selectedFrameIndex])
    
    def newRow(self):
        self.importTable.model().newRow() if self.importTable.model() else None
    
    def removeRow(self):
        self.importTable.removeSelectedRows()
    
    def deleteTable(self):
        if self.frameList:
            self.frameList.pop(self.selectedFrameIndex)
            if self.selectedFrameIndex < len(self.frameList): # set next table
                self.importTable.setModel(self.frameList[self.selectedFrameIndex])
            elif len(self.frameList) > 0:   # set previous table
                self.importTable.setModel(self.frameList[self.selectedFrameIndex -1])
                self.selectedFrameIndex += -1
                self.tableSpinBox.setValue(self.selectedFrameIndex)
            else:   #no model exists => no table
                self.importTable.setModel(None)
            self.tableCountLabel.setText(f"{self.language.Tablecount}: {len(self.frameList)}")
            self.tableSpinBox.setMaximum(len(self.frameList)-1) if len(self.frameList) else self.tableSpinBox.setMaximum(0)
    
    def next_table(self):
        if self.selectedFrameIndex +1 < len(self.frameList):
            self.selectedFrameIndex +=1
            self.importTable.setModel(self.frameList[self.selectedFrameIndex])
            self.tableSpinBox.setValue(self.selectedFrameIndex)
    
    def spinBoxValueChanged(self):
        self.selectedFrameIndex = self.tableSpinBox.value()
        self.importTable.setModel(self.frameList[self.selectedFrameIndex])
    
    def previous_table(self):
        if self.selectedFrameIndex -1 >= 0:
            self.selectedFrameIndex-=1
            self.importTable.setModel(self.frameList[self.selectedFrameIndex])
            self.tableSpinBox.setValue(self.selectedFrameIndex)
    
    def togglecontinuosMode(self):
        if self.continuosMode:
            self.continuosMode = False
            self.continuosAction.setIcon(QIcon("icons:continuos-mode-dark.png"))
            self.continuosAction.setText(self.language.Actions.continuosModeActionOff)
            self.continuosAction.setToolTip(self.language.Hints.continuosModeHintOff)
        else:
            self.continuosMode = True
            self.continuosAction.setIcon(QIcon("icons:continuos-mode.png"))
            self.continuosAction.setText(self.language.Actions.continuosModeAction)
            self.continuosAction.setToolTip(self.language.Hints.continuosModeHint)


    
    
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
        self.changeLanguageAction.setText(self.language.Actions.continuosModeAction)
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
        self.continuosAction.setToolTip(self.language.Hints.continuosModeHint)
        self.uploadAction.setToolTip(self.language.Hints.uploadHint)

















if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow(MainWindow, Language.German())
    ui.setupUi()
    MainWindow.showMaximized()
    sys.exit(app.exec())