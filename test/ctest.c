#include <sys/time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../rtfir.h"

typedef enum {
    MODE_STDIN,
    MODE_FILE,
    MODE_COEFF,
    MODE_PERF
} testmode_t;

/*!\brief High resolution clock
 * \return Current time as a double
 */
double gettime(){
    struct timeval tv;
    struct timezone tz;
    gettimeofday(&tv, &tz);
    return 1e-6*tv.tv_usec + tv.tv_sec;
}

/*!\brief Filter data provided on stdin
 * \param Filter Filter to use
 */
void filterfile(RTFIR *Filter,FILE *FD){
    double sample=0;
    size_t bsize=256;
    char *buffer;
    buffer=(char*)malloc(bsize*sizeof(char));
    while(1){
        int len=getline(&buffer,&bsize,FD);
        if(len>1){
            buffer[len-1]=0;
            sample=strtod(buffer,0);
            printf("%f\n",RTFIR_filter(Filter,sample));
        }
        else{
            break;
        }
    }
    free(buffer);
}

/*!\brief Performance-test filter
 * \param Filter Filter to use
 */
void filterperf(RTFIR *Filter,char *Type){
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
    printf("Filtered %d samples with %s in %f seconds\n",n*n,Type,end-start);
}

/*!\brief Displays help-message
 */
void help(char *Caller){
    printf("RTFIR C Tester 1.0\n");
    printf("For testing RTFIR C unit\n");
    printf("Vegard Fiksdal(C)2021\n");
    printf("\n");
    printf("Usage: %s [OPTIONS] [FILTER]\n",Caller);
    printf("\n");
    printf("Options:\n");
    printf("\t--samplerate HZ\t\tSamplerate in hertz\n");
    printf("\t--performance\t\tTest performance by filtering a large dataset\n");
    printf("\t--file PATH\t\tFilter data from file\n");
    printf("\t--stdin\t\t\tFilter data from stdin to stdout\n");
    printf("\t--coeff\t\t\tDump filter coefficients\n");
    printf("\n");
    printf("Filters:\n");
    printf("\t--lowpass TAPS F0\tTest lowpass filter\n");
    printf("\t--highpass TAPS F0\tTest highpass filter\n");
    printf("\t--bandpass TAPS F1 F2\tTest bandpass filter\n");
    printf("\t--bandstop TAPS F1 F2\tTest bandstop filter\n");
    printf("\n");
}

int main(int argc,char *argv[]){
    // Set sampling rate and mode from parameters
    double samplerate=250;
    testmode_t mode=MODE_STDIN;
    char *filename=0;
    for(int i=1;i<argc;i++){
        if(!strcmp(argv[i],"--samplerate")){
            samplerate=strtod(argv[++i],0);
        }
        if(!strcmp(argv[i],"--file")){
            mode=MODE_FILE;
            filename=argv[++i];
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

    // Open input
    FILE *fd=stdin;
    if(filename){
        fd=fopen(filename,"rb");
    }

    // Run filters
    char *type=0;
    RTFIR filter;
    memset(&filter,0,sizeof(filter));
    for(int i=1;i<argc;i++){
        // Ignore already parsed parameters
        if(!strcmp(argv[i],"--samplerate")){i++;}
        else if(!strcmp(argv[i],"--file")){i++;}
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
            printf("Invalid parameter: %s\n",argv[i]);
            return -1;
        }

        // Execute tests
        if(filter.taps){
            if(mode==MODE_STDIN)    filterfile(&filter,stdin);
            if(mode==MODE_FILE)     filterfile(&filter,fd);
            if(mode==MODE_PERF)     filterperf(&filter,type);
            if(mode==MODE_COEFF){
                for(int i=0;i<filter.taps;i++){
                    printf("%f\n",filter.coeff[i]);
                }
            }
            RTFIR_close(&filter);
        }
    }

    // Close input and terminate
    fclose(fd);
    return 0;
}

