# -*- coding: utf-8 -*-
"""
Automates the SSVEP experiment
"""

from mules import MulesClient
from experiment import *
import subprocess

if __name__ == "__main__":    
    mules_path = 'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe'

    # Number of DEVICE in MuLES config.ini file
    mules_eeg_device = 'DEVICE01'

    # Execute MuLES
    subprocess.Popen(mules_path + ' -- "' + mules_eeg_device + '"' + ' PORT=30000 LOG=T TCP=T')
    pause(5)
    
    # TCP Client for MuLES
    mules_eeg = MulesClient('localhost', 30000)
    pause(2)
    
    # Get data
    mules_eeg.flushdata()
    pause(15)  
    X = mules_eeg.getalldata()
    Y = mules_eeg.getdata(2)
    
    # End MuLES
    mules_eeg.kill()
 