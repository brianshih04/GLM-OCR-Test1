import os
import fitz  # PyMuPDF
from PIL import Image
from typing import Dict, Any


class PDFBuilder:
    """PDF 產生器 - 負責產生雙層 PDF"""

    @staticmethod
    def create_searchable_pdf(image_path: str, text_result: Dict[str, Any], output_path: str = None) -> str:
        """
        建立雙層可搜尋 PDF

        Args:
            image_path: 輸入圖片路徑
            text_result: OCR 結果字典，包含 text, boxes, scores
            output_path: 輸出 PDF 路徑，若為 None 則自動產生

        Returns:
            輸出 PDF 路徑
        """
        # 取得圖片
        image = Image.open(image_path)

        # 設定輸出路徑
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_ocr.pdf"

        # 建立 PDF 文件
        doc = fitz.open()

        # 計算頁面大小 (以圖片為基準)
        img_width, img_height = image.size
        page_rect = fitz.Rect(0, 0, img_width, img_height)

        # 新增頁面
        page = doc.new_page(pno=-1, rect=page_rect)

        # 將圖片寫入 PDF (作為底層)
        image_bytes = PDFBuilder._image_to_bytes(image)
        page.insert_image(page_rect, stream=image_bytes)

        # 取得辨識文字
        ocr_text = text_result.get("text", "")

        # 如果有文字，新增文字層 (可搜尋層)
        if ocr_text.strip():
            # 使用透明文字覆蓋整個頁面
            # 這樣文字就可以被搜尋，但不會影響視覺效果
            page.insert_text(
                point=(0, 0),
                fontsize=1,  # 很小的字體
                text=ocr_text,
                color=(1, 1, 1),  # 白色文字 (與背景相同)
                fill_opacity=0,  # 完全透明
                stroke_opacity=0
            )

        # 儲存 PDF
        doc.save(output_path)
        doc.close()

        return output_path

    @staticmethod
    def _image_to_bytes(image) -> bytes:
        """
        將 PIL Image 轉換為位元組

        Args:
            image: PIL Image 物件

        Returns:
            圖片位元組
        """
        from io import BytesIO
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    @staticmethod
    def create_pdf_from_text(text: str, output_path: str) -> str:
        """
        從文字建立簡單 PDF (僅文字層)

        Args:
            text: 輸入文字
            output_path: 輸出 PDF 路徑

        Returns:
            輸出 PDF 路徑
        """
        doc = fitz.open()

        # 新增頁面
        page = doc.new_page(pno=-1, rect=fitz.Rect(0, 0, 595, 842))  # A4 尺寸

        # 插入文字
        page.insert_text(
            point=(72, 72),  # 頁邊距
            fontsize=12,
            text=text,
            fontname="helv",  # Helvetica 字型
            color=(0, 0, 0)
        )

        # 儲存 PDF
        doc.save(output_path)
        doc.close()

        return output_path
