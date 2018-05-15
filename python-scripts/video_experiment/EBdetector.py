""" Eyes blinking detector """
import numpy as np
from util import coeffbandpass_filter, filtfilt, peaks_detection


class EyesBlinkDetector:
        def __init__(self):
            # channels
            self.chl_hl = 13 # horizontal left
            self.chl_hr = 5  # horizontal right
            self.chl_vl = 0  # vertical left
            self.chl_vc = 0  # vertcial center
            self.chl_vr = 0  # vertical right

        def EBdetection(self, data, fs):
            
            # Selection des channels
            x_hl = data[:, self.chl_hl]
            x_hr = data[:, self.chl_hr]
            x_vl = data[:, self.chl_vl]
            x_vc = data[:, self.chl_vc]
            x_vr = data[:, self.chl_vr]
            
            datalen = len(x_hl) # les signaux sont supposés de même taille

            # Filtrage
            bfilter = coeffbandpass_filter(2, 3, 9, 10, fs, 182);
            flt_hl = filtfilt(x_hl, bfilter, datalen)
            flt_hr = filtfilt(x_hr, bfilter, datalen)
            flt_vl = filtfilt(x_vl, bfilter, datalen)
            flt_vc = filtfilt(x_vc, bfilter, datalen)
            flt_vr = filtfilt(x_vr, bfilter, datalen)
            
            # Fusion des channels
            eogH = (flt_hl+flt_hr)/2  # Annule les mouvements horizontaux
            eogV = (flt_vl+flt_vc+flt_vr)/3 # Moyenne des signaux verticaux
            eog = np.sqrt( (eogH**2) + (eogV**2)) # Normalisation L2
            
            # Evaluation du seuil
            seuil = np.max(eog)/2
            
            # Recherche des pics
            (r_peaks_rec, peaks_pos) = peaks_detection(eog, fs, threshold=3, refract_delay=0.2)
            
            # Suppression des pics ayant une amplitude trop faible
            rpeaks = []
            for pos in peaks_pos:
                if(eog(pos) >= seuil):
                    rpeaks = [rpeaks, pos]
            
            return rpeaks
            
        
        def compareSequence(self, tabs, latence):
            """ Cet algorithme trouve les valeurs communes a plusieurs tableaux.
            Il est utile pour differencier les pics causé par un clignement des
            yeux de ceux causé par le bruit. En effet un pic causé par le clignement
            des yeux est présent au même moment sur toutes les signaux frontaux. """
            nbchl = len(self.chl_eb)
            
            index = np.zeros(nbchl, dtype=int) # index arrays
            endtabs = np.zeros(nbchl, dtype=int) # index size arrays
            
            # Tableau de pics communs à remplir
            EyeBlinkPos = []
            
            # Remplissage du tableau endtabs
            for ichl in range(nbchl):
                endtabs[ichl] = tabs[ichl].shape[0]-1 # indice final du tableau
                print('chl: ' + str(ichl) + ' size: ' + str(endtabs[ichl]))
                print(tabs[ichl])
            
            endtabsreached = False
            
            # Debut de la recherche
            while(not endtabsreached):
                endtabsreached = True # Contraire à démontrer
                
                # Recherche de la valeur la plus petite
                minval = tabs[0][index[0]]
                minidx = 0
                print('Recherche du minimun')
                for ichl in range(nbchl):
                    # tableau de pic channel n°ichl
                    i = index[ichl] # indice actuel sur ce tableau
                    print('i: ' + str(i) + 'ichl: ' + str(ichl))
                    # tabs[ichl][i] represente la valeur actuel sur ce tableau
                    if minval > tabs[ichl][i]:
                        minval = tabs[ichl][i]
                        minidx = ichl # tableau ayant la plus petite valeur
                
                print('tabs[' + str(minidx) + ']['+str(index[minidx])+'] = ' + str(minval))
                
                
                print('Verification des egalités')
                """ Toutes les channels doivent avoir detecté un pic a la même
                position pour considérer ce pic comme un clignement des yeux. """
                equlcounter = 0
                for ichl in range(nbchl):
                    i = index[ichl]  # indice actuel de la channel
                    curval = tabs[ichl][i] # valeur courante de la channel
                    print('tab[' + str(ichl) + ']['+str(i)+'] = ' + str(curval))
                    #print('abs: ' + str(abs(minval-curval)) + ' lat: ' + str(latence))
                    # Comparaison avec le minimun courant
                    if( abs(minval-curval) < latence):
                        # Le pic est à la même position
                        # Incrementation du compteur
                        equlcounter = equlcounter + 1
                        # Pic comptabiliser: Passage au pic suivant pour cette channel
                        if index[ichl] < endtabs[ichl]:
                                index[ichl] = index[ichl] + 1
                                endtabsreached = False # Une incr. a été possible -> l'algo n'a pas terminer
                    #else:
                        # Le pic est trop avancé pour le minimun actuel
                        
                print('counter: ' + str(equlcounter))
                
                if(equlcounter >= int(nbchl*0.8)):
                    # Position du pic commun à toutes les channels
                    print('Ajout du pic')
                    EyeBlinkPos.append(minval);
                
                
                
                print(endtabsreached)
                input('continuer')
                
            return EyeBlinkPos
                        
                
                
            