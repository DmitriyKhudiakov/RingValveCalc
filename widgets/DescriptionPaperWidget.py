from PyQt5.QtWidgets import QWidget, QGroupBox, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QFont


class DescriptionPaperWidget(QGroupBox):
    def __init__(self, head: str, html_desc_path):
        super().__init__(head)
        self.html_desc_path = html_desc_path
        self.init_ui()

    def init_ui(self):
        self.setFont(QFont("Times New Roman", 16))
        self.setStyleSheet("background-color: rgb(240, 240, 240)")
        
        self.v_box_layout = QVBoxLayout()
        
        self.te = QTextEdit()
        self.te.setReadOnly(True)
        with open(self.html_desc_path, "r", encoding='utf-8') as file:
            desc_text = file.read()
            self.te.setHtml(desc_text)
        
        self.v_box_layout.addWidget(self.te)
        
        self.setLayout(self.v_box_layout)
