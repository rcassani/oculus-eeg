import mules       # The signal acquisition toolbox we'll use (MuLES)
import os
import numpy as np
import time
#import matplotlib.pyplot as plt
from HRdetector import HeartRateDetector
from EBdetector import EyesBlinkDetector
from WBdetector import WaveBandDetector
from experiment import tone, pause, TcpClient


class EEGBasicDemo:
    def __init__(self, bufsize):
        """ parameters:
        bufsize : size of the buffer in seconds
        """
        # eeg signal buffer: needs data parameters to be initialized
        self.data = []
        self.bufsize = bufsize # size of buffer
        
        self.HRdetector = HeartRateDetector()
        self.WBdetector = WaveBandDetector()
        self.EBdetector = EyesBlinkDetector()
    
    def connection(self):
        """ This function use MulesClient class to connect to the Mules server. Mules server will provides
        the eeg signal recorded from epoc sensors. The function also start a connection with an Unity
        server application. """
        ## 1) Connection with Mules and retrieve EEG data parameters
        # Creates mules_client object
        if hasattr(self, 'mules_client'):
            print('Connection already established')
        else:
            self.mules_client = mules.MulesClient('localhost', 30000) # connects with MuLES at 127.0.0.1 : 30000
            
        # Retrieve recording information
        self.device_name = self.mules_client.getdevicename()   # get device name
        self.channel_names = self.mules_client.getnames()  # get channel names
        self.fs = 1.0 * self.mules_client.getfs()  # get sampling frequency
        print('fs= ', self.fs)
            
        self.nb_chl = len(self.channel_names)  # Number of channel
        self.data = np.zeros((int(self.bufsize*self.fs), self.nb_chl)) # init buffer
        
        # TCP Client for Unity
        self.unity = TcpClient('localhost', 40000) 
        self.unity.connect()
    
    """ return heart pic positions and heart rate average """
    def HRdetection(self):
        # heart rate detection
        r_peaks = self.HRdetector.r_peaks_detection(self.data, self.fs)
        # Means and global mean of r_peaks
        (r_mean, r_peaks_moy) = self.HRdetector.mean_peaks(4, r_peaks)
        print('global mean: ', str(r_mean))
        return (r_mean, r_peaks_moy)
    
    """ return average and a factor of asymetry power of each band """
    def WBdetection(self):
        avg_pwrBand = self.WBdetector.FreqBandPower(self.data, self.fs)
        asym_pwrBand = self.WBdetector.FreqBandAsymmetry(self.data, self.fs)
        
        return (avg_pwrBand, asym_pwrBand)
        
    """ return: number of eyes blinks and movements per seconde (eye blink rate) """
    def EBdetection(self, idxnewsig=0):
        blinkdetected = False
        
        (peaks_clig, peaks_move_l, peaks_move_r, peaks_move_deb, peaks_move_fin) = self.EBdetector.EyeEventdetection(self.data, self.fs)
        """print('peaks_clig', peaks_clig)
        print('peaks_move_l', peaks_move_l)
        print('peaks_move_r', peaks_move_r)
        print('peaks_move_deb', peaks_move_deb)
        print('peaks_move_fin', peaks_move_fin)"""
        
        lastEBpeaks = [i for i in peaks_clig if i>= idxnewsig]
        
        if(len(lastEBpeaks) > 0):
            blinkdetected = True
        
        datalen = len(self.data)/self.fs # length of data (in seconds)
        blinkRythm = len(peaks_clig)/datalen;
        moveRythm  = (len(peaks_move_l)+len(peaks_move_r))/datalen;
        
        return (blinkRythm, moveRythm)
    
        
    def start_experiment(self):
        """ This function collect eeg data, find heart peaks and compute heart rate mean.
        The resulting heart rate mean is then sent to the unity server application.
        Steps:
        1) Connection with Mules and Unity server
        2) Waiting for user response to continue
        Infinite loop
        3) Collect eeg data from the mules buffer
        4) Add new eeg data in the buffer
        5) Start specific analysis
        6) Send computed heart rate means to unity server application
        """
        # 1) Connection with Mules and Unity server
        self.connection()

        # 2) Waiting for user response
        #input('press a key')
        self.mules_client.flushdata() # flush mules buffer
        tone(f=500, d=500)
        
        startTime = time.time()
        while(True):
            # 3) Collect eeg data from the mules buffer
            new_eeg = self.mules_client.getalldata()
            print('new ', new_eeg.shape[0], 'samples read')
            
            # 4) Add new eeg data in the buffer
            addlen = new_eeg.shape[0]
            buflen = self.data.shape[0]
            self.data = np.concatenate([self.data[addlen:,], new_eeg])
            #self.data = new_eeg
            print('samples (buffer) (added): ', buflen, ' ', addlen)
            
            # 5) Start specific analysis
            (r_mean, r_peaks_moy) = self.HRdetection()
            (avg_pwrBand, asym_pwrBand) = demo.WBdetection()
            #print('Average band power (relative)', avg_pwrBand)
            #print('Asymmetry of frontal bands', asym_pwrBand)
            (blinkRythm, moveRythm) = demo.EBdetection()
            
            # Wait at least 5 secondes before sending next data
            workingTime = time.time()-startTime;
            remainingTime = 5 - workingTime;
            print(remainingTime)
            if(remainingTime > 0):
                pause(remainingTime)
            
            startTime = time.time()
            
            # 6) send data to unity server application
            self.unity.writeInt32(int(r_mean)) # global heart rate mean
            self.unity.writeInt32(int(blinkRythm*10000)) # eye blink rate (nb blink per sec)
            #self.unity.writeInt32(int(moveRythm *10000)) # eye move rate (nb move per sec)
            # alpha, beta, delta, theta, gamma power mean
            self.unity.writeInt32(int(avg_pwrBand[0]*10000))
            self.unity.writeInt32(int(avg_pwrBand[1]*10000))
            self.unity.writeInt32(int(avg_pwrBand[2]*10000))
            self.unity.writeInt32(int(avg_pwrBand[3]*10000))
            self.unity.writeInt32(int(avg_pwrBand[4]*10000))
            
            
            
    def load_data_from_txt(self, nfile, fs, intl=[]):
        """ Use this function to load eeg signal in the buffer.
        Useful for offline tests.
        Txt file format:
        	value1_chl1 value1_chl2 value1_chl3
        	value2_chl1 value2_chl2 value2_chl3
        	... ... ...
        """
        self.fs = fs
        #os.chdir('C:\\Users\\student\\Documents\\Oculus EEG conference\\final test')
        #os.chdir('C:\\Users\\Olivier\\Documents\\Stage MuSAE lab\\Projet Oculus-EEG\\Wave Band')
        os.chdir('C:\\Users\\Olivier\\Documents\\Stage MuSAE lab\\Projet Oculus-EEG\\Code final')
        self.data = np.loadtxt(nfile);
        
        if(intl):
            self.data = self.data[intl[0]*fs : intl[1]*fs ]
            
        print(self.data.dtype);
    

#from util import afficher

if __name__ == "__main__":
    
    demo = EEGBasicDemo(bufsize=10)
    
    ## Offline test: loading data from a file
    # Heart rate
    """demo.load_data_from_txt('HRdata.txt', 128)
    print(demo.HRdetection())"""
    
    # Eyes Blinks and Movements
    """demo.load_data_from_txt('record.txt', 128)
    (blinkRythm, moveRythm) = demo.EBdetection()
    print('nb clignement/seconde', blinkRythm)
    print('nb mouvement/seconde', moveRythm)"""
    
    # Neural waves bands
    """demo.load_data_from_txt('recordWB3.txt', 128)
    (avg_pwrBand, asym_pwrBand) = demo.WBdetection()
    print('Average band power (relative)', avg_pwrBand)
    print('Asymmetry of frontal bands', asym_pwrBand)"""
    
    ## Online test: Connection to mules server
    demo.start_experiment()



