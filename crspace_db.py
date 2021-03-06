#!/usr/bin/env python
# -*- python -*-
'''
Created on 19.1.2018
@author: Adiry
'''
import os
import shutil
import glob
import tarfile
import argparse
import sys
import subprocess
import datetime

class crspace_and_nic: #key=CrSpcae , value=nic 
    CrSpace_dict = {
        '/dev/mst/mt4115_pciconf0': 'crspace_shomron',
        '/dev/mst/mt4117_pciconf0': 'crspace_dotan',
        '/dev/mst/mt4119_pciconf0': 'crspace_galil',
        '/dev/mst/mt4121_pciconf0': 'crspace_galil',
        '/dev/mst/mt41682_pciconf0': ['crspace_bluefield_pcore0','crspace_bluefield_pcore1'],
        '/dev/mst/mt4113_pciconf0': ['crspace_negev_pcore0','crspace_negev_pcore1'],
    }

#order for fields: address, offset, size, default_value, spaces_for_next_element, number_of_available_next_elements
#in every class must provide the jump between port in each reg
#order for filed apdate: address,offset,size,jump
class crspace_shomron:
    REGISTERS = {
        'current_link_speed': [0x11f464, 0, 3, 0x100],
        'speed_en': [0x11f434, 12, 3, 0x100],
        'fw_directed_speed_change': [0x11f410, 1, 1, 0x100],
        'negotiated_link_width': [0x11f464, 8, 6, 0x100],
        'active_host_space': [0X11fd88, 0, 3, 0],
        'cfgwr0_compliter_id': [0X1000C0, 0, 16, 0x80],  # address for port 0

        'fsm_0_speed_en': [0x11f434, 12, 3],
        'port_state': [0xf3810, 0, 8],
        'cx3_directed_width': [0xf39b0, 0, 4],
        'upconfigure_go': [0xf39b4, 0, 1],
        'tx_polarity': [0xf3888, 0, 8],
        'spare_top4x_0': [0xf22b0, 24, 8],
        'spare_top4x_1': [0xf24b0, 24, 8],
        'device_id': [0x0014, 0, 16],


        # cause
        'rx_errors_get':[0x11e80c, 0, 32, 0x200],
        'rx_errors_clear': [0x11e818, 0, 32, 0x200],

        'pxd_cause_get': [0x1100cc, 0, 32, 0x200],
        'pxd_cause_clear': [0x1100d8, 0, 32,  0x200],
        #cause new
        "pxd_causereg0":[0x1100cc,0,32,0x200],
        "clr_pxd_causereg0": [0x1100d8, 0, 32, 0x200],
        "npi_checks_causereg":[0x100dac,0,17,0x0],
        "clr_npi_checks_causereg": [0x100db8, 0, 17, 0x0],
        "cause_fatal_causereg":[0x11e86c,0,12,0x200],
        "clr_cause_fatal_causereg": [0x11e878, 0, 12, 0x200],

    }


class crspace_dotan:
    REGISTERS = {
        'current_link_speed': [0x11f464, 0, 3, 0x100],
        'speed_en': [0x11f434, 12, 3 , 0x100],
        'fw_directed_speed_change': [0x11f410, 1, 1, 0x100],
        'negotiated_link_width': [0x11f464, 8, 6, 0x100],
        'fsm_0_speed_en': [0x11f434, 12, 3],
        'active_host_space': [0X11fd88, 0, 3,0],
        'cfgwr0_compliter_id': [0X1000C0, 0, 16, 0x80],# address for port 0

        # cause
        'rx_errors_get': [0x11e80c, 0, 32, 0x200],
        'rx_errors_clear': [0x11e818, 0, 32, 0x200],
        'pxd_cause_get': [0x1100cc, 0, 32, 0x200],
        'pxd_cause_clear': [0x1100d8, 0, 32, 0x200],
        #cuase new
        "pxd_causereg0": [0x1100cc, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x1100d8, 0, 32, 0x200],
        "npi_checks_causereg": [0x1061cc, 0, 17, 0x20],
        "clr_npi_checks_causereg": [0x1061d8, 0, 17, 0x20],
        "cause_fatal_causereg": [0x11e86c, 0, 12, 0x200],
        "clr_cause_fatal_causereg": [0x11e878, 0, 12, 0x200],

    }

class crspace_galil:
    REGISTERS = {
        'current_link_speed': [0x137064, 0, 3, 0x100],
        'speed_en': [0x137034, 12, 4, 0x100],
        'fw_directed_speed_change': [0x137010, 1, 1, 0x100],
        'pcie_switch_en': [0xf8b0, 0, 0, 0],

        'negotiated_link_width': [0x137064, 8, 6, 0x100],
        'perf_selector2': [0x10fa84, 16, 16],
        'perf_counter2': [0x10fac8, 0, 32],

        # registers for enable VDM
        'vdm_gw[8].desc0.data_1151_1120': [0x105170, 0, 32, 0x72000010],
        'vdm_gw[8].desc0.data_1119_1088': [0x105174, 0, 32, 0x0000007e],
        'vdm_gw[8].desc0.data_1087_1056': [0x105178, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1055_1024': [0x10517c, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1023_992':  [0x105180, 0, 32, 0x0],
        'vdm_gw[8].ctrl_end_pos': [0x105100, 20, 5, 0x13],
        'vdm_gw[8].ctrl_num_extra_lines': [0x105100, 25, 3, 0],
        'vdm_gw[8].ctrl_burst_mode': [0x105100, 28, 1, 1],
        'vdm_gw[8].busy': [0x105100, 30, 1, 1],
        'vdm_gw[8].burst_mode_exit': [0x1050e0, 0, 1, 1],

        'link[8].consumed_ph': [0x101618,16,16],

        #physical
        'fsm[0]_speed_en': [0x137034, 12, 4],
        'fsm[8]_speed_en': [0x137834, 12, 4],
        'fsm[0]_fw_directed_speed_change': [0x137010, 1, 1,1],
        'fsm[8]_fw_directed_speed_change': [0x137810, 1, 1,1],
        'fsm[0]_current_link_speed': [0x137064, 0, 3],

        'active_host_space': [0X126D40, 0, 16, 0],
        'cfgwr0_compliter_id': [0X108340, 0, 16, 0x10],  # address for port 0
        'port_state' : [0x137000,0,8,0x100],

        # cause
        'rx_errors_get': [0x13b01c, 0, 32, 0x400],
        'rx_errors_clear': [0x13b018, 0, 32, 0x400],
        'pxd_cause_get': [0x12019c, 0, 32,  0x200],
        'pxd_cause_clear': [0x120198, 0, 32, 0x200],

        # cuase new
        "pxd_causereg0": [0x12019c, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x120198, 0, 32, 0x200],
        "npi_checks_causereg": [0x10b81c, 0, 32, 0x80],
        "clr_npi_checks_causereg": [0x10b818, 0, 32, 0x80],
        "cause_fatal_causereg": [0x13b0dc, 0, 14, 0x400],
        "clr_cause_fatal_causereg": [0x13b0d8, 0, 14, 0x400],
    }

class crspace_bluefield_pcore0:
    REGISTERS = {
        'current_link_speed': [0x137064, 0, 3, 0x100],
        'speed_en': [0x137034, 12, 4, 0x100],
        'fw_directed_speed_change': [0x137010, 1, 1, 0x100],
        'negotiated_link_width': [0x137064, 8, 6, 0x100],

#registers for enable VDM
        'vdm_gw[8].desc0.data_1151_1120': [0x185b70, 0, 32, 0x72000010],
        'vdm_gw[8].desc0.data_1119_1088': [0x185b74, 0, 32, 0x0000007e ],
        'vdm_gw[8].desc0.data_1087_1056': [0x185b78, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1055_1024': [0x185b7c, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1023_992':  [0x185b80, 0, 32, 0x0],
        'vdm_gw[8].ctrl_end_pos':   [0x185b00, 19, 5, 0x0],
        'vdm_gw[8].ctrl_num_extra_lines': [0x185b00, 24, 3, 0x13],
        'vdm_gw[8].ctrl_burst_mode': [0x185b00, 27, 1,0],
        'vdm_gw[8].busy':            [0x185b00, 30, 1,1],

#registers for enabling link between switch-eep analyzer
        'analyzer_loop_data_en': [0x13ff80, 0, 1, 1,0x40000,2],
        'la_loop_en': [0x13ff98, 0, 1, 1,0x40000,2],
        'rx_power_mode': [0x137034, 26, 2, 2,0x40000,2],
        'rx_active_lanes': [0x137004, 0, 16, 0x00FF,0x40000,2],
        'cfg_wdtstr_2_cmpl_la_ark_en': [0x13ff80, 13, 1, 1,0x40000,2],
        'polling_act_2_cfg_la_ark_en': [0x13ff80, 9, 1, 1,0x40000,2],
        'cfg_compl_2_idle_la_ark_en': [0x13ff80, 29, 1, 1,0x40000,2],
        'pcie_analyzer_en': [0x139100, 0, 1, 1,0x40000,2],
        'analyzer_x_2_x_la_ark_en' :[0x13ff80,0,32,0xfffffff0,0x40000,2],
        'signal_detect_any_combined_la_en': [0x13ff84, 26, 1, 0,0x40000,2],
        'num_of_ts_config_complete': [0x137050, 0, 2, 1, 0x40000, 2],
        'bug193974_disable': [0x13fe28, 18, 1, 1, 0x40000, 2],
        #'vf_stride': [0x111080, 0, 5, 1, 0x40000, 2],
        'bar_en': [0x111004, 0 ,1, 1, 0x40000, 2],
        'bar_link_id': [0x111004, 4, 4, 0, 0x40000, 2],
        'log_minibar_size': [0x11100c, 16, 6, 51, 0x40000, 2],
        'base_bdf': [0x111008, 0, 16, 0, 0x40000, 2],
        'ari_en': [0x111004, 2, 1, 0, 0x40000, 2],
        'num_of_func': [0x11100c, 0, 16, 1, 0x40000, 2],
        'block_state_main': [0x137070, 0, 32, 0x04000012, 0x40000, 2],

        # address for analyzer
        'start_addr_63_32_pcore0': [0x139188, 0, 32, 0xFF],
        'start_addr_31_0_pcore0': [0x13918c, 0, 32, 0xFF],
        'end_addr_63_32_pcore0': [0x139190, 0, 32, 0xFF],
        'end_addr_31_0_pcore0': [0x139194, 0, 32, 0xFF],
        'start_addr_63_32_pcore1': [0x179188, 0, 32, 0xFF],
        'start_addr_31_0_pcore1': [0x17918c, 0, 32, 0xFF],
        'end_addr_63_32_pcore1': [0x179190, 0, 32, 0xFF],
        'end_addr_31_0_pcore1': [0x179194, 0, 32, 0xFF],
        'writes_after_trigger_63_32': [0x139198, 0, 32, 0, 0x40000, 2],
        'writes_after_trigger_31_0': [0x13919c, 0, 32, 5, 0x40000, 2],
        'trigger_cnt': [0x139148, 0, 32, 0, 0x40000, 2],
        'rst_addr': [0x1391a0, 0,1, 1, 0x40000, 2],
        'rst_sync_cnt': [0x1391a0, 1, 1, 1, 0x40000, 2],
        'rst_after_trigger_cnt': [0x1391a0, 2, 1, 1, 0x40000, 2],
        'tlp_hdr_dw1': [0x139184, 0, 32, 0xff, 0x40000, 2],

        # trigger per pcore
        'fw_rx_cmd4_full_byte': [0x13880c, 0, 32, 0x1013000, 0x40000, 2],
        'trigger_rx_ok4_en': [0x139144, 0, 16, 0xFF, 0x40000, 2],
        'trigger_en': [0x139100, 1, 1, 1, 0x40000, 2],

        #physical
# address, offset, size, default_value, spaces_for_next_element, number_of_available_next_elements

        'fw_directed_speed_change_pcore_0': [0x137210, 1, 1, 1, 0x200, 8 ],
        'fw_directed_speed_change_pcore_1': [0x177010, 1, 1, 1, 0x200, 8 ],



        # cause
        'rx_errors_get': [0x13b01c, 0, 32, 0x400],
        'rx_errors_clear': [0x13b018, 0, 32, 0x400],
        'pxd_cause_get': [0x12019c, 0, 32, 0x200],
        'pxd_cause_clear': [0x120198, 0, 32, 0x200],
        'primary_bus': [0X11041c, 8, 8, 0],
        'active_host_space': [0X13ff40, 0, 16, 0],
        'cfgwr0_compliter_id': [0X108340, 0, 16, 0x10],
        'port_state' : [0x137000,0,8,0x100],  #address for port 0

        # cuase new
        "pxd_causereg0": [0x12019c, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x120198, 0, 32, 0x200],
        "npi_checks_causereg": [0x10b81c, 0, 32, 0x80],
        "clr_npi_checks_causereg": [0x10b818, 0, 32, 0x80],
        "cause_fatal_causereg": [0x13b0dc, 0, 14, 0x400],
        "clr_cause_fatal_causereg": [0x13b0d8, 0, 14, 0x400],


    }

class crspace_bluefield_pcore1:
    REGISTERS = {
        'current_link_speed': [0x177064, 0, 3, 0x100],
        'speed_en': [0x177034, 12, 4, 0x100],
        'fw_directed_speed_change': [0x177010, 1, 1, 0x100],
        'negotiated_link_width': [0x177064, 8, 6, 0x100],

#registers for enable VDM
        'vdm_gw[8].desc0.data_1151_1120': [0x185b70, 0, 32, 0x72000010],
        'vdm_gw[8].desc0.data_1119_1088': [0x185b74, 0, 32, 0x0000007e ],
        'vdm_gw[8].desc0.data_1087_1056': [0x185b78, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1055_1024': [0x185b7c, 0, 32, 0x0],
        'vdm_gw[8].desc0.data_1023_992':  [0x185b80, 0, 32, 0x0],
        'vdm_gw[8].ctrl_end_pos':   [0x185b00, 19, 5, 0x0],
        'vdm_gw[8].ctrl_num_extra_lines': [0x185b00, 24, 3, 0x13],
        'vdm_gw[8].ctrl_burst_mode': [0x185b00, 27, 1,0],
        'vdm_gw[8].busy':            [0x185b00, 30, 1,1],

#registers for enabling link between switch-eep analyzer
        'analyzer_loop_data_en': [0x13ff80, 0, 1, 1,0x40000,2],
        'la_loop_en': [0x13ff98, 0, 1, 1,0x40000,2],
        'rx_power_mode': [0x137034, 26, 2, 2,0x40000,2],
        'rx_active_lanes': [0x137004, 0, 16, 0x00FF,0x40000,2],
        'cfg_wdtstr_2_cmpl_la_ark_en': [0x13ff80, 13, 1, 1,0x40000,2],
        'polling_act_2_cfg_la_ark_en': [0x13ff80, 9, 1, 1,0x40000,2],
        'cfg_compl_2_idle_la_ark_en': [0x13ff80, 29, 1, 1,0x40000,2],
        'pcie_analyzer_en': [0x139100, 0, 1, 1,0x40000,2],
        'analyzer_x_2_x_la_ark_en' :[0x13ff80,0,32,0xfffffff0,0x40000,2],
        'signal_detect_any_combined_la_en': [0x13ff84, 26, 1, 0,0x40000,2],
        'num_of_ts_config_complete': [0x137050, 0, 2, 1, 0x40000, 2],
        'bug193974_disable': [0x13fe28, 18, 1, 1, 0x40000, 2],
        #'vf_stride': [0x111080, 0, 5, 1, 0x40000, 2],
        'bar_en': [0x111004, 0 ,1, 1, 0x40000, 2],
        'bar_link_id': [0x111004, 4, 4, 0, 0x40000, 2],
        'log_minibar_size': [0x11100c, 16, 6, 51, 0x40000, 2],
        'base_bdf': [0x111008, 0, 16, 0, 0x40000, 2],
        'ari_en': [0x111004, 2, 1, 0, 0x40000, 2],
        'num_of_func': [0x11100c, 0, 16, 1, 0x40000, 2],
        'block_state_main': [0x137070, 0, 32, 0x04000012, 0x40000, 2],

        # address for analyzer
        'start_addr_63_32_pcore0': [0x139188, 0, 32, 0xFF],
        'start_addr_31_0_pcore0': [0x13918c, 0, 32, 0xFF],
        'end_addr_63_32_pcore0': [0x139190, 0, 32, 0xFF],
        'end_addr_31_0_pcore0': [0x139194, 0, 32, 0xFF],
        'start_addr_63_32_pcore1': [0x179188, 0, 32, 0xFF],
        'start_addr_31_0_pcore1': [0x17918c, 0, 32, 0xFF],
        'end_addr_63_32_pcore1': [0x179190, 0, 32, 0xFF],
        'end_addr_31_0_pcore1': [0x179194, 0, 32, 0xFF],
        'writes_after_trigger_63_32': [0x139198, 0, 32, 0, 0x40000, 2],
        'writes_after_trigger_31_0': [0x13919c, 0, 32, 5, 0x40000, 2],
        'trigger_cnt': [0x139148, 0, 32, 0, 0x40000, 2],
        'rst_addr': [0x1391a0, 0,1, 1, 0x40000, 2],
        'rst_sync_cnt': [0x1391a0, 1, 1, 1, 0x40000, 2],
        'rst_after_trigger_cnt': [0x1391a0, 2, 1, 1, 0x40000, 2],
        'tlp_hdr_dw1': [0x139184, 0, 32, 0xff, 0x40000, 2],

        # trigger per pcore
        'fw_rx_cmd4_full_byte': [0x13880c, 0, 32, 0x1013000, 0x40000, 2],
        'trigger_rx_ok4_en': [0x139144, 0, 16, 0xFF, 0x40000, 2],
        'trigger_en': [0x139100, 1, 1, 1, 0x40000, 2],

        #physical
# address, offset, size, default_value, spaces_for_next_element, number_of_available_next_elements

        'fw_directed_speed_change_pcore_0': [0x137210, 1, 1, 1, 0x200, 8 ],
        'fw_directed_speed_change_pcore_1': [0x177010, 1, 1, 1, 0x200, 8 ],

        # cause
        'rx_errors_get': [0x17b01c, 0, 32, 0x400],
        'rx_errors_clear': [0x17b018, 0, 32, 0x400],
        'pxd_cause_get': [0x16019c, 0, 32, 0x200],
        'pxd_cause_clear': [0x160198, 0, 32, 0x200],
        'primary_bus': [0X15061c, 8, 8, 0],
        'active_host_space': [0X17ff40, 0, 16, 0],
        'cfgwr0_compliter_id': [0X148340, 0, 16, 0x10],  # address for port 0
        'port_state' : [0x177000,0,8,0x100],
        # cuase new
        "pxd_causereg0": [0x16019c, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x160198, 0, 32, 0x200],
        "npi_checks_causereg": [0x14b81c, 0, 32, 0x80],
        "clr_npi_checks_causereg": [0x14b818, 0, 32, 0x80],
        "cause_fatal_causereg": [0x17b0dc, 0, 14, 0x400],
        "clr_cause_fatal_causereg": [0x17b0d8, 0, 14, 0x400],

    }

class crspace_negev_pcore0:
    REGISTERS = {
        'current_link_speed': [0x157064, 0, 3, 0x100],
        'speed_en': [0x157034, 12, 4, 0x100],
        'fw_directed_speed_change': [0x157010, 1, 1, 0x100],
        'negotiated_link_width': [0x157064, 8, 6, 0x100],
        'fsm_0_speed_en': [0x157064, 12, 3],
        # cause
        'rx_errors_get': [0x15b01c, 0, 32, 0x200],
        'rx_errors_clear': [0x15b018, 0, 32, 0x200],
        'pxd_cause_get': [0x14019c, 0, 32, 0x200],
        'pxd_cause_clear': [0x140198, 0, 32, 0x200],
        'primary_bus': [0X11041c, 8, 8],
        'active_host_space': [0X17ff40, 0, 16 , 0],
        'cfgwr0_compliter_id': [0X108340, 0, 16, 0x08],  # address for port 0
        'port_state' : [0x157000,0,8,0x100],
        # cuase new
        "pxd_causereg0": [0x14019c, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x140198, 0, 32, 0x200],
        "npi_checks_causereg": [0x10b81c, 0, 32, 0x80],
        "clr_npi_checks_causereg": [0x10b818, 0, 32, 0x80],
        "cause_fatal_causereg": [0x15b07c, 0, 16, 0x200],
        "clr_cause_fatal_causereg": [0x15b078, 0, 16, 0x200],

    }

class crspace_negev_pcore1:
    REGISTERS = {
        'current_link_speed': [0x1d7064, 0, 3, 0x100],
        'speed_en': [0x1d7034, 12, 4, 0x100],
        'fw_directed_speed_change': [0x1d7010, 1, 1, 0x100],
        'negotiated_link_width': [0x1D7064, 8, 6, 0x100],
        'fsm_0_speed_en': [0x1D7064, 12, 3],
        # cause
        'rx_errors_get': [0x1db01c, 0, 32, 0x200],
        'rx_errors_clear': [0x1db018, 0, 32, 0x200],
        'pxd_cause_get': [0x1c019c, 0, 32, 0x200],
        'pxd_cause_clear': [0x1c0198, 0, 32, 0x200],
        'primary_bus': [0X19061c, 8, 8, 0],
        'active_host_space': [0X1dff40, 0, 16, 0],
        'cfgwr0_compliter_id': [0X188340, 0, 16, 0x08],  # address for port 0
         'port_state' : [0x1d7000,0,8,0x100],
        # cuase new
        "pxd_causereg0": [0x1c019c, 0, 32, 0x200],
        "clr_pxd_causereg0": [0x1c0198, 0, 32, 0x200],
        "npi_checks_causereg": [0x18b81c, 0, 32, 0x80],
        "clr_npi_checks_causereg": [0x18b818, 0, 32, 0x80],
        "cause_fatal_causereg": [0x1db07c, 0, 16, 0x200],
        "clr_cause_fatal_causereg": [0x1db078, 0, 16, 0x200],
    }