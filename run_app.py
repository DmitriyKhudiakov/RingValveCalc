import sys
from App import MainWidget
from PyQt5.QtWidgets import QApplication


def run():
    app = QApplication(sys.argv)
    mw = MainWidget(app)
    sys.exit(app.exec_())
