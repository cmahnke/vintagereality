---
title: "Kartenansicht"
metaPage: true
displayinlist: false
---

Auf dieser Seite werden die Einträge mit (rekonstruierten) Geo-Informationen auf eine Karte angezeigt. Die Kartenanzige nutzt den externen Dienst [OpenStreetmap](https://www.openstreetmap.org/), daher muss der Nutzung zugestimmt werden.

{{< html/iframe-consent >}}
    {{< maps/osm src="./map.geojson" >}}
{{< /html/iframe-consent >}}

{{< html/link file="./map.geojson" content="GeoJSON" >}}
