/*!\file rtfir.h
 * \brief Implements realtime FIR filtering in C
 * \author Vegard Fiksdal
 */

#ifndef _RTFIR_H_
#define _RTFIR_H_

#include <stdbool.h>

// Struct to hold a FIR filter
typedef struct {
    double *coeff;
    double *buffer;
    unsigned int taps;
} RTFIR;

// Initializes FIR objects of various types
bool RTFIR_init_lowpass(RTFIR *Filter,const unsigned int Taps,const double Freq);
bool RTFIR_init_highpass(RTFIR *Filter,const unsigned int Taps,const double Freq);
bool RTFIR_init_bandpass(RTFIR *Filter,const unsigned int Taps,const double Low,const double High);
bool RTFIR_init_bandstop(RTFIR *Filter,const unsigned int Taps,const double Low,const double High);

// Filters a sample with a FIR object
double RTFIR_filter(RTFIR *Filter,const double Sample);

// Deletes a FIR object
void RTFIR_free(RTFIR *Filter);

#endif

