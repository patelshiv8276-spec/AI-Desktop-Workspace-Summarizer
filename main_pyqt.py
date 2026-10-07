import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

load_dotenv()


# --- Background Worker Thread for Non-Blocking Streaming ---
class GeminiWorker(QThread):
    chunk_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished_stream = pyqtSignal(float)

    def __init__(self, client, prompt, parent=None):
        super().__init__(parent)
        self.client = client
        self.prompt = prompt

    def run(self):
        start_time = time.time()
        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
        ]
        stream_successful = False

        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content_stream(
                    model=model_name, contents=self.prompt
                )
                for chunk in response:
                    if chunk.text:
                        self.chunk_received.emit(chunk.text)
                stream_successful = True
                break
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "404" in error_msg:
                    continue
                else:
                    self.error_occurred.emit(f"❌ API Error: {error_msg}")
                    stream_successful = True
                    break

        if not stream_successful:
            self.error_occurred.emit(
                "❌ API Error: Gemini services busy across all regions."
            )

        elapsed = time.time() - start_time
        self.finished_stream.emit(elapsed)


# --- Main PyQt6 UI Window ---
class PyQtAIAssistant(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GEMINI CORE // PyQt6 Hardware Assistant")
        self.resize(960, 720)

        # Initialize API
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

        self.init_ui()
        self.apply_qss_styling()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # --- Header Card ---
        self.header_card = QFrame()
        self.header_card.setObjectName("headerCard")
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(20, 16, 20, 16)

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDotReady")
        header_layout.addWidget(self.status_dot)

        self.title_label = QLabel("GEMINI CORE")
        self.title_label.setObjectName("headerTitle")
        header_layout.addWidget(self.title_label)

        self.sub_title = QLabel(" |  PyQt6 Hardware-Accelerated HUD")
        self.sub_title.setObjectName("headerSubtitle")
        header_layout.addWidget(self.sub_title)

        header_layout.addStretch()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            ["Summarize Text", "Key Takeaways", "Code/Writing Assistant"]
        )
        self.mode_combo.setObjectName("modeCombo")
        header_layout.addWidget(self.mode_combo)

        main_layout.addWidget(self.header_card)

        # --- Input Card ---
        self.input_card = QFrame()
        self.input_card.setObjectName("panelCard")
        input_layout = QVBoxLayout(self.input_card)
        input_layout.setContentsMargins(20, 16, 20, 16)

        input_header_layout = QHBoxLayout()
        input_meta = QLabel("PROMPT INPUT")
        input_meta.setObjectName("metaLabel")
        input_header_layout.addWidget(input_meta)
        input_layout.addLayout(input_header_layout)

        self.input_text = QTextEdit()
        self.input_text.setObjectName("customTextEdit")
        self.input_text.setPlaceholderText("Enter your text or prompt here...")
        self.input_text.setFixedHeight(120)
        input_layout.addWidget(self.input_text)

        input_btn_layout = QHBoxLayout()
        input_btn_layout.addStretch()

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.clicked.connect(self.clear_input)
        input_btn_layout.addWidget(self.clear_btn)

        self.process_btn = QPushButton("⚡ GENERATE")
        self.process_btn.setObjectName("accentBtn")
        self.process_btn.clicked.connect(self.start_ai_task)
        input_btn_layout.addWidget(self.process_btn)

        input_layout.addLayout(input_btn_layout)
        main_layout.addWidget(self.input_card)

        # --- Output Card ---
        self.output_card = QFrame()
        self.output_card.setObjectName("panelCard")
        output_layout = QVBoxLayout(self.output_card)
        output_layout.setContentsMargins(20, 16, 20, 16)

        output_meta_layout = QHBoxLayout()
        output_meta = QLabel("LIVE STREAM OUTPUT")
        output_meta.setObjectName("metaLabel")
        output_meta_layout.addWidget(output_meta)

        output_meta_layout.addStretch()

        self.stats_label = QLabel("System Idle")
        self.stats_label.setObjectName("statsLabel")
        output_meta_layout.addWidget(self.stats_label)
        output_layout.addLayout(output_meta_layout)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("customTextEdit")
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.copy_btn = QPushButton("Copy Output")
        self.copy_btn.setObjectName("secondaryBtn")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        action_layout.addWidget(self.copy_btn)

        output_layout.addLayout(action_layout)
        main_layout.addWidget(self.output_card)

        # Add Neon Glow Shadow Effect to Header Card
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 240, 255, 60))
        glow.setOffset(0, 0)
        self.header_card.setGraphicsEffect(glow)

    def apply_qss_styling(self):
        """Applies hardware-accelerated CSS/QSS Stylesheet to the entire UI."""
        qss = """
        QMainWindow {
            background-color: #0b0d14;
        }
        QFrame#headerCard {
            background-color: #131722;
            border: 1px solid #00f0ff;
            border-radius: 12px;
        }
        QFrame#panelCard {
            background-color: #131722;
            border: 1px solid #2a3147;
            border-radius: 12px;
        }
        QLabel#headerTitle {
            color: #00f0ff;
            font-size: 16px;
            font-weight: bold;
            font-family: "Consolas", monospace;
        }
        QLabel#headerSubtitle {
            color: #6c7897;
            font-size: 13px;
        }
        QLabel#statusDotReady {
            color: #00ff88;
            font-size: 14px;
        }
        QLabel#statusDotStreaming {
            color: #00f0ff;
            font-size: 14px;
        }
        QLabel#metaLabel {
            color: #6c7897;
            font-size: 11px;
            font-weight: bold;
            font-family: "Consolas", monospace;
        }
        QLabel#statsLabel {
            color: #6c7897;
            font-size: 11px;
            font-family: "Consolas", monospace;
        }
        QTextEdit#customTextEdit {
            background-color: #0b0d14;
            color: #ffffff;
            border: 1px solid #2a3147;
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
            selection-background-color: #00f0ff;
            selection-color: #000000;
        }
        QTextEdit#customTextEdit:focus {
            border: 1px solid #00f0ff;
        }
        QComboBox#modeCombo {
            background-color: #1a1f2c;
            color: #ffffff;
            border: 1px solid #2a3147;
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 180px;
        }
        QComboBox#modeCombo::drop-down {
            border: none;
        }
        QComboBox#modeCombo QAbstractItemView {
            background-color: #131722;
            color: #ffffff;
            selection-background-color: #2a3147;
        }
        QPushButton#secondaryBtn {
            background-color: transparent;
            color: #ffffff;
            border: 1px solid #2a3147;
            border-radius: 6px;
            padding: 6px 16px;
            font-size: 12px;
        }
        QPushButton#secondaryBtn:hover {
            background-color: #1a1f2c;
            border: 1px solid #6c7897;
        }
        QPushButton#accentBtn {
            background-color: #00f0ff;
            color: #05070a;
            border: none;
            border-radius: 6px;
            padding: 6px 18px;
            font-size: 12px;
            font-weight: bold;
            font-family: "Consolas", monospace;
        }
        QPushButton#accentBtn:hover {
            background-color: #00b8cc;
        }
        QPushButton#accentBtn:disabled {
            background-color: #1a1f2c;
            color: #6c7897;
        }
        """
        self.setStyleSheet(qss)

    def clear_input(self):
        self.input_text.clear()

    def copy_to_clipboard(self):
        content = self.output_text.toPlainText()
        if content:
            QApplication.clipboard().setText(content)
            self.stats_label.setText("Copied to clipboard! ✓")

    def start_ai_task(self):
        user_input = self.input_text.toPlainText().strip()
        selected_mode = self.mode_combo.currentText()

        if not user_input:
            self.output_text.setText(
                "⚠️ Please enter some text or a prompt to analyze."
            )
            return

        if not self.client:
            self.output_text.setText(
                "❌ Error: Missing GEMINI_API_KEY in your .env file."
            )
            return

        if selected_mode == "Summarize Text":
            prompt = f"Provide a clean, well-structured summary of the following text:\n\n{user_input}"
        elif selected_mode == "Key Takeaways":
            prompt = f"Extract the key bullet points and core takeaways from this text:\n\n{user_input}"
        else:
            prompt = user_input

        self.output_text.clear()
        self.process_btn.setEnabled(False)
        self.process_btn.setText("⚡ STREAMING...")
        self.status_dot.setObjectName("statusDotStreaming")
        self.status_dot.setStyle(self.status_dot.style())
        self.stats_label.setText("Streaming tokens...")

        # Spawn Worker Thread
        self.worker = GeminiWorker(self.client, prompt)
        self.worker.chunk_received.connect(self.append_chunk)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished_stream.connect(self.finish_task)
        self.worker.start()

    def append_chunk(self, chunk):
        self.output_text.insertPlainText(chunk)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )

    def handle_error(self, error_msg):
        self.output_text.setText(error_msg)

    def finish_task(self, elapsed):
        self.process_btn.setEnabled(True)
        self.process_btn.setText("⚡ GENERATE")
        self.status_dot.setObjectName("statusDotReady")
        self.status_dot.setStyle(self.status_dot.style())
        self.stats_label.setText(f"Completed in {round(elapsed, 2)}s")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyQtAIAssistant()
    window.show()
    sys.exit(app.exec())