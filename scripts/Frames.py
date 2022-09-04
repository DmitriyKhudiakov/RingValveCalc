import numpy as np


class PistonCompressorInitFrame:
    def __init__(self, r, lambda_R, Dp, am, n, k, R, p_dis, p_suc, T_suc, rho_suc):
        self.r = r
        self.lambda_R = lambda_R
        self.Dp = Dp
        self.am = am
        self.n = n
        self.k = k
        self.R = R
        self.p_dis = p_dis
        self.p_suc = p_suc
        self.T_suc = T_suc
        self.rho_suc = rho_suc

    def set_values(self, r, lambda_R, Dp, am, n, k, R, p_dis, p_suc, T_suc, rho_suc):
        self.r = r
        self.lambda_R = lambda_R
        self.Dp = Dp
        self.am = am
        self.n = n
        self.k = k
        self.R = R
        self.p_dis = p_dis
        self.p_suc = p_suc
        self.T_suc = T_suc
        self.rho_suc = rho_suc


class RingInitFrame:
    def __init__(self, is_suction, b, f_gap_max, h, m_priv, cpr, x0, tau, theta, velocity_limit):
        self.is_suction = is_suction
        self.b = b
        self.f_gap_max = f_gap_max
        self.h = h
        self.m_priv = m_priv
        self.cpr = cpr 
        self.x0 = x0 
        self.tau = tau 
        self.theta = theta
        self.velocity_limit = velocity_limit

    def set_values(self, is_suction, b, f_gap_max, h, m_priv, cpr, x0, tau, theta, velocity_limit):
        self.is_suction = is_suction
        self.b = b
        self.f_gap_max = f_gap_max
        self.h = h
        self.m_priv = m_priv
        self.cpr = cpr 
        self.x0 = x0 
        self.tau = tau 
        self.theta = theta
        self.velocity_limit = velocity_limit


class CycleFrameResult():
    def __init__(self, df):
        # Работа всысывания
        self.L_suc = -np.trapz(y=df.p_suction, x=df.V_suction)
        # Работа сжатия
        self.L_com = -np.trapz(y=df.p_compression, x=df.V_compression)
        # Работа нагнетания
        self.L_dis = -np.trapz(y=df.p_discharge, x=df.V_discharge)
        # Работа расширения
        self.L_exp = -np.trapz(y=df.p_expansion, x=df.V_expansion)
        # Работа потребляемая компрессором
        self.L_sum = self.L_suc + self.L_com + self.L_dis + self.L_exp
        # Мощность компрессора
        self.N_sum = self.L_sum / df.t_cycle
        # Потери на всасывании
        self.Loss_suc = abs(-np.trapz(y=[df.p_suction[0], df.p_suction[-1]], x=[df.V_suction[0], df.V_suction[-1]]) - self.L_suc)
        # Потери на нагнетани
        self.Loss_dis = abs(-np.trapz(y=[df.p_discharge[0], df.p_discharge[-1]], x=[df.V_discharge[0], df.V_discharge[-1]]) - self.L_dis)
        




















