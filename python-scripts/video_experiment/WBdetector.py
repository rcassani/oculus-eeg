# -*- coding: utf-8 -*-
import numpy as np

class WaveBandDetector:
    def __init__(self):
        self.chl_wb = [13, 5, 15, 8, 7, 11, 4, 14, 3, 10, 6] # index of channel
        self.chl_frontal_left = 13
        self.chl_frontal_right = 5
        # Frequency bands of neural activity
        self.waveband = np.array([[7.5, 12.5], # alpha waves
                                  [13, 30],    # beta waves
                                  [1, 4],      # delta waves
                                  [4, 8],      # theta waves
                                  [30, 55]])   # low gamma waves

    def FreqBandAsymmetry(self, data, fs):
        """
        1) Compute PSD of left and right frontal eeg sensor
        2) Sum 
        """
        nb_wbd = self.waveband.shape[0] # Number of wave bands
        siglen = data.shape[0]
        egy_bands_left = np.zeros(nb_wbd)
        egy_bands_right = np.zeros(nb_wbd)
        
        # windowing data with Hamming window
        win = np.hamming(siglen)
        #print(win[3000:3050])
        
        # rms of hamming window
        win_rms = np.sqrt(np.sum(win**2)/siglen)
        

        (psd_left, f_delta) = self.computePSD(data[:, self.chl_frontal_left], siglen, fs, win, win_rms)
        (psd_right, f_delta) = self.computePSD(data[:, self.chl_frontal_right], siglen, fs, win, win_rms)
    
        # power average of each bands for current channel
        for iband, band in enumerate(self.waveband):
            start_idx = int(band[0]/f_delta)
            end_idx   = int(band[1]/f_delta)
            
            # sum of power of this band
            fsum_left = np.sum(psd_left[start_idx:end_idx])*f_delta
            fsum_right = np.sum(psd_right[start_idx:end_idx])*f_delta
            # add power average of this channel
            egy_bands_left[iband] = fsum_left
            egy_bands_right[iband] = fsum_right
            
        
        # Normalization
        egy_bands_left = egy_bands_left / np.sum(egy_bands_left)
        egy_bands_right = egy_bands_right / np.sum(egy_bands_right)
				
        # ratio between left and right frontal signal for each power band
        egy_bands_ratio = egy_bands_left/egy_bands_right
        
        return egy_bands_ratio
    
    
    
    def FreqBandPower(self, data, fs):
        """
        1) Sum of frequency for each band for each channel
        2) Mean of respective frequency band for each channel
        """
        nb_chl = len(self.chl_wb) # Number of channels
        nb_wbd = self.waveband.shape[0] # Number of wave bands
        siglen = data.shape[0]
        megy_bands = np.zeros(nb_wbd)
        
        # windowing data with Hamming window
        win = np.hamming(siglen)
        
        # rms of hamming window
        win_rms = np.sqrt(np.sum(win**2)/siglen)

        # Power Spectrum for each channel
        for chl_idx in self.chl_wb:
            # Selecting current channel signal
            sig = data[:, chl_idx]
            
            (psd, f_delta) = self.computePSD(sig, siglen, fs, win, win_rms)
    
            # power average of each bands for current channel
            for iband, band in enumerate(self.waveband):
                start_idx = int(band[0]/f_delta)
                end_idx   = int(band[1]/f_delta)
                
                # sum of this band
                fsum = np.sum(psd[start_idx:end_idx])
                # power average of this band
                fsum = fsum *f_delta
                # add power average of this channel
                megy_bands[iband] = megy_bands[iband] + fsum
				
        # average of bands power of all channels
        megy_bands = megy_bands / nb_chl
        
        # Normalization
        megy_bands = megy_bands / np.sum(megy_bands)
        
        return megy_bands
    
    
    
    def computePSD(self, sig, siglen, fs, win, win_rms):
        
        # Applying window to the signal
        sig = sig*win
        
        # fft
        fsig = np.fft.fft(sig)
        fsig = fsig[:int(siglen/2)] # we only need half of the coefficients
        
        # Spectrum scaled with window rms
        fsig = fsig / win_rms
        
        
        # Power spectrum
        pfsig = fsig * np.conj(fsig)
        pfsig = np.abs(pfsig) / (siglen**2) # abs to discard null imaginery part
        
        # As we only taken half of the coefficient, all power frequency component
        # is doubled except DC
        pfsig[1:] = pfsig[1:]*2
        # frequency axis step
        f_delta = (fs/siglen)
        
        # scale PSD with the frequency step
        # pfsig array represents power for each f and f+f_delta interval
        # It can be considered as power per step of f_delta but we want power
        # for f frequency so we divide by the step f_delta. Unit: power^2/Hz (discrete)
        psd = pfsig / f_delta
        
        return (psd, f_delta)
        
    
    