import sys
from PySide6.QtWidgets import QApplication, QWidget
from ui.main_window import MainWindow
from backend.database import create_tables

def main():
    create_tables()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()