#pragma once
#include <cmath>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>

struct Options {
    double spot=100, strike=100, rate=.05, volatility=.2, maturity=1;
    std::size_t paths=50000, steps=50, degree=2;
    std::size_t repeat=1, warmup=0;
    unsigned long long seed=42;
    bool call=false, json=false, demo=false, help=false;
};

inline unsigned long long integer(const std::string& text) {
    if (text.empty() || text.find_first_not_of("0123456789")!=std::string::npos)
        throw std::invalid_argument("Expected a nonnegative integer: "+text);
    std::size_t end=0;
    auto value=std::stoull(text,&end);
    if(end!=text.size()) throw std::invalid_argument("Invalid integer: "+text);
    return value;
}
inline double number(const std::string& text) {
    std::size_t end=0;
    double value=std::stod(text,&end);
    if(end!=text.size() || !std::isfinite(value))
        throw std::invalid_argument("Expected a finite number: "+text);
    return value;
}
inline Options parse(int argc,char** argv) {
    Options o;
    for(int i=1;i<argc;++i) {
        const std::string key=argv[i];
        if(key=="--help" || key=="-h") {o.help=true;continue;}
        if(key=="--put") {o.call=false;continue;}
        if(key=="--call") {o.call=true;continue;}
        if(key=="--json") {o.json=true;continue;}
        if(key=="--demo") {o.demo=true;continue;}
        if(++i>=argc) throw std::invalid_argument("Missing value for "+key);
        const std::string value=argv[i];
        if(key=="--S0") o.spot=number(value);
        else if(key=="--K") o.strike=number(value);
        else if(key=="--r") o.rate=number(value);
        else if(key=="--sigma") o.volatility=number(value);
        else if(key=="--T") o.maturity=number(value);
        else if(key=="--paths") o.paths=integer(value);
        else if(key=="--steps") o.steps=integer(value);
        else if(key=="--deg") o.degree=integer(value);
        else if(key=="--seed") o.seed=integer(value);
        else if(key=="--repeat") o.repeat=integer(value);
        else if(key=="--warmup") o.warmup=integer(value);
        else throw std::invalid_argument("Unknown option: "+key);
    }
    if(o.spot<=0 || o.strike<=0 || o.maturity<=0 || o.volatility<0)
        throw std::invalid_argument("Spot, strike and maturity must be positive; volatility nonnegative.");
    if(o.paths<8 || o.steps<1 || o.steps>10000 || o.degree>7)
        throw std::invalid_argument("Use paths >= 8, steps 1..10000 and degree 0..7 (2 recommended).");
    if(o.repeat<1 || o.repeat>100 || o.warmup>10)
        throw std::invalid_argument("Use repeat 1..100 and warmup 0..10.");
    // A predictable limit for a download-and-try tool; leave room for working arrays.
    const long double bytes=static_cast<long double>(o.paths)*(o.steps+1)*sizeof(double);
    if(bytes>2.0L*1024*1024*1024)
        throw std::invalid_argument("Path matrix exceeds the 2 GiB demo limit. Reduce paths or steps.");
    if(std::abs(o.rate)*o.maturity>100 || o.volatility*std::sqrt(o.maturity)>10)
        throw std::invalid_argument("Parameters exceed the demo's numerical range.");
    return o;
}
