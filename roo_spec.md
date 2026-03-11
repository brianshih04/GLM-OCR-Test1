# 專案名稱：AI 離線雙層 PDF 轉換服務 (GLM-OCR 0.9B)
**Roo Code 開發規格書 (Development Specification for Roo Code)**

## 1. 專案概觀 (Project Overview)
你是一個資深的 Python 桌面應用開發專家與 AI 工程師。
請幫我開發一個「完全離線、本地執行的 Windows 桌面應用程式」。
該程式包含兩大核心功能：
1. **單檔手動轉換**：讓使用者透過圖形化介面 (GUI) 匯入單一圖片，轉換為「雙層可搜尋 PDF (Searchable PDF)」。
2. **自動化資料夾監控 (Hot Folder)**：使用者可指定一個「監聽資料夾 (Input)」與一個「輸出資料夾 (Output)」。程式會在背景監聽，只要有新的影像檔進入，就會自動觸發 AI 推理，並將轉換後的 PDF 存入輸出資料夾。

## 2. Roo Code 執行策略 (Execution Strategy)
請嚴格依照以下兩階段進行開發：
- **階段一 (Architect 模式)**：請先閱讀本規格，建立專案資料夾架構、空白的 Python 檔案，以及 `models/` 和 `fonts/` 等資源資料夾。
- **階段二 (Coder 模式)**：架構建立完成後，請依序實作以下指定的五個檔案，並確保程式碼邏輯符合所有的「防呆機制」與「多執行緒」要求。

## 3. 系統架構與技術棧 (Tech Stack)
- **語言**: Python 3.10+
- **GUI 框架**: `PyQt6` (需實作 QThread 避免主視窗卡死)
- **資料夾監聽**: `watchdog` 
- **AI 推理引擎**: `transformers`, `torch`, `Pillow` (負責載入本地 GLM-OCR 0.9B 模型)
- **PDF 處理引擎**: `PyMuPDF` (`fitz`)
- **打包工具**: `PyInstaller`

## 4. 目錄結構設計 (Directory Structure)
```text
/project_root
  ├── main.py             # GUI 主視窗與進入點
  ├── folder_watcher.py   # watchdog 資料夾監聽與事件捕捉
  ├── ocr_engine.py       # 負責載入本地模型與執行推理
  ├── pdf_builder.py      # 負責產生雙層 PDF
  ├── requirements.txt    # 依賴套件清單
  ├── build.py            # PyInstaller 打包腳本
  ├── /models             # 放置 GLM-OCR 0.9B 權重檔 (外部資源，不打包)
  └── /fonts              # 放置開源中文字型檔 (如 NotoSansTC.ttf，外部資源)