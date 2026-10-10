import cv2

img = cv2.imread('Recibot/setUp/Canva.png')
h, w = img.shape[:2]

# CLASIFICACIÓN
cv2.rectangle(img, (40, 100), (240, 150), (0, 0, 255), 2)
# Escaneando...
cv2.rectangle(img, (315, 95), (450, 125), (0, 255, 0), 2)
# IMPACTO
cv2.rectangle(img, (980, 215), (1220, 260), (255, 0, 0), 2)
# RECICLA CON CONCIENCIA
cv2.rectangle(img, (300, 660), (1000, 715), (0, 255, 255), 2)

cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/test_boxes.png', img)
