#include "lsm.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>

void require(bool condition,const char* message) {
    if(!condition) throw std::runtime_error(message);
}
int main() {
    try {
        auto beta=lsm::solve_linear_system({2,1,1,3},{5,7});
        require(std::abs(beta[0]-1.6)<1e-12 && std::abs(beta[1]-1.8)<1e-12,"linear solve");
        lsm::ModelParams model{100,.05,.2};
        lsm::OptionParams option{100,1,false};
        lsm::LsmConfig config;config.num_paths=40000;config.num_steps=50;
        double put=lsm::price_american_lsm(model,option,config);
        require(put>5.5 && put<6.7,"American put reference range");
        require(put==lsm::price_american_lsm(model,option,config),"seed repeatability");
        option.is_call=true;
        double call=lsm::price_american_lsm(model,option,config);
        require(call>9.8 && call<11.1,"non-dividend call reference range");
        model.S0=1;option.is_call=false;
        double deep=lsm::price_american_lsm(model,option,config);
        require(deep>=99,"time-zero exercise lower bound");
        std::cout<<"Linear solve, repeatability, price ranges, immediate exercise: passed\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<"\n";return 1;}
}
