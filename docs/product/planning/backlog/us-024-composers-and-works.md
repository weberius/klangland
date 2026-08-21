# User Story 024 - Komponisten und Werke

Mit User Story 017 - Open Opus als Quelle für Werkdaten wurde die Grundlage geschaffen, um Informationen zu Komponisten und ihren Werken zu recherchieren. Im Rahmen dieser User Story werden die Information in die Anwendung integriert. 

Es wird eine neue Route erstellt: /composers erstellt. In der Ansicht werden alle Komponisten, die im System hinterlegt sind, alphabetisch aufgelistet. Die Darstellung erfolgt über einen Kachel. In dieser Kachel werden dazu die Werke der Komponisten, die im der aktuellen Spielzeit gespielt werden aufgelistet. 

Mit Klick auf einen Komponisten, wird eine Detailseite des Komponisten geöffnet. Hier finden sich Neben Namen und Lebensdaten weitere Informationen, die mit Open Opus ermittelt wurden. Außerdem gibt es eine Liste an Werken, die aufgeführt werden. Jeder Punkt dieser Liste kann angeklickt werden. Dadurch wird die Detailinformation zu dem entsprechenden Werk anzeigt. 

Bilder sollen, falls verfügbar, aus wikipedia/ wikicommons heruntergeladen werden. Sie werden nicht referenziert, sondern für die Verwendung in der Applikation heruntergeladen. Die Verwendung soll aber bei der Anzeige passend attributiert werden. 

Unterhalb der Details der Komponist:in wird eine Liste angzeigt, in welchen Veranstaltungen Musik der entsprechenden Komponisten aufgeführt werden. 

Die Detailinformation für das Werk besteht neben den Grundinformationen zum Komponisten auch aus der Werkbezeichnung und den Informationen, die zum Werk über Open Opus ermittelt werden konnten. Die URL zu den den Werken erfolgt über /works/xyz, wobei 'xyz' für den Titel, bzw. die id des Werkes steht (workId). 