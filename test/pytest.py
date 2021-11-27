#!/usr/bin/env python3
#
# Script to test realtime fir filters
#

import time,sys,random,subprocess,rtfir
import matplotlib.pyplot as plt
import numpy as np

MODE_STDIN=0
MODE_FILE=1
MODE_COEFF=2
MODE_PERF=3

# Generates frequency sweep
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

# Creates FFT's for a dataset
def fft(unfiltered,filtered,fs,maxf):
    # Calculate fft of unfiltered and filtered data
    N=len(unfiltered)
    T=1.0/fs
    length=int(maxf/(fs/float(N)))
    xf=np.linspace(0.0, 1.0/(2.0*T),int(N/2)+1)[:length]
    unfilteredf=np.abs(np.fft.rfft(unfiltered)[:length])
    filteredf=np.abs(np.fft.rfft(filtered)[:length])
    return unfilteredf,filteredf,xf

# Read samples from a file and filter it
def filterfile(filter,fd):
    for line in fd:
        if len(line)>1:
            sample=float(line[:-1])
            print(str(filter.Filter(sample)))

# Test performance of a filter
def filterperf(filter,type):
    # Generate set of random samples
    n=1000
    samples=[]
    for i in range(0,n):
        samples.append(random.randrange(1000)/500.0)

    # Filter dataset ...
    start=time.time()
    for i in range(0,n):
        for j in range(0,n):
            dummy=filter.Filter(samples[j])
    end=time.time()
    print('Filtered '+str(n*n)+' samples with '+type+' in '+str(end-start)+' seconds')

# Call subprocess and concatenate stdout
def call(caller,parameters):
    cmd=[caller]
    w=''
    for p in parameters:
        if p==' ':
            cmd.append(w)
            w=''
        else:
            w+=p
    if len(w):
        cmd.append(w)
    return (subprocess.run(cmd,stdout=subprocess.PIPE).stdout).decode('utf-8')

# Display help-message
def helpmsg(caller):
    print('RTFIR Python Test 1.0')
    print('Tests RTFIR implementation python')
    print('Fiksdal(C)2021')
    print('')
    print('Usage: '+caller+' [OPTIONS] [FILTER]')
    print('')
    print('Options:')
    print('\t--samplerate HZ\t\tSet sampling frequency in hertz')
    print('\t--performance\t\tTest performance by filtering a large dataset')
    print('\t--file PATH\t\tFilter data from file');
    print('\t--stdin\t\t\tFilter data from stdin to stdout')
    print('\t--coeff\t\t\tDump filter coefficients')
    print('')
    print('Filters:')
    print('\t--lowpass TAPS F0\tTest lowpass filter')
    print('\t--highpass TAPS F0\tTest highpass filter')
    print('\t--bandpass TAPS F1 F2\tTest bandpass filter')
    print('\t--bandstop TAPS F1 F2\tTest bandstop filter')
    print('')
    exit()


# Set samplerate and mode
filename=''
mode=0
fs=250.0
i=1
while i<len(sys.argv):
    if sys.argv[i]=='--samplerate':
        i+=1
        fs=float(sys.argv[i])
    elif sys.argv[i]=='--file':
        i+=1
        filename=sys.argv[i]
        mode=MODE_FILE
    elif sys.argv[i]=='--stdin':
        mode=MODE_STDIN
    elif sys.argv[i]=='--coeff':
        mode=MODE_COEFF
    elif sys.argv[i]=='--performance':
        mode=MODE_PERF
    elif sys.argv[i]=='--help':
        helpmsg(sys.argv[0])
    i+=1
if len(sys.argv)==1:
    helpmsg(sys.argv[0])

# Open input file
fd=sys.stdin
if len(filename):
    fd=open(filename,'r')

# Execute filter options
i=1
name=''
filter=None
while i<len(sys.argv):
    if sys.argv[i]=='--samplerate':
        i+=1
    elif sys.argv[i]=='--file':
        i+=1
    elif sys.argv[i]=='--stdin':
        pass
    elif sys.argv[i]=='--coeff':
        pass
    elif sys.argv[i]=='--performance':
        pass
    elif sys.argv[i]=='--lowpass':
        name=sys.argv[i][2:]
        i+=1
        taps=int(sys.argv[i])
        i+=1
        f0=float(sys.argv[i])
        filter=rtfir.RTFIR_lowpass(taps,f0/fs)
    elif sys.argv[i]=='--highpass':
        name=sys.argv[i][2:]
        i+=1
        taps=int(sys.argv[i])
        i+=1
        f0=float(sys.argv[i])
        filter=rtfir.RTFIR_highpass(taps,f0/fs)
    elif sys.argv[i]=='--bandpass':
        name=sys.argv[i][2:]
        i+=1
        taps=int(sys.argv[i])
        i+=1
        f1=float(sys.argv[i])
        i+=1
        f2=float(sys.argv[i])
        filter=rtfir.RTFIR_bandpass(taps,f1/fs,f2/fs)
    elif sys.argv[i]=='--bandstop':
        name=sys.argv[i][2:]
        i+=1
        taps=int(sys.argv[i])
        i+=1
        f1=float(sys.argv[i])
        i+=1
        f2=float(sys.argv[i])
        filter=rtfir.RTFIR_bandstop(taps,f1/fs,f2/fs)
    else:
        print('Invalid parameter: '+sys.argv[i])
        exit()

    if filter:
        if mode==MODE_STDIN:    filterfile(filter,sys.stdin)
        if mode==MODE_FILE:     filterfile(filter,fd)
        if mode==MODE_PERF:     filterperf(filter,name)
        if mode==MODE_COEFF:
            coeff=filter.GetCoefficients()
            for c in coeff:
                print(str(c))
        filter=None
    i+=1

