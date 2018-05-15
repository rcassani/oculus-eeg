# -*- coding: utf-8 -*-
""" util.py provide tools function for analysis and measurement """
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

def coeffbandpass_filter(lcut1, lcut2, hcut1, hcut2, fs, n):
    """
    Method used to design a bandpass filter
    
    Parameters:
    data : eeg signal to filter
    
            *__________*
    	     /|          |\
    	    / |          | \
    	   /  |          |  \
    ___*/   |          |   \*____
    lcut1  lcut2     hcut1  hcut2
    
    lowcut1, lowcut2, highcut1, highcut2 : frequency band of the fir filter
    fs : sampling frequency
    n : number of iteration for the Remez algorithm
    """
    low1 = lcut1 / fs
    low2 = lcut2 / fs
    high1 = hcut1 / fs
    high2 = hcut2 / fs
    b = signal.remez(n, [0, low1, low2, high1, high2, 0.5], [0, 1, 0])
    #print(b)
    
    freq, response = signal.freqz(b)
    ampl = np.abs(response)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.semilogy(fs*freq/(2*np.pi), ampl, 'b-') # freq in Hz
    
    return b


def filtfilt(self, data, datalen, bfilter):
    ext_data = np.concatenate([np.flip(data,0), data])
    flt_data = signal.lfilter(bfilter, [1], ext_data, axis=0)
    flt_data = flt_data[datalen:]



def peaks_detection(self, data, fs, threshold=3, refract_delay=0.3):
        """ Pan and Tompkins algorithm to detect heart peaks position in an eeg signal
        refract_delay: minimal time betweeb peaks in seconde (typical 300 ms for heart
        rate detection """

        h, axarr = plt.subplots(4, sharex=True)
        h.canvas.set_window_title('EEG data from: ' + 'epoc' + '. Electrode: ' + str(7) )
        
        # Remove dc (only plot purpose)
        data_len = data.shape[0]
        data = data - np.mean(data)
        
        t = np.arange(0,data_len) / fs
        axarr[0].plot(t, data)
        
        # Only keep positive part of the signal
        pos_data = np.where(data >= 0, data, 0)
        axarr[2].plot(t, pos_data)
        
        # Square signal
        sqr_data = np.square(pos_data)
        axarr[3].plot(t, sqr_data)
        
        # Thresholding
        std_data = np.std(sqr_data)
        thr = threshold * std_data
        thr_indice = sqr_data <= thr
        sqr_data[thr_indice] = 0
        axarr[4].plot(t, sqr_data)
        
        plt.show()
        
        # Derivative
        sft_sqr_data = np.concatenate((np.zeros((1)), sqr_data[:-1]))
        diff_data = sqr_data - sft_sqr_data
        
        # finding peaks
        ts = 1/fs
        r_peaks_rec = []
        peaks_pos = []
        prev_idx_peak = 0
        last_sign = 0 # 0 -> positive; 1 -> negative
        #refract_delay = 0.3 # for heart rate detection
        
        
        for i in range(diff_data.shape[0]):
            # positive -> negative = peak
            if diff_data[i] < 0:
                if last_sign == 0:
                    # New peak detected
                    # Is the refractory delay between previous peak respected ?
                    r_peak = (i - prev_idx_peak)*ts
                    #print('r_peak ', r_peak)
                    last_sign = 1
                    if(r_peak > refract_delay):
                        prev_idx_peak = i
                        #print('index: ', i)
                        r_peaks_rec = np.concatenate([r_peaks_rec, [r_peak]]) # Take in account this peak
                        peaks_pos = np.concatenate([peaks_pos, [i]])
                    #else:
                        # delay too small: Wait for next peak
                        # print('delai insuffisant')
                #else
                    #still negative: do nothing
            else:
                # positive sign
                last_sign = 0
        
        return (r_peaks_rec, peaks_pos)
    
    

def afficher(data, fs):
    
    datadim = data.shape
    
    if(len(datadim) > 1):
        datalen = datadim[0]
        nbchl = datadim[1]
        
        h, axarr = plt.subplots(nbchl, sharex=True)
        h.canvas.set_window_title('Affichage des signaux')

        t = np.arange(0,datalen) / fs
        
        for i in range(nbchl):
            axarr[i].plot(t, data[:, i])
        
    else:
        h, axarr = plt.subplots(1)
        h.canvas.set_window_title('Affichage du signal')
        
        axarr.plot(t, data)
    
    plt.show()


if __name__ == "__main__":
    fs = 128
    ts = 1/fs
    l = 200
    t = np.arange(l)*ts
    sig20 = np.sin(2*np.pi*7*t)
    br = np.sin(2*np.pi*30*t)
    sig = sig20 + br
    
    sigtmp = np.concatenate((sig,sig))
    bfilter = bandpass_filter(2, 3, 9, 10, fs, 100)
    sigflt = signal.lfilter(bfilter, [1], sigtmp, axis=0)
    sigflt = sigflt[l:]
    
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    ax2.plot(t, sig, "r", t, sigflt)    
    
    
    