from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDesktopWidget, QLabel
from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from widgets.MatplotlibWidget import MatplotlibWidget
from widgets.StartWidget import StartWidget


class MainWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.active_widgets_list = []
        self.init_ui()
        
    def init_ui(self):
        screen_shape = QDesktopWidget().screenGeometry()
        window_size =  QtCore.QSize(400, 275)
        self.setGeometry((screen_shape.width() - window_size.width()) // 2, (screen_shape.height() - window_size.height()) // 2,\
                         window_size.width(), window_size.height())
        self.old_pos = QtCore.QPoint((screen_shape.width() - window_size.width()) // 2, (screen_shape.height() - window_size.height()) // 2)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.container = QWidget(self)
        self.hbox = QHBoxLayout(self.container)
        self.vbox = QVBoxLayout()
        
        self.container.setStyleSheet("background-color: rgba(240, 240, 240, 200); border-radius: 100px; margin:5px; border: 3px solid rgb(0, 0, 0);")
        self.container.setFixedSize(window_size)
        
        self.start_box_widget = StartWidget()
        
        self.vbox.addWidget(self.start_box_widget)
        
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)
        
        self.avoid_background_widgets = [self.start_box_widget.open_btn, self.start_box_widget.cycle_calc_btn,\
                                         self.start_box_widget.dis_valve_calc_btn, self.start_box_widget.suc_valve_calc_btn,\
                                         self.start_box_widget.exit_btn, self.start_box_widget.info_btn, self.start_box_widget.collapse_btn]
        
        self.show()

    def check_mouse_pos_background(self, pos):
        if all([True if not check_widget.is_hover else False for check_widget in self.avoid_background_widgets]):
            return True
        else:
            return False

    def mousePressEvent(self, event):
        if self.check_mouse_pos_background(event.globalPos()):
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.check_mouse_pos_background(event.globalPos()):
            delta = QtCore.QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def closeEvent(self, event):
        self.app.quit()

    def collapse_widget(self):
        self.showMinimized()










