#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "rtfir.h"

// Some math.h implementations don't define M_PI
#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif


/*!\brief Initializes a RTFIR object and generates lowpass coefficients
 * \param Filter RTFIR filter object to initialize
 * \param Taps Number of taps in the FIR filter
 * \param Freq Normalized cutoff-frequency (f/fs)
 */
bool RTFIR_init_lowpass(RTFIR *Filter,const unsigned int Taps,const double Freq){
    // Check for normalization
    if (Freq<0.0 || Freq>0.5){
        printf("Frequencies must be normalized");
        return false;
    }

    // Allocate memory
    Filter->coeff=(double*)malloc(Taps*sizeof(double));
    Filter->buffer=(double*)malloc(Taps*sizeof(double));
    Filter->taps=Taps;

    // Unset buffer
    memset(Filter->buffer,0,Taps*sizeof(double));
    
    // Generate coefficients
    int W=Taps/2;
    for(int i=-W;i<W;i++){
        if(i==0){
            Filter->coeff[W]=2*Freq;
        }
        else{      
            Filter->coeff[i+W]=sin(2*(M_PI)*Freq*i)/(i*(M_PI));
        }
    }
    return true;
}

/*!\brief Initializes a RTFIR object and generates highpass coefficients
 * \param Filter RTFIR filter object to initialize
 * \param Taps Number of taps in the FIR filter
 * \param Freq Normalized cutoff-frequency (f/fs)
 */
bool RTFIR_init_highpass(RTFIR *Filter,const unsigned int Taps,const double Freq){
    // Check for normalization
    if (Freq<0.0 || Freq>0.5){
        printf("Frequencies must be normalized");
        return false;
    }

    // Allocate memory
    Filter->coeff=(double*)malloc(Taps*sizeof(double));
    Filter->buffer=(double*)malloc(Taps*sizeof(double));
    Filter->taps=Taps;

    // Unset buffer
    memset(Filter->buffer,0,Taps*sizeof(double));
    
    // Generate coefficients
    int W=Taps/2;
    for(int i=-W;i<W;i++){
        if(i==0){
            Filter->coeff[W]=1-(2*Freq);
        }
        else{
            Filter->coeff[i+W]=-sin(2*M_PI*Freq*i)/(i*M_PI);
        }
    }
    return true;
}

/*!\brief Initializes a RTFIR object and generates bandpass coefficients
 * \param Filter RTFIR filter object to initialize
 * \param Taps Number of taps in the FIR filter
 * \param Low Normalized lower cutoff-frequency (f/fs)
 * \param High Normalized higher cutoff-frequency (f/fs)
 */
bool RTFIR_init_bandpass(RTFIR *Filter,const unsigned int Taps,const double Low,const double High){
    // Check for normalization
    if (Low<0.0 || Low>0.5 || High<0.0 || High>0.5){
        printf("Frequencies must be normalized");
        return false;
    }

    // Allocate memory
    Filter->coeff=(double*)malloc(Taps*sizeof(double));
    Filter->buffer=(double*)malloc(Taps*sizeof(double));
    Filter->taps=Taps;

    // Unset buffer
    memset(Filter->buffer,0,Taps*sizeof(double));
    
    // Generate coefficients
    int W=Taps/2;
    for(int i=-W;i<W;i++){
        if(i==0){
            Filter->coeff[i+W]=((2*M_PI*High)-(2*M_PI*Low))/M_PI;
        }
        else{
            Filter->coeff[i+W]=(sin(2*M_PI*High*i)-sin(2*M_PI*Low*i))/(i*M_PI);
        }
    }
    return true;
}

/*!\brief Initializes a RTFIR object and generates bandstop coefficients
 * \param Filter RTFIR filter object to initialize
 * \param Taps Number of taps in the FIR filter
 * \param Low Normalized lower cutoff-frequency (f/fs)
 * \param High Normalized higher cutoff-frequency (f/fs)
 */
bool RTFIR_init_bandstop(RTFIR *Filter,const unsigned int Taps,const double Low,const double High){
    // Check for normalization
    if (Low<0.0 || Low>0.5 || High<0.0 || High>0.5){
        printf("Frequencies must be normalized");
        return false;
    }

    // Allocate memory
    Filter->coeff=(double*)malloc(Taps*sizeof(double));
    Filter->buffer=(double*)malloc(Taps*sizeof(double));
    Filter->taps=Taps;

    // Unset buffer
    memset(Filter->buffer,0,Taps*sizeof(double));
    
    // Generate coefficients
    int W=Taps/2;
    for(int i=-W;i<W;i++){
        if(i==0){
            Filter->coeff[i+W]=1+((2*M_PI*Low)-(2*M_PI*High))/M_PI;
        }
        else{
            Filter->coeff[i+W]=(sin(2*M_PI*Low*i)-sin(2*M_PI*High*i))/(i*M_PI);
        }
    }
    return true;
}

/*!\brief Filters input data
 * \param Filter RTFIR filter object to filter with
 * \param Sample Sample to filter
 * \return Filtered sample
 */
double RTFIR_filter(RTFIR *Filter,const double Sample){
    // Roll back samplebuffer
    memmove(&Filter->buffer[1],&Filter->buffer[0],(Filter->taps-1)*sizeof(*Filter->buffer));
    Filter->buffer[0]=Sample;

    // Perform multiplication
    double output=0.0;
    for(unsigned int i=0;i<Filter->taps;i++){
        output+=Filter->buffer[i]*Filter->coeff[i];
    }
    return output;  
}

/*!\brief Free filter data and close object
 * \param Filter RTFIR filter object to free
 */
void RTFIR_close(RTFIR *Filter){
    if(Filter->coeff){
        free(Filter->coeff);
        Filter->coeff=0;
    }
    if(Filter->buffer){
        free(Filter->buffer);
        Filter->buffer=0;
    }
    Filter->taps=0;
}

