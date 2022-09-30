import enum
from pydoc import Helper

from numpy import absolute

class Language():
    class English():
        WindowTitle = "ShopwareProductInserter"
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
        
        class Hints():
            openHint    = "Open a excel, pdf or csv file"
            newHint     = "Add new row to current view" 
            deleteHint  = "Delete a row from current view"
            removeTableHint = "Remove table from list"
            saveHint    = "Save all products of current table"
            saveAllHint = "Save all products of all current tables"
            backHint    = "Go back to previous table"
            nextHint    = "Go to next table"
            translateHint = "Translate selected Products to selected Language"
            uploadHint  = "Uploads all saved and flagged products to Shopware"
            helpHint    = "Help Content"
            changeLanguageHint = "Choose new language"
            currentTableHint = "Current table"
        
        class Menu():
            file    = "File"
            table   = "Table"
            help  = "Help"
            
        
    class German():
        WindowTitle = "ShopwareProduktInserter"
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
            helpAction    = "Hilfe"
            changeLanguageAction = "Sprache ändern"
        
        class Hints():
            openHint    = "Öffne eine Excel, PDF oder CSV Datei"
            newHint     = "Neue Reihe der aktuellen Ansicht hinzufügen"
            deleteHint  = "Reihe aus aktueller Ansicht entfernen"
            removeTableHint = "Entferne Tabelle aus der aktuellen liste"
            saveHint    = "Speicher alle Produkte der aktuellen Tabelle"
            saveAllHint = "Speicher alle Produkte von allen Tabellen"
            backHint    = "Gehe zurück zur vorherigen Tabelle"
            nextHint    = "Gehe zur nächsten Tabelle"
            translateHint = "Übersetze alle ausgewählten Produkte in die gewünschte Sprache"
            uploadHint  = "Lädt alle gespeicherten und markierten Produkte zu Shopware hoch"
            helpHint    = "Hilfe Inhalt"
            changeLanguageHint = "Wähle die neue Sprache"
            currentTableHint = "Aktuelle Tabelle"
        
        class Menu():
            file    = "Datei"
            table   = "Tabelle"
            help    = "Hilfe"

class TranslationLanguages(enum.Enum):
    English = "en"
    German  = "de"
    French  = "fr"
    Dutch   = "nl"
    Chinese = "zh-CN"
    Russian = "ru"
    Spanish = "es"
