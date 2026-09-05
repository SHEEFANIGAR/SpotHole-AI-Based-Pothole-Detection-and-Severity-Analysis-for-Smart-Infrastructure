# 🕳️ SpotHole - AI-Based Pothole Detection & Severity Analysis

SpotHole is a real-time, AI-powered system that detects potholes from images and videos, analyzes their severity, geotags them on a live map, and generates plain-English road condition summaries using Generative AI.

Built for **smart infrastructure, automated road inspection, and road maintenance decision-making**.
---

## Overview

Manual pothole inspection is slow, labor-intensive, and difficult to scale across large road networks. **SpotHole** automates this process using computer vision and generative AI.

The system uses **YOLOv12** for real-time pothole detection, performs severity analysis based on pothole geometry, extracts GPS coordinates from image EXIF metadata, visualizes potholes on an interactive map, and uses **Google Gemini** to generate human-readable road condition summaries.

### Key Results

Evaluation was performed using **RDD2022 and Roboflow datasets** containing 10,000+ annotated instances.

| Model | mAP@0.5 | mAP@0.5:0.95 | FPS |
|---|---:|---:|---:|
| YOLOv8 | 0.931 | 0.598 | 62 |
| YOLOv10 | 0.948 | 0.631 | 70 |
| **YOLOv12 (SpotHole)** | **0.956** | **0.654** | **79** |

- **94.3%** agreement with expert road-condition labeling
- Approximately **79 FPS** real-time inference
- Automatic GPS-based geotagging using image EXIF metadata
- Automated pothole severity classification
- AI-generated road condition summaries

---

## Features

### Real-Time Pothole Detection

Upload an image or video and SpotHole detects potholes frame-by-frame using a trained YOLOv12 model.

### Severity Classification

Detected potholes are classified into:

- 🟢 Minor
- 🟡 Moderate
- 🔴 Severe

Severity is estimated using bounding-box geometry, area, and shape characteristics.

### GPS Geotagging

The system extracts GPS coordinates from image EXIF metadata and displays pothole locations on an interactive Leaflet.js map.

### AI-Generated Road Condition Summaries

Google Gemini analyzes detection results and generates plain-English road condition summaries and maintenance recommendations.

### PDF Reporting

Generate a formatted PDF report containing:

- Pothole detection results
- Severity breakdown
- Detection information
- GPS coordinates
- Road-condition summary

### Interactive Dashboard

The Flask-based dashboard provides:

- Image upload
- Video upload
- Real-time detection
- Detection counts
- Severity information
- Interactive map
- AI-generated summaries
- PDF report generation

---

## System Architecture

```text
                 Image / Video Upload
                         │
                         ▼
                  Flask Web Interface
                         │
                         ▼
                  OpenCV Processing
                         │
                         ▼
                  YOLOv12 Detection
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
          Bounding    Severity    EXIF GPS
           Boxes      Analysis    Extraction
              │          │          │
              │          │          ▼
              │          │      Leaflet.js
              │          │          │
              └──────────┼──────────┘
                         │
                         ▼
                    Gemini AI
                         │
                         ▼
              Road Condition Summary
                         │
                         ▼
              Dashboard + PDF Report
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python 3.9+ |
| Object Detection | YOLOv12 |
| Computer Vision | OpenCV |
| Detection Utilities | Supervision |
| Backend | Flask |
| Generative AI | Google Gemini API |
| Gemini Model | `gemini-2.5-flash` |
| Geospatial Processing | Pillow / EXIF |
| Interactive Map | Leaflet.js |
| PDF Generation | ReportLab |
| Training Data | RDD2022 + Roboflow |

---
# Getting Started

## Prerequisites

Make sure you have:

- Python **3.9 or later**
- Git
- Google Gemini API key
- Recommended: NVIDIA GPU for faster inference

---

## 1. Clone the Repository

```bash
git clone https://github.com/SHEEFANIGAR/SpotHole-AI-Based-Pothole-Detection-and-Severity-Analysis-for-Smart-Infrastructure.git
```

Move into the project directory:

```bash
cd SpotHole-AI-Based-Pothole-Detection-and-Severity-Analysis-for-Smart-Infrastructure
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Gemini API Configuration

SpotHole uses Google Gemini to generate natural-language road condition summaries.

Create a Gemini API key using **Google AI Studio**.

Set the API key as an environment variable.

### Windows CMD

```cmd
set GEMINI_API_KEY=your-api-key-here
```

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="your-api-key-here"
```

> **Never hardcode or commit your API key to GitHub.**

If you use a `.env` file, add it to `.gitignore`:

```text
.env
```

---

# Run the Application

Start the Flask application:

```bash
python app.py
```

Open the application in your browser:

```text
http://localhost:5000
```

---

# How It Works

### 1. Upload

The user uploads an image or video through the web interface.

### 2. Preprocessing

OpenCV processes the input image or video frames through resizing and image enhancement operations.

### 3. Pothole Detection

The trained YOLOv12 model detects potholes and returns:

- Bounding boxes
- Confidence scores
- Detection locations

### 4. Severity Analysis

Detected potholes are analyzed using geometric characteristics such as bounding-box area and shape to classify their severity.

### 5. GPS Extraction

For images containing EXIF metadata, GPS coordinates are extracted automatically.

### 6. Map Visualization

The extracted coordinates are displayed using an interactive Leaflet.js map.

### 7. Generative AI Analysis

Detection and severity information is provided to Google Gemini to generate a plain-English road condition summary.

### 8. Reporting

Detection results, severity information, GPS coordinates, and AI-generated summaries can be compiled into a PDF report.

---

# Model Performance

SpotHole was evaluated against multiple YOLO versions.

| Model | mAP@0.5 | mAP@0.5:0.95 | FPS |
|---|---:|---:|---:|
| YOLOv8 | 93.1% | 59.8% | 62 |
| YOLOv10 | 94.8% | 63.1% | 70 |
| **YOLOv12** | **95.6%** | **65.4%** | **79** |

YOLOv12 achieved the highest reported detection performance among the evaluated models while maintaining real-time inference speed.

---

# Applications

SpotHole can support:

- Municipal road maintenance
- Vehicle-based road inspection
- Drone-assisted infrastructure monitoring
- Smart city infrastructure
- Geospatial pothole mapping
- Road repair prioritization
- Automated infrastructure reporting

---

# Limitations

- Performance may decrease under poor lighting conditions.
- Heavy rain and adverse weather can affect detection accuracy.
- Severity estimation depends on image quality and camera angle.
- GPS information depends on EXIF metadata availability.
- The current implementation primarily targets street-level imagery.

---

# Future Work

Planned improvements include:

- Drone-based aerial inspection
- City-scale pothole mapping
- IoT/V2I integration
- Mobile application integration
- Improved performance under adverse weather conditions
- Improved severity estimation
- Expansion of training datasets
- Cloud deployment
- Historical pothole monitoring and maintenance tracking

---

# Datasets

The project uses pothole datasets including:

- **RDD2022**
- **Roboflow**

The combined dataset contains **10,000+ annotated instances** used for model training and evaluation.

---

# Acknowledgements

We acknowledge the open-source computer vision, deep learning, and generative AI communities whose tools, frameworks, and datasets supported the development of SpotHole.

---

# SpotHole

**Detect. Analyze. Map. Maintain.**

An AI-powered approach toward smarter and safer road infrastructure.
