import cv2
import numpy as np

def inpaint_text(img, region, new_text, text_pos, scale, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX, color=(0,0,0)):
    x1, y1, x2, y2 = region
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    # Extract ROI
    roi = img[y1:y2, x1:x2]
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Text is dark, so threshold to find dark pixels
    # You might need to adjust threshold value
    _, mask_roi = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    
    # Clean up mask (dilate slightly to cover text edges)
    kernel = np.ones((3,3), np.uint8)
    mask_roi = cv2.dilate(mask_roi, kernel, iterations=1)
    
    mask[y1:y2, x1:x2] = mask_roi
    
    # Inpaint
    inpainted = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)
    
    # Draw new text
    if new_text:
        cv2.putText(inpainted, new_text, text_pos, font, scale, color, thickness)
        
    return inpainted

# 1. Patch Canva.png
canva_path = 'Recibot/setUp/Canva.png'
img = cv2.imread(canva_path)
if img is not None:
    # CLASIFICACIÓN
    img = inpaint_text(img, (40, 130, 230, 180), "CLASSIFY", (75, 170), 0.8, 2)
    # Escaneando...
    img = inpaint_text(img, (240, 110, 390, 160), "Scanning...", (250, 150), 0.7, 2)
    # IMPACTO
    # White pill is around 760 to 950? Wait, text is around 800? 
    # Let's check translated_canva.png. The white box was around x=1000. Let's make region generous: x=900 to 1250, y=190 to 240
    # Actually, inpaint_text only affects dark pixels, so a generous region is safe if there's no other dark stuff.
    # The letters "IMPACTO" are dark. The white background will remain untouched.
    img = inpaint_text(img, (950, 190, 1250, 250), "IMPACT", (1030, 230), 0.7, 2)
    
    # RECICLA CON CONCIENCIA
    # Text is thick black text.
    img = inpaint_text(img, (250, 650, 1050, 720), "RECYCLE CONSCIOUSLY", (450, 705), 1.2, 3)

    cv2.imwrite(canva_path, img)
    cv2.imwrite('C:/Users/Lenovo/.gemini/antigravity-ide/brain/d5f9fd83-b324-429e-9c9a-b387e2cbab8d/scratch/final_canva.png', img)

# 2. Patch class images
class_files = {
    'metal.png': 'Metal',
    'organico.png': 'Organic',
    'papel_y_carton.png': 'Paper',
    'plastico.png': 'Plastic',
    'vidrio.png': 'Glass'
}

for filename, en_text in class_files.items():
    path = f'Recibot/setUp/{filename}'
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED) # preserve alpha if any
    
    if img is not None:
        # Most of these images are ~200x200, text is at the bottom (y=150 to 200).
        # We only inpaint the RGB channels
        rgb = img[:, :, :3] if img.shape[2] == 4 else img.copy()
        
        # Region: bottom part of image
        h, w = rgb.shape[:2]
        region = (0, int(h*0.75), w, h)
        
        # Inpaint
        rgb = inpaint_text(rgb, region, "", (0,0), 1) # Just erase
        
        # Add text centered
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        thickness = 2
        size = cv2.getTextSize(en_text, font, scale, thickness)[0]
        x_pos = (w - size[0]) // 2
        # y position around 90% of height
        y_pos = int(h * 0.9)
        cv2.putText(rgb, en_text, (x_pos, y_pos), font, scale, (0, 0, 0), thickness)
        
        if img.shape[2] == 4:
            img[:, :, :3] = rgb
        else:
            img = rgb
            
        cv2.imwrite(path, img)

print("Patching complete.")
