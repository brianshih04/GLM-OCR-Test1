import os
from typing import List, Dict, Any
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer


class OCREngine:
    """OCR 推理引擎 - 負責載入本地模型與執行推理"""

    def __init__(self, model_path: str = None):
        """
        初始化 OCR 引擎

        Args:
            model_path: GLM-OCR 0.9B 模型路徑，預設為 models/glm-ocr-0.9b
        """
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()

    def _get_default_model_path(self) -> str:
        """取得預設模型路徑"""
        default_path = os.path.join(os.path.dirname(__file__), 'models', 'glm-ocr-0.9b')
        return default_path

    def _get_device(self) -> str:
        """取得運算裝置 (CUDA 或 CPU)"""
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_model(self):
        """載入 GLM-OCR 模型"""
        if self.model is not None:
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"模型不存在於: {self.model_path}\n"
                "請將 GLM-OCR 0.9B 模型放置於 models/ 資料夾中"
            )

        print(f"正在載入模型從: {self.model_path}")
        print(f"使用裝置: {self.device}")

        # 載入 tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )

        # 載入模型
        self.model = AutoModel.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)

        print("模型載入完成")

    def ocr(self, image_path: str) -> Dict[str, Any]:
        """
        執行 OCR 推理

        Args:
            image_path: 輸入圖片路徑

        Returns:
            包含辨識結果的字典
        """
        # 載入模型（如果尚未載入）
        self._load_model()

        # 載入圖片
        image = Image.open(image_path).convert('RGB')

        # 執行推理
        with torch.no_grad():
            # GLM-OCR 的推理方式
            result = self.model.chat(
                image=image,
                tokenizer=self.tokenizer,
                device=self.device
            )

        return {
            "text": result.get("text", ""),
            "boxes": result.get("boxes", []),
            "scores": result.get("scores", [])
        }

    def ocr_text_only(self, image_path: str) -> str:
        """
        執行 OCR 並只回傳文字

        Args:
            image_path: 輸入圖片路徑

        Returns:
            辨識出的文字
        """
        result = self.ocr(image_path)
        return result.get("text", "")
