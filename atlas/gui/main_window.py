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
            QFrame,
            QGridLayout,
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
        "QFrame": QFrame,
        "QGridLayout": QGridLayout,
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
    q_frame = qt["QFrame"]
    q_widget = qt["QWidget"]
    q_vbox_layout = qt["QVBoxLayout"]
    q_hbox_layout = qt["QHBoxLayout"]
    q_grid_layout = qt["QGridLayout"]
    q_label = qt["QLabel"]
    q_text_edit = qt["QTextEdit"]
    q_line_edit = qt["QLineEdit"]
    q_push_button = qt["QPushButton"]

    class AtlasMainWindow(q_main_window):  # type: ignore[misc, valid-type]
        """Small PyQt6 window for text-command Atlas interaction."""

        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Atlas // Desktop Cognitive Engine")
            self.resize(1180, 760)
            self.controller = controller
            self.setStyleSheet(ATLAS_STYLESHEET)

            central = q_widget()
            central.setObjectName("Root")
            shell = q_hbox_layout()
            shell.setContentsMargins(18, 18, 18, 18)
            shell.setSpacing(18)

            rail = q_frame()
            rail.setObjectName("CommandRail")
            rail_layout = q_vbox_layout()
            rail_layout.setContentsMargins(16, 18, 16, 18)
            rail_layout.setSpacing(12)

            brand = q_label("ATLAS")
            brand.setObjectName("Brand")
            rail_layout.addWidget(brand)

            subtitle = q_label("Desktop Cognitive Engine")
            subtitle.setObjectName("Subtitle")
            rail_layout.addWidget(subtitle)

            quick_commands = (
                ("SYSTEM SCAN", "system diagnostics"),
                ("VOICE CORE", "voice status"),
                ("WEB INTEL", "search linux voice assistant"),
                ("FOCUS MODE", "pomodoro 15"),
                ("DEFINE ATLAS", "define atlas"),
                ("GIT STATUS", "git status"),
            )
            for label, command in quick_commands:
                button = q_push_button(label)
                button.setObjectName("RailButton")
                button.clicked.connect(lambda _checked=False, value=command: self.run_quick(value))
                rail_layout.addWidget(button)
            rail_layout.addStretch()

            safety = q_label("SAFE MODE: ACTIVE\nLocal-first / confirmation-gated")
            safety.setObjectName("SafetyBadge")
            rail_layout.addWidget(safety)
            rail.setLayout(rail_layout)
            shell.addWidget(rail, 1)

            main_panel = q_frame()
            main_panel.setObjectName("MainPanel")
            layout = q_vbox_layout()
            layout.setContentsMargins(22, 20, 22, 20)
            layout.setSpacing(16)

            header_row = q_hbox_layout()
            title_block = q_vbox_layout()
            title = q_label("Atlas Command Deck")
            title.setObjectName("Title")
            title_block.addWidget(title)
            tagline = q_label("Ask, route, automate, and verify from one local cockpit.")
            tagline.setObjectName("Tagline")
            title_block.addWidget(tagline)
            header_row.addLayout(title_block)

            self.status_label = q_label("READY")
            self.status_label.setObjectName("StatusPill")
            header_row.addWidget(self.status_label)
            layout.addLayout(header_row)

            metrics = q_grid_layout()
            metrics.setSpacing(12)
            for index, (label, value) in enumerate(
                (
                    ("MODE", "LOCAL-FIRST"),
                    ("VOICE", "OPTIONAL"),
                    ("SYSTEM", "CONFIRM-GATED"),
                    ("WEB", "SAFE ADAPTERS"),
                )
            ):
                card = q_frame()
                card.setObjectName("MetricCard")
                card_layout = q_vbox_layout()
                card_layout.setContentsMargins(14, 10, 14, 10)
                card_label = q_label(label)
                card_label.setObjectName("MetricLabel")
                card_value = q_label(value)
                card_value.setObjectName("MetricValue")
                card_layout.addWidget(card_label)
                card_layout.addWidget(card_value)
                card.setLayout(card_layout)
                metrics.addWidget(card, 0, index)
            layout.addLayout(metrics)

            self.chat_display = q_text_edit()
            self.chat_display.setObjectName("Transcript")
            self.chat_display.setReadOnly(True)
            self.chat_display.setPlaceholderText("Atlas conversation appears here.")
            layout.addWidget(self.chat_display, 1)

            input_panel = q_frame()
            input_panel.setObjectName("InputPanel")
            input_row = q_hbox_layout()
            input_row.setContentsMargins(12, 10, 12, 10)
            self.command_input = q_line_edit()
            self.command_input.setObjectName("CommandInput")
            self.command_input.setPlaceholderText('Try: system info, voice status, "define atlas"')
            self.command_input.returnPressed.connect(self.run_command)
            input_row.addWidget(self.command_input)

            self.send_button = q_push_button("EXECUTE")
            self.send_button.setObjectName("ExecuteButton")
            self.send_button.clicked.connect(self.run_command)
            input_row.addWidget(self.send_button)
            input_panel.setLayout(input_row)
            layout.addWidget(input_panel)

            main_panel.setLayout(layout)
            shell.addWidget(main_panel, 4)
            central.setLayout(shell)
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
            self.chat_display.setHtml(_transcript_html(self.controller.history))

    return AtlasMainWindow()


def _transcript_html(history: list[object]) -> str:
    """Return styled transcript HTML for QTextEdit."""
    rows = []
    for message in history:
        sender = getattr(message, "sender", "Atlas")
        text = _escape_html(getattr(message, "text", ""))
        css_class = "user" if sender == "You" else "atlas"
        rows.append(
            f'<div class="msg {css_class}"><b>{_escape_html(sender)}</b><br>{text}</div>'
        )
    return "<style>" + TRANSCRIPT_STYLE + "</style>" + "".join(rows)


def _escape_html(value: str) -> str:
    """Escape minimal HTML entities for transcript rendering."""
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def run_gui() -> int:
    """Run the Atlas PyQt6 GUI."""
    qt = import_pyqt6()
    q_application = qt["QApplication"]
    app = q_application([])
    window = build_main_window()
    window.show()
    return int(app.exec())


TRANSCRIPT_STYLE = """
body { background: #07111f; color: #d8f6ff; font-family: Inter, Arial, sans-serif; }
.msg { margin: 10px 4px; padding: 12px 14px; border-radius: 14px; }
.atlas { background: rgba(0, 229, 255, 0.10); border: 1px solid rgba(0, 229, 255, 0.35); }
.user { background: rgba(125, 92, 255, 0.14); border: 1px solid rgba(125, 92, 255, 0.38); }
b { color: #63f7ff; letter-spacing: 1px; }
"""


ATLAS_STYLESHEET = """
QWidget#Root {
    background: #050812;
}
QFrame#CommandRail {
    background: #081527;
    border: 1px solid rgba(0, 229, 255, 0.28);
    border-radius: 22px;
}
QFrame#MainPanel {
    background: #07111f;
    border: 1px solid rgba(99, 247, 255, 0.30);
    border-radius: 24px;
}
QLabel#Brand {
    color: #63f7ff;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 5px;
}
QLabel#Subtitle, QLabel#Tagline {
    color: #8aa4b8;
    font-size: 13px;
}
QLabel#Title {
    color: #edfaff;
    font-size: 30px;
    font-weight: 800;
}
QLabel#StatusPill {
    color: #041018;
    background: #63f7ff;
    border-radius: 17px;
    padding: 9px 18px;
    font-weight: 800;
}
QFrame#MetricCard, QFrame#InputPanel {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
}
QLabel#MetricLabel {
    color: #7f96aa;
    font-size: 11px;
    font-weight: 700;
}
QLabel#MetricValue {
    color: #dffbff;
    font-size: 15px;
    font-weight: 800;
}
QTextEdit#Transcript {
    background: #050b16;
    border: 1px solid rgba(99, 247, 255, 0.20);
    border-radius: 18px;
    color: #d8f6ff;
    padding: 12px;
    font-size: 14px;
}
QLineEdit#CommandInput {
    background: #030813;
    border: 1px solid rgba(99, 247, 255, 0.24);
    border-radius: 15px;
    color: #ffffff;
    padding: 13px 15px;
    font-size: 15px;
}
QLineEdit#CommandInput:focus {
    border: 1px solid #63f7ff;
}
QPushButton#ExecuteButton, QPushButton#RailButton {
    background: #102b45;
    color: #e9fbff;
    border: 1px solid rgba(99, 247, 255, 0.35);
    border-radius: 14px;
    padding: 12px 16px;
    font-weight: 800;
}
QPushButton#ExecuteButton:hover, QPushButton#RailButton:hover {
    background: #164264;
    border: 1px solid #63f7ff;
}
QPushButton#ExecuteButton {
    background: #00bcd4;
    color: #031018;
}
QLabel#SafetyBadge {
    color: #9fffe0;
    background: rgba(29, 255, 176, 0.08);
    border: 1px solid rgba(29, 255, 176, 0.24);
    border-radius: 14px;
    padding: 12px;
    font-size: 12px;
}
"""
