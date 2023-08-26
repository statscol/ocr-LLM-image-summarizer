from image_processor import ImageProcessor
import os

test_img="test_img.jpg"


class TesterOcr:
    def test_ocr(self):
        processor=ImageProcessor()
        img_text=processor.run(os.path.join(os.path.dirname(__file__), test_img))
        assert len(img_text)>0,ValueError("Text not found in the image")
