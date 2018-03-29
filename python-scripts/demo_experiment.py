# -*- coding: utf-8 -*-
"""
Template for the DemoScene
"""

from mules import MulesClient
from experiment import *
import subprocess
import numpy as np

if __name__ == "__main__":
    ###################    
    ## Parameters
    ###################    
    mules_path = r'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe'

    # Number of DEVICE in MuLES config.ini file
    mules_eeg_device = 'DEVICE01'

    ###################    
    ## Execute other software
    ###################
    # Execute MuLES
    # subprocess.Popen(mules_path + ' -- "' + mules_eeg_device + '"' + ' PORT=30000 LOG=T TCP=T')
    # Pause for the Experimenter to confirm the quality of the Epoc electrodes
    #pause(20)
    
    ###################    
    ## TCP/IP clients
    ###################
    # TCP Client for MuLES
    # mules_eeg = MulesClient('localhost', 30000)
    unity = TcpClient('localhost', 40000) 
    unity.connect()

    # Wait for Unity App
    pause(3)

    for ix in range(1000):
        # Tone
        # tone(500, 500)
        # Send Int32 to Unity with HR
        unity.writeInt32(ix + 20) 
        pause(2)
             
    ###################    
    ## End Experiment
    ################### 
    unity.writeInt32(11)
    unity.close()