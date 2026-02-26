from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
import base64

# --- SAFE IMPORTS ---
try:
    import pytesseract
    import zxingcpp
    ADVANCED_MODE = True
except ImportError:
    ADVANCED_MODE = False

app = Flask(__name__)
CORS(app)

# --- NEW: Serve the Website ---
@app.route('/')
def home():
    return render_template('index.html')

# --- CONFIGURATION ---
ORB_MATCH_THRESHOLD = 15   # Needs 15 matching points
COLOR_THRESHOLD = 0.75     # Needs 75% color match

def decode_image(base64_string):
    if not base64_string: return None
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# --- COMPARISON LOGIC ---
def check_shape(img1, img2):
    if img1 is None or img2 is None: return False, 0
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    if des1 is None or des2 is None: return False, 0
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = [m for m in matches if m.distance < 50]
    
    return len(good_matches) >= ORB_MATCH_THRESHOLD, len(good_matches)

def check_color(img1, img2):
    if img1 is None or img2 is None: return False, 0
    try:
        hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
        
        hist1 = cv2.calcHist([hsv1], [0,1], None, [50,60], [0,180,0,256])
        hist2 = cv2.calcHist([hsv2], [0,1], None, [50,60], [0,180,0,256])
        
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return score >= COLOR_THRESHOLD, score
    except: return True, 1.0

def scan_qr(image):
    if image is None: return False, "No Image"
    if not ADVANCED_MODE: return False, "Skipped"
    try:
        # <-- FIX: New cloud-friendly zxing-cpp logic
        barcodes = zxingcpp.read_barcodes(image)
        if len(barcodes) > 0:
            url = barcodes[0].text
            return True, url
        return False, "No QR Found"
    except Exception as e: 
        print(f"QR Error: {e}") # This will print the exact error in Render logs if it fails again
        return False, "Error"
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Get 3 Images
    ref_img = decode_image(data.get('reference_image'))
    test_img = decode_image(data.get('test_image'))
    qr_img = decode_image(data.get('qr_image'))
    
    # 1. Compare Visuals (Ref vs Test)
    shape_ok, shape_score = check_shape(ref_img, test_img)
    color_ok, color_score = check_color(ref_img, test_img)
    
    # 2. Scan QR (QR Image)
    qr_found, qr_data = scan_qr(qr_img)

    # 3. Final Verdict Logic
    # If QR is found, it's a strong sign (user must verify link).
    # If Visuals match, it's good.
    if qr_found:
        verdict = "MATCH CONFIRMED"
    elif shape_ok and  color_ok:
        verdict = "MATCH CONFIRMED"
    else:
        verdict = "MISMATCH DETECTED"

    return jsonify({
        "results": {
            "shape": {"passed": bool(shape_ok), "score": shape_score},
            "color": {"passed": bool(color_ok), "score": f"{color_score:.2f}"},
            "qr": {"found": bool(qr_found), "data": qr_data}
        },
        "verdict": verdict
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True)
