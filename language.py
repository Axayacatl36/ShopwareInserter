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
            Ignore          = 8
            
        
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
            Ignorieren      = 8

class TranslationLanguages(enum.Enum):
    English = "en"
    German  = "de"
    French  = "fr"
    Dutch   = "nl"
    Chinese = "zh-CN"
    Russian = "ru"
    Spanish = "es"
