# SIO – Smart Intelligent Ophthalmology
### AI-Based Eye Disease Detection and Advisory Chatbot

SIO (Smart Intelligent Ophthalmology) is an AI-powered web application designed to support early detection and awareness of common eye diseases. It combines deep learning, computer vision, and conversational AI to provide users with preliminary eye health insights and educational guidance.

Users can upload eye images or capture them using a webcam to receive AI-based predictions, severity assessments, and relevant health information.

## Key Features

- **AI-Based Eye Disease Detection:** CNN-based image classification for five eye conditions.
- **Image Upload & Webcam Scanning:** Analyze images uploaded from a device or captured through a camera.
- **Severity Assessment:** Categorizes predicted conditions into mild, moderate, and severe levels.
- **AI Health Assistant:** Gemini API-powered chatbot for eye-health-related questions and educational guidance.
- **User Tracking:** MongoDB integration for storing user information and scan history.
- **Interactive Symptom Checker:** Explore possible causes based on selected symptoms.
- **Learn & Practice:** Eye-care education, exercises, and basic vision tests.

## Eye Conditions Covered

1. Cataract
2. Glaucoma
3. Uveitis
4. Crossed Eyes (Strabismus)
5. Bulging Eyes

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Machine Learning | Convolutional Neural Networks (CNN) |
| Image Processing | OpenCV, NumPy |
| AI Chatbot | Google Gemini API |
| Database | MongoDB |
| Development | Visual Studio Code |

## Project Structure

```text
SIO-Smart-Intelligent-Ophthalmology/
│
├── dataset/
├── model/
├── templates/
├── app.py
├── train_model.py
├── newapp
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sio-smart-intelligent-ophthalmology.git
```

### 2. Navigate to the Project Directory

```bash
cd sio-smart-intelligent-ophthalmology
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

Install the dependencies required by the project:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Configure the required API keys and database connection settings, including:

- Gemini API key
- MongoDB connection URI

Keep credentials in environment variables and never commit private API keys.

### 6. Run the Application

```bash
python app.py
```

Open the local URL displayed in your terminal in a web browser.

## Project Objectives

- Promote awareness and early screening of common eye diseases.
- Make AI-assisted eye health information more accessible.
- Provide an interactive and user-friendly healthcare experience.
- Combine deep learning and conversational AI in a single platform.
- Encourage preventive eye care and timely professional consultation.

## Future Enhancements

- Integration with nearby ophthalmologists and healthcare facilities.
- Mobile application development.
- Telemedicine integration.
- Improved deep learning architectures.
- Explainable AI with visual prediction heatmaps.
- Offline screening capabilities.

## Disclaimer

SIO is an academic project intended for educational purposes and preliminary eye-health awareness. Its AI-generated predictions and chatbot responses are not a substitute for professional medical diagnosis, examination, or treatment. Users should consult a qualified ophthalmologist for medical advice.

## Sustainable Development Goals

This project supports:

- **SDG 3:** Good Health and Well-Being
- **SDG 9:** Industry, Innovation and Infrastructure
- **SDG 10:** Reduced Inequalities

---

**Project:** SIO – Smart Intelligent Ophthalmology  
**Project Type:** Undergraduate BCA Mini Project  
**Institution:** CHRIST (Deemed to be University)  
**Academic Year:** 2025

