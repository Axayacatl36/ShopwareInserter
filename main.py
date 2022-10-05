from cProfile import label
from decimal import Decimal
import string
import sys
import threading
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

class PercentageWorker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    percentageChanged = pyqtSignal(int)
    sendMessage = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percentage = 0

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        if self._percentage == value:
            return
        self._percentage = value
        self.percentageChanged.emit(self.percentage)
    
    def printMessage(self, message):
        self.sendMessage.emit(message)

    def start(self):
        self.started.emit()

    def finish(self):
        self.finished.emit()


class FakeWorker:
    def printMessage(self, message):
        pass

    def start(self):
        pass

    def finish(self):
        pass

    @property
    def percentage(self):
        return 0

    @percentage.setter
    def percentage(self, value):
        pass

class ProgressBar(QWidget):
    def __init__(self, parent=None, MainWindow: "Ui_MainWindow" =None):
        super().__init__(parent)
        self.progress = QProgressBar()
        self.progress.hide()
        self.mainWindow = MainWindow
    
    def start(self):
        self.progress.show()
    
    def finished(self):
        self.progress.hide()

    def launch(self, long_running_function, args=[]):
        worker = PercentageWorker()
        worker.sendMessage.connect(self.mainWindow.printMessage)
        worker.started.connect(self.start)
        worker.finished.connect(self.finished)
        worker.percentageChanged.connect(self.progress.setValue)
        threading.Thread(
            target=long_running_function,
            args=args,
            kwargs=dict(worker=worker),
            daemon=True,
        ).start()

class Product(QStandardItem):

    def __init__(self,
        productNumber: Union[int, str],
        productName: str = "",
        priceBrutto: Decimal = Decimal("0.00"),
        priceNetto: Decimal = Decimal("0.00"),
        manufacturer: string = "",
        category: list = [],
        font_size=6, color=QColor(0, 0, 0)):

        super().__init__()
        self.fnt = QFont('Open Sans', font_size)
        self.setFont(self.fnt)
        self.productName    = productName
        self.productNumber  = productNumber
        self.priceBrutto    = priceBrutto
        self.priceNetto     = priceNetto
        self._priceBruttoRaw = Decimal(0)
        self._priceNettoRaw  = Decimal(0)
        self.manufacturer   = manufacturer
        self.category       = category
        self.stock          = Decimal("0.00")
        self.minimumPurchase = Decimal("1.00")
        self.description    = None
        self._amount = Decimal(1)
        self.variants: list = []

        self.existsOnline = False
        self.productNameOnline  = None
        self.priceBruttoOnline  = None
        self.priceNettoOnline   = None
        self.manufacturerOnline = None
        self.categoryOnline     = []
        self.stockOnline        = None
        self.minimumPurchaseOnline = None
        self.descriptionOnline  = None

        self.imageUrl = None
        self.uploadFlag = False
        self.uploadedFlag = False
    
    @property
    def priceBruttoRaw(self):
        return self._priceBruttoRaw
    @priceBruttoRaw.setter
    def priceBruttoRaw(self, value: Decimal):
        self._priceBruttoRaw = value
        if self._amount:
            self.priceBrutto = self._priceBruttoRaw/self._amount
    
    @property
    def priceNettoRaw(self):
        return self._priceNettoRaw
    @priceNettoRaw.setter
    def priceNettoRaw(self, value: Decimal):
        self._priceNettoRaw = value
        if self._amount:
            self.priceNetto = self._priceNettoRaw/self._amount
    
    @property
    def amount(self):
        return self._amount
    @amount.setter
    def amount(self, value: Decimal):
        self._amount = value
        if self.priceNettoRaw:
            self.priceNetto = self.priceNettoRaw/self.amount
        if self.priceBruttoRaw:
            self.priceBrutto = self.priceBruttoRaw/self.amount

    def productPayload(self, ADMIN_API: Shopware6API) -> dict:
        # id und number sind schon gesetzt
        payload = dict()
        tax_name = "Standard rate"
        currency_iso_code = "EUR"
        linked = True

        if not self.priceNetto:
            tax_rate = ADMIN_API.product.tax.get_tax_rate_by_name(tax_name=tax_name)
            self.priceNetto = self.priceBrutto / (1 + tax_rate / 100)
        if not self.priceBrutto:
            tax_rate = ADMIN_API.product.tax.get_tax_rate_by_name(tax_name=tax_name)
            self.priceBrutto = self.priceNetto * (1 + tax_rate / 100)
        currency_id = ADMIN_API.product.currency.get_currency_id_by_iso_code(currency_iso_code=currency_iso_code)
        # new_product_id = ADMIN_API.product.calc_new_product_id(product_number=self.productNumber)
        manufacturer_id = ADMIN_API.product.calc_new_product_id(product_number=self.manufacturer)
        tax_id =  ADMIN_API.tax.get_tax_id_by_name(tax_name=tax_name)
        payload["name"] = self.productName
        if self.stock:
            payload["stock"] = int(self.stock)
        payload["taxId"] = tax_id
        payload["price"] = [{"currencyId": currency_id, "gross": str(self.priceBrutto), "net": str(self.priceNetto), "linked": linked}]
        if self.manufacturer:
            payload["manufacturer"] = {"id": manufacturer_id, "name": self.manufacturer }
        payload["minPurchase"] = int(self.minimumPurchase)
        payload["description"] = self.description
        payload["active"] = True
        return payload

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
    
    def newColumn(self):
        if "changeMe" not in self.getHeaderKeys():
            self._data=self._data.assign(changeMe="")
            self.layoutChanged.emit()

    def removeColumn(self):
        if list(self.getHeaderKeys()):
            self._data.drop(columns = [list(self.getHeaderKeys()).pop()], inplace=True)
            self.layoutChanged.emit()

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

class ProductTableModel(QAbstractTableModel):
    def __init__(self, MainWindow: "Ui_MainWindow"):
        super().__init__()
        self._data: typing.List["Product"] = []
        self.MainWindow = MainWindow

    def rowCount(self, index=0):
        return len(self._data)

    def columnCount(self, parnet=None):
        return 10 # image, number, name, pricen, priceb, amount, stock, minimum purchase,  manufacturer, description | list variants/categorys

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                # value = self._data.iloc[index.row(), index.column()]
                product = self._data[index.row()]
                if index.column() == 0: #productimagewidget
                    return None
                elif index.column() == 1:   # number
                    return str(product.productNumber)
                elif index.column() == 2:   # name
                    return str(product.productName)
                elif index.column() == 3:   # priceNetto
                    return str(product.priceNetto)
                elif index.column() == 4:   # priceBrutto
                    return str(product.priceBrutto)
                elif index.column() == 5:   # amount
                    return int(product.amount)
                elif index.column() == 6:   # stock
                    return int(product.stock)
                elif index.column() == 7:   # min purchase
                    return int(product.minimumPurchase)

                elif index.column() == 8:   # manufacturer
                    return str(product.manufacturer)
                elif index.column() == 9:   # description
                    return str(product.description)
        return None

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            product = self._data[index.row()]
            try:
                if index.column() == 0: #productimagewidget
                    ...
                elif index.column() == 1:   # number
                    product.productNumber = str(value)
                elif index.column() == 2:   # name
                    product.productName = str(value)
                elif index.column() == 3:   # priceNetto
                    if Decimal(value) >= 0:
                        product.priceNetto = Decimal(value)
                elif index.column() == 4:   # priceBrutto
                    if Decimal(value) >= 0:
                        product.priceBrutto = Decimal(value)
                elif index.column() == 5:   # amount
                    product.amount = Decimal(value)
                    self.layoutChanged.emit()
                elif index.column() == 6:   # stock
                    product.stock = value
                elif index.column() == 7:   # min purchase
                    product.minimumPurchase = value
                elif index.column() == 8:   # manufacturer
                    product.manufacturer = str(value)
                elif index.column() == 9:   # description
                    product.description = str(value)
            except:
                return False
            else:
                return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.MainWindow.language.ProductTable(col).name
    
    def setHeaderData(self, col,orientation, value, role):
        if role == Qt.ItemDataRole.EditRole:
            return True
        return False
    
    def append(self, product: "Product"):
        self._data.append(product)


    def columns(self):
        return (lan.name for lan in self.MainWindow.language.ProductTable)

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
        self._data.insert(row_target,self._data.pop(row_source))
        self.endMoveRows()
    
    def removeRow(self, row):
        if row >= len(self._data):
            self._data.pop(row)
            self.layoutChanged.emit()
        else:
            print(f"no row {row} to delete")
    
    def removeRows(self, row: int, count: int, parent: QModelIndex = None):
        del self._data[row: row + count]
        self.layoutChanged.emit()
    
    def newRow(self):
        for product in self._data:
            if product.productNumber == "0":
                return
        self._data.append(Product("0"))
        self.layoutChanged.emit()
    
    def getProducts(self):
        return self._data

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
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setDragEnabled(True)
        self.setStyle(self.DropmarkerStyle())
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setModel(ProductTableModel(MainWindow=self.MainWindow))
        self.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
    
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
        self.ADMIN_API: Shopware6API = Shopware6API(config=ConfShopware6ApiBase())
    
    def setupUi(self):
        self.MainWindow.setWindowTitle(self.language.WindowTitle)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()
        # Create Status Bar
        self.statusbar = self.MainWindow.statusBar()
        self.statusbar.setFont(QFont('Times', 11))
        self.progressBar = ProgressBar(MainWindow=self)
        self.progressBar.progress.setMaximumWidth(300)
        self.statusbar.addPermanentWidget(self.progressBar.progress)
        self.tableCountLabel = QLabel(f"{self.language.Tablecount}: 0")
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
        self.removeTableAction  = QAction(QIcon("icons:remove-table.png"), "&"+self.language.Actions.removeTableAction, self.MainWindow)
        self.newColumnAction    = QAction(QIcon("icons:new-column.png"), "&"+self.language.Actions.newColumnAction, self.MainWindow)
        self.removeColumnAction = QAction(QIcon("icons:remove-column.png"), "&"+self.language.Actions.removeColumnAction, self.MainWindow)
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
        self.newColumnAction.setToolTip(self.language.Hints.newColumnHint)
        self.removeColumnAction.setToolTip(self.language.Hints.removeColumnHint)
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
        self.tableMenu.addActions([self.newAction, self.deleteAction, self.newColumnAction, self.removeColumnAction, self.removeTableAction, self.saveAction, self.saveAllAction, self.backAction, self.nextAction, self.continuosAction, self.translateAction, self.uploadAction])
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
        self.tableToolBar.addActions([self.newAction, self.deleteAction, self.newColumnAction, self.removeColumnAction, self.removeTableAction, self.backAction])
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
        self.newColumnAction.triggered.connect(self.newColumn)
        self.removeColumnAction.triggered.connect(self.removeColumn)
        self.removeTableAction.triggered.connect(self.deleteTable)
        self.backAction.triggered.connect(self.previous_table)
        self.nextAction.triggered.connect(self.next_table)
        self.continuosAction.triggered.connect(self.togglecontinuosMode)
        self.saveAction.triggered.connect(self.importPandasTable)
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
                frames = [pd.read_excel(fname, dtype="string")]
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
                self.frameList: typing.List[ImportTableModel] = list(map(ImportTableModel, frames))
                self.importTable.setModel(self.frameList[self.selectedFrameIndex])
                self.importTable.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
    
    def newRow(self):
        self.importTable.model().newRow() if self.importTable.model() else None
    
    def removeRow(self):
        self.importTable.removeSelectedRows()
    
    def newColumn(self):
        if self.importTable.model():
            self.importTable.model().newColumn()
    
    def removeColumn(self):
        if self.importTable.model():
            self.importTable.model().removeColumn()
        
    
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
    
    def importPandasTable(self):
        if self.importTable.model():
            self.progressBar.launch(self.importProducts)
    
    def importProducts(self, worker, allTables: bool = False):
        if worker is None:
            worker = FakeWorker()
        worker.percentage = 0
        steps = 0
        if allTables:
            for table in self.frameList:
                steps += table.rowCount(0)
        else:
            steps = self.frameList[self.selectedFrameIndex].rowCount()
        self.progressBar.progress.setMaximum(steps)
        worker.start()
        if allTables:
            tableSelection = self.frameList
        else:
            tableSelection = [self.frameList[self.selectedFrameIndex]]
        
        productNumberLang = self.language.ImportSelection(1).name
        
        for table  in tableSelection:
            if table._data.empty:
                continue
            for indTable, row in table._data.iterrows():
                # productnumber not in keys
                if productNumberLang not in row.keys(): 
                    worker.printMessage(self.language.ImportSelectionError.KeyErrorP1+productNumberLang+self.language.ImportSelectionError.KeyErrorP2+str(self.frameList.index(table)))
                    return
                # valid value for productnumber
                if row[productNumberLang] is None or row[productNumberLang] == "":
                    worker.printMessage(productNumberLang + self.language.ImportSelectionError.ValueError1 + str(self.frameList.index(table)) + productNumberLang + self.language.ImportSelectionError.ValueError2 + str(indTable))
                    return
                # create new product or edit existing
                product = None
                # search existing products for product number
                for prod in self.productTable.model().getProducts():
                    if prod.productNumber == row[productNumberLang]:
                        product = prod
                        break
                    self.searchChildProducts(prod.variants, row[productNumberLang])
                # when this productnumber does not exist
                if product == None:
                    product = Product(row[productNumberLang])
                    # add product to list of products
                    self.productTable.model().append(product)
                    if self.ADMIN_API.product.is_product_number_existing(product.productNumber):
                        product.existsOnline = True
                        # get online product data
                        product_online = self.ADMIN_API.product._admin_client.request_get(f"product/{self.ADMIN_API.product.get_product_id_by_product_number(product.productNumber)}", dict())["data"]
                        product.productNameOnline   = product_online["name"]
                        product.priceBruttoOnline   = Decimal(str(product_online["price"][0]["gross"]))
                        product.priceNettoOnline    = Decimal(str(product_online["price"][0]["net"]))
                        product.manufacturerOnline  = str(product_online["manufacturer"])
                        product.categoryOnline      =  product_online["categoryIds"]
                        product.minimumPurchaseOnline = Decimal(str(product_online["minPurchase"]))
                        product.descriptionOnline   = str(product_online["description"])
                        product.stockOnline         = Decimal(str(product_online["availableStock"]))
                
                ## fill product with data
                # productname
                if self.language.ImportSelection(0).name in row.keys():
                    product.productName = row[self.language.ImportSelection(0).name]
                # amount
                if self.language.ImportSelection(4).name in row.keys():
                    try:
                        product.amount = Decimal(str(row[self.language.ImportSelection(4).name]))
                    except:
                        worker.printMessage(self.language.ImportSelectionError.ConvertError1+self.language.ImportSelection(4).name+self.language.ImportSelectionError.ConvertError2+product.productName)
                # price netto
                if self.language.ImportSelection(2).name in row.keys():
                    try:
                        product.priceNettoRaw = Decimal(str(row[self.language.ImportSelection(2).name]))
                    except:
                        worker.printMessage(self.language.ImportSelectionError.ConvertError1+self.language.ImportSelection(2).name+self.language.ImportSelectionError.ConvertError2+product.productName)
                # price brutto
                if self.language.ImportSelection(3).name in row.keys():
                    try:
                        product.priceBruttoRaw = Decimal(str(row[self.language.ImportSelection(3).name]))
                    except:
                        worker.printMessage(self.language.ImportSelectionError.ConvertError1+self.language.ImportSelection(3).name+self.language.ImportSelectionError.ConvertError2+product.productName)
                # stock
                if self.language.ImportSelection(5).name in row.keys():
                    try:
                        product.stock = Decimal(str(row[self.language.ImportSelection(5).name]))
                    except:
                        worker.printMessage(self.language.ImportSelectionError.ConvertError1+self.language.ImportSelection(5).name+self.language.ImportSelectionError.ConvertError2+product.productName)
                elif product.stockOnline:
                    product.stock = product.stockOnline
                #minimum purchase
                if self.language.ImportSelection(7).name in row.keys():
                    try:
                        product.minimumPurchase = Decimal(str(row[self.language.ImportSelection(7).name]))
                    except:
                        worker.printMessage(self.language.ImportSelectionError.ConvertError1+self.language.ImportSelection(7).name+self.language.ImportSelectionError.ConvertError2+product.productName)
                #description
                if self.language.ImportSelection(6).name in row.keys():
                    product.description = row[self.language.ImportSelection(6).name]
                worker.percentage += 1
        worker.finish()
        self.productTable.model().layoutChanged.emit()
    
    def searchChildProducts(self, children: typing.List["Product"], productNumber):
        for child in children:
            if child.productNumber == productNumber:
                return child
        return None

    def printMessage(self, message:str, duration = 10000):
        self.statusbar.showMessage(message, duration)



        


    
    
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