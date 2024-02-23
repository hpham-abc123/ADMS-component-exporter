#----------------------------------------------------------------------------
# Created By  : Hung Pham
# Created Date: 29/05/2022
# version ='1.0'
# My weekend out of work's hour work, to skill up my python skill(s) and to
# provide a free open source software to greater benefit the POA community
# Script has not been fully tested, please use with cautious
# Copy Right under GNU GENERAL PUBLIC LICENSE to provide freely distributable
# Please read LICENSE.md for ship with the script for more details
# ---------------------------------------------------------------------------

# 04/06/2022 - Hung Pham - Added JSONExporter
# 16/06/2022 - Hung Pham - Fixed up PFL export to generate definition for RT only
#                          Added definition to vector attribute
# 06/09/2022 - Hung Pham - change to json format to properly output attributes
# 24/02/2024 - Hung Pham - Added get_footer to IExporter and PflExporter
from PoaPfl import PoaPfl
import copy
import datetime
import json

# ---------------------------------------------------------------------------
class IExporter(object):
    """ Abstrct Interface for Format Exporter """

    def __init__(self):
        self._result = ''

    def export_component(self, comp_details):
        raise NotImplementedError

    def export_attribute(self, attr):
        raise NotImplementedError

    def _export_scalar_attribute(self, attr):
        raise NotImplementedError

    def _export_vector_attribute(self, attr):
        raise NotImplementedError

    @staticmethod
    def _is_attr_type_table(attr_type):
        if int(attr_type) in [1,2]:
            return True
        return False

    def get_result(self):
        return self._result
    
    def get_footer(self):
        return ''


# ---------------------------------------------------------------------------
class TxtExporter(IExporter):

    def __init__(self):
        self._result = ''

    def export_attribute(self, attr):
        pfl = self._export_scalar_attribute(attr)
        pfl_table = ''
        if self._is_attr_type_table(attr['ATTRIBUTE_TYPE']):
            pfl_table = self._export_vector_attribute(attr['TABLE'])
        return pfl + pfl_table

    def export_component(self, comp_details):

        res = ''
        for key, value in comp_details.items():
            res += "COMPONENT_HEADER | %32s | %s\n" % ( key, value)
        self._result += res
        return res

    def _export_scalar_attribute(self, attr):
        res =''
        for key, value in attr.items():
            if key == 'TABLE':
                continue
            res += "ATTRIBUTE        | %32s | %s\n" % (key, value)
        self._result += res
        return res

    def _export_vector_attribute(self, attr_table):
        res = ''
        for v in attr_table['HEADING']:
            res += "ATTRIBUTE TABLE  | %32s | %s\n" % ('HEADING', v)
        for v in attr_table['DATA']:
            res += "ATTRIBUTE TABLE  | %32s | %s\n" % ('DATA', v)
        self._result += res
        return res


# ---------------------------------------------------------------------------
class PflExporter(IExporter):
    """ Concrete Implementation of PFL Exporter """

    def __init__(self, pfl_obj=PoaPfl()):
        super(PflExporter, self).__init__()
        self._pfl = pfl_obj
        self._attr_def = ''

    def export_component(self, comp_details):
        """ Build Component header """
        alias = comp_details['COMPONENT_ALIAS']
        rel_path = comp_details['RELATIVE_PATH']
        name = comp_details['COMPONENT_PATHNAME']

        select_alias = self._pfl.select_alias_1101( alias, rel_path, name)
        update_comp_header = self._pfl.update_comp_header(comp_details)
        self._result += select_alias + update_comp_header
        return select_alias + update_comp_header

    def export_attribute(self, attr):
        pfl =''
        if attr['ATTRIBUTE_TYPE'] == 0: #SCALAR
            return self._export_scalar_attribute(attr)
        elif attr['ATTRIBUTE_TYPE'] == 1: # VECTOR
            return self._export_vector_attribute(attr)
        elif attr['ATTRIBUTE_TYPE'] == 2: #TABLE
            return self._export_table_attribute(attr)
        elif attr['ATTRIBUTE_TYPE'] == 3: # TEXTUAL
            return self._export_scalar_attribute(attr)
        return pfl

    # --------------------------------------------------------------------------
    def _export_scalar_attribute(self, attr):
        """ Build SCALAR attribute details """

        name = attr['ATTRIBUTE_NAME']
        val = attr['ATTRIBUTE_VALUE']
        type = attr['ATTRIBUTE_TYPE']
        location = attr['ATTRIBUTE_LOCATION']

        select_attr_type = self._pfl.select_attr_type(type)
        select_attr = self._pfl.select_attr(name)
        update_attr_header= self._pfl.update_attr_header(attr)
        attr_val = self._pfl.update_attr_val(val)
        #alarm_ref = self._pfl.link_alarm_ref(attr['ATTRIBUTE_ALARM_REF'])
        attr_defn = self._pfl.attr_defn(attr['ATTRIBUTE_DEFINITION']) if location ==1 else ''

        res = select_attr_type + select_attr + update_attr_header + attr_val# + alarm_ref
        self._result += res
        if location == 1:
            self._attr_def += select_attr + attr_defn
        return res + attr_defn

    # --------------------------------------------------------------------------
    def _export_vector_attribute(self, attr):
        """ Build Vector detail such as table """
        res  = ''
        attr_table = attr['TABLE']
        col_cnt = len(attr_table['HEADING'])
        cell_cnt = len(attr_table['DATA'])
        row_cnt = int(cell_cnt/col_cnt)
        location = attr['ATTRIBUTE_LOCATION']

        select_type = self._pfl.select_attr_type(attr['ATTRIBUTE_TYPE'])
        set_attr_table_size = self._pfl.set_attr_table_size(col_cnt, row_cnt)
        select_attr = self._pfl.select_attr(attr['ATTRIBUTE_NAME'])
        update_attr_header= self._pfl.update_attr_header(attr)
        attr_defn = self._pfl.attr_defn(attr['ATTRIBUTE_DEFINITION']) if location ==1 else ''

        # ----------------------------------------------------------------------
        tab_data = ''
        res = select_type + set_attr_table_size + select_attr + update_attr_header + tab_data

        if location == 1:
            self._attr_def += select_attr + attr_defn
        self._result += res
        return res + attr_defn

    # --------------------------------------------------------------------------
    def _export_table_attribute(self, attr):
        """ Build table detail such as table """

        res  = ''
        attr_table = attr['TABLE']
        col_cnt = len(attr_table['HEADING'])
        cell_cnt = len(attr_table['DATA'])
        row_cnt = int(cell_cnt/col_cnt)

        select_type = self._pfl.select_attr_type(attr['ATTRIBUTE_TYPE'])
        set_attr_table_size = self._pfl.set_attr_table_size(col_cnt, row_cnt)
        select_attr = self._pfl.select_attr(attr['ATTRIBUTE_NAME'])

        update_attr_header= self._pfl.update_attr_header(attr)

        # ----------------------------------------------------------------------------------------
        col_names = []
        col_data_types = []
        for val in attr_table['HEADING']:
                col_names.append(val['COL_NAME'])
                col_data_types.append(val['DE_TYPE'])
        columns_name_and_de_type = self._pfl.set_columns_name_and_de_type(col_names, col_data_types)

        # ----------------------------------------------------------------------------------------
        tab_data = ''
        for v in attr_table['DATA']:
            tab_data += self._pfl.set_table_data_val(v['COL_NUM'], v['ROW_NUM'], v['VALUE'])
        res = select_type + set_attr_table_size + columns_name_and_de_type + select_attr + update_attr_header + tab_data
        self._result += res
        return res

    # --------------------------------------------------------------------------
    def get_result(self):
        """ Return output export result in a string format """
        return self._result + self._attr_def
    
    # --------------------------------------------------------------------------
    def get_footer(self):
        return self._pfl.eof()

# ---------------------------------------------------------------------------
class JSONExporter(IExporter):
    """ JSON file exporter """

    def __init__(self, json):
        super(JSONExporter, self).__init__()
        self._json = json
        self._header_dict = None
        self._attrs = {}

    def export_component(self, comp_details):
        res = self._json.dumps(comp_details, default = str, indent = 4)
        self._header_dict =  copy.deepcopy(comp_details)
        return res

    def export_attribute(self, attr):
        res = self._json.dumps(attr, indent = 4, default = str)
        attr_name = attr['ATTRIBUTE_NAME']
        self._attrs[attr_name] = copy.deepcopy(attr)
        return res

    def get_result(self):
        comp_id= self._header_dict.get("COMPONENT_ID")
        res = { comp_id :
            {
                'COMPONENT_HEADER': self._header_dict,
                'COMPONENT_ATTRIBUTES': self._attrs,
            }
        }
        return self._json.dumps(res, indent = 4, default = str)


# ---------------------------------------------------------------------------
class MarkDownExporter(IExporter):

    ignore_header_fields = (
		'EXTERNAL_SOURCE',
		'MRCOT',
		'COMPONENT_ID',
		'COMMISSIONING_DRESSING_VALID',
		'LIVE_STATE',
		'COMPONENT_NORMAL_PRIORITY',
		'AUTOMATIC_CIRCUIT_NAMING',
		'COMPONENT_SOURCE_ID',
		'COMPONENT_HAS_CTE',
		'COMPONENT_PRIORITY',
		'COMPONENT_PARENT_ID',
		'COMPONENT_DRESSING',
		'COMPONENT_CLONE_ID',
		'COMPONENT_LAST_ZONE',
		'COMMISSIONING_DRESSING',
		'COMPONENT_CATEGORIES',
		'COMPONENT_NEEDS_REPLICATION',
		'COMPONENT_APPLIC_FLAGS',
		'PHASE',
		'DRESSING_TEXT',
		'COMPONENT_AREA',
		'COMPONENT_OWN_MAINT_CTRL',
		'COMPONENT_LAST_OPERATION',
		'COMMISSIONING_STATE',
		'COMPONENT_STATUS',
		'COMPONENT_CONNECT_CLASS',
		'COMPONENT_DEST_ID',
		'COMPONENT_SWITCH_STATUS',
		'COMPONENT_CE_ENABLE',
		'COMPONENT_NORMAL_DRESSING',
		'COMPONENT_VERSION',
		'MAINTENANCE_ZONE_ID',
		'NAMING',
		'COMPONENT_DEAD_ID',
		'COMPONENT_PATCH_NUMBER',
		'PHASES_SWITCHING_MODE',
		'DELEGATED_ZONE_ID',
		'PHASES_PRESENT',
		'COMPONENT_SUBSTATION_CLASS',
		'COMPONENT_DEAD_STATUS',
		'COMPONENT_DAMAGE_ID',
		'PHASES_NORMALLY_OPEN',
		'COMPONENT_DAMAGE_STATUS',
		'COMPONENT_DSH_DRESSING',
		'BIT_SIZE',
		'LIVE_STATE_COLOUR',
     )

    interested_attribute_fields=(
    'ATTRIBUTE_INDEX',
    'ATTRIBUTE_NAME',
    'ATTRIBUTE_VALUE',
    'ATTRIBUTE_DEFINITION',
    'ATTRIBUTE_DE_TYPE',
    'PROTECTION_LEVEL',
    'ATTRIBUTE_ALARM_REF',
    'ATTRIBUTE_LOCATION',
    )

    def __init__(self):
        self._result = ''
        self.has_attribute_header_generated = False

    def export_attribute(self, attr):

        pfl = self._export_scalar_attribute(attr)
        pfl_table = ''
        if self._is_attr_type_table(attr['ATTRIBUTE_TYPE']):
            pfl_table = self._export_vector_attribute(attr['TABLE'])
        return pfl + pfl_table

    def export_component(self, comp_details):

        res = '#### Component Header\n\n' + \
        "| Name | Value |\n" + \
        "| ---- | ----- |\n"
        for key, value in comp_details.items():
			# Skipping the ignore header fields as some of the field we do not interested.
            if key in MarkDownExporter.ignore_header_fields:
                continue
            if value is None:
                value = ''
            res += "| %s | %s |\n" % ( key, value)
        self._result += res
        return res

    def _export_scalar_attribute(self, attr):

        res =''

        if not self.has_attribute_header_generated:
            res +='\n\n#### Component Attributes\n\n'
            sep = ''
            for col_name in MarkDownExporter.interested_attribute_fields:
                res += "| %s " % col_name
                sep += "| ---- "
            res +="|\n" + sep + "|\n"
            self.has_attribute_header_generated = True

        for col_name in  MarkDownExporter.interested_attribute_fields:
            value = attr[col_name]
            if value is None:
                value = ''
            if value and "\n" in str(value):
                value = value.replace("\n", "<br/>")
                value = value.replace(" ", "&nbsp;")
            res += "| %s " % (value)
        self._result += res + "|\n"
        return res

    def _export_vector_attribute(self, attr_table):
        res = ''
        raise NotImplemented("TODO")
        return res

# ---------------------------------------------------------------------------
class ExporterFactory(object):

    def __init__(self, exporter):
        self._exporter = exporter

    def export_component(self, comp_details):
        return self._exporter.export_component(comp_details)

    def export_attribute(self, attr_details):
        return self._exporter.export_attribute(attr_details)

    def get_result(self):
        return self._exporter.get_result()

    def save_to_file(self, fname):
        with open (fname, "w") as out:
            out.write(self._exporter.get_file_content())
        print "{} generated ...".format(fname)


