from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from backend.database import add_user, get_user

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout()
        header = self.create_header()
        main_layout.addWidget(header)

        menu = self.create_menu()
        main_layout.addWidget(menu)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout()

        logo = QLabel("MyApp")

        layout.addWidget(logo)
        layout.addStretch()

        header.setLayout(layout)
        return header

    def create_menu(self):
        menu = QWidget()
        layout = QHBoxLayout()

        btn_mainPage = QPushButton("Main Page")
        btn_mainPage.clicked.connect(lambda: print("Clicked!"))
        layout.addWidget(btn_mainPage)

        btn_account = QPushButton("Account")
        btn_account.clicked.connect(lambda: print("Clicked!"))
        layout.addWidget(btn_account)

        btn_postList = QPushButton("Posts")
        btn_postList.clicked.connect(lambda: print("Clicked!"))
        layout.addWidget(btn_postList)

        menu.setLayout(layout)
        return menu

