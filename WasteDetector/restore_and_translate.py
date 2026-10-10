import cv2
import numpy as np

def draw_pill(img, x1, y1, x2, y2, color):
    r = (y2 - y1) // 2
    cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
    cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
    cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)

img = cv2.imread('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/translated_canva.png')

if img is not None:
    # 1. Colors
    beige = (223, 238, 252) # BGR for the beige panel (actually it looks like a light yellowish color, let's sample it)
    beige = [int(x) for x in img[400, 100]]
    orange = [int(x) for x in img[100, 600]]
    light_blue = [int(x) for x in img[125, 70]] # From the visible pill part
    if sum(light_blue) < 100:
        light_blue = (230, 218, 209) # Approx light blue in BGR

    # 2. Fix the CLASSIFY pill area
    # Paint beige over the whole top left area up to x=230 to erase the old CLASIFICACIÓN and CLASSIFY
    cv2.rectangle(img, (20, 100), (235, 200), beige, -1)
    
    # Redraw light blue pill for CLASSIFY
    draw_pill(img, 40, 140, 230, 185, light_blue)
    text1 = "CLASSIFY"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thick = 2
    size1 = cv2.getTextSize(text1, font, scale, thick)[0]
    x_pos1 = 40 + (190 - size1[0]) // 2
    y_pos1 = 140 + (45 + size1[1]) // 2 - 2
    cv2.putText(img, text1, (x_pos1, y_pos1), font, scale, (0,0,0), thick)

    # 3. Fix the Escaneando... area
    # Paint orange over the old Escaneando and Scanning...
    cv2.rectangle(img, (240, 90), (420, 160), orange, -1)
    text2 = "Scanning..."
    cv2.putText(img, text2, (250, 140), font, scale, (0,0,0), thick)

    # 4. IMPACT (Already mostly fixed in translated_canva.png, but let's redraw pill to be clean)
    draw_pill(img, 990, 225, 1180, 265, (255,255,255))
    text3 = "IMPACT"
    size3 = cv2.getTextSize(text3, font, scale, thick)[0]
    x_pos3 = 990 + (190 - size3[0]) // 2
    y_pos3 = 225 + (40 + size3[1]) // 2 - 2
    cv2.putText(img, text3, (x_pos3, y_pos3), font, scale, (0,0,0), thick)

    # Bottom text is already RECYCLE CONSCIOUSLY in translated_canva.png
    
    # Save back to the actual asset folder
    cv2.imwrite('Recibot/setUp/Canva.png', img)
    cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/final_canva_restored.png', img)
