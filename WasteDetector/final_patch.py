import cv2
import numpy as np

def erase_text_smart(img, region):
    x1, y1, x2, y2 = region
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    roi = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, mask_roi = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3,3), np.uint8)
    mask_roi = cv2.dilate(mask_roi, kernel, iterations=1)
    mask[y1:y2, x1:x2] = mask_roi
    return cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

img = cv2.imread('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/clean_base.png')

if img is not None:
    # 1. CLASIFICACIÓN
    img = erase_text_smart(img, (50, 140, 210, 175))
    cv2.putText(img, "CLASSIFY", (75, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

    # 2. Escaneando...
    img = erase_text_smart(img, (240, 115, 380, 155))
    cv2.putText(img, "Scanning...", (250, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

    # 3. IMPACT (Already erased in clean_base)
    cv2.putText(img, "IMPACT", (1030, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

    cv2.imwrite('Recibot/setUp/Canva.png', img)
    cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/final_canva_perfect.png', img)
