from PistonCompressor import PistonCompressor
from RingDis import RingDis
from RingSuc import RingSuc
from Solver import Solver
from DiagramFrame import DiagramFrame
import view


def main():
    # Создание объекта компрессора с необходимыми параметрами
    comp = PistonCompressor(r=0.034, lambda_R=0.2165467, Dp=0.12, am=0.2, n=1500, k=1.4, R=287.1, p_dis=101325*3, p_suc=101325, T_suc=293.15, rho_suc=1.27)
    # Создание объектов колец всасывающего и нагнетательного клапанов с необходимыми параметрами
    ring_dis_1 = RingDis(b=0.003, f_gap_max=0.0005, h=0.0005, m_priv=0.008, cpr=10000, x0=0.003, tau=2.0, theta=0.2, velocity_limit=0.01)
    ring_dis_2 = RingDis(b=0.005, f_gap_max=0.0008, h=0.0005, m_priv=0.008, cpr=10000, x0=0.003, tau=2.0, theta=0.2, velocity_limit=0.01)
    ring_suc_1 = RingSuc(b=0.003, f_gap_max=0.0003, h=0.0005, m_priv=0.03, cpr=10000, x0=0.0003, tau=2.0, theta=0.2, velocity_limit=0.01)
    ring_suc_2 = RingSuc(b=0.003, f_gap_max=0.0005, h=0.0005, m_priv=0.03, cpr=10000, x0=0.0003, tau=2.0, theta=0.2, velocity_limit=0.01)
    
    # Решение
    solver = Solver(compressor=comp)
    result_suc, result_dis = solver.run(plates=[ring_dis_1, ring_dis_2, ring_suc_1, ring_suc_2], n_interations=5)
    
    # Построение результатов
    diagram_frame_1 = DiagramFrame(comp, result_suc, result_dis)
    view.plot_diagram([diagram_frame_1])
    view.plot_ring([result_suc])
    view.plot_ring([result_dis])


if __name__ == "__main__":
    main()
