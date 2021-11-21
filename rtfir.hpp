/*!\file rtfir.hpp
 * \brief Implements realtime FIR filtering for C++
 * \author Vegard Fiksdal
 */

#ifndef _RTFIR_HPP_
#define _RTFIR_HPP_

#include <vector>

class RTFIR {
    protected:
        double *coeff;      //!< Coefficients of the FIR filter
        double *buffer;     //!< Sample buffer for FIR filter
        unsigned int taps;  //!< Number of coefficients of the FIR filter
    public:
        RTFIR(const unsigned int &Taps);
        ~RTFIR();
        double Filter(const double &x);
        std::vector<double> GetCoefficients() const;
};
    
class RTFIR_lowpass : public RTFIR {
    public:
        RTFIR_lowpass(const unsigned int &Taps,const double &Freq);
};

class RTFIR_highpass : public RTFIR {
    public:
        RTFIR_highpass(const unsigned int &Taps,const double &Freq);
};

class RTFIR_bandpass : public RTFIR {
    public:
        RTFIR_bandpass(const unsigned int &Taps,const double &Freq1,const double &Freq2);
};

class RTFIR_bandstop : public RTFIR {
    public:
        RTFIR_bandstop(const unsigned int &Taps,const double &Freq1,const double &Freq2);
};


#endif

