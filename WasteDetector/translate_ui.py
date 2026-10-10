import cv2
import numpy as np

img = cv2.imread('Recibot/setUp/Canva.png')
original = img.copy()

# Helper to get the most common color in a region (to avoid text)
def get_bg_color(img, x1, y1, x2, y2):
    roi = img[y1:y2, x1:x2]
    # Simple heuristic: pick a pixel that is not black
    for r in range(roi.shape[0]):
        for c in range(roi.shape[1]):
            if np.mean(roi[r,c]) > 50:
                return [int(x) for x in roi[r,c]]
    return (255,255,255)

# 1. CLASIFICACIÓN
# Pill interior approx: x=50 to 220, y=140 to 180
# Wait, looking at the image, the red box was y=100 to 150 and the text was at the bottom. Let's use y=140 to 190.
c1 = get_bg_color(img, 70, 150, 80, 160)
cv2.rectangle(img, (60, 145), (210, 185), c1, -1)
cv2.putText(img, "CLASSIFY", (75, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

# 2. Escaneando...
# Green box was y=95 to 125.
c2 = get_bg_color(img, 315, 95, 325, 105)
cv2.rectangle(img, (315, 115), (460, 150), c2, -1)  # Adjusting Y based on observation
cv2.putText(img, "Scanning...", (320, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

# 3. IMPACTO
# Blue box was 980 to 1220, y=215 to 260
# White pill interior
c3 = (255, 255, 255)
cv2.rectangle(img, (1000, 225), (1150, 255), c3, -1)
cv2.putText(img, "IMPACT", (1030, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

# 4. RECICLA CON CONCIENCIA (Bottom Gradient)
# Yellow box was 300 to 1000, y=660 to 715
mask = np.zeros(img.shape[:2], dtype=np.uint8)
cv2.rectangle(mask, (320, 665), (960, 715), 255, -1)
# Inpaint the bottom text
img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

# Write the new text
text = "RECYCLE CONSCIOUSLY"
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1.5
thickness = 4
size = cv2.getTextSize(text, font, scale, thickness)[0]
x_pos = 640 - size[0] // 2
cv2.putText(img, text, (x_pos, 705), font, scale, (0, 0, 0), thickness)

cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/translated_canva.png', img)
