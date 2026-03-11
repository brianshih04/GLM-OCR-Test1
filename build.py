#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyInstaller 打包腳本
用於將 GLM-OCR 專案打包成單一可執行檔
"""

import os
import sys
import PyInstaller.__main__

# 取得專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 設定打包選項
PyInstaller.__main__.run([
    # 主程式入口
    'main.py',
    
    # 名稱
    '--name=GLM-OCR-Converter',
    
    # 關閉控制台視窗 (Windows GUI 應用程式)
    '--windowed',
    '--noconsole',
    
    # 一體成型 (單一檔案)
    '--onefile',
    
    # 最佳化壓縮
    '--compress',
    
    # 資料夾與資源
    f'--add-data={os.path.join(PROJECT_ROOT, "models")};models',
    f'--add-data={os.path.join(PROJECT_ROOT, "fonts")};fonts',
    
    # 隱藏模組 (減少檔案大小)
    '--hidden-import=PyQt6.sip',
    '--hidden-import=transformers',
    '--hidden-import=torch',
    '--hidden-import=watchdog',
    '--hidden-import=fitz',
    
    # 作業系統特定選項
    '--clean',  # 清理暫存檔案
    
    # 輸出目錄
    '--distpath', os.path.join(PROJECT_ROOT, 'dist'),
    '--workpath', os.path.join(PROJECT_ROOT, 'build'),
    '--specpath', PROJECT_ROOT,
    
    # 顯示詳細資訊
    '--verbose',
])

print("\n" + "="*50)
print("打包完成！可執行檔位於: dist/GLM-OCR-Converter.exe")
print("="*50)
