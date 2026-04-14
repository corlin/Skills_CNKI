import ddddocr
import io
from PIL import Image

class OCRHelper:
    """
    基于 ddddocr 的验证码识别辅助类
    """
    def __init__(self):
        # show_ad=False 减少控制台输出
        self.ocr = ddddocr.DdddOcr(show_ad=False)

    def classify(self, image_bytes: bytes) -> str:
        """
        识别验证码字节流并返回字符串
        """
        try:
            res = self.ocr.classification(image_bytes)
            return res.strip()
        except Exception as e:
            print(f"OCR 识别异常: {e}")
            return ""

    def classify_image_element(self, screenshot_bytes: bytes) -> str:
        """
        处理从 Playwright 获得的截图字节流
        """
        return self.classify(screenshot_bytes)
