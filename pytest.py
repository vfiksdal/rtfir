#!/usr/bin/env python3
#
# Script to test realtime fir filters
#
import time,sys,random,rtfir

MODE_STDIN=0
MODE_COEFF=1
MODE_PERF=2

def stdinfilter(filter):
    for line in sys.stdin:
        if len(line)>1:
            sample=float(line[:-1])
            print(str(filter.Filter(sample)))

def perfilter(filter,type):
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
    print('\t--stdin\t\t\tFilter data from stdin to stdout')
    print('\t--coeff\t\t\tDump filter coefficients')
    print('')
    print('Options:')
    print('\t--lowpass TAPS F0\tTest lowpass filter')
    print('\t--highpass TAPS F0\tTest highpass filter')
    print('\t--bandpass TAPS F1 F2\tTest bandpass filter')
    print('\t--bandstop TAPS F1 F2\tTest bandstop filter')
    print('')
    exit()


# Set samplerate and mode
mode=0
fs=1000.0
i=1
while i<len(sys.argv):
    if sys.argv[i]=='--samplerate':
        i+=1
        fs=float(sys.argv[i])
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

# Execute filter options
i=1
name=''
filter=None
while i<len(sys.argv):
    if sys.argv[i]=='--samplerate':
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
        if mode==MODE_STDIN:    stdinfilter(filter)
        if mode==MODE_PERF:     perfilter(filter,name)
        if mode==MODE_COEFF:
            coeff=filter.GetCoefficients()
            for c in coeff:
                print(str(c))
        filter=None
    i+=1

