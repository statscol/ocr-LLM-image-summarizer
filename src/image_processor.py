import cv2
import pytesseract
from config import PYTESSERACT_DEFAULT_CONFIG
from pathlib import Path
from tqdm import tqdm
import numpy as np

class ImageProcessor:

    def binarize(self,img_path:str):
        """
        This function is to binarize an input image
        :param img: image in format of (h, w, channel)
        :return: am image in format of (h, w)
        """
        img=cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] #threshold may affect performance for invoices|receipts as seen in our test dataset
        return gray
    
    def remove_watermark(self,img,alpha = 1.8,beta = -180):
        """remove watermark from image 
        img: cv2 image| np.array"""
        new = alpha * img + beta
        new = np.clip(new, 0, 255).astype(np.uint8)
        return new
        
    def deskew(self,image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def dilate_erode(self,img):
        """
        apply an erosion and dilation kernel
        img: cv2 image| np.array
        """
        kernel = np.ones((2, 1), np.uint8)
        kernel2 = np.ones((1, 1), np.uint8)
        img = cv2.blur(img,(6,5))
        img=cv2.dilate(img, kernel, iterations=3)
        img = cv2.erode(img, (2,1), iterations=1)
        img = cv2.blur(img,(1,1))
        img = cv2.bilateralFilter(img,10,35,30)
        img= cv2.dilate(img, kernel2, iterations=1)
        return img

    def opening(self,image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    def process_image(self,img_path:str):
        img=self.binarize(img_path)
        img=self.remove_watermark(img)
        return img

    def img_to_text(self,img,lang="spa"):
        text=pytesseract.image_to_string(img,lang=lang,config=PYTESSERACT_DEFAULT_CONFIG)   
        return text
    
if __name__=="__main__":
    processor=ImageProcessor()
    image_paths=list(Path("images/raw").glob("*.jpg"))
    for img_pth in tqdm(image_paths,desc="Img Preproc+ OCR "):
        img_processed=processor.process_image(str(img_pth))
        text=processor.img_to_text(img_processed)
        cv2.imwrite(f"images/processed/{img_pth.name}",img_processed)
        with open(f"images/text/{img_pth.name.replace('.jpg','.txt')}",'w') as f:
            f.write(text)