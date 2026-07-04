import sys

from PySide6.QtWidgets import QApplication

from desktop.main_window import MainWindow
from desktop.qt_theme import desktop_theme


def main():
    """Launch the AirControl desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("AirControl")
    app.setOrganizationName("AirControl")
    app.setStyleSheet(desktop_theme.global_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()