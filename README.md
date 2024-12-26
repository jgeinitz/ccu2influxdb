
This tiny little program reads xml data from a homematic ccu

It does this by reading three xml-files

- devicelist.xml
- statelist.xml
- rssilist.xml

These files are consolidated inside an sqlite db and then converted to influxdb lines.

