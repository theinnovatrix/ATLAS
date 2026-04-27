"""
Module: atlas.gui.main_window
Purpose: Optional PyQt6 main window for Atlas.
Author: NOVA Development Agent
Version: 0.7.0
Dependencies: optional PyQt6, atlas.gui.controller
Last Updated: 2026-04-27
"""

from __future__ import annotations

from atlas.gui.controller import AtlasGuiController


def import_pyqt6() -> dict[str, object]:
    """Import PyQt6 lazily so non-GUI environments can still run tests."""
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as error:
        raise RuntimeError("Install GUI extras with: python -m pip install -e '.[gui]'") from error
    return {
        "QApplication": QApplication,
        "QHBoxLayout": QHBoxLayout,
        "QLabel": QLabel,
        "QLineEdit": QLineEdit,
        "QMainWindow": QMainWindow,
        "QPushButton": QPushButton,
        "QTextEdit": QTextEdit,
        "QVBoxLayout": QVBoxLayout,
        "QWidget": QWidget,
        "Qt": Qt,
    }


def pyqt_available() -> bool:
    """Return whether PyQt6 can be imported in this environment."""
    try:
        import_pyqt6()
    except RuntimeError:
        return False
    return True


def build_main_window(controller: AtlasGuiController | None = None):
    """Create the Atlas main window class instance."""
    qt = import_pyqt6()
    controller = controller or AtlasGuiController()
    q_main_window = qt["QMainWindow"]
    q_widget = qt["QWidget"]
    q_vbox_layout = qt["QVBoxLayout"]
    q_hbox_layout = qt["QHBoxLayout"]
    q_label = qt["QLabel"]
    q_text_edit = qt["QTextEdit"]
    q_line_edit = qt["QLineEdit"]
    q_push_button = qt["QPushButton"]

    class AtlasMainWindow(q_main_window):  # type: ignore[misc, valid-type]
        """Small PyQt6 window for text-command Atlas interaction."""

        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Atlas Assistant")
            self.resize(900, 650)
            self.controller = controller

            central = q_widget()
            layout = q_vbox_layout()

            self.status_label = q_label("Atlas ready")
            layout.addWidget(self.status_label)

            self.chat_display = q_text_edit()
            self.chat_display.setReadOnly(True)
            self.chat_display.setPlaceholderText("Atlas conversation appears here.")
            layout.addWidget(self.chat_display)

            input_row = q_hbox_layout()
            self.command_input = q_line_edit()
            self.command_input.setPlaceholderText('Try: system info, voice status, "define atlas"')
            self.command_input.returnPressed.connect(self.run_command)
            input_row.addWidget(self.command_input)

            self.send_button = q_push_button("Send")
            self.send_button.clicked.connect(self.run_command)
            input_row.addWidget(self.send_button)
            layout.addLayout(input_row)

            quick_row = q_hbox_layout()
            quick_commands = (
                ("System", "system info"),
                ("Voice", "voice status"),
                ("Web", "search linux voice assistant"),
                ("Pomodoro", "pomodoro 15"),
            )
            for label, command in quick_commands:
                button = q_push_button(label)
                button.clicked.connect(lambda _checked=False, value=command: self.run_quick(value))
                quick_row.addWidget(button)
            layout.addLayout(quick_row)

            central.setLayout(layout)
            self.setCentralWidget(central)
            self.render_history()

        def run_quick(self, command: str) -> None:
            """Run a quick command from a button."""
            self.command_input.setText(command)
            self.run_command()

        def run_command(self) -> None:
            """Run the command currently typed in the input box."""
            command = self.command_input.text().strip()
            if not command:
                return
            self.controller.run_command(command)
            self.status_label.setText(self.controller.state.status)
            self.command_input.clear()
            self.render_history()

        def render_history(self) -> None:
            """Render controller transcript into the chat display."""
            self.chat_display.setPlainText(self.controller.transcript_text())

    return AtlasMainWindow()


def run_gui() -> int:
    """Run the Atlas PyQt6 GUI."""
    qt = import_pyqt6()
    q_application = qt["QApplication"]
    app = q_application([])
    window = build_main_window()
    window.show()
    return int(app.exec())
