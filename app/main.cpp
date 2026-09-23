#include "options.hpp"
#include "lsm.hpp"
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#ifdef LSM_CUDA
#include <cuda_runtime.h>
#endif
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

void run(const Options& o, bool emit=true) {
#ifdef LSM_CUDA
    int count=0;
    const auto status=cudaGetDeviceCount(&count);
    if(status!=cudaSuccess || count==0)
        throw std::runtime_error("No usable CUDA device. Check the NVIDIA driver or run lsm_cpu.");
    ModelParams model{o.spot,o.rate,o.volatility};
    OptionParams option{o.strike,o.maturity,o.call};
    LsmConfig config;
    const char* backend="cuda";
#else
    lsm::ModelParams model{o.spot,o.rate,o.volatility};
    lsm::OptionParams option{o.strike,o.maturity,o.call};
    lsm::LsmConfig config;
    const char* backend="cpu";
#endif
    config.num_paths=o.paths;config.num_steps=o.steps;
    config.poly_degree=o.degree;config.rng_seed=o.seed;
    double device_ms=0, simulation_ms=0, price=0;
    const auto start=std::chrono::steady_clock::now();
    if(o.volatility==0) {
        // Deterministic limit: optimize discounted exercise payoff over the grid.
        for(std::size_t j=0;j<=o.steps;++j) {
            double t=o.maturity*j/o.steps;
            double spot=o.spot*std::exp(o.rate*t);
            double payoff=std::max(o.call ? spot-o.strike : o.strike-spot,0.0);
            price=std::max(price,payoff*std::exp(-o.rate*t));
        }
    } else {
#ifdef LSM_CUDA
        price=price_american_lsm_gpu(model,option,config,&device_ms,&simulation_ms);
#else
        price=lsm::price_american_lsm(model,option,config);
#endif
    }
    const double wall_ms=std::chrono::duration<double,std::milli>(
        std::chrono::steady_clock::now()-start).count();
    if(!std::isfinite(price)) throw std::runtime_error("Nonfinite result; reduce numerical extremes.");
    if(!emit) return;
    std::cout<<std::setprecision(12);
    if(o.json) {
        std::cout<<"{\"backend\":\""<<backend<<"\",\"type\":\""<<(o.call?"call":"put")
          <<"\",\"price\":"<<price<<",\"wall_ms\":"<<wall_ms
          <<",\"device_pipeline_ms\":"<<device_ms<<",\"path_simulation_ms\":"<<simulation_ms
          <<",\"paths\":"<<o.paths<<",\"steps\":"<<o.steps<<",\"degree\":"<<o.degree
          <<",\"seed\":"<<o.seed<<",\"spot\":"<<o.spot<<",\"strike\":"<<o.strike
          <<",\"rate\":"<<o.rate<<",\"volatility\":"<<o.volatility
          <<",\"maturity\":"<<o.maturity<<"}\n";
    } else {
        std::cout<<"LSM Solver | "<<backend<<" | American "<<(o.call?"call":"put")
          <<"\n"<<o.paths<<" paths x "<<o.steps<<" exercise dates | degree "<<o.degree
          <<" | seed "<<o.seed<<"\nPrice estimate: "<<price
          <<"\nSolver wall time: "<<wall_ms<<" ms\n";
#ifdef LSM_CUDA
        std::cout<<"CUDA pipeline: "<<device_ms<<" ms | path simulation: "<<simulation_ms<<" ms\n";
#endif
        std::cout<<"Finite exercise grid, one underlying, constant-volatility GBM.\n";
    }
}

int main(int argc,char** argv) {
    bool pause=false;
#ifdef _WIN32
    DWORD ids[2];
    pause=argc==1 && GetConsoleProcessList(ids,2)==1;
#endif
    int result=0;
    try {
        Options o=parse(argc,argv);
        if(o.help) {
            std::cout<<"LSM Solver - CPU / CUDA Longstaff-Schwartz research demo\n"
              <<"Usage: lsm_cpu [--put|--call] [--paths 50000] [--steps 50]\n"
              <<"  --S0 100 --K 100 --r 0.05 --sigma 0.2 --T 1\n"
              <<"  --deg 2 --seed 42 --json --demo --repeat 1 --warmup 0 --help\n"
              <<"No arguments: run the default American put. --demo: run put and call.\n"
              <<"CUDA build uses the same flags through lsm_cuda.\n";
        } else {
            for(std::size_t i=0;i<o.warmup;++i) run(o,false);
            for(std::size_t i=0;i<o.repeat;++i) {
                if(o.demo) {o.call=false;run(o);o.call=true;run(o);}
                else run(o);
            }
        }
    } catch(const std::exception& error) {
        std::cerr<<"Error: "<<error.what()<<"\nUse --help for valid options.\n";result=1;
    }
    if(pause) {std::cout<<"\nPress Enter to close.";std::cin.get();}
    return result;
}
