#include <stdexcept>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "rtfir.hpp"

// Some math.h implementations don't define M_PI
#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif


/*!\brief Constructor for base FIR object
 * \param Taps Number of taps in the filter
 */
RTFIR::RTFIR(const unsigned int &Taps){
    coeff=new double[Taps];
    buffer=new double[Taps];
    memset(buffer,0,Taps*sizeof(double));
    taps=Taps;
}

/*!\brief Deconstructor for base FIR object
 */
RTFIR::~RTFIR(){
    delete [] coeff;
    delete [] buffer;
}

/*!\brief Filters input data
 * \param Sample Sample to filter
 * \return Filtered sample
 */
double RTFIR::Filter(const double &Sample){
    double output=0;
    for(int i=taps-1;i>0;i--){
        buffer[i]=buffer[i-1];
    }
    buffer[0]=Sample;
    for(unsigned int i=0;i<taps;i++){
        output+=buffer[i]*coeff[i];
    }
    return output;  
}

/*!\brief Get a list of coefficients for debugging
 * \return List of FIR coefficients
 */
std::vector<double> RTFIR::GetCoefficients() const{
    std::vector<double> c;
    c.resize(taps);
    for(unsigned int i=0;i<taps;i++){
        c[i]=coeff[i];
    }
    return c;
}

/*!\brief Constructor for lowpass FIR filter
 * \param Taps Number of taps in the FIR filter
 * \param Freq Normalized cutoff-frequency (f/fs)
 */
RTFIR_lowpass::RTFIR_lowpass(const unsigned int &Taps,const double &Freq) : RTFIR(Taps){
    if (Freq<0.0 || Freq>0.5){
        throw std::invalid_argument("Frequencies must be normalized");
    }
    else{
        int W=Taps/2;
        for(int i=-W;i<W;i++){
            if(i==0){
                coeff[W]=2*Freq;
            }
            else{      
                coeff[i+W]=sin(2*(M_PI)*Freq*i)/(i*(M_PI));
            }
        }
    }
}

/*!\brief Constructor for highpass FIR filter
 * \param Taps Number of taps in the FIR filter
 * \param Freq Normalized cutoff-frequency (f/fs)
 */
RTFIR_highpass::RTFIR_highpass(const unsigned int &Taps,const double &Freq) : RTFIR(Taps){
    if (Freq<0.0 || Freq>0.5){
        throw std::invalid_argument("Frequencies must be normalized");
    }
    else{
        int W=Taps/2;
        for(int i=-W;i<W;i++){
            if(i==0){
                coeff[W]=1-(2*Freq);
            }
            else{
                coeff[i+W]=-sin(2*M_PI*Freq*i)/(i*M_PI);
            }
        }
    }
}

/*!\brief Constructor for bandpass FIR filter
 * \param Taps Number of taps in the FIR filter
 * \param Low Normalized lower cutoff-frequency (f/fs)
 * \param High Normalized higher cutoff-frequency (f/fs)
 */
RTFIR_bandpass::RTFIR_bandpass(const unsigned int &Taps,const double &Low,const double &High) : RTFIR(Taps){
    if (Low<0.0 || Low>0.5 || High<0.0 || High>0.5){
        throw std::invalid_argument("Frequencies must be normalized");
    }
    else{
        int W=Taps/2;
        for(int i=-W;i<W;i++){
            if(i==0){
                coeff[W]=((2*M_PI*High)-(2*M_PI*Low))/M_PI;
            }
            else{
                coeff[i+W]=(sin(2*M_PI*High*i)-sin(2*M_PI*Low*i))/(i*M_PI);
            }
        }
    }
}

/*!\brief Constructor for bandstop FIR filter
 * \param Taps Number of taps in the FIR filter
 * \param Low Normalized lower cutoff-frequency (f/fs)
 * \param High Normalized higher cutoff-frequency (f/fs)
 */
RTFIR_bandstop::RTFIR_bandstop(const unsigned int &Taps,const double &Low,const double &High) : RTFIR(Taps){
    if (Low<0.0 || Low>0.5 || High<0.0 || High>0.5){
        throw std::invalid_argument("Frequencies must be normalized");
    }
    else{
        int W=Taps/2;
        for(int i=-W;i<W;i++){
            if(i==0){
                coeff[W]=1+((2*M_PI*Low)-(2*M_PI*High))/M_PI;
            }
            else{
                coeff[i+W]=(sin(2*M_PI*Low*i)-sin(2*M_PI*High*i))/(i*M_PI);
            }
        }
    }
}

