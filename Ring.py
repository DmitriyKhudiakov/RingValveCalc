
class Ring:
    def __init__(self, b, f_gap_max, h, m_priv, cpr, x0, tau, theta, velocity_limit):
        # Основные параметры
        # ширина прохода в седле, м
        self.b = b
        # площадь щели при полностью открытом клапане, м^3
        self.f_gap_max = f_gap_max
        # высота подъёма пластины, м
        self.h = h
        # приведенная масса (масса пластины + масса пружины / 3.0), кг
        self.m_priv = m_priv
        # постоянная пружины,  Н / м
        self.cpr = cpr
        # предварительное поджатие пружины, м
        self.x0 = x0
        # коэффициент демпфирования, Н * с / м
        self.tau = tau
        # коэффициент восстановления
        self.theta = theta
        # модуль пороговой скорости, при которой считается, что пластина останавливается
        self.velocity_limit = velocity_limit
        # площадь прохода в седла
        self.f_c = self.f_gap_max * 1.5
        # силы тяжести подвижного элемента Н
        self.G = 9.81 * self.m_priv
