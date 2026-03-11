import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path


class FileCreatedHandler(FileSystemEventHandler):
    """處理檔案建立事件的監聽器"""

    def __init__(self, output_dir: str, callback=None):
        super().__init__()
        self.output_dir = output_dir
        self.callback = callback
        self.processed_files = set()  # 避免重複處理

    def on_created(self, event):
        """當有新檔案建立時觸發"""
        if event.is_directory:
            return

        file_path = event.src_path
        file_ext = Path(file_path).suffix.lower()

        # 只處理圖片檔案
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
        if file_ext not in image_extensions:
            return

        # 避免重複處理
        if file_path in self.processed_files:
            return

        self.processed_files.add(file_path)

        # 等待檔案寫入完成
        time.sleep(0.5)

        # 呼叫回呼函數處理檔案
        if self.callback:
            self.callback(file_path)


class FolderWatcher:
    """資料夾監聽器"""

    def __init__(self, input_dir: str, output_dir: str, callback=None):
        self.input_dir = os.path.abspath(input_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.callback = callback
        self.observer = None
        self.handler = None
        self.running = False

        # 確保輸出資料夾存在
        os.makedirs(self.output_dir, exist_ok=True)

    def start(self):
        """啟動監聽"""
        if self.running:
            return

        self.handler = FileCreatedHandler(self.output_dir, self.callback)
        self.observer = Observer()
        self.observer.schedule(self.handler, self.input_dir, recursive=False)
        self.observer.start()
        self.running = True

    def stop(self):
        """停止監聽"""
        if not self.running:
            return

        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def is_running(self) -> bool:
        """檢查監聽器是否正在運行"""
        return self.running
