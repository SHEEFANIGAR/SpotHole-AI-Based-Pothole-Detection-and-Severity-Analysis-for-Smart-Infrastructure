from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, send_from_directory
import cv2
import supervision as sv
from ultralytics import YOLO
import os
import random
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import google.generativeai as genai
import base64

# -------------------- CONFIG --------------------
print("Flask running from:", os.getcwd())

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

PR_MODEL_PATH = "best.pt"

# Globals
detection_count = 0
uploaded_file_path = None
geo_detections = []

# -------------------- GPS Extraction --------------------
def get_exif_gps(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None

        gps_info = {}
        for key, val in exif_data.items():
            tag = TAGS.get(key)
            if tag == 'GPSInfo':
                for t in val:
                    sub_tag = GPSTAGS.get(t)
                    gps_info[sub_tag] = val[t]

        def convert_to_degrees(value):
            d, m, s = value
            return float(d[0] / d[1]) + float(m[0] / d[1]) / 60 + float(s[0] / s[1]) / 3600

        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            if gps_info.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_info.get('GPSLongitudeRef') == 'W':
                lon = -lon
            return round(lat, 6), round(lon, 6)
        else:
            return None
    except Exception as e:
        print("⚠️ GPS extraction failed:", e)
        return None

# -------------------- YOLO + Visualization --------------------
class PyResearchVisualizer:
    """Simple Visualizer without restrictions"""

    def __init__(self):
        self.model = YOLO(PR_MODEL_PATH)
        self.box_annotator = sv.BoxAnnotator(thickness=2, color=sv.Color.from_hex("#0055FF"))
        self.label_annotator = sv.LabelAnnotator(text_scale=0.7, text_thickness=1, text_color=sv.Color.WHITE)

    def process_frame(self, frame):
        global detection_count, geo_detections, uploaded_file_path

        results = self.model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        detection_count = len(detections)

        gps_coords = None
        if uploaded_file_path and uploaded_file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            gps_coords = get_exif_gps(uploaded_file_path)

        for i in range(len(detections)):
            if gps_coords:
                lat, lon = gps_coords
            else:
                lat = round(16.506 + random.uniform(-0.03, 0.03), 6)
                lon = round(80.648 + random.uniform(-0.03, 0.03), 6)

            x1, y1, x2, y2 = detections.xyxy[i]
            area = int((x2 - x1) * (y2 - y1))

            # Rough severity by area
            if area > 80000:
                severity = "Severe"
            elif area > 30000:
                severity = "Moderate"
            else:
                severity = "Minor"

            geo_detections.append({
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "area": area,
                "severity": severity
            })

        annotated = self.box_annotator.annotate(scene=frame, detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections)
        return annotated

# -------------------- Frame Generator --------------------
def generate_frames(file_path):
    visualizer = PyResearchVisualizer()

    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        cap = cv2.VideoCapture(file_path)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            output_frame = visualizer.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', output_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        cap.release()
    else:
        frame = cv2.imread(file_path)
        if frame is not None:
            output_frame = visualizer.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', output_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# -------------------- Routes --------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_path
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    uploaded_file_path = file_path
    return redirect(url_for('video_feed_page'))

@app.route('/video_feed_page')
def video_feed_page():
    return render_template('video.html')

@app.route('/video_feed')
def video_feed():
    global uploaded_file_path
    if not uploaded_file_path:
        return "No file uploaded", 400
    return Response(generate_frames(uploaded_file_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_count')
def get_detection_count():
    return jsonify({'detections': detection_count})

@app.route('/geo_data')
def get_geo_data():
    return jsonify(geo_detections[-10:])

# -------------------- PDF REPORT --------------------
@app.route('/generate_report')
def generate_report():
    if not geo_detections:
        return jsonify({"error": "No detections found"}), 400

    report_path = os.path.join(app.config['UPLOAD_FOLDER'], "pothole_report.pdf")
    doc = SimpleDocTemplate(report_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Pothole Detection Report</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    total = len(geo_detections)
    severe = sum(1 for d in geo_detections if d["severity"] == "Severe")
    moderate = sum(1 for d in geo_detections if d["severity"] == "Moderate")
    minor = sum(1 for d in geo_detections if d["severity"] == "Minor")

    summary_text = f"""
    Total Potholes: {total}<br/>
    Severe: {severe}<br/>
    Moderate: {moderate}<br/>
    Minor: {minor}<br/>
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [["Timestamp", "Latitude", "Longitude", "Severity", "Area(px²)"]]
    for d in geo_detections[-20:]:
        data.append([d["timestamp"], d["lat"], d["lon"], d["severity"], d["area"]])

    table = Table(data, colWidths=[120, 80, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)

    return jsonify({"message": "Report generated", "report_path": report_path})

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------- Gemini AI Analysis --------------------
genai.configure(api_key="AIzaSyDckuJ1oLffdVwqp90hAtk6rq85KZg7hP0")

@app.route('/analyze_pothole', methods=['POST'])
def analyze_pothole():
    global uploaded_file_path
    if not uploaded_file_path:
        return jsonify({"error": "No uploaded file found."}), 400

    try:
        with open(uploaded_file_path, "rb") as f:
            image_data = f.read()

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([
            {"mime_type": "image/jpeg", "data": base64.b64encode(image_data).decode()},
            "You are a civil engineer. Describe the road condition and pothole severity briefly."
        ])

        return jsonify({"analysis": response.text.strip()})
    except Exception as e:
        print("Gemini API error:", e)
        return jsonify({"error": str(e)}), 500

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
