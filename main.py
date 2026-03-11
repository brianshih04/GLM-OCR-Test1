import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, QTabWidget,
    QGroupBox, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from folder_watcher import FolderWatcher
from ocr_engine import OCREngine
from pdf_builder import PDFBuilder


class OCRWorker(QThread):
    """OCR 工作執行緒 - 避免主視窗卡死"""
    progress_changed = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(str)  # signal with PDF path
    error = pyqtSignal(str)

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path

    def run(self):
        try:
            self.log_message.emit(f"開始處理圖片: {self.image_path}")
            self.progress_changed.emit(10)

            # 載入模型
            self.log_message.emit("載入 GLM-OCR 模型...")
            self.progress_changed.emit(20)

            ocr_engine = OCREngine()
            self.progress_changed.emit(40)

            # 執行 OCR
            self.log_message.emit("執行文字辨識...")
            text_result = ocr_engine.ocr(self.image_path)
            self.progress_changed.emit(70)

            # 建立 PDF
            self.log_message.emit("產生雙層 PDF...")
            pdf_path = PDFBuilder.create_searchable_pdf(
                image_path=self.image_path,
                text_result=text_result
            )
            self.progress_changed.emit(100)
            self.finished.emit(pdf_path)

        except Exception as e:
            self.error.emit(str(e))


class FolderWatcherWorker(QThread):
    """資料夾監聽工作執行緒"""
    log_message = pyqtSignal(str)

    def __init__(self, input_dir: str, output_dir: str, parent=None):
        super().__init__(parent)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.watcher = None
        self.running = False

    def run(self):
        self.watcher = FolderWatcher(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            callback=self.handle_new_file
        )
        self.running = True
        self.log_message.emit(f"開始監聽資料夾: {self.input_dir}")
        self.watcher.start()

    def stop(self):
        self.running = False
        if self.watcher:
            self.watcher.stop()

    def handle_new_file(self, file_path: str):
        """處理新檔案的回呼函數"""
        self.log_message.emit(f"偵測到新檔案: {file_path}")
        # 可以在這裡觸發 OCR 處理
        # 為了簡單起見，這裡只記錄日誌


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 離線雙層 PDF 轉換服務 (GLM-OCR 0.9B)")
        self.setGeometry(100, 100, 900, 700)

        # 中文字型設定
        font = QFont()
        font.setFamily("Microsoft JhengHei")
        self.setFont(font)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 標題
        title_label = QLabel("AI 離線雙層 PDF 轉換服務")
        title_label.setFont(QFont("Microsoft JhengHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 製作者標籤
        author_label = QLabel("Powered by GLM-OCR 0.9B")
        author_label.setFont(QFont("Microsoft JhengHei", 10))
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(author_label)

        # 分隔線
        main_layout.addSpacing(10)

        # Tab Widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Tab 1: 單檔轉換
        single_tab = self.create_single_conversion_tab()
        tab_widget.addTab(single_tab, "單檔轉換")

        # Tab 2: Hot Folder
        hotfolder_tab = self.create_hotfolder_tab()
        tab_widget.addTab(hotfolder_tab, "Hot Folder")

        # 日誌區域
        log_group = QGroupBox("處理日誌")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

    def create_single_conversion_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # 輸入檔案選擇
        input_layout = QHBoxLayout()
        input_label = QLabel("輸入圖片:")
        input_label.setMinimumWidth(80)
        self.input_line = QLineEdit()
        self.browse_btn = QPushButton("瀏覽...")
        self.browse_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.browse_btn)
        layout.addLayout(input_layout)

        # 轉換按鈕
        self.convert_btn = QPushButton("開始轉換")
        self.convert_btn.setFont(QFont("Microsoft JhengHei", 12, QFont.Weight.Bold))
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.convert_btn.clicked.connect(self.start_single_conversion)
        layout.addWidget(self.convert_btn)

        layout.addStretch()

        return tab

    def create_hotfolder_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # 輸入資料夾
        input_layout = QHBoxLayout()
        input_label = QLabel("輸入資料夾:")
        input_label.setMinimumWidth(80)
        self.input_folder_line = QLineEdit()
        self.browse_input_folder_btn = QPushButton("瀏覽...")
        self.browse_input_folder_btn.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_folder_line)
        input_layout.addWidget(self.browse_input_folder_btn)
        layout.addLayout(input_layout)

        # 輸出資料夾
        output_layout = QHBoxLayout()
        output_label = QLabel("輸出資料夾:")
        output_label.setMinimumWidth(80)
        self.output_folder_line = QLineEdit()
        self.browse_output_folder_btn = QPushButton("瀏覽...")
        self.browse_output_folder_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_folder_line)
        output_layout.addWidget(self.browse_output_folder_btn)
        layout.addLayout(output_layout)

        # Hot Folder 控制按鈕
        button_layout = QHBoxLayout()
        self.start_watcher_btn = QPushButton("啟動監聽")
        self.stop_watcher_btn = QPushButton("停止監聽")
        self.start_watcher_btn.clicked.connect(self.start_watcher)
        self.stop_watcher_btn.clicked.connect(self.stop_watcher)
        self.stop_watcher_btn.setEnabled(False)
        button_layout.addWidget(self.start_watcher_btn)
        button_layout.addWidget(self.stop_watcher_btn)
        layout.addLayout(button_layout)

        layout.addStretch()

        return tab

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇圖片", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_path:
            self.input_line.setText(file_path)

    def browse_input_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "選擇輸入資料夾")
        if folder_path:
            self.input_folder_line.setText(folder_path)

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder_path:
            self.output_folder_line.setText(folder_path)

    def start_single_conversion(self):
        image_path = self.input_line.text()
        if not image_path or not os.path.exists(image_path):
            self.log_message("請選擇有效的圖片檔案")
            return

        # 禁用按鈕
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 啟動工作執行緒
        self.worker = OCRWorker(image_path)
        self.worker.progress_changed.connect(self.update_progress)
        self.worker.log_message.connect(self.log_message)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def start_watcher(self):
        input_dir = self.input_folder_line.text()
        output_dir = self.output_folder_line.text()

        if not input_dir or not os.path.exists(input_dir):
            self.log_message("請選擇有效的輸入資料夾")
            return

        if not output_dir:
            self.log_message("請選擇輸出資料夾")
            return

        # 建立輸出資料夾
        os.makedirs(output_dir, exist_ok=True)

        # 啟動監聽執行緒
        self.watcher_worker = FolderWatcherWorker(input_dir, output_dir)
        self.watcher_worker.log_message.connect(self.log_message)
        self.watcher_worker.start()

        # 更新按鈕狀態
        self.start_watcher_btn.setEnabled(False)
        self.stop_watcher_btn.setEnabled(True)
        self.input_folder_line.setEnabled(False)
        self.output_folder_line.setEnabled(False)

    def stop_watcher(self):
        if hasattr(self, 'watcher_worker') and self.watcher_worker:
            self.watcher_worker.stop()
            self.watcher_worker.wait()

        # 更新按鈕狀態
        self.start_watcher_btn.setEnabled(True)
        self.stop_watcher_btn.setEnabled(False)
        self.input_folder_line.setEnabled(True)
        self.output_folder_line.setEnabled(True)

        self.log_message("資料夾監聽已停止")

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def conversion_finished(self, pdf_path: str):
        self.log_message(f"轉換完成！PDF 已儲存至: {pdf_path}")
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def conversion_error(self, error_msg: str):
        self.log_message(f"錯誤: {error_msg}")
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def log_message(self, message: str):
        """新增日誌訊息"""
        self.log_text.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
