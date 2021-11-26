#!/usr/bin/env python3
#
# Script to test realtime fir filters
#
import matplotlib.pyplot as plt
import numpy as np
import sys,rtfir


def chirp(fs_Hz, rep_Hz, f0_Hz, f1_Hz, phase_rad=0):
    # Estimate timing
    T_s=1/rep_Hz
    c=(f1_Hz-f0_Hz)/T_s
    n=int(fs_Hz/rep_Hz)
    t_s=np.linspace(0,T_s,n)

    # Phase, phi_Hz, is integral of frequency, f(t) = ct + f0.
    phi_Hz=(c*t_s**2)/2+(f0_Hz*t_s)
    phi_rad=2*np.pi*phi_Hz
    phi_rad+=phase_rad
    return np.sin(phi_rad)

def fft(unfiltered,filtered,fs,maxf):
    # Calculate fft of unfiltered and filtered data
    N=len(unfiltered)
    T=1.0/fs
    length=int(maxf/(fs/float(N)))
    xf=np.linspace(0.0, 1.0/(2.0*T),int(N/2)+1)[:length]
    unfilteredf=np.abs(np.fft.rfft(unfiltered)[:length])
    filteredf=np.abs(np.fft.rfft(filtered)[:length])
    return unfilteredf,filteredf,xf

# Test setup
span=100.0
fs=1000.0
t=60
taps=64
i=1
while i<len(sys.argv):
    if sys.argv[i]=='--samplerate':
        i+=1
        fs=float(sys.argv[i])
    elif sys.argv[i]=='--length':
        i+=1
        t=float(sys.argv[i])
    elif sys.argv[i]=='--taps':
        i+=1
        taps=int(sys.argv[i])
    elif sys.argv[i]=='--span':
        i+=1
        span=float(sys.argv[i])
    elif sys.argv[i]=='--help':
        print('RTFIR Python Example 1.0')
        print('Tests RTFIR implementation for C++ and python')
        print('Fiksdal(C)2021')
        print('')
        print('Usage: '+sys.argv[0]+'')
        print('')
        print('Options:')
        print('\t--samplerate HZ\tSet sampling frequency in hertz')
        print('\t--length S\tLength of synthesized recording in seconds')
        print('\t--taps N\tNumber of taps for the FIR filter')
        print('\t--span HZ\tLength of frequency sweep to test with in Hz')
        print('')
        exit()
    else:
        print('Invalid parameter: '+sys.argv[i])
        exit()
    i+=1


# Create a frequency sweep of 1-100 Hz
sweep=chirp(fs,1/t,1.0,span)
flow=span/8.0*3.0
fhigh=span/8.0*5.0

# Create lowpass filter
lpf=rtfir.RTFIR_lowpass(taps,flow/fs)

# Create highpass filter
hpf=rtfir.RTFIR_highpass(taps,fhigh/fs)

# Create bandpass filter
bpf=rtfir.RTFIR_bandpass(taps,flow/fs,fhigh/fs)

# Create bandstop filter
bsf=rtfir.RTFIR_bandstop(taps,flow/fs,fhigh/fs)


# Filter chirp
lowpass=np.zeros(len(sweep))
highpass=np.zeros(len(sweep))
bandpass=np.zeros(len(sweep))
bandstop=np.zeros(len(sweep))
for i in range(0,len(sweep)):
    lowpass[i]=lpf.Filter(sweep[i])
    highpass[i]=hpf.Filter(sweep[i])
    bandpass[i]=bpf.Filter(sweep[i])
    bandstop[i]=bsf.Filter(sweep[i])


# Plot FFT data
fig, axs = plt.subplots(2, 2)
unfilteredf,filteredf,xf=fft(sweep,lowpass,fs,span*1.1)
axs[0, 0].plot(xf,unfilteredf)
axs[0, 0].plot(xf,filteredf)
axs[0, 0].set_title('Lowpass')
unfilteredf,filteredf,xf=fft(sweep,highpass,fs,span*1.1)
axs[0, 1].plot(xf,unfilteredf)
axs[0, 1].plot(xf,filteredf)
axs[0, 1].set_title('Highpass')
unfilteredf,filteredf,xf=fft(sweep,bandpass,fs,span*1.1)
axs[1, 0].plot(xf,unfilteredf)
axs[1, 0].plot(xf,filteredf)
axs[1, 0].set_title('Bandpass')
unfilteredf,filteredf,xf=fft(sweep,bandstop,fs,span*1.1)
axs[1, 1].plot(xf,unfilteredf)
axs[1, 1].plot(xf,filteredf)
axs[1, 1].set_title('Bandstop')
for ax in axs.flat: ax.set(xlabel='Frequency [Hz]',ylabel='Magnitude')
for ax in axs.flat: ax.label_outer()
fig.suptitle('Spectrum of filtered chirp\nFlow='+str(flow)+'Hz Fhigh='+str(fhigh)+'Hz Taps='+str(taps)+'\nFs='+str(fs)+'Hz t='+str(t)+'s')
fig.set_size_inches(11.7,8.3)
fig.tight_layout()
plt.savefig('test_fft.png')

