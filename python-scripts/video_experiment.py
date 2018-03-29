# -*- coding: utf-8 -*-
"""
Automates the SSVEP experiment
"""

from mules import MulesClient
from experiment import *
import subprocess
import numpy as np

if __name__ == "__main__":
    ###################    
    ## Parameters
    ###################
    np.random.seed(40)
    videos = np.arange(6) + 1
    videos = np.random.permutation(videos)
    time_between = 5;
    
    mules_path = r'C:\Program Files (x86)\MuSAE_Lab\MuLES\mules.exe'

    # Number of DEVICE in MuLES config.ini file
    mules_eeg_device = 'DEVICE01'
    mules_ecg_device = "DEVICE07"

    ###################    
    ## Execute other software
    ###################
    # Execute MuLES
    subprocess.Popen(mules_path + ' -- "' + mules_eeg_device + '"' + ' PORT=30000 LOG=T TCP=T')
    # Execute MuLES
    subprocess.Popen(mules_path + ' -- "' + mules_ecg_device + '"' + ' PORT=31000 LOG=T TCP=T') 
    # Pause for the Experimenter to confirm the quality of the Epoc electrodes
    pause(20)
    

    ###################    
    ## TCP/IP clients
    ###################
    # TCP Client for MuLES
    mules_eeg = MulesClient('localhost', 30000)
    pause(2)
    mules_ecg = MulesClient('localhost', 31000)
    # TCP Client for Unity
    unity = TcpClient('localhost', 40000) 
    unity.connect()

    # Wait for Unity App
    pause(3)

    for video in videos:
        # Tone start
        tone(500, 500)
        pause(1)
        
        # Send command to Unity
        unity.writeInt32(video) 
        # Send trigger to MuLES
        mules_eeg.sendtrigger(video)
        mules_ecg.sendtrigger(video)
        # Receive command that video ended
        video_end = unity.readInt32()
        # Send trigger to MuLES
        mules_eeg.sendtrigger(video)
        mules_ecg.sendtrigger(video)
        # Pause between videos
        pause(time_between)

    ###################    
    ## End Experiment
    ################### 
    mules_eeg.kill()
    mules_ecg.kill()
    unity.writeInt32(66)
    unity.close()