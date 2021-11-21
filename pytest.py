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

# Dumps filter coefficients
def qatest_coeff(samplerate):
    print('Dumping coefficients')
    flow=(samplerate/5)/8.0*3.0
    fhigh=(samplerate/5)/8.0*5.0
    taps=64
    lpf=rtfir.RTFIR_lowpass(taps,flow/samplerate)
    hpf=rtfir.RTFIR_highpass(taps,fhigh/samplerate)
    bpf=rtfir.RTFIR_bandpass(taps,flow/samplerate,fhigh/samplerate)
    bsf=rtfir.RTFIR_bandstop(taps,flow/samplerate,fhigh/samplerate)
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(lpf.GetCoefficients())
    axs[0, 0].set_title('Lowpass')
    axs[0, 1].plot(hpf.GetCoefficients())
    axs[0, 1].set_title('Highpass')
    axs[1, 0].plot(bpf.GetCoefficients())
    axs[1, 0].set_title('Bandpass')
    axs[1, 1].plot(bsf.GetCoefficients())
    axs[1, 1].set_title('Bandstop')
    for ax in axs.flat: ax.label_outer()
    fig.suptitle('FIR coefficients for '+str(taps)+' taps')
    fig.set_size_inches(11.7,8.3)
    fig.tight_layout()
    plt.savefig('qa_coeff.png')

# Create a frequency sweep and filter it through the test programs
def qatest_filter(samplerate):
    # Generate a dataset
    print('Synthesizing dataset')
    span=samplerate/5
    taps=64
    t=60
    sweep=chirp(samplerate,1/t,1.0,span)
    fd=open('test.csv','w')
    for x in sweep:
        fd.write(str(x)+'\n')
    fd.close()
    flow=span/8.0*3.0
    fhigh=span/8.0*5.0

    # Filter data in test-applications and plot FFT data
    print('Lowpass filtering dataset')
    fig, axs = plt.subplots(2, 2)
    result=call('./ctest','--file test.csv --samplerate '+str(samplerate)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 0].plot(xf,unfilteredf,label='Unfiltered')
    axs[0, 0].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(samplerate)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 0].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(samplerate)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 0].plot(xf,filteredf,label='Python')
    axs[0, 0].set_title('Lowpass')
    axs[0, 0].legend()
    axs[0, 0].grid()

    print('Highpass filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(samplerate)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 1].plot(xf,unfilteredf,label='Unfiltered')
    axs[0, 1].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(samplerate)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 1].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(samplerate)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[0, 1].plot(xf,filteredf,label='Python')
    axs[0, 1].set_title('Highpass')
    axs[0, 1].legend()
    axs[0, 1].grid()

    print('Bandpass filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(samplerate)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 0].plot(xf,unfilteredf,label='Unfiltered')
    axs[1, 0].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(samplerate)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 0].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(samplerate)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 0].plot(xf,filteredf,label='Python')
    axs[1, 0].set_title('Bandpass')
    axs[1, 0].legend()
    axs[1, 0].grid()

    print('Bandstop filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(samplerate)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 1].plot(xf,unfilteredf,label='Unfiltered')
    axs[1, 1].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(samplerate)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 1].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(samplerate)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,samplerate,span*1.1)
    axs[1, 1].plot(xf,filteredf,label='Python')
    axs[1, 1].set_title('Bandstop')
    axs[1, 1].legend()
    axs[1, 1].grid()

    for ax in axs.flat: ax.set(xlabel='Frequency [Hz]',ylabel='Magnitude')
    for ax in axs.flat: ax.label_outer()
    fig.suptitle('Spectrum of filtered chirp\nFlow='+str(flow)+'Hz Fhigh='+str(fhigh)+'Hz Taps='+str(taps)+'\nFs='+str(fs)+'Hz t='+str(t)+'s')
    fig.set_size_inches(11.7,8.3)
    fig.tight_layout()
    plt.savefig('qa_fft.png')


# Performance test all filters in c,c++ and python
def qatest_perf(samplerate):
    # Performance test filters
    tpython=[]
    tcpp=[]
    tc=[]
    n=[]
    print('Performance testing:')
    for i in range(100,1100,100):
        result=call('./pytest.py','--samplerate '+str(samplerate)+' --performance --lowpass '+str(i)+' 10')
        p=float(result[result.find(' in ')+4:result.find(' seconds')])
        result=call('./cpptest','--samplerate '+str(samplerate)+' --performance --lowpass '+str(i)+' 10')
        cpp=float(result[result.find(' in ')+4:result.find(' seconds')])
        result=call('./ctest','--samplerate '+str(samplerate)+' --performance --lowpass '+str(i)+' 10')
        c=float(result[result.find(' in ')+4:result.find(' seconds')])
        print('taps:'+str(i)+' c:'+str(c)+'s cpp:'+str(cpp)+'s python: '+str(p)+'s')
        tpython.append(1000000/p)
        tcpp.append(1000000/cpp)
        tc.append(1000000/c)
        n.append(i)

    # Plot result
    plt.figure(figsize=(11.7,8.3))
    plt.plot(n,tc,label="C")
    plt.plot(n,tcpp,label="C++")
    plt.plot(n,tpython,label="Python")
    plt.title('Performance Test\nLowpass filtering at '+str(samplerate)+'Hz sampling rate')
    plt.ylabel('Samples/second')
    plt.xlabel('Taps')
    plt.legend()
    plt.tight_layout()
    plt.savefig('qa_performance.png')

# Run all QA tests and quit
def qatest(samplerate):
    qatest_coeff(samplerate)
    qatest_filter(samplerate)
    qatest_perf(samplerate)
    exit(0)

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
i=1
while i<len(sys.argv):
    if sys.argv[i]=='--qa':
        qatest(fs)
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

