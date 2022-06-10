import numpy as np
from scipy.integrate import solve_ivp
from RingDis import RingDis
from RingSuc import RingSuc
from SuctionModelRing import SuctionModelRing
from DischargeModelRing import DischargeModelRing
from DataFrame import DataFrame


class Solver:
    def __init__(self, compressor):
        self.comp = compressor
        self.relative_step = 0.001
    
    def run(self, plates, n_interations=1):
        # check the presence of suction and discharge plates
        plates_types = [False, False]
        for plate in plates:
            if isinstance(plate, (RingSuc)):
                plates_types[0] = True
            elif isinstance(plate, (RingDis)):
                plates_types[1] = True
        if plates_types[0] and plates_types[1]:
            self.suc_plates = [plate for plate in plates if isinstance(plate, (RingSuc))]
            self.dis_plates = [plate for plate in plates if isinstance(plate, (RingDis))]
            if isinstance(self.suc_plates[0], (RingSuc)):
                self.suc_model = SuctionModelRing(self)
            if isinstance(self.dis_plates[0], (RingDis)):
                self.dis_model = DischargeModelRing(self)
            # n_interations cycle for angle selection (find right compressor cycle params)
            # change compressor object
            # start solver params
            t_3 = np.radians(0) / self.comp.omega
            p_3 = self.comp.p_dis
            for _ in range(n_interations):
                self.comp.calc_cycle_suc(t_3=t_3, p_3=p_3)
                init_values = [self.comp.p_4] + [0.0 for _ in range(len(self.suc_plates) * 2)]
                result_suc, t_1, p_1 = self.solve(init_values=init_values, time_range=(self.comp.phi_4/self.comp.omega, (self.comp.phi_4+np.pi*2.0)/self.comp.omega), curr_plates=self.suc_plates, model=self.suc_model)
                self.comp.calc_cycle_dis(t_1=t_1, p_1=p_1)
                init_values = [self.comp.p_2] + [0.0 for _ in range(len(self.dis_plates) * 2)]
                result_dis, t_3, p_3 = self.solve(init_values=init_values, time_range=(self.comp.phi_2/self.comp.omega, (self.comp.phi_2+np.pi*2.0)/self.comp.omega), curr_plates=self.dis_plates, model=self.dis_model)
        return result_suc, result_dis

    def solve(self, init_values, time_range, curr_plates, model):
        result = self.calc_impact(time_range, init_values, curr_plates, model)
        return result, result[-1].time, result[-1].pressure

    def calc_impact(self, time_range, init_values, curr_plates, model):
        self.curr_plates = curr_plates
        def stop_condition(t, vars):
            xs = vars[1:]
            if any((((xs[0+2*i] <= 0) and (xs[1+2*i] < 0)) or ((xs[0+2*i] >= self.curr_plates[i].h) and (xs[1+2*i] > 0))) for i in range(len(self.curr_plates))):
                return 0
            else:
                return 1
        stop_condition.terminal = True
        # init start variables
        result = np.zeros((1, 1 + 2 * len(self.curr_plates)))[1:]
        time_result = np.zeros((1))[1:]
        current_time = time_range[0]
        # cycle for full time range
        while current_time < time_range[1]: 
            # integrate
            curr_result = solve_ivp(model.solve_ivp_function, (current_time, time_range[1]), init_values ,method='LSODA', events=stop_condition, max_step=(time_range[1] - time_range[0])*self.relative_step)
            # border conditions
            for i in range(len(self.curr_plates)):
                if curr_result.t[-1] < time_range[1]:
                    if (((curr_result.y[1 + 2 * i][-1] <= 0) and (curr_result.y[2 + 2 * i][-1] < 0)) or ((curr_result.y[1 + 2 * i][-1] >= self.curr_plates[i].h) and (curr_result.y[2 + 2 * i][-1] > 0))):
                        if curr_result.y[1 + 2 * i][-1] < abs(curr_result.y[1 + 2 * i][-1] - self.curr_plates[i].h):
                            curr_result.y[1 + 2 * i][-1] = 0
                        else:
                            curr_result.y[1 + 2 * i][-1] = self.curr_plates[i].h
                        if abs(curr_result.y[2 + 2 * i][-1]) < self.curr_plates[i].velocity_limit:
                            curr_result.y[2 + 2 * i][-1] = 0
                        else:
                            curr_result.y[2 + 2 * i][-1] *= (-self.curr_plates[i].theta)
            # stack rseult
            time_result = np.concatenate((time_result, curr_result.t), axis=0)
            result = np.concatenate((result, curr_result.y.transpose()), axis=0)
            # update init values
            current_time = curr_result.t[-1]
            init_values = [curr_result.y[0][-1]]
            for i in range(len(self.curr_plates)):
                init_values += [curr_result.y[1 + 2 * i][-1], curr_result.y[2 + 2 * i][-1]]
        return self.clear_results(self.result_equipment(result, time_result, model))

    def result_equipment(self, prev_res, time_result, model):
        return [DataFrame(time=curr_time, pressure=curr_p, chi=model.chi(curr_p), phi=model.phi(curr_time), xs_list=curr_xs, V=self.comp.Fp * self.comp.r * model.f_func(curr_time)) for curr_p, curr_xs, curr_time in zip(prev_res[:, 0], prev_res[:, 1:], time_result)]

    def clear_results(self, df_list):
        df_list.reverse()
        n_index = len(df_list)
        for df in df_list:
            n_index -= 1
            if any(curr_vm.x != 0 for curr_vm in df.vm):
                break
        df_list.reverse()
        return df_list[:n_index]





























