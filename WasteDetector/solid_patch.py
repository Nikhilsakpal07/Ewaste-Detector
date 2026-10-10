import cv2
import numpy as np

def draw_pill(img, x1, y1, x2, y2, color):
    r = (y2 - y1) // 2
    cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
    cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
    cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)

img = cv2.imread('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/translated_canva.png')

if img is not None:
    # CLASSIFY: cover y=120 to y=190
    light_blue = [int(x) for x in img[140, 70]] # Sample from the original pill
    draw_pill(img, 35, 120, 235, 195, light_blue)
    cv2.putText(img, "CLASSIFY", (65, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

    # Scanning: cover y=95 to y=165
    orange = [int(x) for x in img[100, 310]] # Sample from the orange background next to text
    cv2.rectangle(img, (240, 95), (460, 165), orange, -1)
    cv2.putText(img, "Scanning...", (250, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

    # IMPACT: (already mostly fine, but let's redraw white pill to be sure)
    draw_pill(img, 980, 215, 1220, 265, (255,255,255))
    cv2.putText(img, "IMPACT", (1030, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

    cv2.imwrite('Recibot/setUp/Canva.png', img)
    cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/final_canva_solid.png', img)
