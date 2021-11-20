# RTFIR
Real time FIR filter drop-in classes and units for C, C++ and Python. Includes lowpass, highpass, bandpass and bandstop filters.

## C++ example
```
#include "rtfir.hpp"
#include <stdlib.h>

int main(){
    double samplerate=500;  // Fs in Hz
    double cutoff=100;      // Fc in Hz
    int taps=100;           // FIR taps

    RTFIR_lowpass lowpass=RTFIR_lowpass(taps,cutoff/samplerate);
    double filtered[1000];
    for(int i=0;i<1000;i++){
        filtered[i]=lowpass.Filter(rand()%100);
    }
    return 0;
}
```

## C example
```
#include "rtfir.h"
#include <stdlib.h>

int main(){
    double samplerate=500;  // Fs in Hz
    double cutoff=100;      // Fc in Hz
    int taps=100;           // FIR taps

    RTFIR lowpass;
    RTFIR_init_lowpass(&lowpass,taps,cutoff/samplerate);
    double filtered[1000];
    for(int i=0;i<1000;i++){
        filtered[i]=RTFIR_filter(&lowpass,rand()%100);
    }
    RTFIR_free(&lowpass);
    return 0;
}
```

## Python example
For python we have to compile the c++ library first:
```
make
```
This will generate the python module (rtfir.py) and a shared library (_rtfir.so) which must either be installed in your system path or with your code.
```
import random,rtfir

samplerate=500  # Fs in Hz
cutoff=100      # Fc in Hz
taps=100        # FIR taps

lowpass=rtfir.RTFIR_lowpass(taps,cutoff/samplerate)
filtered=[]
for i in range(0,1000):
  filtered.append(random.random())
```

## Demo
For a more comprehensive example, including other filter types, check out test.py which synthesizes a frequency sweep, filters it through the available filter types and plots the resulting fft's so you can assess it's performance. Use the --help parameter for further information on the script's usage.
```
make
./test.py --samplerate 250 --taps 256
```

