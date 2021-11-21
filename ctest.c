#include <sys/time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rtfir.h"

typedef enum {
    MODE_STDIN,
    MODE_COEFF,
    MODE_PERF
} testmode_t;

double gettime(){
    struct timeval tv;
    struct timezone tz;
    gettimeofday(&tv, &tz);
    return 1e-6*tv.tv_usec + tv.tv_sec;
}

/*!\brief Filter data provided on stdin
 * \param Filter Filter to use
 */
void stdinfilter(RTFIR *Filter){
    double sample=0;
    size_t bsize=256;
    char *buffer;
    buffer=(char*)malloc(bsize*sizeof(char));
    while(1){
        size_t len=getline(&buffer,&bsize,stdin);
        if(len>1){
            buffer[len-1]=0;
            sample=strtod(buffer,0);
            printf("%f\r\n",RTFIR_filter(Filter,sample));
        }
    }
    free(buffer);
}

/*!\brief Performance-test filter
 * \param Filter Filter to use
 */
void perfilter(RTFIR *Filter,char *Type){
    // Generate random input data
    size_t n=1000;
    double samples[n];
    for(size_t i=0;i<n;i++){
        samples[i]=(rand()%1000)/500.0;
    }

    // Filter dataset ...
    double start=gettime();
    double dummy;
    for(size_t i=0;i<n;i++){
        for(size_t j=0;j<n;j++){
            dummy=RTFIR_filter(Filter,samples[j]);
        }
    }
    double end=gettime();
    printf("Filtered %d samples with %s in %f seconds\r\n",n*n,Type,end-start);
}

void help(char *Caller){
    printf("RTFIR C Tester 1.0\r\n");
    printf("For testing RTFIR C unit\r\n");
    printf("Vegard Fiksdal(C)2021\r\n");
    printf("\r\n");
    printf("Usage: %s [OPTIONS] [FILTER]\r\n",Caller);
    printf("\r\n");
    printf("Options:\r\n");
    printf("\t--samplerate HZ\t\tSamplerate in hertz\r\n");
    printf("\t--performance\t\tTest performance by filtering a large dataset\r\n");
    printf("\t--stdin\t\t\tFilter data from stdin to stdout\r\n");
    printf("\t--coeff\t\t\tDump filter coefficients\r\n");
    printf("\r\n");
    printf("Filters:\r\n");
    printf("\t--lowpass TAPS F0\tTest lowpass filter\r\n");
    printf("\t--highpass TAPS F0\tTest highpass filter\r\n");
    printf("\t--bandpass TAPS F1 F2\tTest bandpass filter\r\n");
    printf("\t--bandstop TAPS F1 F2\tTest bandstop filter\r\n");
    printf("\r\n");
}

int main(int argc,char *argv[]){
    // Set sampling rate and mode from parameters
    double samplerate=1000;
    testmode_t mode=MODE_STDIN;
    for(int i=1;i<argc;i++){
        if(!strcmp(argv[i],"--samplerate")){
            samplerate=strtod(argv[++i],0);
        }
        if(!strcmp(argv[i],"--stdin")){
            mode=MODE_STDIN;
        }
        if(!strcmp(argv[i],"--coeff")){
            mode=MODE_COEFF;
        }
        if(!strcmp(argv[i],"--performance")){
            mode=MODE_PERF;
        }
        if(!strcmp(argv[i],"--help")){
            help(argv[0]);
            return 0;
        }
    }
    if(argc==1){
        help(argv[0]);
    }

    // Run filters
    char *type=0;
    RTFIR filter;
    memset(&filter,0,sizeof(filter));
    for(int i=1;i<argc;i++){
        // Ignore already parsed parameters
        if(!strcmp(argv[i],"--samplerate")){i++;}
        else if(!strcmp(argv[i],"--stdin")){}
        else if(!strcmp(argv[i],"--coeff")){}
        else if(!strcmp(argv[i],"--performance")){}

        // Load filters
        else if(!strcmp(argv[i],"--lowpass")){
            type=argv[i]+2;
            unsigned int taps=atoi(argv[++i]);
            double cutoff=strtod(argv[++i],0);
            RTFIR_init_lowpass(&filter,taps,cutoff/samplerate);
        }
        else if(!strcmp(argv[i],"--highpass")){
            type=argv[i]+2;
            unsigned int taps=atoi(argv[++i]);
            double cutoff=strtod(argv[++i],0);
            RTFIR_init_highpass(&filter,taps,cutoff/samplerate);
        }
        else if(!strcmp(argv[i],"--bandpass")){
            type=argv[i]+2;
            unsigned int taps=atoi(argv[++i]);
            double flow=strtod(argv[++i],0);
            double fhigh=strtod(argv[++i],0);
            RTFIR_init_bandpass(&filter,taps,flow/samplerate,fhigh/samplerate);
        }
        else if(!strcmp(argv[i],"--bandstop")){
            type=argv[i]+2;
            unsigned int taps=atoi(argv[++i]);
            double flow=strtod(argv[++i],0);
            double fhigh=strtod(argv[++i],0);
            RTFIR_init_bandstop(&filter,taps,flow/samplerate,fhigh/samplerate);
        }
        else{
            printf("Invalid parameter: %s\r\n",argv[i]);
            return -1;
        }

        // Execute tests
        if(filter.taps){
            if(mode==MODE_STDIN)    stdinfilter(&filter);
            if(mode==MODE_PERF)     perfilter(&filter,type);
            if(mode==MODE_COEFF){
                for(int i=0;i<filter.taps;i++){
                    printf("%f\r\n",filter.coeff[i]);
                }
            }
            RTFIR_close(&filter);
        }
    }

    return 0;
}

