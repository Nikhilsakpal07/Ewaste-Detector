import os
import cv2
import numpy as np
import threading
from flask import Flask, render_template, Response, request, jsonify
from ultralytics import YOLO
import base64
from google import genai
import imutils
import json
import socket
import time
import uuid

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

app = Flask(__name__)

# Constants and Data
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
    "CRT Monitor": "Old CRT monitors are extremely hazardous, containing several pounds of lead glass. They must be carefully disassembled by certified professionals.",
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

# Global State
model = None
model_error = ""

gemini_cache = {}
fetching_classes = set()

# Lock for camera
camera_lock = threading.Lock()
cap = None
is_streaming = False
mobile_sync_data = None
INVENTORY_FILE = "inventory.json"

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_inventory_to_disk():
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory_history, f, indent=4)

inventory_history = load_inventory()

def save_to_inventory(info, img_array):
    if info and info.get('class') != 'None':
        filename = f"item_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        # Convert RGB back to BGR for cv2 if needed, but it should already be BGR
        cv2.imwrite(filepath, img_array)
        
        record = {
            "id": filename,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": f"/static/uploads/{filename}",
            "info": info
        }
        inventory_history.insert(0, record)
        save_inventory_to_disk()

latest_detection_info = {
    'class': 'None',
    'confidence': 0,
    'value': '₹0',
    'hazard': False,
    'impact': 'Waiting for detection...'
}

def fetch_gemini_info(class_name):
    if class_name in gemini_cache:
        return gemini_cache[class_name]
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return "API Key missing! Please set GEMINI_API_KEY."

        client = genai.Client(api_key=api_key)
        prompt = f"Provide a brief, 2-sentence explanation of the environmental impact of {class_name} as e-waste, and mention if it is hazardous and why. Keep it punchy and informative. Also briefly suggest how to recycle it."
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        gemini_cache[class_name] = response.text
        return response.text
    except Exception as e:
        error_msg = f"API Error: {str(e)}"
        print(f"Gemini API Error for {class_name}: {error_msg}")
        # Use our intelligent fallback instead of showing a rate limit error to the user
        fallback = fallback_impacts.get(class_name, f"{class_name} should be handled by a certified e-waste recycling facility to recover materials and prevent environmental contamination.")
        gemini_cache[class_name] = fallback
        return fallback

def process_frame_for_info(frame):
    global model, model_error
    
    # Lazy load the model to save RAM on boot and catch exact crash moments
    if model is None and model_error == "":
        try:
            import torch
            torch.set_num_threads(1)  # Drastically reduces RAM usage on Render
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "runs", "detect", "train-8", "weights", "best.pt")
            model = YOLO(model_path)
        except Exception as e:
            model_error = str(e)
            print(f"Error loading model: {e}")

    if model is None:
        return frame, {
            'class': 'None',
            'confidence': 0,
            'value': '₹0',
            'hazard': False,
            'impact': f'CRITICAL ERROR: YOLO failed to load! Details: {model_error}'
        }
    
    # Lowered confidence threshold to 0.15 to ensure detections happen
    result = model.predict(source=frame, save=False, verbose=False, conf=0.15, iou=0.5)[0]
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
        
    return frame, None

def generate_frames():
    global cap, latest_detection_info, is_streaming
    
    with camera_lock:
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(0)
    
    is_streaming = True
    
    while is_streaming:
        with camera_lock:
            if cap is None or not cap.isOpened():
                break
            success, frame = cap.read()
            
        if not success:
            break
        
        processed_frame, info = process_frame_for_info(frame)
        
        if info:
            # We want to update global latest_detection_info but we don't want to block the video stream waiting for Gemini
            c_name = info['class']
            impact_text = "Checking Gemini AI..."
            if c_name in gemini_cache:
                impact_text = gemini_cache[c_name]
            elif c_name not in fetching_classes:
                fetching_classes.add(c_name)
                # Fire and forget thread
                def bg_fetch(name):
                    txt = fetch_gemini_info(name)
                    gemini_cache[name] = txt
                    fetching_classes.discard(name)
                threading.Thread(target=bg_fetch, args=(c_name,), daemon=True).start()
                
            info['impact'] = impact_text
            latest_detection_info = info
        else:
            latest_detection_info = {
                'class': 'None',
                'confidence': 0,
                'value': '₹0',
                'hazard': False,
                'impact': 'Scanning...'
            }
            
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', local_ip=get_local_ip())

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stop_stream', methods=['POST'])
def stop_stream():
    global is_streaming, cap
    is_streaming = False
    with camera_lock:
        if cap is not None:
            cap.release()
            cap = None
    return jsonify({"status": "stopped"})

@app.route('/api/latest_detection')
def get_latest_detection():
    return jsonify(latest_detection_info)

@app.route('/api/desktop_sync')
def desktop_sync():
    global mobile_sync_data
    if mobile_sync_data:
        data = mobile_sync_data
        mobile_sync_data = None
        return jsonify({"has_new": True, "data": data})
    return jsonify({"has_new": False})

@app.route('/api/inventory')
def get_inventory():
    return jsonify(inventory_history)

@app.route('/api/mobile_upload', methods=['POST'])
def mobile_upload():
    global mobile_sync_data
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
        
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    processed_frame, info = process_frame_for_info(frame)
    
    if info:
        c_name = info['class']
        info['impact'] = fetch_gemini_info(c_name)
        save_to_inventory(info, processed_frame)
    else:
        info = {
            'class': 'None',
            'confidence': 0,
            'value': '₹0',
            'hazard': False,
            'impact': 'No E-Waste detected in frame.'
        }
        
    _, buffer = cv2.imencode('.jpg', processed_frame)
    base64_img = base64.b64encode(buffer).decode('utf-8')
    
    mobile_sync_data = {
        "info": info,
        "image": f"data:image/jpeg;base64,{base64_img}"
    }
    return jsonify({"status": "success", "data": mobile_sync_data})

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
            
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Failed to decode image using cv2.imdecode. Is it a valid image file?"}), 400
        
        processed_frame, info = process_frame_for_info(frame)
        
        if info:
            c_name = info['class']
            info['impact'] = fetch_gemini_info(c_name)
            save_to_inventory(info, processed_frame)
        else:
            info = {
                'class': 'None',
                'confidence': 0,
                'value': '₹0',
                'hazard': False,
                'impact': 'No E-Waste detected in frame.'
            }
            
        _, buffer = cv2.imencode('.jpg', processed_frame)
        base64_img = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "info": info,
            "image": f"data:image/jpeg;base64,{base64_img}"
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/analyze_frame_yolo', methods=['POST'])
def analyze_frame_yolo():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
            
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Failed to decode image using cv2.imdecode. Is it a valid image file?"}), 400
        
        processed_frame, info = process_frame_for_info(frame)
        
        if info:
            c_name = info['class']
            impact_text = "Checking Gemini AI..."
            if c_name in gemini_cache:
                impact_text = gemini_cache[c_name]
            elif c_name not in fetching_classes and c_name != 'None':
                fetching_classes.add(c_name)
                def bg_fetch(name):
                    txt = fetch_gemini_info(name)
                    gemini_cache[name] = txt
                    fetching_classes.discard(name)
                threading.Thread(target=bg_fetch, args=(c_name,), daemon=True).start()
                
            info['impact'] = impact_text
        else:
            info = {
                'class': 'None',
                'confidence': 0,
                'value': '₹0',
                'hazard': False,
                'impact': 'Scanning...'
            }
            
        _, buffer = cv2.imencode('.jpg', processed_frame)
        base64_img = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "info": info,
            "image": f"data:image/jpeg;base64,{base64_img}"
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
