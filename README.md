# ADMS component exporter

## Install

Copy the src files into your target directory and ensured the requires library are part of the PYTHONPATH environment variable. PoA Version 6.8 and above should have 
the correct PATH and doe s not require the PYTHONPATH to be added. However, if the script does not run then the PYTHONPATH will need to be added

For example:

```bash
PYTHONPATH=/users/lib/python:/users/lib/python:/user/poweron/release/v6.x.x.x.xx_rt/lib/python/
```

The /user/poweron/release/v6.x.x.x.xx_rt/lib/python/ is the path where cx_Oracle.so is located.

```bash
locate cx_Oracle
/user/poweron/release/v6.x.x.x.xx_rt/lib/python/cx_Oracle.so
```

## Usage

```bash
python comp_exporter
usage: comp_exporter/comp_exporter.py [-h] [-i COMP_ID]
                                                       [-c COMP_ALIAS]
                                                       [-a ATTRIBUTE_FILTER]
                                                       [-f OUTPUT_FORMAT] [-r]
                                                       [-n PFL_NEWLINE_CHAR]

=========================================================================

- v0.1: Experimental version
- v0.2: Added Recursive option to pull out all children component, excluding connection component
- v0.3: Fix issue with the recursive option where all the attribute was also added to the end of the PFL
- v0.4: Added new line character for multi-line attribute definition

=========================================================================

A basic script to pull out information from component_header_view and
component_attributes to a specific format for viewing or importing
into another environment

Currently, the format supported are: pfl, txt, json, md

With PFL, only core fields are export. Other non important field(s) are
currently not included.

For example, to run the script:
Example to enable Python
    To generate a PFL
    python comp_exporter  -c 'ALIAS-123-T'

    To generate a PFL filtered by a specified attribute name
    python comp_exporter -c 'ALIAS-123-T' -f '(Scan Value|Set State)'
    python comp_exporter -i 'x00abcdefCOMP' -f '(Scan Value|Set State)'

    To generate a PFL and all it associated children, excluding connection component
    python comp_exporter -c 'ALIAS-123-T' -r

    To generate a PFL with newline character as ';'. This is for multiline attribute definition
    python comp_exporter -c 'ALIAS-123-T' -n ';'

    To generate a TXT output filtered by a specified attribute name
    python comp_exporter -c 'ALIAS-123-T' -f Scan Value
|Set State
' -f txt

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
  -n PFL_NEWLINE_CHAR, --pfl_newline_char PFL_NEWLINE_CHAR
                        PFL newline char to put in PFL 1103 command
```
