import numpy as np
from Ring import Ring


class RingDis(Ring):
    def __init__(self, b, f_gap_max, h, m_priv, cpr, x0, tau, theta, velocity_limit):
        super(RingDis, self).__init__(b, f_gap_max, h, m_priv, cpr, x0, tau, theta, velocity_limit)

    def alpha_gap(self, x):
        return 2.0366 * (x / self.b) ** 2 - 2.0884 * (x / self.b) + 1.0075

    def f_gap(self, x):
        return self.f_gap_max * x / self.h

    def rho_p(self, x):
        return (-21.977789 * (x / self.b) ** 3 + 17.95322 * (x / self.b) ** 2 - 3.45206 * (x / self.b) + 1.237686)

    def Pd(self, x, p, p_dis):
        return self.rho_p(x) * (p - p_dis) * self.f_c

    def Ppr(self, x): 
        return self.cpr * (x + self.x0)

    def Ptr(self, x_deriv):
        return 2.0 * 0.0125 * np.sqrt(self.cpr * self.m_priv) * x_deriv
