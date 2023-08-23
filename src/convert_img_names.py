from pathlib import Path
import os

IMAGES_PATH="images"


if __name__=="__main__":
    file_list=list(Path(IMAGES_PATH).glob("*.jpg*"))
    for idx,img in enumerate(file_list):
        new_name=f'{IMAGES_PATH}\invoice{idx}{img.suffix}'       
        if not Path(new_name).exists():    
            os.rename(str(img),new_name) 