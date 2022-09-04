import matplotlib.pyplot as plt
import numpy as np


def plot_diagram(diagram_frame_list):
    plt.figure(figsize=(15, 12), dpi=80)
    plt.rcParams['axes.grid'] = True
    for index, df in enumerate(diagram_frame_list):
        color = np.random.rand(3,)
        plt.subplot(2, 1, 1)
        plt.title(f"Развернутая индикаторная диаграмма")
        plt.xlabel(r"$\phi,\ град$")
        plt.ylabel(r"$p,\ Па$")
        plt.plot(df.phi_expansion, df.p_expansion, c=color)
        plt.plot([df.phi_expansion[-1]] + df.phi_suction, [df.p_expansion[-1]] + df.p_suction, c=color)
        plt.plot(np.concatenate((np.array([df.phi_suction[-1]]), df.phi_compression), axis=0).tolist(), [df.p_suction[-1]] + df.p_compression, c=color)
        plt.plot(df.phi_discharge, df.p_discharge, c=color)

        plt.subplot(2, 1, 2)
        plt.title(f"Свернутая индикаторная диаграмма")
        plt.xlabel(r"$V,\ м^{3}$")
        plt.ylabel(r"$p,\ Па$")
        plt.plot(df.V_expansion, df.p_expansion)
        plt.plot(df.V_suction, df.p_suction)
        plt.plot(df.V_compression, df.p_compression)
        plt.plot(df.V_discharge, df.p_discharge)
        
        L_suc = -np.trapz(y=df.p_suction, x=df.V_suction)
        L_com = -np.trapz(y=df.p_compression, x=df.V_compression)
        L_dis = -np.trapz(y=df.p_discharge, x=df.V_discharge)
        L_exp = -np.trapz(y=df.p_expansion, x=df.V_expansion)
        L_sum = L_suc + L_com + L_dis + L_exp
        N_sum = L_sum / df.t_cycle
        Loss_suc = abs(-np.trapz(y=[df.p_suction[0], df.p_suction[-1]], x=[df.V_suction[0], df.V_suction[-1]]) - L_suc)
        Loss_dis = abs(-np.trapz(y=[df.p_discharge[0], df.p_discharge[-1]], x=[df.V_discharge[0], df.V_discharge[-1]]) - L_dis)
        
        plt.plot([], [], label=f"Работа всысывания = {round(L_suc, 3)} Дж", color="none")
        plt.plot([], [], label=f"Работа сжатия = {round(L_com, 3)} Дж", color="none")
        plt.plot([], [], label=f"Работа нагнетания = {round(L_dis, 3)} Дж", color="none")
        plt.plot([], [], label=f"Работа расширения = {round(L_exp, 3)} Дж", color="none")
        plt.plot([], [], label=f"Работа потребляемая компрессором = {round(L_sum, 3)} Дж", color="none")
        plt.plot([], [], label=f"Потери на всасывании = {round(Loss_suc, 3)} Дж", color="none")
        plt.plot([], [], label=f"Потери на нагнетани = {round(Loss_dis, 3)} Дж", color="none")
        plt.plot([], [], label=f"Мощность компрессора = {round(N_sum, 3)} Вт", color="none")
        plt.legend()
    plt.show()

def plot_ring(df_lists, param_list=None):
    plt.figure(figsize=(15, 12), dpi=80)
    plt.rcParams['axes.grid'] = True
    for index, df_list in enumerate(df_lists):
        for i in range(len(df_list[0].vm)):
            chi = [df.chi for df in df_list]
            phi = [np.degrees(df.phi) for df in df_list]
            x = [df.vm[i].x * 1000 for df in df_list]
            x_velocity = [df.vm[i].x_velocity for df in df_list]
            pressure = [df.pressure for df in df_list]
            
            plt.subplot(3, 1, 1)
            plt.title(f"Pressure")
            plt.plot(phi, pressure, label=r"$pressure_{" + str(i + 1) + "}$")
            plt.legend()
            
            plt.subplot(3, 1, 2)
            plt.title(f"X")
            plt.ylabel(r"$x,\  мм$")
            plt.plot(phi, x, label=r"$x_{" + str(i + 1) + "}$")
            plt.legend()
            
            plt.subplot(3, 1, 3)
            plt.plot(phi, x_velocity, label=r"$\frac{dx}{dt}_{" + str(i + 1) + "}$")
            # plt.scatter(phi, x_velocity)
            plt.legend()
            plt.ylabel(r"$velocity,\  \frac{м}{с}$")
            plt.xlabel(r"$\phi,\ град.$")
        plt.show()
        