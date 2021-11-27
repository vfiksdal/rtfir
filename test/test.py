#!/usr/bin/env python3
#
# Script to test realtime fir filters
#

# Standard imports
import time,sys,random,subprocess,rtfir
import matplotlib.pyplot as plt
import numpy as np


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


# Performance test filters in c,c++ and python
def performance(fs,taps):
    result=call('./pytest.py','--samplerate '+str(fs)+' --performance --lowpass '+str(taps)+' 10')
    p=1000000/float(result[result.find(' in ')+4:result.find(' seconds')])
    result=call('./cpptest','--samplerate '+str(fs)+' --performance --lowpass '+str(taps)+' 10')
    cpp=1000000/float(result[result.find(' in ')+4:result.find(' seconds')])
    result=call('./ctest','--samplerate '+str(fs)+' --performance --lowpass '+str(taps)+' 10')
    c=1000000/float(result[result.find(' in ')+4:result.find(' seconds')])
    print('taps:'+str(taps)+'\tc:'+str(c)+'sps c++:'+str(cpp)+'sps python: '+str(p)+'sps')
    return c,cpp,p


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
def qatest_coeff(fs,taps,postfix):
    print('Dumping coefficients')
    flow=(fs/5)/8.0*3.0
    fhigh=(fs/5)/8.0*5.0
    lpf=rtfir.RTFIR_lowpass(taps,flow/fs)
    hpf=rtfir.RTFIR_highpass(taps,fhigh/fs)
    bpf=rtfir.RTFIR_bandpass(taps,flow/fs,fhigh/fs)
    bsf=rtfir.RTFIR_bandstop(taps,flow/fs,fhigh/fs)
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
    plt.savefig('qa_coeff'+postfix+'.png')


# Estimate frequency response
def qatest_fresponse(fs,taps,postfix):
    # Estimate frequency response
    flow=(fs/5)/8.0*3.0
    fhigh=(fs/5)/8.0*5.0
    L=1024
    lpc=rtfir.RTFIR_lowpass(taps,flow/fs).GetCoefficients()
    lph=np.zeros(L)
    lph[0:len(lpc)]=lpc
    lph=np.abs(np.fft.fft(lph))[0:L//2+1]
    hpc=rtfir.RTFIR_highpass(taps,fhigh/fs).GetCoefficients()
    hph=np.zeros(L)
    hph[0:len(hpc)]=hpc
    hph=np.abs(np.fft.fft(hph))[0:L//2+1]
    bpc=rtfir.RTFIR_bandpass(taps,flow/fs,fhigh/fs).GetCoefficients()
    bph=np.zeros(L)
    bph[0:len(bpc)]=bpc
    bph=np.abs(np.fft.fft(bph))[0:L//2+1]
    bsc=rtfir.RTFIR_bandstop(taps,flow/fs,fhigh/fs).GetCoefficients()
    bsh=np.zeros(L)
    bsh[0:len(bsc)]=bsc
    bsh=np.abs(np.fft.fft(bsh))[0:L//2+1]

    # Plot responses
    x=np.linspace(0,fs/2,len(lph))
    fig, axs = plt.subplots(2, 2)
    axs[0,0].plot(x,lph)
    axs[0,0].set_title('Lowpass')
    axs[0,0].grid()
    axs[0,1].plot(x,hph)
    axs[0,1].set_title('Highpass')
    axs[0,1].grid()
    axs[1,0].plot(x,bph)
    axs[1,0].set_title('Bandpass')
    axs[1,0].grid()
    axs[1,1].plot(x,bsh)
    axs[1,1].set_title('Bandstop')
    axs[1,1].grid()
    for ax in axs.flat: ax.set(xlabel='Frequency [Hz]',ylabel='Gain [dB]')
    for ax in axs.flat: ax.label_outer()
    fig.suptitle('Frequency Reponse\nFs='+str(fs)+'Hz Taps='+str(taps)+'\nFlow='+str(flow)+'Hz Fhigh='+str(fhigh)+'Hz')
    fig.set_size_inches(11.7,8.3)
    fig.tight_layout()
    plt.savefig('qa_fresponse'+postfix+'.png')


# Test pulse response
def qatest_presponse(fs,taps,postfix):
    # Filter pulse response
    flow=(fs/5)/8.0*3.0
    fhigh=(fs/5)/8.0*5.0
    pulse=[]
    pulse.extend(np.zeros(taps*2))
    pulse.extend(np.ones(taps))
    pulse.extend(np.zeros(taps*2))
    lpf=rtfir.RTFIR_lowpass(taps,flow/fs)
    hpf=rtfir.RTFIR_highpass(taps,fhigh/fs)
    bpf=rtfir.RTFIR_bandpass(taps,flow/fs,fhigh/fs)
    bsf=rtfir.RTFIR_bandstop(taps,flow/fs,fhigh/fs)
    lppulse=[]
    hppulse=[]
    bppulse=[]
    bspulse=[]
    for i in range(0,len(pulse)):
        lppulse.append(lpf.Filter(pulse[i]))
        hppulse.append(hpf.Filter(pulse[i]))
        bppulse.append(bpf.Filter(pulse[i]))
        bspulse.append(bsf.Filter(pulse[i]))

    # Plot pulse response
    n=int((taps-1)/2)*0
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(pulse)
    axs[0, 0].plot(lppulse)
    axs[0, 0].set_title('Lowpass')
    axs[0, 1].plot(pulse)
    axs[0, 1].plot(hppulse)
    axs[0, 1].set_title('Highpass')
    axs[1, 0].plot(pulse)
    axs[1, 0].plot(bppulse)
    axs[1, 0].set_title('Bandpass')
    axs[1, 1].plot(pulse)
    axs[1, 1].plot(bspulse)
    axs[1, 1].set_title('Bandstop')
    for ax in axs.flat: ax.label_outer()
    fig.suptitle('FIR pulse responses for '+str(taps)+' taps')
    fig.set_size_inches(11.7,8.3)
    fig.tight_layout()
    plt.savefig('qa_presponse'+postfix+'.png')


# Create a frequency sweep and filter it through the test programs
def qatest_chirp(fs,taps,postfix):
    # Generate a dataset
    print('Synthesizing dataset')
    span=fs/5
    t=60
    sweep=chirp(fs,1/t,1.0,span)
    fd=open('test.csv','w')
    for x in sweep:
        fd.write(str(x)+'\n')
    fd.close()
    flow=span/8.0*3.0
    fhigh=span/8.0*5.0

    # Filter data in test-applications and plot FFT data
    print('Lowpass filtering dataset')
    fig, axs = plt.subplots(2, 2)
    result=call('./ctest','--file test.csv --samplerate '+str(fs)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 0].plot(xf,unfilteredf,label='Unfiltered')
    axs[0, 0].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(fs)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 0].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(fs)+' --lowpass '+str(taps)+' '+str(flow))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 0].plot(xf,filteredf,label='Python')
    axs[0, 0].set_title('Lowpass')
    axs[0, 0].legend()
    axs[0, 0].grid()

    print('Highpass filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(fs)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 1].plot(xf,unfilteredf,label='Unfiltered')
    axs[0, 1].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(fs)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 1].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(fs)+' --highpass '+str(taps)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[0, 1].plot(xf,filteredf,label='Python')
    axs[0, 1].set_title('Highpass')
    axs[0, 1].legend()
    axs[0, 1].grid()

    print('Bandpass filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(fs)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 0].plot(xf,unfilteredf,label='Unfiltered')
    axs[1, 0].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(fs)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 0].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(fs)+' --bandpass '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 0].plot(xf,filteredf,label='Python')
    axs[1, 0].set_title('Bandpass')
    axs[1, 0].legend()
    axs[1, 0].grid()

    print('Bandstop filtering dataset')
    result=call('./ctest','--file test.csv --samplerate '+str(fs)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 1].plot(xf,unfilteredf,label='Unfiltered')
    axs[1, 1].plot(xf,filteredf,label='C')
    result=call('./cpptest','--file test.csv --samplerate '+str(fs)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 1].plot(xf,filteredf,label='C++')
    result=call('./pytest.py','--file test.csv --samplerate '+str(fs)+' --bandstop '+str(taps)+' '+str(flow)+' '+str(fhigh))
    result=result.split('\n')[:-1]
    map(float,result)
    unfilteredf,filteredf,xf=fft(sweep,result,fs,span*1.1)
    axs[1, 1].plot(xf,filteredf,label='Python')
    axs[1, 1].set_title('Bandstop')
    axs[1, 1].legend()
    axs[1, 1].grid()

    for ax in axs.flat: ax.set(xlabel='Frequency [Hz]',ylabel='Magnitude')
    for ax in axs.flat: ax.label_outer()
    fig.suptitle('Spectrum of filtered chirp\nFlow='+str(flow)+'Hz Fhigh='+str(fhigh)+'Hz Taps='+str(taps)+'\nFs='+str(fs)+'Hz t='+str(t)+'s')
    fig.set_size_inches(11.7,8.3)
    fig.tight_layout()
    plt.savefig('qa_chirp'+postfix+'.png')


# Perform standard QA test
def qa_standard(postfix):
    # Formalized test settings
    fs=250.0
    taps=64

    # Filter chirp
    qatest_chirp(fs,taps,postfix)

    # Get frequency responses
    qatest_fresponse(fs,taps,postfix)

    # Performance test filters
    tpython=[]
    tcpp=[]
    tc=[]
    n=[]
    print('Performance testing:')
    for i in range(100,1100,100):
        c,cpp,p=performance(fs,i)
        tpython.append(p)
        tcpp.append(cpp)
        tc.append(c)
        n.append(i)

    # Plot result
    plt.figure(figsize=(11.7,8.3))
    plt.plot(n,tc,label="C")
    plt.plot(n,tcpp,label="C++")
    plt.plot(n,tpython,label="Python")
    plt.title('Performance Test\nLowpass filtering at '+str(fs)+'Hz sampling rate')
    plt.ylabel('Samples/second')
    plt.xlabel('Taps')
    plt.legend()
    plt.tight_layout()
    plt.savefig('qa_performance'+postfix+'.png')


# Display help-message
def helpmsg(caller):
    print('RTFIR Test 1.0')
    print('Tests and plots RTFIR performance')
    print('Fiksdal(C)2021')
    print('')
    print('Usage: '+caller+' [OPTIONS] COMMAND')
    print('')
    print('Options:')
    print('\t--samplerate HZ\t\tSet sampling frequency in hertz')
    print('\t--postfix STRING\tApply a postfix to output filenames')
    print('\t--taps N\t\tSet filter length')
    print('')
    print('Commands:')
    print('\t--standard\t\tExecute standard QA test')
    print('\t--fresponse\t\tCalculate frequency response of filters')
    print('\t--presponse\t\tTest pulse response of filters')
    print('\t--chirp\t\t\tSynthesize frequency sweep and filter it')
    print('\t--perf\t\t\tMeasure number of samples per second for filter')
    print('\t--coeff\t\t\tPlot filter coefficients')
    print('')
    exit()


# Parse settings
postfix=''
fs=250.0
taps=64
i=1
while i<len(sys.argv):
    if sys.argv[i]=='--standard':       pass
    elif sys.argv[i]=='--fresponse':    pass
    elif sys.argv[i]=='--presponse':    pass
    elif sys.argv[i]=='--chirp':        pass
    elif sys.argv[i]=='--perf':         pass
    elif sys.argv[i]=='--coeff':        pass
    elif sys.argv[i]=='--postfix':
        i+=1
        postfix=sys.argv[i]
    elif sys.argv[i]=='--samplerate':
        i+=1
        fs=float(sys.argv[i])
    elif sys.argv[i]=='--taps':
        i+=1
        taps=int(sys.argv[i])
    elif sys.argv[i]=='--help':
        helpmsg(sys.argv[0])
    else:
        print('Invalid parameter: '+sys.argv[i])
    i+=1
i=1

#Adjust and adapt settings
if len(postfix) and not postfix[0]=='_':
    postfix='_'+postfix

# Run commands
while i<len(sys.argv):
    if sys.argv[i]=='--standard':
        qa_standard(postfix)
    if sys.argv[i]=='--fresponse':
        qatest_fresponse(fs,taps,postfix)
    if sys.argv[i]=='--presponse':
        qatest_presponse(fs,taps,postfix)
    if sys.argv[i]=='--chirp':
        qatest_chirp(fs,taps,postfix)
    if sys.argv[i]=='--coeff':
        qatest_coeff(fs,taps,postfix)
    if sys.argv[i]=='--perf':
        performance(fs,taps)
    i+=1
if len(sys.argv)==1:
    helpmsg(sys.argv[0])

