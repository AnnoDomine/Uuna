# AGENT.md - Technical Project Guide

Dieses Dokument dient als technischer Kontext für KI-Agenten und Entwickler, die an diesem Repository arbeiten.

## Projekt-Struktur

- **Core.lua**: Zentrale Logik, Event-Handling und Datenspeicherung.
- **UI_Main.lua**: Hauptfenster (Story Log) und Slash-Befehl `/uuna`.
- **UI_Aura.lua**: UI-Modul für das Aura-Tracking.
- **UI_Debug.lua**: UI-Modul für das Event-Logging.
- **UI_Quest.lua**: UI-Modul für den Quest-Status.
- **UI_Minimap.lua**: Implementierung des Minimap-Buttons (LibDBIcon-ähnlich, aber nativ).
- **UunaWantSomething.toc**: Addon-Metadaten und Dateireferenz.

## Datenmodell (SavedVariables)

- `UunaLogHistory`: Tabelle mit Strings der protokollierten Story-Ereignisse.
- `UunaSettings`: Benutzereinstellungen (Positionen, Sichtbarkeit).
- `UntrackedAuras`: Blacklist für Auras, die nicht im Log erscheinen sollen.
- `UunaCustomQuests`: (Geplant/In Arbeit) Tracking für spezifische Quest-IDs.

## Wichtige Konstanten

- `UunaAddon.SPECIES_ID = 2136`: Die SpeciesID von Uuna.

## Kern-Funktionen

- `UunaAddon:AddToStory(name, text, do_not_log)`: Fügt einen Eintrag zum Story-Log hinzu.
- `UunaAddon:AddToDebug(event, ...)`: Protokolliert ein Event für die Debug-Konsole.
- `UunaAddon:InitUI()`: Initialisiert das Haupt-Frame.

## Entwicklungskonventionen

- Alle Funktionen des Addons sollten an die globale Tabelle `UunaAddon` gebunden werden.
- UI-Elemente nutzen die `BasicFrameTemplateWithInset`.
- Lokalisierung ist aktuell hartkodiert (Deutsch/Englisch Mix), sollte bei Erweiterung modularisiert werden.

## TODOs / Roadmap

1. **Refactoring UI_Minimap.lua**: Prüfung auf Kompatibilität mit gängigen Bibliotheken.
2. **Quest Database**: Vervollständigung der geheimen Quest-IDs für Uuna (z.B. Weltreise-Etappen).
3. **Localization**: Einführung einer `L`-Tabelle für Mehrsprachigkeit.
4. **Export-Funktion**: Möglichkeit, das Log in die Zwischenablage zu kopieren.
