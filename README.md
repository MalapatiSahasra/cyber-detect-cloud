Master Comparator (Fake Product Detection) 
AI-powered web application designed to detect counterfeit products. It uses Computer Vision and digital scanning to verify the authenticity of a suspect item by comparing it against a verified reference product.

---

✨ How It Works

The system evaluates products in two distinct phases:

1. Phase 1: Visual Verification**
       Shape Similarity:  Uses the **ORB (Oriented FAST and Rotated BRIEF)** algorithm via OpenCV to detect and match key geometric features between the real and suspect products.
       Color Similarity:  Converts images to HSV format and compares their color histograms to ensure the exact shades and dyes match the original.

2. Phase 2: Digital Verification**
       Barcode / QR Scanning:  Uses `zxing-cpp` to scan product tags or boxes, extracting hidden digital signatures or URLs to verify the supply chain.

Based on these combined scores, the AI generates a final verdict of **MATCH CONFIRMED** or **MISMATCH DETECTED**.

🛠️ Tech Stack

Frontend:  HTML5, CSS3, Vanilla JavaScript (Fetch API)
Backend:  Python, Flask
Computer Vision:  OpenCV (`opencv-python-headless`), Numpy
Decoding:  ZXing-CPP
Deployment:  Render
