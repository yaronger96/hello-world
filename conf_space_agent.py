import os
import shutil
import glob
import tarfile
import argparse
import sys
import subprocess
import datetime
import operator
import time
from collections import namedtuple


class conf_space_agent:

    FIRST_N_CAP_PTR = 0x34
    FIRST_E_CAP_PTR = 0x100


    def __init__(self , bdf):
        self.cap_address_n = {}
        self.cap_address_e = {}
        self._bdf = bdf
        self._server = Monostate()
        self.init_capbilities_table()
        # self.print_capalities()

    def getBdf(self):
        return self._bdf

    def exe_cmd(self , cmd, print_cmd = False):
        (status, val) = self._server.exec_agent.execute_job_and_return_returncode_and_output(cmd, print_cmd=print_cmd)
        return status , val

    def init_capbilities_table(self):
        ## Normal Configuration space
        self.cap_address_n[0] = 0 #PCI_HEADER_NORMAL
        cmd = "setpci -s " + self._bdf + " " + str(hex(self.FIRST_N_CAP_PTR)) + ".w"
        (status, val) = self.exe_cmd(cmd , False)
        nextPtr = int(val,16)
        while (nextPtr != 0):
            cmd = "setpci -s " + self._bdf + " " + str(hex(nextPtr)) + ".w"
            (status, val) = self.exe_cmd(cmd , False)
            foundId = int(val, 16) & 0xff
            self.cap_address_n[foundId] = nextPtr
            nextPtr = int(val,16) >> 8

        ## Extended Configuration space
        nextPtr = self.FIRST_E_CAP_PTR
        while (nextPtr != 0):
            cmd = "setpci -s " + self._bdf + " " + str(hex(nextPtr)) + ".l"
            (status, val) = self.exe_cmd(cmd)
            foundId = int(val, 16) & 0xffff
            self.cap_address_e[foundId] = nextPtr
            nextPtr = int(val, 16) >> 20

    def read_bits_from_reg(self, regVal , bitLoc, size):
        mask = (1 << size ) - 1
        return (regVal >> bitLoc ) & mask;

    def read_capbilities(self, capID , isExtended, offset, bit_loc, size):
        reg_offset = (self.cap_address_e[capID] if isExtended else self.cap_address_n[capID]) + offset
        aligned_offset = reg_offset & 0xffffffc #get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, val) = self.exe_cmd(cmd, print_cmd=False)
        val = (int(val ,16)  >> ((reg_offset%4) * 8))
        bitsVal = self.read_bits_from_reg(val, bit_loc, size)
        return  bitsVal
    
    def read_header(self, offset, bit_loc, size):
        aligned_offset = offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, val) = self.exe_cmd(cmd, print_cmd=False)
        val = (int(val, 16) >> ((offset % 4) * 8))
        bitsVal = self.read_bits_from_reg(val, bit_loc, size)
        return bitsVal

    def write(self, capID, isExtended, offset, bit_loc, size , value):
        reg_offset = (self.cap_address_e[capID] if isExtended else self.cap_address_n[capID]) + offset
        aligned_offset = reg_offset & 0xffffffc  # get to the near by long word address
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, org_val) = self.exe_cmd(cmd, print_cmd=False)
        bit_loc_aligned = bit_loc + ((reg_offset%4) * 8)
        reset_mask = ((1 << size ) -1 ) << bit_loc_aligned
        new_val = ( int(org_val,16) & ~reset_mask ) | (value << bit_loc_aligned)
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l=" + str(hex(new_val))
        status = self.exe_cmd(cmd, print_cmd=False)
        cmd = "setpci -s " + self._bdf + " " + str(hex(aligned_offset)) + ".l"
        (status, read_val) = self.exe_cmd(cmd, print_cmd=False)
        return read_val

    def print_capalities(self):
        print ('{:*^30}').format("  BDF : "+self._bdf+"  ")
        print ('{: ^8}'.format("CapID") + " | " + '{: ^8}'.format("offset") + " | "+'{: ^8}'.format("Extended"))
        print ('{:-^30}').format("")
        for k in sorted(self.cap_address_n.keys()):
            print ('{: ^8}'.format(hex(k)) + " | " +
                   '{: ^8}'.format(hex(self.cap_address_n[k]))+ " | " +
                   '{: ^8}'.format("No"))
        for k in sorted(self.cap_address_e.keys()):
            print ('{: ^8}'.format(hex(k)) + " | " +
                   '{: ^8}'.format(hex(self.cap_address_e[k]))+ " | " +
                   '{: ^8}'.format("Yes"))

# def speed_change_example(DSConf , USConf , speed):
#     DSConf.print_capalities()
#     link_speed  = hex(DSConf.read(0x10, False, 0x12, 0, 4))
#     print "current Link speed" , link_speed
#     print "Changing target link speed to Gen"+speed
#     link_target_updated = USConf.write(0x10, False, 0x30, 0, 4, int(speed))
#     print "Executing disable enable flow"
#     USConf.write(capID=0x10, isExtended=False, offset=0x10, bit_loc=4, size=1, value=1)
#     time.sleep(50e-3)
#     USConf.write(0x10, False, 0x10, 4, 1, 0)
#     time.sleep(1)
#     link_speed = hex(DSConf.read(0x10, False, 0x12, 0, 4))
#     print "current Link speed", link_speed , ("PASSED" if int(speed) == int(link_speed, 16) else "FAILED")

if __name__ == "__main__":
    DSConf = conf_space_agent(sys.argv[1])
    USConf = conf_space_agent(sys.argv[2])
    # speed_change_example(DSConf ,USConf , sys.argv[3])
