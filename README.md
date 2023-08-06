# ADMS component exporter


## Install

Copy the src files into your target directory and ensured the requires library are part of the PYTHONPATH environment variable

For example:
```
PYTHONPATH=/users/lib/python:/users/lib/python:/user/poweron/release/v6.x.x.x.xx_rt/lib/python/
```

The /user/poweron/release/v6.x.x.x.xx_rt/lib/python/ is the path where cx_Oracle.so is located.

```
locate cx_Oracle
/user/poweron/release/v6.x.x.x.xx_rt/lib/python/cx_Oracle.so
```


## Usage

```
python comp_exporter.py
usage: comp_exporter.py [-h] [-i COMP_ID] [-c COMP_ALIAS]
                        [-a ATTRIBUTE_FILTER] [-f OUTPUT_FORMAT] [-r]

=========================================================================

- v0.1: Experimental version
- License under GNU GENERAL PUBLIC LICENSE to provide freely distributable
- v0.2: Added Recursive option to pull out all children component, excluding connection component

=========================================================================

A basic script to pull out information from component_header_view and
component_attributes to a specific format for viewing or importing
into another environment

Currently, the format supported are pfl and txt.

With PFL, only core fields are export. Other non important field(s) are
currently not included.

Format supported are: pfl, txt, json, md

For example, to run the script:

Enable PYTHONPATH 
PYTHONPATH=/users/lib/python:/users/lib/python:/opt/poweron/release/v6.x.x.x.xx_rt/lib/python/

    To generate a PFL
    ./comp_exporter.py  -c 'ALIAS-123-T'

    To generate a PFL filtered by a specified attribute name
    ./comp_exporter.py -c 'ALIAS-123-T' -f '(Scan Value|Set State)'
    ./comp_exporter.py -i 'x00abcdefCOMP' -f '(Scan Value|Set State)'

    To generate a PFL and all it associated children, excluding connection component
    ./comp_exporter.py -c 'ALIAS-123-T' -r

    To generate a TXT output filtered by a specified attribute name
    ./comp_exporter.py -c 'ALIAS-123-T' -f '(Scan Value|Set State)' -f txt

=========================================================================

optional arguments:
  -h, --help            show this help message and exit
  -i COMP_ID, --comp_id COMP_ID
                        Component ID
  -c COMP_ALIAS, --comp_alias COMP_ALIAS
                        Component Alias
  -a ATTRIBUTE_FILTER, --attribute_filter ATTRIBUTE_FILTER
                        Attribute to filter on. Use Python's regex expression
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        Output format (pfl, txt, json, md). Default to pfl
  -r, --recursive       Recursively down the child component
```