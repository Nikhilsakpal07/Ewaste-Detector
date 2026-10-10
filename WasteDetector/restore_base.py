import cv2
import numpy as np

img = cv2.imread('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/translated_canva.png')

# Erase my bad edits by inpainting them with surrounding pixels
mask = np.zeros(img.shape[:2], dtype=np.uint8)
# The bad CLASSIFY box was drawn at: cv2.rectangle(img, (60, 145), (210, 185), c1, -1)
cv2.rectangle(mask, (55, 140), (215, 190), 255, -1)

# The bad Scanning... box was at: cv2.rectangle(img, (315, 115), (460, 150), c2, -1)
cv2.rectangle(mask, (310, 110), (465, 155), 255, -1)

# The bad IMPACT box was at: cv2.rectangle(img, (1000, 225), (1150, 255), c3, -1)
cv2.rectangle(mask, (995, 220), (1155, 260), 255, -1)

# Perform inpainting to restore the background
cleaned = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)
cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/clean_base.png', cleaned)
