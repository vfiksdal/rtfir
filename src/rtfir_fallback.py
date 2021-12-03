#
# Pure python fallback for systems without working compilers
#
# This will work well enough for short filters with low sampling rate, but
# is not recommended due to the performance hit compared to the compiled 
# counterparts.
#
import numpy as np
import sys
    
class RTFIR():
    def __init__(self,taps):
        sys.stderr.write('WARNING: You are using the uncompiled fallback for python.\n')
        self.coeff=np.zeros(taps)
        self.buffer=np.zeros(taps)
        self.taps=taps

    def GetCoefficients(self):
        return self.coeff

    def Filter(self,sample):
        for i in range(self.taps-1,0,-1):
            self.buffer[i]=self.buffer[i-1]
        self.buffer[0]=sample
        output=0.0
        for i in range(0,self.taps):
            output+=self.buffer[i]*self.coeff[i]

        return output


class RTFIR_lowpass(RTFIR):
    def __init__(self,taps,fcutoff):
        if fcutoff<0 or fcutoff>0.5:
            print('Cutoff frequency must be normalized')
            raise
        RTFIR.__init__(self,taps)
        W=int(taps/2)
        for i in range(-W,W):
            if i==0:
                self.coeff[i+W]=2*fcutoff
            else:
                self.coeff[i+W]=np.sin(2*np.pi*fcutoff*i)/(i*np.pi)

class RTFIR_highpass(RTFIR):
    def __init__(self,taps,fcutoff):
        if fcutoff<0 or fcutoff>0.5:
            print('Cutoff frequency must be normalized')
            raise
        RTFIR.__init__(self,taps)
        W=int(taps/2)
        for i in range(-W,W):
            if i==0:
                self.coeff[i+W]=1-2*fcutoff
            else:
                self.coeff[i+W]=-np.sin(2*np.pi*fcutoff*i)/(i*np.pi)

class RTFIR_bandpass(RTFIR):
    def __init__(self,taps,fclow,fchigh):
        if fclow<0 or fclow>0.5 or fchigh<0 or fchigh>0.5:
            print('Cutoff frequency must be normalized')
            raise
        RTFIR.__init__(self,taps)
        W=int(taps/2)
        for i in range(-W,W):
            if i==0:
                self.coeff[i+W]=((2*np.pi*fchigh)-(2*np.pi*fclow))/np.pi
            else:
                self.coeff[i+W]=(np.sin(2*np.pi*fchigh*i)-np.sin(2*np.pi*fclow*i))/(i*np.pi)

class RTFIR_bandstop(RTFIR):
    def __init__(self,taps,fclow,fchigh):
        if fclow<0 or fclow>0.5 or fchigh<0 or fchigh>0.5:
            print('Cutoff frequency must be normalized')
            raise
        RTFIR.__init__(self,taps)
        W=int(taps/2)
        for i in range(-W,W):
            if i==0:
                self.coeff[i+W]=1+((2*np.pi*fclow)-(2*np.pi*fchigh))/np.pi
            else:
                self.coeff[i+W]=(np.sin(2*np.pi*fclow*i)-np.sin(2*np.pi*fchigh*i))/(i*np.pi)

