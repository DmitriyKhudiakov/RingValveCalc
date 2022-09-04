import numpy as np


class SuctionModelRing:
    def __init__(self, solver):
        # solver object
        self.sol = solver
    
    def chi(self, p):
        return (self.sol.comp.p_suc - p) / self.sol.comp.p_suc

    def phi(self,t):
        return self.sol.comp.omega * t

    def f_func(self,t):
        return 2.0 * self.sol.comp.am + 1.0 + self.sol.comp.lambda_R / 4.0 - np.cos(self.phi(t)) - self.sol.comp.lambda_R * np.cos(2.0 * self.phi(t)) / 4.0

    def f_func_deriv(self,t):
        return np.sin(self.phi(t)) + self.sol.comp.lambda_R * np.sin(2 * self.phi(t)) / 2.0

    def solve_ivp_function(self, t, vars):
        # unzip vars
        p = vars[0]
        xs = vars[1:]
        dx_derivdt = [0.0 for i in range(len(self.sol.suc_plates))]
        
        # condition 1 - limits of x 
        delta_x_range = 0.01
        delta_x_velocity = 0.05
        
        for i in range(len(self.sol.suc_plates)):
            if xs[0+2*i] > self.sol.suc_plates[i].h:
                xs[0+2*i] = self.sol.suc_plates[i].h
            if xs[0+2*i] < 0:
                xs[0+2*i] = 0
        
        # condition 2
        for i in range(len(self.sol.suc_plates)):
            if ((xs[0+2*i] >= self.sol.suc_plates[0].h) and (xs[1+2*i] > 0)) or ((xs[0+2*i] <= 0) and (xs[1+2*i] < 0)) and (abs(xs[1+2*i]) <= delta_x_velocity):
                xs[1+2*i] *= 0.0
        
        
        # equation 1
        dpdt = 0.0
        if self.chi(p) >= 0:
            dpdt += - (self.sol.comp.p_suc * self.sol.comp.omega) * ((1 - self.chi(p)) * self.sol.comp.k * self.f_func_deriv(t) / self.f_func(t))
        else:
            dpdt += - (self.sol.comp.p_suc * self.sol.comp.omega) * ((1 + self.chi(p)) * self.sol.comp.k * self.f_func_deriv(t) / self.f_func(t))
        for i in range(len(self.sol.suc_plates)):
            if self.chi(p) >= 0:
                dpdt += - (self.sol.comp.p_suc * self.sol.comp.omega) * (- self.sol.suc_plates[i].alpha_gap(xs[0+2*i]) * self.sol.suc_plates[i].f_gap(xs[0+2*i]) * np.sqrt(2.0 * self.sol.comp.k ** 3.0/ (self.sol.comp.k - 1.0)) * np.sqrt(self.sol.comp.R * self.sol.comp.T_suc) * np.sqrt((1.0 - self.chi(p)) ** (2.0 / self.sol.comp.k) - (1.0 - self.chi(p)) ** ((self.sol.comp.k + 1) / self.sol.comp.k)) / (self.sol.comp.Fp * self.sol.comp.r * self.sol.comp.omega * self.f_func(t)) )
            else:
                dpdt += - (self.sol.comp.p_suc * self.sol.comp.omega) * (- self.sol.suc_plates[i].alpha_gap(xs[0+2*i]) * self.sol.suc_plates[i].f_gap(xs[0+2*i]) * np.sqrt(2.0 * self.sol.comp.k ** 3.0/ (self.sol.comp.k - 1.0)) * np.sqrt(self.sol.comp.R * self.sol.comp.T_suc) * np.sqrt((1.0 + self.chi(p)) ** (2.0 / self.sol.comp.k) - (1.0 + self.chi(p)) ** ((self.sol.comp.k + 1) / self.sol.comp.k)) / (self.sol.comp.Fp * self.sol.comp.r * self.sol.comp.omega * self.f_func(t)) )
              
        # equation 2
        for i in range(len(self.sol.suc_plates)):
            dx_derivdt[i] = (self.sol.suc_plates[i].Pd(xs[0+2*i], p, self.sol.comp.p_suc) - self.sol.suc_plates[i].Ppr(xs[0+2*i]) - self.sol.suc_plates[i].Ptr(xs[1+2*i]) - self.sol.suc_plates[i].G) / self.sol.suc_plates[i].m_priv
        
        # condition 3
        for i in range(len(self.sol.suc_plates)):
            if ((xs[0+2*i] <= 0) and (dx_derivdt[i] < 0)) or ((xs[0+2*i] >= self.sol.suc_plates[i].h) and (dx_derivdt[i] > 0)):
                dx_derivdt[i] = 0
        
        res = [dpdt]
        for i in range(len(self.sol.suc_plates)):
            res += [xs[1+2*i], dx_derivdt[i]]
        return res
























