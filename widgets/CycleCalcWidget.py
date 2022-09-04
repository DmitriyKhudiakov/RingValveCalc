from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QProgressBar, QLabel, QGroupBox, QSplitter, QTextEdit, QScrollArea, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from scripts.Frames import PistonCompressorInitFrame, RingInitFrame, CycleFrameResult
from ring_valve_calc.PistonCompressor import PistonCompressor
from ring_valve_calc.RingDis import RingDis
from ring_valve_calc.RingSuc import RingSuc
from ring_valve_calc.Solver import Solver
from ring_valve_calc.DiagramFrame import DiagramFrame
from scripts.formula import create_formula, convert_to_number, convert_from_number, is_appearance


RES_SUC = None
RES_DIS = None
CYCLE_FRAME_RESULT = None


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, fig, axes):
        self.fig = fig
        self.axes = axes
        super(MplCanvas, self).__init__(fig)


class CalcExternal(QThread):
    progress_val_int = pyqtSignal(int)
    message = pyqtSignal(str)
    
    def __init__(self, comp, cycle_calc_widget, pc_df, suc_df, dis_df, n_interations):
        super().__init__()
        self.cycle_calc_widget = cycle_calc_widget
        self.n_interations = n_interations
        
        self.comp = comp
        
        self.plates = []
        for sdf in suc_df:
            self.plates.append(RingSuc(b=sdf.b, f_gap_max=sdf.f_gap_max, h=sdf.h, m_priv=sdf.m_priv, cpr=sdf.cpr, x0=sdf.x0, tau=sdf.tau, theta=sdf.theta, velocity_limit=sdf.velocity_limit))
        for ddf in dis_df:
            self.plates.append(RingDis(b=ddf.b, f_gap_max=ddf.f_gap_max, h=ddf.h, m_priv=ddf.m_priv, cpr=ddf.cpr, x0=ddf.x0, tau=ddf.tau, theta=ddf.theta, velocity_limit=ddf.velocity_limit))
        
        self.solver = Solver(compressor=self.comp, progress_val_int=self.progress_val_int)
        
    
    def run(self):
        global RES_DIS, RES_SUC, CYCLE_FRAME_RESULT
        try:
            RES_SUC, RES_DIS = self.solver.run(plates=self.plates, n_interations=self.n_interations)
            CYCLE_FRAME_RESULT = CycleFrameResult(DiagramFrame(self.cycle_calc_widget.comp, RES_SUC, RES_DIS))
            self.message.emit("Done")
        except Exception as error:
            
            self.progress_val_int = 0
            self.message.emit(f"Error: {error}, Try set another init values...")


class Panel(QGroupBox):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()

    def init_ui(self):
        self.h_box = QHBoxLayout()
        self.v_box = QVBoxLayout()
        self.load_btn = QPushButton("Загрузить")
        self.load_btn.clicked.connect(self.load_btn_func)
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_btn_func)
        self.back_btn = QPushButton("Назад")
        self.back_btn.clicked.connect(self.back_btn_func)
        
        self.h_box.addWidget(self.back_btn)
        self.h_box.addStretch()
        self.h_box.addWidget(self.load_btn)
        self.h_box.addWidget(self.save_btn)
        
        self.v_box.addLayout(self.h_box)
        
        self.output_te = QTextEdit("> ")
        self.output_te.setReadOnly(True)
        self.output_te.setMaximumHeight(25)
        self.output_te.setStyleSheet("background-color: rgb(240, 240, 240)")
        self.output_te.setText("> Calculating...")
        
        self.v_box.addWidget(self.output_te)
        
        self.setLayout(self.v_box)

    def load_btn_func(self):
        pass

    def save_btn_func(self):
        pass

    def back_btn_func(self):
        pass


class ResultProcGroupBox(QGroupBox):
    def __init__(self, name, cycle_calc_widget):
        super().__init__(name)
        self.cycle_calc_widget = cycle_calc_widget
        self.scroll_area = QScrollArea()
        self.init_ui()
        
    def init_ui(self):
        self.main_v_box = QVBoxLayout()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.main_widget = QWidget()
        self.main_widget_v_box = QVBoxLayout()
        
        self.h_box_cycle_calc = QHBoxLayout()
        self.v_box_cycle_calc = QVBoxLayout()
        self.h_box_plot = QHBoxLayout()
        self.h_box_plot_suc = QHBoxLayout()
        self.h_box_plot_dis = QHBoxLayout()
        self.lbl_cycle_calc = QLabel("Характеристики рабочего цикла")
        self.lbl_plot_diagram = QLabel("Диаграмма рабочего цикла")
        self.lbl_plot_suc = QLabel("Диаграмма пластин всасывающих клапанов")
        self.lbl_plot_dis = QLabel("Диаграмма пластин нагнетательных клапанов")
        self.lbl_plot_diagram.setMinimumWidth(300)
        self.lbl_plot_diagram.setMaximumWidth(300) 
        self.lbl_plot_suc.setMinimumWidth(300)
        self.lbl_plot_suc.setMaximumWidth(300)
        self.lbl_plot_dis.setMinimumWidth(300)
        self.lbl_plot_dis.setMaximumWidth(300)
        self.lbl_cycle_calc.setMinimumWidth(300)
        self.lbl_cycle_calc.setMaximumWidth(300) 
        self.btn_cycle_calc = QPushButton("Показать")
        self.btn_plot_diagram = QPushButton("Построить")
        self.btn_plot_suc = QPushButton("Построить")
        self.btn_plot_dis = QPushButton("Построить")
        self.btn_cycle_calc.clicked.connect(self.btn_cycle_calc_func)
        self.btn_plot_diagram.clicked.connect(self.btn_plot_diagram_func)
        self.btn_plot_suc.clicked.connect(self.btn_plot_suc_func)
        self.btn_plot_dis.clicked.connect(self.btn_plot_dis_func)
        self.h_box_cycle_calc.addWidget(self.lbl_cycle_calc)
        self.h_box_plot.addWidget(self.lbl_plot_diagram)
        self.h_box_plot_suc.addWidget(self.lbl_plot_suc)
        self.h_box_plot_dis.addWidget(self.lbl_plot_dis)
        # self.h_box_plot.addStretch()
        self.h_box_cycle_calc.addWidget(self.btn_cycle_calc)
        self.h_box_plot.addWidget(self.btn_plot_diagram)
        self.h_box_plot_suc.addWidget(self.btn_plot_suc)
        self.h_box_plot_dis.addWidget(self.btn_plot_dis)
        self.h_box_cycle_calc.addStretch()
        self.h_box_plot.addStretch()
        self.h_box_plot_suc.addStretch()
        self.h_box_plot_dis.addStretch()
        
        self.v_box_cycle_calc.addLayout(self.h_box_cycle_calc)
        
        self.main_widget_v_box.addLayout(self.v_box_cycle_calc)
        self.main_widget_v_box.addLayout(self.h_box_plot)
        self.main_widget_v_box.addLayout(self.h_box_plot_suc)
        self.main_widget_v_box.addLayout(self.h_box_plot_dis)
        self.main_widget_v_box.addStretch()
        self.main_widget.setLayout(self.main_widget_v_box)
        
        self.scroll_area.setWidget(self.main_widget)
        self.main_v_box.addWidget(self.scroll_area)
        self.setLayout(self.main_v_box)

    def get_formula_lbl(self, name):
        if not is_appearance(formula=name, folder_path="formula"):
            create_formula(formula=f"{name}", path=f"formula\\{convert_to_number(name)}") 
        lbl = QLabel()
        lbl.setPixmap(QPixmap(f"formula\\{convert_to_number(name)}.png"))
        return lbl

    def btn_cycle_calc_func(self):
        if CYCLE_FRAME_RESULT is not None:
            if self.btn_cycle_calc.text() == "Показать":
                h_box_table = QHBoxLayout()
                table_result = QTableWidget()
                table_result.setEditTriggers(QTableWidget.NoEditTriggers)
                
                table_result.setStyleSheet("background-color: rgb(240, 240, 240);")
                table_result.setColumnCount(4)
                table_result.setRowCount(8)
                table_result.setHorizontalHeaderLabels(["Переменная", "Размерность", "Значение", "Описание"])
                
                table_result.setItem(0, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.L_suc}"))
                table_result.setItem(0, 3, QTableWidgetItem(f"Работа всасывания"))
                table_result.setItem(0, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(0, 0, self.get_formula_lbl(r"$L_{suc}$"))
                table_result.setItem(1, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.L_com}"))
                table_result.setItem(1, 3, QTableWidgetItem(f"Работа сжатия"))
                table_result.setItem(1, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(1, 0, self.get_formula_lbl(r"$L_{com}$"))
                table_result.setItem(2, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.L_dis}"))
                table_result.setItem(2, 3, QTableWidgetItem(f"Работа нагнетания"))
                table_result.setItem(2, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(2, 0, self.get_formula_lbl(r"$L_{dis}$"))
                table_result.setItem(3, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.L_exp}"))
                table_result.setItem(3, 3, QTableWidgetItem(f"Работа расширения"))
                table_result.setItem(3, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(3, 0, self.get_formula_lbl(r"$L_{exp}$"))
                table_result.setItem(4, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.L_sum}"))
                table_result.setItem(4, 3, QTableWidgetItem(f"Работа потребляемая компрессором"))
                table_result.setItem(4, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(4, 0, self.get_formula_lbl(r"$L_{sum}$"))
                table_result.setItem(5, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.N_sum}"))
                table_result.setItem(5, 3, QTableWidgetItem(f"Мощность компрессора"))
                table_result.setItem(5, 1, QTableWidgetItem(f"Вт"))
                table_result.setCellWidget(5, 0, self.get_formula_lbl(r"$N_{sum}$"))
                table_result.setItem(6, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.Loss_suc}"))
                table_result.setItem(6, 3, QTableWidgetItem(f"Потери на всасывании"))
                table_result.setItem(6, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(6, 0, self.get_formula_lbl(r"$Loss_{suc}$"))
                table_result.setItem(7, 2, QTableWidgetItem(f"{CYCLE_FRAME_RESULT.Loss_dis}"))
                table_result.setItem(7, 3, QTableWidgetItem(f"Потери на нагнетании"))
                table_result.setItem(7, 1, QTableWidgetItem(f"Дж"))
                table_result.setCellWidget(7, 0, self.get_formula_lbl(r"$Loss_{dis}$"))
                
                table_result.resizeColumnsToContents()
                self.btn_cycle_calc.setText("Скрыть")
                self.v_box_cycle_calc.addWidget(table_result)
            else:
                self.v_box_cycle_calc.itemAt(1).widget().setParent(None)
                self.btn_cycle_calc.setText("Показать")

    def btn_plot_diagram_func(self):
        index = self.cycle_calc_widget.v_box_sc.count() - 1
        while index >= 0:
            curr_widget = self.cycle_calc_widget.v_box_sc.itemAt(index).widget()
            if type(curr_widget) in [NavigationToolbar, MplCanvas]:
                curr_widget.setParent(None)
            index -=1
        
        if self.cycle_calc_widget.comp is not None:
            if RES_SUC is not None:
                if RES_DIS is not None:
                    diagram = DiagramFrame(self.cycle_calc_widget.comp, RES_SUC, RES_DIS)
                    
                    fig = Figure(figsize=(15, 20), dpi=80)
                    fig.set_facecolor("#f0f0f0")
                    axes = [fig.add_subplot(211), fig.add_subplot(212)]
                    for curr_axes in axes:
                        curr_axes.grid(True)
                        curr_axes.set_facecolor("#f0f0f0")
                    self.cycle_calc_widget.sc = MplCanvas(fig, axes)
                    
                    for index, df in enumerate([diagram]):
                        color = np.random.rand(3,)
                        self.cycle_calc_widget.sc.axes[0].set_title(f"Развернутая индикаторная диаграмма")
                        self.cycle_calc_widget.sc.axes[0].set_xlabel(r"$\phi,\ град$")
                        self.cycle_calc_widget.sc.axes[0].set_ylabel(r"$p,\ Па$")
                        self.cycle_calc_widget.sc.axes[0].plot(df.phi_expansion, df.p_expansion, c=color)
                        self.cycle_calc_widget.sc.axes[0].plot([df.phi_expansion[-1]] + df.phi_suction, [df.p_expansion[-1]] + df.p_suction, c=color)
                        self.cycle_calc_widget.sc.axes[0].plot(np.concatenate((np.array([df.phi_suction[-1]]), df.phi_compression), axis=0).tolist(), [df.p_suction[-1]] + df.p_compression, c=color)
                        self.cycle_calc_widget.sc.axes[0].plot(df.phi_discharge, df.p_discharge, c=color)
                        
                        self.cycle_calc_widget.sc.axes[1].set_title(f"Свернутая индикаторная диаграмма")
                        self.cycle_calc_widget.sc.axes[1].set_xlabel(r"$V,\ м^{3}$")
                        self.cycle_calc_widget.sc.axes[1].set_ylabel(r"$p,\ Па$")
                        self.cycle_calc_widget.sc.axes[1].plot(df.V_expansion, df.p_expansion)
                        self.cycle_calc_widget.sc.axes[1].plot(df.V_suction, df.p_suction)
                        self.cycle_calc_widget.sc.axes[1].plot(df.V_compression, df.p_compression)
                        self.cycle_calc_widget.sc.axes[1].plot(df.V_discharge, df.p_discharge)
                
                self.cycle_calc_widget.sc.draw()
                self.cycle_calc_widget.gp_plot.setVisible(True)
                self.cycle_calc_widget.toolbar = NavigationToolbar(self.cycle_calc_widget.sc, self.cycle_calc_widget)
                self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.toolbar)
                self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.sc)

    def btn_plot_suc_func(self):
        index = self.cycle_calc_widget.v_box_sc.count() - 1
        while index >= 0:
            curr_widget = self.cycle_calc_widget.v_box_sc.itemAt(index).widget()
            if type(curr_widget) in [NavigationToolbar, MplCanvas]:
                curr_widget.setParent(None)
            index -=1
        
        fig = Figure(figsize=(15, 20), dpi=80)
        fig.set_facecolor("#f0f0f0")
        axes = [fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
        for curr_axes in axes:
            curr_axes.grid(True)
            curr_axes.set_facecolor("#f0f0f0")
        self.cycle_calc_widget.sc = MplCanvas(fig, axes)
        
        
        if (RES_DIS is not None) and (RES_SUC is not None):
            for index, df_list in enumerate([RES_SUC]):
                for i in range(len(df_list[0].vm)):
                    chi = [df.chi for df in df_list]
                    phi = [np.degrees(df.phi) for df in df_list]
                    x = [df.vm[i].x * 1000 for df in df_list]
                    x_velocity = [df.vm[i].x_velocity for df in df_list]
                    pressure = [df.pressure for df in df_list]
                    
                    # self.sc.fig.suptitle(f"Pressure")
                    self.cycle_calc_widget.sc.axes[0].set_title(f"Pressure")
                    self.cycle_calc_widget.sc.axes[0].plot(phi, pressure, label=r"$pressure_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[0].legend()
                    
                    self.cycle_calc_widget.sc.axes[1].set_title(f"X")
                    self.cycle_calc_widget.sc.axes[1].set_ylabel(r"$x,\  мм$")
                    self.cycle_calc_widget.sc.axes[1].plot(phi, x, label=r"$x_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[1].legend()
                    
                    self.cycle_calc_widget.sc.axes[2].plot(phi, x_velocity, label=r"$\frac{dx}{dt}_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[2].legend()
                    self.cycle_calc_widget.sc.axes[2].set_ylabel(r"$velocity,\  \frac{м}{с}$")
                    self.cycle_calc_widget.sc.axes[2].set_xlabel(r"$\phi,\ град.$")
                    
                self.cycle_calc_widget.sc.draw()
        self.cycle_calc_widget.gp_plot.setVisible(True)
        self.cycle_calc_widget.toolbar = NavigationToolbar(self.cycle_calc_widget.sc, self.cycle_calc_widget)
        self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.toolbar)
        self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.sc)
    
    def btn_plot_dis_func(self):
        index = self.cycle_calc_widget.v_box_sc.count() - 1
        while index >= 0:
            curr_widget = self.cycle_calc_widget.v_box_sc.itemAt(index).widget()
            if type(curr_widget) in [NavigationToolbar, MplCanvas]:
                curr_widget.setParent(None)
            index -=1
        
        
        fig = Figure(figsize=(15, 20), dpi=80)
        fig.set_facecolor("#f0f0f0")
        axes = [fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
        for curr_axes in axes:
            curr_axes.grid(True)
            curr_axes.set_facecolor("#f0f0f0")
        self.cycle_calc_widget.sc = MplCanvas(fig, axes)
        if (RES_DIS is not None) and (RES_SUC is not None):
            for index, df_list in enumerate([RES_DIS]):
                for i in range(len(df_list[0].vm)):
                    chi = [df.chi for df in df_list]
                    phi = [np.degrees(df.phi) for df in df_list]
                    x = [df.vm[i].x * 1000 for df in df_list]
                    x_velocity = [df.vm[i].x_velocity for df in df_list]
                    pressure = [df.pressure for df in df_list]
                    
                    # self.sc.fig.suptitle(f"Pressure")
                    self.cycle_calc_widget.sc.axes[0].set_title(f"Pressure")
                    self.cycle_calc_widget.sc.axes[0].plot(phi, pressure, label=r"$pressure_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[0].legend()
                    
                    self.cycle_calc_widget.sc.axes[1].set_title(f"X")
                    self.cycle_calc_widget.sc.axes[1].set_ylabel(r"$x,\  мм$")
                    self.cycle_calc_widget.sc.axes[1].plot(phi, x, label=r"$x_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[1].legend()
                    
                    self.cycle_calc_widget.sc.axes[2].plot(phi, x_velocity, label=r"$\frac{dx}{dt}_{" + str(i + 1) + "}$")
                    self.cycle_calc_widget.sc.axes[2].legend()
                    self.cycle_calc_widget.sc.axes[2].set_ylabel(r"$velocity,\  \frac{м}{с}$")
                    self.cycle_calc_widget.sc.axes[2].set_xlabel(r"$\phi,\ град.$")
                    
                self.cycle_calc_widget.sc.draw()
        self.cycle_calc_widget.gp_plot.setVisible(True)
        self.cycle_calc_widget.toolbar = NavigationToolbar(self.cycle_calc_widget.sc, self.cycle_calc_widget)
        self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.toolbar)
        self.cycle_calc_widget.v_box_sc.addWidget(self.cycle_calc_widget.sc)


class CycleCalcWidget(QWidget):
    def __init__(self, data_init_frames, n_interations):
        super().__init__()
        self.data_init_frames = data_init_frames
        self.n_interations = n_interations
        self.pc_df = None
        self.suc_df = []
        self.dis_df = []
        for df in self.data_init_frames:
            if type(df) is PistonCompressorInitFrame:
                self.pc_df = df
            elif type(df) is RingInitFrame:
                if df.is_suction:
                    self.suc_df.append(df)
                else:
                    self.dis_df.append(df)
        self.init_ui()
        self.calc = None
        self.curr_result_suc = None
        self.curr_result_dis = None
        self.comp = None
        self.run_calc()

    def init_ui(self):
        self.setWindowTitle("Расчет цикла")
        self.h_box = QHBoxLayout()
        self.v_box_progress = QVBoxLayout()
        self.v_box = QVBoxLayout()
        self.v_box_sc = QVBoxLayout()
        self.horizontal_splitter = QSplitter(Qt.Horizontal)
        self.horizontal_splitter.setHandleWidth(20)
        self.setStyleSheet("QSplitter::handle {background :qradialgradient(cx:0.5, cy:0.5, radius: 0.3, fx:0.5, fy:0.5, stop:0 #5B5B5B, stop:1 #F0F0F0);; width: 5px; height: 5px; border-radius: 2px;}")
        
        
        self.left_widget = QWidget()
        self.v_box_panel = QVBoxLayout()
        # self.v_box_panel.addStretch(-1)
        
        self.panel = Panel("Панель управления")
        self.panel.setMaximumHeight(95)
        self.v_box_panel.addWidget(self.panel)
        
        self.gb_progress = QGroupBox("Прогресс")
        # self.gb_progress.setMaximumWidth(500)
        self.gb_progress.setMaximumHeight(95)
        self.lbl_state_calc = QLabel("Calculate...")
        self.lbl_state_calc.setMaximumWidth(400)
        self.lbl_state_calc.setMinimumWidth(400)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.v_box_progress.addWidget(self.progress)
        self.v_box_progress.addWidget(self.lbl_state_calc)
        self.gb_progress.setLayout(self.v_box_progress)
        self.v_box_panel.addWidget(self.gb_progress)
        
        self.res_gb = ResultProcGroupBox("Обработка результатов", self)
        self.v_box_panel.addWidget(self.res_gb)
        
        self.left_widget.setLayout(self.v_box_panel)
        self.horizontal_splitter.addWidget(self.left_widget)
        
        self.gp_plot = QGroupBox("Построение результатов")
        self.sc = None
        self.toolbar = None
        self.right_widget = QWidget()
        self.gp_plot.setLayout(self.v_box_sc)
        self.gp_plot.setVisible(False)
        self.horizontal_splitter.addWidget(self.gp_plot)
        
        self.horizontal_splitter.setSizes([300, 800])
        
        self.h_box.addWidget(self.horizontal_splitter)
        self.setLayout(self.h_box)
        
        self.showMaximized()

    def lbl_state_calc_changed(self, value):
        self.lbl_state_calc.setText(value)

    def progress_bar_changed(self, value):
        self.progress.setValue(value)

    def run_calc(self):
        self.comp = PistonCompressor(r=self.pc_df.r, lambda_R=self.pc_df.lambda_R, Dp=self.pc_df.Dp, am=self.pc_df.am, n=self.pc_df.n, k=self.pc_df.k, R=self.pc_df.R, p_dis=self.pc_df.p_dis, p_suc=self.pc_df.p_suc, T_suc=self.pc_df.T_suc, rho_suc=self.pc_df.rho_suc)
        self.calc = CalcExternal(self.comp, self, self.pc_df, self.suc_df, self.dis_df, self.n_interations)
        self.calc.progress_val_int.connect(self.progress_bar_changed)
        self.calc.message.connect(self.lbl_state_calc_changed)
        self.calc.start()

