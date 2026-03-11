#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GLM-OCR 模型下載腳本
從 Hugging Face 下載 GLM-OCR 0.9B 模型到 models/ 資料夾
"""

import os
from huggingface_hub import snapshot_download

# 模型 ID
REPO_ID = "THUMLab/GLM-OCR-0.9B"

# 目標資料夾
TARGET_DIR = os.path.join(os.path.dirname(__file__), "models", "glm-ocr-0.9b")

print(f"正在下載 GLM-OCR 0.9B 模型...")
print(f"模型 ID: {REPO_ID}")
print(f"目標位置: {TARGET_DIR}")

# 下載模型
snapshot_download(
    repo_id=REPO_ID,
    local_dir=TARGET_DIR,
    local_dir_use_symlinks=False  # 不使用符號連結，直接複製檔案
)

print(f"\n模型下載完成！")
print(f"模型位置: {TARGET_DIR}")
