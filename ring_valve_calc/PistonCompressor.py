import numpy as np


class PistonCompressor:
    def __init__(self, r, lambda_R, Dp, am, n, k, R, p_dis, p_suc, T_suc, rho_suc):
        # радиус кривошипа, м
        self.r = r
        # отношение радиуса кривошипа к длине шатуна
        self.lambda_R = lambda_R
        # диаметр поршня, м
        self.Dp = Dp
        # относительный мертвый объём
        self.am = am
        # число оборотов вала в минуту, об/мин
        self.n = n
        # коэффициент адиабаты
        self.k = k
        # газовая постоянная воздуха, Дж / (кг * К)
        self.R = R
        # давление нагнетания, Па
        self.p_dis = p_dis
        # давление всасывания, Па
        self.p_suc = p_suc
        # температура всасывания, К
        self.T_suc = T_suc
        # плотность воздуха на всасывании, кг/м^3
        self.rho_suc = rho_suc
        # частота вращения вала, рад/с
        self.omega = 2.0 * np.pi * self.n / 60.0
        # площадь поршня, м^2
        self.Fp = 0.25 * np.pi * self.Dp ** 2.0

    def phi(self, t):
        return self.omega * t

    def f_func(self, t):
        return 2.0 * self.am + 1.0 + self.lambda_R / 4.0 - np.cos(self.phi(t)) - self.lambda_R * np.cos(2.0 * self.phi(t)) / 4.0

    def calc_cycle_suc(self, t_3, p_3):
        # угол начала расширения газа из мертвого объема
        self.phi_3 = self.phi(t_3) % (2 * np.pi)
        self.p_3 = p_3
        self.V_3 = self.f_func(t_3) * self.Fp * self.r
        # адиабатное/поитропное расширение pv^k = const
        self.p_4 = self.p_suc
        self.V_4 = self.V_3 * (self.p_3 / self.p_4) ** (1 / self.k)
        # использовано выражение Fp * r * f(phi) = V |> f(phi) = V / (Fp * r)        
        time_volume = np.linspace(0, np.radians(180) / self.omega, 1000)
        volume = [self.Fp * self.r * self.f_func(curr_time) for curr_time in time_volume]
        phi_volume = [self.phi(curr_time) for curr_time in time_volume]
        self.phi_4 = phi_volume[min(range(len(volume)), key=lambda i: abs(volume[i]-self.V_4))]

    def calc_cycle_dis(self,t_1, p_1):
        self.phi_1 = self.phi(t_1)
        self.p_1 = p_1
        self.V_1 = self.f_func(t_1) * self.Fp * self.r
        self.p_2 = self.p_dis
        self.V_2 = self.V_1 * (self.p_1 / self.p_2) ** (1 / self.k)
        time_volume = np.linspace(np.radians(180) / self.omega, np.radians(360) / self.omega, 1000)
        volume = [self.Fp * self.r * self.f_func(curr_time) for curr_time in time_volume]
        phi_volume = [self.phi(curr_time) for curr_time in time_volume]
        self.phi_2 = phi_volume[min(range(len(volume)), key=lambda i: abs(volume[i]-self.V_2))]


















