from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QPushButton, QScrollArea, QSplitter, QComboBox, QTextEdit, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from widgets.DescriptionPaperWidget import DescriptionPaperWidget
from scripts.formula import create_formula, convert_to_number, convert_from_number, is_appearance
from widgets.CycleCalcWidget import CycleCalcWidget
from scripts.Frames import PistonCompressorInitFrame, RingInitFrame
import sqlite3


EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME = PistonCompressorInitFrame(r=0.034, lambda_R=0.2165467, Dp=0.12, am=0.25, n=1500, k=1.4, R=287.1, p_dis=101325*3, p_suc=101325, T_suc=293.15, rho_suc=1.27)
EXAMPLE_RING_INIT_FRAME_LIST = [
                                RingInitFrame(False, b=0.005, f_gap_max=0.001, h=0.001, m_priv=0.008, cpr=5000, x0=0.0008, tau=4.2, theta=0.1, velocity_limit=0.01),
                                RingInitFrame(False, b=0.005, f_gap_max=0.001, h=0.001, m_priv=0.008, cpr=6000, x0=0.0008, tau=4.2, theta=0.3, velocity_limit=0.01),
                                RingInitFrame(True, b=0.003, f_gap_max=0.0008, h=0.0005, m_priv=0.03, cpr=8000, x0=0.0006, tau=3.8, theta=0.1, velocity_limit=0.01),
                                RingInitFrame(True, b=0.003, f_gap_max=0.0008, h=0.0005, m_priv=0.03, cpr=10000, x0=0.0006, tau=3.8, theta=0.3, velocity_limit=0.01),
                                ]


class EditLineParam(QWidget):
    def __init__(self, param_name, param_desc):
        super().__init__()
        self.param_name = param_name
        self.param_desc = param_desc
        self.num = None
        self.init_ui()

    def init_ui(self):
        self.h_box = QHBoxLayout()
        
        # param icon pre generated (using matplotlib), or generate here
        if not is_appearance(formula=self.param_name, folder_path="formula"):
            create_formula(formula=f"{self.param_name}", path=f"formula\\{convert_to_number(self.param_name)}")    
        self.param_icon = QLabel()
        self.param_icon.setPixmap(QPixmap(f"formula\\{convert_to_number(self.param_name)}.png"))
        self.param_icon.setToolTip(self.param_desc)
        self.param_icon.setStyleSheet("QLabel:hover {background-color: rgb(200, 200, 200);}")
        
        self.lbl_error = QLabel("Введите значение...")
        self.lbl_error.setMinimumWidth(200)
        
        self.le = QLineEdit()
        self.le.setMinimumWidth(200)
        self.le.setMaximumWidth(200)
        
        self.le_error = QLabel()
        self.le_error.setMinimumWidth(200)
        
        
        self.h_box.addWidget(self.param_icon)
        self.h_box.addStretch()
        self.h_box.addWidget(self.le)
        self.h_box.addWidget(self.lbl_error)
        self.setLayout(self.h_box)

    def get_num(self):
        res = None
        try:
            res = float(self.le.text().replace(",", "."))
        except ValueError:
            self.lbl_error.setText("> Wrong values")
            return None
        self.lbl_error.setText("> Ok")
        return res



class Panel(QGroupBox):
    def __init__(self, name, piston_group_box, cycle_init_widget):
        super().__init__(name)
        self.cycle_init_widget = cycle_init_widget
        self.piston_group_box = piston_group_box
        self.setMaximumHeight(95)
        
        self.h_box = QHBoxLayout()
        self.h_box_btns = QHBoxLayout()
        self.v_box = QVBoxLayout()
        
        self.btn_calc = QPushButton("Рассчитать цикл")
        self.btn_calc.clicked.connect(self.calc_btn_func)
        self.example_calc = QPushButton("Пример данных")
        self.example_calc.clicked.connect(self.example_calc_func)
        self.load_calc = QPushButton("Загрузить")
        self.load_calc.clicked.connect(self.load_calc_func)
        self.save_calc = QPushButton("Сохранить")
        self.save_calc.clicked.connect(self.save_calc_func)
        self.lbl_iter = QLabel("Кол-во итераций:")
        self.n_iter_combo_box = QComboBox(self)
        for i in range(30):
            self.n_iter_combo_box.addItem(f"{i + 1}")
            # combo.activated[str].connect(self.onActivated)
        self.n_iter_combo_box.setCurrentIndex(1)
        self.h_box_btns.addWidget(self.load_calc)
        self.h_box_btns.addWidget(self.save_calc)
        self.h_box_btns.addWidget(self.example_calc)
        self.h_box_btns.addStretch()
        self.h_box_btns.addWidget(self.lbl_iter)
        self.h_box_btns.addWidget(self.n_iter_combo_box)
        self.h_box_btns.addWidget(self.btn_calc)
        
        self.output_te = QTextEdit("> ")
        self.output_te.setReadOnly(True)
        self.output_te.setMaximumHeight(25)
        self.output_te.setStyleSheet("background-color: rgb(240, 240, 240)")
        self.output_te.setText("> Задайте параметры компрессора и клапанов...")
        
        self.v_box.addLayout(self.h_box_btns)
        self.v_box.addWidget(self.output_te)
        self.setLayout(self.v_box)

    def example_calc_func(self):
        self.piston_group_box.v_box_params.itemAt(0).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.r}")
        self.piston_group_box.v_box_params.itemAt(1).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.lambda_R}")
        self.piston_group_box.v_box_params.itemAt(2).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.Dp}")
        self.piston_group_box.v_box_params.itemAt(3).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.am}")
        self.piston_group_box.v_box_params.itemAt(4).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.n}")
        self.piston_group_box.v_box_params.itemAt(5).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.k}")
        self.piston_group_box.v_box_params.itemAt(6).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.R}")
        self.piston_group_box.v_box_params.itemAt(7).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.p_dis}")
        self.piston_group_box.v_box_params.itemAt(8).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.p_suc}")
        self.piston_group_box.v_box_params.itemAt(9).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.T_suc}")
        self.piston_group_box.v_box_params.itemAt(10).widget().le.setText(f"{EXAMPLE_PISTON_COMPRESSOR_INIT_FRAME.rho_suc}")
        self.piston_group_box.btn_init.click()
        
        index = self.cycle_init_widget.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
            if type(curr_widget) in (SuctionRingBox, DischargeRingBox):
                curr_widget.setParent(None)
            index -=1
        
        suc_1 = SuctionRingBox(name="Параметры кольца всасывающего клапана", init_widget=self.cycle_init_widget)
        suc_1.v_box_params.itemAt(0).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].b}")
        suc_1.v_box_params.itemAt(1).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].f_gap_max}")
        suc_1.v_box_params.itemAt(2).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].h}")
        suc_1.v_box_params.itemAt(3).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].m_priv}")
        suc_1.v_box_params.itemAt(4).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].cpr}")
        suc_1.v_box_params.itemAt(5).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].x0}")
        suc_1.v_box_params.itemAt(6).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].tau}")
        suc_1.v_box_params.itemAt(7).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].theta}")
        suc_1.v_box_params.itemAt(8).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[2].velocity_limit}")
        suc_1.btn_init.click()
        self.cycle_init_widget.v_box_init.addWidget(suc_1)
        
        suc_2 = SuctionRingBox(name="Параметры кольца всасывающего клапана", init_widget=self.cycle_init_widget)
        suc_2.v_box_params.itemAt(0).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].b}")
        suc_2.v_box_params.itemAt(1).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].f_gap_max}")
        suc_2.v_box_params.itemAt(2).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].h}")
        suc_2.v_box_params.itemAt(3).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].m_priv}")
        suc_2.v_box_params.itemAt(4).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].cpr}")
        suc_2.v_box_params.itemAt(5).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].x0}")
        suc_2.v_box_params.itemAt(6).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].tau}")
        suc_2.v_box_params.itemAt(7).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].theta}")
        suc_2.v_box_params.itemAt(8).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[3].velocity_limit}")
        suc_2.btn_init.click()
        self.cycle_init_widget.v_box_init.addWidget(suc_2)
        
        dis_1 = DischargeRingBox(name="Параметры кольца нагнетательного клапана", init_widget=self.cycle_init_widget)
        dis_1.v_box_params.itemAt(0).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].b}")
        dis_1.v_box_params.itemAt(1).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].f_gap_max}")
        dis_1.v_box_params.itemAt(2).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].h}")
        dis_1.v_box_params.itemAt(3).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].m_priv}")
        dis_1.v_box_params.itemAt(4).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].cpr}")
        dis_1.v_box_params.itemAt(5).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].x0}")
        dis_1.v_box_params.itemAt(6).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].tau}")
        dis_1.v_box_params.itemAt(7).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].theta}")
        dis_1.v_box_params.itemAt(8).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[0].velocity_limit}")
        dis_1.btn_init.click()
        self.cycle_init_widget.v_box_init.addWidget(dis_1)
        
        dis_2 = DischargeRingBox(name="Параметры кольца нагнетательного клапана", init_widget=self.cycle_init_widget)
        dis_2.v_box_params.itemAt(0).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].b}")
        dis_2.v_box_params.itemAt(1).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].f_gap_max}")
        dis_2.v_box_params.itemAt(2).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].h}")
        dis_2.v_box_params.itemAt(3).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].m_priv}")
        dis_2.v_box_params.itemAt(4).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].cpr}")
        dis_2.v_box_params.itemAt(5).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].x0}")
        dis_2.v_box_params.itemAt(6).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].tau}")
        dis_2.v_box_params.itemAt(7).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].theta}")
        dis_2.v_box_params.itemAt(8).widget().le.setText(f"{EXAMPLE_RING_INIT_FRAME_LIST[1].velocity_limit}")
        dis_2.btn_init.click()
        self.cycle_init_widget.v_box_init.addWidget(dis_2)

    def calc_btn_func(self):
        self.piston_group_box.btn_init.click()
        index = self.cycle_init_widget.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
            if type(curr_widget) in [SuctionRingBox, DischargeRingBox]:
               curr_widget.btn_init.click()
            index -=1
        if self.parent().parent().parent().parent().check_data_ready_to_calc():
            df_list = [self.cycle_init_widget.init_params_box.data_frame]
            index = self.cycle_init_widget.v_box_init.count() - 1
            while index >= 0:
                curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
                if type(curr_widget) in [SuctionRingBox, DischargeRingBox]:
                    df_list.append(curr_widget.data_frame)
                index -=1
            self.parent().parent().parent().parent().active_widgets_list.append(CycleCalcWidget(df_list, int(self.n_iter_combo_box.currentText())))
        else:
            self.output_te.setText("> Wrong values")

    def load_calc_func(self):
        file_name = QFileDialog.getOpenFileName(self, 'Загрузить исходные данные', '*', "DB files (*.db)")[0]
        if file_name != "":
            connection = sqlite3.connect(f"{file_name}")
            cursor = connection.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = cursor.fetchall()
            if ('piston_compressor',) in table_names:
                cursor.execute("SELECT * from piston_compressor;")
                res_dict = {}
                for curr_res in cursor.fetchall():
                    res_dict[curr_res[0]] = curr_res[1]
                self.piston_group_box.data_frame.set_values(**res_dict)
                self.piston_group_box.update_piston_init_data()
            
            index = self.cycle_init_widget.v_box_init.count() - 1
            while index >= 0:
                curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
                if type(curr_widget) in (SuctionRingBox, DischargeRingBox):
                    curr_widget.setParent(None)
                index -=1
            
            if ('suction_rings',) in table_names:
                cursor.execute("SELECT * from suction_rings;")
                res = cursor.fetchall()
                for curr_n_ring in range(max([int(current_res[0]) for current_res in res])):
                    res_dict = {}
                    for curr_res in res:
                        if curr_res[0] == curr_n_ring + 1:
                            res_dict[curr_res[1]] = curr_res[2]
                    suc = SuctionRingBox(name="Параметры кольца всасывающего клапана", init_widget=self.cycle_init_widget)
                    suc.v_box_params.itemAt(0).widget().le.setText(f"{res_dict['b']}")
                    suc.v_box_params.itemAt(1).widget().le.setText(f"{res_dict['f_gap_max']}")
                    suc.v_box_params.itemAt(2).widget().le.setText(f"{res_dict['h']}")
                    suc.v_box_params.itemAt(3).widget().le.setText(f"{res_dict['m_priv']}")
                    suc.v_box_params.itemAt(4).widget().le.setText(f"{res_dict['cpr']}")
                    suc.v_box_params.itemAt(5).widget().le.setText(f"{res_dict['x0']}")
                    suc.v_box_params.itemAt(6).widget().le.setText(f"{res_dict['tau']}")
                    suc.v_box_params.itemAt(7).widget().le.setText(f"{res_dict['theta']}")
                    suc.v_box_params.itemAt(8).widget().le.setText(f"{res_dict['velocity_limit']}")
                    suc.btn_init.click()
                    self.cycle_init_widget.v_box_init.addWidget(suc)

            if ('discharge_rings',) in table_names:
                cursor.execute("SELECT * from discharge_rings;")
                res = cursor.fetchall()
                for curr_n_ring in range(max([int(current_res[0]) for current_res in res])):
                    res_dict = {}
                    for curr_res in res:
                        if curr_res[0] == curr_n_ring + 1:
                            res_dict[curr_res[1]] = curr_res[2]
                    dis = DischargeRingBox(name="Параметры кольца нагнетательного клапана", init_widget=self.cycle_init_widget)
                    dis.v_box_params.itemAt(0).widget().le.setText(f"{res_dict['b']}")
                    dis.v_box_params.itemAt(1).widget().le.setText(f"{res_dict['f_gap_max']}")
                    dis.v_box_params.itemAt(2).widget().le.setText(f"{res_dict['h']}")
                    dis.v_box_params.itemAt(3).widget().le.setText(f"{res_dict['m_priv']}")
                    dis.v_box_params.itemAt(4).widget().le.setText(f"{res_dict['cpr']}")
                    dis.v_box_params.itemAt(5).widget().le.setText(f"{res_dict['x0']}")
                    dis.v_box_params.itemAt(6).widget().le.setText(f"{res_dict['tau']}")
                    dis.v_box_params.itemAt(7).widget().le.setText(f"{res_dict['theta']}")
                    dis.v_box_params.itemAt(8).widget().le.setText(f"{res_dict['velocity_limit']}")
                    dis.btn_init.click()
                    self.cycle_init_widget.v_box_init.addWidget(dis)
                            
                            
            

    def save_calc_func(self):
        self.piston_group_box.data_frame.set_values(self.piston_group_box.v_box_params.itemAt(0).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(1).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(2).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(3).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(4).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(5).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(6).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(7).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(8).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(9).widget().get_num(),
                                                    self.piston_group_box.v_box_params.itemAt(10).widget().get_num(),
                                                    )
        index = self.cycle_init_widget.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
            
            if type(curr_widget) in (SuctionRingBox, DischargeRingBox):
                curr_widget.data_frame.set_values(True if type(curr_widget) is SuctionRingBox else False,
                                                  curr_widget.v_box_params.itemAt(0).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(1).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(2).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(3).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(4).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(5).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(6).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(7).widget().get_num(),
                                                  curr_widget.v_box_params.itemAt(8).widget().get_num(),
                                                  )       
            index -=1
        
        file_name = QFileDialog.getSaveFileName(self, 'Сохранить', '*', "DB files (*.db)")[0]
        if file_name != "":
            
            connection = sqlite3.connect(f"{file_name}")
            cursor = connection.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS piston_compressor;")
            cursor.execute("DROP TABLE IF EXISTS suction_rings;")
            cursor.execute("DROP TABLE IF EXISTS discharge_rings;")
            
            cursor.execute("CREATE TABLE IF NOT EXISTS piston_compressor(var_name TEXT, var_value REAL);")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'r'}', {self.piston_group_box.data_frame.r if self.piston_group_box.data_frame.r is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'lambda_R'}', {self.piston_group_box.data_frame.lambda_R if self.piston_group_box.data_frame.lambda_R is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'Dp'}', {self.piston_group_box.data_frame.Dp if self.piston_group_box.data_frame.Dp is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'am'}', {self.piston_group_box.data_frame.am if self.piston_group_box.data_frame.am is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'n'}', {self.piston_group_box.data_frame.n if self.piston_group_box.data_frame.n is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'k'}', {self.piston_group_box.data_frame.k if self.piston_group_box.data_frame.k is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'R'}', {self.piston_group_box.data_frame.R if self.piston_group_box.data_frame.R is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'p_dis'}', {self.piston_group_box.data_frame.p_dis if self.piston_group_box.data_frame.p_dis is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'p_suc'}', {self.piston_group_box.data_frame.p_suc if self.piston_group_box.data_frame.p_suc is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'T_suc'}', {self.piston_group_box.data_frame.T_suc if self.piston_group_box.data_frame.T_suc is not None else 0.0})")
            cursor.execute(f"INSERT INTO piston_compressor(var_name, var_value) VALUES('{'rho_suc'}', {self.piston_group_box.data_frame.rho_suc if self.piston_group_box.data_frame.rho_suc is not None else 0.0})")
            connection.commit()
            
            suc_ring_n = 0
            dis_ring_n = 0
            
            index = self.cycle_init_widget.v_box_init.count() - 1
            while index >= 0:
                curr_widget = self.cycle_init_widget.v_box_init.itemAt(index).widget()
                
                if type(curr_widget) is SuctionRingBox:
                    suc_ring_n += 1
                    cursor.execute("CREATE TABLE IF NOT EXISTS suction_rings(n_ring INT, var_name TEXT, var_value REAL);")
                    
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'b'}', {curr_widget.data_frame.b if type(curr_widget.data_frame.b) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'f_gap_max'}', {curr_widget.data_frame.f_gap_max if type(curr_widget.data_frame.f_gap_max) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'h'}', {curr_widget.data_frame.h if type(curr_widget.data_frame.h) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'m_priv'}', {curr_widget.data_frame.m_priv if type(curr_widget.data_frame.m_priv) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'cpr'}', {curr_widget.data_frame.cpr if type(curr_widget.data_frame.cpr) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'x0'}', {curr_widget.data_frame.x0 if type(curr_widget.data_frame.x0) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'tau'}', {curr_widget.data_frame.tau if type(curr_widget.data_frame.tau) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'theta'}', {curr_widget.data_frame.theta if type(curr_widget.data_frame.theta) is float else 0.0})")
                    cursor.execute(f"INSERT INTO suction_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'velocity_limit'}', {curr_widget.data_frame.velocity_limit if type(curr_widget.data_frame.velocity_limit) is float else 0.0})")
                
                if type(curr_widget) is SuctionRingBox:
                    dis_ring_n += 1
                    cursor.execute("CREATE TABLE IF NOT EXISTS discharge_rings(n_ring INT, var_name TEXT, var_value REAL);")
                    
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'b'}', {curr_widget.data_frame.b if type(curr_widget.data_frame.b) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'f_gap_max'}', {curr_widget.data_frame.f_gap_max if type(curr_widget.data_frame.f_gap_max) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'h'}', {curr_widget.data_frame.h if type(curr_widget.data_frame.h) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'m_priv'}', {curr_widget.data_frame.m_priv if type(curr_widget.data_frame.m_priv) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'cpr'}', {curr_widget.data_frame.cpr if type(curr_widget.data_frame.cpr) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'x0'}', {curr_widget.data_frame.x0 if type(curr_widget.data_frame.x0) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'tau'}', {curr_widget.data_frame.tau if type(curr_widget.data_frame.tau) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'theta'}', {curr_widget.data_frame.theta if type(curr_widget.data_frame.theta) is float else 0.0})")
                    cursor.execute(f"INSERT INTO discharge_rings(n_ring, var_name, var_value) VALUES({suc_ring_n}, '{'velocity_limit'}', {curr_widget.data_frame.velocity_limit if type(curr_widget.data_frame.velocity_limit) is float else 0.0})")
                
                index -=1
            
            connection.commit()
            connection.close()


class PistonCompressorGroupBox(QGroupBox):
    def __init__(self, name):
        super().__init__(name)
        
        self.data_frame = PistonCompressorInitFrame(None, None, None, None, None, None, None, None, None, None, None)
        
        self.setFont(QFont("Times New Roman", 16))
        self.v_box_params = QVBoxLayout()
        self.v_box_params.addWidget(EditLineParam(param_name=r"$r,\ м$", param_desc="Радиус кривошипа"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\lambda_{R}$", param_desc="Отношение радиуса кривошипа к длине шатуна"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$D_{п},\ м$", param_desc="Диаметр поршня"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$a_{m}$", param_desc="Относительный мертвый объём"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$n,\ \frac{об}{мин}$", param_desc="Число оборотов вала в минуту"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$k$", param_desc="Коэффициент адиабаты"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$R,\ \frac{Дж}{кг\cdot k}$", param_desc="Газовая постоянная воздуха"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$p_{н},\ Па$", param_desc="Давление нагнетания"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$p_{вс},\ Па$", param_desc="Давление всасывания"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$Т_{вс},\ К$", param_desc="Температура всасывания"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\rho_{вс},\ \frac{кг}{м^3}$", param_desc="Плотность воздуха на всасывании"))
        
        self.h_box_panel_btn = QHBoxLayout()
        
        self.te_info = QTextEdit("> Введите значения...")
        self.te_info.setReadOnly(True)
        self.te_info.setMaximumHeight(25)
        self.te_info.setStyleSheet("background-color: rgb(240, 240, 240)")
        
        
        
        self.btn_init = QPushButton("Задать")
        self.btn_init.clicked.connect(self.btn_init_func)
        
        self.h_box_panel_btn.addWidget(self.te_info)
        self.h_box_panel_btn.addStretch()
        self.h_box_panel_btn.addWidget(self.btn_init)
        self.v_box_params.addLayout(self.h_box_panel_btn)
        
        self.setLayout(self.v_box_params)

    def btn_init_func(self):
        vl = []
        for i in range(11):
            vl.append(self.v_box_params.itemAt(i).widget().get_num())
        self.data_frame.set_values(r=vl[0], lambda_R=vl[1], Dp=vl[2], am=vl[3], n=vl[4], k=vl[5], R=vl[6], p_dis=vl[7], p_suc=vl[8], T_suc=vl[9], rho_suc=vl[10])
        if None in vl:
            self.te_info.setText("> Wrong values")
            self.parent().parent().parent().parent().parent().parent().panel.output_te.setText("> Wrong values")
        else:
            self.te_info.setText("> Ok")
            index = self.parent().parent().parent().parent().parent().parent().v_box_init.count() - 1
            is_suc_valves = False
            is_dis_valves = False
            is_false = True
            while index >= 0:
                curr_widget = self.parent().parent().parent().parent().parent().parent().v_box_init.itemAt(index).widget()
                if type(curr_widget) is SuctionRingBox:
                    is_suc_valves = True
                    if curr_widget.te_info.toPlainText() != "> Ok":
                        is_false = False
                if type(curr_widget) is DischargeRingBox:
                    is_dis_valves = True
                    if curr_widget.te_info.toPlainText() != "> Ok":
                        is_false = False
                index -=1
            if is_suc_valves and is_dis_valves and is_false:
                self.parent().parent().parent().parent().parent().parent().panel.output_te.setText("> Ok")
            if is_false:
                if not is_suc_valves:
                    self.parent().parent().parent().parent().parent().parent().panel.output_te.setText("> Задайте параметры колец всасывающего клапана")
            if is_false:
                if not is_dis_valves:
                    self.parent().parent().parent().parent().parent().parent().panel.output_te.setText("> Задайте параметры колец нагнетательного клапана")
            


    def update_piston_init_data(self):
        self.v_box_params.itemAt(0).widget().le.setText(str(self.data_frame.r))
        self.v_box_params.itemAt(1).widget().le.setText(str(self.data_frame.lambda_R))
        self.v_box_params.itemAt(2).widget().le.setText(str(self.data_frame.Dp))
        self.v_box_params.itemAt(3).widget().le.setText(str(self.data_frame.am))
        self.v_box_params.itemAt(4).widget().le.setText(str(self.data_frame.n))
        self.v_box_params.itemAt(5).widget().le.setText(str(self.data_frame.k))
        self.v_box_params.itemAt(6).widget().le.setText(str(self.data_frame.R))
        self.v_box_params.itemAt(7).widget().le.setText(str(self.data_frame.p_dis))
        self.v_box_params.itemAt(8).widget().le.setText(str(self.data_frame.p_suc))
        self.v_box_params.itemAt(9).widget().le.setText(str(self.data_frame.T_suc))
        self.v_box_params.itemAt(10).widget().le.setText(str(self.data_frame.rho_suc))
        self.btn_init.click()


class SuctionRingBox(QGroupBox):
    def __init__(self, name, init_widget):
        super().__init__(name)
        self.init_widget = init_widget
        
        self.data_frame = RingInitFrame(None, None, None, None, None, None, None, None, None, None)
        
        self.setFont(QFont("Times New Roman", 16))
        self.v_box_params = QVBoxLayout()
        self.v_box_params.addWidget(EditLineParam(param_name=r"$b,\ м$", param_desc="Ширина прохода в седле"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$f_{щ.max},\ м^3$", param_desc="Площадь щели при полностью открытом клапане"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$h,\ м$", param_desc="Высота подъёма пластины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$m_{прив},\ кг$", param_desc="Приведенная масса"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$c_{пр},\ \frac{Н}{м}$", param_desc="Постоянная пружины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$x_{0},\ м$", param_desc="Предварительное поджатие пружины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\tau,\ \frac{Н\cdot с}{м}$", param_desc="Коэффициент демпфирования"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\Theta$", param_desc="Коэффициент восстановления"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$V_{limit}$", param_desc="Модуль пороговой скорости, при которой считается, что пластина останавливается"))
        
        self.h_box_panel_btn = QHBoxLayout()
        
        self.te_info = QTextEdit("> Введите значения...")
        self.te_info.setReadOnly(True)
        self.te_info.setMaximumHeight(25)
        self.te_info.setStyleSheet("background-color: rgb(240, 240, 240)")
        
        self.btn_init = QPushButton("Задать")
        self.btn_init.clicked.connect(self.btn_init_func)
        
        self.btn_delete_box = QPushButton("Убрать форму")
        self.btn_delete_box.clicked.connect(self.btn_delete_box_func)
        
        self.h_box_panel_btn.addWidget(self.te_info)
        self.h_box_panel_btn.addStretch()
        self.h_box_panel_btn.addWidget(self.btn_delete_box)
        self.h_box_panel_btn.addWidget(self.btn_init)
        self.v_box_params.addLayout(self.h_box_panel_btn)
        
        self.setLayout(self.v_box_params)

    def btn_init_func(self):
        vl = []
        for i in range(9):
            vl.append(self.v_box_params.itemAt(i).widget().get_num())
        self.data_frame.set_values(True, b=vl[0], f_gap_max=vl[1], h=vl[2], m_priv=vl[3], cpr=vl[4], x0=vl[5], tau=vl[6], theta=vl[7], velocity_limit=vl[8])
        if None in vl:
            self.te_info.setText("> Wrong values")
            self.parent().parent().parent().parent().parent().parent().panel.output_te.setText("> Wrong values")
        else:
            self.te_info.setText("> Ok")
            index = self.init_widget.v_box_init.count() - 1
            is_dis_valves = False
            is_false = True
            is_piston_right = True if self.init_widget.init_params_box.te_info.toPlainText() == "> Ok" else False
            while index >= 0:
                curr_widget = self.init_widget.v_box_init.itemAt(index).widget()
                if type(curr_widget) is DischargeRingBox:
                    is_dis_valves = True
                    if curr_widget.te_info.toPlainText() != "> Ok":
                        is_false = False
                index -=1
            if is_dis_valves and is_false and is_piston_right:
                self.init_widget.panel.output_te.setText("> Ok")
                self.te_info.setText("> Ok")
            if is_false:
                if not is_dis_valves:
                    self.init_widget.panel.output_te.setText("> Задайте параметры колец нагнетательного клапана")
            
    
    def btn_delete_box_func(self):
        self.setParent(None)

class DischargeRingBox(QGroupBox):
    def __init__(self, name, init_widget):
        super().__init__(name)
        self.init_widget = init_widget
        
        self.data_frame = RingInitFrame(None, None, None, None, None, None, None, None, None, None)
        
        self.setFont(QFont("Times New Roman", 16))
        self.v_box_params = QVBoxLayout()
        self.v_box_params.addWidget(EditLineParam(param_name=r"$b,\ м$", param_desc="Ширина прохода в седле"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$f_{щ.max},\ м^3$", param_desc="Площадь щели при полностью открытом клапане"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$h,\ м$", param_desc="Высота подъёма пластины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$m_{прив},\ кг$", param_desc="Приведенная масса"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$c_{пр},\ \frac{Н}{м}$", param_desc="Постоянная пружины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$x_{0},\ м$", param_desc="Предварительное поджатие пружины"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\tau,\ \frac{Н\cdot с}{м}$", param_desc="Коэффициент демпфирования"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$\Theta$", param_desc="Коэффициент восстановления"))
        self.v_box_params.addWidget(EditLineParam(param_name=r"$V_{limit}$", param_desc="Модуль пороговой скорости, при которой считается, что пластина останавливается"))
        
        self.h_box_panel_btn = QHBoxLayout()
        
        self.te_info = QTextEdit("> Введите значения...")
        self.te_info.setReadOnly(True)
        self.te_info.setMaximumHeight(25)
        self.te_info.setStyleSheet("background-color: rgb(240, 240, 240)")
        
        self.btn_init = QPushButton("Задать")
        self.btn_init.clicked.connect(self.btn_init_func)
        
        self.btn_delete_box = QPushButton("Убрать форму")
        self.btn_delete_box.clicked.connect(self.btn_delete_box_func)
        
        self.h_box_panel_btn.addWidget(self.te_info)
        self.h_box_panel_btn.addStretch()
        self.h_box_panel_btn.addWidget(self.btn_delete_box)
        self.h_box_panel_btn.addWidget(self.btn_init)
        self.v_box_params.addLayout(self.h_box_panel_btn)
        
        self.setLayout(self.v_box_params)

    def btn_init_func(self):
        vl = []
        for i in range(9):
            vl.append(self.v_box_params.itemAt(i).widget().get_num())
        self.data_frame.set_values(False, b=vl[0], f_gap_max=vl[1], h=vl[2], m_priv=vl[3], cpr=vl[4], x0=vl[5], tau=vl[6], theta=vl[7], velocity_limit=vl[8])
        if None in vl:
            self.te_info.setText("> Wrong values")
            self.init_widget.panel.output_te.setText("> Wrong values")
        else:
            self.te_info.setText("> Ok")
            
            index = self.init_widget.v_box_init.count() - 1
            is_suc_valves = False
            is_false = True
            is_piston_right = True if self.init_widget.init_params_box.te_info.toPlainText() == "> Ok" else False
            while index >= 0:
                curr_widget = self.init_widget.v_box_init.itemAt(index).widget()
                if type(curr_widget) is SuctionRingBox:
                    is_suc_valves = True
                    if curr_widget.te_info.toPlainText() != "> Ok":
                        is_false = False
                index -=1
            if is_suc_valves and is_false and is_piston_right:
                self.init_widget.panel.output_te.setText("> Ok")
                self.te_info.setText("> Ok")
            if is_false:
                if not is_suc_valves:
                    self.init_widget.panel.output_te.setText("> Задайте параметры колец всасывающего клапана")

    def btn_delete_box_func(self):
        self.setParent(None)

class CycleInitWidget(QWidget):
    def __init__(self, active_widgets_list):
        super().__init__()
        self.active_widgets_list = active_widgets_list
        self.init_ui()

    def init_ui(self):
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Задание параметров цикла")
        self.main_widget = QWidget()
        self.main_box = QHBoxLayout()
        
        self.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.v_box_layout = QVBoxLayout()
        self.h_box_layout_head = QHBoxLayout()
        
        self.group_box_head = QGroupBox("Задание параметров цикла")
        self.group_box_head.setFont(QFont("Times New Roman", 34))
        # self.h_box_layout_head.addWidget(self.lbl_head)
        self.group_box_head_layout = QVBoxLayout()
        self.group_box_head.setLayout(self.group_box_head_layout)
        
        self.scroll_left_area = QScrollArea()
        
        self.h_box_layout_params = QHBoxLayout()
        self.left_part_widget = QWidget()
        self.left_part_v_box = QVBoxLayout()
        self.v_box_init = QVBoxLayout()
        
        # self.init_params_box = QGroupBox("Задание переменных компрессора")
        self.init_params_box = PistonCompressorGroupBox("Задание переменных компрессора")
        self.v_box_init.addWidget(self.init_params_box)
        self.left_part_v_box.addLayout(self.v_box_init)
        
        self.lbl_add_suction_rings = QLabel("Добавить кольцо всасывающего клапана")
        self.lbl_add_suction_rings.setFont(QFont("Times New Roman", 16))
        self.btn_add_suction_ring = QPushButton()
        self.btn_add_suction_ring.setIcon(QIcon("images\\icons\\plus_btn.png"))
        self.btn_add_suction_ring.clicked.connect(self.btn_add_suction_ring_func)
        self.h_box_add_suction_rings = QHBoxLayout()
        self.h_box_add_suction_rings.addStretch()
        self.h_box_add_suction_rings.addWidget(self.lbl_add_suction_rings)
        self.h_box_add_suction_rings.addWidget(self.btn_add_suction_ring)
        self.h_box_add_suction_rings.addStretch()
        self.left_part_v_box.addLayout(self.h_box_add_suction_rings)
        
        self.lbl_add_discharge_rings = QLabel("Добавить кольцо нагнетательнго клапана")
        self.lbl_add_discharge_rings.setFont(QFont("Times New Roman", 16))
        self.btn_add_discharge_ring = QPushButton()
        self.btn_add_discharge_ring.setIcon(QIcon("images\\icons\\plus_btn.png"))
        self.btn_add_discharge_ring.clicked.connect(self.btn_add_discharge_ring_func)
        self.h_box_add_discharge_rings = QHBoxLayout()
        self.h_box_add_discharge_rings.addStretch()
        self.h_box_add_discharge_rings.addWidget(self.lbl_add_discharge_rings)
        self.h_box_add_discharge_rings.addWidget(self.btn_add_discharge_ring)
        self.h_box_add_discharge_rings.addStretch()
        self.left_part_v_box.addLayout(self.h_box_add_discharge_rings)
        
        self.left_part_v_box.addStretch()
        
        self.group_box_head_layout.addLayout(self.left_part_v_box)
        self.left_part_widget.setLayout(self.group_box_head_layout)
        self.group_box_head.setLayout(self.group_box_head_layout)
        
        
        self.scroll_left_area.setWidget(self.group_box_head)
        self.scroll_left_area.setWidgetResizable(True)
        
        self.desc_widget = DescriptionPaperWidget("Описание расчета цикла", "papers\\desc_cycle.html")
        self.panel = Panel("Панель управления", self.init_params_box, self)
        self.right_area = QWidget()
        self.right_area_v_box = QVBoxLayout()
        self.right_area_v_box.addWidget(self.panel)
        self.right_area_v_box.addWidget(self.desc_widget)
        self.right_area.setLayout(self.right_area_v_box)
        
        
        self.horizontal_splitter = QSplitter(Qt.Horizontal)
        self.horizontal_splitter.setHandleWidth(20)
        self.setStyleSheet("QSplitter::handle {background :qradialgradient(cx:0.5, cy:0.5, radius: 0.3, fx:0.5, fy:0.5, stop:0 #5B5B5B, stop:1 #F0F0F0);; width: 5px; height: 5px; border-radius: 2px;}")
        
        self.horizontal_splitter.addWidget(self.scroll_left_area)
        self.horizontal_splitter.addWidget(self.right_area)
        self.horizontal_splitter.setSizes([800,800])
        
        self.v_box_layout.addLayout(self.h_box_layout_head)
        self.v_box_layout.addWidget(self.horizontal_splitter)
        
        self.main_widget.setLayout(self.v_box_layout)
        self.main_box.addWidget(self.main_widget)
        self.setLayout(self.main_box)
        
        self.showMaximized()

    def btn_add_suction_ring_func(self):
        self.v_box_init.addWidget(SuctionRingBox(name="Параметры кольца всасывающего клапана", init_widget=self))

    def btn_add_discharge_ring_func(self):
        self.v_box_init.addWidget(DischargeRingBox(name="Параметры кольца нагнетательного клапана", init_widget=self))

    def check_data_ready_to_calc(self):
        
        # click all init btns
        self.init_params_box.btn_init.click()
        index = self.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.v_box_init.itemAt(index).widget()
            if type(curr_widget) in [SuctionRingBox, DischargeRingBox]:
                curr_widget.btn_init.click()
            index -=1
        
        # piston compressor
        is_right = True
        index = self.init_params_box.v_box_params.count() - 1
        while index >= 0:
            curr_widget = self.init_params_box.v_box_params.itemAt(index).widget()
            if type(curr_widget) is EditLineParam:
                if curr_widget.lbl_error.text() != "> Ok":
                    is_right = False
            index -=1
        
        # suction_rings
        is_suc = False
        is_suc_right = True
        index = self.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.v_box_init.itemAt(index).widget()
            if type(curr_widget) is SuctionRingBox:
                is_suc = True
                if curr_widget.te_info.toPlainText() != "> Ok":
                    is_suc_right = False
            index -=1
        
        #discharge_rings
        is_dis = False
        is_dis_right = True
        index = self.v_box_init.count() - 1
        while index >= 0:
            curr_widget = self.v_box_init.itemAt(index).widget()
            if type(curr_widget) is DischargeRingBox:
                is_dis = True
                if curr_widget.te_info.toPlainText() != "> Ok":
                    is_dis_right = False
            index -=1
        
        if is_suc and is_suc_right and is_dis and is_dis_right and is_right:
            return True
        else:
            return False
        
