import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from google import genai
import os
import json

# --- Config & Data ---
st.set_page_config(page_title="E-Waste Detector", page_icon="♻️", layout="wide")

cls_name = ['Air-Conditioner', 'Bar-Phone', 'Battery', 'Blood-Pressure-Monitor', 'Boiler', 'CRT-Monitor', 'CRT-TV', 'Calculator', 'Camera', 'Ceiling-Fan', 'Christmas-Lights', 'Clothes-Iron', 'Coffee-Machine', 'Compact-Fluorescent-Lamps', 'Computer-Keyboard', 'Computer-Mouse', 'Cooled-Dispenser', 'Cooling-Display', 'Dehumidifier', 'Desktop-PC', 'Digital-Oscilloscope', 'Dishwasher', 'Drone', 'Electric-Bicycle', 'Electric-Guitar', 'Electrocardiograph-Machine', 'Electronic-Keyboard', 'Exhaust-Fan', 'Flashlight', 'Flat-Panel-Monitor', 'Flat-Panel-TV', 'Floor-Fan', 'Freezer', 'Glucose-Meter', 'HDD', 'Hair-Dryer', 'Headphone', 'LED-Bulb', 'Laptop', 'Microwave', 'Music-Player', 'Neon-Sign', 'Network-Switch', 'Non-Cooled-Dispenser', 'Oven', 'PCB', 'Patient-Monitoring-System', 'Photovoltaic-Panel', 'PlayStation-5', 'Power-Adapter', 'Printer', 'Projector', 'Pulse-Oximeter', 'Range-Hood', 'Refrigerator', 'Rotary-Mower', 'Router', 'SSD', 'Server', 'Smart-Watch', 'Smartphone', 'Smoke-Detector', 'Soldering-Iron', 'Speaker', 'Stove', 'Straight-Tube-Fluorescent-Lamp', 'Street-Lamp', 'TV-Remote-Control', 'Table-Lamp', 'Tablet', 'Telephone-Set', 'Toaster', 'Tumble-Dryer', 'USB-Flash-Drive', 'Vacuum-Cleaner', 'Washing-Machine', 'Xbox-Series-X']

value_mapping = {
    'Air-Conditioner': 1200, 'Bar-Phone': 100, 'Battery': 0, 'Blood-Pressure-Monitor': 50, 
    'Boiler': 800, 'CRT-Monitor': 0, 'CRT-TV': 0, 'Calculator': 30, 'Camera': 80, 
    'Ceiling-Fan': 150, 'Christmas-Lights': 20, 'Clothes-Iron': 50, 'Coffee-Machine': 100, 
    'Compact-Fluorescent-Lamps': 0, 'Computer-Keyboard': 30, 'Computer-Mouse': 20, 
    'Cooled-Dispenser': 500, 'Cooling-Display': 1500, 'Dehumidifier': 300, 'Desktop-PC': 850, 
    'Digital-Oscilloscope': 1000, 'Dishwasher': 800, 'Drone': 250, 'Electric-Bicycle': 2000, 
    'Electric-Guitar': 300, 'Electrocardiograph-Machine': 2000, 'Electronic-Keyboard': 400, 
    'Exhaust-Fan': 100, 'Flashlight': 20, 'Flat-Panel-Monitor': 150, 'Flat-Panel-TV': 500, 
    'Floor-Fan': 80, 'Freezer': 1000, 'Glucose-Meter': 30, 'HDD': 60, 'Hair-Dryer': 40, 
    'Headphone': 30, 'LED-Bulb': 0, 'Laptop': 650, 'Microwave': 200, 'Music-Player': 50, 
    'Neon-Sign': 100, 'Network-Switch': 100, 'Non-Cooled-Dispenser': 300, 'Oven': 600, 
    'PCB': 350, 'Patient-Monitoring-System': 3000, 'Photovoltaic-Panel': 800, 'PlayStation-5': 400, 
    'Power-Adapter': 30, 'Printer': 150, 'Projector': 300, 'Pulse-Oximeter': 20, 'Range-Hood': 400, 
    'Refrigerator': 1500, 'Rotary-Mower': 600, 'Router': 40, 'SSD': 50, 'Server': 1000, 
    'Smart-Watch': 100, 'Smartphone': 200, 'Smoke-Detector': 0, 'Soldering-Iron': 30, 
    'Speaker': 100, 'Stove': 500, 'Straight-Tube-Fluorescent-Lamp': 0, 'Street-Lamp': 300, 
    'TV-Remote-Control': 10, 'Table-Lamp': 40, 'Tablet': 150, 'Telephone-Set': 50, 
    'Toaster': 50, 'Tumble-Dryer': 800, 'USB-Flash-Drive': 10, 'Vacuum-Cleaner': 200, 
    'Washing-Machine': 1200, 'Xbox-Series-X': 400
}

hazard_mapping = {
    'Battery': 'HAZMAT WARNING: Fire risk. Contains heavy metals/acid. Do NOT crush or puncture.',
    'CRT-Monitor': 'HAZMAT WARNING: Contains high levels of Lead and Phosphorus glass. Handle carefully.',
    'CRT-TV': 'HAZMAT WARNING: Contains high levels of Lead and Phosphorus glass. Handle carefully.',
    'Compact-Fluorescent-Lamps': 'HAZMAT WARNING: Contains Mercury vapor. Extremely toxic if broken.',
    'Straight-Tube-Fluorescent-Lamp': 'HAZMAT WARNING: Contains Mercury vapor. Extremely toxic if broken.',
    'Smoke-Detector': 'HAZMAT WARNING: Contains radioactive materials (Americium-241). Special disposal required.',
    'Air-Conditioner': 'HAZMAT WARNING: Contains harmful refrigerants. Must be evacuated professionally.',
    'Refrigerator': 'HAZMAT WARNING: Contains harmful refrigerants. Must be evacuated professionally.',
    'Freezer': 'HAZMAT WARNING: Contains harmful refrigerants. Must be evacuated professionally.',
    'Dehumidifier': 'HAZMAT WARNING: Contains harmful refrigerants. Must be evacuated professionally.'
}

fallback_impacts = {
    "Battery": "Batteries contain lithium, cobalt, and toxic heavy metals. They can easily start fires if punctured or crushed in normal trash. Recycle at designated battery drop-off locations.",
    "Smartphone": "Smartphones contain valuable metals like gold, silver, and copper, but also toxic lead and mercury. Dropping them in landfills poisons soil and groundwater.",
    "Laptop": "Laptops hold a large lithium-ion battery and complex circuitry. E-waste recycling facilities can recover their precious metals and safely neutralize the battery.",
    "Keyboard": "Keyboards are mostly plastic and minor circuitry. While not highly toxic, they break down into microplastics if discarded improperly.",
    "Mouse": "Computer mice contribute to electronic plastic waste. Specialized recyclers can shred them to recover copper wiring and ABS plastic.",
    "PCB": "Printed Circuit Boards are the goldmines of e-waste, containing copper, gold, and palladium. However, they also contain toxic brominated flame retardants.",
    "Motherboard": "Motherboards are dense with valuable metals but coated in toxic flame retardants. Professional smelting is required to safely extract the gold and silver.",
    "CRT-Monitor": "Old CRT monitors are extremely hazardous, containing several pounds of lead glass. They must be carefully disassembled by certified professionals.",
    "CRT-TV": "Old CRT TVs are extremely hazardous, containing several pounds of lead glass. They must be carefully disassembled by certified professionals.",
    "Compact-Fluorescent-Lamps": "CFLs contain highly toxic mercury vapor. If broken, they contaminate the surrounding air and soil. Must be recycled safely.",
    "Straight-Tube-Fluorescent-Lamp": "Fluorescent tubes contain highly toxic mercury vapor. If broken, they contaminate the surrounding air and soil. Must be recycled safely.",
    "Smoke-Detector": "Smoke detectors contain a small amount of radioactive Americium-241. They should be mailed back to the manufacturer or taken to specialized hazardous waste centers.",
    "Air-Conditioner": "Air conditioners contain toxic refrigerants (CFCs/HFCs) that are incredibly potent greenhouse gases if released into the atmosphere.",
    "Refrigerator": "Refrigerators contain toxic refrigerants (CFCs/HFCs) that are incredibly potent greenhouse gases if released into the atmosphere.",
    "Freezer": "Freezers contain toxic refrigerants (CFCs/HFCs) that are incredibly potent greenhouse gases if released into the atmosphere.",
    "Dehumidifier": "Dehumidifiers contain toxic refrigerants (CFCs/HFCs) that are incredibly potent greenhouse gases if released into the atmosphere."
}

# --- Caching logic ---

@st.cache_resource
def load_yolo_model():
    try:
        model = YOLO("runs/detect/train-8/weights/best.pt")
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_yolo_model()

if "gemini_cache" not in st.session_state:
    st.session_state["gemini_cache"] = {}

def fetch_gemini_info(class_name):
    if class_name in st.session_state["gemini_cache"]:
        return st.session_state["gemini_cache"][class_name]
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return "API Key missing! Please set GEMINI_API_KEY."

        client = genai.Client(api_key=api_key)
        prompt = f"Provide a brief, 2-sentence explanation of the environmental impact of {class_name} as e-waste, and mention if it is hazardous and why. Keep it punchy and informative. Also briefly suggest how to recycle it."
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        res_text = response.text
        st.session_state["gemini_cache"][class_name] = res_text
        return res_text
    except Exception as e:
        fallback = fallback_impacts.get(class_name, f"{class_name} should be handled by a certified e-waste recycling facility to recover materials and prevent environmental contamination.")
        st.session_state["gemini_cache"][class_name] = fallback
        return fallback

def process_frame_for_info(img_array):
    if model is None:
        return img_array, None
    
    # Using balanced conf, stricter IOU, and agnostic NMS to reduce false positives while maintaining detection
    result = model.predict(source=img_array, save=False, verbose=False, conf=0.45, iou=0.45, agnostic_nms=True, imgsz=640)[0]
    boxes = result.boxes
    
    info = None
    if boxes is not None and len(boxes) > 0:
        plotted_frame = result.plot()
        
        best_box = max(boxes, key=lambda b: b.conf[0].item())
        class_index = int(best_box.cls[0].item())
        confidence = float(best_box.conf[0].item())
        current_class = cls_name[class_index]
        conf_pct = int(confidence * 100)
        
        val = value_mapping.get(current_class, 20)
        value_str = f"₹{val}"
        
        is_hazard = current_class in hazard_mapping
        
        info = {
            'class': current_class,
            'confidence': conf_pct,
            'value': value_str,
            'hazard': is_hazard,
            'hazard_text': hazard_mapping.get(current_class, ""),
        }
        return plotted_frame, info
        
    return img_array, None

def process_image_with_gemini(img_array):
    info = None
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            client = genai.Client(api_key=api_key)
            pil_img = Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
            
            prompt = f"""
Analyze this image and identify if there is any E-Waste (electronic waste) in it.
Identify the closest matching category from this list: {', '.join(cls_name)}.
If none match well, just say 'None'.
Respond ONLY with a JSON object in this format (no code blocks, just raw JSON):
{{
    "class": "Category Name",
    "confidence": 99,
    "impact": "A brief 2-sentence explanation of the environmental impact, if it is hazardous and why, and how to recycle it."
}}
"""
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[prompt, pil_img]
            )
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            
            c_name = data.get("class", "None")
            val = value_mapping.get(c_name, 0)
            is_hazard = c_name in hazard_mapping
            
            if c_name != "None":
                info = {
                    'class': c_name,
                    'confidence': data.get("confidence", 95),
                    'value': f"₹{val}",
                    'hazard': is_hazard,
                    'hazard_text': hazard_mapping.get(c_name, ""),
                    'impact': data.get("impact", "Identified by Gemini AI.")
                }
    except Exception as e:
        # Silently fallback to YOLO if Gemini Vision API hits rate limits
        pass

    processed_frame = img_array
    if not info:
        processed_frame, info = process_frame_for_info(img_array)
        if info:
            c_name = info['class']
            info['impact'] = fetch_gemini_info(c_name)
        else:
            info = {
                'class': 'None',
                'confidence': 0,
                'value': '₹0',
                'hazard': False,
                'impact': 'No E-Waste detected.'
            }
            
    # Always try to plot boxes using YOLO if it finds anything, even if Gemini found it first
    # Or just rely on YOLO for bounding boxes:
    if info['class'] != 'None':
        # run YOLO for bounding boxes overlay
        processed_frame, yolo_info = process_frame_for_info(img_array)
        # if YOLO didn't find anything but Gemini did, keep original frame

    return processed_frame, info


# --- Streamlit UI ---
st.title("♻️ E-Waste Detector & Value Estimator")
st.markdown("Upload an image of an electronic item to detect its e-waste category, estimated value, and environmental impact.")

# Two columns for input choices
col1, col2 = st.columns(2)

with col1:
    st.subheader("Option 1: Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

with col2:
    st.subheader("Option 2: Use Camera")
    camera_image = st.camera_input("Take a picture")

image_to_process = None

if uploaded_file is not None:
    image_to_process = Image.open(uploaded_file)
elif camera_image is not None:
    image_to_process = Image.open(camera_image)

if image_to_process is not None:
    # Convert PIL to CV2 format
    img_array = np.array(image_to_process)
    if img_array.shape[-1] == 4:
        # Convert RGBA to RGB
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    
    # BGR for OpenCV processing
    cv2_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    st.markdown("### Processing Image...")
    with st.spinner("Analyzing with YOLO & Gemini..."):
        processed_img, info = process_image_with_gemini(cv2_img)

    # Convert back to RGB for displaying in Streamlit
    display_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)

    # Display results
    res_col1, res_col2 = st.columns([1, 1])
    
    with res_col1:
        st.image(display_img, caption="Detected E-Waste", use_column_width=True)
        
    with res_col2:
        if info and info['class'] != 'None':
            st.success(f"**Detected:** {info['class']} (Confidence: {info['confidence']}%)")
            st.info(f"**Estimated Value:** {info['value']}")
            
            if info['hazard']:
                st.error(f"⚠️ {info['hazard_text']}")
                
            st.markdown("### Environmental Impact & Recycling")
            st.write(info['impact'])
        else:
            st.warning("No E-Waste detected in this image.")
