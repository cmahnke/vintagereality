---
title: Vintage Reality
displayinlist: false
metaPage: true
description: "3D images are not a new invention - already at the end of the 19th century there were 3D viewers..."
outputs:
- html
- geojson
---

An experiment on media types and file formats.

{{< html/link file="./map.geojson" content="GeoJSON" >}}

{{< html/iframe-consent >}}
    {{< maps/osm src="./map.geojson" >}}
{{< /html/iframe-consent >}}

# Update Christmas 2022

* The quality of generated wigglegrams has been massively improved by using [StereoscoPy](https://github.com/2sh/StereoscoPy). It uses OpenCV to improve the image layout. Additionally, anaglyphs can now be generated.
* The improved arrangement does not work very well with low structured content, like interiors or many plants, without horizon or without contrast.
* There are now more images online
* [MPO](https://de.wikipedia.org/wiki/Multi_Picture_Object) files are now generated.


## For more information on viewing in the browser, see several blogs:
* [Learning to Free-View: See Stereoscopic Images with the Naked Eye](https://stereoscopy.blog/2022/03/11/learning-to-free-view-see-stereoscopic-images-with-the-naked-eye/)

# Image licenses
The following files from Wikimedia Commons are used, the respective license conditions can be found behind the respective link.
* {{< figure src="/images/3d/3d_glasses_red_blue.svg" class="glasses-icon" link="https://commons.wikimedia.org/wiki/File:3d_glasses_red_blue.svg" >}}
* {{< figure src="/images/3d/3d_glasses_red_cyan.svg" class="glasses-icon" link="https://de.wikipedia.org/wiki/Datei:3d_glasses_red_cyan.svg" >}}
