import math as m
import numpy as np


class DiagramFrame:
    def __init__(self, prm, result_suc, result_dis):
        self.prm = prm
        self.phi_expansion = np.linspace(m.degrees(prm.phi_3), m.degrees(prm.phi_4), 300)
        self.p_expansion = [prm.p_3 * (prm.V_3 / (prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega))) ** prm.k for phi in self.phi_expansion]
        self.V_expansion = [prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega) for phi in self.phi_expansion]
        self.phi_suction = [m.degrees(res.phi) for res in result_suc]
        self.p_suction = [res.pressure for res in result_suc]
        self.V_suction = [prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega) for phi in self.phi_suction]
        self.phi_compression = np.linspace(m.degrees(prm.phi_1), m.degrees(prm.phi_2), 300)
        self.p_compression = [prm.p_1 * (prm.V_1 / (prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega))) ** prm.k for phi in self.phi_compression]
        self.V_compression = [prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega) for phi in self.phi_compression]
        self.phi_discharge = [m.degrees(res.phi) for res in result_dis]
        self.p_discharge = [res.pressure for i, res in enumerate(result_dis) if i < len(self.phi_discharge)]
        self.V_discharge = [prm.Fp * prm.r * prm.f_func(m.radians(phi) / prm.omega) for phi in self.phi_discharge]
        self.full_pressure_list = self.p_expansion + self.p_suction + self.p_compression + self.p_discharge
        self.full_phi_list = self.phi_expansion.tolist() + self.phi_suction + self.phi_compression.tolist() + self.phi_discharge
        self.full_time_list = [m.radians(curr_phi) / prm.omega for curr_phi in self.full_phi_list]
        self.full_V_list = [prm.Fp * prm.r * prm.f_func(curr_time) for curr_time in self.full_time_list]
        self.t_cycle = m.radians(360.0) / prm.omega
