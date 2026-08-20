# Map Country

Alle Orte sollen auf einer Karte angezeigt werden. Als Grundlage soll Openstreetmap verwendet werden. In dieser Ansicht werden die Marker nur auf die Orte selber gesetzt. Für Köln z.B. wird die x/y Koordinate von Köln verwendet und nicht die Adresse, bzw. x/y-Koordinate der Philharmonie. Diese Ansicht soll in erster Linie der Übersicht dienen. Wenn auf einen Ort geklickt wird, wird der Filter auf den entsprechenden Ort angewandt. Wird also auf Köln geklickt, werden nur Konzerte, die mit der cities-id ("id": "koeln") angezeigt. Außerdem wird der ausgewählte Ort markiert. 
Es ist möglich, den Filter zurück zu setzen, um wieder alle events anzuzeigen. 

Die Anzeige der Orte findet auf einer eigenen Seite statt. Dafür wird eine Route http://localhost:4200/cities implementiert. Der Navigationseintrag  wird in der Navigation von 'Kalender', 'Ensembles' und 'Spielstätten' angezeigt. 

Datentechnisch muss für jeden Ort, der einem ensemble zugeordnet ist, die x/y-Koordinate abgespeichert werden. Zur Recherche soll openstreetmap verwendet werden. Für die Abfrage kann ein eigenes python-skript erstellt werden, 