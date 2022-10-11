import enum
from pydoc import Helper

from numpy import absolute

class Language():
    class English():
        WindowTitle = "ShopwareProductInserter"
        Tablecount  = "Tablecount"
        InvalidFile = "Invalid File"
        fileError   = "Error while reading file"
        noFrames    = "Couldnt find any tables"
        framesFound = "Found Tables:"
        class Actions():
            openAction      = "Open..."
            newAction       = "Add Row"
            deleteAction    = "Delete Row"
            removeTableAction = "Tabelle entfernen"
            newColumnAction = "Add new column"
            removeColumnAction = "Remove last column"
            saveAction      = "Save Table"
            saveAllAction   = "Save all Tables"
            backAction      = "Previous Table"
            nextAction      = "Next Table"
            translateAction = "Translate"
            uploadAction    = "Upload"
            helpAction = "Help"
            changeLanguageAction = "Change Language"
            continuosModeAction   = "Activate continuos renameing"
            continuosModeActionOff   = "Deactivate continuos renameing"
        
        class Hints():
            openHint    = "Open a excel, pdf or csv file"
            newHint     = "Add new row to current view" 
            deleteHint  = "Delete a row from current view"
            removeTableHint = "Remove table from list"
            newColumnHint = "Add new column"
            removeColumnHint = "Remove last column"
            saveHint    = "Save products to importlist"
            saveAllHint = "Save all products to importlist"
            backHint    = "Go back to previous table"
            nextHint    = "Go to next table"
            translateHint = "Translate selected Products to selected Language"
            uploadHint  = "Uploads marked products to shopware"
            helpHint    = "Help Content"
            changeLanguageHint = "Choose new language"
            continuosModeHint = "Rename column title in following tables"
            continuosModeHintOff = "Rename column title in active table"
            currentTableHint = "Current table"
        
        class Label():
            variantsLabel = "Variants"
            categoryLabel = "Category"
        
        class ProductTable(enum.Enum):
            Image   = 0
            Number  = 1
            Name    = 2
            PriceNetto = 3
            PriceBrutto = 4
            Amount = 5
            InStock = 6
            MinPurchase   = 7
            Manufacturer = 8
            Description = 9
        
        class Menu():
            file    = "File"
            table   = "Table"
            help  = "Help"
        
        class Tabs():
            data    = "Open Catalogue"
            products = "Import List"
            detail  ="Details"
        
        class ImportSelection(enum.Enum):
            Productname     = 0
            Productnumber   = 1
            PriceNetto      = 2
            PriceBrutto     = 3
            Amount          = 4
            Stock           = 5
            Description     = 6
            MinimumPurchase = 7
            Manufacturer    = 8
            Ignore          = 9
        
        class ImportSelectionError():
            KeyErrorP1 = "Columntitle'" 
            KeyErrorP2 = "' is missing in table: "
        
            
        
    class German():
        WindowTitle = "ShopwareProduktInserter"
        Tablecount  = "Tabellenanzahl"
        InvalidFile = "Ungültige Datei"
        fileError   = "Es ist ein Fehler beim lesen der Datei aufgetreten"
        noFrames    = "Es konnten keine Tabellen gefunden werden"
        framesFound = "Gefundene Tabellen:"

        class Actions():
            openAction      = "Öffnen..."
            newAction       = "Neue Reihe"
            deleteAction    = "Reihe löschen"
            removeTableAction = "Tabelle entfernen"
            newColumnAction = "Neue Spalte hinzufügen"
            removeColumnAction = "Letzte Spalte entfernen"
            saveAction      = "Tabelle speichern"
            saveAllAction   = "Alle Tabellen speichern"
            backAction      = "Vorherige Tabelle"
            nextAction      = "Nächste Tabelle"
            translateAction = "Übersetzen"
            uploadAction    = "Hochladen"
            helpAction      = "Hilfe"
            changeLanguageAction = "Sprache ändern"
            continuosModeAction   = "Kontinuierliche Umbenennung aktiviert"
            continuosModeActionOff   = "Kontinuierliche Umbenennung deaktiviert"
        
        class Hints():
            openHint    = "Öffne eine Excel, PDF oder CSV Datei"
            newHint     = "Neue Reihe der aktuellen Ansicht hinzufügen"
            deleteHint  = "Reihe aus aktueller Ansicht entfernen"
            removeTableHint = "Entferne Tabelle aus der aktuellen liste"
            newColumnHint = "Neue Spalte hinzufügen"
            removeColumnHint = "Letzte Spalte entfernen"
            removeColumnHint = "Letzte Spalte entfernen"
            saveHint    = "Tabelle in Importliste speichern"
            saveAllHint = "Alle Tabellen in Importliste speichern"
            backHint    = "Gehe zurück zur vorherigen Tabelle"
            nextHint    = "Gehe zur nächsten Tabelle"
            translateHint = "Übersetze alle ausgewählten Produkte in die gewünschte Sprache"
            uploadHint  = "Markierte Artikel zu Shopware hochladen"
            helpHint    = "Hilfe Inhalt"
            changeLanguageHint = "Wähle die neue Sprache"
            currentTableHint = "Aktuelle Tabelle"
            continuosModeHint = "Spaltentitel in nachfolgenden Tabellen umbenennen"
            continuosModeHintOff = "Spaltentitel in aktiver Tabelle umbenennen"
        
        class Label():
            variantsLabel = "Varianten"
            categoryLabel = "Kategorien"
        
        class ProductTable():
            image   = "Bild"
            number  = "Nummer"
            name    = "Name"
            priceNetto = "PreisNetto"
            priceBrutto = "PreisBrutto"
            amount = "Anzahl"
            stock = "Im Lager"
            minPurchase   = "Min.Kauf"
            manufacturer = "Hersteller"
            description = "Beschreibung"
        
        class ProductTable(enum.Enum):
            Bild        = 0
            Nummer      = 1
            Name        = 2
            PreisNetto  = 3
            PreisBrutto = 4
            Anzahl      = 5
            AufLager    = 6
            MinKaufen   = 7
            Hersteller  = 8
            Beschreibung = 9
        
        class Menu():
            file    = "Datei"
            table   = "Tabelle"
            help    = "Hilfe"

        
        class Tabs():
            data    = "Katalog öffnen"
            products = "Importliste"
            detail  ="Details"
        
        class ImportSelection(enum.Enum):
            Produktname     = 0
            Produktnummer   = 1
            PreisNetto      = 2
            PreisBrutto     = 3
            Anzahl          = 4
            Lagerbestand    = 5
            Beschreibung    = 6
            Mindestabnahme  = 7
            Hersteller      = 8
            Ignorieren      = 9
        
        class ImportSelectionError():
            KeyErrorP1 = "Spaltentitel '" 
            KeyErrorP2 = "' fehlt in Tabelle: "
            ValueError1 = " has no value and is being skipped, Table: "
            ValueError2 = " , row: "
            ConvertError1 = "Could not convert"
            ConvertError2 = "for product: "

class TranslationLanguages(enum.Enum):
    English = "en"
    German  = "de"
    French  = "fr"
    Dutch   = "nl"
    Chinese = "zh-CN"
    Russian = "ru"
    Spanish = "es"
