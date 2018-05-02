""" Eyes blinking detector """
import numpy as np
from util import removeBaseline, peaks_detection


class EyesBlinkDetector:
        def __init__(self):
            # channels
            self.chl_hl = 13 # horizontal left
            self.chl_hr = 16  # horizontal right
            self.chl_vl = 5  # vertical left
            self.chl_vc = 12  # vertcial center
            self.chl_vr = 15  # vertical right

        def EyeEventdetection(self, data, fs):
            # Selection des channels
            Hleft = data[:, self.chl_hl]
            Hright = data[:, self.chl_hr]
            Vleft = data[:, self.chl_vl]
            Vcenter = data[:, self.chl_vc]
            Vright = data[:, self.chl_vr]
            
            datalen = len(Hleft) # les signaux sont supposés de même taille
            
            t = np.arange(datalen)/fs;
            
            # Pré-traitement: Soustraction de la baseline par approx. poly.
            print('Suppression baseline par approx. poly.')
            Hleft = removeBaseline(t, Hleft)
            Hright = removeBaseline(t, Hright)
            Vleft = removeBaseline(t, Vleft)
            Vcenter = removeBaseline(t, Vcenter)
            Vright = removeBaseline(t, Vright)
            
            # Calcul des signaux intermedieres
            Hoppos = np.abs(Hleft - Hright);
            Hunion = np.abs(Hleft + Hright);
            Hsum = Hoppos + Hunion;
            
            # Calcul des signaux finaux
            EogH = Hsum/2;
            EogV = (Vleft+Vcenter+Vright)/3;
            EogV = np.maximum(EogV, 0);
            Eog = np.sqrt(np.power(EogH,2) + np.power(EogV,2));
            
            # Detection des pics
            print('Detection des pics');
            (_unused, peaks_ix) = peaks_detection(Eog, fs, threshold=1, refract_delay=0)
            
            # Fusion des pics du même pic principal
            # Pour chaque pic, recherche du pic de plus grande amplitude au alentour de
            # 'dureeMax' échantillons. Si tout les pics alentour d'un pic sont
            # inferieur en amplitude, le pic se reference lui-même.
            dureeMax = 1.0*fs; # 1 seconde
            nbpeaks = peaks_ix.size;
            pic_max = np.zeros(nbpeaks);
            
            for i in range(nbpeaks):
                idx = peaks_ix[i];
                
                jmax = i;
                valmax = Eog[idx];
                ## Recherche du max
                # Recherche en arriere
                j=i;
                while( j>1 and (idx-peaks_ix[j]) < dureeMax):
                    if(valmax < Eog[peaks_ix[j]]):
                        valmax = Eog[peaks_ix[j]];
                        jmax = j;
                    j=j-1;
                
                # Recherche en avant
                j=i;
                while( j<nbpeaks and (peaks_ix[j]-idx) < dureeMax):
                    if(valmax < Eog[peaks_ix[j]]):
                        valmax = Eog[peaks_ix[j]];
                        jmax = j;
                    j=j+1;
                
                # Reference vers le pic maximun
                pic_max[i] = jmax;

            # Sauvegarde des pics qui s'autoreference comme pic maximun
            pic_retenu = [];
            for i in range(nbpeaks):
                if(pic_max[i] == i):
                    pic_retenu = np.append(pic_retenu, peaks_ix[i]);
            peaks_ix = pic_retenu;
            
            
            print('Determination de la nature de chaque pic')
            # Differentiation entre clignement et mouvement (droite/gauche)
            peaks_clig = np.array([]);
            peaks_move_r = np.array([]);
            peaks_move_l = np.array([]);
            
            peaks_move_deb = np.array([]);
            peaks_move_fin = np.array([]);
            
            for i in range(peaks_ix.size):
                idx = int(peaks_ix[i]);
                if(Hunion[idx] > Hoppos[idx]):
                    peaks_clig = np.append(peaks_clig, idx);
                else:
                    # Determination du sens
                    if(Hleft[idx]>Hright[idx]):
                        peaks_move_l = np.append(peaks_move_l, idx);
                    else:
                        peaks_move_r = np.append(peaks_move_r, idx);
                    
                    # Determination de la durée
                    maxval = Hsum[idx];
                    maxidx = idx;
                    # Recherche en arriere
                    j=maxidx;
                    while( j > max(1,       maxidx-dureeMax/2) and Hsum[j] > maxval*0.5):
                        j=j-1;
                    debpic = j;
                    
                    j=maxidx;
                    while( j < min(datalen, maxidx+dureeMax/2) and Hsum[j] > maxval*0.5):
                        j=j+1;
                    finpic = j;

                    peaks_move_deb = np.append(peaks_move_deb, debpic);
                    peaks_move_fin = np.append(peaks_move_fin, finpic);
                    
            return (peaks_clig, peaks_move_l, peaks_move_r, peaks_move_deb, peaks_move_fin)
        
        
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
                        
                
                
            