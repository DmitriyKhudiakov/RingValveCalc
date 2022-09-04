from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QEvent, QUrl
from widgets.MatplotlibWidget import MatplotlibWidget
from widgets.CycleInitWidget import CycleInitWidget


class MainButton(QPushButton):
    def __init__(self, css_style_filname, icon_name, icon_hover_name):
        super().__init__()
        self.css_style_filname = css_style_filname
        self.icon_name = icon_name
        self.icon_hover_name = icon_hover_name
        self.is_hover = False
        self.init_ui()

    def init_ui(self):
        with open(f"styles\\{self.css_style_filname}", "r") as f:
            btn_style = f.read()
            btn_style = btn_style.replace("image_name.png", self.icon_name)
            btn_style = btn_style.replace("image_name_hover.png", self.icon_hover_name)
            self.setStyleSheet(btn_style)

    def event(self, event):
        if event.type() == QEvent.HoverEnter and not self.is_hover:
            self.is_hover = True
        elif event.type() == QEvent.HoverLeave and self.is_hover:
            self.is_hover = False
        return super().event(event)

class StartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        
        self.hbox_btn = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox_panel = QVBoxLayout()
        
        self.panel_widget = QWidget()
        self.panel_widget.setFixedSize(100, 140)
        self.exit_btn = MainButton("panel_button.css", icon_name="exit.png", icon_hover_name="exit_hover.png")
        self.exit_btn.setFixedSize(30, 30)
        self.exit_btn.clicked.connect(self.closeEvent)
        self.exit_btn.setToolTip("Exit")
        self.collapse_btn = MainButton("panel_button.css", icon_name="collapse.png", icon_hover_name="collapse_hover.png")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.clicked.connect(self.collapse_widget)
        self.collapse_btn.setToolTip("Hide")
        self.info_btn = MainButton("panel_button.css", icon_name="info.png", icon_hover_name="info_hover.png")
        self.info_btn.setFixedSize(30, 30)
        self.info_btn.clicked.connect(self.open_info)
        self.info_btn.setToolTip("Info")
        self.vbox_panel.addWidget(self.exit_btn)
        self.vbox_panel.addWidget(self.collapse_btn)
        self.vbox_panel.addWidget(self.info_btn)
        self.panel_widget.setLayout(self.vbox_panel)
        
        self.open_btn = MainButton("main_button.css", icon_name="open.png", icon_hover_name="open_hover.png")
        self.open_btn.setFixedSize(100, 140)
        
        self.cycle_calc_btn = MainButton("main_button.css", icon_name="cycle.png", icon_hover_name="cycle_hover.png")
        self.cycle_calc_btn.clicked.connect(self.cycle_calc_btn_clicked)
        self.cycle_calc_btn.setFixedSize(100, 140)
        
        self.suc_valve_calc_btn = MainButton("main_button.css", icon_name="suc_valve.png", icon_hover_name="suc_valve_hover.png")
        self.suc_valve_calc_btn.setFixedSize(100, 140)
        
        self.dis_valve_calc_btn = MainButton("main_button.css", icon_name="dis_valve.png", icon_hover_name="dis_valve_hover.png")
        self.dis_valve_calc_btn.setFixedSize(100, 140)
        
        # self.hbox_btn.addWidget(self.open_btn)
        self.hbox_btn.addWidget(self.cycle_calc_btn)
        # self.hbox_btn.addWidget(self.suc_valve_calc_btn)
        # self.hbox_btn.addWidget(self.dis_valve_calc_btn)
        self.hbox_btn.addWidget(self.panel_widget)
        
        self.vbox.addLayout(self.hbox_btn)
        self.setLayout(self.vbox)

    def closeEvent(self, event):
        self.parent().closeEvent(event)

    def collapse_widget(self):
        self.parent().collapse_widget()

    def open_info(self):
        QDesktopServices.openUrl(QUrl("https://github.com/DmitriyKhudiakov/RingValveCalc"))

    def cycle_calc_btn_clicked(self):
        self.parent().active_widgets_list.append(CycleInitWidget(self.parent().active_widgets_list))













