import cv2
import numpy as np

def draw_pill(img, x1, y1, x2, y2, color):
    r = (y2 - y1) // 2
    cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
    cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
    cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)

img = cv2.imread('Recibot/setUp/Canva.png')

if img is not None:
    # 1. CLASIFICACIÓN (Light blue pill)
    # Get color from top right of the screen? No, get it from a clean spot inside the pill
    # In my patched image, the pill at (220, 160) should be clean.
    bg_pill_1 = [int(x) for x in img[160, 220]]
    # Draw pill to completely cover old text and my bad patch
    draw_pill(img, 35, 135, 240, 195, bg_pill_1)
    # Write text centered
    text1 = "CLASSIFY"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thick = 2
    size1 = cv2.getTextSize(text1, font, scale, thick)[0]
    x_pos1 = 35 + (240 - 35 - size1[0]) // 2
    y_pos1 = 135 + (195 - 135 + size1[1]) // 2 - 2
    cv2.putText(img, text1, (x_pos1, y_pos1), font, scale, (0,0,0), thick)

    # 2. Escaneando... (Orange background)
    # Get color from background at (250, 90)
    bg_orange = [int(x) for x in img[90, 250]]
    cv2.rectangle(img, (240, 110), (450, 170), bg_orange, -1)
    text2 = "Scanning..."
    size2 = cv2.getTextSize(text2, font, scale, thick)[0]
    cv2.putText(img, text2, (250, 150), font, scale, (0,0,0), thick)

    # 3. IMPACTO (White pill)
    # The white pill was roughly x=980 to 1220, y=210 to 270.
    # Color is white
    draw_pill(img, 980, 215, 1220, 265, (255,255,255))
    text3 = "IMPACT"
    size3 = cv2.getTextSize(text3, font, scale, thick)[0]
    x_pos3 = 980 + (1220 - 980 - size3[0]) // 2
    y_pos3 = 215 + (265 - 215 + size3[1]) // 2 - 2
    cv2.putText(img, text3, (x_pos3, y_pos3), font, scale, (0,0,0), thick)
    
    cv2.imwrite('Recibot/setUp/Canva.png', img)
    cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/fixed_canva.png', img)

