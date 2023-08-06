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

import re

class PoaPfl(object):

    def __init__(self):
        pass

    # --------------------------------------------------------------------------------------
    @staticmethod
    def eof():
    # --------------------------------------------------------------------------------------
        return "    0\nENDSEC"

    # --------------------------------------------------------------------------------------
    @staticmethod
    def comment(comment):
    # --------------------------------------------------------------------------------------
        return "    999\n### %s ### \n" % comment

    # --------------------------------------------------------------------------------------
    @staticmethod
    def select_alias_1(alias):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Selecting Alias") + \
        "    1\n{}\n".format(alias)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def select_alias_1101(alias, rel_path, name):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Selecting Alias") + \
        "    1101\n{},{},{}\n".format(alias, rel_path, name)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def update_comp_header(detail):
    # --------------------------------------------------------------------------------------
        user_ref = detail.get('USER_REFERENCE') if detail.get('USER_REFERENCE') else ''
        comp_class = detail.get('COMPONENT_CLASS')
        trace_class = detail.get('COMPONENT_SWITCH_STATUS')
        substation_class = detail.get('COMPONENT_SUBSTATION_CLASS')
        type = detail.get('COMPONENT_TYPE')
        zone = detail.get('COMPONENT_ZONE') if detail.get('COMPONENT_ZONE') else ''

        return  PoaPfl.comment("Updating User Ref:{}, Class:{}, Trace Class:{}, Substation Class:{}, Type:{} and District Zone:{}".format(user_ref, comp_class, trace_class, substation_class, type, zone)) + \
        "7\n3,{},  9,{},  18,{},  19,{},  29,{},  15,{},\n".format(user_ref, comp_class, trace_class, substation_class, type, zone)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def select_attr_type(type):
    # --------------------------------------------------------------------------------------
        type_txt =''
        if type == 0:
            type_txt = 'SCALAR'
        elif type == 1:
            type_txt = 'VECTOR'
        elif type == 2:
            type_txt = 'TABLE'
        elif type == 3:
            type_txt = 'TEXTUAL'
        return PoaPfl.comment("Select {} Attribute Type".format(type_txt)) + "    66\n{}\n".format(type)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def select_attr(name):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Selecting Attribute '{}'".format(name)) + "    2\n{}\n".format(name)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def update_attr_header(detail):
    # --------------------------------------------------------------------------------------
        index = detail.get('ATTRIBUTE_INDEX')
        location = detail.get('ATTRIBUTE_LOCATION')
        de_type =  detail.get('ATTRIBUTE_DE_TYPE')
        protection = detail.get('PROTECTION_LEVEL')
        source = detail.get('SOURCE')
        alarm_ref = detail.get('ATTRIBUTE_ALARM_REF')
        ce_eval = detail.get('CE_EVAL_MODE')
        ce_interval = detail.get('RT_CALC_PERIODICITY') if detail.get('RT_CALC_PERIODICITY') else ''

        if ce_eval == 2: ## CE Evaluation: Periodic
            return PoaPfl.comment("Updating attribute header - Index: {}, Location: {}, DE type: {}, Protection Level: {}, Source: {}, Alarm Ref: {}, CE Evaluation: {}, CE Interval: {}".format(index, location, de_type, protection, source, alarm_ref, ce_eval, ce_interval)) + \
                                    "    5\n2,{},  5,{},  9,{},  16,{},  20,{},  10,{},  17,{},  23,{},\n".format(index, location, de_type, protection, source, alarm_ref, ce_eval, ce_interval)

        return PoaPfl.comment("Updating attribute header - Index: {}, Location: {}, DE type: {}, Protection Level: {}, Source: {}, Alarm Ref: {}, CE Evaluation: {}".format(index, location, de_type, protection, source, alarm_ref, ce_eval)) + \
                                    "    5\n2,{},  5,{},  9,{},  16,{},  20,{},  10,{},  17,{},\n".format(index, location, de_type, protection, source, alarm_ref, ce_eval)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_attr_table_size(col_size, row_size):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Set Table to {} col x {} row".format(col_size, row_size)) + \
        "    65\n{}\n    64\n{}\n".format(col_size, row_size)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_table_col_length(col_size):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Set column size to {}".format(col_size)) + \
        "    65\n{}\n".format(col_size)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_table_row_length(row_size):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Set row size to {}".format(row_size)) + \
        "    64\n{}\n".format(row_size)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def update_attr_val(val, force_update=False):
    # --------------------------------------------------------------------------------------
        if val is None and not force_update:
            return ""
        elif val is None and force_update:
            val = ""
        return "    6\n{}\n".format(val)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def attr_defn(defn):
    # --------------------------------------------------------------------------------------
        if defn is None:
            defn = ''
        return PoaPfl.comment("Set Attribute Definition") + \
        "    1000\n{}\n".format(str(defn).replace('\n', ' '))

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_columns_name_and_de_type(names, types):
    # --------------------------------------------------------------------------------------
        names_str = ','.join(names)
        types_str = ','.join(str(v) for v in types)
        return PoaPfl.comment("Set table column names and data type") + \
        "    8\n{}\n    9\n{}\n".format(names_str, types_str)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_table_data_val(col_num, row_num, val):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Populating column {}, row {} with {}".format(col_num, row_num, val)) + \
        "    60\n{}\n    61\n{}\n    3\n{}\n".format(col_num, row_num, val)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def set_vector_data_val(row_num, val):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Populating vector row {} with {}".format(row_num, val)) + \
        "    61\n{}\n    3\n{}\n".format(row_num, val)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def link_alarm_ref(alarm_ref):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Linking attribute alarm reference to {}".format(alarm_ref)) + \
        "    62\n{}\n".format(alarm_ref)

    # --------------------------------------------------------------------------------------
    @staticmethod
    def update_comp_header_set_comp_class(class_index):
    # --------------------------------------------------------------------------------------
        return PoaPfl.comment("Updating Compnenent class to {}".format(class_index)) + \
        "    7\n9,{}\n".format(class_index)

