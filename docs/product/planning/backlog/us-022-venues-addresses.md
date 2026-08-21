# User Story 022 - Adressen für die Veranstaltungsorte

Zur Darstellung der Veranstaltungsorte werden neben dem Namen des Veranstaltungsortes auch die Adresse und die x/y Koordinate benötigt. 
Hierfür soll ein python - Skript geschrieben werden, das mit Hilfe der Overpass-API und den OpenStreetmap Daten, anhand der bisherigen Informationen die fehlenden Daten recherchiert.
Entsprechend wird die Venues Information um die notwendigen Felder erweitert. 

Außerdem werden für alle bereits erfassten Venues (Veranstaltungsorte) die entsprechenden Daten heruntergeladen und als Datum gespeichert.

Es muss darauf geachtet werden, dass nur eine Adresse pro Sekunde ermittelt wird, um die Last auf die Openstreetmap Infrastruktur in Grenzen zu halten. 
