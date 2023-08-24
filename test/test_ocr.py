from image_processor import ImageProcessor
import os

test_img="test_img.jpg"


class TesterOcr:
    def test_ocr(self):
        processor=ImageProcessor()
        img=processor.process_image(os.path.join(os.path.dirname(__file__), test_img))
        assert len(processor.img_to_text(img))>0