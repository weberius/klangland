# Map Country

Alle Orte der Ensembels sollen auf einer Karte angezeigt werden. Es werden nur die Orte der Ensembles angezeigt, nicht die Venues. Als Grundlage für die Darstellung der Karten soll Openstreetmap verwendet werden. Die Orte werden als rote Punkte auf der Karte dargestellt. Zur Darstellung der PUnkte wird Leaflet verwendet. 

In dieser Ansicht werden die Marker nur auf die Orte selber gesetzt. Für Köln z.B. wird die x/y Koordinate von Köln verwendet und nicht die Adresse, bzw. x/y-Koordinate der Philharmonie. Diese Ansicht soll in erster Linie der Übersicht dienen. Wenn auf einen Ort geklickt wird, wird angeboten, den Filter auf den entsprechenden Ort anzuwenden. 

Wird also auf Köln geklickt, werden nur Konzerte, die mit der cities-id ("id": "koeln") angezeigt. Außerdem wird der ausgewählte Ort markiert. 

Der Filter wird an den bereits vorhandenen Stellen zurück gesetzt. 

Die Anzeige der Orte findet auf einer eigenen Seite statt. Dafür wird eine Route http://localhost:4200/cities implementiert. Der Navigationseintrag  wird in der Navigation von 'Kalender', 'Ensembles' und 'Spielstätten' angezeigt. 

Datentechnisch muss für jeden Ort, der einem ensemble zugeordnet ist, die x/y-Koordinate abgespeichert werden. Zur Recherche soll openstreetmap verwendet werden. Für die Abfrage kann ein eigenes python-skript erstellt werden, das die Overpass API von Openstreetmap verwendet. Es muss darauf geachtet werden, dass nicht mehr als 1 Standort pro Sekunde abgefragt wird, um zu verhindern, dass openstreetmap zu stark unter Last gerät.