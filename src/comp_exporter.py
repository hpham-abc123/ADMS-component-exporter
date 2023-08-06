#!/usr/bin/env python2.7
# ----------------------------------------------------------------------------
# Created Date: 29/05/2022
# version ='1.0'
# My weekend's work, to skill up my python skill(s) and to provide a free open
# source software to greater benefit the POA community.
#
# Script have been written with limited testing, please use with cautious
#
# License under GNU GENERAL PUBLIC LICENSE to provide freely distributable
# Please read LICENSE for ship with the script for more details
# ---------------------------------------------------------------------------

"""
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
Example to enable Python
PYTHONPATH=/users/lib/python:/users/lib/python:/opt/poweron/release/v6.5.1.1.11_rt/lib/python/
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
"""

from CompExportFormatter import ExporterFactory, PflExporter, TxtExporter, JSONExporter, MarkDownExporter
from libs.database import RDBMS
import PoaLibPath
import sys
import os
import re
import argparse
import json
import logging
# Append the script directory into the lib path so that we can
# import the custom PoaLibPath into the script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'lib'))

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

# ---------------------------------------------------------------------------


class PoaComponent(object):
    """ Class for connecting to Oracle database """

    def __init__(self, db):
        self._db = db

    # ----------------------------------------------------------------------
    def fetch_comp_id_from_alias(self, alias):
        sql = """select component_id from component_header
            where component_alias = :p1 and component_patch_number < 1
        """
        rows = self._db.fetch_rows(sql, p1=alias)
        if len(rows) > 1:
            raise NotImplementedError("This should never happen. Logic error")
        if not rows:
            return None
        return rows[0][0]

    # ----------------------------------------------------------------------
    def fetch_component_and_child_components(self, id):

        comp_ids = []
        sql = """
        with comp_list as (
            select component_id, component_dest_id, component_patch_number, level as lvl from component_header start with
            component_id = :p1
            connect by prior component_id = component_parent_id
        )
        select component_id, lvl from comp_list where component_dest_id is null
        and component_patch_number < 1
        order by lvl
        """
        rows = self._db.fetch_rows(sql, p1=id)
        for row in rows:
            comp_ids.append(row[0])

        if not len(comp_ids):
            return None

        return comp_ids

    # ----------------------------------------------------------------------

    def _fetch_relative_path_from_comp_id(self, id):
        """ Fetch the relative path of the compoment id """
        sql = """
        select reverse(tree) from
            (select  sys_connect_by_path( reverse(component_pathname), ':') as tree,
            connect_by_isleaf leaf from component_header start with component_id = :p1
            connect by prior component_parent_id = component_id)
            where leaf=1
        """
        rows = self._db.fetch_rows(sql, p1=id)
        if len(rows) > 1:
            raise NotImplementedError("This should never happen. Logic error")

        if not rows:
            return None

        c = rows[0][0].split(":")
        c = c[1:-2]  # remove the ROOT and the last two fields as it not requires
        return ":" + ":".join(c)

    # -----------------------------------------------------------------------
    def fetch_comp_header_from_id(self, id):
        """ Fetching the component details using the component id """
        result = []
        sql = "select * from component_header_view where component_id = :p1"
        rows, headings = self._db.fetch_all(sql, p1=id)

        if not len(rows):
            logger.fatal(
                "Component Id '{}' does no exist. Now exiting ...".format(id))
            sys.exit()
        for row in rows:
            details = dict(zip(headings, row))
            details['RELATIVE_PATH'] = self._fetch_relative_path_from_comp_id(
                id)
            result.append(details)
        return result[0]

    # -----------------------------------------------------------------------
    def fetch_attrs_from_comp_id(self, id):
        result = []
        sql = "select * from component_attributes where component_id = :p1 order by ATTRIBUTE_INDEX"
        rows, headings = self._db.fetch_all(sql, p1=id)
        for row in rows:
            res = dict(zip(headings, row))
            if res['ATTRIBUTE_TYPE'] == 1:  # VECTOR
                res['TABLE'] = (
                    self._fetch_attr_vector_details(res['ATTRIBUTE_ID']))
            elif res['ATTRIBUTE_TYPE'] == 2:  # TABLE
                res['TABLE'] = (
                    self._fetch_attr_vector_details(res['ATTRIBUTE_ID']))
            # elif res['ATTRIBUTE_TYPE'] == 3: #TEXTUAL
            #     pass
            result.append(res)
        return result

    # -----------------------------------------------------------------------
    def _get_attr_table_column_name(self, id):
        """Fetch attribute table column name from left to right"""
        res = []
        sql = """select column_number, column_name, column_de_type
            from vector_definition
            where attribute_id= :p1 order by column_number"""
        rows = self._db.fetch_rows(sql, p1=id)
        for row in rows:
            res.append({
                'COL_NUM': row[0],
                'COL_NAME': row[1],
                'DE_TYPE': row[2],
            })
        return res

    # -----------------------------------------------------------------------
    def _get_attr_table_data(self, id):
        res = []
        sql = """select vd.COLUMN_NUMBER, vv.VECTOR_ROW_NUM, vv.VECTOR_VALUE from VECTOR_VALUES vv
            inner join VECTOR_DEFINITION vd on vd.VECTOR_ID = vv.VECTOR_ID
            where vd.ATTRIBUTE_ID= :p1"""

        rows = self._db.fetch_rows(sql, p1=id)
        for row in rows:
            res.append({
                'COL_NUM': row[0],
                'ROW_NUM': row[1],
                'VALUE': row[2],
            })
        return res

    # -----------------------------------------------------------------------
    def _fetch_attr_vector_details(self, id):
        headings = self._get_attr_table_column_name(id)
        data = self._get_attr_table_data(id)
        return {'HEADING': headings, 'DATA': data}


# ---------------------------------------------------------------------------
def comp_export(poa_comp, id, is_recursive, file_exporter, attribute_filter):

    comp_ids = []

    f = ExporterFactory(file_exporter)
    if is_recursive:
        comp_ids = poa_comp.fetch_component_and_child_components(id)
    else:
        comp_ids.append(id)

    for comp_id in comp_ids:
        comp = poa_comp.fetch_comp_header_from_id(comp_id)
        f.export_component(comp)
        attrs = poa_comp.fetch_attrs_from_comp_id(comp_id)
        for attr in attrs:
            if attribute_filter and not re.search(attribute_filter, attr['ATTRIBUTE_NAME']):
                continue
            f.export_attribute(attr)
    return f.get_result()

# ---------------------------------------------------------------------------


def file_exporter_factory(output_format):
    file_exporter = None
    if output_format:
        if output_format.lower() == 'txt':
            file_exporter = TxtExporter()
        elif output_format.lower() == 'json':
            file_exporter = JSONExporter(json)
        elif output_format.lower() == 'md':
            file_exporter = MarkDownExporter()
        else:
            file_exporter = PflExporter()
    else:
        file_exporter = PflExporter()
    return file_exporter


# ---------------------------------------------------------------------------
def main():

    # -----------------------------------------------------------------------
    # Retrieving parameter input
    comp_id = None
    try:
        parser = argparse.ArgumentParser(
            prog=__file__,
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument('-i', '--comp_id', type=str,
                            required=False, help="Component ID")
        parser.add_argument('-c', '--comp_alias', type=str,
                            required=False, help="Component Alias")
        parser.add_argument('-a', '--attribute_filter', type=str, required=False,
                            help="Attribute to filter on. Use Python's regex expression")
        parser.add_argument('-f', '--output_format', type=str, required=False,
                            help="Output format (pfl, txt, json, md). Default to pfl")
        parser.add_argument('-r', '--recursive', action='store_true',
                            required=False, help="Recursively down the child component")
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    try:
        # -------------------------------------------------------------------
        # Need to have either a component id or component alias
        if not args.comp_id and not args.comp_alias:
            parser.print_help()
            sys.exit(0)

        poa_comp = PoaComponent(RDBMS)

        if args.comp_alias:
            comp_id = poa_comp.fetch_comp_id_from_alias(args.comp_alias)

        if args.comp_id:
            comp_id = args.comp_id

        is_recursive = False
        if args.recursive:
            is_recursive = True

        # -------------------------------------------------------------------
        # Define file format to output
        file_exporter = file_exporter_factory(args.output_format)

        print(comp_export(poa_comp, comp_id, is_recursive, file_exporter,
                          args.attribute_filter))

    except NotImplementedError as exp:
        logger.fatal(exp)
        sys.exit()


if __name__ == '__main__':
    main()
