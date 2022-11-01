import cv2
import numpy as np
import pandas as pd
import pytesseract


@staticmethod
def load_image(uploaded_file) -> pd.DataFrame:
    image = cv2.imdecode(np.frombuffer(uploaded_file.getvalue(), dtype=np.uint8), -1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(image)
    return pd.Series(text.splitlines()).to_frame()
