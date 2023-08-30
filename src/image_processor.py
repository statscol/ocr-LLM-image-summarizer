import cv2
import pytesseract
from config import PYTESSERACT_DEFAULT_CONFIG
from pathlib import Path
from tqdm import tqdm
import numpy as np
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from PIL import Image

class ImageProcessor(BaseTool):

    name = "ImageProcessor"
    description = "useful when you need to extract info from an image in an img_path corresponding to a receipt or invoice and tries to preprocess it returning all the text in the image using an OCR system."

    def binarize(self,img_path):
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
        
    def deskew(self,img):
        coords = np.column_stack(np.where(img > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
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


    def detect_angle(self,img_path):
        """detects angle of rotation in the image using the text lines found"""
        ##taken from https://stackoverflow.com/questions/13872331/rotating-an-image-with-orientation-specified-in-exif-using-python-without-pil-in
        pil_img=Image.open(img_path)
        img_exif = pil_img.getexif()
        if len(img_exif):
            if img_exif[274] == 3:
                pil_img = pil_img.transpose(Image.ROTATE_180)
            elif img_exif[274] == 6:
                pil_img = pil_img.transpose(Image.ROTATE_270)
            elif img_exif[274] == 8:
                pil_img = pil_img.transpose(Image.ROTATE_90)

        return np.array(pil_img)[:, :, ::-1] #convert to BGR
    
    def opening(self,image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    def process_image(self,img_path):
        img=self.binarize(img_path)
        img=self.remove_watermark(img)
        return img

    def img_to_text(self,img,lang="spa"):
        text=pytesseract.image_to_string(img,lang=lang,config=PYTESSERACT_DEFAULT_CONFIG)   
        return text
    
    def _run(self,img_path,save_to_disk=False):
        img=self.process_image(img_path)
        text=self.img_to_text(img)
        if save_to_disk:
            with open(f"/tmp/{str(img_path).split('/')[-1].replace('.jpg','.txt')}",'w') as f:
                f.write(text)
            cv2.imwrite(f"images/rotated-{img_pth.name}",img)
        return text

    # as used in langchain documentation https://python.langchain.com/docs/modules/agents/tools/custom_tools
    async def _arun(self, img_path: str,save_to_disk=False, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("does not support async")


if __name__=="__main__":
    processor=ImageProcessor()
    image_paths=list(Path("images/raw").glob("*.jpg"))
    for img_pth in tqdm(image_paths,desc="Img Preproc+ OCR "):
        text=processor.run(str(img_pth),save_to_disk=True)
        print(img_pth,text)


