from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout()

        self.button = QPushButton("Click me")
        self.button.clicked.connect(self.on_click)

        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_click(self):
        print("Button clicked!")