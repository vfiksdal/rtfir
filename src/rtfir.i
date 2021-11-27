%module rtfir

%include "std_vector.i"
%include "std_string.i"
namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
}

%{
#include "rtfir.hpp"
%}

%include "rtfir.hpp"
