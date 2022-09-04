

class ValveMove:
    def __init__(self, x, x_velocity):
        self.x = x
        self.x_velocity = x_velocity


class DataFrame:
    def __init__(self, time, pressure, chi, phi, xs_list, V, m=None, w=None):
        self.time = time
        self.pressure = pressure
        self.chi = chi
        self.phi = phi
        self.vm = [ValveMove(xs_list[0 + i * 2], xs_list[1 + i * 2]) for i in range(len(xs_list) // 2)]
        self.V = V
        self.m = m
        self.w = w
