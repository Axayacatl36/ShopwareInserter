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
            saveAction      = "Save Table"
            saveAllAction   = "Save all Tables"
            translateAction = "Translate"
            uploadAction    = "Upload"
            helpAction = "Help"
            changeLanguageAction = "Change Language"
        
        class Hints():
            openHint    = "Open a excel, pdf or csv file"
            newHint     = "Add new row to current view" 
            deleteHint  = "Delete a row from current view"
            saveHint    = "Save all products of current table"
            saveAllHint = "Save all products of all current tables"
            translateHint = "Translate selected Products to selected Language"
            uploadHint  = "Uploads all saved and flagged products to Shopware"
            helpHint    = "Help Content"
            changeLanguageHint = "Choose new language"
        
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
            saveAction      = "Tabelle speichern"
            saveAllAction   = "Alle Tabellen speichern"
            translateAction = "Übersetzen"
            uploadAction    = "Hochladen"
            helpAction    = "Hilfe"
            changeLanguageAction = "Sprache ändern"
        
        class Hints():
            openHint    = "Öffne eine Excel, PDF oder CSV Datei"
            newHint     = "Neue Reihe der aktuellen Ansicht hinzufügen"
            deleteHint  = "Reihe aus aktueller Ansicht entfernen"
            saveHint    = "Speicher alle Produkte der aktuellen Tabelle"
            saveAllHint = "Speicher alle Produkte von allen Tabellen"
            translateHint = "Übersetze alle ausgewählten Produkte in die gewünschte Sprache"
            uploadHint  = "Lädt alle gespeicherten und markierten Produkte zu Shopware hoch"
            helpHint    = "Hilfe Inhalt"
            changeLanguageHint = "Wähle die neue Sprache"
        
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
